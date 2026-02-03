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

-- RLS 정책 (선택: anon 키로 API 접근 허용)
ALTER TABLE sites ENABLE ROW LEVEL SECURITY;
ALTER TABLE personnel ENABLE ROW LEVEL SECURITY;
ALTER TABLE certificates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "sites_all" ON sites FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "personnel_all" ON personnel FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "certificates_all" ON certificates FOR ALL USING (true) WITH CHECK (true);
