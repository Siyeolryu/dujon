"""
현장배정 관리 시스템 - REST API 서버 (2-1 조회 + 2-2 수정)
"""
import os
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CORS(app, resources={
    r"/api/*": {
        "origins": os.getenv('ALLOWED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000').split(','),
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


@app.route('/')
def index():
    """API 정보"""
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
    return jsonify({
        'success': False,
        'error': {
            'code': 'NOT_FOUND',
            'message': '요청한 리소스를 찾을 수 없습니다',
        },
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': {
            'code': 'INTERNAL_ERROR',
            'message': '서버 내부 오류가 발생했습니다',
        },
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').strip().lower() == 'true'
    print(f"🚀 서버 시작: http://localhost:{port}")
    print(f"📖 API 정보: http://localhost:{port}/")
    print(f"❤️  헬스: http://localhost:{port}/api/health")
    app.run(host='0.0.0.0', port=port, debug=debug)
