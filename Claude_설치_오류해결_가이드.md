# Claude Code 설치 오류 해결 (Git Bash 필요)

이미지와 같은 오류가 나는 이유: **Windows에서 Claude Code는 Git Bash가 필요**합니다.

---

## 오류 메시지

- `Claude Code on Windows requires git-bash (https://git-scm.com/downloads/win).`
- `If installed but not in PATH, set environment variable: CLAUDE_CODE_GIT_BASH_PATH=C:\Program Files\Git\bin\bash.exe`
- `Installation failed`

---

## 해결 방법 (둘 중 하나 선택)

### 방법 A: 자동 스크립트 (권장)

1. **관리자 권한**으로 실행  
   - `claude_install_with_git.bat` **우클릭 → 관리자 권한으로 실행**
2. 스크립트가 다음을 자동으로 수행합니다.  
   - Git Bash 설치 여부 확인  
   - 없으면 winget으로 Git for Windows 설치  
   - `CLAUDE_CODE_GIT_BASH_PATH` 사용자 환경 변수 설정  
   - Claude Code 설치 실행 여부 선택 (y/n)

**또는** 관리자 PowerShell에서:

```powershell
cd "c:\Users\user\.cursor\projects\배정관리 앱"
.\fix_claude_gitbash.ps1
```

---

### 방법 B: 수동 설정

#### 1단계: Git for Windows 설치

- 다운로드: **https://git-scm.com/download/win**
- 설치 시 **"Git Bash Here"** 등 기본 옵션 그대로 진행
- 설치 후 기본 경로: `C:\Program Files\Git\bin\bash.exe`

#### 2단계: 환경 변수 설정

1. **Windows 키** → "환경 변수" 검색 → **시스템 환경 변수 편집** 실행
2. **환경 변수** 버튼 클릭
3. **사용자 변수**에서 **새로 만들기**
   - 변수 이름: `CLAUDE_CODE_GIT_BASH_PATH`
   - 변수 값: `C:\Program Files\Git\bin\bash.exe`
4. **확인**으로 모두 닫기

#### 3단계: Claude Code 재설치

**새로 연** 명령 프롬프트 또는 PowerShell에서:

```cmd
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

또는 PowerShell:

```powershell
irm https://claude.ai/install.ps1 | iex
```

---

## 설치 확인

- `claude --version`  
- `claude` → 브라우저 로그인(인증)

---

## 요약

| 원인 | 조치 |
|------|------|
| Git Bash 미설치 | Git for Windows 설치 (https://git-scm.com/download/win) |
| Git 설치됐지만 PATH 없음 | `CLAUDE_CODE_GIT_BASH_PATH=C:\Program Files\Git\bin\bash.exe` 설정 |

**가장 빠른 방법:** `claude_install_with_git.bat` 을 **관리자 권한으로 실행**하세요.
