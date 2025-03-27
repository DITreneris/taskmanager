from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import base64
from datetime import datetime, timedelta
import re
import databutton as db
from googleapiclient.discovery import build
import dateparser

# Import auth utilities
from app.apis.gmail_auth import get_credentials, EmailMessage

# Define the router
router = APIRouter()

class ScanEmailsRequest(BaseModel):
    max_results: int = 20
    include_content: bool = True

class MeetingRequest(BaseModel):
    message_id: str
    sender: str
    sender_email: str
    subject: str
    date_received: str
    detected_dates: List[str] = []
    detected_times: List[str] = []
    email_content: str
    proposed_datetime: Optional[str] = None
    status: str = "pending"  # pending, confirmed, declined, suggested_alternative

# Date and time regex patterns
DATE_PATTERNS = [
    # MM/DD/YYYY or DD/MM/YYYY
    r'\b(0?[1-9]|1[0-2])[\/\.](0?[1-9]|[12]\d|3[01])[\/\.]([12]\d{3})\b',
    # Month DD, YYYY
    r'\b(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[\s,]+(0?[1-9]|[12]\d|3[01])(?:[\s,]+([12]\d{3}))?\b',
    # DD Month YYYY
    r'\b(0?[1-9]|[12]\d|3[01])[\s,]+(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?:[\s,]+([12]\d{3}))?\b',
    # YYYY-MM-DD (ISO format)
    r'\b([12]\d{3})-(0?[1-9]|1[0-2])-(0?[1-9]|[12]\d|3[01])\b',
    # Tomorrow, day after tomorrow, next Monday, etc.
    r'\b(tomorrow|day after tomorrow|next (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun))\b',
    # This/next week/month
    r'\b(this|next) (week|month)\b'
]

TIME_PATTERNS = [
    # HH:MM (12-hour or 24-hour format)
    r'\b([01]?\d|2[0-3]):([0-5]\d)\s*(am|pm|AM|PM)?\b',
    # H.MM (12-hour or 24-hour format with period)
    r'\b([01]?\d|2[0-3])\.([0-5]\d)\s*(am|pm|AM|PM)?\b',
    # H AM/PM (simple 12-hour format)
    r'\b([01]?\d)\s*(am|pm|AM|PM)\b',
    # noon, midnight
    r'\b(noon|midnight)\b'
]

# Combined pattern for detecting meeting phrases
MEETING_PHRASES = [
    r'\b(meet|meeting|appointment|schedule|call|chat|discuss|sync|talk|connect)\b',
    r'\b(available|free|calendar|agenda|slot|time)\b',
    r'\b(lets|let\'s|can we|would you|are you|how about)\b.*?\b(meet|talk|discuss|call|chat|connect)\b'
]

def extract_email_content(payload):
    """Extract plain text content from email payload."""
    if not payload:
        return ""
    
    if 'body' in payload and payload['body'].get('data'):
        # Base64 decode the data
        text = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        return text
    
    # If there are parts (multipart email), recursively extract from all parts
    if 'parts' in payload:
        text_parts = []
        for part in payload['parts']:
            # Look for text/plain parts first
            if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                text = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                text_parts.append(text)
            # Otherwise, recursively check parts
            elif 'parts' in part:
                text_parts.append(extract_email_content(part))
        return "\n".join([part for part in text_parts if part])
    
    return ""

def detect_dates_and_times(text):
    """Extract potential dates and times from text using regex."""
    dates = []
    times = []
    
    # Look for dates
    for pattern in DATE_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            date_str = match.group(0)
            dates.append(date_str)
    
    # Look for times
    for pattern in TIME_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            time_str = match.group(0)
            times.append(time_str)
    
    return dates, times

def is_meeting_request(text, subject):
    """Determine if the email is likely a meeting request based on content."""
    # Combine subject and body for analysis
    full_text = f"{subject} {text}"
    
    # Check for meeting-related phrases
    for pattern in MEETING_PHRASES:
        if re.search(pattern, full_text, re.IGNORECASE):
            return True
    
    # Check for detected dates and times
    dates, times = detect_dates_and_times(full_text)
    
    # If we find both a date and a time, it's likely a meeting request
    if dates and times:
        return True
    
    return False

def normalize_datetime(date_str, time_str=None):
    """Attempt to normalize date/time strings into a standard format."""
    if not date_str:
        return None
    
    # Combine date and time if both are provided
    if time_str:
        parse_str = f"{date_str} {time_str}"
    else:
        parse_str = date_str
    
    # Use dateparser to handle various formats
    parsed_date = dateparser.parse(parse_str, settings={
        'PREFER_DATES_FROM': 'future',
        'RELATIVE_BASE': datetime.now()
    })
    
    if parsed_date:
        return parsed_date.isoformat()
    
    return None

