from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Get authenticated Google Calendar service"""
    try:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        raise Exception(f"Failed to authenticate with Google Calendar: {str(e)}")

def add_to_calendar(events):
    """Add extracted events to calendar"""
    service = get_calendar_service()

    for e in events:
        event = {
            'summary': e['event'],
            'description': e['raw'],
            'start': {
                'date': e['date'],
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'date': e['date'],
                'timeZone': 'Asia/Kolkata',
            },
        }

        event_result = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created: {event_result['htmlLink']}")

def create_manual_event(title, description, event_date, event_time, duration_minutes=60):
    """Create a manual event with specific date and time"""
    try:
        service = get_calendar_service()
        
        # Parse the date and time
        if isinstance(event_date, str):
            event_date = datetime.strptime(event_date, '%Y-%m-%d').date()
        if isinstance(event_time, str):
            # Handle different time formats
            try:
                event_time = datetime.strptime(event_time, '%H:%M').time()
            except ValueError:
                try:
                    event_time = datetime.strptime(event_time, '%I:%M %p').time()
                except ValueError:
                    raise ValueError("Invalid time format. Please use HH:MM or HH:MM AM/PM")
        
        # Combine date and time
        start_datetime = datetime.combine(event_date, event_time)
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        
        # Convert to ISO format with timezone
        tz = pytz.timezone('Asia/Kolkata')
        start_datetime = tz.localize(start_datetime)
        end_datetime = tz.localize(end_datetime)
        
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 30},       # 30 minutes before
                ],
            },
        }

        event_result = service.events().insert(calendarId='primary', body=event).execute()
        return {
            'success': True,
            'event_id': event_result['id'],
            'html_link': event_result['htmlLink'],
            'start_time': start_datetime.strftime('%Y-%m-%d %I:%M %p'),
            'end_time': end_datetime.strftime('%Y-%m-%d %I:%M %p')
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def list_upcoming_events(max_results=10):
    """List upcoming events from Google Calendar"""
    try:
        service = get_calendar_service()
        
        now = datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        return events
        
    except Exception as e:
        raise Exception(f"Failed to fetch events: {str(e)}")
