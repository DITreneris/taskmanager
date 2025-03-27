from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import databutton as db

# Define the router
router = APIRouter()

class TimeSlot(BaseModel):
    start: str  # ISO format datetime
    end: str    # ISO format datetime

class ScheduleRequest(BaseModel):
    date: str  # YYYY-MM-DD
    duration_minutes: int = 30

class CalendarEvent(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    start_time: str  # ISO format datetime
    end_time: str    # ISO format datetime
    is_all_day: bool = False
    status: str = "confirmed"  # confirmed, tentative, cancelled
    source: str = "manual"     # manual, email, api
    meeting_request_id: Optional[str] = None  # reference to the email message id

# In-memory store for calendar events until we integrate with Google Calendar
def get_calendar_events():
    """Get calendar events from storage or return empty list if none exist"""
    try:
        return db.storage.json.get("calendar_events", default=[])
    except:
        return []

def save_calendar_events(events):
    """Save calendar events to storage"""
    db.storage.json.put("calendar_events", events)

@router.get("/calendar/events")
def list_events() -> List[CalendarEvent]:
    """Get all calendar events"""
    events = get_calendar_events()
    return events

@router.post("/calendar/events")
def create_event(event: CalendarEvent) -> CalendarEvent:
    """Create a new calendar event"""
    events = get_calendar_events()
    
    # Check for conflicts
    if is_conflicting(event, events):
        raise HTTPException(status_code=400, detail="Event conflicts with existing events")
    
    events.append(event.dict())
    save_calendar_events(events)
    return event

@router.get("/calendar/events/{event_id}")
def get_event(event_id: str) -> CalendarEvent:
    """Get a specific calendar event"""
    events = get_calendar_events()
    for event in events:
        if event["id"] == event_id:
            return CalendarEvent(**event)
    
    raise HTTPException(status_code=404, detail="Event not found")

@router.delete("/calendar/events/{event_id}")
def delete_event(event_id: str) -> Dict[str, Any]:
    """Delete a calendar event"""
    events = get_calendar_events()
    initial_count = len(events)
    events = [event for event in events if event["id"] != event_id]
    
    if len(events) == initial_count:
        raise HTTPException(status_code=404, detail="Event not found")
    
    save_calendar_events(events)
    return {"success": True, "message": "Event deleted"}

@router.put("/calendar/events/{event_id}")
def update_event(event_id: str, updated_event: CalendarEvent) -> CalendarEvent:
    """Update a calendar event"""
    events = get_calendar_events()
    event_found = False
    
    for i, event in enumerate(events):
        if event["id"] == event_id:
            # Check for conflicts with other events (excluding this one)
            other_events = [e for e in events if e["id"] != event_id]
            if is_conflicting(updated_event, other_events):
                raise HTTPException(status_code=400, detail="Updated event conflicts with existing events")
            
            events[i] = updated_event.dict()
            event_found = True
            break
    
    if not event_found:
        raise HTTPException(status_code=404, detail="Event not found")
    
    save_calendar_events(events)
    return updated_event

def is_conflicting(event: CalendarEvent, other_events: List[Dict[str, Any]]) -> bool:
    """Check if an event conflicts with any other events"""
    event_start = datetime.fromisoformat(event.start_time)
    event_end = datetime.fromisoformat(event.end_time)
    
    for other in other_events:
        # Skip cancelled events
        if other.get("status") == "cancelled":
            continue
            
        other_start = datetime.fromisoformat(other["start_time"])
        other_end = datetime.fromisoformat(other["end_time"])
        
        # Check for overlap
        if (event_start < other_end and event_end > other_start):
            return True
    
    return False

@router.get("/calendar/available-slots")
def get_available_slots(date: str, duration_minutes: int = 30) -> List[TimeSlot]:
    """Find available time slots on a given day"""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Default business hours (9 AM to 5 PM)
    day_start = datetime.combine(target_date, datetime.min.time().replace(hour=9))
    day_end = datetime.combine(target_date, datetime.min.time().replace(hour=17))
    
    # Get all events for this day
    all_events = get_calendar_events()
    day_events = []
    
    for event in all_events:
        event_start = datetime.fromisoformat(event["start_time"])
        event_end = datetime.fromisoformat(event["end_time"])
        
        # Skip events not on the target date or cancelled events
        if (event_start.date() != target_date or 
            event_end.date() != target_date or
            event.get("status") == "cancelled"):
            continue
            
        day_events.append({
            "start": event_start,
            "end": event_end
        })
    
    # Sort events by start time
    day_events.sort(key=lambda x: x["start"])
    
    # Find free slots
    free_slots = []
    slot_duration = timedelta(minutes=duration_minutes)
    current_time = day_start
    
    # Add occupied slots
    occupied_slots = []
    for event in day_events:
        occupied_slots.append((event["start"], event["end"]))
    
    # If no events, the entire day is free
    if not occupied_slots:
        # Generate slots at regular intervals
        while current_time + slot_duration <= day_end:
            slot_end = current_time + slot_duration
            free_slots.append(TimeSlot(
                start=current_time.isoformat(),
                end=slot_end.isoformat()
            ))
            current_time += slot_duration
        return free_slots
    
    # Start with the beginning of the day to the first event
    if current_time < occupied_slots[0][0]:
        while current_time + slot_duration <= occupied_slots[0][0]:
            slot_end = current_time + slot_duration
            free_slots.append(TimeSlot(
                start=current_time.isoformat(),
                end=slot_end.isoformat()
            ))
            current_time += slot_duration
    
    # Add slots between events
    for i in range(len(occupied_slots) - 1):
        current_time = occupied_slots[i][1]  # End of current event
        next_start = occupied_slots[i + 1][0]  # Start of next event
        
        while current_time + slot_duration <= next_start:
            slot_end = current_time + slot_duration
            free_slots.append(TimeSlot(
                start=current_time.isoformat(),
                end=slot_end.isoformat()
            ))
            current_time += slot_duration
    
    # Add slots after the last event to the end of the day
    current_time = occupied_slots[-1][1]  # End of the last event
    while current_time + slot_duration <= day_end:
        slot_end = current_time + slot_duration
        free_slots.append(TimeSlot(
            start=current_time.isoformat(),
            end=slot_end.isoformat()
        ))
        current_time += slot_duration
    
    return free_slots

@router.post("/calendar/suggest-alternatives")
def suggest_alternative_times(request: ScheduleRequest) -> List[TimeSlot]:
    """Suggest alternative meeting times if requested slot is not available"""
    # Get available slots for the requested date
    available_slots = get_available_slots(request.date, request.duration_minutes)
    
    # Return top 3 available slots (or all if fewer than 3)
    return available_slots[:min(3, len(available_slots))]
