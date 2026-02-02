# 🤖 Role: Senior Full-Stack Engineer (20+ Years Exp)
# 🎯 Task: DJ-CON Map Phase 2-3 - Kakao Maps API Integration

당신은 이제부터 'DJ-CON Map' 시스템의 프론트엔드 고도화를 담당하는 시니어 개발자입니다. 
기존의 정적 구조를 탈피하고, Kakao Maps API를 사용하여 실시간 현장 관리 및 소장 배정 시스템을 완성해야 합니다.

---

## 1. 📌 개발 전제 조건
- **프로젝트명**: DJ-CON Map (더존하우징/더존종합건설 현장 관리 시스템)
- **현재 상태**: Phase 2 백엔드 API 완비, 프론트엔드 모듈화 작업 중.
- **핵심 기술 스택**: Vanilla JS, Kakao Maps API, CSS3 (Cyberpunk/Dark Theme).
- **데이터 구조**: API 응답 키는 한글('현장ID', '현장명', '주소' 등)을 사용함.

---

## 2. 🛠️ 상세 구현 지침 (STEP-BY-STEP)

### STEP 1: `js/map.js` 모듈 전면 개편
Kakao Maps API를 활용하여 `SiteMap` 객체를 구현하세요.
1.  **초기화 (`init`)**: 
    - `CONFIG.MAP_CENTER`와 `CONFIG.MAP_ZOOM`을 사용하여 지도를 생성합니다.
    - 지도 컨트롤(줌 컨트롤, 지도 타입 전환)을 추가합니다.
2.  **마커 렌더링 (`updateMarkers`)**:
    - `sites` 배열을 받아 기존 마커를 제거하고 새 마커를 찍습니다.
    - **상태별 색상 구분**: 배정완료(초록), 미배정(빨강), 경고(노랑), 위험(보라/주황) 등 커스텀 이미지 마커를 사용하세요.
    - 마커 클릭 시 `SiteDetail.open(siteId)`를 호출합니다.
3.  **주소 변환 (Geocoding)**:
    - 좌표(lat, lng)가 없는 데이터의 경우 `kakao.maps.services.Geocoder`를 사용하여 주소를 좌표로 변환 후 표시하는 예외 처리를 포함하세요.
4.  **클러스터러 적용**: 현장이 많아질 경우를 대비해 `kakao.maps.MarkerClusterer`를 적용합니다.

### STEP 2: 커스텀 인포윈도우 (CustomOverlay)
- 기본 InfoWindow 대신, 다크 테마에 어울리는 HTML 기반 `CustomOverlay`를 제작하세요.
- 현장명, 회사구분(종합/하우징), 담당소장 이름이 간략하게 표시되어야 합니다.

### STEP 3: 상세 패널 및 배정 UI 연동 (`js/app.js` & `js/assign.js`)
- 지도의 마커를 클릭하면 우측 `SiteDetailPanel`이 열리며 해당 현장의 상세 정보가 API로부터 로드되어야 합니다.
- 미배정 현장 마커는 시각적으로 강조(애니메이션 등)하여 관리자가 즉시 인지하도록 합니다.

### STEP 4: 반응형 및 성능 최적화
- 지도의 유휴 상태(idle) 이벤트를 활용해 화면 내에 보이는 마커만 렌더링하는 최적화를 고려하세요.
- 모바일 환경에서 지도가 잘리지 않도록 레이아웃 브레이크포인트를 적용하세요.

---

## 3. ⚠️ 기술적 주의사항 (MUST FOLLOW)

1.  **API Key 관리**: `index.html`의 스크립트 태그에 `autoload=false`를 사용하고, `kakao.maps.load()`를 통해 안전하게 초기화하세요.
2.  **데이터 바인딩**: API에서 오는 한글 키(`site['현장명']`)를 정확히 참조하고, 데이터가 null인 경우 '정보 없음'으로 처리하는 방어적 코딩을 하세요.
3.  **UI 일관성**: 기존 `Phase2_이후_개발계획.md`에 정의된 사이버펑크 디자인 톤(Dark Theme, Neon Accent)을 유지하세요.
4.  **CORS & Protocol**: API 통신 시 `http`와 `https` 혼용 에러가 발생하지 않도록 상대 경로 또는 환경 변수를 활용하세요.

---

## 4. ✅ 최종 결과물 체크리스트
- [ ] Kakao Map이 지정된 영역에 정상 출력되는가?
- [ ] 필터 변경 시 해당되는 현장 마커만 지도에 실시간 반영되는가?
- [ ] 마커 클릭 시 상세 패널이 열리고 배정 로직으로 이어지는가?
- [ ] 좌표 데이터가 없는 현장을 주소 기반으로 지도에 표시하는 기능이 작동하는가?
- [ ] 모든 JS 모듈(`api.js`, `map.js`, `ui.js`)이 충돌 없이 유기적으로 작동하는가?

**지금 바로 STEP 1부터 순서대로 코드를 작성 및 리팩토링 해주세요.**