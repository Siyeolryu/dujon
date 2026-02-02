"""
2-1 데이터 조회 API 서버 실행 스크립트
프로젝트 루트에서 실행: python run_api.py
"""
import os
import sys

# 프로젝트 루트를 path에 추가
root = os.path.dirname(os.path.abspath(__file__))
if root not in sys.path:
    sys.path.insert(0, root)

# api.app 실행
from api.app import app

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').strip().lower() == 'true'
    print(f"🚀 2-1 데이터 조회 API 서버 시작: http://localhost:{port}")
    print(f"📖 API 정보: http://localhost:{port}/")
    print(f"❤️  헬스: http://localhost:{port}/api/health")
    app.run(host='0.0.0.0', port=port, debug=debug)
