# Claude Code Windows 설치 실행 스크립트
# 관리자 PowerShell에서: .\run_claude_install.ps1
# 또는 우클릭 -> PowerShell에서 실행

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
Invoke-RestMethod -Uri https://claude.ai/install.ps1 -OutFile $env:TEMP\claude_install.ps1
& $env:TEMP\claude_install.ps1
