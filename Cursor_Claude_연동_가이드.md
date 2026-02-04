# Cursor와 Claude 연동 가이드

**웹 Claude(claude.ai)**와 **Cursor**를 이어 쓰고 싶을 때 선택할 수 있는 방법입니다.

> **API 키는 월정액 계정으로 대체**  
> 별도 API 키 과금 없이 **Claude Pro/Max 월정액 계정**으로 로그인·동일 계정 API 키를 사용해 Cursor와 Claude Code를 쓸 수 있습니다.

---

## Claude Code 설치 완료 후 (Windows)

- **실행 파일**: `C:\Users\user\.local\bin\claude.exe`
- **PATH**: 사용자 PATH에 `C:\Users\user\.local\bin`이 추가되어 있음.  
  터미널에서 `claude` 명령이 동작하려면 **새 터미널** 또는 **Cursor 재시작**이 필요할 수 있습니다.
- **인증**: 터미널에서 `claude` 실행 후 **월정액(Claude Pro/Max) 계정**으로 브라우저 로그인하면 API 키 없이 사용할 수 있습니다.
- **확인**: `claude --version` → `2.1.29 (Claude Code)` 등으로 표시되면 정상입니다.

---

## Cursor에서 Claude Open으로 로그인하기

Cursor 안에서 **Claude Open**을 실행해 터미널에서 로그인할 수 있습니다.

1. **명령 팔레트**  
   `Ctrl + Shift + P` → **Tasks: Run Task** 입력 후 선택
2. **작업 선택**  
   목록에서 **Claude Open (로그인)** 선택
3. **로그인**  
   터미널에 Claude Code가 열리면, 인증 안내가 나오면 **월정액(Claude Pro/Max) 계정**으로 브라우저에서 로그인합니다.  
   이미 로그인된 경우에는 그대로 대화 세션이 시작됩니다.

**바로 가기**: 터미널 패널(`Ctrl + `` `)을 연 뒤 `claude` 입력 후 Enter 해도 동일하게 로그인·실행할 수 있습니다.

---

## 방법 1: Cursor에서 Claude 모델 사용 (권장)

Cursor 채팅/Composer에서 **Claude(Opus, Sonnet 등)**를 모델로 쓰려면, Anthropic API 키를 넣거나 **월정액(Claude Pro/Max)과 같은 계정**의 API 키를 사용하면 됩니다.

### API 키 vs 월정액 계정

- **월정액(Claude Pro/Max) 계정**을 쓰는 경우: 같은 Anthropic 계정에서 API 키를 한 번만 발급해 Cursor에 넣으면, 웹·CLI와 동일한 월정액 범위 안에서 Cursor에서도 Claude를 쓸 수 있습니다. (별도 API 종량 과금 없이 사용 가능한 경우가 많습니다.)
- API 키만 쓰는 경우: 콘솔에서 키 발급 후 사용량 기준 과금됩니다.

### 단계

1. **Anthropic API 키 발급** (월정액 계정으로 로그인)
   - [https://console.anthropic.com/](https://console.anthropic.com/) 에서 **월정액으로 쓰는 동일 계정**으로 로그인
   - **API Keys**에서 키 생성 후 복사  
   - 월정액 구독이 있으면 해당 계정의 API 사용이 구독에 포함될 수 있음

2. **Cursor에서 API 키 입력**
   - Cursor 메뉴: **File** → **Preferences** → **Cursor Settings**  
     (또는 `Ctrl + ,` 후 **Cursor Settings** 탭)
   - 왼쪽에서 **Models** 선택
   - **Anthropic API Key** 항목에 키 붙여넣기 → **Verify**
   - 사용할 Claude 모델(예: Claude 3.5 Sonnet, Claude 3 Opus) 선택/체크

3. **사용**
   - 채팅(Composer) 열고 모델 선택 시 **Claude** 선택  
   → Cursor 안에서 웹 Claude와 같은 계정의 Claude를 사용하는 효과

### 참고

- Cursor 공식: [API Keys | Cursor Docs](https://cursor.com/docs/settings/api-keys)
- Tab 자동완성 등 일부 기능은 Cursor 기본 모델을 계속 사용할 수 있음
- **월정액 계정**으로 콘솔에 로그인한 뒤 같은 계정의 API 키를 Cursor에 넣으면, 별도 API 과금 없이 월정액으로 사용할 수 있는 경우가 많습니다.

---

## 방법 2: Claude Code 확장을 Cursor에 설치 (CLI 연동)

**Claude Code**(CLI 도구)를 쓰고 있고, 그 경험을 Cursor와 같이 쓰고 싶다면, Claude Code 확장을 Cursor에 설치할 수 있습니다.

- **Claude Code**: 터미널에서 `claude` 명령으로 쓰는 코딩 도구  
- 이 확장을 Cursor에 설치하면, Cursor가 “지원 IDE”처럼 Claude Code와 연동됩니다.

### 사전 조건

- **Claude Code**가 이미 설치되어 있어야 함  
  - 설치: [Claude Code 개발자 도구킷](https://developertoolkit.ai/en/claude-code/quick-start/) 참고  
  - Windows에서는 WSL 또는 Git Bash 등 POSIX 환경에서 설치하는 경우가 많음

**참고**: Windows에서 공식 `install.ps1`(네이티브 빌드)으로만 설치한 경우, 아래 VSIX 경로가 없을 수 있습니다. Cursor에서 Claude를 쓰려면 **방법 1(API 키)** 를 사용하는 것이 가장 간단합니다.

### Cursor에 확장 설치 (Windows)

1. **VSIX 파일 위치**  
   Claude Code 설치 후 아래 경로에 `claude-code.vsix`가 있습니다.  
   ```
   %USERPROFILE%\.claude\local\node_modules\@anthropic-ai\claude-code\vendor\claude-code.vsix
   ```
   (탐색기 주소창에 `%USERPROFILE%\.claude` 입력 후 해당 폴더까지 이동해 확인)

2. **Cursor에 설치**
   - **방법 A (명령어)**  
     명령 프롬프트 또는 PowerShell에서:
     ```cmd
     cursor --install-extension "%USERPROFILE%\.claude\local\node_modules\@anthropic-ai\claude-code\vendor\claude-code.vsix"
     ```
   - **방법 B (Cursor 안에서)**  
     - `Ctrl + Shift + P` → **Extensions: Install from VSIX** 입력
     - 위 경로의 `claude-code.vsix` 파일 선택

3. **Cursor 완전히 종료 후 다시 실행**

이후 Cursor에서 Claude Code와 연동된 기능을 사용할 수 있습니다.

---

## 요약

| 목표 | 추천 방법 |
|------|-----------|
| Cursor 채팅/Composer에서 웹에서 쓰는 것처럼 Claude 쓰기 | **방법 1**: Cursor 설정에 API 키 추가 (월정액 계정과 동일 계정의 키 사용 권장) |
| Claude Code(CLI)와 Cursor를 함께 쓰기 | **방법 2**: Claude Code VSIX를 Cursor에 설치 |

“웹 Claude에 Cursor를 연결”하고 싶다면, 보통은 **방법 1**로 Cursor에서 Claude 모델을 선택해 쓰는 방식이 가장 직접적입니다.
