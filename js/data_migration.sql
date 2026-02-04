-- =====================================================
-- Dujon 기존 데이터 마이그레이션 스크립트
-- Google Sheets CSV → Supabase
-- =====================================================

-- ※ 이 스크립트는 CSV 데이터를 Supabase로 마이그레이션합니다.
-- ※ 실행 전 supabase_migration_v2.sql이 먼저 실행되어야 합니다.

-- =====================================================
-- 1. 인력(소장) 데이터 마이그레이션
-- =====================================================

-- 인력풀_샘플데이터.csv → personnel 테이블
INSERT INTO personnel (legacy_id, company_id, name, position, phone, email, status, join_date, notes, created_at)
SELECT 
    인력ID,
    (SELECT id FROM companies WHERE name = 소속 LIMIT 1),
    성명,
    직책,
    연락처,
    이메일,
    CASE 현재상태
        WHEN '투입중' THEN '투입중'::personnel_status
        WHEN '투입가능' THEN '투입가능'::personnel_status
        WHEN '휴직' THEN '휴직'::personnel_status
        WHEN '퇴사' THEN '퇴사'::personnel_status
        ELSE '투입가능'::personnel_status
    END,
    입사일::DATE,
    비고,
    등록일::TIMESTAMPTZ
FROM temp_personnel_import;

-- ※ 실제 마이그레이션 시 CSV를 temp 테이블로 먼저 로드해야 함
-- COPY temp_personnel_import FROM '/path/to/인력풀_샘플데이터.csv' WITH CSV HEADER;

-- =====================================================
-- 2. 자격증 데이터 마이그레이션
-- =====================================================

-- 자격증풀_샘플데이터.csv → certificates 테이블
INSERT INTO certificates (legacy_id, personnel_id, cert_type_id, cert_number, issued_date, expiry_date, status, notes, created_at)
SELECT 
    자격증ID,
    (SELECT id FROM personnel WHERE legacy_id = 소유자ID LIMIT 1),
    (SELECT id FROM certificate_types WHERE name = 자격증명 LIMIT 1),
    자격증번호,
    취득일::DATE,
    유효기간::DATE,
    CASE 사용가능여부
        WHEN '사용중' THEN '사용중'::certificate_status
        WHEN '사용가능' THEN '사용가능'::certificate_status
        WHEN '만료' THEN '만료'::certificate_status
        ELSE '사용가능'::certificate_status
    END,
    비고,
    등록일::TIMESTAMPTZ
FROM temp_certificate_import;

-- =====================================================
-- 3. 현장 데이터 마이그레이션
-- =====================================================

-- 현장정보_샘플데이터.csv → sites 테이블
INSERT INTO sites (legacy_id, company_id, name, address, latitude, longitude, permit_date, start_date, end_date, status, assignment_status, notes, completion_doc_url, created_at, updated_at)
SELECT 
    현장ID,
    (SELECT id FROM companies WHERE name = 회사구분 LIMIT 1),
    현장명,
    주소,
    위도::DECIMAL,
    경도::DECIMAL,
    건축허가일::DATE,
    착공예정일::DATE,
    준공일::DATE,
    CASE 현장상태
        WHEN '건축허가' THEN '건축허가'::site_status
        WHEN '착공예정' THEN '착공예정'::site_status
        WHEN '착공' THEN '착공'::site_status
        WHEN '진행중' THEN '진행중'::site_status
        WHEN '준공예정' THEN '준공예정'::site_status
        WHEN '준공완료' THEN '준공완료'::site_status
        ELSE '건축허가'::site_status
    END,
    CASE 배정상태
        WHEN '배정완료' THEN '배정완료'::assignment_status
        WHEN '배정중' THEN '배정중'::assignment_status
        ELSE '미배정'::assignment_status
    END,
    특이사항,
    준공필증파일URL,
    등록일::TIMESTAMPTZ,
    수정일::TIMESTAMPTZ
FROM temp_site_import;

-- =====================================================
-- 4. 배정 관계 마이그레이션
-- =====================================================

-- 기존 담당소장ID 기반으로 site_assignments 생성
INSERT INTO site_assignments (site_id, personnel_id, role, status, assigned_at)
SELECT 
    s.id,
    p.id,
    '담당'::assignment_role,
    '배정중'::assignment_active_status,
    s.created_at
