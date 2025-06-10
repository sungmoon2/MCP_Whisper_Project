#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper STT Light Web App with Progress Bar
기능만 잘 되는 깡통 웹앱 - CSS 최소화, 기능 중심, 진척도 추가
"""

from flask import Flask, request, render_template, send_file, flash, redirect, url_for, jsonify
import os
import subprocess
import uuid
import zipfile
import threading
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import shutil

app = Flask(__name__)
app.secret_key = 'whisper-stt-webapp-secret-key-2025'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB 제한

# 디렉토리 경로 설정
PROJECT_ROOT = os.path.expanduser('~/whisper_project')
WEBAPP_ROOT = os.path.join(PROJECT_ROOT, 'webapp')
UPLOAD_FOLDER = os.path.join(WEBAPP_ROOT, 'uploads')
DATA_OUTPUT_PATH = os.path.join(PROJECT_ROOT, 'data', 'output')

# 필요한 디렉토리 생성
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_OUTPUT_PATH, exist_ok=True)

# Whisper 모델 설정
WHISPER_MODELS = {
    'tiny': 'tiny (73MB) - 매우 빠름, 낮은 품질',
    'base': 'base (139MB) - 빠름, 보통 품질', 
    'small': 'small (462MB) - 보통 속도, 중간 품질',
    'medium': 'medium (1.5GB) - 느림, 좋은 품질',
    'large-v3': 'large-v3 (2.9GB) - 매우 느림, 최고 품질',
    'large-v3-turbo': 'large-v3-turbo (1.6GB) - 보통 속도, 최고 품질 (추천)'
}

# 출력 형식 설정
OUTPUT_FORMATS = {
    'txt': 'txt - 순수 텍스트',
    'json': 'json - 타임스탬프 포함 상세 데이터',
    'srt': 'srt - 자막 파일 (영상용)',
    'vtt': 'vtt - 웹 자막 파일',
    'tsv': 'tsv - 표 형식 (Excel 호환)'
}

# 지원하는 파일 형식
ALLOWED_EXTENSIONS = {
    # 오디오 형식
    'mp3', 'wav', 'flac', 'm4a', 'ogg', 'wma', 'aac', '3gp', 'amr',
    # 비디오 형식  
    'mp4', 'mov', 'avi', 'mkv', 'webm', 'f4v', 'mpg', 'mpeg', 'wmv'
}

def allowed_file(filename):
    """허용된 파일 형식 확인"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_status_file_path(task_id):
    """상태 파일 경로 반환"""
    return os.path.join(DATA_OUTPUT_PATH, f"{task_id}_status.json")

