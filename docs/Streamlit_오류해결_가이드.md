# Streamlit 멀티페이지 오류 해결 가이드

**오류**: `StreamlitAPIException` - `st.navigation()` 관련 오류  
**원인**: `pages/` 폴더에 중복 파일 및 잘못된 파일 존재  
**작성일**: 2026-02-04

---

## 🔴 발견된 문제점

### 1. pages/ 폴더에 중복 파일 (영문 + 한글)

Streamlit은 `pages/` 폴더를 자동으로 스캔하여 멀티페이지 앱을 구성합니다.  
같은 번호로 시작하는 파일이 여러 개 있으면 **충돌 오류**가 발생합니다.

| 영문 파일 (❌ 삭제) | 한글 파일 (✅ 유지) |
|-------------------|-------------------|
| `1_dashboard.py` | `1_대시보드.py` |
| `2_site_list.py` | `2_현장_목록.py` |
| `3_site_register.py` | `3_현장등록.py` |
| `4_cert_register.py` | `4_자격증등록.py` |
| `8_personnel_detail.py` | `8_투입가능인원_상세.py` |

### 2. pages/ 폴더에 9_streamlit_app.py 존재

이 파일은 **루트에만 있어야 하는 진입점 파일**입니다.  
`pages/` 폴더에 있으면 Streamlit이 페이지로 인식하여 오류 발생.

### 3. 루트에 진입점 파일 2개 존재

| 파일 | 조치 |
|------|------|
| `streamlit_app.py` | ✅ 유지 (Streamlit Cloud 기본 진입점) |
| `app_streamlit.py` | ❌ 삭제 (중복) |

---

## ✅ 해결 방법

### 방법 1: 배치 파일 실행 (권장)

1. **fix_streamlit_pages.bat**를 프로젝트 루트에 두고 더블클릭 실행
2. **git_push_fix.bat** 실행하여 GitHub에 푸시

### 방법 2: 수동으로 파일 삭제

**Git Bash 또는 터미널에서:**

```bash
cd "프로젝트_폴더"

# 1. 중복 영문 파일 삭제
git rm pages/1_dashboard.py
git rm pages/2_site_list.py
git rm pages/3_site_register.py
git rm pages/4_cert_register.py
git rm pages/8_personnel_detail.py

# 2. pages/의 streamlit_app 삭제
git rm pages/9_streamlit_app.py

# 3. 루트의 중복 진입점 삭제
git rm app_streamlit.py

# 4. 커밋 및 푸시
git commit -m "fix: Streamlit 멀티페이지 오류 수정 - 중복 파일 삭제"
git push origin main
```

---

## 📁 수정 후 올바른 파일 구조

```
(프로젝트 루트)/
├── streamlit_app.py              ← 메인 진입점 (유일)
├── requirements.txt
├── requirements_streamlit.txt
├── streamlit_utils/
│   ├── api_client.py
│   ├── theme.py
│   └── html_renderer.py
└── pages/
    ├── 1_대시보드.py              ← 한글 파일만 유지
    ├── 2_현장_목록.py
    ├── 3_현장등록.py
    ├── 4_자격증등록.py
    └── 8_투입가능인원_상세.py
```

---

## 🚀 실행 방법

- **로컬**: `streamlit run streamlit_app.py`
- **Streamlit Cloud**: Main file path에 `streamlit_app.py` 지정

---

## 🔄 Streamlit Cloud 재배포

GitHub에 푸시 후 Streamlit Cloud에서 자동으로 재배포됩니다.

만약 자동 재배포가 안 되면:
1. [Streamlit Cloud](https://share.streamlit.io/) 접속
2. 해당 앱의 **"Manage app"** 클릭
3. **"Reboot app"** 클릭

---

## ⚠️ requirements.txt 확인

```txt
streamlit>=1.28.0
requests>=2.31.0
python-dotenv>=1.0.0
pandas>=2.0.0
plotly>=5.17.0
supabase>=2.0.0
```

---

## 📞 문제 지속 시

오류가 계속되면 다음 정보와 함께 알려주세요:
1. Streamlit Cloud 로그 (Manage app → Logs)
2. `pages/` 폴더의 파일 목록
3. 루트 폴더의 `.py` 진입점 파일 목록
