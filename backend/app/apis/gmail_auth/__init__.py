from fastapi import APIRouter, HTTPException, Request, Depends, BackgroundTasks, Query
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
import os
import json
from typing import Optional, List
import databutton as db
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import re

# Define the router
router = APIRouter()

# OAuth2 scopes needed
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class AuthStatus(BaseModel):
    is_authenticated: bool
    username: Optional[str] = None
    email: Optional[str] = None

class AuthRequest(BaseModel):
    redirect_uri: str

class UserProfile(BaseModel):
    name: str
    email: str
    picture: Optional[str] = None

class EmailMessage(BaseModel):
    message_id: str
    sender: str
    subject: str
    date: str
    snippet: str
    contains_meeting_request: bool
    detected_dates: List[str] = []
    detected_times: List[str] = []

def get_credentials() -> Optional[Credentials]:
    """Get the stored OAuth credentials if they exist and are valid."""
    try:
        creds_json = db.storage.json.get("gmail_credentials", default=None)
        if not creds_json:
            return None
        
        creds = Credentials.from_authorized_user_info(creds_json, SCOPES)
        
        # Check if credentials are expired and can be refreshed
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Update the stored credentials
            db.storage.json.put("gmail_credentials", json.loads(creds.to_json()))
        
        return creds
    except Exception as e:
        print(f"Error getting credentials: {e}")
        return None

@router.get("/auth/gmail/status")
async def auth_status() -> AuthStatus:
    """Check the current authentication status."""
    creds = get_credentials()
    if not creds:
        return AuthStatus(is_authenticated=False)
    
    try:
        # Get the user information from Gmail API
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        return AuthStatus(
            is_authenticated=True, 
            username=profile.get('emailAddress', '').split('@')[0],
            email=profile.get('emailAddress')
        )
    except Exception as e:
        print(f"Error checking auth status: {e}")
        # If we can't get profile info, credentials are probably invalid
        return AuthStatus(is_authenticated=False)

@router.post("/auth/gmail/login")
async def login(auth_request: AuthRequest):
    """Initiate the OAuth flow."""
    try:
        # Check if we have client_secret (this should be stored in secrets)
        client_secret_json = db.secrets.get("GOOGLE_CLIENT_SECRET")
        if not client_secret_json:
            raise HTTPException(status_code=500, detail="Google API credentials not configured")

        # Create OAuth flow with client secret JSON
        client_config = json.loads(client_secret_json)
        
        # Create a flow instance with client_secrets from the JSON
        flow = Flow.from_client_config(
            client_config=client_config,
            scopes=SCOPES,
            redirect_uri=auth_request.redirect_uri
        )
        
        # Generate the authorization URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        # Store flow state in storage for later retrieval
        db.storage.json.put("gmail_auth_flow", flow.to_json())
        
        return {"auth_url": auth_url}
        
    except Exception as e:
        print(f"Error initiating login: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initiate login: {str(e)}")

@router.get("/auth/gmail/callback")
async def callback(
    code: str = Query(...),
    state: str = Query(...),
    redirect_uri: str = Query(...)
):
    """Handle the OAuth callback."""
    try:
        # Get the flow from storage
        flow_json = db.storage.json.get("gmail_auth_flow")
        if not flow_json:
            raise HTTPException(status_code=400, detail="Auth flow missing or expired")
        
        # Recreate the flow
        flow = Flow.from_json(flow_json)
        flow.redirect_uri = redirect_uri
        
        # Exchange the authorization code for credentials
        flow.fetch_token(code=code)
        
        # Get credentials and save them
        creds = flow.credentials
        db.storage.json.put("gmail_credentials", json.loads(creds.to_json()))
        
        # Clean up the flow data
        db.storage.json.put("gmail_auth_flow", None)
        
        # Return success message or redirect to a success page
        return RedirectResponse(url="/")
        
    except Exception as e:
        print(f"Error in callback: {e}")
        raise HTTPException(status_code=500, detail=f"Auth callback failed: {str(e)}")

@router.get("/auth/gmail/logout")
async def logout():
    """Log out by removing the stored credentials."""
    try:
        db.storage.json.put("gmail_credentials", None)
        return {"success": True, "message": "Logged out successfully"}
    except Exception as e:
        print(f"Error during logout: {e}")
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")

@router.get("/auth/gmail/user")
async def get_user_profile() -> UserProfile:
    """Get the authenticated user's profile information."""
    creds = get_credentials()
    if not creds:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        
        # Use People API to get more details
        people_service = build('people', 'v1', credentials=creds)
        person = people_service.people().get(
            resourceName='people/me',
            personFields='names,emailAddresses,photos'
        ).execute()
        
        # Extract name and photo from People API response
        name = profile.get('emailAddress', '').split('@')[0]  # Fallback to email username
        if 'names' in person and person['names']:
            name = person['names'][0].get('displayName', name)
        
        photo_url = None
        if 'photos' in person and person['photos']:
            photo_url = person['photos'][0].get('url')
        
        return UserProfile(
            name=name,
            email=profile.get('emailAddress', ''),
            picture=photo_url
        )
        
    except Exception as e:
        print(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user profile: {str(e)}")
