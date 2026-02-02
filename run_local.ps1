# 현장배정 관리 시스템 - 로컬 실행 (PowerShell)
# 프론트엔드 + 백엔드 동일 서버 (http://localhost:5000/)

$Host.UI.RawUI.WindowTitle = "현장배정 관리 - 로컬"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " 현장배정 관리 시스템 - 로컬 실행" -ForegroundColor Cyan
Write-Host " (프론트엔드 + 백엔드 동일 서버)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "브라우저에서 아래 주소로 접속하세요:" -ForegroundColor Yellow
Write-Host "  http://localhost:5000/" -ForegroundColor Green
Write-Host ""
Write-Host "종료: 이 창에서 Ctrl+C" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

python run_api.py
