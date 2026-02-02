@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo GitHub Siyeolryu/dujon push
echo.

if not exist .git (
  echo Git 초기화 및 원격 연결...
  git init
  git remote add origin https://github.com/Siyeolryu/dujon.git
  git branch -M main
)
git remote -v
echo.

git add .
git status
echo.
set /p msg="Commit message (Enter = default): "
if "%msg%"=="" set msg=Phase 2: 1단계~2-3 (Google Sheets 고급화, API, 실시간 동기화)
git commit -m "%msg%"
git branch -M main
git push -u origin main
echo.
echo Done.
pause
