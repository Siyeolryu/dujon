# GitHub ↔ Supabase 연동 가이드

**저장소**: [Siyeolryu/dujon](https://github.com/Siyeolryu/dujon)  
**Supabase 프로젝트**: 현장배정 관리 시스템 DB

---

## 1. DB 구축 (Supabase에 테이블 생성)

프로젝트용 테이블 **sites**, **personnel**, **certificates**를 Supabase에 만듭니다.

### 방법 A: 스크립트로 한 번에 적용 (권장)

`.env`에 `DATABASE_URL`이 설정된 상태에서:

```bash
python supabase_migrate.py
```

- `supabase/migrations/001_initial_tables.sql` 내용이 Supabase DB에 적용됩니다.
- 최초 1회 실행하면 됩니다. 이미 테이블이 있으면 "already exists" 메시지가 나올 수 있습니다.

### 방법 B: Supabase 대시보드에서 SQL 실행

1. [Supabase Dashboard](https://supabase.com/dashboard) → 프로젝트 선택
2. **SQL Editor** 메뉴
3. `supabase/migrations/001_initial_tables.sql` 파일 내용 전체 복사 후 붙여넣기
4. **Run** 실행

### 생성되는 테이블

| 테이블 | 설명 | 용도 |
|--------|------|------|
| **sites** | 현장정보 | 시트1 대응 |
| **personnel** | 인력풀 | 시트2 대응 |
| **certificates** | 자격증풀 | 시트3 대응 |

RLS(Row Level Security) 정책도 함께 생성되어, API 키로 조회·수정이 가능합니다.

---

## 2. GitHub ↔ Supabase 연결 (대시보드)

Supabase 프로젝트와 GitHub 저장소를 연결하면, 브랜치 연동·자동 배포 등을 사용할 수 있습니다.

### 단계

1. **Supabase Dashboard** 접속  
   https://supabase.com/dashboard

2. **프로젝트 선택**  
   현장배정용 Supabase 프로젝트 클릭

3. **Project Settings** (왼쪽 하단 톱니바퀴) → **Integrations**

4. **GitHub** 항목에서 **Authorize GitHub** 클릭  
   - GitHub 로그인/권한 허용

5. **Connect repository**  
   - Organization/계정: 본인 계정 선택  
   - Repository: **Siyeolryu/dujon** 선택  
   - Supabase 디렉터리 경로: `supabase` (기본값, 프로젝트 루트의 `supabase` 폴더)

6. **Enable integration** 클릭

7. (선택) **Deploy to production**  
   - production 브랜치(main)에 푸시 시 마이그레이션·Edge Functions 등 자동 배포  
   - 필요하면 켜두고, 마이그레이션은 위 1번으로 이미 적용했다면 그대로 사용 가능

### 참고 문서

- [Supabase – GitHub integration](https://supabase.com/docs/guides/deployment/branching/github-integration)

---

## 3. 연동 후 확인

- **DB**: Supabase **Table Editor**에서 `sites`, `personnel`, `certificates` 테이블이 보이면 구축 완료.
- **연결 테스트**: `python db_connect_test.py` 로 DB 연결 확인.
- **API**: `DB_BACKEND=supabase`, `SUPABASE_URL`, `SUPABASE_KEY` 설정 후 `python run_api.py`로 API 서버를 띄우고 `/api/sites` 등으로 조회 테스트.

---

## 4. 요약

| 항목 | 내용 |
|------|------|
| GitHub 저장소 | https://github.com/Siyeolryu/dujon |
| DB 구축 | `python supabase_migrate.py` 또는 SQL Editor에서 마이그레이션 실행 |
| GitHub 연동 | Supabase Dashboard → Project Settings → Integrations → GitHub → dujon 연결 |
