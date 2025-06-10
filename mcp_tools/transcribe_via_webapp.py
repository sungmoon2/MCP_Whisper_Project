#!/usr/bin/env python3
"""
MCP 도구: 웹앱을 통한 STT 처리
Claude Desktop에서 호출되어 로컬 웹앱으로 STT 작업 위임
"""

import sys
import json
import requests
import time
import os
from pathlib import Path

def transcribe_audio_via_webapp(file_path, model="small", formats=["txt"]):
    """
    웹앱을 통한 음성파일 STT 처리
    
    Args:
        file_path: 음성파일 경로
        model: whisper 모델 (tiny, base, small, medium, large-v3, large-v3-turbo)
        formats: 출력 형식 리스트
    
    Returns:
        dict: STT 결과 및 메타데이터
    """
    
    quiet_mode = '--quiet' in sys.argv
    
    # 1. 웹앱 실행 상태 확인
    try:
        health_check = requests.get('http://localhost:5000/health', timeout=5)
        if health_check.status_code != 200:
            raise Exception("웹앱이 실행되지 않았습니다.")
        
        health_data = health_check.json()
        if not quiet_mode:
            print(f"✅ 웹앱 상태: {health_data.get('message', '정상')}")
        
    except requests.exceptions.ConnectionError:
        return {
            "success": False, 
            "error": "웹앱이 실행되지 않았습니다. 먼저 'cd ~/whisper_project/webapp && python app.py'로 실행해주세요."
        }
    except Exception as e:
        return {
            "success": False, 
            "error": f"웹앱 연결 실패: {str(e)}"
        }
    
    # 2. 파일 존재 및 크기 확인
    if not os.path.exists(file_path):
        return {"success": False, "error": f"파일을 찾을 수 없습니다: {file_path}"}
    
    file_size = os.path.getsize(file_path)
    file_size_mb = file_size / (1024 * 1024)
    
    if file_size_mb > 500:
        return {
            "success": False, 
            "error": f"파일 크기가 너무 큽니다: {file_size_mb:.1f}MB (최대 500MB)"
        }
    
    if not quiet_mode:
        print(f"📁 파일 정보: {os.path.basename(file_path)} ({file_size_mb:.1f}MB)")
    
    # 3. 파일 업로드 및 STT 시작
    try:
        if not quiet_mode:
            print("📤 파일 업로드 중...")
        
        with open(file_path, 'rb') as f:
            files = {'audio': (os.path.basename(file_path), f, 'audio/mpeg')}
            data = {
                'model': model,
                'formats': ','.join(formats)
            }
            
            response = requests.post(
                'http://localhost:5000/api/transcribe',
                files=files,
                data=data,
                timeout=60
            )
            
        if response.status_code != 200:
            return {
                "success": False, 
                "error": f"업로드 실패 (HTTP {response.status_code}): {response.text}"
            }
            
        upload_result = response.json()
        if not upload_result.get('success'):
            return {
                "success": False, 
                "error": f"업로드 실패: {upload_result.get('error', '알 수 없는 오류')}"
            }
            
        task_id = upload_result['task_id']
        if not quiet_mode:
            print(f"✅ 업로드 완료! Task ID: {task_id}")
            print(f"🎯 모델: {model}, 형식: {', '.join(formats)}")
        
    except Exception as e:
        return {"success": False, "error": f"업로드 중 오류: {str(e)}"}
    
    # 4. 진행상황 폴링
    if not quiet_mode:
        print("\n🔄 STT 처리 진행상황:")
        print("=" * 50)
    
    max_wait_time = 600  # 10분 최대 대기
    start_time = time.time()
    last_progress = -1
    
    while time.time() - start_time < max_wait_time:
        try:
            status_response = requests.get(
                f'http://localhost:5000/api/status/{task_id}',
                timeout=10
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                
                progress = status_data.get('progress', 0)
                message = status_data.get('message', '')
                status = status_data.get('status', 'unknown')
                
                # 진행률이 변경되었을 때만 출력
                if progress != last_progress and not quiet_mode:
                    progress_bar = "█" * int(progress // 5) + "░" * (20 - int(progress // 5))
                    print(f"[{progress_bar}] {progress}% - {message}")
                    last_progress = progress
                
                if status == 'completed':
                    if not quiet_mode:
                        print("✅ STT 처리 완료!")
                    break
                elif status == 'error':
                    return {
                        "success": False, 
                        "error": f"STT 처리 실패: {message}"
                    }
                    
            else:
                if not quiet_mode:
                    print(f"⚠️ 상태 확인 실패 (HTTP {status_response.status_code})")
                
        except Exception as e:
            if not quiet_mode:
                print(f"⚠️ 상태 확인 중 오류: {e}")
            
        time.sleep(2)
    else:
        return {
            "success": False, 
            "error": f"STT 처리 시간 초과 ({max_wait_time//60}분)"
        }
    
    # 5. 결과 가져오기
    try:
        if not quiet_mode:
            print("\n📥 결과 가져오는 중...")
        
        result_response = requests.get(
            f'http://localhost:5000/api/result/{task_id}',
            timeout=30
        )
        
        if result_response.status_code != 200:
            return {
                "success": False, 
                "error": f"결과 가져오기 실패 (HTTP {result_response.status_code})"
            }
            
        result_data = result_response.json()
        
        # 텍스트 내용 추출 (실제 파일 다운로드 방식)
        text_content = ""
        selected_format = ""
        selected_filename = ""
        
        if result_data.get('previews'):
            format_priority = ['TXT (순수 텍스트)', 'JSON (타임스탬프 포함)', 'VTT (웹 자막)', 'SRT (영상 자막)', 'TSV (표 형식)']
            
            # 우선순위에 따라 파일 선택
            for fmt in format_priority:
                for preview in result_data['previews']:
                    if preview['format'] == fmt:
                        selected_filename = preview['filename']
                        selected_format = fmt
                        break
                if selected_filename:
                    break
            
            if not selected_filename and result_data['previews']:
                # 우선순위에 없는 형식이어도 첫 번째 preview 사용
                selected_filename = result_data['previews'][0]['filename']
                selected_format = result_data['previews'][0]['format']
            
            # 실제 파일 다운로드해서 전체 텍스트 추출
            if selected_filename:
                download_url = f"http://localhost:5000/download/{task_id}/{selected_filename}"
                try:
                    download_response = requests.get(download_url, timeout=30)
                    if download_response.status_code == 200:
                        # UTF-8 인코딩 에러 무시하여 완전한 텍스트 추출
                        text_content = download_response.content.decode('utf-8', errors='ignore')
                        if not quiet_mode:
                            print(f"📥 전체 파일 다운로드 완료: {selected_filename}")
                    else:
                        # 다운로드 실패 시 미리보기라도 사용
                        for preview in result_data['previews']:
                            if preview['filename'] == selected_filename:
                                text_content = preview['content']
                                if not quiet_mode:
                                    print(f"⚠️ 파일 다운로드 실패, 미리보기 사용: {download_response.status_code}")
                                break
                except Exception as e:
                    # 다운로드 오류 시 미리보기라도 사용
                    for preview in result_data['previews']:
                        if preview['filename'] == selected_filename:
                            text_content = preview['content']
                            if not quiet_mode:
                                print(f"⚠️ 다운로드 오류, 미리보기 사용: {str(e)}")
                            break
        
        # 결과 요약 출력
        if not quiet_mode:
            print(f"✅ 텍스트 추출 완료!")
            print(f"📝 형식: {selected_format}")
            print(f"📊 길이: {len(text_content):,}자")
            
            if text_content:
                preview_text = text_content[:200] + "..." if len(text_content) > 200 else text_content
                print(f"🔍 미리보기: {preview_text}")
        
        return {
            "success": True,
            "task_id": task_id,
            "text": text_content,
            "text_format": selected_format,
            "text_length": len(text_content),
            "text_preview": text_content[:500] + "..." if len(text_content) > 500 else text_content,
            "file_info": result_data.get('file_info', {}),
            "previews": result_data.get('previews', []),
            "download_links": result_data.get('download_links', {}),
            "processing_time": f"{time.time() - start_time:.1f}초"
        }
        
    except Exception as e:
        return {"success": False, "error": f"결과 처리 중 오류: {str(e)}"}

def main():
    """MCP 진입점"""
    # 조용한 모드 확인 (다른 MCP 도구에서 호출할 때)
    quiet_mode = '--quiet' in sys.argv
    if quiet_mode:
        sys.argv.remove('--quiet')
    
    if len(sys.argv) < 2:
        help_info = {
            "error": "사용법: python transcribe_via_webapp.py <audio_file_path> [model] [formats]",
            "examples": [
                "python transcribe_via_webapp.py /path/to/audio.mp3",
                "python transcribe_via_webapp.py /path/to/audio.mp3 large-v3-turbo",
                "python transcribe_via_webapp.py /path/to/audio.mp3 small txt,json,srt"
            ]
        }
        print(json.dumps(help_info, ensure_ascii=False, indent=2))
        return
    
    file_path = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "small"
    formats_str = sys.argv[3] if len(sys.argv) > 3 else "txt"
    formats = formats_str.split(',')
    
    if not quiet_mode:
        print(f"🎙️ Whisper STT via WebApp")
        print(f"📁 파일: {file_path}")
        print(f"🤖 모델: {model}")
        print(f"📋 형식: {', '.join(formats)}")
        print("-" * 50)
    
    result = transcribe_audio_via_webapp(file_path, model, formats)
    
    if quiet_mode:
        # JSON만 출력 (다른 도구에서 파싱용)
        print(json.dumps(result, ensure_ascii=False))
    else:
        # 사용자 친화적 출력
        print("\n" + "=" * 50)
        print("🎯 최종 결과:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()