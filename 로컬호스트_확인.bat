@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   로컬호스트 확인 - 현장배정 관리 시스템
echo ========================================
echo.

REM 서버 창을 새로 띄움
start "현장배정 API 서버" cmd /k "cd /d "%~dp0" && (python run_api.py 2>nul || py -3 run_api.py 2>nul || node server.js)"
echo 서버를 시작했습니다. 잠시 후 브라우저가 열립니다...
echo.

REM 서버가 뜰 때까지 대기
timeout /t 3 /nobreak >nul

REM 브라우저로 로컬호스트 열기
start "" "http://localhost:5000/"

echo.
echo ========================================
echo   접속 주소: http://localhost:5000/
echo   API 정보: http://localhost:5000/api-info
echo   헬스:     http://localhost:5000/api/health
echo ========================================
echo 서버 창을 닫으면 접속이 끊깁니다.
pause
