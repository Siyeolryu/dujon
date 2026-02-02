# WSL2 설치를 위한 Windows 기능 활성화 스크립트
# 관리자 권한 PowerShell에서 실행하세요: .\enable_wsl_features.ps1

$ErrorActionPreference = "Stop"
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  WSL2 필수 Windows 기능 활성화" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Linux용 Windows 하위 시스템 활성화
Write-Host "[1/2] Linux용 Windows 하위 시스템 활성화 중..." -ForegroundColor Yellow
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
if ($LASTEXITCODE -ne 0) { Write-Host "실패" -ForegroundColor Red; exit 1 }
Write-Host "완료" -ForegroundColor Green
Write-Host ""

# 2. 가상 머신 플랫폼 활성화
Write-Host "[2/2] 가상 머신 플랫폼 활성화 중..." -ForegroundColor Yellow
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
if ($LASTEXITCODE -ne 0) { Write-Host "실패" -ForegroundColor Red; exit 1 }
Write-Host "완료" -ForegroundColor Green
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  기능 활성화 완료!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "다음 단계:" -ForegroundColor Yellow
Write-Host "1. 컴퓨터를 재시작하세요." -ForegroundColor White
Write-Host "2. 재시작 후 관리자 PowerShell에서 다음 명령 실행:" -ForegroundColor White
Write-Host "   wsl --install" -ForegroundColor Cyan
Write-Host ""
Write-Host "BIOS 가상화가 꺼져 있다면:" -ForegroundColor Yellow
Write-Host "- 재부팅 시 F2/F10/Del 키로 BIOS 진입" -ForegroundColor White
Write-Host "- Virtualization Technology / VT-x / AMD-V 항목을 Enabled로 설정" -ForegroundColor White
Write-Host ""
$restart = Read-Host "지금 재시작하시겠습니까? (y/n)"
if ($restart -eq "y" -or $restart -eq "Y") { shutdown /r /t 30 }
