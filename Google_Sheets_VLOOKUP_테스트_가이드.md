# Google Sheets 연동 + VLOOKUP 테스트 가이드

## 1. 구조 검증 테스트 (API 호출 없음)

코드 구조·함수·VLOOKUP 컬럼 정의만 검증합니다. **Google 시트 접속 없이** 실행 가능합니다.

### 방법 A: 전용 스크립트

```bash
python test_google_sheets_vlookup.py
```

**검증 항목**
- **1-3 VLOOKUP 수식**: `apply_vlookup_formulas.py`에 `get_google_sheets_service`, `insert_column`, `add_header`, `apply_formula_column`, `COLUMNS_TO_ADD`(5개 컬럼), `main` 존재 및 `COLUMNS_TO_ADD` 헤더가 담당소장명·담당소장연락처·자격증명·자격증소유자명·자격증소유자연락처인지
- **Sheets 서비스**: `api.services.sheets_service`에 `read_sheet`, `update_cell`, `update_row`, `batch_update`, `find_row_by_id`, `append_row`, `get_all_sites` 등 메서드 존재

### 방법 B: 전체 테스트 스위트

```bash
python run_all_tests.py
```

실행 후 `test_report.html`이 생성되며, 1단계(1-1 검증, 1-2 조건부 서식, **1-3 VLOOKUP**)와 2단계(**Sheets 서비스** 포함) 결과가 포함됩니다.

---

## 2. 실제 Google Sheets 연동 테스트 (선택)

실제 스프레드시트에 접속해 VLOOKUP 적용을 테스트하려면 아래 조건이 필요합니다.

1. **`.env`** 에 시트 ID 설정  
   `SPREADSHEET_ID=실제_스프레드시트_ID`
2. **인증 파일**  
   프로젝트 루트에 `client_secret_xxx.json` (Google Cloud OAuth 클라이언트) 또는 `token.pickle` (이미 로그인된 경우)
3. **필요 패키지**  
   `pip install google-api-python-client google-auth-oauthlib google-auth-httplib2`

### VLOOKUP 실제 적용

```bash
python apply_vlookup_formulas.py
```

- 시트1이 **17컬럼**일 때만 동작합니다. (이미 22컬럼이면 “이미 적용됨” 등으로 스킵될 수 있음)
- 실행 시 시트1에 **5개 컬럼**이 추가되고, 담당소장명·담당소장연락처·자격증명·자격증소유자명·자격증소유자연락처에 VLOOKUP 수식이 들어갑니다.

### API로 시트 읽기 테스트

API 서버를 띄운 뒤 시트 데이터를 조회해 볼 수 있습니다.

```bash
# 터미널 1: .env 로드 후 API 실행
python run_api.py

# 터미널 2 또는 브라우저
# GET http://localhost:5000/api/sites → 시트1 데이터 조회
```

---

## 3. 요약

| 테스트 종류           | 명령어                          | Google 시트 접속 |
|----------------------|----------------------------------|------------------|
| 구조 검증 (VLOOKUP+Sheets) | `python test_google_sheets_vlookup.py` | 불필요           |
| 전체 구조 검증       | `python run_all_tests.py`       | 불필요           |
| 실제 VLOOKUP 적용    | `python apply_vlookup_formulas.py` | 필요 (.env + 인증) |
| API로 시트 조회      | `python run_api.py` 후 `/api/sites` | 필요 (.env + 인증) |

Python이 설치되어 있지만 `python` 명령이 동작하지 않으면, `py test_google_sheets_vlookup.py` 또는 가상환경의 `python` 경로를 사용해 실행하면 됩니다.
