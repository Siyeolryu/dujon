# Cursor와 Google Workspace 연결 가이드

Cursor에서 **Google Workspace**(Gmail, Google 캘린더 등)를 사용하려면 **MCP(Model Context Protocol)** 서버인 **mcp-gsuite**를 설정합니다. 설정 후 Composer에서 "최근 메일 요약해줘", "내일 일정 알려줘" 같은 요청을 할 수 있습니다.

> **참고:** Gmail/캘린더 연동에는 **OAuth 2.0 클라이언트 ID·시크릿**이 필요합니다.  
> Google API 키(예: `AIzaSy...`)는 이 MCP에서 사용하지 않습니다. Cloud Console에서 "OAuth 클라이언트 ID"를 만들어 `.gauth.json`에 넣어야 합니다.

---

## 1. 사전 준비

### 1.1 uv 설치 (Python 패키지 실행 도구)

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

설치 후 터미널을 다시 열고 `uvx --version`으로 확인합니다.

### 1.2 Google Cloud OAuth2 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. **프로젝트** 생성 또는 기존 프로젝트 선택
3. **API 및 서비스** → **라이브러리**에서 다음 API 사용 설정:
   - **Gmail API**
   - **Google Calendar API**
4. **API 및 서비스** → **사용자 인증 정보** → **사용자 인증 정보 만들기** → **OAuth 클라이언트 ID**
5. 애플리케이션 유형: **데스크톱 앱** 또는 **웹 애플리케이션**
6. **승인된 리디렉션 URI**에 `http://localhost:4100/code` 추가
7. OAuth 동의 화면에서 필요한 범위 설정 후, 생성된 **클라이언트 ID**와 **클라이언트 보안 비밀** 복사

---

## 2. 설정 폴더 및 파일 준비

### 2.1 설정 폴더 만들기

다음 폴더가 이미 생성되어 있습니다.

- **Windows:** `C:\Users\user\.cursor\google-workspace`
- **계정(.accounts.json):** siyeolryu00@gmail.com (work, 업무용·개발용) 적용됨

### 2.2 인증 설정 파일 (.gauth.json)

1. 이 프로젝트의 `google-workspace-config\.gauth.json.example` 파일을 복사합니다.
2. `C:\Users\user\.cursor\google-workspace\` 폴더에 **`.gauth.json`** 이름으로 붙여넣습니다.
3. `.gauth.json`을 열어 다음을 실제 값으로 수정합니다.
   - `client_id`: Google Cloud에서 복사한 클라이언트 ID
   - `client_secret`: Google Cloud에서 복사한 클라이언트 보안 비밀
   - `redirect_uris`는 그대로 `["http://localhost:4100/code"]` 유지

### 2.3 계정 설정 파일 (.accounts.json)

**이미 적용됨:** `C:\Users\user\.cursor\google-workspace\.accounts.json`에  
siyeolryu00@gmail.com (account_type: work, extra_info: 업무용, 개발용)이 설정되어 있습니다.  
추가 계정이 필요하면 같은 형식으로 `accounts` 배열에 항목을 더 넣으면 됩니다.

---

## 3. Cursor MCP 설정

전역 MCP 설정 파일에 Google Workspace 서버가 이미 추가되어 있습니다.

- **설정 파일 위치:** `C:\Users\user\.cursor\mcp.json`
- **서버 이름:** `google-workspace`

경로를 바꾼 경우(예: 다른 사용자명) `mcp.json` 안의 `google-workspace` 항목에서 다음 경로만 본인 경로로 수정하면 됩니다.

- `--gauth-file`: `.gauth.json` 전체 경로
- `--accounts-file`: `.accounts.json` 전체 경로
- `--credentials-dir`: 토큰이 저장될 폴더 (예: `...\google-workspace\credentials`)

---

## 4. 첫 사용 시 로그인

1. Cursor를 **재시작**합니다.
2. **Composer**(Agent)를 연 뒤, Google 관련 도구를 쓰는 요청을 합니다.  
   예: "내 Gmail 최근 읽지 않은 메일 5개 요약해줘"
3. 처음에는 **브라우저가 열리며 Google 로그인 및 권한 승인**을 요청합니다.
4. 승인하면 토큰이 `--credentials-dir`에 저장되고, 다음부터는 자동으로 사용됩니다.

---

## 5. 사용 예시 (Composer에서)

- "최근 읽지 않은 메일 알려줘"
- "○○○님이 보낸 메일 검색해줘"
- "내일 일정 알려줘"
- "다음 주 회의 이벤트 하나 만들어줘"

---

## 6. 문제 해결

| 현상 | 확인 사항 |
|------|-----------|
| MCP 서버가 안 뜸 | `uvx --version`으로 uv 설치 여부 확인, Cursor 재시작 |
| 로그인 창이 안 뜸 | `.gauth.json`의 `redirect_uris`에 `http://localhost:4100/code` 있는지 확인 |
| "권한 없음" 오류 | Google Cloud에서 Gmail API, Calendar API 사용 설정 및 OAuth 동의 화면 범위 확인 |
| Windows에서 경로 오류 | `mcp.json` 경로에 `\\` 이스케이프가 올바른지, 또는 `/` 사용 여부 확인 |

설정 파일 위치 요약:
- 인증/계정: `C:\Users\user\.cursor\google-workspace\.gauth.json`, `.accounts.json`
- MCP 설정: `C:\Users\user\.cursor\mcp.json`
