# Phase 2 - 2단계: 실시간 데이터 연동 API 개발

## 🎯 2단계 목표
Google Sheets와 HTML 앱을 실시간으로 연결하는 REST API 서버 구축

---

## 📋 2단계 구성

### 2-1. 데이터 조회 API (1일)
- GET 엔드포인트 구현
- 현장/인력/자격증 조회
- 필터링 및 검색 기능
- 통계 API

### 2-2. 데이터 수정 API (1일)
- POST/PUT 엔드포인트 구현
- 현장 정보 수정
- 소장 배정 기능
- 트랜잭션 관리

### 2-3. 실시간 동기화 (선택, 1일)
- 버전 관리 시스템
- 충돌 감지 및 해결
- 변경 이력 추적

---

## 🗂️ 학습 자료

### 가이드 문서 (순서대로)
1. **2-1_데이터조회API_가이드.md** ⭐⭐⭐☆☆
   - Flask 서버 기본 구조
   - GET 엔드포인트 전체
   - 필터링 및 검색
   - 예상 시간: 4시간

2. **2-2_데이터수정API_가이드.md** ⭐⭐⭐⭐☆
   - POST/PUT 엔드포인트
   - 소장 배정 로직
   - 관계 데이터 업데이트
   - 예상 시간: 4시간

3. **2-3_실시간동기화_가이드.md** ⭐⭐⭐⭐⭐ (선택)
   - 낙관적 잠금
   - 버전 관리
   - 충돌 해결
   - 예상 시간: 4시간

---

## 🏗️ 아키텍처 개요

```
┌─────────────────┐
│   HTML 앱       │
│  (프론트엔드)    │
└────────┬────────┘
         │ HTTP Request
         │ (JSON)
         ↓
┌─────────────────┐
│  Flask API      │
│  (백엔드 서버)   │
│  - 라우팅       │
│  - 비즈니스 로직 │
│  - 검증         │
└────────┬────────┘
         │ Google Sheets API
         ↓
┌─────────────────┐
│ Google Sheets   │
│  (데이터베이스)  │
│  - 시트1: 현장   │
│  - 시트2: 인력   │
│  - 시트3: 자격증 │
└─────────────────┘
```

---

## 📊 API 엔드포인트 전체 목록

### 데이터 조회 (GET)
```
GET  /api/sites                    # 현장 목록
GET  /api/sites/{id}               # 현장 상세
GET  /api/personnel                # 인력 목록
GET  /api/personnel/{id}           # 인력 상세
GET  /api/certificates             # 자격증 목록
GET  /api/certificates/{id}        # 자격증 상세
GET  /api/stats                    # 통계 정보
GET  /api/health                   # 서버 상태
```

### 데이터 수정 (POST/PUT)
```
POST /api/sites                    # 현장 생성
PUT  /api/sites/{id}               # 현장 수정
POST /api/sites/{id}/assign        # 소장 배정
POST /api/sites/{id}/unassign      # 소장 배정 해제
PUT  /api/personnel/{id}           # 인력 정보 수정
PUT  /api/certificates/{id}        # 자격증 정보 수정
```

---

## 🚀 빠른 시작

### 준비 사항
```bash
# 1. 필요 패키지 설치
pip install flask flask-cors python-dotenv

# 2. 프로젝트 구조 확인
현장배정현황/
├── api/
│   ├── __init__.py
│   ├── app.py                    # Flask 앱
│   ├── routes.py                 # 라우트 정의
│   ├── sheets_service.py         # Google Sheets 연동
│   ├── models.py                 # 데이터 모델
│   └── utils.py                  # 유틸리티 함수
├── .env                          # 환경 변수
└── requirements_api.txt          # API 의존성
```

### 실행 방법
```bash
# 개발 서버 실행
cd 현장배정현황
python api/app.py

# 서버 시작 확인
# Running on http://127.0.0.1:5000

# 테스트
curl http://localhost:5000/api/health
```

---

## 📝 개발 순서

### Day 1: 조회 API (2-1단계)
```
09:00 - 11:00  Flask 기본 구조 및 Google Sheets 연동
11:00 - 12:00  현장 목록 조회 API
13:00 - 15:00  필터링 및 상세 조회 API
15:00 - 17:00  인력/자격증 조회 API
17:00 - 18:00  통계 API 및 테스트
```

### Day 2: 수정 API (2-2단계)
```
09:00 - 11:00  현장 수정 API
11:00 - 12:00  소장 배정 로직 설계
13:00 - 15:00  소장 배정 API 구현
15:00 - 17:00  관계 데이터 자동 업데이트
17:00 - 18:00  에러 처리 및 검증
```

### Day 3: 동기화 (2-3단계, 선택)
```
09:00 - 12:00  버전 관리 시스템
13:00 - 15:00  충돌 감지 로직
15:00 - 17:00  변경 이력 추적
17:00 - 18:00  통합 테스트
```

---

## 🎯 완료 기준

### 2-1단계 완료
- [ ] Flask 서버 정상 실행
- [ ] 모든 GET 엔드포인트 작동
- [ ] 필터링 기능 정상 작동
- [ ] Postman/curl 테스트 통과

### 2-2단계 완료
- [ ] POST/PUT 엔드포인트 작동
- [ ] 소장 배정 기능 정상 작동
- [ ] 관계 데이터 자동 업데이트
- [ ] 에러 처리 정상 작동

### 2-3단계 완료 (선택)
- [ ] 버전 관리 시스템 작동
- [ ] 충돌 감지 정상 작동
- [ ] 변경 이력 조회 가능

