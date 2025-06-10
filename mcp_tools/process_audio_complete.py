#!/usr/bin/env python3
"""
완전 통합 MCP 도구: 음성 → STT (Claude가 텍스트 분석)
STT 처리만 수행하고 Claude에게 텍스트 분석을 위임
"""

import sys
import json
import subprocess
import os
from pathlib import Path

def transcribe_audio_for_claude(file_path, model="small"):
    """
    음성파일 STT 처리: Claude의 텍스트 분석을 위한 전처리
    
    Args:
        file_path: 음성파일 경로
        model: whisper 모델 (기본값: small)
    
    Returns:
        dict: STT 결과와 Claude 분석용 메타데이터
    """
    
    print("🎙️ === STT 처리 시작 ===")
    print(f"📁 파일: {os.path.basename(file_path)}")
    print(f"🤖 모델: {model}")
    print("-" * 50)
    
    # 파일 존재 확인
    if not os.path.exists(file_path):
        return {
            "success": False, 
            "error": f"파일을 찾을 수 없습니다: {file_path}"
        }
    
    # 파일 크기 확인
    file_size = os.path.getsize(file_path)
    file_size_mb = file_size / (1024 * 1024)
    print(f"📊 파일 크기: {file_size_mb:.1f}MB")
    
    if file_size_mb > 500:
        return {
            "success": False, 
            "error": f"파일이 너무 큽니다: {file_size_mb:.1f}MB (최대 500MB)"
        }
    
    # MCP 도구 경로 설정
    mcp_tools_dir = os.path.dirname(os.path.abspath(__file__))
    webapp_bridge_path = os.path.join(mcp_tools_dir, 'transcribe_via_webapp.py')
    
    if not os.path.exists(webapp_bridge_path):
        return {
            "success": False, 
            "error": f"웹앱 브릿지 도구를 찾을 수 없습니다: {webapp_bridge_path}"
        }
    
    # 웹앱을 통한 STT 처리
    try:
        print("🔄 웹앱 브릿지를 통한 STT 처리 중...")
        
        stt_result = subprocess.run([
            'python', webapp_bridge_path,
            file_path, model, 'txt', '--quiet'
        ],
        capture_output=True, 
        text=True, 
        cwd=mcp_tools_dir,
        timeout=900  # 15분 타임아웃
        )
        
        if stt_result.returncode != 0:
            error_msg = stt_result.stderr or "알 수 없는 오류"
            return {
                "success": False, 
                "error": f"STT 처리 실패 (exit code {stt_result.returncode}): {error_msg}"
            }
        
        # STT 결과 파싱
        try:
            stt_data = json.loads(stt_result.stdout)
        except json.JSONDecodeError as e:
            # JSON 파싱 실패 시 원본 출력에서 JSON 부분 추출 시도
            stdout_lines = stt_result.stdout.strip().split('\n')
            json_line = None
            
            for line in reversed(stdout_lines):
                if line.strip().startswith('{') and line.strip().endswith('}'):
                    json_line = line.strip()
                    break
            
            if json_line:
                try:
                    stt_data = json.loads(json_line)
                except:
                    return {
                        "success": False, 
                        "error": f"STT 결과 JSON 파싱 실패: {e}"
                    }
            else:
                return {
                    "success": False, 
                    "error": f"STT 결과에서 JSON을 찾을 수 없습니다: {stt_result.stdout[:500]}"
                }
        
        # STT 성공 여부 확인
        if not stt_data.get('success'):
            return {
                "success": False, 
                "error": f"STT 실패: {stt_data.get('error', '알 수 없는 STT 오류')}"
            }
        
        # 텍스트 내용 확인
        text_content = stt_data.get('text', '').strip()
        if not text_content:
            return {
                "success": False, 
                "error": "STT 처리는 완료되었으나 텍스트 내용이 비어있습니다."
            }
        
        # 성공 결과 처리
        print(f"✅ STT 완료!")
        print(f"📝 텍스트 길이: {len(text_content):,}자")
        print(f"⏱️ 처리 시간: {stt_data.get('processing_time', '알 수 없음')}")
        
        # Claude 분석용 텍스트 미리보기
        preview_length = 300
        text_preview = (text_content[:preview_length] + "...") if len(text_content) > preview_length else text_content
        
        print(f"\n🔍 텍스트 미리보기:")
        print("-" * 30)
        print(text_preview)
        print("-" * 30)
        
        return {
            "success": True,
            "task_id": stt_data.get('task_id'),
            "text": text_content,
            "text_length": len(text_content),
            "text_preview": text_preview,
            "text_format": stt_data.get('text_format', 'txt'),
            "file_info": {
                "original_file": os.path.basename(file_path),
                "file_size_mb": round(file_size_mb, 1),
                "model_used": model
            },
            "processing_info": {
                "processing_time": stt_data.get('processing_time'),
                "stt_task_id": stt_data.get('task_id')
            },
            "download_links": stt_data.get('download_links', {}),
            "message": f"STT 처리 완료. {len(text_content):,}자의 텍스트가 생성되었습니다. 이제 Claude가 이 텍스트를 분석할 수 있습니다.",
            "claude_instructions": {
                "next_step": "이 텍스트를 분석하여 회의 내용 요약 및 일정 추출을 진행하세요.",
                "suggested_analysis": [
                    "회의 내용 요약",
                    "주요 결정사항 추출", 
                    "액션 아이템 정리",
                    "일정/미팅/약속 추출",
                    "중요한 날짜 및 마감일 확인"
                ]
            }
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False, 
            "error": "STT 처리 시간 초과 (15분). 파일이 너무 크거나 복잡할 수 있습니다."
        }
    except Exception as e:
        return {
            "success": False, 
            "error": f"STT 처리 중 예상치 못한 오류: {str(e)}"
        }

