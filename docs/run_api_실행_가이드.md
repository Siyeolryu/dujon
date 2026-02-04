# `python run_api.py` 실행 가이드

Flask API 서버를 실행하는 방법과 문제 해결 가이드입니다.

---

## 🚀 빠른 시작

### 1. 기본 실행

```bash
python run_api.py
```

또는

```bash
py -3 run_api.py
```

### 2. 실행 확인

서버가 정상적으로 시작되면 다음과 같은 메시지가 표시됩니다:

```
==================================================
현장배정 관리 시스템 (API + 프론트엔드)
==================================================
  프론트엔드: http://localhost:5000/
  API 정보:   http://localhost:5000/api-info
  헬스:       http://localhost:5000/api/health
==================================================
종료: Ctrl+C
```

### 3. 접속 확인

브라우저에서 다음 URL로 접속하여 확인:

- **프론트엔드**: http://localhost:5000/
- **API 정보**: http://localhost:5000/api-info
- **헬스 체크**: http://localhost:5000/api/health

---

## ⚙️ 설정 확인

### 1. 포트 확인

**기본값**: 5000번 포트

포트를 변경하려면 `.env` 파일에 다음을 추가:

```env
FLASK_PORT=5000
```

**포트 충돌 확인**:

```bash
# Windows
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :5000
```

다른 프로그램이 5000번 포트를 사용 중이면:
- `.env` 파일에서 `FLASK_PORT`를 다른 포트로 변경 (예: `FLASK_PORT=5001`)
- 또는 해당 프로그램을 종료

---

### 2. 환경 변수 확인

`.env` 파일에 다음 설정이 올바르게 되어 있는지 확인:

#### 필수 설정

```env
# DB 백엔드 설정
DB_BACKEND=supabase

# Supabase 설정
SUPABASE_URL=https://hhpofxpnztzibtpkpiar.supabase.co
SUPABASE_KEY=your_service_role_secret_key
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Flask 서버 설정

```env
# Flask 포트 (기본값: 5000)
FLASK_PORT=5000

# 디버그 모드 (개발 시 True 권장)
FLASK_DEBUG=True

# CORS 허용 도메인
ALLOWED_ORIGINS=http://localhost:5000,http://localhost:8501,http://localhost:8000
```

#### Streamlit에서 API 호출 시 (선택사항)

```env
# Streamlit이 Flask API를 호출할 때 사용하는 URL
# 로컬 개발: http://localhost:5000/api
API_BASE_URL=http://localhost:5000/api
```

**주의**: `API_BASE_URL`은 Streamlit 앱에서 Flask API를 호출할 때 사용됩니다. 
- 로컬 개발: `http://localhost:5000/api` (포트 번호 포함)
- 배포 환경: 실제 API 서버 URL (예: `https://your-api-server.com/api`)

---

### 3. 방화벽 확인

로컬호스트 연결이 차단되지 않았는지 확인:

#### Windows 방화벽 확인

1. **Windows 보안** → **방화벽 및 네트워크 보호**
2. **고급 설정** → **인바운드 규칙**
3. Python 또는 포트 5000에 대한 규칙이 차단되어 있지 않은지 확인

#### 방화벽 예외 추가 (필요 시)

```powershell
# PowerShell 관리자 권한으로 실행
New-NetFirewallRule -DisplayName "Flask API Port 5000" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

#### 로컬호스트 연결 테스트

```bash
# PowerShell
Test-NetConnection -ComputerName localhost -Port 5000

