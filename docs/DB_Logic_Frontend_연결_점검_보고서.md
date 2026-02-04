# 현장관리앱 DB-Logic-Frontend 연결 점검 보고서

**작성일**: 2026년 2월 4일  
**점검자**: Debug 전문 개발자  
**점검 범위**: 데이터베이스, 백엔드 로직, 프론트엔드 연결

---

## 📋 실행 요약

현장관리앱의 DB, Logic, Frontend 연결 상태를 점검한 결과, **중요한 스키마 불일치 문제**와 **API 모드 설정 불일치**를 발견했습니다. 이로 인해 프론트엔드와 백엔드가 서로 다른 데이터베이스 스키마를 가정하고 있어 연결 오류가 발생할 수 있습니다.

---

## 🔍 발견된 문제점

### 1. **DB 스키마 불일치 (Critical)**

#### 문제 상황
- **프론트엔드 (`js/supabase-api.js`)**: 정규화된 스키마(v2) 사용
  - UUID 기반 Primary Key
  - JOIN을 통한 관계 데이터 조회 (`companies`, `certificate_types`, `site_assignments` 등)
  - 컬럼명: `id`, `legacy_id`, `name`, `company_id` 등 (영문)
  
- **백엔드 (`api/services/supabase_service.py`)**: 비정규화된 스키마(v1) 사용
  - 한글 컬럼명 기반 (`현장ID`, `현장명`, `회사구분` 등)
  - 단일 테이블 구조 (JOIN 없음)
  - 컬럼명: `"현장ID"`, `"현장명"`, `"회사구분"` 등 (한글)

#### 영향
- `config.js`에서 `API_MODE: 'supabase'`로 설정 시 프론트엔드는 정규화된 스키마를 가정
- 하지만 실제 DB가 비정규화된 스키마라면 쿼리 실패
- 백엔드 Flask API는 비정규화된 스키마를 가정하므로 Streamlit 등에서 사용 시 문제 없음
- **프론트엔드와 백엔드가 서로 다른 스키마를 사용하는 상황**

#### 관련 파일
- `supabase/migrations/001_initial_tables.sql` (비정규화 스키마)
- `supabase/migrations/002_normalized_schema.sql` (정규화 스키마)
- `api/services/supabase_service.py` (비정규화 스키마 사용)
- `js/supabase-api.js` (정규화 스키마 사용)

---

### 2. **API 모드 설정 불일치**

#### 문제 상황
- `js/config.js`: `API_MODE: 'supabase'` (기본값)
- 프론트엔드는 Supabase 직접 연결을 시도 (`supabase-api.js` 사용)
- 하지만 실제 DB 스키마가 비정규화된 경우 쿼리 실패

#### 영향
- 프론트엔드가 정규화된 스키마를 가정하지만 실제 DB는 비정규화된 스키마일 수 있음
- Streamlit은 Flask API를 사용하므로 문제 없음

---

### 3. **데이터 형식 변환 불일치**

#### 문제 상황
- `supabase-api.js`의 `_transformSite()`: 정규화된 스키마 → 프론트엔드 호환 형식
- `supabase_service.py`의 `_row_to_site()`: 비정규화된 스키마 → API 응답 형식
- 두 변환 로직이 서로 다른 스키마를 가정

---

### 4. **API 엔드포인트 경로**

#### 확인 사항
- `js/api.js`: `/sites` 호출 (상대 경로)
- `CONFIG.API_BASE_URL`: `/api` 포함 시 `/api/sites`로 변환됨
- Flask 라우트: `/api/sites` (정상)
- **문제 없음** (정상 동작)

---

## ✅ 정상 동작하는 부분

1. **Flask API 라우트 구조**: 모든 엔드포인트가 올바르게 정의됨
2. **CORS 설정**: 프론트엔드-백엔드 간 CORS 허용 설정 정상
3. **에러 처리**: 프론트엔드와 백엔드 모두 에러 처리 로직 구현됨
4. **Streamlit 연동**: Flask API를 통한 연동은 정상 동작

---

## 🔧 개선 방안

### 방안 1: 백엔드를 정규화된 스키마에 맞게 수정 (권장)

**이유**: 개발일지(2026-02-03)에 따르면 정규화된 스키마(v2)로 전환했으므로, 백엔드도 이를 따르는 것이 일관성 있음

**작업 내용**:
1. `api/services/supabase_service.py`를 정규화된 스키마에 맞게 수정
2. JOIN을 통한 관계 데이터 조회 구현
3. `legacy_id`를 통한 기존 ID 호환성 유지

**장점**:
- 프론트엔드와 백엔드가 동일한 스키마 사용
- 정규화된 스키마의 장점 활용 (확장성, 데이터 무결성)

**단점**:
- 기존 데이터가 비정규화된 스키마라면 마이그레이션 필요

---

### 방안 2: 프론트엔드를 비정규화된 스키마에 맞게 수정

**작업 내용**:
1. `js/supabase-api.js`를 비정규화된 스키마에 맞게 수정
2. 한글 컬럼명 사용
3. JOIN 없이 단일 테이블 조회

**장점**:
- 기존 데이터와 호환성 유지

**단점**:
- 정규화된 스키마의 장점을 활용하지 못함
- 향후 확장성 제한

---

