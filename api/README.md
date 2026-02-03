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

## DB: Google Sheets 연동

현장등록·소장(인력)등록·자격증등록 등 모든 데이터는 **아래 Google 스프레드시트**에 저장됩니다.

- **DB 스프레드시트:** [https://docs.google.com/spreadsheets/d/15fAEzkC9FCLA6sG1N--f69r-32WHoYLvmXcwED5xWzM/edit](https://docs.google.com/spreadsheets/d/15fAEzkC9FCLA6sG1N--f69r-32WHoYLvmXcwED5xWzM/edit)
- `.env`에서 `SPREADSHEET_ID`로 덮어쓰기 가능 (미설정 시 위 스프레드시트 사용)
- 프로젝트 루트에 `token.pickle` (또는 첫 실행 시 Google 로그인으로 생성)
- 프로젝트 루트에 `client_secret_xxx.json` (Google Cloud OAuth2 클라이언트)
- 시트 탭 이름: `.env`에서 `SHEET_SITES`, `SHEET_PERSONNEL`, `SHEET_CERTIFICATES`로 지정 가능  
  미설정 시 **시트1**(현장정보), **시트2**(인력풀), **시트3**(자격증풀) 사용  
  구축가이드대로 만들었다면 `SHEET_SITES=현장정보`, `SHEET_PERSONNEL=인력풀`, `SHEET_CERTIFICATES=자격증풀` 로 설정

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

### 수정 (2-2, Google Sheets에 저장)
| 경로 | 설명 |
|------|------|
| POST /api/sites | 현장 등록 (Google Sheets 현장정보 시트에 추가) |
| PUT /api/sites/<id> | 현장 수정 |
| POST /api/sites/<id>/assign | 소장 배정 (body: manager_id, certificate_id) |
| POST /api/sites/<id>/unassign | 소장 배정 해제 |
| PUT /api/personnel/<id> | 인력 정보 수정 |
| POST /api/certificates | 자격증 등록 (Google Sheets 자격증풀 시트에 추가, 자격증ID·소유자ID 자동 부여) |
| PUT /api/certificates/<id> | 자격증 정보 수정 |
