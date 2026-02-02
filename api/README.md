# 2-1 데이터 조회 API + 2-2 데이터 수정 API

## 실행 방법

**프로젝트 루트**에서 실행하세요.

```bash
# 의존성 설치 (최초 1회)
pip install -r requirements_api.txt

# 서버 실행
python run_api.py
# 또는
python -m api.app
```

서버가 뜨면:
- API 정보: http://localhost:5000/
- 헬스: http://localhost:5000/api/health
- 현장 목록: http://localhost:5000/api/sites
- 통계: http://localhost:5000/api/stats

## 필요 조건

- 프로젝트 루트에 `token.pickle` (또는 첫 실행 시 Google 로그인으로 생성)
- 프로젝트 루트에 `client_secret_xxx.json` (Google Cloud OAuth2 클라이언트)
- Google Sheets 시트 이름: **시트1**, **시트2**, **시트3**

## 엔드포인트

### 조회 (GET)
| 경로 | 설명 |
|------|------|
| GET /api/sites | 현장 목록 (쿼리: company, status, state) |
| GET /api/sites/search?q=검색어 | 현장 검색 |
| GET /api/sites/<id> | 현장 상세 |
| GET /api/personnel | 인력 목록 (쿼리: status, role) |
| GET /api/personnel/<id> | 인력 상세 |
| GET /api/certificates | 자격증 목록 (쿼리: available=true/false) |
| GET /api/certificates/<id> | 자격증 상세 |
| GET /api/stats | 통계 |
| GET /api/health | 헬스 체크 |

### 수정 (2-2)
| 경로 | 설명 |
|------|------|
| POST /api/sites | 현장 생성 (body: 현장ID, 현장명, 회사구분, 주소 등) |
| PUT /api/sites/<id> | 현장 수정 |
| POST /api/sites/<id>/assign | 소장 배정 (body: manager_id, certificate_id) |
| POST /api/sites/<id>/unassign | 소장 배정 해제 |
| PUT /api/personnel/<id> | 인력 정보 수정 |
| PUT /api/certificates/<id> | 자격증 정보 수정 |
