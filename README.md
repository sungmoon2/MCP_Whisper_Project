# 음성파일 STT 처리 및 캘린더 등록 자동화 프로젝트

## 프로젝트 개요
음성파일을 자동으로 STT(Speech-To-Text) 처리하고, 추출된 텍스트에서 일정을 파악하여 Google Calendar에 자동 등록하는 완전 자동화 워크플로우입니다.

## 주요 기능
- 🎙️ 음성파일 자동 STT 처리 (Whisper 모델 사용)
- 🤖 Claude AI를 통한 지능적 텍스트 분석
- 📅 자동 일정 추출 및 Google Calendar 등록
- 🌐 웹 인터페이스를 통한 편리한 사용
- 🔧 MCP(Model Context Protocol) 도구 통합

## 디렉토리 구조
```
whisper_project/
├── mcp_tools/          # MCP 도구들
├── src/               # 소스 코드
├── webapp/            # 웹 애플리케이션
├── docs/              # 프로젝트 문서
├── data/              # 데이터 파일들 (gitignore 처리됨)
├── tests/             # 테스트 파일들
└── requirements.txt   # Python 의존성 목록
```

## 설치 및 실행

### 1. 가상환경 설정
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. Google API 설정
1. Google Cloud Console에서 프로젝트 생성
2. Calendar API 활성화
3. 서비스 계정 생성 및 인증 파일 다운로드
4. `credentials.json` 파일을 프로젝트 루트에 배치

### 4. 웹앱 실행
```bash
cd webapp
python app.py
```

## 사용법
1. 웹 인터페이스에서 음성 파일 업로드
2. STT 처리 및 분석 자동 실행
3. 추출된 일정이 Google Calendar에 자동 등록

## 주요 MCP 도구
- `process_audio_complete.py`: 음성파일 STT 처리
- `create_google_calendar_event_v2.py`: Google Calendar 이벤트 생성
- `summarize_notes.py`: 노트 요약 및 분석

## 보안 주의사항
- `credentials.json`, `token.json` 파일은 절대 Git에 커밋하지 마세요
- 개인 음성 파일들은 `data/` 폴더에 저장되며 Git에서 제외됩니다

## 라이선스
[라이선스 정보 추가 필요]

## 기여
이슈 리포트나 풀 리퀘스트는 언제든 환영합니다.
