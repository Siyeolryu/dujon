@echo off
chcp 65001 >nul
echo ==========================================
echo   Claude Code (Windows) 설치
echo ==========================================
echo.
echo PowerShell 설치 스크립트를 실행합니다...
echo 관리자 권한이 필요할 수 있습니다.
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_claude_install.ps1"

echo.
echo ==========================================
pause