def update_task_status(task_id, status, progress=0, message=""):
    """작업 상태 업데이트"""
    status_file = get_status_file_path(task_id)
    status_data = {
        'status': status,  # 'processing', 'completed', 'error'
        'progress': progress,  # 0-100
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    with open(status_file, 'w', encoding='utf-8') as f:
        json.dump(status_data, f, ensure_ascii=False, indent=2)

def get_task_status(task_id):
    """작업 상태 조회"""
    status_file = get_status_file_path(task_id)
    if os.path.exists(status_file):
        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {'status': 'not_found', 'progress': 0, 'message': '작업을 찾을 수 없습니다.'}

def run_whisper_background(input_file, model, output_formats, task_id):
    """백그라운드에서 Whisper 실행"""
    try:
        # 상태 업데이트: 시작
        update_task_status(task_id, 'processing', 10, 'STT 처리 시작...')
        
        # 출력 디렉토리 생성
        output_dir = os.path.join(DATA_OUTPUT_PATH, task_id)
        os.makedirs(output_dir, exist_ok=True)
        
        update_task_status(task_id, 'processing', 20, 'Whisper 모델 로딩 중...')
        
        # whisper 명령어 구성
        cmd = [
            'whisper', 
            input_file,
            '--model', model,
            '--language', 'Korean',
            '--device', 'cuda:0',  # GPU 0 강제 사용 (여유 메모리 24GB)
            '--output_dir', output_dir
        ]
        
        if output_formats:
            # 선택한 형식만 생성하기 위해 'all'로 실행 후 불필요한 파일 삭제
            if len(output_formats) > 1:
                cmd.extend(['--output_format', 'all'])
                print(f"다중 형식 선택됨 ({len(output_formats)}개) -> 선택한 형식만 유지")
            else:
                cmd.extend(['--output_format', output_formats[0]])
        
        print(f"실행 명령어: {' '.join(cmd)}")
        update_task_status(task_id, 'processing', 30, f'{model} 모델로 음성 분석 중...')
        
        # whisper 실행
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
        
        if result.returncode == 0:
            update_task_status(task_id, 'processing', 90, '결과 파일 정리 중...')
            
            # 선택하지 않은 형식의 파일들 삭제 (다중 형식 선택 시)
            if len(output_formats) > 1:
                cleanup_unwanted_files(task_id, output_formats)
            
            # 생성된 파일 확인
            files = get_result_files(task_id)
            if files:
                update_task_status(task_id, 'completed', 100, f'STT 처리 완료! {len(files)}개 파일 생성됨')
                return True, "처리 완료"
            else:
                update_task_status(task_id, 'error', 0, '결과 파일이 생성되지 않았습니다.')
                return False, "결과 파일 없음"
        else:
            error_msg = result.stderr or "알 수 없는 오류"
            update_task_status(task_id, 'error', 0, f'STT 처리 실패: {error_msg}')
            return False, error_msg
            
    except Exception as e:
        error_msg = f"예외 발생: {str(e)}"
        update_task_status(task_id, 'error', 0, error_msg)
        return False, error_msg

def cleanup_unwanted_files(task_id, selected_formats):
    """선택하지 않은 형식의 파일들 삭제"""
    output_dir = os.path.join(DATA_OUTPUT_PATH, task_id)
    if not os.path.exists(output_dir):
        return
    
    # 모든 가능한 형식
    all_formats = ['txt', 'json', 'srt', 'vtt', 'tsv']
    
    # 삭제할 형식 = 전체 형식 - 선택한 형식
    formats_to_delete = set(all_formats) - set(selected_formats)
    
    deleted_count = 0
    for filename in os.listdir(output_dir):
        if filename.endswith('_status.json'):
            continue  # 상태 파일은 건드리지 않음
            
        # 파일 확장자 확인
        for format_ext in formats_to_delete:
            if filename.endswith(f'.{format_ext}'):
                file_path = os.path.join(output_dir, filename)
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"삭제됨: {filename} (선택되지 않은 형식)")
                except Exception as e:
                    print(f"파일 삭제 실패: {filename}, 오류: {e}")
                break
    
    print(f"총 {deleted_count}개의 불필요한 파일이 삭제되었습니다.")

def get_result_files(task_id):
    """결과 파일 목록 조회"""
    output_dir = os.path.join(DATA_OUTPUT_PATH, task_id)
    files = []
    
    if os.path.exists(output_dir):
        for filename in os.listdir(output_dir):
            if not filename.endswith('_status.json'):  # 상태 파일 제외
                file_path = os.path.join(output_dir, filename)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    files.append({
                        'name': filename,
                        'size': f"{file_size / 1024:.1f} KB",
                        'path': file_path
                    })
    
    return files

def cleanup_temp_files(task_id):
    """임시 업로드 파일 삭제"""
    temp_dir = os.path.join(UPLOAD_FOLDER, task_id)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

def cleanup_status_file(task_id):
    """상태 파일 삭제"""
    status_file = get_status_file_path(task_id)
    if os.path.exists(status_file):
        os.remove(status_file)

