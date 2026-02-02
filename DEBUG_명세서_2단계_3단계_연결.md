# Debug 명세서: 2단계 ↔ 3단계 연결

**작성일**: 2026-02-02  
**목적**: Phase 2에서 2단계(REST API)와 3단계(HTML 앱) 연결 구간의 디버그·점검 사항 정리

---

## 1. 개요

- **2단계**: Flask REST API (GET/PUT/POST, 낙관적 잠금, `/api/sites`, `/api/personnel`, `/api/certificates`, `/api/stats`, `/api/health`).
- **3단계**: HTML/JS 앱 — `js/api.js`로 API 호출, `js/assign.js` 배정 플로우, `js/site-detail.js` 상세, `js/dashboard.js` 통계, `js/filter.js` 필터·검색.
- **연결 이슈**: API 응답 형식·쿼리 파라미터·버전 전달·에러 처리·빈 상태 구분 등.

---

## 2. 점검 결과 요약

| 구분 | 상태 | 비고 |
|------|------|------|
| API 베이스 URL / 엔드포인트 | ✅ 일치 | `CONFIG.API_BASE_URL` + `/sites`, `/health` 등 — Flask 라우트와 일치 |
| 현장 조회·필터 (company, status, state) | ✅ 일치 | 프론트 `DISPLAY_MAP.companyReverse` → API 쿼리, 응답 `data`/`count` 사용 |
| 현장 상세·version | ✅ 정상 | GET 상세 응답에 `version`(수정일) 포함, 배정/해제 시 `assignData.version`·`unassignManager(siteId, version)` 전달 |
| 배정 시 version 확보 | ✅ 정상 | 목록에서만 "배정하기"로 열어도 `Assign.open()` 내 `API.getSiteDetail(siteId)`로 `this.siteDetail.version` 확보 후 `confirm()`에서 사용 |
| 인력/자격증 필터 (status, role, available) | ✅ 일치 | API `personnel`는 status/role, `certificates`는 available — 파라미터명·값 일치 |
| 통계 /stats 응답 구조 | ✅ 일치 | API `data.sites`/`data.personnel`/`data.certificates` (total, assigned, unassigned, available 등) — Dashboard에서 동일 키 사용 |
| 409 처리 | ✅ 처리됨 | api.js에서 토스트 + 800ms 후 `App.loadAll()` 호출 |
| API 실패 vs 데이터 0건 | ✅ 개선 반영 | `result === null` 시 "서버에 연결할 수 없습니다...", 0건 시 "조건에 맞는 현장이 없습니다" 구분 표시 |
| 에러 응답 request_id | ✅ API 반영됨 | 2단계 API가 404/500에 `request_id` 포함 — 프론트는 토스트에 미표시(선택 사항) |

---

## 3. 상세 점검 내용

### 3.1 API 호출·엔드포인트

- **api.js**  
  - `request(endpoint, options)`: `url = CONFIG.API_BASE_URL + endpoint` (예: `http://localhost:5000/api` + `/sites`).  
  - Flask: `url_prefix='/api'`, 라우트 `/sites` → 최종 경로 `/api/sites`. **일치.**

- **healthCheck**: `fetch(CONFIG.API_BASE_URL + '/health')` → `http://localhost:5000/api/health`.  
  - Flask: `@app.route('/api/health')`. **일치.**

### 3.2 현장 목록·필터

- **app.js loadSites**: `Filter.currentFilters` → `company`는 `DISPLAY_MAP.companyReverse`로 API 값(더존종합건설/더존하우징)으로 변환, `status`/`state`는 그대로 전달.
- **API sites**: `request.args.get('company')`, `('status')`, `('state')` 사용. **일치.**

### 3.3 현장 상세·버전(낙관적 잠금)

- **API GET /sites/<id>**: 응답 `data`에 `version`(수정일) 포함.
- **assign.js**  
  - `open(siteId, ...)`: `API.getSiteDetail(siteId)` → `this.siteDetail = detail` (version 포함).  
  - `confirm()`: `version = SiteDetail.currentSite?.version ?? this.siteDetail?.version` 후 `assignData.version`에 넣어 전달.  
  - 목록에서만 "배정하기"로 열어도 `getSiteDetail`로 version 확보. **정상.**

### 3.4 배정/해제 API 파라미터

- **api.js assignManager**: body `manager_id`, `certificate_id`, `version`(있을 때).
- **API POST /sites/<id>/assign**: `data.get('manager_id')`, `data.get('certificate_id')`, `data.get('version')` 사용. **일치.**

- **api.js unassignManager**: body `version`(있을 때).
- **API POST /sites/<id>/unassign**: `version` 사용. **일치.**

### 3.5 통계 Dashboard

- **API GET /stats**:  
  `data: { sites: { total, assigned, unassigned, ... }, personnel: { available, ... }, certificates: { available, ... } }`
- **api.js getStats()**: `res?.data || null` 반환 → `data` 객체 그대로 전달.
- **dashboard.js**: `data.sites.total`, `data.sites.unassigned`, `data.sites.assigned`, `data.personnel.available`, `data.certificates.available` 사용. **일치.**

### 3.6 API 실패 vs 데이터 0건 (개선 권장)

- **현재**: `API.getSites()` 실패 시 `result === null`, 성공 시 `result.data`/`result.count`.  
  - `loadSites`에서 `result`가 null이면 목록/카운트 갱신을 하지 않아, 이전 데이터가 그대로 보이거나 카운트만 안 바뀔 수 있음.  
  - "조건에 맞는 현장이 없습니다"는 `result.data.length === 0`일 때만 적절한 메시지.
- **권장**:  
  - API 실패(null) 시: 빈 목록으로 렌더 + "서버에 연결할 수 없습니다. 네트워크를 확인하세요." 등 별도 메시지 또는 토스트 유지.  
  - 성공·0건 시: 기존처럼 "조건에 맞는 현장이 없습니다" 표시.

---

## 4. 개선 사항 (반영 권장)

| 우선순위 | 항목 | 조치 |
|----------|------|------|
| 중간 | API 실패 vs 0건 구분 | `loadSites`/필터·검색에서 `result === null`일 때 빈 목록 + 서버 오류 메시지, `result.data.length === 0`일 때만 "조건에 맞는 현장이 없습니다" 표시 |
| 낮음 | 409/에러 시 request_id 표시 | 개발/지원용으로 토스트 또는 콘솔에 `error.request_id` 출력 (선택) |

---

## 5. 수정/추가된 파일 (개선 반영 완료)

| 파일 | 반영 내용 |
|------|-----------|
| `js/app.js` | `loadSites()`: API 실패(`result === null`) 시 `renderSiteList(null, true)` 호출, 카운트 '-' 표시. `renderSiteList(sites, apiFailed)`: `apiFailed === true`일 때 "서버에 연결할 수 없습니다. API 서버를 확인하세요.", 아니면 "조건에 맞는 현장이 없습니다." 표시. |
| `js/filter.js` | `apply()`/`search()`: `result === null`일 때 `App.renderSiteList(null, true)` 및 카운트 '-' 표시. |

---

## 6. 검증 방법

- **버전·배정**: 목록에서만 "배정하기"로 열어 소장·자격증 선택 후 배정 → 409 없이 완료되는지, 상세에서 다시 열어 배정 시 version 전달되는지 확인.
- **통계**: 앱 로드 후 대시보드 숫자가 /api/stats 응답과 일치하는지 확인.
- **API 실패 vs 0건**: API 서버 중지 후 목록/필터 동작 → "서버에 연결할 수 없습니다" 등 구분 메시지 노출 여부 확인.