# 또는 브라우저에서
# http://localhost:5000/api/health 접속 시도
```

---

## 🔧 문제 해결

### 문제 1: 포트가 이미 사용 중입니다

**에러 메시지**:
```
OSError: [WinError 10048] 보통 각 소켓 주소(프로토콜/네트워크 주소/포트)는 한 번만 사용할 수 있습니다.
```

**해결 방법**:

1. **포트 사용 중인 프로세스 확인**:
   ```bash
   # Windows
   netstat -ano | findstr :5000
   ```

2. **프로세스 종료**:
   ```bash
   # PID 확인 후
   taskkill /PID <PID번호> /F
   ```

3. **또는 다른 포트 사용**:
   ```env
   # .env 파일 수정
   FLASK_PORT=5001
   ```

---

### 문제 2: 모듈을 불러올 수 없습니다

**에러 메시지**:
```
[오류] 모듈을 불러올 수 없습니다.
ModuleNotFoundError: No module named 'flask'
```

**해결 방법**:

1. **의존성 설치**:
   ```bash
   pip install -r requirements_api.txt
   ```

2. **또는 개별 설치**:
   ```bash
   pip install flask flask-cors python-dotenv supabase
   ```

---

### 문제 3: Supabase 연결 실패

**에러 메시지**:
```
ValueError: SUPABASE_URL, SUPABASE_KEY를 설정해 주세요. .env에 추가하세요.
```

**해결 방법**:

1. **`.env` 파일 확인**:
   - `SUPABASE_URL`이 올바르게 설정되어 있는지 확인
   - `SUPABASE_KEY`가 올바르게 설정되어 있는지 확인

2. **환경 변수 로드 확인**:
   - `.env` 파일이 프로젝트 루트에 있는지 확인
   - 파일 이름이 정확히 `.env`인지 확인 (`.env.example`이 아님)

---

### 문제 4: API 연결 실패 (Streamlit에서)

**에러 메시지**:
```
❌ API 연결 실패: Connection refused
```

**해결 방법**:

1. **Flask API 서버 실행 확인**:
   ```bash
   python run_api.py
   ```

2. **포트 확인**:
   - Flask 서버가 실행 중인 포트 확인 (기본값: 5000)
   - `.env`의 `FLASK_PORT`와 `API_BASE_URL`의 포트가 일치하는지 확인

3. **API_BASE_URL 확인**:
   ```env
   # .env 파일
   API_BASE_URL=http://localhost:5000/api
   ```
   - 포트 번호가 올바른지 확인
   - `/api` 경로가 포함되어 있는지 확인

---

### 문제 5: CORS 오류

**에러 메시지** (브라우저 콘솔):
```
Access to fetch at 'http://localhost:5000/api/sites' from origin 'http://localhost:8501' has been blocked by CORS policy
```

**해결 방법**:

1. **`.env` 파일에 CORS 설정 추가**:
   ```env
   ALLOWED_ORIGINS=http://localhost:5000,http://localhost:8501,http://localhost:8000,http://127.0.0.1:5000,http://127.0.0.1:8501
   ```

2. **서버 재시작**:
   ```bash
   # Ctrl+C로 서버 종료 후
   python run_api.py
   ```

---

## 📋 체크리스트

서버 실행 전 확인사항:

- [ ] `.env` 파일이 프로젝트 루트에 존재
- [ ] `DB_BACKEND=supabase` 설정됨
- [ ] `SUPABASE_URL` 설정됨
- [ ] `SUPABASE_KEY` 설정됨
- [ ] `FLASK_PORT=5000` 설정됨 (또는 원하는 포트)
- [ ] 포트 5000이 다른 프로그램에 사용 중이지 않음
- [ ] `requirements_api.txt`의 패키지가 설치됨
- [ ] 방화벽이 로컬호스트 연결을 차단하지 않음
- [ ] Streamlit 사용 시 `API_BASE_URL=http://localhost:5000/api` 설정됨

---

## 🔍 디버깅

### 로그 확인

서버 실행 시 디버그 모드가 활성화되어 있으면 상세한 에러 메시지가 표시됩니다:

```env
FLASK_DEBUG=True
```

### 헬스 체크

API 서버가 정상 작동하는지 확인:

```bash
# 브라우저에서
http://localhost:5000/api/health

# 또는 curl
curl http://localhost:5000/api/health
```

**예상 응답**:
```json
{
  "status": "healthy",
  "service": "site-management-api",
  "timestamp": "2026-02-04T12:00:00"
}
```

### API 정보 확인

```bash
# 브라우저에서
http://localhost:5000/api-info
```

---

## 📚 관련 문서

- [로컬호스트 확인 가이드](로컬호스트_확인.md)
- [로컬 실행 가이드](로컬실행_가이드.md)
- [Supabase 연동 가이드](Supabase_연동_가이드.md)
- [API README](../api/README.md)

---

## 💡 팁

1. **터미널 여러 개 사용**: 
   - 터미널 1: `python run_api.py` (Flask API 서버)
   - 터미널 2: `streamlit run app_streamlit.py` (Streamlit 앱)

2. **포트 변경 시**: 
   - `.env`의 `FLASK_PORT` 변경
   - Streamlit 사용 시 `API_BASE_URL`도 함께 변경

3. **자동 재시작**: 
   - `FLASK_DEBUG=True` 설정 시 코드 변경 시 자동 재시작됨