def get_all_previews(task_id):
    """모든 생성된 파일의 미리보기 반환"""
    output_dir = os.path.join(DATA_OUTPUT_PATH, task_id)
    previews = []
    
    if not os.path.exists(output_dir):
        return previews
    
    # 형식별 우선순위 및 설명
    format_info = {
        '.txt': {'name': 'TXT (순수 텍스트)', 'priority': 1},
        '.json': {'name': 'JSON (타임스탬프 포함)', 'priority': 2}, 
        '.vtt': {'name': 'VTT (웹 자막)', 'priority': 3},
        '.srt': {'name': 'SRT (영상 자막)', 'priority': 4},
        '.tsv': {'name': 'TSV (표 형식)', 'priority': 5}
    }
    
    # 파일 스캔 및 미리보기 생성
    found_files = []
    for filename in os.listdir(output_dir):
        for ext in format_info.keys():
            if filename.endswith(ext):
                found_files.append((ext, filename, format_info[ext]))
                break
    
    # 우선순위 정렬
    found_files.sort(key=lambda x: x[2]['priority'])
    
    for ext, filename, info in found_files:
        file_path = os.path.join(output_dir, filename)
        try:
            content = extract_text_from_file(file_path, ext)
            if content:
                preview_content = content[:500] + "..." if len(content) > 500 else content
                previews.append({
                    'format': info['name'],
                    'filename': filename,
                    'content': preview_content,
                    'full_length': len(content)
                })
        except Exception as e:
            print(f"Preview extraction error for {filename}: {e}")
            continue
    
    return previews

