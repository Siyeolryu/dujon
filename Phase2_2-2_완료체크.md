# Phase 2 - 2-2 데이터 수정 API 완료 체크

## 목표
Google Sheets 데이터를 HTTP POST/PUT으로 수정하는 API 구축

---

## 구현 현황 (완료)

### 1. Sheets 서비스 확장 (`api/services/sheets_service.py`)

| 메서드 | 용도 |
|--------|------|
| `update_cell(range_name, value)` | 셀 1개 업데이트 |
| `update_row(range_name, values)` | 행(여러 셀) 업데이트 |
| `batch_update(updates)` | 여러 범위 일괄 업데이트 |
| `find_row_by_id(sheet_name, id_value)` | ID로 행 번호 반환 (1-based) |
| `append_row(sheet_name, values)` | 시트 마지막에 행 추가 |

### 2. 검증 로직 (`api/services/validation.py`)

| 함수 | 용도 |
|------|------|
| `validate_site_data(data, is_update)` | 현장 필수/회사구분/현장상태/날짜 형식 검증 |
| `validate_assignment(site, manager, certificate)` | 배정 가능 여부(배정완료/퇴사/휴가/자격증 상태) 검증 |

### 3. 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/sites` | 현장 생성 (필수: 현장ID, 현장명, 회사구분, 주소) |
| PUT | `/api/sites/<id>` | 현장 정보 수정 (22컬럼 시트 기준) |
| POST | `/api/sites/<id>/assign` | 소장 배정 (body: manager_id, certificate_id) |
| POST | `/api/sites/<id>/unassign` | 소장 배정 해제 |
| PUT | `/api/personnel/<id>` | 인력 정보 수정 |
| PUT | `/api/certificates/<id>` | 자격증 정보 수정 |

### 4. 배정/해제 시 연동

- **assign**: 시트1(담당소장ID, 사용자격증ID, 배정상태, 수정일) + 시트2(현재담당현장수+1, 현재상태=투입중) + 시트3(사용가능여부=사용중, 현재사용현장ID)
- **unassign**: 시트1(담당소장ID/사용자격증ID 비우기, 배정상태=미배정) + 시트2(현재담당현장수-1, 0이면 투입가능) + 시트3(사용가능, 현재사용현장ID 비우기)

---

## 검증 테스트

### 구조 검증 (Google API/서버 없이)

```cmd
python test_phase2_step2.py
```

- Sheets 서비스 메서드, validation, sites/personnel/certificates 라우트 존재 여부 확인
- 통과 시: `결과: 5/5 통과`

### 실제 API 테스트 (서버 실행 후)

1. **서버 실행**
   ```cmd
   python run_api.py
   ```

2. **현장 생성**
   ```bash
   curl -X POST http://localhost:5000/api/sites -H "Content-Type: application/json" -d "{\"현장ID\":\"S999\",\"현장명\":\"테스트현장\",\"회사구분\":\"더존종합건설\",\"주소\":\"서울시\"}"
   ```

3. **현장 수정**
   ```bash
   curl -X PUT http://localhost:5000/api/sites/S999 -H "Content-Type: application/json" -d "{\"현장상태\":\"착공예정\"}"
   ```

4. **소장 배정**
   ```bash
   curl -X POST http://localhost:5000/api/sites/S999/assign -H "Content-Type: application/json" -d "{\"manager_id\":\"P001\",\"certificate_id\":\"C001\"}"
   ```

5. **배정 해제**
   ```bash
   curl -X POST http://localhost:5000/api/sites/S999/unassign
   ```

---

## 체크리스트

- [x] Sheets 서비스: update_cell, update_row, batch_update, find_row_by_id, append_row
- [x] validation: validate_site_data, validate_assignment
- [x] POST /api/sites (현장 생성)
- [x] PUT /api/sites/<id> (현장 수정)
- [x] POST /api/sites/<id>/assign (소장 배정)
- [x] POST /api/sites/<id>/unassign (배정 해제)
- [x] PUT /api/personnel/<id>
- [x] PUT /api/certificates/<id>
- [ ] 실제 Google 시트 연동 테스트 (token.pickle + run_api.py)

---

**2-2 완료 후**: 2-3 실시간 동기화(선택) 또는 3단계 HTML 앱 API 연동으로 진행
