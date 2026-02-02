# Claude Code - Git Bash 의존성 해결 스크립트
# 관리자 PowerShell에서 실행: .\fix_claude_gitbash.ps1

$ErrorActionPreference = "Stop"
$gitPaths = @(
    "C:\Program Files\Git\bin\bash.exe",
    "C:\Program Files (x86)\Git\bin\bash.exe",
    "$env:LOCALAPPDATA\Programs\Git\bin\bash.exe"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Claude Code - Git Bash 설정" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 기존 Git Bash 경로 찾기
$bashExe = $null
foreach ($p in $gitPaths) {
    if (Test-Path $p) {
        $bashExe = $p
        Write-Host "[확인] Git Bash 발견: $p" -ForegroundColor Green
        break
    }
}

# 2. 없으면 winget으로 Git 설치
if (-not $bashExe) {
    Write-Host "[설치] Git for Windows 설치 중 (winget)..." -ForegroundColor Yellow
    try {
        winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
        $bashExe = "C:\Program Files\Git\bin\bash.exe"
        if (-not (Test-Path $bashExe)) {
            Write-Host "[경고] 설치 후 경로를 확인하세요. 새 터미널을 열어야 PATH에 반영될 수 있습니다." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[실패] winget 설치 실패. 수동 설치: https://git-scm.com/download/win" -ForegroundColor Red
        exit 1
    }
}

# 3. 사용자 환경 변수 설정
if ($bashExe -and (Test-Path $bashExe)) {
    [System.Environment]::SetEnvironmentVariable("CLAUDE_CODE_GIT_BASH_PATH", $bashExe, "User")
    $env:CLAUDE_CODE_GIT_BASH_PATH = $bashExe
    Write-Host "[설정] CLAUDE_CODE_GIT_BASH_PATH = $bashExe" -ForegroundColor Green
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "  설정 완료!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "다음: 새 명령 프롬프트 또는 PowerShell을 열고 Claude Code 설치를 다시 실행하세요." -ForegroundColor Yellow
    Write-Host "  irm https://claude.ai/install.ps1 | iex" -ForegroundColor White
    Write-Host ""
    $rerun = Read-Host "지금 Claude Code 설치를 실행하시겠습니까? (y/n)"
    if ($rerun -eq "y" -or $rerun -eq "Y") {
        Invoke-RestMethod -Uri https://claude.ai/install.ps1 | Invoke-Expression
    }
} else {
    Write-Host "[오류] Git Bash 경로를 찾을 수 없습니다. Git을 수동 설치한 뒤 이 스크립트를 다시 실행하세요." -ForegroundColor Red
    exit 1
}
