@echo off
chcp 65001 >nul
cd /d "%~dp0"
title GitHub 전체 업로드 - Siyeolryu/dujon
echo ============================================
echo   전체 파일 업로드: https://github.com/Siyeolryu/dujon
echo ============================================
echo.

if not exist .git (
  echo [1/4] Git 초기화 및 원격 연결...
  git init
  git remote add origin https://github.com/Siyeolryu/dujon.git
  git branch -M main
  echo.
) else (
  echo [1/4] Git 저장소 확인...
  git remote add origin https://github.com/Siyeolryu/dujon.git 2>nul
  if errorlevel 1 git remote set-url origin https://github.com/Siyeolryu/dujon.git
  git branch -M main
  echo.
)

echo [2/4] 전체 파일 스테이징 (git add .)...
git add .
git status
echo.

echo [3/4] 커밋...
git commit -m "전체 업로드: 현장배정 관리 시스템 Phase 2 (1단계~2-3)" 2>nul
if errorlevel 1 (
  echo   변경 사항이 없거나 이미 커밋됨. 푸시만 진행합니다.
) else (
  echo   커밋 완료.
)
echo.

echo [4/4] GitHub 푸시 (origin main)...
git push -u origin main
if errorlevel 1 (
  echo.
  echo   푸시 실패. GitHub 로그인 또는 Personal Access Token 확인 후 다시 실행하세요.
  echo   https://github.com/Siyeolryu/dujon
) else (
  echo.
  echo   전체 업로드 완료: https://github.com/Siyeolryu/dujon
)
echo.
pause
