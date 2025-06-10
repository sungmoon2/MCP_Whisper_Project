#!/usr/bin/env python3
"""
회의록 요약 및 일정 추출 MCP Tool
STT 결과에서 주요 내용 요약 및 일정 정보 추출
"""

import json
import sys
import re
from datetime import datetime, timedelta

def extract_schedule_info(text):
    """텍스트에서 일정 정보 추출"""
    schedules = []
    
    # 날짜 패턴 (다양한 형식 지원)
    date_patterns = [
        r'(\d{4})[년\-\.\/](\d{1,2})[월\-\.\/](\d{1,2})[일]?',
        r'(\d{1,2})[월\-\.\/](\d{1,2})[일]?',
        r'다음주|내일|모레|내주|다음달',
        r'월요일|화요일|수요일|목요일|금요일|토요일|일요일'
    ]
    
    # 시간 패턴
    time_patterns = [
        r'(오전|오후)?\s*(\d{1,2})[시:](\d{2})?분?',
        r'(\d{1,2}):(\d{2})',
        r'(\d{1,2})시\s*(\d{2})?분?'
    ]
    
    # 일정 키워드
    schedule_keywords = [
        '회의', '미팅', '만남', '약속', '모임', '세미나', '발표',
        '제출', '마감', '데드라인', '완료', '점검', '리뷰',
        '계획', '스케줄', '일정', '예약', '체크인'
    ]
    
    # 기본 추출 로직
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 일정 키워드가 포함된 라인 찾기
        has_schedule_keyword = any(keyword in line for keyword in schedule_keywords)
        
        if has_schedule_keyword:
            # 기본 일정 정보 생성
            schedule = {
                "title": line[:50] + "..." if len(line) > 50 else line,
                "description": line,
                "extracted_from": line
            }
            
            # 날짜/시간 추출 시도
            date_found = False
            for pattern in date_patterns:
                match = re.search(pattern, line)
                if match:
                    # 간단한 날짜 파싱 (실제로는 더 정교해야 함)
                    today = datetime.now()
                    schedule["date"] = (today + timedelta(days=7)).strftime("%Y-%m-%d")
                    date_found = True
                    break
            
            if not date_found:
                # 기본값: 1주일 후
                schedule["date"] = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            
            # 시간 추출
            time_found = False
            for pattern in time_patterns:
                match = re.search(pattern, line)
                if match:
                    schedule["time"] = "14:00"  # 기본값
                    time_found = True
                    break
            
            if not time_found:
                schedule["time"] = "14:00"  # 기본 시간
            
            schedules.append(schedule)
    
    return schedules

def summarize_content(text):
    """회의 내용 요약"""
    lines = text.split('\n')
    summary_lines = []
    
    for line in lines:
        line = line.strip()
        if len(line) > 10:  # 의미있는 길이의 문장만
            summary_lines.append(line)
    
    # 간단한 요약 (처음 5개 문장)
    summary = '\n'.join(summary_lines[:5])
    
    return {
        "summary": summary,
        "total_lines": len(lines),
        "content_lines": len(summary_lines)
    }

def main():
    """MCP 인터페이스"""
    if len(sys.argv) != 2:
        print(json.dumps({"error": "사용법: python summarize_notes.py '<텍스트_파일_경로>'"}))
        sys.exit(1)
    
    try:
        file_path = sys.argv[1]
        
        # 파일 읽기
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # 내용 요약
        summary_result = summarize_content(text)
        
        # 일정 정보 추출
        schedules = extract_schedule_info(text)
        
        # 결과 조합
        result = {
            "summary": summary_result,
            "schedules": schedules,
            "extracted_count": len(schedules),
            "source_file": file_path
        }
        
        # 결과 출력 (JSON 형식)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except FileNotFoundError:
        print(json.dumps({"error": f"파일을 찾을 수 없습니다: {sys.argv[1]}"}, ensure_ascii=False))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"실행 오류: {e}"}, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main()