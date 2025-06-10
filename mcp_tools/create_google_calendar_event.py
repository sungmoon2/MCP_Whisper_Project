#!/usr/bin/env python3
"""
Google Calendar Event Creation MCP Tool
Claude MCP를 통해 일정 데이터를 받아 Google Calendar에 이벤트를 생성하는 도구
"""

import json
import sys
import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Google Calendar API 스코프
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    """Google Calendar API 인증"""
    creds = None
    project_dir = '/home/minsujo/whisper_project'
    token_path = os.path.join(project_dir, 'token.json')
    credentials_path = os.path.join(project_dir, 'credentials.json')
    
    # 기존 토큰 파일이 있으면 로드
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # 유효하지 않은 토큰이면 새로 인증
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"토큰 갱신 실패: {e}")
                creds = None
        
        if not creds:
            if not os.path.exists(credentials_path):
                print(f"오류: {credentials_path} 파일을 찾을 수 없습니다.")
                print("Google Cloud Console에서 OAuth 2.0 credentials.json을 다운로드하세요.")
                return None
                
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 토큰을 파일에 저장
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return creds

def create_calendar_event(event_data):
    """캘린더 이벤트 생성"""
    try:
        creds = authenticate_google_calendar()
        if not creds:
            return {"error": "Google Calendar 인증 실패"}
        
        service = build('calendar', 'v3', credentials=creds)
        
        # 이벤트 데이터 파싱
        title = event_data.get('title', '제목 없음')
        date = event_data.get('date', '')
        time = event_data.get('time', '09:00')
        description = event_data.get('description', '')
        duration = event_data.get('duration', 60)  # 기본 60분
        
        # 날짜/시간 조합
        try:
            start_datetime = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            end_datetime = start_datetime + datetime.timedelta(minutes=duration)
        except ValueError as e:
            return {"error": f"날짜/시간 형식 오류: {e}"}
        
        # 이벤트 객체 생성
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
        
        # 이벤트 생성
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        
        return {
            "success": True,
            "event_id": created_event['id'],
            "event_link": created_event.get('htmlLink'),
            "message": f"'{title}' 일정이 {date} {time}에 생성되었습니다."
        }
        
    except HttpError as e:
        return {"error": f"Google Calendar API 오류: {e}"}
    except Exception as e:
        return {"error": f"예상치 못한 오류: {e}"}

def main():
    """MCP 인터페이스"""
    if len(sys.argv) != 2:
        print(json.dumps({"error": "사용법: python create_google_calendar_event.py '<JSON_DATA>'"}))
        sys.exit(1)
    
    try:
        # JSON 데이터 파싱
        event_data = json.loads(sys.argv[1])
        
        # 이벤트 생성
        result = create_calendar_event(event_data)
        
        # 결과 출력 (JSON 형식)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"JSON 파싱 오류: {e}"}, ensure_ascii=False))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"실행 오류: {e}"}, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main()
def create_calendar_event(event_data):
    """캘린더 이벤트 생성"""
    try:
        creds = authenticate_google_calendar()
        if not creds:
            return {"error": "Google Calendar 인증 실패"}
        
        service = build('calendar', 'v3', credentials=creds)
        
        # 이벤트 데이터 파싱
        title = event_data.get('title', '제목 없음')
        date = event_data.get('date', '')
        time = event_data.get('time', '09:00')
        description = event_data.get('description', '')
        duration = event_data.get('duration', 60)  # 기본 60분
        
        # 날짜/시간 조합
        try:
            start_datetime = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            end_datetime = start_datetime + datetime.timedelta(minutes=duration)
        except ValueError as e:
            return {"error": f"날짜/시간 형식 오류: {e}"}
        
        # 이벤트 객체 생성
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
        
        # 이벤트 생성
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        
        return {
            "success": True,
            "event_id": created_event['id'],
            "event_link": created_event.get('htmlLink'),
            "message": f"'{title}' 일정이 {date} {time}에 생성되었습니다."
        }
        
    except HttpError as e:
        return {"error": f"Google Calendar API 오류: {e}"}
    except Exception as e:
        return {"error": f"예상치 못한 오류: {e}"}

def main():
    """MCP 인터페이스"""
    if len(sys.argv) != 2:
        print(json.dumps({"error": "사용법: python create_google_calendar_event.py '<JSON_DATA>'"}))
        sys.exit(1)
    
    try:
        # JSON 데이터 파싱
        event_data = json.loads(sys.argv[1])
        
        # 이벤트 생성
        result = create_calendar_event(event_data)
        
        # 결과 출력 (JSON 형식)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"JSON 파싱 오류: {e}"}, ensure_ascii=False))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"실행 오류: {e}"}, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main()
