# Supabase SQL Editor & Table Editor 진행 가이드

Supabase에 테이블을 만들고 Table Editor에서 확인하는 방법입니다.

---

## 1. SQL Editor에서 테이블 생성

1. **Supabase 대시보드** 접속  
   https://supabase.com/dashboard

2. 프로젝트 **hhpofxpnztzibtpkpiar** 선택.

3. 왼쪽 메뉴에서 **SQL Editor** 클릭.

4. **+ New query** 선택.

5. 아래 SQL **전체**를 복사해 편집창에 붙여넣기 후 **Run** (또는 Ctrl+Enter).

```sql
-- 현장배정 관리 시스템 - Supabase 초기 테이블
-- 시트1(현장정보), 시트2(인력풀), 시트3(자격증풀) 구조에 맞춤

-- 현장정보 (시트1)
CREATE TABLE IF NOT EXISTS sites (
  "현장ID" TEXT PRIMARY KEY,
  "현장명" TEXT NOT NULL,
  "건축주명" TEXT DEFAULT '',
  "회사구분" TEXT DEFAULT '',
  "주소" TEXT DEFAULT '',
  "위도" TEXT DEFAULT '',
  "경도" TEXT DEFAULT '',
  "건축허가일" TEXT DEFAULT '',
  "착공예정일" TEXT DEFAULT '',
  "준공일" TEXT DEFAULT '',
  "현장상태" TEXT DEFAULT '건축허가',
  "특이사항" TEXT DEFAULT '',
  "담당소장ID" TEXT DEFAULT '',
  "담당소장명" TEXT DEFAULT '',
  "담당소장연락처" TEXT DEFAULT '',
  "사용자격증ID" TEXT DEFAULT '',
  "자격증명" TEXT DEFAULT '',
  "자격증소유자명" TEXT DEFAULT '',
  "자격증소유자연락처" TEXT DEFAULT '',
  "준공필증파일URL" TEXT DEFAULT '',
  "배정상태" TEXT DEFAULT '미배정',
  "등록일" TEXT DEFAULT '',
  "수정일" TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인력풀 (시트2)
CREATE TABLE IF NOT EXISTS personnel (
  "인력ID" TEXT PRIMARY KEY,
  "성명" TEXT NOT NULL,
  "직책" TEXT DEFAULT '',
  "소속" TEXT DEFAULT '',
  "연락처" TEXT DEFAULT '',
  "이메일" TEXT DEFAULT '',
  "보유자격증" TEXT DEFAULT '',
  "현재상태" TEXT DEFAULT '투입가능',
  "현재담당현장수" TEXT DEFAULT '0',
  "비고" TEXT DEFAULT '',
  "입사일" TEXT DEFAULT '',
  "등록일" TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 자격증풀 (시트3)
CREATE TABLE IF NOT EXISTS certificates (
  "자격증ID" TEXT PRIMARY KEY,
  "자격증명" TEXT NOT NULL,
  "자격증번호" TEXT DEFAULT '',
  "소유자ID" TEXT DEFAULT '',
  "소유자명" TEXT DEFAULT '',
  "소유자연락처" TEXT DEFAULT '',
  "발급기관" TEXT DEFAULT '',
  "취득일" TEXT DEFAULT '',
  "유효기간" TEXT DEFAULT '',
  "사용가능여부" TEXT DEFAULT '사용가능',
  "현재사용현장ID" TEXT DEFAULT '',
  "비고" TEXT DEFAULT '',
  "등록일" TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS 정책 (anon 키로 API 접근 허용)
ALTER TABLE sites ENABLE ROW LEVEL SECURITY;
ALTER TABLE personnel ENABLE ROW LEVEL SECURITY;
ALTER TABLE certificates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "sites_all" ON sites FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "personnel_all" ON personnel FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "certificates_all" ON certificates FOR ALL USING (true) WITH CHECK (true);
```

6. 실행이 끝나면 **Success** 메시지가 나옵니다. (이미 테이블이 있으면 일부 문장에서 "already exists"가 나올 수 있으며, 무시해도 됩니다.)

---

## 2. Table Editor에서 확인

1. 왼쪽 메뉴에서 **Table Editor** 클릭.

2. 상단/왼쪽에서 다음 테이블이 보이는지 확인합니다.

   | 테이블 | 설명 |
   |--------|------|
   | **sites** | 현장정보 (시트1) |
   | **personnel** | 인력풀 (시트2) |
   | **certificates** | 자격증풀 (시트3) |

3. 각 테이블을 클릭하면 컬럼 목록과 데이터(없으면 빈 테이블)를 볼 수 있습니다.

4. **Insert row**로 행을 추가하거나, 기존 행을 더블클릭해 수정할 수 있습니다.

---

## 3. 로컬에서 마이그레이션 실행 (선택)

이미 SQL Editor로 적용했다면 생략해도 됩니다.  
로컬에서 같은 스키마를 적용하려면:

```bash
# Node 사용 (권장)
npm run migrate:db

# 또는 Python
python supabase_migrate.py
```

`.env`에 `DATABASE_URL`이 설정되어 있어야 합니다.

---

## 4. 요약

| 단계 | 작업 |
|------|------|
| 1 | Supabase → **SQL Editor** → 위 SQL 붙여넣기 → **Run** |
| 2 | **Table Editor**에서 `sites`, `personnel`, `certificates` 확인 |

이후 API(`run_api.py` 또는 프론트)에서 Supabase URL/Key로 이 테이블들을 조회·수정할 수 있습니다.