---

## 📦 필요 패키지

### requirements_api.txt
```txt
# Flask 웹 프레임워크
flask==3.0.0
flask-cors==4.0.0

# Google Sheets API
google-api-python-client==2.110.0
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0

# 환경 변수 관리
python-dotenv==1.0.0

# 날짜/시간 처리
python-dateutil==2.8.2

# 유틸리티
requests==2.31.0
```

### 설치 방법
```bash
pip install -r requirements_api.txt
```

---

## 🔧 환경 변수 설정

### .env 파일 생성
```bash
# Google Sheets 설정
SPREADSHEET_ID=15fAEzkC9FCLA6sG1N--f69r-32WHoYLvmXcwED5xWzM
GOOGLE_API_KEY=AIzaSyBmQY3MXgpZT2UeHqaMHM6ecRKYV11ktLo

# Flask 설정
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000

# CORS 설정
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# API 보안 (선택)
API_KEY=your-secret-api-key-here
```

---

## 🧪 테스트 도구

### Postman 컬렉션
```json
{
  "info": {
    "name": "현장배정 관리 API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "현장 목록 조회",
      "request": {
        "method": "GET",
        "url": "http://localhost:5000/api/sites"
      }
    },
    {
      "name": "현장 상세 조회",
      "request": {
        "method": "GET",
        "url": "http://localhost:5000/api/sites/S001"
      }
    }
  ]
}
```

### curl 테스트
```bash
# 현장 목록
curl http://localhost:5000/api/sites

# 필터링
curl "http://localhost:5000/api/sites?company=더존종합건설&status=미배정"

# 현장 상세
curl http://localhost:5000/api/sites/S001

# 통계
curl http://localhost:5000/api/stats
```

---

## 📊 API 응답 형식

### 성공 응답
```json
{
  "success": true,
  "data": {
    "현장ID": "S001",
    "현장명": "평택 푸르지오",
    "배정상태": "배정완료"
  },
  "timestamp": "2026-01-06T14:30:00Z"
}
```

### 오류 응답
```json
{
  "success": false,
  "error": {
    "code": "SITE_NOT_FOUND",
    "message": "현장을 찾을 수 없습니다",
    "details": "현장ID S999가 존재하지 않습니다"
  },
  "timestamp": "2026-01-06T14:30:00Z"
}
```

---

## 🎨 프로젝트 구조

```
현장배정현황/
├── api/
│   ├── __init__.py
│   ├── app.py                    # Flask 앱 메인
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── sites.py              # 현장 라우트
│   │   ├── personnel.py          # 인력 라우트
│   │   ├── certificates.py       # 자격증 라우트
│   │   └── stats.py              # 통계 라우트
│   ├── services/
│   │   ├── __init__.py
│   │   ├── sheets_service.py     # Google Sheets 연동
│   │   ├── sync_service.py       # 동기화 서비스
│   │   └── validation.py         # 검증 로직
│   ├── models/
│   │   ├── __init__.py
│   │   ├── site.py               # 현장 모델
│   │   ├── personnel.py          # 인력 모델
│   │   └── certificate.py        # 자격증 모델
│   └── utils/
│       ├── __init__.py
│       ├── errors.py             # 에러 핸들러
│       ├── response.py           # 응답 포맷터
│       └── decorators.py         # 데코레이터
├── tests/
│   ├── test_sites.py
│   ├── test_personnel.py
│   └── test_integration.py
├── .env
├── requirements_api.txt
└── README_API.md
```

---

## 💡 개발 팁

### 1. 개발 서버 자동 재시작
```python
# app.py
if __name__ == '__main__':
    app.run(
        debug=True,      # 자동 재시작
        host='0.0.0.0',
        port=5000
    )
```

### 2. 로깅 설정
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
```

### 3. CORS 설정
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8000"],
        "methods": ["GET", "POST", "PUT", "DELETE"]
    }
})
```

---

## 🔒 보안 고려사항

### 1. API 키 검증 (선택)
```python
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != os.getenv('API_KEY'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/sites')
@require_api_key
def get_sites():
    pass
```

### 2. Rate Limiting
```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    default_limits=["100 per hour"]
)

@app.route('/api/sites')
@limiter.limit("10 per minute")
def get_sites():
    pass
```

---

## 📈 성능 최적화

### 1. 캐싱
```python
from functools import lru_cache
from datetime import datetime, timedelta

# 5분간 캐시
cache_time = timedelta(minutes=5)
last_cache_update = None
cached_data = None

def get_sites_cached():
    global last_cache_update, cached_data
    
    now = datetime.now()
    if (not last_cache_update or 
        now - last_cache_update > cache_time):
        cached_data = fetch_from_sheets()
        last_cache_update = now
    
    return cached_data
```

### 2. 배치 처리
```python
# 여러 ID를 한 번에 조회
@app.route('/api/sites/batch', methods=['POST'])
def get_sites_batch():
    site_ids = request.json.get('ids', [])
    sites = sheets_service.get_sites_by_ids(site_ids)
    return jsonify(sites)
```

---

## 🎯 다음 단계

2단계 완료 후:
- [ ] API 테스트 완료
- [ ] 문서화 완료
- [ ] HTML 앱 연동 준비
- [ ] 3단계 진행: HTML 앱 개선

---

**예상 총 소요 시간**: 8-12시간 (2-3일)  
**난이도**: ⭐⭐⭐⭐☆  
**다음 단계**: HTML 앱 API 연동 (Phase 2 - 3단계)