### 방안 3: 두 스키마 모두 지원 (하이브리드)

**작업 내용**:
1. 환경 변수로 스키마 버전 선택 (`DB_SCHEMA_VERSION=v1|v2`)
2. 각 서비스에서 스키마 버전에 따라 다른 쿼리 사용

**장점**:
- 유연성 확보

**단점**:
- 복잡도 증가
- 유지보수 어려움

---

## ✅ 완료된 개선 사항

### 1. 백엔드 정규화된 스키마 지원 완료 (2026-02-04)

**작업 내용**:
- `api/services/supabase_service.py`를 정규화된 스키마(v2)에 맞게 완전 수정
- JOIN을 통한 관계 데이터 조회 구현 (`companies`, `certificate_types`, `site_assignments`, `certificate_assignments`)
- 배정 관계 테이블을 통한 배정 정보 관리
- `legacy_id`를 통한 기존 ID 호환성 유지
- 프론트엔드와 동일한 데이터 변환 로직 적용

**주요 변경 사항**:
- `get_all_sites()`, `get_site_by_id()`: JOIN을 통한 관계 데이터 조회
- `assign_site()`, `unassign_site()`: 배정 관계 테이블(`site_assignments`, `certificate_assignments`) 사용
- `_transform_site()`, `_transform_personnel()`, `_transform_certificate()`: 정규화된 스키마 → API 응답 형식 변환
- 폴백 로직 추가: 정규화되지 않은 스키마와의 호환성 유지

**결과**:
- ✅ 프론트엔드와 백엔드가 동일한 정규화된 스키마 사용
- ✅ 데이터 형식 변환 로직 일관성 확보
- ✅ 배정 관계 테이블을 통한 정확한 배정 정보 관리

---

## 📝 권장 조치 사항

### 즉시 조치 (High Priority)

1. **실제 DB 연결 테스트**
   - Supabase Table Editor에서 정규화된 스키마(v2) 적용 확인
   - Flask API 서버 실행 후 엔드포인트 테스트
   - 프론트엔드-백엔드 통합 테스트

2. **환경 변수 확인**
   - `.env` 파일에 `SUPABASE_URL`, `SUPABASE_KEY` 설정 확인
   - `DB_BACKEND=supabase` 설정 확인

---

### 중기 조치 (Medium Priority)

1. **데이터 마이그레이션 (필요 시)**
   - 기존 비정규화된 스키마 데이터가 있다면 정규화된 스키마로 마이그레이션
   - `legacy_id` 필드를 통한 기존 ID 보존

2. **문서화**
   - 정규화된 스키마 사용 가이드 작성
   - API 모드별 사용 가이드 업데이트

---

### 장기 조치 (Low Priority)

1. **모니터링 및 로깅 강화**
   - DB 연결 오류 로깅
   - API 호출 실패 추적

2. **자동화 테스트**
   - 통합 테스트 자동화
   - 스키마 변경 시 자동 검증

---

## 🔍 점검 체크리스트

- [x] DB 스키마 일관성 확인
- [x] API 모드 설정 확인
- [x] 프론트엔드-백엔드 연결 경로 확인
- [x] 데이터 형식 변환 로직 확인
- [x] 백엔드 정규화된 스키마 지원 구현
- [x] 배정 관계 테이블 사용 구현
- [ ] 실제 DB 연결 테스트 (수동 확인 필요)
- [ ] 프론트엔드-백엔드 통합 테스트 (수동 확인 필요)

---

## 📊 영향도 분석

| 문제 | 심각도 | 영향 범위 | 우선순위 |
|------|--------|----------|---------|
| DB 스키마 불일치 | 🔴 Critical | 전체 시스템 | P0 |
| API 모드 설정 불일치 | 🟡 Medium | 프론트엔드 | P1 |
| 데이터 형식 변환 불일치 | 🟡 Medium | 데이터 일관성 | P1 |
| API 엔드포인트 경로 | 🟢 Low | 없음 | P2 |

---

## 📌 결론

**✅ 개선 완료**: 백엔드 `supabase_service.py`를 정규화된 스키마(v2)에 맞게 수정하여 프론트엔드와 백엔드가 동일한 스키마를 사용하도록 통일했습니다.

**주요 개선 사항**:
1. ✅ 정규화된 스키마(v2) 지원 완료
2. ✅ JOIN을 통한 관계 데이터 조회 구현
3. ✅ 배정 관계 테이블(`site_assignments`, `certificate_assignments`) 사용
4. ✅ 데이터 형식 변환 로직 일관성 확보
5. ✅ `legacy_id`를 통한 기존 ID 호환성 유지

**다음 단계**: 실제 DB 연결 테스트 및 프론트엔드-백엔드 통합 테스트를 진행하여 정상 동작을 확인해야 합니다.

---

## 📎 참고 문서

- `개발일지/개발일지_2026-02-03_개발명세서.md` - 정규화된 스키마 전환 기록
- `supabase/migrations/001_initial_tables.sql` - 비정규화 스키마
- `supabase/migrations/002_normalized_schema.sql` - 정규화 스키마
- `api/services/supabase_service.py` - 백엔드 Supabase 서비스
- `js/supabase-api.js` - 프론트엔드 Supabase API 모듈
- `js/config.js` - API 모드 설정
