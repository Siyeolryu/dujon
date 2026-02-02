# Streamlit 웹 운영 가이드

현장배정 관리 시스템을 **Streamlit**으로 실행·운영하는 방법입니다. Streamlit은 기존 Flask API를 그대로 호출합니다.

---

## 1. 사전 준비

- **Python 3** 설치
- **Flask API**가 먼저 실행되어 있어야 합니다 (Streamlit은 API 클라이언트 역할만 함)

### 의존성 설치

```bash
pip install -r requirements_streamlit.txt
```

---

## 2. 로컬 실행 방법

### 2-1. Flask API 실행 (터미널 1)

```bash
python run_api.py
```

- 포트 **5000**에서 API + 기존 HTML 정적 파일 서빙
- `.env` 및 Google 시트 설정 시 실제 데이터 사용

### 2-2. Streamlit 실행 (터미널 2)

프로젝트 루트에서:

```bash
streamlit run app_streamlit.py
```

- 기본 주소: **http://localhost:8501**
- 브라우저가 자동으로 열리지 않으면 위 주소로 접속

### 2-3. 환경 변수 (선택)

프로젝트 루트의 `.env`에 API 주소를 지정할 수 있습니다.

```env
API_BASE_URL=http://localhost:5000
```

- 없으면 기본값 `http://localhost:5000` 사용
- 배포 시 Flask API가 다른 서버에 있으면 해당 URL로 설정

---

## 3. 페이지 구성

| 페이지 | 경로 | 설명 |
|--------|------|------|
| 홈 | `app_streamlit.py` | API 연결 상태, 기존 웹 UI 링크 |
| 대시보드 | 사이드바 → 대시보드 | 통계(전체 현장, 미배정, 배정완료, 투입가능 인력, 사용가능 자격증) |
| 현장 목록 | 사이드바 → 현장 목록 | 필터·검색·테이블, 현장 상세, 소장 배정/해제 |
| 현장등록 | 사이드바 → 현장등록 | 새 현장 등록 (현장ID 자동 부여) |
| 자격증등록 | 사이드바 → 자격증등록 | 새 자격증 등록 (자격증ID·소유자ID 자동 부여) |

---

## 4. GitHub / Streamlit Cloud 배포 시 Main file path

배포 설정에서 **Main file path**를 다음 중 하나로 지정하세요 (저장소 루트 기준).

| Main file path | 설명 |
|----------------|------|
| **`app_streamlit.py`** | 메인 진입점 (권장) |
| **`streamlit_app.py`** | 동일 앱, Cloud에서 기본으로 찾는 이름 |

- **Requirements file**: `requirements_streamlit.txt` (또는 루트의 `requirements.txt` 사용 가능)
- **Branch**: `main` (또는 사용 중인 기본 브랜치)

---

## 5. 배포 옵션

- **Streamlit Cloud**: 레포에 `app_streamlit.py`(또는 `streamlit_app.py`)와 `pages/`를 올린 뒤 Streamlit Cloud에서 앱 연결. Main file path를 위 표대로 입력. `API_BASE_URL`만 배포된 Flask API URL로 설정.
- **Docker**: Streamlit 전용 Dockerfile에서 `streamlit run app_streamlit.py` 실행. Flask API는 별도 컨테이너 또는 서비스로 운영.
- **단일 서버**: 같은 서버에서 Flask(5000) + Streamlit(8501) 동시 실행 후, Nginx 등으로 경로 분리(예: `/` → Streamlit, `/api` → Flask).

---

## 6. 기존 HTML 웹 UI와의 관계

- **Streamlit**: 대시보드·목록·등록 폼 위주. 빠른 운영·배포용.
- **기존 HTML** (지도, AG-Grid 스타일 테이블 등): Flask 서버의 `http://localhost:5000/` 에서 그대로 사용 가능.
- Streamlit 홈 화면에서 "기존 웹 UI 열기" 링크로 동일 API 서버의 HTML 화면으로 이동할 수 있습니다.

---

## 7. 문제 해결

| 현상 | 확인 사항 |
|------|-----------|
| "API에 연결할 수 없습니다" | Flask API(`python run_api.py`)가 포트 5000에서 실행 중인지 확인 |
| 409 Conflict (배정/해제 시) | 다른 사용자가 동시에 수정했을 수 있음. 페이지 새로고침 후 재시도 |
| Streamlit 설치 오류 | `pip install -r requirements_streamlit.txt` 재실행, Python 버전 3.8 이상 권장 |
