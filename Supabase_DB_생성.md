# Supabase DB 생성 (Cursor → Supabase)

프로젝트 DB(sites, personnel, certificates)를 Supabase에 한 번에 생성하는 방법입니다.

**상세 단계(SQL 전체 포함):** [docs/Supabase_SQL_및_Table_Editor_가이드.md](docs/Supabase_SQL_및_Table_Editor_가이드.md)

---

## 방법 1: Supabase 대시보드에서 SQL 실행 (권장, 즉시 적용)

1. **Supabase 대시보드** 접속  
   https://supabase.com/dashboard

2. 프로젝트 **hhpofxpnztzibtpkpiar** 선택 (또는 본인 프로젝트).

3. 왼쪽 메뉴 **SQL Editor** 클릭.

4. **New query** 선택 후, 아래 중 하나 사용:
   - **파일:** `supabase/migrations/001_initial_tables.sql` 내용 전체 복사 후 붙여넣기
   - **가이드:** `docs/Supabase_SQL_및_Table_Editor_가이드.md`에 SQL 전체 수록됨

5. **Run** (또는 Ctrl+Enter) 실행.

6. 완료 시 **Table Editor**에서 `sites`, `personnel`, `certificates` 테이블이 보이면 성공입니다.

---

## 방법 2: 로컬에서 스크립트로 실행

`.env`에 DB 비밀번호 등이 설정된 후:

```bash
python supabase_migrate.py
```

또는 `DATABASE_URL`만 설정:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.hhpofxpnztzibtpkpiar.supabase.co:5432/postgres
```

- 비밀번호는 Supabase 대시보드 → **Project Settings** → **Database** → **Connection string**에서 확인 가능합니다.

---

## 생성되는 테이블

| 테이블        | 설명     |
|-------------|----------|
| **sites**   | 현장정보 (시트1) |
| **personnel** | 인력풀 (시트2) |
| **certificates** | 자격증풀 (시트3) |

RLS 정책도 함께 생성되어 API(anon key)로 조회·수정할 수 있습니다.