def extract_text_from_file(file_path, ext):
    """다양한 형식 파일에서 원본 구조 그대로 추출"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if ext == '.txt':
                # TXT: 그대로 반환
                return f.read()
            elif ext == '.json':
                # JSON: 포맷팅된 JSON 구조로 반환
                import json
                data = json.load(f)
                return json.dumps(data, ensure_ascii=False, indent=2)
            elif ext in ['.vtt', '.srt', '.tsv']:
                # VTT, SRT, TSV: 원본 구조 그대로 반환
                return f.read()
    except Exception as e:
        # 오류 시 파일 읽기 재시도
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return f"파일 읽기 오류: {str(e)}"
    return None

@app.route('/')
def index():
    """메인 업로드 페이지"""
    return render_template('index.html', models=WHISPER_MODELS, formats=OUTPUT_FORMATS)

@app.route('/process', methods=['POST'])
def process_audio():
    """오디오 파일 처리 시작"""
    try:
        # 파일 업로드 확인
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '파일을 선택해주세요.'})
        
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'success': False, 'message': '올바른 파일을 선택해주세요.'})
        
        # 옵션 확인
        model = request.form.get('model')
        output_formats = request.form.getlist('formats')
        
        if not model or not output_formats:
            return jsonify({'success': False, 'message': '모델과 출력 형식을 선택해주세요.'})
        
        # 파일 저장 (시간 기반 task_id 생성)
        now = datetime.now()
        time_part = now.strftime("%Y%m%d_%H%M%S")
        uuid_part = str(uuid.uuid4())[:4]
        task_id = f"{time_part}_{uuid_part}"
        task_upload_dir = os.path.join(UPLOAD_FOLDER, task_id)
        os.makedirs(task_upload_dir, exist_ok=True)
        
        filename = secure_filename(file.filename)
        input_file_path = os.path.join(task_upload_dir, filename)
        file.save(input_file_path)
        
        print(f"파일 저장: {input_file_path}, 모델: {model}, 형식: {output_formats}")
        
        # 초기 상태 설정
        update_task_status(task_id, 'processing', 0, '파일 업로드 완료, 처리 준비 중...')
        
        # 백그라운드에서 처리 시작
        thread = threading.Thread(
            target=run_whisper_background,
            args=(input_file_path, model, output_formats, task_id)
        )
        thread.daemon = True
        thread.start()
        
        # 진척도 페이지로 리다이렉트
        return jsonify({'success': True, 'task_id': task_id, 'message': 'STT 처리 시작!'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류 발생: {str(e)}'})

@app.route('/api/status/<task_id>')
def api_status(task_id):
    """작업 상태 API"""
    status = get_task_status(task_id)
    return jsonify(status)

@app.route('/api/result/<task_id>')
def api_result(task_id):
    """결과 API"""
    files = get_result_files(task_id)
    previews = get_all_previews(task_id)
    
    # 처리 완료 후 정리
    cleanup_temp_files(task_id)
    
    return jsonify({
        'files': files,
        'previews': previews,
        'task_id': task_id
    })

@app.route('/download/<task_id>/<filename>')
def download_file(task_id, filename):
    """개별 파일 다운로드"""
    try:
        output_dir = os.path.join(DATA_OUTPUT_PATH, task_id)
        file_path = os.path.join(output_dir, filename)
        
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            flash('파일을 찾을 수 없습니다.')
            return redirect(url_for('show_result', task_id=task_id))
    except Exception as e:
        flash(f'다운로드 오류: {str(e)}')
        return redirect(url_for('show_result', task_id=task_id))

@app.route('/health')
def health_check():
    """MCP 도구에서 웹앱 상태 확인용 헬스체크 엔드포인트"""
    return jsonify({
        "status": "ok", 
        "message": "웹앱이 정상 작동 중입니다.",
        "timestamp": datetime.now().isoformat(),
        "available_models": list(WHISPER_MODELS.keys()),
        "available_formats": list(OUTPUT_FORMATS.keys())
    })

@app.route('/api/transcribe', methods=['POST'])
def api_transcribe():
    """MCP 도구용 STT 처리 API 엔드포인트"""
    try:
        # 파일 업로드 확인
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': '오디오 파일이 필요합니다.'})
        
        file = request.files['audio']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'success': False, 'error': '올바른 오디오 파일을 업로드해주세요.'})
        
        # 옵션 확인 (기본값 설정)
        model = request.form.get('model', 'small')
        formats_str = request.form.get('formats', 'txt')
        output_formats = formats_str.split(',') if formats_str else ['txt']
        
        if model not in WHISPER_MODELS:
            return jsonify({'success': False, 'error': f'지원하지 않는 모델입니다: {model}'})
        
        # 파일 저장 (시간 기반 task_id 생성)
        now = datetime.now()
        time_part = now.strftime("%Y%m%d_%H%M%S")
        uuid_part = str(uuid.uuid4())[:4]
        task_id = f"{time_part}_{uuid_part}"
        
        task_upload_dir = os.path.join(UPLOAD_FOLDER, task_id)
        os.makedirs(task_upload_dir, exist_ok=True)
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(task_upload_dir, filename)
        file.save(filepath)
        
        # 백그라운드 STT 처리 시작
        output_dir = os.path.join(DATA_OUTPUT_PATH, task_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # 초기 상태 파일 생성
        update_task_status(task_id, "processing", 0, "STT 처리를 시작합니다...")
        
        # 백그라운드 스레드로 처리
        thread = threading.Thread(
            target=run_whisper_background,
            args=(filepath, model, output_formats, task_id)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': f'STT 처리가 시작되었습니다. (모델: {model}, 형식: {", ".join(output_formats)})',
            'status_url': f'/api/status/{task_id}',
            'result_url': f'/api/result/{task_id}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'처리 중 오류가 발생했습니다: {str(e)}'})

@app.route('/download_all/<task_id>')
def download_all_files(task_id):
    """모든 결과 파일 ZIP 다운로드"""
    try:
        output_dir = os.path.join(DATA_OUTPUT_PATH, task_id)
        
        if not os.path.exists(output_dir):
            flash('결과 디렉토리를 찾을 수 없습니다.')
            return redirect(url_for('show_result', task_id=task_id))
        
        # ZIP 파일 생성
        zip_path = os.path.join(output_dir, f'{task_id}_results.zip')
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename in os.listdir(output_dir):
                if not filename.endswith('.zip') and not filename.endswith('_status.json'):
                    file_path = os.path.join(output_dir, filename)
                    if os.path.isfile(file_path):
                        zipf.write(file_path, filename)
        
        return send_file(zip_path, as_attachment=True)
        
    except Exception as e:
        flash(f'ZIP 생성 오류: {str(e)}')
        return redirect(url_for('show_result', task_id=task_id))

if __name__ == '__main__':
    print("=== Whisper STT Light Web App with Progress ===")
    print(f"프로젝트 경로: {PROJECT_ROOT}")
    print(f"업로드 폴더: {UPLOAD_FOLDER}")
    print(f"결과 저장: {DATA_OUTPUT_PATH}")
    print("브라우저에서 http://localhost:5000 접속")
    print("===============================================")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)