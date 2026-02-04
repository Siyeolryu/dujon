# Role
너는 시니어 프론트엔드 엔지니어이자 UX 디자인 전문가야. 구글 시트를 DB로 사용하는 '현장배정 관리 시스템(dujon)'의 UI/UX를 임원진 보고용 수준으로 고도화하는 업무를 맡았어.

# Context
- 현재 백엔드 REST API(Flask)는 준비 완료됨.
- 주요 엔드포인트: /api/sites (현장), /api/personnel (인력), /api/stats (통계).
- 데이터 구조: 22개 컬럼 기반의 시트 데이터를 API가 JSON으로 반환함.
- 사용자: 건설사 임원 및 운영 관리자 (가독성과 직관적인 현황 파악이 최우선).

# Instruction: UI/UX 개발 가이드라인
1. **Visual Style**:
   - Modern, Minimal, Premium 엔터프라이즈 디자인 적용.
   - 배경은 연한 그레이(#F8F9FA)를 사용하고, 카드는 화이트 배경에 은은한 그림자(Soft Shadow) 적용.
   - 상태 색상은 제공된 명세서의 가이드(#d9ead3 등)를 따르되, 더 세련된 파스텔 톤이나 인디케이터 스타일로 정제할 것.
   
2. **Main Dashboard**:
   - 상단에 핵심 통계(전체 현장, 미배정 현장, 투입 인력 등)를 요약 카드(Scorecard) 형태로 배치.
   - Chart.js나 가벼운 SVG를 활용하여 배정 현황을 시각화할 것.

3. **Site List & Detail**:
   - 테이블은 'Ag-Grid' 스타일의 정돈된 레이아웃을 사용하고, 행(Row) 클릭 시 우측에서 슬라이드 인(Slide-in)되는 상세 패널 구현.
   - 상세 패널 내부에 '소장 배정' 버튼과 '자격증 선택' 드롭다운을 인터렉티브하게 배치.

4. **Technical Implementation**:
   - `js/api.js`를 통해 Fetch API를 호출하고, `js/app.js`에서 상태를 관리함.
   - 낙관적 잠금(Optimistic Locking)을 지원하기 위해 상세 데이터의 `version`(수정일)을 추적하고, 배정 API 호출 시 `If-Match` 헤더나 페이로드에 포함할 것.
   - 로딩 시 스켈레톤 UI(Skeleton UI)를 적용하여 데이터가 불러와지는 동안에도 고급스러운 인상을 줄 것.

# Tasks
- 제공된 `site-management.html`, `style.css`, `app.js`를 분석하여 위 가이드라인에 맞게 코드를 전면 개편해줘.
- 특히 `js/assign.js`의 배정 로직이 API 엔드포인트 `/api/sites/{id}/assign`과 완벽히 연동되도록 작성해줘.
- 반응형 레이아웃을 적용하여 태블릿(iPad)에서도 임원들이 확인할 수 있게 해줘.

# Constraint
- 외부 라이브러리는 최소화하되, 꼭 필요한 경우 CDN 방식으로 추가할 것.
- 모든 UI 요소는 한글로 작성할 것.