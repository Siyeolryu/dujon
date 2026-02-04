# data_migration.sql Supabase 적용 점검 결과

**점검 일시**: 2026-02-04  
**대상**: `js/data_migration.sql` 및 Supabase DB 상태

---

## 1. 요약

| 항목 | 상태 | 비고 |
|------|------|------|
| 정규화 스키마(002) | ✅ 적용됨 | companies, certificate_types, personnel, certificates, sites, site_assignments, certificate_assignments |
| 마스터 데이터 | ✅ 정상 | 회사 2, 자격증종류 5 |
| 인력/자격증/현장 데이터 | ✅ 정상 | 각 5건, legacy_id 매핑 일치 |
| 현장배정 / 자격증배정 | ⚠️ 0건 | CSV에 담당소장ID·사용자격증ID 없음 → 정상 |

**결론**: data_migration.sql이 기대하는 **스키마와 핵심 데이터는 Supabase에 정상 반영**되어 있습니다. 배정 테이블이 0건인 것은 샘플 CSV에 배정 정보(담당소장ID, 사용자격증ID)가 비어 있기 때문이며, 스크립트 오류가 아닙니다.

---

## 2. 스키마 점검

- **Supabase `list_migrations`**: `[]` (마이그레이션 이력 테이블에는 기록 없음. SQL을 대시보드 등에서 수동 적용했을 수 있음)
- **public 스키마 테이블**: 아래 7개 테이블 존재, 컬럼/타입/ENUM은 `supabase/migrations/002_normalized_schema.sql`과 일치

| 테이블 | RLS | 행 수(점검 시) |
|--------|-----|----------------|
| companies | ✅ | 2 |
| certificate_types | ✅ | 5 |
| personnel | ✅ | 5 |
| certificates | ✅ | 5 |
| sites | ✅ | 5 |
| site_assignments | ✅ | 0 |
| certificate_assignments | ✅ | 0 |

---

## 3. 데이터 검증 쿼리 결과 (data_migration.sql §5 기준)

```
회사           2
자격증종류     5
인력          5
자격증        5
현장          5
현장배정      0
자격증배정    0
```

---

## 4. 배정 현황 (data_migration.sql §5 배정 검증)

| 현장ID | 현장명 | 배정상태 | 배정인원수 | 배정소장 |
|--------|--------|----------|------------|----------|
| T001 | 테스트 서울 강남 현장 | 미배정 | 0 | (없음) |
| T002 | 테스트 부산 해운대 현장 | 미배정 | 0 | (없음) |
| T003 | 테스트 대전 둔산 현장 | 미배정 | 0 | (없음) |
| T004 | 테스트 인천 송도 현장 | 미배정 | 0 | (없음) |
| T005 | 테스트 광주 첨단 현장 | 미배정 | 0 | (없음) |

- `테스트_현장_5개.csv`에 **담당소장ID**, **사용자격증ID** 컬럼이 비어 있음 → `temp_site_import`에 값이 없으면 data_migration.sql의 배정 INSERT는 0건이 됨 (의도된 동작).

---

## 5. legacy_id 매핑 확인

- **인력**: legacy_id `P-T01` ~ `P-T05` ↔ CSV 인력ID와 일치
- **현장**: legacy_id `T001` ~ `T005` ↔ CSV 현장ID와 일치  
→ 인력/현장 데이터가 CSV와 동일한 식별체계로 이관된 상태로 보임.

---

## 6. data_migration.sql 적용 방식 참고

- `js/data_migration.sql`은 **임시 테이블** `temp_personnel_import`, `temp_certificate_import`, `temp_site_import`에서 INSERT하는 구조입니다.
- 해당 temp 테이블 정의 및 CSV 로드(COPY 또는 별도 ETL)는 스크립트에 포함되어 있지 않으므로, 실제 적용은 다음 중 하나일 수 있습니다.
  - Supabase SQL Editor에서 temp 테이블 생성 → CSV 로드 → data_migration.sql의 INSERT만 실행
  - `scripts/migrate-db.mjs`는 현재 `001_initial_tables.sql`만 적용하므로, 정규화 스키마(002) 및 데이터는 다른 경로(대시보드, 수동 SQL, 별도 스크립트)로 적용된 것으로 보입니다.

---

## 7. 권장 사항

1. **배정 데이터가 필요한 경우**: 현장 CSV에 `담당소장ID`(인력 legacy_id), 자격증 CSV에 `현재사용현장ID`를 채운 뒤, temp 테이블 로드 → data_migration.sql §4(배정 INSERT)만 다시 실행하거나, 앱에서 배정 기능으로 입력.
2. **마이그레이션 이력 관리**: 추후에는 `supabase migration apply` 또는 MCP `apply_migration`으로 002 등을 적용하면 `list_migrations`에 기록되어 적용 여부 추적이 쉬워집니다.
3. **추가 검증**: 필요 시 `personnel.company_id`, `certificates.personnel_id`/`cert_type_id`, `sites.company_id` 등 FK가 모두 유효한지 간단 SELECT로 확인 가능합니다 (현재 점검에서는 문제 없음).

이 문서는 Supabase MCP `list_tables`, `execute_sql`로 조회한 결과를 바탕으로 작성되었습니다.
