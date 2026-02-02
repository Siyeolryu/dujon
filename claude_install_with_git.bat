@echo off
chcp 65001 >nul
echo ==========================================
echo   Claude Code 설치 (Git Bash 자동 설정)
echo ==========================================
echo.
echo 1. Git Bash 확인/설치 및 환경변수 설정
echo 2. Claude Code 설치
echo.
echo 관리자 권한으로 실행하는 것을 권장합니다.
echo (우클릭 -^> 관리자 권한으로 실행)
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0fix_claude_gitbash.ps1"

echo.
pause
