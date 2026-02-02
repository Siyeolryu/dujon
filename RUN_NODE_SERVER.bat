@echo off
chcp 65001 >nul
cd /d "%~dp0"

title 현장배정 관리 - Node 서버 (종료: Ctrl+C)
color 0A

echo.
echo ============================================================
echo   현장배정 관리 시스템 - Node.js 로컬 서버
echo ============================================================
echo.
echo   브라우저에서 접속:  http://localhost:5000/
echo.
echo   이 창을 닫지 마세요. 종료하려면 Ctrl+C 입력 후 닫기.
echo ============================================================
echo.

where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [오류] Node.js를 찾을 수 없습니다.
    echo https://nodejs.org 에서 설치 후 다시 실행하세요.
    pause
    exit /b 1
)

node server.js
pause
