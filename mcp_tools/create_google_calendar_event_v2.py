#!/usr/bin/env python3
import json
import sys
import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    creds = None
    project_dir = '/home/minsujo/whisper_project'
    token_path = os.path.join(project_dir, 'token.json')
    credentials_path = os.path.join(project_dir, 'credentials.json')
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        
        if not creds:
            if not os.path.exists(credentials_path):
                return {"error": f"credentials.json 파일을 찾을 수 없습니다: {credentials_path}"}
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return creds

def check_duplicate_events(service, title, date):
    try:
        time_min = f"{date}T00:00:00Z"
        time_max = f"{date}T23:59:59Z"
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        duplicate_events = [event for event in events if event.get('summary', '') == title]
        return duplicate_events
    except Exception:
        return []

def create_calendar_event(event_data):
    try:
        creds = authenticate_google_calendar()
        if isinstance(creds, dict) and "error" in creds:
            return creds
        
        service = build('calendar', 'v3', credentials=creds)
        
        title = event_data.get('title', '제목 없음')
        date = event_data.get('date', '')
        time = event_data.get('time', '09:00')
        description = event_data.get('description', '')
        duration = event_data.get('duration', 60)
        
        existing_events = check_duplicate_events(service, title, date)
        if existing_events:
            return {
                "success": False,
                "message": f"동일한 제목의 이벤트가 이미 존재합니다: {title}",
                "existing_event_id": existing_events[0]['id']
            }
        
        try:
            start_datetime = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            end_datetime = start_datetime + datetime.timedelta(minutes=duration)
        except ValueError as e:
            return {"error": f"날짜/시간 형식 오류: {e}"}
        
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'Asia/Seoul',
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'Asia/Seoul',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 30},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }
        
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        
        return {
            "success": True,
            "event_id": created_event['id'],
            "event_link": created_event.get('htmlLink'),
            "message": f"'{title}' 일정이 {date} {time}에 생성되었습니다.",
            "duration_minutes": duration
        }
        
    except HttpError as e:
        return {"error": f"Google Calendar API 오류: {e}"}
    except Exception as e:
        return {"error": f"예상치 못한 오류: {e}"}

def main():
    if len(sys.argv) != 2:
        result = {"error": "사용법: python create_google_calendar_event_v2.py '<JSON_DATA>'"}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    try:
        event_data = json.loads(sys.argv[1])
        result = create_calendar_event(event_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except json.JSONDecodeError as e:
        result = {"error": f"JSON 파싱 오류: {e}"}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)
    except Exception as e:
        result = {"error": f"실행 오류: {e}"}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
