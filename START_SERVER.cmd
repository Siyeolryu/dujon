@echo off
chcp 65001 >nul
cd /d "%~dp0"

title 현장배정 관리 - 서버 (종료: Ctrl+C)
color 0A

echo.
echo ============================================================
echo   현장배정 관리 시스템 - 서버 시작
echo ============================================================
echo.
echo   브라우저에서 접속:  http://localhost:5000/
echo.
echo   이 창을 닫지 마세요. 종료하려면 Ctrl+C 입력 후 닫기.
echo ============================================================
echo.

REM PATH에 Python이 있어야 함. 순서대로 시도.
set PYCMD=
where python >nul 2>&1 && set PYCMD=python
if "%PYCMD%"=="" where py >nul 2>&1 && set PYCMD=py -3
if "%PYCMD%"=="" where python3 >nul 2>&1 && set PYCMD=python3

if "%PYCMD%"=="" (
    echo [오류] Python을 찾을 수 없습니다.
    echo.
    echo 1. Python 설치: https://www.python.org/downloads/
    echo 2. 설치 시 반드시 "Add Python to PATH" 체크
    echo 3. 설치 후 이 창을 닫고 새로 열어서 다시 실행
    echo.
    pause
    exit /b 1
)

echo Python: %PYCMD%
echo.
%PYCMD% run_api.py

if errorlevel 1 (
    echo.
    echo [오류] 서버가 종료되었습니다. 위 메시지를 확인하세요.
    echo 의존성 설치: pip install -r requirements_api.txt
    echo.
)
pause
