@echo off
chcp 65001 >nul
echo ============================================
echo  Streamlit 오류 수정 - GitHub 푸시
echo ============================================
echo.

cd /d "%~dp0"

echo [1단계] 삭제된 파일들 Git에서 제거...
git rm --cached pages/1_dashboard.py 2>nul
git rm --cached pages/2_site_list.py 2>nul
git rm --cached pages/3_site_register.py 2>nul
git rm --cached pages/4_cert_register.py 2>nul
git rm --cached pages/8_personnel_detail.py 2>nul
git rm --cached pages/9_streamlit_app.py 2>nul
git rm --cached app_streamlit.py 2>nul

echo.
echo [2단계] 변경사항 스테이징...
git add -A

echo.
echo [3단계] 커밋...
git commit -m "fix: Streamlit 멀티페이지 오류 수정 - 중복 파일 삭제"

echo.
echo [4단계] GitHub에 푸시...
git push origin main

echo.
echo ============================================
echo  완료! Streamlit Cloud에서 앱이 자동 재배포됩니다.
echo  약 1-2분 후 확인하세요.
echo ============================================
echo.

pause