FROM sites s
JOIN personnel p ON (
    SELECT 담당소장ID FROM temp_site_import WHERE 현장ID = s.legacy_id
) = p.legacy_id
WHERE (SELECT 담당소장ID FROM temp_site_import WHERE 현장ID = s.legacy_id) IS NOT NULL
  AND (SELECT 담당소장ID FROM temp_site_import WHERE 현장ID = s.legacy_id) != '';

-- 자격증-현장 배정 관계 마이그레이션
INSERT INTO certificate_assignments (certificate_id, site_id, status, assigned_at)
SELECT 
    c.id,
    s.id,
    '배정중'::assignment_active_status,
    s.created_at
FROM certificates c
JOIN sites s ON (
    SELECT 현재사용현장ID FROM temp_certificate_import WHERE 자격증ID = c.legacy_id
) = s.legacy_id
WHERE (SELECT 현재사용현장ID FROM temp_certificate_import WHERE 자격증ID = c.legacy_id) IS NOT NULL
  AND (SELECT 현재사용현장ID FROM temp_certificate_import WHERE 자격증ID = c.legacy_id) != '';

-- =====================================================
-- 5. 데이터 검증 쿼리
-- =====================================================

-- 마이그레이션 후 데이터 검증
SELECT '회사' as table_name, COUNT(*) as count FROM companies
UNION ALL
SELECT '자격증종류', COUNT(*) FROM certificate_types
UNION ALL
SELECT '인력', COUNT(*) FROM personnel
UNION ALL
SELECT '자격증', COUNT(*) FROM certificates
UNION ALL
SELECT '현장', COUNT(*) FROM sites
UNION ALL
SELECT '현장배정', COUNT(*) FROM site_assignments
UNION ALL
SELECT '자격증배정', COUNT(*) FROM certificate_assignments;

-- 배정 현황 검증
SELECT 
    s.legacy_id as 현장ID,
    s.name as 현장명,
    s.assignment_status as 배정상태,
    COUNT(sa.id) as 배정인원수,
    STRING_AGG(p.name, ', ') as 배정소장
FROM sites s
LEFT JOIN site_assignments sa ON s.id = sa.site_id AND sa.status = '배정중'
LEFT JOIN personnel p ON sa.personnel_id = p.id
GROUP BY s.id, s.legacy_id, s.name, s.assignment_status
ORDER BY s.legacy_id;

-- =====================================================
-- 6. Python 마이그레이션 스크립트 (참고용)
-- =====================================================

/*
import pandas as pd
from supabase import create_client

# Supabase 연결
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1. 회사 데이터 (이미 마이그레이션 SQL에서 처리)

# 2. 인력 데이터 마이그레이션
df_personnel = pd.read_csv('인력풀_샘플데이터.csv')
for _, row in df_personnel.iterrows():
    # 회사 ID 조회
    company = supabase.table('companies').select('id').eq('name', row['소속']).single().execute()
    
    data = {
        'legacy_id': row['인력ID'],
        'company_id': company.data['id'] if company.data else None,
        'name': row['성명'],
        'position': row['직책'],
        'phone': row['연락처'],
        'email': row['이메일'],
        'status': row['현재상태'],
        'join_date': row['입사일'],
        'notes': row['비고']
    }
    supabase.table('personnel').insert(data).execute()

# 3. 자격증 데이터 마이그레이션
df_cert = pd.read_csv('자격증풀_샘플데이터.csv')
for _, row in df_cert.iterrows():
    # 인력 ID 조회
    personnel = supabase.table('personnel').select('id').eq('legacy_id', row['소유자ID']).single().execute()
    # 자격증 종류 ID 조회
    cert_type = supabase.table('certificate_types').select('id').eq('name', row['자격증명']).single().execute()
    
    data = {
        'legacy_id': row['자격증ID'],
        'personnel_id': personnel.data['id'] if personnel.data else None,
        'cert_type_id': cert_type.data['id'] if cert_type.data else None,
        'cert_number': row['자격증번호'],
        'issued_date': row['취득일'],
        'expiry_date': row['유효기간'],
        'status': row['사용가능여부'],
        'notes': row['비고']
    }
    supabase.table('certificates').insert(data).execute()

# 4. 현장 데이터 마이그레이션 (유사한 방식)
*/
