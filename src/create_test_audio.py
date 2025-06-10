#!/usr/bin/env python3
from gtts import gTTS
import os

def create_test_audio():
    # 테스트용 회의 내용
    meeting_text = """
    안녕하세요, 오늘 프로젝트 회의를 시작하겠습니다.
    첫 번째 안건은 데이터베이스 설계 진행 상황입니다.
    지난주에 완료된 테이블 설계를 검토하고, 이번 주 구현 계획을 논의하겠습니다.
    두 번째 안건은 일정 조율입니다.
    다음 스프린트는 6월 15일부터 시작될 예정이며, 
    중간 점검 미팅은 6월 20일 오후 2시로 예정되어 있습니다.
    세 번째로 리소스 배분에 대해 논의하겠습니다.
    프론트엔드 개발에 추가 인력이 필요할 것 같습니다.
    마지막으로 다음 주 화요일 오전 10시에 클라이언트 미팅이 예정되어 있으니 
    모든 팀원들은 참석 부탁드립니다.
    오늘 회의는 여기서 마치겠습니다. 감사합니다.
    """
    
    print("🎤 테스트용 한국어 음성 파일 생성 중...")
    
    try:
        tts = gTTS(text=meeting_text.strip(), lang='ko', slow=False)
        output_file = "test_meeting_korean.mp3"
        tts.save(output_file)
        
        print(f"✅ 성공! {output_file} 파일이 생성되었습니다.")
        print(f"📁 파일 경로: {os.path.abspath(output_file)}")
        
        file_size = os.path.getsize(output_file)
        print(f"📊 파일 크기: {file_size / 1024:.1f} KB")
        
        print("\n🚀 이제 Whisper로 테스트해보세요:")
        print(f"whisper {output_file} --language Korean --device cuda --model small")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("💡 gTTS 설치가 필요합니다: pip install gTTS")

if __name__ == "__main__":
    create_test_audio()
