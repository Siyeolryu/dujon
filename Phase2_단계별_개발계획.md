# Phase 2 단계별 개발 계획

## 목표
**"Google Sheets를 실시간 DB로 전환하고, HTML 앱과 양방향 연동"**

---

## 전체 단계 요약

| 단계 | 내용 | 상태 | 담당 파일/폴더 |
|------|------|------|----------------|
| **1단계** | Google Sheets 고급 기능 | 진행 중 | 스크립트 3개 |
| 1-1 | 데이터 검증 규칙 | ✅ 완료 | `apply_data_validation.py` |
| 1-2 | 조건부 서식 | ✅ 스크립트 준비 | `apply_conditional_formatting.py` |
| 1-3 | VLOOKUP 수식 | ✅ 스크립트 준비 | `apply_vlookup_formulas.py` |
| **2단계** | 실시간 데이터 연동 API | ✅ 완료 | `api/` |
| 2-1 | 데이터 조회 API | ✅ 완료 | `api/routes/*.py` |
| 2-2 | 데이터 수정 API | ✅ 완료 | `api/routes/*.py`, `api/services/` (검증: `test_phase2_step2.py`, `Phase2_2-2_완료체크.md`) |
| 2-3 | 실시간 동기화 (낙관적 잠금) | ✅ 완료 | `api/services/sync_manager.py`, `Phase2_2-3_완료체크.md` |
| **3단계** | HTML 앱 기능 확장 | ⏳ 예정 | `site-management.html`, `app.js` |
| 3-1 | API 연동 | ⏳ 예정 | - |
| 3-2 | 소장 배정 UI | ⏳ 예정 | - |
| 3-3 | 실시간 업데이트 UI | ⏳ 예정 | - |

---

## 1단계: Google Sheets 고급 기능 (우선 진행)

### 1-1 데이터 검증 규칙 ✅
- **파일**: `apply_data_validation.py`
- **실행**: `python apply_data_validation.py`
- **결과**: 드롭다운, 날짜/전화번호 검증 등 18개 규칙 적용

### 1-2 조건부 서식 ✅
- **파일**: `apply_conditional_formatting.py`
- **실행**: `python apply_conditional_formatting.py`
- **결과**: 시트1/2/3 상태별 색상, 헤더·줄무늬 등 24개 서식
- **가이드**: `1-2_조건부서식_가이드.md`

### 1-3 VLOOKUP 수식 ✅
- **파일**: `apply_vlookup_formulas.py`
- **실행**: `python apply_vlookup_formulas.py`
- **결과**: 현장정보 시트에 담당소장명/연락처, 자격증명/소유자 등 5개 컬럼 자동 조회
- **가이드**: `1-3_VLOOKUP수식_가이드.md`

**1단계 완료 후**: 시트 고급화 완료 → 2단계 API와 연동 가능한 구조 확보

---

## 2단계: 실시간 데이터 연동 API ✅

- **실행**: `python run_api.py` 또는 `python api/app.py`
- **엔드포인트**: `GET/POST/PUT /api/sites`, `/api/personnel`, `/api/certificates`, `/api/stats`, `/api/health`
- **소장 배정**: `POST /api/sites/<id>/assign`, `POST /api/sites/<id>/unassign`

(이미 구현 완료. 2-3 실시간 동기화는 선택 사항.)

---

## 3단계: HTML 앱 기능 확장 (예정)

- 정적 데이터 → API 호출로 전환
- 미배정 현장 클릭 시 소장 배정 패널
- 실시간 반영 (SSE 또는 폴링)

---

## 1단계 테스트

- **검증만**: `python test_phase2_step1.py` (Google API 호출 없음, 스크립트 구조·함수 검증)
- **적용까지**: `run_phase2_step1.bat` (테스트 통과 후 1-1 → 1-2 → 1-3 순서로 시트 적용)

## 권장 진행 순서

1. **1단계 테스트 후 실행**
   - **방법 A**: 프로젝트 폴더에서 `run_phase2_step1.bat` 더블클릭 (테스트 → 적용 한 번에)
   - **방법 B**: `python test_phase2_step1.py` 로 검증 후, 수동으로 1-1·1-2·1-3 스크립트 실행
   - 상세: `Phase2_1단계_실행가이드.md` 참고
2. **이후**: 3단계 HTML 앱 API 연동 및 소장 배정 UI

---

## 참고 문서

- `Phase2_착수보고서.md` - Phase 2 전체 개요
- `Phase2_1단계_실행가이드.md` - 1단계 통합 실행 방법
- `Phase2_2단계_개요.md` - API 개발 개요
- `개발일지/개발일지_2026-01-30_개발현황.md` - 최근 개발 현황
