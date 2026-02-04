"""
현장배정 관리 시스템 - REST API 서버 (2-1 조회 + 2-2 수정)
"""
import os
import json
import logging
import uuid
from datetime import datetime
from flask import Flask, jsonify, request, g, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# 프로젝트 루트 (프론트엔드 정적 파일 서빙용)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
logger = logging.getLogger(__name__)


@app.before_request
def assign_request_id():
    """요청별 request_id 부여 (에러 추적용)"""
    g.request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())[:8]


@app.after_request
def set_security_headers(response):
    """보안 헤더 설정 (XSS, Clickjacking 방지 등)"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # HTTPS 환경에서만 HSTS 설정
    if request.is_secure:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Content-Security-Policy 설정
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://dapi.kakao.com https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' https://*.supabase.co http://127.0.0.1:7242; "  # 개발용 디버깅 서버
        "frame-ancestors 'none';"
    )
    response.headers['Content-Security-Policy'] = csp
    
    return response


@app.after_request
def log_connection_errors(response):
    """4xx/5xx 응답 시 백엔드-프론트 연결 문제 확인용 로그 기록"""
    if response.status_code >= 400:
        try:
            request_id_val = getattr(g, 'request_id', '')
            data = None
            try:
                if response.is_json:
                    data = response.get_json(silent=True) or {}
            except Exception:
                pass
            error_code = (data or {}).get('error', {}).get('code', '')
            root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            log_path = os.path.join(root, '.cursor', 'debug.log')
            line = json.dumps({
                'location': 'api/app.py:after_request',
                'message': 'BE connection error response',
                'data': {
                    'path': request.path,
                    'method': request.method,
                    'status_code': response.status_code,
                    'error_code': error_code,
                    'request_id': request_id_val,
                },
                'timestamp': int(datetime.now().timestamp() * 1000),
                'sessionId': 'fe-be-connection',
                'hypothesisId': 'connection-fail',
            }, ensure_ascii=False) + '\n'
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(line)
        except Exception:
            pass
    return response


# CORS 설정: 로컬 개발 + 프로덕션 도메인 지원
ALLOWED_ORIGINS = os.getenv(
    'ALLOWED_ORIGINS',
    'http://localhost:5000,http://127.0.0.1:5000,http://localhost:8000,http://127.0.0.1:8000,http://localhost:8501,http://127.0.0.1:8501'
).split(',')

# 프로덕션 도메인 추가 (환경 변수로 설정, 쉼표 구분)
PRODUCTION_ORIGINS = os.getenv('PRODUCTION_ORIGINS', '').split(',')
if PRODUCTION_ORIGINS and PRODUCTION_ORIGINS[0]:
    ALLOWED_ORIGINS.extend([origin.strip() for origin in PRODUCTION_ORIGINS if origin.strip()])

CORS(app, resources={
    r"/api/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-API-Key", "If-Match"],
    }
})

# 라우트 등록 (2-1: GET 전용)
from api.routes import sites, personnel, certificates, stats

app.register_blueprint(sites.bp, url_prefix='/api')
app.register_blueprint(personnel.bp, url_prefix='/api')
app.register_blueprint(certificates.bp, url_prefix='/api')
app.register_blueprint(stats.bp, url_prefix='/api')


@app.route('/api-info')
def api_info():
    """API 정보 (JSON)"""
    return jsonify({
        'name': '현장배정 관리 API',
        'version': '1.0.0',
        'phase': '2-1 조회 + 2-2 수정 + 2-3 실시간 동기화(낙관적 잠금)',
        'endpoints': {
            'sites': 'GET/POST /api/sites',
            'sites_detail': 'GET/PUT /api/sites/<id>',
            'sites_search': 'GET /api/sites/search?q=검색어',
            'sites_assign': 'POST /api/sites/<id>/assign',
            'sites_unassign': 'POST /api/sites/<id>/unassign',
            'personnel': 'GET /api/personnel',
            'personnel_detail': 'GET/PUT /api/personnel/<id>',
            'certificates': 'GET /api/certificates',
            'certificates_detail': 'GET/PUT /api/certificates/<id>',
            'stats': 'GET /api/stats',
            'health': 'GET /api/health',
        },
    })


@app.route('/')
def index():
    """프론트엔드 메인 페이지 (로컬 확인용)"""
    return send_from_directory(PROJECT_ROOT, 'site-management.html')


@app.route('/streamlit-assets/<path:subpath>')
def serve_streamlit_assets(subpath):
    """Streamlit에서 정적 파일 접근용 (CSS, JS 등)"""
    if '..' in subpath:
        return jsonify({'error': 'Forbidden'}), 403
    
    # CSS 파일
    if subpath.endswith('.css'):
        return send_from_directory(os.path.join(PROJECT_ROOT, 'css'), subpath.replace('css/', ''))
    # JS 파일
    elif subpath.endswith('.js'):
        return send_from_directory(os.path.join(PROJECT_ROOT, 'js'), subpath.replace('js/', ''))
    else:
        return jsonify({'error': 'Not Found'}), 404


@app.route('/css/<path:subpath>')
def serve_css(subpath):
    """css 정적 파일"""
    if '..' in subpath:
        return jsonify({'error': 'Forbidden'}), 403
    return send_from_directory(os.path.join(PROJECT_ROOT, 'css'), subpath)


@app.route('/js/<path:subpath>')
def serve_js(subpath):
    """js 정적 파일"""
    if '..' in subpath:
        return jsonify({'error': 'Forbidden'}), 403
    return send_from_directory(os.path.join(PROJECT_ROOT, 'js'), subpath)


@app.route('/ui/<path:subpath>')
def serve_ui(subpath):
    """ui 정적 파일 (체크리스트 등)"""
    if '..' in subpath:
        return jsonify({'error': 'Forbidden'}), 403
    return send_from_directory(os.path.join(PROJECT_ROOT, 'ui'), subpath)


@app.route('/api/health')
def health():
    """헬스 체크"""
    return jsonify({
        'status': 'healthy',
        'service': 'site-management-api',
        'timestamp': datetime.now().isoformat(),
    })


@app.errorhandler(404)
def not_found(error):
    request_id = getattr(g, 'request_id', '')
    logger.warning(
        '404 NOT_FOUND path=%s method=%s request_id=%s',
        request.path, request.method, request_id,
    )
    return jsonify({
        'success': False,
        'error': {
            'code': 'NOT_FOUND',
            'message': '요청한 리소스를 찾을 수 없습니다',
            'request_id': request_id,
        },
    }), 404


@app.errorhandler(500)
def internal_error(error):
    request_id = getattr(g, 'request_id', '')
    logger.exception(
        '500 INTERNAL_ERROR path=%s method=%s request_id=%s error=%s',
        request.path, request.method, request_id, str(error),
    )
    return jsonify({
        'success': False,
        'error': {
            'code': 'INTERNAL_ERROR',
            'message': '서버 내부 오류가 발생했습니다',
            'request_id': request_id,
        },
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').strip().lower() == 'true'
    print(f"🚀 서버 시작: http://localhost:{port}")
    print(f"📖 API 정보: http://localhost:{port}/")
    print(f"❤️  헬스: http://localhost:{port}/api/health")
    app.run(host='0.0.0.0', port=port, debug=debug)
