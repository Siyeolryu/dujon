# Streamlit 로컬호스트 UI 통합 가이드

**작성일**: 2026년 2월 4일  
**목적**: 로컬호스트의 HTML/JS UI를 Streamlit에 직접 통합

---

## 📋 개요

로컬호스트에서 개발한 HTML/JS 기반 UI(`site-management.html`)를 Streamlit Cloud 배포 환경에 그대로 적용하기 위해, CSS와 JS 파일을 인라인으로 포함시키는 방식으로 통합했습니다.

---

## ✅ 완료된 작업

### 1. HTML 렌더러 모듈 생성
- `streamlit_utils/html_renderer.py`: HTML 파일을 Streamlit에 렌더링
- `streamlit_utils/static_inliner.py`: CSS/JS 파일을 인라인으로 포함

### 2. 메인 앱 통합
- `app_streamlit.py`: 로컬호스트의 `site-management.html`을 직접 렌더링
- iframe이나 외부 링크가 아닌 직접 통합

### 3. 대시보드 페이지 통합
- `pages/1_대시보드.py`: 로컬호스트의 대시보드 UI를 그대로 사용

---

## 🔧 작동 방식

### 로컬 개발 환경

1. **HTML 파일 로드**: `site-management.html` 파일을 읽어옴
2. **CSS/JS 인라인화**: 외부 CSS/JS 파일을 HTML 내부에 포함
3. **API URL 설정**: 환경 변수에서 API URL 읽어서 설정
4. **Streamlit 렌더링**: `st.components.v1.html()`로 렌더링

### Streamlit Cloud 배포 환경

1. **정적 파일 없이 동작**: 모든 CSS/JS가 HTML에 인라인으로 포함됨
2. **API URL 자동 설정**: `/api` 경로로 자동 설정
3. **Flask API 연동**: 별도 Flask 서버 또는 같은 서버의 `/api` 경로 사용

---

## 📝 사용 방법

### 로컬 실행

```bash
# 1. Flask API 서버 실행 (터미널 1)
python run_api.py

# 2. Streamlit 실행 (터미널 2)
streamlit run app_streamlit.py
```

### Streamlit Cloud 배포

1. **GitHub에 푸시**
   ```bash
   git add .
   git commit -m "Streamlit 로컬호스트 UI 통합"
   git push origin main
   ```

2. **Streamlit Cloud 설정**
   - Main file path: `app_streamlit.py`
   - Requirements file: `requirements_streamlit.txt`
   - Branch: `main`

3. **환경 변수 설정** (Streamlit Secrets)
   ```
   API_BASE_URL=https://your-api-server.com
   ```

---

## 🎨 UI/UX 특징

- **로컬호스트 UI 그대로 사용**: `site-management.html`의 모든 기능과 스타일 유지
- **반응형 디자인**: 모바일/태블릿/데스크톱 모두 지원
- **인터랙티브 요소**: 지도, 필터, 검색 등 모든 기능 동작
- **실시간 업데이트**: API 연동으로 실시간 데이터 표시

---

## 🔍 문제 해결

### CSS/JS가 로드되지 않는 경우

**원인**: Streamlit Cloud에서 정적 파일 접근 불가

**해결**: `static_inliner.py`가 자동으로 CSS/JS를 인라인으로 포함시킵니다.

### API 연결 실패

**원인**: Flask API 서버가 실행되지 않음 또는 URL 설정 오류

**해결**:
1. 로컬: `python run_api.py` 실행 확인
2. 배포: Streamlit Secrets에 `API_BASE_URL` 설정 확인

### plotly 오류

**원인**: `pages/1_대시보드.py`에서 plotly import하지만 사용하지 않음

**해결**: plotly를 사용하지 않으므로 import 제거 (이미 완료)

---

## 📊 파일 구조

```
streamlit_utils/
├── html_renderer.py      # HTML 렌더링 유틸리티
├── static_inliner.py     # CSS/JS 인라인화 유틸리티
├── api_client.py         # API 클라이언트
└── theme.py              # 테마 설정

pages/
├── 1_대시보드.py          # 대시보드 (HTML/JS 통합)
├── 2_현장_목록.py          # 현장 목록
├── 3_현장등록.py           # 현장 등록
└── 4_자격증등록.py         # 자격증 등록

app_streamlit.py          # 메인 앱 (HTML/JS 통합)
```

---

## 🚀 다음 단계

1. **테스트**: 로컬에서 `streamlit run app_streamlit.py` 실행하여 확인
2. **배포**: Streamlit Cloud에 배포하여 실제 환경에서 테스트
3. **최적화**: 필요시 CSS/JS 최적화 및 압축

---

## 📌 주의사항

- **파일 크기**: CSS/JS를 인라인으로 포함하면 HTML 파일 크기가 커질 수 있음
- **캐싱**: Streamlit Cloud에서는 HTML이 매번 재생성되므로 캐싱 이점 없음
- **디버깅**: 개발 시에는 외부 파일 사용, 배포 시에만 인라인화 권장

---

## 📎 참고 문서

- Streamlit Components: https://docs.streamlit.io/library/components
- HTML Components: https://docs.streamlit.io/library/components/components-api#components.html
