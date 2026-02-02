# 현장배정 관리 시스템 - 전체 개발 명세서 (Gemini 회의용)

**작성일**: 2026년 2월 2일  
**목적**: 처음부터 현재까지의 개발 범위·구조·상태를 정리하여 Gemini와 회의·협업 시 공유  
**저장소**: [Siyeolryu/dujon](https://github.com/Siyeolryu/dujon)

---

## 1. 프로젝트 개요

### 1.1 목표

- **프로젝트명**: 현장배정 관리 시스템 (dujon)
- **한 줄 요약**: Google Sheets를 DB로 사용하는 **현장·인력·자격증** 관리 및 **소장 배정** API + HTML 앱
- **핵심 가치**: 시트를 실시간 DB처럼 쓰고, HTML 앱에서 조회·수정·배정까지 한 번에 처리

### 1.2 아키텍처 (목표)

```
Google Sheets (시트1·2·3)  ←→  Flask API Server  ←→  HTML/JS 앱
       ↓                            ↓                      ↓
  데이터·검증·서식·VLOOKUP      REST API·낙관적 잠금      대시보드·필터·배정 UI
```

### 1.3 기술 스택

| 구분 | 기술 |
|------|------|
| 백엔드 | Python 3.x, Flask, Google Sheets API v4 |
| 프론트엔드 | HTML5, Vanilla JavaScript (ES6+), CSS |
| DB | Google Sheets 3시트 (시트1 현장정보, 시트2 인력풀, 시트3 자격증풀) |
| 인증 | OAuth2 (token.pickle, client_secret_xxx.json) |
| 실행 | `run_api.py` (Flask), 정적 HTML은 브라우저 또는 로컬 서버 |

---

## 2. Phase 1 (완료)

### 2.1 범위

- Google Sheets API 연동
- 3개 시트 DB 구축 (1,182셀 업로드, 100% 성공)
- 기본 HTML 앱 (정적 데이터)

### 2.2 결과

- **시트1** 현장정보, **시트2** 인력풀, **시트3** 자격증풀
- OAuth2·token.pickle·client_secret 연동 완료
- 문서: `DB_구조_설계.md`, `Google_Sheets_구축가이드.md`

---

## 3. Phase 2 (진행 중) — 단계별 명세

### 3.1 1단계: Google Sheets 고급 기능 ✅

| 하위 | 내용 | 파일 | 상태 |
|------|------|------|------|
| 1-1 | 데이터 검증 규칙 (드롭다운, 날짜/전화번호 등) | `apply_data_validation.py` | ✅ 완료 |
| 1-2 | 조건부 서식 (배정상태·현장상태별 색상 등) | `apply_conditional_formatting.py` | ✅ 완료 |
| 1-3 | VLOOKUP 수식 (담당소장명·연락처, 자격증명·소유자 등) | `apply_vlookup_formulas.py` | ✅ 완료 |

**중요**: 시트1은 **17컬럼(기본)** 또는 **22컬럼(VLOOKUP 적용 후)** 두 가지 구조.  
1-1·1-2는 **시트1 컬럼 수를 읽어** 17이면 O,P,Q(14,15,16), 22이면 T,U,V(19,20,21) 사용하도록 개선 반영됨.  
**실행 순서**: 1-1 → 1-2 → 1-3 권장. (DEBUG 명세서 1↔2 참고)

**테스트**: `python test_phase2_step1.py` (구조 검증), 실제 적용은 `run_phase2_step1.bat` 또는 스크립트 순차 실행.

---

### 3.2 2단계: 실시간 데이터 연동 API ✅

#### 3.2.1 2-1 데이터 조회 API

| 항목 | 내용 |
|------|------|
| 폴더 | `api/`, `api/routes/`, `api/services/`, `api/models/`, `api/utils/` |
| 서비스 | `api/services/sheets_service.py` — 시트1(22컬럼 기준)·시트2·시트3 읽기 |
| 엔드포인트 | `GET /api/sites`, `/api/sites/<id>`, `/api/sites/search?q=`, `GET /api/personnel`, `/api/personnel/<id>`, `GET /api/certificates`, `/api/certificates/<id>`, `GET /api/stats`, `GET /api/health` |
| 필터 | sites: company, status, state / personnel: status, role / certificates: available |

#### 3.2.2 2-2 데이터 수정 API

| 항목 | 내용 |
|------|------|
| Sheets 확장 | `update_cell`, `update_row`, `batch_update`, `find_row_by_id`, `append_row` |
| 검증 | `api/services/validation.py` — `validate_site_data`, `validate_assignment` |
| 엔드포인트 | `POST /api/sites`, `PUT /api/sites/<id>`, `POST /api/sites/<id>/assign`, `POST /api/sites/<id>/unassign`, `PUT /api/personnel/<id>`, `PUT /api/certificates/<id>` |
| 배정/해제 시 | 시트1(담당소장ID·사용자격증ID·배정상태·수정일), 시트2(현재담당현장수·현재상태), 시트3(사용가능여부·현재사용현장ID) 연동 |

#### 3.2.3 2-3 실시간 동기화 (낙관적 잠금) ✅

| 항목 | 내용 |
|------|------|
| 모듈 | `api/services/sync_manager.py` — 버전=현장 `수정일`, `ConflictError` |
| 동작 | GET /api/sites/<id> 응답에 `version` 포함 / PUT·assign·unassign 시 `If-Match` 또는 body `version` 검사, 불일치 시 **409 Conflict** |
| CORS | `allow_headers`에 `If-Match` 포함 |

**실행**: 프로젝트 루트에서 `python run_api.py` → http://localhost:5000  
**필수**: `token.pickle`, `client_secret_xxx.json`, `.env`에 `SPREADSHEET_ID` (선택). 시트 이름 **시트1, 시트2, 시트3**.

**테스트**: `python test_phase2_step2.py` (구조 검증). 실제 API는 서버 실행 후 curl/Postman.

---

### 3.3 3단계: HTML 앱 기능 확장 ✅

| 항목 | 내용 |
|------|------|
| 진입점 | `site-management.html` |
| 스크립트 | `js/config.js`, `js/api.js`, `js/app.js`, `js/assign.js`, `js/site-detail.js`, `js/dashboard.js`, `js/filter.js`, `js/ui.js`, `js/map.js` |
| 스타일 | `css/style.css`, `css/components.css`, `css/assign-panel.css` |
| API 연동 | `CONFIG.API_BASE_URL`(기본 `http://localhost:5000/api`) + `api.js` — getSites, searchSites, getSiteDetail, assignManager, unassignManager, getStats 등 |
| 기능 | 대시보드(통계), 필터(회사/배정상태/현장상태), 검색(현장명·주소), 정렬, 현장 목록·상세, **소장 배정 패널**(미배정 현장 클릭 시 소장·자격증 선택 후 배정/해제) |
| 버전(낙관적 잠금) | 상세 조회로 `version` 확보 후 배정/해제 시 전달, 409 시 토스트 + 자동 재로드 |

**2↔3 연결**: API 엔드포인트·쿼리·응답 구조·version·409 처리 일치 확인 완료 (DEBUG 명세서 2↔3 참고).

---

### 3.4 4단계: 배포·테스트 및 리스트 고도화

| 구분 | 내용 | 상태 |
|------|------|------|
| 4(배포) | 로컬 서버, CORS/보안, 통합 테스트 | ⚠️ 배포 시 `js/config.js`의 `API_BASE_URL` 변경 필요. 3단계 E2E/브라우저 테스트는 수동 또는 Playwright/Cypress 검토 |
| 4(리스트) | 테이블 정렬, 검색, API 필터 | ✅ 3단계에서 이미 구현 (정렬·검색·필터). 페이지네이션만 선택 미구현 |

---

## 4. 디버그·개선 명세 (연결 구간)

- **1↔2**: 시트1 17/22 컬럼 분기, SPREADSHEET_ID .env 사용, API request_id·구조화 로그 — 반영 완료.
- **2↔3**: API·프론트 엔드포인트·필터·version·409·실패 vs 0건 구분 — 점검 완료.
- **3↔4**: 배포 시 API URL 설정 문서화, 3단계 E2E 검토, API 키 검증(4-2) 미구현 — 문서화·선택 사항으로 정리.

상세: `DEBUG_명세서_1단계_2단계_연결.md`, `DEBUG_명세서_2단계_3단계_연결.md`, `DEBUG_명세서_3단계_4단계_연결.md`.

---

## 5. 주요 파일·폴더 구조

```
프로젝트 루트
├── .env, .env.example
├── run_api.py, requirements_api.txt
├── apply_data_validation.py, apply_conditional_formatting.py, apply_vlookup_formulas.py
├── test_phase2_step1.py, test_phase2_step2.py, run_all_tests.py
├── site-management.html
├── css/ (style.css, components.css, assign-panel.css)
├── js/ (config.js, api.js, app.js, assign.js, dashboard.js, filter.js, site-detail.js, ui.js, map.js)
├── api/
│   ├── app.py
│   ├── routes/ (sites.py, personnel.py, certificates.py, stats.py)
│   ├── services/ (sheets_service.py, validation.py, sync_manager.py)
│   ├── models/, utils/
│   └── README.md
├── 개발일지/ (개발일지_날짜_제목.md)
├── DB_구조_설계.md
├── Phase2_착수보고서.md, Phase2_단계별_개발계획.md
├── 2-1_데이터조회API_가이드.md, 2-2_데이터수정API_가이드.md
├── DEBUG_명세서_1단계_2단계_연결.md, DEBUG_명세서_2단계_3단계_연결.md, DEBUG_명세서_3단계_4단계_연결.md
├── Google_Workspace_연결_가이드.md
└── 개발명세서_전체_Gemini회의용.md (본 문서)
```

---

## 6. API 엔드포인트 요약 (Gemini 회의 시 참고)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | /api/sites | 현장 목록 (company, status, state) |
| GET | /api/sites/search?q= | 현장 검색 |
| GET | /api/sites/<id> | 현장 상세 (version 포함) |
| POST | /api/sites | 현장 생성 |
| PUT | /api/sites/<id> | 현장 수정 (version 검사) |
| POST | /api/sites/<id>/assign | 소장 배정 (manager_id, certificate_id, version) |
| POST | /api/sites/<id>/unassign | 배정 해제 (version) |
| GET | /api/personnel, /api/personnel/<id> | 인력 조회 |
| PUT | /api/personnel/<id> | 인력 수정 |
| GET | /api/certificates, /api/certificates/<id> | 자격증 조회 |
| PUT | /api/certificates/<id> | 자격증 수정 |
| GET | /api/stats | 통계 |
| GET | /api/health | 헬스 |

에러: 400/404/409/500, 응답 body에 `success`, `error.code`, `error.message`, (404/500) `error.request_id`.

---

## 7. 데이터 구조 요약 (시트1·2·3)

- **시트1(현장정보)**: 현장ID, 현장명, 회사구분, 주소, 위도, 경도, 건축허가일, 착공예정일, 준공일, 현장상태, 특이사항, 담당소장ID, 담당소장명, 담당소장연락처, 사용자격증ID, 자격증명, 자격증소유자명, 자격증소유자연락처, 준공필증파일URL, 배정상태, 등록일, 수정일 (22컬럼 기준).
- **시트2(인력풀)**: 인력ID, 성명, 직책, 소속, 연락처, 이메일, 보유자격증, 현재상태, 현재담당현장수, 비고, 입사일, 등록일.
- **시트3(자격증풀)**: 자격증ID, 자격증명, 자격증번호, 소유자ID, 소유자명, 소유자연락처, 발급기관, 취득일, 유효기간, 사용가능여부, 현재사용현장ID, 비고, 등록일.

상세: `DB_구조_설계.md`.

---

## 8. 다음 단계·회의 시 논의 포인트 (Gemini용)

1. **배포**: `API_BASE_URL` 환경별 설정 방법(빌드 치환 vs 런타임 주입) 및 4단계 배포 가이드 보강.
2. **테스트**: 3단계 HTML 앱 E2E(Playwright/Cypress) 도입 여부 및 시나리오.
3. **보안**: 4-2 API 키 검증(`X-API-Key`) 도입 여부 및 CORS·헤더 정책.
4. **선택 기능**: 페이지네이션, SSE 등 실시간 알림, 추가 필터/정렬.
5. **운영**: 로깅·모니터링, 에러 알림, Google API 할당량 관리.

---

**문서 버전**: 1.0  
**최종 갱신**: 2026-02-02