def main():
    """MCP 진입점 - STT만 처리하고 Claude에게 텍스트 분석 위임"""
    
    if len(sys.argv) < 2:
        help_info = {
            "error": "사용법: python process_audio_complete.py <audio_file_path> [model]",
            "description": "음성파일을 STT 처리하여 Claude 분석용 텍스트로 변환합니다.",
            "examples": [
                "python process_audio_complete.py /path/to/meeting.mp3",
                "python process_audio_complete.py /path/to/recording.wav large-v3-turbo",
                "python process_audio_complete.py ~/Downloads/interview.m4a medium"
            ],
            "available_models": [
                "tiny (73MB) - 매우 빠름, 낮은 품질",
                "base (139MB) - 빠름, 보통 품질",
                "small (462MB) - 보통 속도, 중간 품질 (기본값)",
                "medium (1.5GB) - 느림, 좋은 품질",
                "large-v3 (2.9GB) - 매우 느림, 최고 품질",
                "large-v3-turbo (1.6GB) - 보통 속도, 최고 품질 (추천)"
            ],
            "note": "STT 처리 후 텍스트를 Claude가 직접 분석합니다."
        }
        print(json.dumps(help_info, ensure_ascii=False, indent=2))
        return
    
    file_path = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "small"
    
    # 파일 경로 절대 경로 변환
    file_path = os.path.abspath(os.path.expanduser(file_path))
    
    print(f"🎯 음성파일 STT 처리 (Claude 분석용)")
    print(f"📁 파일: {file_path}")
    print(f"🤖 모델: {model}")
    print("=" * 60)
    
    result = transcribe_audio_for_claude(file_path, model)
    
    print("\n" + "=" * 60)
    print("🎯 최종 결과:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if result.get('success'):
        print(f"\n✅ 성공! Claude가 분석할 준비가 완료되었습니다.")
        print(f"📊 텍스트 길이: {result['text_length']:,}자")
        print(f"🔗 다음 단계: Claude에게 일정 추출 및 캘린더 등록을 요청하세요.")

if __name__ == "__main__":
    main()