@router.get("/gmail/scan")
async def scan_emails(background_tasks: BackgroundTasks, max_results: int = 20) -> List[EmailMessage]:
    """Scan recent emails for potential meeting requests."""
    creds = get_credentials()
    if not creds:
        raise HTTPException(status_code=401, detail="Not authenticated with Gmail")
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Get recent messages
        result = service.users().messages().list(
            userId='me', 
            maxResults=max_results,
            q='newer_than:7d'
        ).execute()
        
        messages = result.get('messages', [])
        
        if not messages:
            return []
        
        email_results = []
        for msg in messages:
            msg_id = msg['id']
            # Get the full message
            message = service.users().messages().get(userId='me', id=msg_id).execute()
            
            # Extract headers
            headers = {header['name']: header['value'] for header in message['payload']['headers']}
            
            sender = headers.get('From', '')
            sender_email = re.search(r'<(.+?)>', sender) or re.search(r'(.+)', sender)
            if sender_email:
                sender_email = sender_email.group(1)
            else:
                sender_email = ''
                
            subject = headers.get('Subject', '(No subject)')
            date = headers.get('Date', '')
            
            # Extract email content
            content = extract_email_content(message['payload'])
            
            # Check if it's a meeting request
            is_meeting = is_meeting_request(content, subject)
            
            # If it's a meeting request, extract dates and times
            detected_dates = []
            detected_times = []
            if is_meeting:
                detected_dates, detected_times = detect_dates_and_times(content + " " + subject)
            
            email_results.append(EmailMessage(
                message_id=msg_id,
                sender=sender,
                subject=subject,
                date=date,
                snippet=message.get('snippet', ''),
                contains_meeting_request=is_meeting,
                detected_dates=detected_dates,
                detected_times=detected_times
            ))
        
        # Start a background task to process and store meeting requests
        if email_results:
            background_tasks.add_task(process_meeting_requests, email_results, service)
        
        return email_results
        
    except Exception as e:
        print(f"Error scanning emails: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to scan emails: {str(e)}")

async def process_meeting_requests(emails: List[EmailMessage], service):
    """Process and store meeting requests found in emails."""
    try:
        # Get existing meeting requests
        try:
            existing_requests = db.storage.json.get("meeting_requests", default=[])
        except:
            existing_requests = []
        
        # Process each email that contains a meeting request
        for email in emails:
            if not email.contains_meeting_request:
                continue
                
            # Check if we already have this message processed
            if any(req.get('message_id') == email.message_id for req in existing_requests):
                continue
                
            # Get the full message to extract more content
            message = service.users().messages().get(userId='me', id=email.message_id).execute()
            content = extract_email_content(message['payload'])
            
            # Extract sender email
            headers = {header['name']: header['value'] for header in message['payload']['headers']}
            sender = headers.get('From', '')
            sender_email = re.search(r'<(.+?)>', sender) or re.search(r'(.+)', sender)
            if sender_email:
                sender_email = sender_email.group(1)
            else:
                sender_email = ''
            
            # Try to determine a proposed datetime if we have both date and time
            proposed_datetime = None
            if email.detected_dates and email.detected_times:
                # Use the first detected date and time for simplicity
                # In a real app, you might want to use NLP to get the most likely date/time pair
                proposed_datetime = normalize_datetime(email.detected_dates[0], email.detected_times[0])
            
            # Create a new meeting request
            new_request = {
                "message_id": email.message_id,
                "sender": sender,
                "sender_email": sender_email,
                "subject": email.subject,
                "date_received": email.date,
                "detected_dates": email.detected_dates,
                "detected_times": email.detected_times,
                "email_content": content,
                "proposed_datetime": proposed_datetime,
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }
            
            # Add to existing requests
            existing_requests.append(new_request)
        
        # Save updated meeting requests
        if existing_requests:
            db.storage.json.put("meeting_requests", existing_requests)
            
    except Exception as e:
        print(f"Error processing meeting requests: {e}")

@router.get("/gmail/meeting-requests")
async def get_meeting_requests() -> List[Dict[str, Any]]:
    """Get stored meeting requests."""
    try:
        # Get existing meeting requests
        existing_requests = db.storage.json.get("meeting_requests", default=[])
        
        # Sort by date received, newest first
        sorted_requests = sorted(
            existing_requests,
            key=lambda x: dateparser.parse(x.get('date_received', '')), 
            reverse=True
        )
        
        return sorted_requests
        
    except Exception as e:
        print(f"Error getting meeting requests: {e}")
        return []