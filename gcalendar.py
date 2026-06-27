import speech_recognition as sr
from datetime import datetime, timedelta
from pytz import timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os.path
import re

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    service = build('calendar', 'v3', credentials=creds)
    return service

def create_event(start_time, end_time, summary, description=None, location=None):
    """
    Creates a Google Calendar event.
    
    Args:
        start_time: datetime object for event start
        end_time: datetime object for event end
        summary: str, title of the event
        description: str, optional description
        location: str, optional location
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Get calendar service
        service = get_calendar_service()
        
        # Ensure datetime objects have timezone
        if start_time.tzinfo is None or end_time.tzinfo is None:
            raise ValueError("start_time and end_time must include timezone information")

        # Create event body
        event_body = {
            'summary': summary,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': str(start_time.tzinfo),
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': str(end_time.tzinfo),
            },
        }

        # Add optional fields if provided
        if description:
            event_body['description'] = description
        if location:
            event_body['location'] = location

        # Create the event
        event = service.events().insert(
            calendarId='primary',
            body=event_body
        ).execute()

        # Return success with event link
        return True, f"Event created successfully. Link: {event.get('htmlLink')}"

    except Exception as e:
        error_message = str(e)
        if "credentials" in error_message.lower():
            return False, "Authentication error: Please check your Google Calendar credentials"
        elif "quota" in error_message.lower():
            return False, "API quota exceeded: Please try again later"
        else:
            return False, f"Failed to create event: {error_message}"
        

        
def extract_date(command):
    today = datetime.now().date()
    
    if 'today' in command:
        return today
    elif 'tomorrow' in command:
        return today + timedelta(days=1)
    elif 'day after tomorrow' in command:
        return today + timedelta(days=2)
    elif 'next' in command:
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for i, day in enumerate(days):
            if day in command.lower():
                days_ahead = (i - today.weekday() + 7) % 7 or 7
                return today + timedelta(days=days_ahead)
    
    # Check for specific date format (e.g., "27 august", "august 27", "27th august", "august 27th")
    date_patterns = [
        r'(\d{1,2})(st|nd|rd|th)?\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)',
        r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2})(st|nd|rd|th)?'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, command.lower())
        if match:
            groups = match.groups()
            if len(groups[0]) > 3:  # First group is month
                month_str, day = groups[0], groups[1]
            else:  # First group is day
                month_str, day = groups[2], groups[0]
            
            day = int(day)
            month = datetime.strptime(month_str[:3], '%b').month
            year = today.year
            
            # If the parsed date is earlier than today, assume it's for next year
            parsed_date = datetime(year, month, day).date()
            if parsed_date < today:
                year += 1
            
            return datetime(year, month, day).date()
    
    return None

def extract_time(command):
    time_regex = re.compile(r'\b(\d{1,2})(?::(\d{2}))?\s*(AM|PM|am|pm|a\.m\.|p\.m\.)?(?:\b|\s+)')
    time_match = time_regex.search(command)
    
    if time_match:
        hour, minute, meridiem = time_match.groups()
        hour = int(hour)
        minute = int(minute or 0)  # Use 0 if minute is None
        
        if meridiem:
            meridiem = meridiem.lower().replace('.', '')  # Normalize meridiem
        
        if not meridiem:
            # If meridiem is not specified, assume it based on the hour
            meridiem = 'pm' if 12 <= hour < 24 else 'am'
        
        # Convert to 24-hour format
        if meridiem in ['pm', 'p.m.'] and hour != 12:
            hour += 12
        elif meridiem in ['am', 'a.m.'] and hour == 12:
            hour = 0
        
        return f"{hour:02d}:{minute:02d}"
    
    return None

def parse_command(command):
    print(f"Original command: {command}")
    
    date_part = extract_date(command)
    time_part = extract_time(command)
    
    print(f"Extracted date part: {date_part}")
    print(f"Extracted time part: {time_part}")
    
    if not date_part:
        raise ValueError("Could not parse the date. Please specify a valid date.")
    
    if not time_part:
        raise ValueError("Could not parse the time. Please specify a valid time.")
    
    # Combine date and time
    date_time_str = f"{date_part} {time_part}"
    print(f"Combined date and time: {date_time_str}")
    
    try:
        date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
        
        # Additional check for valid hour
        if date_time.hour >= 24:
            raise ValueError("Invalid hour. Must be between 0 and 23.")
        
    except ValueError as e:
        raise ValueError(f"Failed to parse datetime string: {e}")
    
    print(f"Parsed date and time: {date_time}")
    
    summary_match = re.search(r"meeting with (.+?)(?:\s+on|\s+at|$)", command, re.IGNORECASE)
    summary = summary_match.group(1).strip() if summary_match else " Scheduled Meeting"
    
    return summary, date_time

def recognize_speech_and_create_event():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Listening for voice command...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        print(f"You said: {command}")

        summary, start_time = parse_command(command)
        
        india_tz = timezone('Asia/Kolkata')
        start_time = india_tz.localize(start_time)
        end_time = start_time + timedelta(hours=1)

        create_event(start_time, end_time, summary)

    except sr.UnknownValueError:
        print("Sorry, I did not understand that.")
    except sr.RequestError:
        print("Sorry, I could not request results; check your network connection.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    recognize_speech_and_create_event()