# Supabase DB 연동 가이드

Google Workspace/Sheets 대신 **Supabase**를 DB로 사용하도록 설정되어 있습니다.

---

## 1. 환경 변수 (.env)

| 변수 | 설명 | 예시 |
|------|------|------|
| `DB_BACKEND` | `supabase` 또는 `sheets` | `supabase` |
| `SUPABASE_URL` | Supabase 프로젝트 URL | `https://xxxx.supabase.co` |
| `SUPABASE_KEY` | API 키 (anon 또는 service_role) | `sbp_xxx` 또는 `eyJ...` |

- **SUPABASE_URL**: [Supabase 대시보드](https://supabase.com/dashboard) → 프로젝트 선택 → **Project Settings** → **API** → Project URL
- **SUPABASE_KEY**: 같은 화면에서 **anon public** 또는 **service_role** 키 복사

`.env`에 `SUPABASE_URL`을 반드시 입력하세요. 현재 `SUPABASE_KEY`는 설정되어 있으며, URL만 프로젝트에 맞게 바꾸면 됩니다.

---

## 2. Supabase 테이블 생성

프로젝트에 포함된 마이그레이션으로 테이블을 만듭니다.

1. Supabase 대시보드 → **SQL Editor**
2. `supabase/migrations/001_initial_tables.sql` 파일 내용을 복사해 붙여넣기
3. **Run** 실행

생성되는 테이블:

- **sites** – 현장정보 (시트1 대응)
- **personnel** – 인력풀 (시트2 대응)
- **certificates** – 자격증풀 (시트3 대응)

컬럼명은 한글(현장ID, 현장명, 담당소장ID 등)으로 되어 있어 기존 API 응답과 동일합니다.

---

## 3. API 서버 실행

```bash
pip install -r requirements_api.txt
python run_api.py
```

`DB_BACKEND=supabase`이고 `SUPABASE_URL`, `SUPABASE_KEY`가 설정되어 있으면 API가 Supabase를 사용합니다.

---

## 4. Google Sheets로 되돌리기

`.env`에서 다음처럼 변경하면 다시 Sheets를 사용합니다.

```env
DB_BACKEND=sheets
SPREADSHEET_ID=your_spreadsheet_id
```

그리고 프로젝트 루트에 `client_secret_xxx.json`, `token.pickle` 등 Google 인증 파일이 있어야 합니다.

---

## 5. 요약

| 항목 | 내용 |
|------|------|
| 기본 DB | Supabase (`DB_BACKEND=supabase`) |
| 토큰 | `.env`의 `SUPABASE_KEY`에 설정됨 |
| 필수 설정 | `.env`에 **SUPABASE_URL** 입력 (프로젝트 URL) |
| 테이블 | `supabase/migrations/001_initial_tables.sql` 실행 |

URL만 설정하면 Supabase를 DB로 사용할 수 있습니다.
