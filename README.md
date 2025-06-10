# 🎙️ MCP Whisper 프로젝트 - 하이브리드 AI 음성 분석 시스템

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Whisper](https://img.shields.io/badge/OpenAI-Whisper-green.svg)](https://github.com/openai/whisper)
[![MCP](https://img.shields.io/badge/Protocol-MCP-purple.svg)](https://spec.modelcontextprotocol.io/)
[![Calendar](https://img.shields.io/badge/Google-Calendar_API-red.svg)](https://developers.google.com/calendar)

> **혁신적인 하이브리드 AI 시스템**: 로컬 GPU STT 처리 + Claude AI 텍스트 분석 + MCP 자동화 도구

음성파일을 업로드하면 **완전 자동화**로 STT 처리, 회의 내용 분석, 일정 추출, Google Calendar 등록까지 **1-Process**로 완료하는 지능형 시스템입니다.

## 🌟 핵심 혁신 특징

### 🔥 **하이브리드 AI 아키텍처**
```
[로컬 GPU STT] + [Claude AI 분석] + [MCP 자동화] = 최적의 효율성
```

- **로컬 처리**: GPU 가속 Whisper 모델로 고품질 STT (토큰 소비 0)
- **AI 분석**: Claude의 자연어 이해로 정확한 일정 추출 
- **자동화**: MCP 도구로 Google Calendar 직접 등록

### ⚡ **90% 토큰 절약**
- STT 처리를 로컬에서 수행하여 대용량 음성파일도 토큰 걱정 없음
- Claude는 텍스트 분석에만 집중하여 최고 성능 발휘

### 🚀 **완전 자동화 워크플로우**  
```bash
음성파일 업로드 → STT 처리 → Claude 분석 → 일정 추출 → 캘린더 등록 → 완료
```
**사용자 개입 없이 모든 과정이 자동으로 진행됩니다.**

## 🏗️ 시스템 아키텍처

### 📋 **전체 구성도**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Claude Desktop │    │   MCP Bridge    │    │   STT 웹앱      │
│                 │    │                 │    │                 │
│ • 파일 수신     │ ←→ │ • HTTP 클라이언트│ ←→ │ • Whisper 처리  │
│ • 텍스트 분석   │    │ • 폴링 관리     │    │ • GPU 가속     │
│ • 일정 추출     │    │ • 에러 처리     │    │ • 진척도 관리   │
│ • 캘린더 등록   │    │ • 결과 반환     │    │ • 다중 형식 출력│
└─────────────────┘    └─────────────────┘    └─────────────────┘
        ↕                       ↕                       ↕
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Google Calendar │    │   파일 시스템   │    │   실시간 모니터 │
│                 │    │                 │    │                 │
│ • 이벤트 생성   │    │ • 임시 파일 관리│    │ • 프로세스 추적 │
│ • 중복 체크     │    │ • 결과 저장     │    │ • 성능 측정     │
│ • 일정 조회     │    │ • 로그 관리     │    │ • 상태 리포트   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🔄 **데이터 흐름**
1. **파일 업로드**: 사용자가 Claude Desktop에 음성파일 제공
2. **MCP 호출**: Claude가 `process_audio_complete.py` 실행
3. **웹앱 연계**: MCP 도구가 로컬 웹앱 API 호출  
4. **STT 처리**: Whisper 모델로 로컬 GPU에서 음성→텍스트 변환
5. **Claude 분석**: STT 결과를 Claude가 직접 분석하여 회의 내용 구조화
6. **일정 추출**: Claude의 자연어 이해로 날짜/시간/이벤트 정확 파싱
7. **캘린더 등록**: `create_google_calendar_event_v2.py`로 Google Calendar 연동
8. **완료 보고**: 등록된 일정 정보와 함께 처리 결과 제공

## 🛠️ 시스템 구성 요소

### 📁 **프로젝트 구조**
```
whisper_project/
├── 🌐 webapp/                    # STT 처리 웹 애플리케이션
│   ├── app.py                   # Flask 웹서버 (일반적인 STT 웹앱)
│   ├── templates/               # 웹 인터페이스
│   ├── static/                  # CSS, JS 리소스
│   └── uploads/                 # 업로드 파일 임시 저장
├── 🔧 mcp_tools/                # MCP(Model Context Protocol) 도구들
│   ├── process_audio_complete.py     # 🎯 메인 STT 처리 도구
│   ├── transcribe_via_webapp.py      # 웹앱 API 브릿지  
│   ├── create_google_calendar_event_v2.py  # Google Calendar 연동
│   └── summarize_notes.py            # 텍스트 분석 및 요약
├── 📊 src/                      # 테스트 및 유틸리티 스크립트
├── 📚 docs/                     # 프로젝트 문서
├── 🗂️ data/                     # 데이터 디렉토리 (gitignore 처리)
│   ├── input/                   # 입력 음성파일들
│   └── output/                  # STT 결과 파일들
└── 📋 requirements.txt          # Python 의존성 목록
```

### 🎯 **핵심 MCP 도구들**

#### 1️⃣ **`process_audio_complete.py`** - 메인 STT 처리 엔진
```python
# 음성파일 → STT → Claude 분석용 텍스트 반환
python mcp_tools/process_audio_complete.py audio_file.mp3 large-v3-turbo
```
- **기능**: 웹앱 API를 통한 완전 자동화 STT 처리
- **특징**: 실시간 진행률 모니터링, 다중 모델 지원 (tiny ~ large-v3-turbo)
- **출력**: Claude가 분석할 수 있는 구조화된 텍스트

#### 2️⃣ **`transcribe_via_webapp.py`** - 웹앱 HTTP 브릿지
```python  
# 웹앱과의 HTTP 통신 및 폴링 관리
```
- **기능**: MCP 도구와 웹앱 간 HTTP 통신 중개
- **특징**: 비동기 처리, 상태 폴링, 에러 복구
- **역할**: 파일 업로드, 진행률 추적, 결과 수집

#### 3️⃣ **`create_google_calendar_event_v2.py`** - 캘린더 자동 등록
```python
# 추출된 일정 → Google Calendar 자동 등록
python mcp_tools/create_google_calendar_event_v2.py '{"title": "회의", "date": "2025-06-15", "time": "14:00"}'
```
- **기능**: JSON 형태 일정 데이터를 Google Calendar 이벤트로 변환
- **특징**: 중복 이벤트 자동 감지, OAuth 2.0 인증, 에러 처리
- **출력**: 등록된 이벤트 ID 및 Google Calendar 링크

### 🌐 **웹앱 (일반적인 STT 처리용)**

#### **Flask 기반 STT 웹 애플리케이션**
- **목적**: 일반 사용자를 위한 웹 인터페이스 제공
- **기능**: 
  - 브라우저에서 음성파일 업로드
  - 다양한 Whisper 모델 선택 (tiny, base, small, medium, large-v3, large-v3-turbo)
  - 실시간 처리 진행률 표시
  - 다중 형식 결과 제공 (TXT, JSON, SRT, VTT, TSV)
  - 결과 미리보기 및 다운로드

#### **MCP 도구와의 연계**
- **API 엔드포인트**: `/process` - MCP 도구가 HTTP POST로 호출
- **상태 추적**: `/api/status/{task_id}` - 실시간 진행률 확인
- **결과 제공**: `/api/result/{task_id}` - 완료된 STT 결과 반환

## 🚀 설치 및 실행

### 📋 **사전 요구사항**
- Python 3.9+
- CUDA 지원 GPU (권장)
- Google Cloud Project (Calendar API 활성화)
- Claude Desktop + MCP 설정

### 1️⃣ **프로젝트 복제 및 환경 설정**
```bash
git clone https://github.com/sungmoon2/MCP_Whisper_Project.git
cd MCP_Whisper_Project

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는 venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2️⃣ **Google Calendar API 설정**
```bash
# Google Cloud Console에서:
# 1. 프로젝트 생성
# 2. Calendar API 활성화  
# 3. OAuth 2.0 클라이언트 ID 생성
# 4. credentials.json 다운로드

# credentials.json을 프로젝트 루트에 배치
cp ~/Downloads/credentials.json ./credentials.json
```

### 3️⃣ **웹앱 실행 (일반적인 STT 서비스)**
```bash
cd webapp
python app.py
# → http://localhost:5000 에서 웹 인터페이스 접근 가능
```

### 4️⃣ **Claude Desktop MCP 설정**
`claude_desktop_config.json`에 다음 설정 추가:
```json
{
  "mcpServers": {
    "whisper-processor": {
      "command": "/path/to/whisper_project/venv/bin/python",
      "args": ["/path/to/whisper_project/mcp_tools/process_audio_complete.py"],
      "env": {
        "PYTHONPATH": "/path/to/whisper_project/venv/lib/python3.9/site-packages"
      }
    },
    "calendar-manager": {
      "command": "/path/to/whisper_project/venv/bin/python", 
      "args": ["/path/to/whisper_project/mcp_tools/create_google_calendar_event_v2.py"],
      "env": {
        "PYTHONPATH": "/path/to/whisper_project/venv/lib/python3.9/site-packages"
      }
    }
  }
}
```

## 💡 사용법

### 🎯 **MCP를 통한 완전 자동화 (추천)**

Claude Desktop에서 음성파일과 함께 다음과 같이 요청하세요:

```
📎 meeting_recording.mp3

이 음성파일을 STT 처리해서 회의 내용을 분석하고, 
언급된 일정들을 Google Calendar에 등록해줘.
```

**자동 실행 과정:**
1. 🎙️ Claude가 `process_audio_complete.py` MCP 도구 호출
2. 🔄 웹앱에서 GPU 가속 STT 처리 (실시간 진행률 표시)  
3. 🧠 Claude가 STT 결과 텍스트를 직접 분석
4. 📅 Claude가 일정을 추출하고 `create_google_calendar_event_v2.py` 호출
5. ✅ Google Calendar에 일정 자동 등록 완료

### 🌐 **웹앱을 통한 일반적인 STT 처리**

브라우저에서 `http://localhost:5000` 접속:

1. **파일 업로드**: 음성/비디오 파일 드래그&드롭
2. **모델 선택**: 품질/속도에 따라 모델 선택
   - `tiny`, `base`: 빠른 처리, 기본 품질
   - `small`, `medium`: 균형잡힌 성능  
   - `large-v3`, `large-v3-turbo`: 최고 품질 (권장)
3. **형식 선택**: TXT, JSON, SRT, VTT, TSV 중 선택
4. **처리 시작**: 실시간 진행률과 함께 자동 처리
5. **결과 확인**: 미리보기 및 다운로드

### 🔧 **개별 MCP 도구 직접 실행**

#### STT 처리만 수행
```bash
cd whisper_project
source venv/bin/activate
python mcp_tools/process_audio_complete.py audio_file.mp3 large-v3-turbo
```

#### Google Calendar 이벤트 생성
```bash
python mcp_tools/create_google_calendar_event_v2.py '{
    "title": "프로젝트 회의",
    "date": "2025-06-15", 
    "time": "14:00",
    "description": "Q2 진행상황 점검",
    "duration": 120
}'
```

## 🎛️ 고급 설정

### 📊 **모델별 성능 특성** (실제 측정 기준)

| 모델 | 처리속도 | 품질 | 메모리 | 권장 용도 |
|------|---------|------|--------|-----------|
| `tiny` | ⚡⚡⚡⚡⚡ | ⭐⭐ | 💾 | 빠른 초안, 실시간 |
| `base` | ⚡⚡⚡⚡ | ⭐⭐⭐ | 💾💾 | 일반 회의 |  
| `small` | ⚡⚡⚡ | ⭐⭐⭐⭐ | 💾💾💾 | 표준 품질 |
| `medium` | ⚡⚡ | ⭐⭐⭐⭐ | 💾💾💾💾 | 고품질 필요시 |
| `large-v3` | ⚡ | ⭐⭐⭐⭐⭐ | 💾💾💾💾💾 | 최고 품질 (느림) |
| `large-v3-turbo` | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | 💾💾💾💾 | **최적 균형** ⭐ |

**✨ 권장**: `large-v3-turbo` 모델 - 최고 품질과 실용적 속도의 완벽한 균형

### ⚙️ **환경 변수 설정**
```bash
# GPU 강제 사용 (CUDA 환경)
export CUDA_VISIBLE_DEVICES=0

# 웹앱 포트 변경  
export FLASK_PORT=8000

# 로그 레벨 설정
export LOG_LEVEL=INFO
```

## 🔧 문제 해결

### ❗ **자주 발생하는 문제들**

#### 1. **파일 경로 인식 실패**
```bash
# 문제: 공백, 한글 포함 파일명 인식 불가
# 해결: 파일 복사로 우회
cd "파일경로" && cp "복잡한 파일명"* simple_audio.mp3
```

#### 2. **웹앱 연결 실패**  
```bash
# 확인: 웹앱 실행 상태
curl http://localhost:5000/health

# 실행: 웹앱 시작
cd webapp && python app.py
```

#### 3. **Google Calendar 인증 오류**
```bash
# 확인: credentials.json 파일 존재
ls -la credentials.json

# 재인증: 기존 토큰 삭제 후 재시도  
rm token.json
```

#### 4. **GPU 메모리 부족**
```bash
# 해결: 더 작은 모델 사용
python mcp_tools/process_audio_complete.py audio.mp3 small
```

### 📊 **로그 및 모니터링**

#### 처리 진행률 실시간 확인
```bash
# 웹앱 로그 모니터링
tail -f webapp/webapp.log

# 시스템 리소스 확인
nvidia-smi  # GPU 사용률
htop        # CPU 및 메모리
```

#### 결과 파일 위치
- **STT 결과**: `data/output/{task_id}/`
- **로그 파일**: `webapp/webapp.log`  
- **임시 파일**: `webapp/uploads/`

## 🚀 성능 최적화

### ⚡ **속도 향상 팁**
1. **모델 선택**: 용도에 맞는 최적 모델 선택
2. **GPU 활용**: CUDA 설정으로 처리 속도 10배 향상
3. **파일 전처리**: 복잡한 파일명 사전 단순화  
4. **배치 처리**: 여러 파일 동시 처리 시 큐 활용

### 💾 **메모리 최적화**
1. **임시 파일 정리**: 처리 완료 후 자동 삭제 설정
2. **모델 캐싱**: 동일 모델 재사용으로 로딩 시간 단축
3. **청크 처리**: 대용량 파일 분할 처리

## 🤝 기여하기

### 🐛 **버그 리포트**
- Issue 템플릿을 사용하여 버그 상세 설명
- 재현 가능한 최소 예제 첨부
- 시스템 환경 정보 포함

### 💡 **기능 제안** 
- Feature Request 템플릿 활용
- 사용 사례와 예상 효과 설명
- 기술적 구현 방안 검토

### 🔧 **Pull Request**
1. Fork 후 feature 브랜치 생성
2. 코드 스타일 가이드 준수  
3. 테스트 케이스 추가
4. 문서 업데이트

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 크레딧

- **OpenAI Whisper**: 고품질 STT 엔진
- **Google Calendar API**: 캘린더 연동 서비스  
- **Claude MCP**: Model Context Protocol 지원
- **Flask**: 웹 애플리케이션 프레임워크

---

## 📞 지원 및 문의

- **GitHub Issues**: 버그 리포트 및 기능 요청
- **Discussions**: 일반적인 질문 및 아이디어 공유  
- **Wiki**: 자세한 사용법 및 고급 설정 가이드

**🎯 이 프로젝트로 음성 데이터를 효율적으로 텍스트화하고 자동으로 일정을 관리하세요!**