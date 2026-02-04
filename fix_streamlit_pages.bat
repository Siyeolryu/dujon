@echo off
chcp 65001 >nul
echo ============================================
echo  Streamlit 페이지 오류 수정 스크립트
echo ============================================
echo.

cd /d "%~dp0"

echo [1단계] 중복 영문 페이지 파일 삭제...
echo.

REM pages/ 폴더의 영문 파일들 삭제 (한글 파일만 유지)
if exist "pages\1_dashboard.py" (
    del "pages\1_dashboard.py"
    echo   삭제: pages\1_dashboard.py
)

if exist "pages\2_site_list.py" (
    del "pages\2_site_list.py"
    echo   삭제: pages\2_site_list.py
)

if exist "pages\3_site_register.py" (
    del "pages\3_site_register.py"
    echo   삭제: pages\3_site_register.py
)

if exist "pages\4_cert_register.py" (
    del "pages\4_cert_register.py"
    echo   삭제: pages\4_cert_register.py
)

if exist "pages\8_personnel_detail.py" (
    del "pages\8_personnel_detail.py"
    echo   삭제: pages\8_personnel_detail.py
)

echo.
echo [2단계] pages/ 폴더의 streamlit_app 파일 삭제...
echo.

REM 9_streamlit_app.py가 pages/에 있으면 삭제 (이 파일은 pages에 있으면 안됨)
if exist "pages\9_streamlit_app.py" (
    del "pages\9_streamlit_app.py"
    echo   삭제: pages\9_streamlit_app.py
)

echo.
echo [3단계] 루트의 중복 진입점 파일 삭제...
echo.

REM app_streamlit.py 삭제 (streamlit_app.py만 유지)
if exist "app_streamlit.py" (
    del "app_streamlit.py"
    echo   삭제: app_streamlit.py
)

echo.
echo ============================================
echo  완료! 남은 파일 구조:
echo ============================================
echo.
echo   (프로젝트 루트)/
echo   ├── streamlit_app.py          (메인 진입점)
echo   ├── requirements.txt
echo   └── pages/
echo       ├── 1_대시보드.py
echo       ├── 2_현장_목록.py
echo       ├── 3_현장등록.py
echo       ├── 4_자격증등록.py
echo       └── 8_투입가능인원_상세.py
echo.
echo ============================================
echo.

pause
