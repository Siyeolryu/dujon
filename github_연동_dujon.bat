@echo off
chcp 65001 >nul
cd /d "%~dp0"
title GitHub 연동 - Siyeolryu/dujon
echo ============================================
echo   GitHub 연동: https://github.com/Siyeolryu/dujon
echo ============================================
echo.

if not exist .git (
  echo [1/3] Git 저장소 초기화...
  git init
  echo.
) else (
  echo [1/3] 이미 Git 저장소가 있습니다.
  echo.
)

echo [2/3] 원격 저장소 설정...
git remote remove origin 2>nul
git remote add origin https://github.com/Siyeolryu/dujon.git
git remote -v
echo.

echo [3/3] 기본 브랜치 main 설정...
git branch -M main
echo.

echo ============================================
echo   연동 완료.
echo   푸시: git_push_dujon.bat 실행 또는
echo         git add . ^& git commit -m "메시지" ^& git push -u origin main
echo ============================================
pause
