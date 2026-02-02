"""
2-1 데이터 조회 API 서버 실행 스크립트
프로젝트 루트에서 실행: python run_api.py 또는 py -3 run_api.py
"""
import os
import sys

# 프로젝트 루트를 path에 추가하고 작업 디렉터리로 이동 (로컬 실행 안정화)
root = os.path.dirname(os.path.abspath(__file__))
if root not in sys.path:
    sys.path.insert(0, root)
try:
    os.chdir(root)
except OSError:
    pass

try:
    from api.app import app
except ImportError as e:
    print("=" * 50)
    print("[오류] 모듈을 불러올 수 없습니다.")
    print(str(e))
    print()
    print("의존성 설치: pip install -r requirements_api.txt")
    print("=" * 50)
    sys.exit(1)

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').strip().lower() == 'true'
    base = f"http://localhost:{port}"
    print("=" * 50)
    print("현장배정 관리 시스템 (API + 프론트엔드)")
    print("=" * 50)
    print(f"  프론트엔드: {base}/")
    print(f"  API 정보:   {base}/api-info")
    print(f"  헬스:       {base}/api/health")
    print("=" * 50)
    print("종료: Ctrl+C")
    print()
    app.run(host='0.0.0.0', port=port, debug=debug)
