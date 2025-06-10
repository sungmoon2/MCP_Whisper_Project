#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper 모델 성능 비교 스크립트
다양한 모델과 파일 길이로 처리 시간 및 정확도 측정
"""

import os
import time
import subprocess
import json
from datetime import datetime

def get_audio_file_info(filename):
    """오디오 파일 정보 조회"""
    if not os.path.exists(filename):
        return None
    
    file_size = os.path.getsize(filename)
    return {
        "filename": filename,
        "size_bytes": file_size,
        "size_kb": round(file_size / 1024, 1),
        "size_mb": round(file_size / (1024 * 1024), 2)
    }

def run_whisper_test(audio_file, model_name, device="cuda"):
    """Whisper 모델 테스트 실행 및 시간 측정"""
    
    print(f"\n🔄 테스트 중: {model_name} 모델로 {audio_file} 처리")
    
    # 명령어 구성
    cmd = [
        "whisper", 
        audio_file,
        "--language", "Korean",
        "--device", device,
        "--model", model_name,
        "--output_format", "txt"
    ]
    
    try:
        # 시작 시간 기록
        start_time = time.time()
        
        # Whisper 실행
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=600  # 최대 10분 대기
        )
        
        # 종료 시간 기록
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 결과 파일명 (Whisper가 자동으로 생성)
        base_name = os.path.splitext(audio_file)[0]
        output_file = f"{base_name}.txt"
        
        # 출력 파일 확인
        output_text = ""
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                output_text = f.read().strip()
        
        return {
            "success": result.returncode == 0,
            "processing_time": round(processing_time, 2),
            "output_text": output_text,
            "text_length": len(output_text),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_file": output_file
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "타임아웃 (10분 초과)",
            "processing_time": 600
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "processing_time": 0
        }

def main():
    """메인 성능 테스트 함수"""
    
    print("🎯 Whisper 모델 성능 비교 테스트")
    print("=" * 60)
    
    # 테스트할 파일들
    test_files = [
        "test_meeting_korean.mp3",      # 기존 (54초)
        "medium_meeting_korean.mp3",    # 중간 (1-2분)
        "long_meeting_korean.mp3"       # 긴 (3-5분)
    ]
    
    # 테스트할 모델들 (빠른 것부터 느린 것 순서)
    models = [
        "tiny",
        "base", 
        "small",
        "medium",
        "large-v3-turbo",
        "large-v3"
    ]
    
    # 결과 저장용
    all_results = []
    
    print("📁 테스트 파일 정보:")
    for filename in test_files:
        info = get_audio_file_info(filename)
        if info:
            print(f"   {filename}: {info['size_kb']} KB")
        else:
            print(f"   ❌ {filename}: 파일을 찾을 수 없음")
    
    print("\n🤖 테스트할 모델들:")
    for model in models:
        print(f"   - {model}")
    
    print(f"\n⏰ 테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 각 파일별로 모든 모델 테스트
    for audio_file in test_files:
        if not os.path.exists(audio_file):
            print(f"❌ 파일 없음: {audio_file}")
            continue
            
        file_info = get_audio_file_info(audio_file)
        print(f"\n📄 {audio_file} 테스트 ({file_info['size_kb']} KB)")
        print("-" * 50)
        
        file_results = {
            "audio_file": audio_file,
            "file_info": file_info,
            "model_results": {}
        }
        
        for model in models:
            result = run_whisper_test(audio_file, model)
            file_results["model_results"][model] = result
            
            if result["success"]:
                print(f"✅ {model:15s}: {result['processing_time']:6.2f}초, 출력 {result['text_length']:4d}자")
            else:
                error_msg = result.get("error", "알 수 없는 오류")
                print(f"❌ {model:15s}: 실패 - {error_msg}")
        
        all_results.append(file_results)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 성능 비교 요약")
    print("=" * 60)
    
    # 표 형태로 결과 출력
    print(f"{'파일명':<25s} {'모델':<15s} {'시간(초)':<8s} {'텍스트길이':<10s}")
    print("-" * 65)
    
    for file_result in all_results:
        filename = file_result["audio_file"]
        for model, result in file_result["model_results"].items():
            if result["success"]:
                print(f"{filename:<25s} {model:<15s} {result['processing_time']:<8.2f} {result['text_length']:<10d}")
            else:
                print(f"{filename:<25s} {model:<15s} {'실패':<8s} {'-':<10s}")
    
    # JSON 파일로 상세 결과 저장
    results_filename = f"whisper_performance_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_filename, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 상세 결과가 저장되었습니다: {results_filename}")
    
    # 속도 순위
    print(f"\n🏁 모델별 평균 처리 속도 (성공한 테스트만):")
    speed_stats = {}
    for file_result in all_results:
        for model, result in file_result["model_results"].items():
            if result["success"]:
                if model not in speed_stats:
                    speed_stats[model] = []
                speed_stats[model].append(result["processing_time"])
    
    # 평균 계산 및 정렬
    avg_speeds = {}
    for model, times in speed_stats.items():
        avg_speeds[model] = sum(times) / len(times)
    
    sorted_speeds = sorted(avg_speeds.items(), key=lambda x: x[1])
    
    for i, (model, avg_time) in enumerate(sorted_speeds, 1):
        print(f"{i}. {model:<15s}: {avg_time:.2f}초 평균")

if __name__ == "__main__":
    main()
