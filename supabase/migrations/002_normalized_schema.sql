-- =====================================================
-- Dujon 현장배정 관리 시스템 - 정규화된 DB 스키마 (v2)
-- =====================================================

-- 1. ENUM 타입 생성
DO $$ BEGIN CREATE TYPE personnel_status AS ENUM ('투입가능', '투입중', '휴직', '퇴사'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE certificate_status AS ENUM ('사용가능', '사용중', '만료'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE site_status AS ENUM ('건축허가', '착공예정', '착공', '진행중', '준공예정', '준공완료'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE assignment_status AS ENUM ('미배정', '배정중', '배정완료'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE assignment_role AS ENUM ('담당', '보조', '임시'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE assignment_active_status AS ENUM ('배정중', '해제'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- 2. 참조 테이블
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    short_name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS certificate_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 주요 테이블
CREATE TABLE IF NOT EXISTS personnel (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    legacy_id TEXT UNIQUE,
    company_id UUID REFERENCES companies(id),
    name TEXT NOT NULL,
    position TEXT DEFAULT '소장',
    phone TEXT,
    email TEXT,
    status personnel_status DEFAULT '투입가능',
    current_site_count INTEGER DEFAULT 0,
    join_date DATE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS certificates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    legacy_id TEXT UNIQUE,
    personnel_id UUID REFERENCES personnel(id),
    cert_type_id UUID REFERENCES certificate_types(id),
    cert_number TEXT,
    issued_date DATE,
    expiry_date DATE,
    status certificate_status DEFAULT '사용가능',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    legacy_id TEXT UNIQUE,
    company_id UUID REFERENCES companies(id),
    name TEXT NOT NULL,
    owner_name TEXT,
    address TEXT,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    permit_date DATE,
    start_date DATE,
    end_date DATE,
    status site_status DEFAULT '건축허가',
    assignment_status assignment_status DEFAULT '미배정',
    notes TEXT,
    completion_doc_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. 배정 관계 테이블 (N:M)
CREATE TABLE IF NOT EXISTS site_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    personnel_id UUID NOT NULL REFERENCES personnel(id) ON DELETE CASCADE,
    role assignment_role DEFAULT '담당',
    status assignment_active_status DEFAULT '배정중',
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    released_at TIMESTAMPTZ,
    notes TEXT,
    UNIQUE(site_id, personnel_id, status)
);

CREATE TABLE IF NOT EXISTS certificate_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    certificate_id UUID NOT NULL REFERENCES certificates(id) ON DELETE CASCADE,
    site_id UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    status assignment_active_status DEFAULT '배정중',
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    released_at TIMESTAMPTZ,
    notes TEXT,
    UNIQUE(certificate_id, site_id, status)
);

-- 5. 인덱스
CREATE INDEX IF NOT EXISTS idx_personnel_company ON personnel(company_id);
CREATE INDEX IF NOT EXISTS idx_personnel_status ON personnel(status);
CREATE INDEX IF NOT EXISTS idx_personnel_legacy ON personnel(legacy_id);
CREATE INDEX IF NOT EXISTS idx_certificates_personnel ON certificates(personnel_id);
CREATE INDEX IF NOT EXISTS idx_certificates_type ON certificates(cert_type_id);
CREATE INDEX IF NOT EXISTS idx_certificates_status ON certificates(status);
CREATE INDEX IF NOT EXISTS idx_certificates_legacy ON certificates(legacy_id);
CREATE INDEX IF NOT EXISTS idx_sites_company ON sites(company_id);
CREATE INDEX IF NOT EXISTS idx_sites_status ON sites(status);
CREATE INDEX IF NOT EXISTS idx_sites_assignment ON sites(assignment_status);
CREATE INDEX IF NOT EXISTS idx_sites_legacy ON sites(legacy_id);
CREATE INDEX IF NOT EXISTS idx_site_assignments_site ON site_assignments(site_id);
CREATE INDEX IF NOT EXISTS idx_site_assignments_personnel ON site_assignments(personnel_id);
CREATE INDEX IF NOT EXISTS idx_cert_assignments_cert ON certificate_assignments(certificate_id);
CREATE INDEX IF NOT EXISTS idx_cert_assignments_site ON certificate_assignments(site_id);

-- 6. RLS 정책
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE certificate_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE personnel ENABLE ROW LEVEL SECURITY;
ALTER TABLE certificates ENABLE ROW LEVEL SECURITY;
ALTER TABLE sites ENABLE ROW LEVEL SECURITY;
ALTER TABLE site_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE certificate_assignments ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "companies_all" ON companies;
DROP POLICY IF EXISTS "cert_types_all" ON certificate_types;
DROP POLICY IF EXISTS "personnel_all" ON personnel;
DROP POLICY IF EXISTS "certificates_all" ON certificates;
DROP POLICY IF EXISTS "sites_all" ON sites;
DROP POLICY IF EXISTS "site_assignments_all" ON site_assignments;
DROP POLICY IF EXISTS "cert_assignments_all" ON certificate_assignments;

CREATE POLICY "companies_all" ON companies FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "cert_types_all" ON certificate_types FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "personnel_all" ON personnel FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "certificates_all" ON certificates FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "sites_all" ON sites FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "site_assignments_all" ON site_assignments FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "cert_assignments_all" ON certificate_assignments FOR ALL USING (true) WITH CHECK (true);

-- 7. 기본 데이터
INSERT INTO companies (name, short_name) VALUES
    ('더존종합건설', '종합건설'),
    ('더존하우징', '하우징')
ON CONFLICT (name) DO NOTHING;

INSERT INTO certificate_types (name, description) VALUES
    ('건축기사', '건축기사 자격증'),
    ('건축산업기사', '건축산업기사 자격증'),
    ('건설초급', '건설초급 자격증'),
    ('건설중급', '건설중급 자격증'),
    ('건설고급', '건설고급 자격증')
ON CONFLICT (name) DO NOTHING;
