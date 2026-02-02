# Phase 2 - 2-3 실시간 동기화 (낙관적 잠금) 완료 체크

## 목표
여러 사용자가 동시에 수정할 때 데이터 충돌 방지 (낙관적 잠금)

---

## 구현 현황 (완료)

### 1. SyncManager (`api/services/sync_manager.py`)

| 항목 | 내용 |
|------|------|
| **버전** | 현장(시트1)의 `수정일` 값을 버전으로 사용 |
| **ConflictError** | 버전 불일치 시 발생하는 예외 |
| **get_site_version(site_id)** | 현장의 현재 버전(수정일) 반환 |
| **check_site_version(site_id, expected)** | 버전 일치 여부 (expected 비어 있으면 통과) |
| **require_site_version(site_id, expected)** | 불일치 시 ConflictError 발생 |

### 2. API 동작

| 엔드포인트 | 버전 반환 | 버전 검사 | 충돌 시 |
|------------|-----------|-----------|---------|
| GET /api/sites/<id> | `data.version` = 수정일 | - | - |
| PUT /api/sites/<id> | 응답 `data.version` = 갱신된 수정일 | If-Match 또는 body.version | 409 Conflict |
| POST /api/sites/<id>/assign | 응답 `data.version` | If-Match 또는 body.version | 409 Conflict |
| POST /api/sites/<id>/unassign | 응답 `data.version` | If-Match 또는 body.version | 409 Conflict |

### 3. 클라이언트 사용 예

1. **조회 시 버전 저장**
   ```js
   const res = await fetch('/api/sites/S001');
   const { data } = await res.json();
   const version = data.version;  // 수정 시 함께 전달
   ```

2. **수정 시 버전 전달 (둘 중 하나)**
   - 헤더: `If-Match: 2026-01-30`
   - Body: `{ "version": "2026-01-30", "현장상태": "착공중" }`

3. **409 응답 시**
   - "데이터가 다른 사용자에 의해 수정되었습니다" 메시지
   - 최신 데이터 다시 조회 후 사용자 확인 후 재시도

---

## 체크리스트

- [x] sync_manager.py (SyncManager, ConflictError)
- [x] GET /api/sites/<id> 응답에 version 포함
- [x] PUT/assign/unassign 요청 시 If-Match 또는 body.version 검사
- [x] 충돌 시 409 Conflict, code: CONFLICT
- [x] CORS allow_headers에 If-Match 추가

---

**2-3 완료 후**: 3단계 HTML 앱 API 연동·소장 배정 UI 진행
