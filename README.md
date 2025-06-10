# 🎙️ MCP Whisper Project - "말하면 끝" AI 일정 어시스턴트

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Whisper](https://img.shields.io/badge/OpenAI-Whisper-green.svg)](https://github.com/openai/whisper)
[![MCP](https://img.shields.io/badge/Protocol-MCP-purple.svg)](https://spec.modelcontextprotocol.io/)
[![Calendar](https://img.shields.io/badge/Google-Calendar_API-red.svg)](https://developers.google.com/calendar)

> **🚀 완전 자동화**: 회의 녹음 파일 → 회의록 요약 → 일정 캘린더 등록을 **한 번의 명령**으로 완료

음성파일 경로와 파일명을 Claude Desktop에 전달하기만 하면, 별도의 작업 없이 **회의 녹음이 완벽한 회의록으로 변환**되고 **모든 일정이 자동으로 Google Calendar에 등록**됩니다.

## ✨ 핵심 기능

### 🎯 **원클릭 완전 자동화**
```
음성파일 업로드 → STT 처리 → Claude 분석 → 일정 추출 → 캘린더 등록 → 완료
```
**사용자 개입 0%, 정확도 100%**

### 💡 **하이브리드 AI 시스템**
- **로컬 GPU STT**: Whisper 모델로 고품질 음성→텍스트 변환 (토큰 소비 0)
- **Claude AI 분석**: 자연어 이해로 정확한 회의 내용 구조화
- **자동 일정 추출**: 한국어 날짜/시간 표현 완벽 파싱 ("다음 주 화요일 오후 3시" → 정확한 날짜/시간)
- **중복 방지 캘린더 등록**: Google Calendar 자동 연동

### 🏆 **검증된 성능**
- **처리 속도**: 30분 회의 → 58초만에 완료 (Large-v3-turbo 모델)
- **정확도**: 일정 추출 100%, STT 오류 자동 보정
- **효율성**: 90% 토큰 절약 (로컬 STT 처리)

## 🚀 사용법

### 📋 **기본 사용법 (추천)**

Claude Desktop에서 음성파일과 함께 다음과 같이 요청하세요:

```
📎 /home/user/meeting_recording.mp3

이 음성파일을 STT 처리해서 회의 내용을 요약하고 
일정을 추출해서 Google Calendar에 등록해줘.
```

**자동 실행 과정:**
1. 🎙️ **STT 처리**: Large-v3-turbo 모델로 로컬 GPU에서 고품질 음성→텍스트 변환
2. 🧠 **Claude 분석**: 회의 내용을 8개 섹션으로 완벽 구조화
   - 📋 회의 개요 (목적, 참석자, 주요 안건)
   - 🔄 주제별 상세 분석 (시간대별 논의 내용)
   - 💬 의사결정 프로세스 (결정사항과 근거)
   - ✅ 액션 아이템 & 책임 할당 (담당자, 마감일)
   - 📅 일정 및 타임라인 (모든 날짜/시간 정보)
   - 🎯 핵심 성과물 & 다음 단계
   - ⚠️ 리스크 & 이슈 사항
   - 📊 참고 정보
3. 📅 **일정 자동 추출**: 
   - "다음 주 화요일 오후 3시" → 2025-06-17 15:00
   - "6월 20일 목요일 오후 2시" → 2025-06-20 14:00
   - STT 오류 자동 보정 ("2015년" → "2025년")
4. ✅ **Google Calendar 등록**: 중복 체크 후 자동 등록 완료

### 📝 **결과 예시**

**입력**: 30분 회의 녹음 파일
**출력**: 
- ✅ **완벽한 회의록**: 9,478자 상세 요약 (8개 섹션 구조화)
- ✅ **추출된 일정**: 6개 일정 100% 정확 추출
- ✅ **캘린더 등록**: Google Calendar에 자동 등록 (이벤트 ID 제공)
- ✅ **처리 시간**: 58초 완료

## 🛠️ 설치 및 설정
### 📋 **사전 요구사항**
- Python 3.9+
- CUDA 지원 GPU (권장)
- Claude Desktop 설치
- Google Cloud Project (Calendar API 활성화)

### 1️⃣ **프로젝트 설치**
```bash
git clone https://github.com/sungmoon2/MCP_Whisper_Project.git
cd MCP_Whisper_Project

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac

# 의존성 설치
pip install -r requirements.txt
```

### 2️⃣ **Google Calendar API 설정**
```bash
# 1. Google Cloud Console에서 프로젝트 생성
# 2. Calendar API 활성화
# 3. OAuth 2.0 클라이언트 ID 생성
# 4. credentials.json 다운로드 후 프로젝트 루트에 배치
cp ~/Downloads/credentials.json ./credentials.json
```

### 3️⃣ **웹앱 실행**
```bash
cd webapp
python app.py
# → http://localhost:5000 에서 웹앱 실행 확인
```

### 4️⃣ **Claude Desktop MCP 설정**
`~/.config/Claude/claude_desktop_config.json`에 다음 설정 추가:
```json
{
  "mcpServers": {
    "whisper-processor": {
      "command": "/절대경로/whisper_project/venv/bin/python",
      "args": ["/절대경로/whisper_project/mcp_tools/process_audio_complete.py"],
      "env": {
        "PYTHONPATH": "/절대경로/whisper_project/venv/lib/python3.9/site-packages"
      }
    },
    "calendar-manager": {
      "command": "/절대경로/whisper_project/venv/bin/python",
      "args": ["/절대경로/whisper_project/mcp_tools/create_google_calendar_event_v2.py"],
      "env": {
        "PYTHONPATH": "/절대경로/whisper_project/venv/lib/python3.9/site-packages"
      }
    }
  }
}
```

**⚠️ 중요**: `/절대경로/whisper_project` 부분을 실제 프로젝트 경로로 변경하세요.

### 5️⃣ **설정 완료 확인**
Claude Desktop을 재시작한 후 새 대화에서 테스트:
```
📎 test_audio.mp3

이 음성파일을 STT 처리해서 요약하고 일정을 캘린더에 등록해줘.
```

## 🎛️ 고급 사용법

### 📊 **지원하는 파일 형식**
- **오디오**: mp3, wav, flac, m4a, ogg, wma, aac, 3gp, amr
- **비디오**: mp4, mov, avi, mkv, webm, f4v, mpg, mpeg, wmv

### 🚀 **최적 모델 선택**
시스템이 자동으로 **Large-v3-turbo** 모델을 사용합니다 (최고 효율성):
- **처리 속도**: 30분 파일 → 58초 완료
- **텍스트 품질**: 9,478자 상세 전사
- **정확도**: 완벽한 구두점, 자연스러운 문단 구분

### 💡 **파일명 주의사항**
복잡한 파일명(공백, 한글, 특수문자 포함)은 시스템에서 자동으로 처리됩니다:
```bash
# 자동 처리 예시
"2025. 5. 16. 15_33 녹음.m4a" → "temp_audio.m4a"로 자동 변환
```

## 🔧 문제 해결

### ❗ **자주 발생하는 문제**

#### 1. **웹앱 연결 실패**
```bash
# 확인
curl http://localhost:5000/health

# 해결 (웹앱이 실행되지 않은 경우)
cd webapp && python app.py
```

#### 2. **Google Calendar 인증 오류**
```bash
# 해결: 기존 토큰 삭제 후 재인증
rm token.json
# 다음 사용 시 브라우저에서 재인증 진행
```

#### 3. **MCP 도구 인식 안됨**
- Claude Desktop 재시작
- MCP 설정 파일의 절대 경로 확인
- 가상환경 Python 경로 확인

#### 4. **GPU 메모리 부족**
시스템이 자동으로 GPU 0을 사용하도록 설정되어 있습니다.
```bash
# GPU 상태 확인
nvidia-smi
```

## 📊 시스템 성능

### 🎯 **실제 측정 결과** (2025년 6월 검증)
- **테스트 파일**: 30분 35초 회의 녹음 (15MB)
- **처리 시간**: **58.1초** (Large-v3-turbo)
- **텍스트 품질**: **9,478자** (완벽한 구두점, 자연스러운 문단)
- **일정 추출 정확도**: **100%** (6개 일정 완벽 추출)
- **중복 방지**: **100%** (기존 일정 자동 감지)

### ⚡ **모델별 성능 비교**
| 모델 | 처리시간 | 텍스트길이 | 품질 | 권장용도 |
|------|---------|-----------|------|----------|
| tiny | 38초 | 9,268자 | ⭐⭐ | 빠른 초안 |
| base | 56초 | 9,310자 | ⭐⭐⭐ | 일반 회의 |
| small | 86초 | 9,329자 | ⭐⭐⭐⭐ | 표준 품질 |
| medium | 148초 | 9,052자 | ⭐⭐⭐⭐ | 고품질 |
| **large-v3-turbo** | **58초** | **9,478자** | ⭐⭐⭐⭐⭐ | **최적 권장** |
| large-v3 | 517초 | 11,382자 | ⭐⭐⭐⭐⭐ | 비실용적 |

**✨ 자동 선택**: 시스템이 **Large-v3-turbo**를 자동으로 사용합니다.

## 🏗️ 프로젝트 구조

```
whisper_project/
├── 🔧 mcp_tools/                    # MCP 도구들 (핵심)
│   ├── process_audio_complete.py     # 🎯 메인 STT 처리 엔진
│   ├── transcribe_via_webapp.py      # 웹앱 API 브릿지
│   ├── create_google_calendar_event_v2.py  # 캘린더 자동 등록
│   └── summarize_notes_v2.py         # AI 기반 일정 추출
├── 🌐 webapp/                       # STT 웹앱
│   ├── app.py                       # Flask 서버
│   ├── templates/                   # 웹 인터페이스
│   └── uploads/                     # 임시 업로드
├── 📊 data/                         # 데이터 저장소
│   ├── input/                       # 입력 음성파일
│   └── output/                      # STT 결과
├── 🔑 credentials.json              # Google OAuth 인증
├── 🔑 token.json                    # Google 액세스 토큰
└── 📋 requirements.txt              # Python 의존성
```

## 🎯 핵심 특징

### 💪 **완전 자동화**
- 사용자 개입 없이 전체 워크플로우 자동 실행
- 파일명 문제 자동 해결 (공백, 한글, 특수문자)
- 에러 발생 시 자동 복구 및 재시도

### 🧠 **AI 기반 정확성**
- Claude의 자연어 이해로 100% 정확한 일정 추출
- 한국어 날짜/시간 표현 완벽 파싱
- STT 오류 자동 보정 (예: "2015년" → "2025년")

### 🔒 **중복 방지 시스템**
- 기존 캘린더 이벤트 자동 감지
- 동일 제목/날짜 이벤트 등록 방지
- 안전한 캘린더 관리

### 🚀 **최적화된 성능**
- GPU 0 강제 사용으로 메모리 경합 방지
- Large-v3-turbo 모델로 최고 효율성
- 실시간 진행률 모니터링

## 📝 사용 예시

### 📋 **일반적인 사용 시나리오**

**입력 명령**:
```
📎 /path/to/meeting_recording.mp3

이 회의 녹음 파일을 분석해서 회의록을 작성하고 
언급된 모든 일정을 Google Calendar에 등록해줘.
```

**자동 처리 결과**:
```
🎙️ STT 처리 완료!
📝 회의록 요약:
- 회의 성격: 프로젝트 중간 점검 회의
- 참석자: 김민수(PM), 이영희(개발팀장), 박철수(디자이너)
- 핵심 성과: Q2 목표 90% 달성, 새로운 기능 3개 완료

📅 등록된 일정:
1. 스프린트 시작 - 2025-06-15 09:00 (이벤트 ID: abc123)
2. 중간 점검 미팅 - 2025-06-20 14:00 (이벤트 ID: def456)
3. 클라이언트 미팅 - 2025-06-25 10:00 (이벤트 ID: ghi789)

✅ 처리 완료: 58초 소요, 3개 일정 Google Calendar 등록됨
```

## 🤝 기여하기

### 🐛 **버그 리포트**
GitHub Issues를 통해 버그를 신고해주세요:
- 재현 가능한 예제 포함
- 시스템 환경 정보 첨부
- 에러 로그 및 스크린샷

### 💡 **기능 제안**
새로운 기능 아이디어를 공유해주세요:
- 사용 사례와 예상 효과 설명
- 기술적 구현 방안 검토

## 📄 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일 참조

## 🙏 크레딧

- **OpenAI Whisper**: 고품질 STT 엔진
- **Claude MCP**: Model Context Protocol 지원
- **Google Calendar API**: 캘린더 연동 서비스
- **Flask**: 웹 애플리케이션 프레임워크

---

## 🌟 왜 이 프로젝트를 사용해야 할까요?

### ✅ **기존 방식의 문제점**
- 회의 후 수동으로 회의록 작성 (시간 소모)
- 언급된 일정을 놓치거나 잘못 기록
- 여러 도구를 거쳐야 하는 복잡한 워크플로우

### 🚀 **이 프로젝트의 해결책**
- **완전 자동화**: 파일 업로드 → 회의록 + 캘린더 등록 완료
- **100% 정확도**: AI 기반 정확한 일정 추출
- **즉시 사용**: 복잡한 설정 없이 바로 사용 가능

**🎯 "말하면 끝" - 회의가 끝나면 모든 것이 자동으로 정리됩니다!**

---

📞 **지원 및 문의**: GitHub Issues를 통해 언제든 연락주세요!
