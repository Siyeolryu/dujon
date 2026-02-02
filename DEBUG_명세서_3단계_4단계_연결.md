# Debug 명세서: 3단계 ↔ 4단계 연결

**작성일**: 2026-02-02  
**목적**: Phase 2에서 3단계(HTML 앱)와 4단계로 넘어가는 구간의 디버그·점검 사항 정리

---

## 1. 개요

- **3단계**: HTML 앱 개선 완료 — API 연동(api.js), 소장 배정 UI(assign.js), 필터·검색·정렬(filter.js, app.js), 대시보드(dashboard.js).
- **4단계**는 문서에 따라 두 가지로 정의됨:
  1. **다음단계_개발계획.md**: 4단계 = **배포 및 테스트** (4-1 로컬 서버, 4-2 CORS/보안, 4-3 통합 테스트)
  2. **프론트엔드_개발_단계별_계획.md**: 4단계 = **리스트·필터 고도화** (테이블 정렬, 검색, API 필터, 페이지네이션)

본 명세서는 **3→4(배포·테스트)** 와 **3→4(리스트·필터)** 모두에 대해 점검 결과를 정리합니다.

---

## 2. 3→4(배포·테스트) 점검 결과

| 구분 | 상태 | 비고 |
|------|------|------|
| API 서버 실행 | ✅ | `run_api.py`, `FLASK_PORT`/`FLASK_DEBUG` 환경 변수 사용 |
| CORS | ✅ | `api/app.py`에서 `ALLOWED_ORIGINS` 환경 변수로 제어, 배포 시 프론트 도메인 추가 가능 |
| **프론트 API URL** | ⚠️ 배포 시 수정 필요 | `js/config.js`에 `API_BASE_URL: 'http://localhost:5000/api'` 하드코딩. 배포 시 백엔드 URL로 변경 필요 |
| 통합 테스트 | ⚠️ 3단계 미포함 | `run_all_tests.py`는 1단계·2단계 + API 헬스만 실행. HTML 앱(3단계) E2E/브라우저 테스트 없음 |
| API 키 검증 | ❌ 미구현 | 4-2 권장 사항. 현재 `verify_api_key` 없음, CORS에 `X-API-Key` 헤더만 허용 |

### 2.1 배포 시 API URL 변경

- **현재**: `js/config.js`에 `API_BASE_URL: 'http://localhost:5000/api'` 고정.
- **영향**: 배포 환경(예: 프론트 `https://app.example.com`, API `https://api.example.com`)에서 그대로 쓰면 API 호출이 localhost로 나감.
- **권장**:
  1. **빌드 시 치환**: 배포 스크립트에서 `CONFIG.API_BASE_URL` 값을 환경별로 치환.
  2. **런타임 주입**: HTML에서 `<script>window.__API_BASE_URL__ = 'https://api.example.com/api';</script>` 등으로 주입 후, `config.js`에서 `window.__API_BASE_URL__ || 'http://localhost:5000/api'` 사용.
  3. **문서화**: 4단계(배포) 가이드에 "배포 전 `CONFIG.API_BASE_URL` 또는 `window.__API_BASE_URL__` 설정" 명시.

### 2.2 통합 테스트(4-3)와 3단계

- **다음단계_개발계획.md** 4-3 시나리오: 현장 목록 조회(필터), 상세 조회, 소장 배정, 자격증 배정, 통계 조회, (선택) 실시간 동기화.
- **현재**: `run_all_tests.py`는 1단계 스크립트 검증 + 2단계 API 단위 테스트 + API 헬스 체크만 수행. 3단계(브라우저에서 목록/상세/배정 플로우) 자동화 없음.
- **권장**: 4단계 통합 테스트 시 3단계 포함하려면 수동 체크리스트 또는 Playwright/Cypress 등 E2E 추가 검토.

---

## 3. 3→4(리스트·필터 고도화) 점검 결과

| 구분 | 4단계 요구(프론트엔드_개발_단계별_계획) | 현재 3단계 구현 | 상태 |
|------|----------------------------------------|------------------|------|
| 테이블 정렬 | 헤더 클릭 시 현장명/회사/착공예정/상태 기준 오름차순·내림차순 토글 | `sortBy` select(현장명/배정상태/현장상태), 클라이언트 정렬 | ✅ 기능 있음, UX만 다름(헤더 클릭 vs 드롭다운) |
| 검색 | 현장명/주소 검색 입력창, API 또는 클라이언트 필터 | `searchInput` + `API.searchSites(query)` | ✅ 구현됨 |
| API 필터 연동 | 회사/배정상태 등 API 쿼리로 서버 필터 | `Filter` → `company`/`status`/`state` API 쿼리 | ✅ 구현됨 |
| 페이지네이션 | (선택) limit/offset 또는 무한 스크롤 | 없음 | ❌ 미구현(선택) |

- **결론**: 리스트·필터 관점에서 3단계는 프론트엔드 4단계 요구의 대부분을 이미 충족. 페이지네이션만 선택 사항으로 미구현.

---

## 4. 디버그·개선 사항 요약

| 우선순위 | 항목 | 조치 |
|----------|------|------|
| 높음 | API_BASE_URL 배포 대응 | config.js에서 `window.__API_BASE_URL__` 등 런타임 값 우선 사용하도록 변경. 배포 가이드에 설정 방법 명시. |
| 중간 | 통합 테스트에 3단계 반영 | 4-3 체크리스트 또는 E2E로 "목록→상세→배정→통계" 시나리오 문서화/자동화 검토. |
| 낮음 | 페이지네이션 | 현장 수 많을 때만 필요 시 API limit/offset + 프론트 페이지 UI 추가. |

---

## 5. 수정/추가된 파일 (개선 반영 완료)

| 파일 | 반영 내용 |
|------|-----------|
| `js/config.js` | `API_BASE_URL`을 `window.__API_BASE_URL__`가 있으면 우선 사용, 없으면 `http://localhost:5000/api` 사용. 배포 시 HTML에서 `window.__API_BASE_URL__ = 'https://api.example.com/api';` 설정 가능. |

---

## 6. 검증 방법

- **API URL 런타임 오버라이드**: HTML에서 `window.__API_BASE_URL__ = 'http://localhost:5000/api';` 설정 후 앱 로드 → API 호출이 해당 URL로 나가는지 확인.
- **배포 시나리오**: 프론트와 API를 다른 호스트에 두고, CORS·API_BASE_URL 설정 후 목록/배정/통계 동작 확인.
- **통합 테스트**: run_all_tests.py 실행 후 test_report.html에서 1·2단계 + API 헬스 통과 여부 확인; 3단계는 수동 체크리스트로 보완.
