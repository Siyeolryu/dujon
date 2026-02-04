# Red Team UI/UX 점검 개선 적용 요약

**적용일**: 2026-02-04  
**대상**: `docs/RedTeam_UI_UX_점검_보고서.md` 권장사항

---

## 1회차: 네비게이션 URL + 현재 페이지 강조

- **1.1** Streamlit 멀티페이지 URL 규칙 확인: 파일명 identifier 기준(`/대시보드`, `/현장_목록` 등)으로 `NAV_LINKS` 및 `href` 일치. 주석으로 규칙 명시.
- **1.2** `render_top_nav(current_page=None)` 추가. 현재 페이지에 `.active` 클래스 적용(파란 배경·흰 글씨). 홈·각 서브 페이지에서 `current_page` 인자 전달.

**수정 파일**: `streamlit_utils/theme.py`, `app_streamlit.py`, `pages/1_대시보드.py`, `pages/2_현장_목록.py`, `pages/3_현장등록.py`, `pages/4_자격증등록.py`, `pages/8_투입가능인원_상세.py`

---

## 2회차: 현장 목록 테이블·헤더 고정

- **1.3** `st.dataframe` 유지. 테이블 헤더 스크롤 시 고정: `theme.py`에 `[data-testid="stDataFrame"] th`에 `position: sticky` 적용.
- 빠른 액션(행별 배정·해제·상세)을 **expander**로 감싸 기본 접기(`expanded=False`)로 목록 가독성 우선.

**수정 파일**: `streamlit_utils/theme.py`, `pages/2_현장_목록.py`

---

## 3회차: 공통 스타일 theme 이전·색상 체계 통일

- **2.1** 공통 폼/탭 클래스(`.form-section-divider`, `.required-section-title`, `.optional-section-title`, `.tab-select-label`, `.form-submit-area`) 및 라디오 탭 레이아웃을 `LOCALHOST_CSS`로 이전. `3_현장등록.py`, `4_자격증등록.py` 인라인 스타일 제거. `2_현장_목록.py` 필터 라디오는 theme 공통 적용.
- **2.2** CTA(주요 액션): 폼 제출·primary 버튼 = **#3b82f6**. 탭/필터 선택 = **#495057**(보조 계층).

**수정 파일**: `streamlit_utils/theme.py`, `pages/2_현장_목록.py`, `pages/3_현장등록.py`, `pages/4_자격증등록.py`

---

## 4회차: 배정 패널 위치·페이지네이션 하단 복제

- **3.1** 소장 배정 패널을 **필터 바로 아래·목록 위**에 두고 `st.expander('📌 소장 배정', expanded=True)`로 감싸 배정 모드 시 항상 노출.
- **3.3** 페이지네이션을 `_render_pagination()`으로 공통화. **상단**에 전체 컨트롤(페이지당 항목 수 + 이전/다음), **하단**에 캡션 + 이전/다음만 복제(`bottom_only=True`).

**수정 파일**: `pages/2_현장_목록.py`

---

## 5회차: 날짜 필드·성공 피드백

- **5.1** 현장등록: 건축허가일·착공예정일·준공일 → `st.date_input` 교체. 자격증등록: 취득일·유효기간 → `st.date_input`. 서버 전달 시 `strftime('%Y-%m-%d')` 사용.
- **3.2** 등록 성공 시 안내 문구 + **현장 목록 / 자격증·투입가능인원** 링크 + **「다른 현장/자격증 등록」** 버튼(클릭 시 `st.rerun()`).

**수정 파일**: `pages/3_현장등록.py`, `pages/4_자격증등록.py`

---

## 6회차: 대시보드 메트릭 연동·접근성·반응형

- **3.5** 대시보드 메트릭 아래에 **「현장 목록 보기」「미배정 현장 보기」「배정완료 현장 보기」** 링크 추가. `/현장_목록`, `/현장_목록?status=미배정`, `/현장_목록?status=배정완료`로 이동(기존 `st.query_params` 연동).
- **4.1** 라디오·버튼·폼 제출 버튼에 `:focus-visible` 시 `outline: 2px solid #3b82f6` 적용.
- **4.2** `@media (max-width: 768px)`에서 `.top-nav` 세로 정렬·컬럼 정렬 보완.

**수정 파일**: `streamlit_utils/theme.py`, `pages/1_대시보드.py`

---

## 테스트 권장 사항

1. **네비**: 홈·각 페이지 이동 후 현재 메뉴 강조 여부 확인.
2. **현장 목록**: 배정 클릭 시 상단 배정 패널 노출, 목록 하단에서 이전/다음 동작 확인.
3. **현장/자격증 등록**: 날짜는 날짜 선택기로 입력, 등록 성공 후 링크·다른 등록 버튼 동작 확인.
4. **대시보드**: 메트릭 아래 링크로 현장 목록·미배정/배정완료 필터 이동 확인.
5. **키보드**: Tab으로 라디오·버튼 포커스 시 아웃라인 표시 확인.

실행: `streamlit run app_streamlit.py`
