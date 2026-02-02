@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   현장배정 관리 시스템 - 로컬 실행
echo   (프론트엔드 + 백엔드 동일 서버)
echo ========================================
echo.
echo 브라우저에서 접속: http://localhost:5000/
echo 종료: Ctrl+C
echo ========================================
echo.

REM Windows: python / py -3 / python3 순서로 시도
set PYCMD=
where python >nul 2>&1 && set PYCMD=python
if "%PYCMD%"=="" where py >nul 2>&1 && set PYCMD=py -3
if "%PYCMD%"=="" where python3 >nul 2>&1 && set PYCMD=python3
if "%PYCMD%"=="" (
    echo [오류] Python을 찾을 수 없습니다.
    echo.
    echo 1. Python 설치: https://www.python.org/downloads/
    echo 2. 설치 시 "Add Python to PATH" 체크
    echo 3. 또는 명령 프롬프트에서 python --version 확인
    echo.
    pause
    exit /b 1
)
%PYCMD% run_api.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [오류] 서버가 종료되었습니다. 위 메시지를 확인하세요.
    pause
)
