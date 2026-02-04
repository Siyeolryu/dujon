# Streamlit API 연결 및 기존 웹 배포 문제점 점검 보고서

**작성일**: 2026년 2월 4일  
**점검자**: Frontend/UI-UX 전문가 (30년 경력)  
**점검 범위**: Streamlit API 연결 로직, 기존 웹 배포 구조, 환경 설정 불일치

---

## 📋 실행 요약

Streamlit에서 API 연결 확인 로직과 기존 웹 배포 구조를 점검한 결과, **여러 중요한 문제점**을 발견했습니다. 특히 API 모드 설정 불일치, 배포 환경별 설정 부재, CORS 및 정적 파일 서빙 구조의 문제가 발견되었습니다.

---

## 🔴 Critical 문제점

### 1. **API 모드 설정 불일치 (Critical)**

#### 문제 상황
- **Streamlit**: Flask API를 직접 호출 (`streamlit_utils/api_client.py`)
- **기존 웹 (`site-management.html`)**: `js/config.js`에서 `API_MODE: 'supabase'`로 설정되어 Supabase 직접 연결 시도
- **두 프론트엔드가 서로 다른 백엔드 연결 방식 사용**

#### 영향
- Streamlit은 Flask API를 통해 동작하므로 정상 작동
- 기존 웹은 Supabase 직접 연결을 시도하므로 Flask API 서버가 실행 중이어도 무시됨
- 배포 시 두 프론트엔드가 서로 다른 데이터 소스에 접근할 수 있음
- 데이터 일관성 문제 발생 가능

#### 관련 파일
- `js/config.js`: `API_MODE: 'supabase'` (기본값)
- `js/api.js`: `CONFIG.API_MODE`에 따라 Flask 또는 Supabase 선택
- `streamlit_utils/api_client.py`: Flask API만 사용

---

### 2. **Streamlit API 연결 확인 로직의 문제**

#### 문제 상황
```python
# streamlit_utils/api_client.py
API_BASE = os.getenv('API_BASE_URL', 'http://localhost:5000').rstrip('/')

def _url(path):
    p = path if path.startswith('/') else '/' + path
    return f"{API_BASE}{p}"

def check_api_connection():
    try:
        r = requests.get(_url('/api/health'), timeout=5)
        return r.status_code == 200
    except Exception:
        return False
```

**문제점**:
- `API_BASE`가 `http://localhost:5000`이고, `_url('/api/health')`를 호출하면 `http://localhost:5000/api/health`가 됨
- 하지만 `API_BASE`에 이미 `/api`가 포함되어 있지 않으므로, 실제 Flask 라우트는 `/api/health`가 맞음
- **정상 동작하지만, 에러 메시지가 불명확함**

#### 개선 필요 사항
- 연결 실패 시 구체적인 에러 메시지 제공 부재
- 타임아웃(5초)이 짧아 느린 네트워크에서 실패할 수 있음
- 재시도 로직 없음

---

### 3. **배포 환경별 API URL 설정 부재 (Critical)**

#### 문제 상황
- **로컬 개발**: `http://localhost:5000` 하드코딩
- **배포 환경**: 환경 변수나 런타임 설정으로 변경 불가능
- Streamlit Cloud 배포 시 Flask API가 다른 서버에 있으면 연결 불가

#### 현재 구조
```python
# streamlit_utils/api_client.py
API_BASE = os.getenv('API_BASE_URL', 'http://localhost:5000').rstrip('/')
```

```javascript
// js/config.js
API_BASE_URL: (typeof window !== 'undefined' && window.__API_BASE_URL__)
    ? window.__API_BASE_URL__
    : (typeof window !== 'undefined' && window.location && window.location.origin
        ? window.location.origin + '/api'
        : 'http://localhost:5000/api'),
```

**문제점**:
- Streamlit은 환경 변수만 사용 (배포 시 Streamlit Secrets 설정 필요)
- 기존 웹은 `window.__API_BASE_URL__` 런타임 주입 방식 지원 (HTML에서 설정)
- **두 방식이 일치하지 않음**

---

### 4. **기존 웹 배포 시 정적 파일 서빙 구조 문제**

#### 문제 상황
```python
# api/app.py
@app.route('/')
def index():
    return send_from_directory(PROJECT_ROOT, 'site-management.html')

@app.route('/css/<path:subpath>')
def serve_css(subpath):
    return send_from_directory(os.path.join(PROJECT_ROOT, 'css'), subpath)

@app.route('/js/<path:subpath>')
def serve_js(subpath):
    return send_from_directory(os.path.join(PROJECT_ROOT, 'js'), subpath)
```

**문제점**:
- Flask가 정적 파일을 서빙하는 구조는 로컬 개발에는 적합하지만, 배포 시 문제 발생 가능:
  1. **프로덕션 서버**: Nginx 등 웹 서버가 정적 파일을 직접 서빙하는 것이 효율적
  2. **CDN 배포**: 정적 파일을 CDN에 배포하는 경우 Flask 라우트가 불필요
  3. **보안**: Flask가 모든 정적 파일을 서빙하면 보안 설정이 복잡해짐
  4. **성능**: Python 프로세스가 정적 파일 요청을 처리하면 성능 저하

---

### 5. **CORS 설정의 배포 환경 대응 부족**

#### 문제 상황
```python
# api/app.py
CORS(app, resources={
    r"/api/*": {
        "origins": os.getenv(
            'ALLOWED_ORIGINS',
            'http://localhost:5000,http://127.0.0.1:5000,http://localhost:8000,http://127.0.0.1:8000,http://localhost:8501,http://127.0.0.1:8501'
        ).split(','),
        ...
    }
})
```

**문제점**:
- 기본값이 로컬호스트만 포함
- 배포 시 프로덕션 도메인을 환경 변수로 설정해야 함
- Streamlit Cloud 도메인 등이 기본값에 포함되지 않음
- **환경 변수 누락 시 CORS 오류 발생**

---

## 🟡 Medium 문제점

### 6. **에러 처리 및 사용자 피드백 부족**

#### 문제 상황
- `check_api_connection()` 실패 시 단순히 `False` 반환
- 사용자에게 구체적인 원인(네트워크 오류, 서버 미실행, 타임아웃 등) 제공하지 않음
- Streamlit 페이지에서 "Flask 서버를 먼저 실행하세요" 메시지만 표시

#### 개선 필요 사항
- 연결 실패 원인별 구체적인 메시지 제공
- 재시도 버튼 또는 자동 재연결 기능
- 서버 상태 모니터링 및 시각적 피드백

---

### 7. **환경 변수 문서화 부족**

#### 문제 상황
- `.env.example`에 `API_BASE_URL`이 주석 처리되어 있음
- 배포 시 필요한 환경 변수 목록이 명확하지 않음
- Streamlit Cloud Secrets 설정 방법이 문서화되지 않음

---

### 8. **기존 웹의 API 모드 전환 로직 복잡성**

#### 문제 상황
```javascript
// js/api.js
async request(endpoint, options = {}) {
    // API_MODE가 'supabase'이고 SupabaseAPI가 있으면 Supabase 사용
    if (CONFIG.API_MODE === 'supabase' && typeof SupabaseAPI !== 'undefined') {
        return await SupabaseAPI.request(endpoint, options);
    }
    // 그 외에는 Flask API 사용
    const url = endpoint.startsWith('http') ? endpoint : `${CONFIG.API_BASE_URL}${endpoint}`;
    ...
}
```

**문제점**:
- 런타임에 API 모드가 결정되므로 디버깅이 어려움
- 두 가지 백엔드 연결 방식이 혼재하여 유지보수 복잡
- 배포 시 어떤 모드를 사용할지 명확하지 않음

---

## 🟢 Low 문제점

### 9. **중복된 Streamlit 진입점 파일**

#### 문제 상황
- `app_streamlit.py`와 `streamlit_app.py`가 거의 동일한 내용
- GitHub/Streamlit Cloud 배포 시 둘 중 하나만 필요

#### 개선 필요 사항
- 하나로 통일하거나, 하나는 다른 용도로 사용하도록 명확히 구분

---

### 10. **타임아웃 설정이 짧음**

#### 문제 상황
```python
# streamlit_utils/api_client.py
TIMEOUT = 15  # 일반 API 호출
# check_api_connection()에서는 timeout=5 사용
```

**문제점**:
- 헬스 체크에 5초는 적절하지만, 느린 네트워크나 서버 부하 시 실패할 수 있음
- 일반 API 호출의 15초와 불일치

---

## ✅ 정상 동작하는 부분

1. **Flask API 라우트 구조**: 모든 엔드포인트가 올바르게 정의됨
2. **Streamlit API 클라이언트 기본 구조**: Flask API 호출 로직은 정상
3. **기존 웹의 런타임 API URL 주입**: `window.__API_BASE_URL__` 지원은 좋은 설계
4. **에러 로깅**: 백엔드-프론트엔드 연결 문제 추적 로직 구현됨

---

## 🔧 개선 방안

### 즉시 조치 (High Priority)

#### 1. API 모드 통일
**권장 방안**: 기존 웹도 Flask API를 기본으로 사용하도록 변경

```javascript
// js/config.js
const CONFIG = {
    // API 모드: 'flask' (Flask 백엔드, 기본값) 또는 'supabase' (Supabase 직접 연결)
    API_MODE: 'flask',  // 'supabase'에서 'flask'로 변경
    
    // Flask 백엔드 URL (기본값)
    API_BASE_URL: (typeof window !== 'undefined' && window.__API_BASE_URL__)
        ? window.__API_BASE_URL__
        : (typeof window !== 'undefined' && window.location && window.location.origin
            ? window.location.origin + '/api'
            : 'http://localhost:5000/api'),
    ...
};
```

**이유**:
- Streamlit과 동일한 백엔드 사용으로 일관성 확보
- 배포 시 단일 API 서버만 관리하면 됨
- 데이터 일관성 보장

---

#### 2. Streamlit API 연결 확인 로직 개선

```python
# streamlit_utils/api_client.py
def check_api_connection():
    """GET /api/health 로 연결 확인. 실패 시 구체적인 에러 메시지 반환."""
    try:
        r = requests.get(_url('/api/health'), timeout=5)
        if r.status_code == 200:
            return True, None
        else:
            return False, f"API 서버 응답 오류: HTTP {r.status_code}"
    except requests.exceptions.Timeout:
        return False, "API 서버 연결 시간 초과 (5초). 서버가 실행 중인지 확인하세요."
    except requests.exceptions.ConnectionError:
        return False, f"API 서버에 연결할 수 없습니다. ({API_BASE}/api/health)"
    except Exception as e:
        return False, f"연결 확인 중 오류 발생: {str(e)}"
```

**사용 예시**:
```python
# app_streamlit.py
is_connected, error_msg = check_api_connection()
if is_connected:
    st.success(f'API 연결됨: {API_BASE_URL}')
else:
    st.error(f'API 연결 실패: {error_msg}')
    st.info('💡 해결 방법:\n1. Flask 서버 실행: `python run_api.py`\n2. 포트 확인: 기본값은 5000번 포트입니다.')
```

---

#### 3. 배포 환경별 설정 가이드 작성

**Streamlit Cloud 배포 시**:
1. Streamlit Secrets에 다음 추가:
   ```
   API_BASE_URL=https://your-api-server.com
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_key
   ```

2. `.streamlit/config.toml` 확인:
   ```toml
   [server]
   port = 8501
   enableCORS = false
   enableXsrfProtection = false
   ```

**기존 웹 배포 시**:
1. HTML에서 API URL 주입:
   ```html
   <script>
       window.__API_BASE_URL__ = 'https://your-api-server.com/api';
   </script>
   ```

2. 또는 빌드 시 `config.js`의 `API_BASE_URL` 치환

---

#### 4. CORS 설정 개선

```python
# api/app.py
ALLOWED_ORIGINS = os.getenv(
    'ALLOWED_ORIGINS',
    'http://localhost:5000,http://127.0.0.1:5000,http://localhost:8000,http://127.0.0.1:8000,http://localhost:8501,http://127.0.0.1:8501'
).split(',')

# 프로덕션 도메인 추가 (환경 변수로 설정)
PRODUCTION_ORIGINS = os.getenv('PRODUCTION_ORIGINS', '').split(',')
if PRODUCTION_ORIGINS and PRODUCTION_ORIGINS[0]:
    ALLOWED_ORIGINS.extend(PRODUCTION_ORIGINS)

CORS(app, resources={
    r"/api/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-API-Key", "If-Match"],
    }
})
```

---

### 중기 조치 (Medium Priority)

#### 5. 정적 파일 서빙 구조 개선

**권장 구조**:
- **로컬 개발**: Flask가 정적 파일 서빙 (현재 구조 유지)
- **프로덕션 배포**: 
  - Nginx 등 웹 서버가 정적 파일 직접 서빙
  - 또는 CDN 사용
  - Flask는 API만 서빙

**구현 방안**:
```python
# api/app.py
import os

# 프로덕션 환경에서는 정적 파일 라우트 비활성화
SERVE_STATIC_FILES = os.getenv('SERVE_STATIC_FILES', 'true').lower() == 'true'

if SERVE_STATIC_FILES:
    @app.route('/')
    def index():
        return send_from_directory(PROJECT_ROOT, 'site-management.html')
    # ... 기타 정적 파일 라우트
```

---

#### 6. 환경 변수 문서화 강화

`.env.example` 업데이트:
```env
# === API 설정 ===
# Streamlit이 Flask API를 호출할 때 사용하는 URL
# 로컬: http://localhost:5000
# 배포: https://your-api-server.com
API_BASE_URL=http://localhost:5000

# === CORS 설정 ===
# 허용할 오리진 목록 (쉼표 구분)
# 로컬: 기본값 사용
# 배포: 프로덕션 도메인 추가 (예: https://your-app.streamlit.app,https://your-web-domain.com)
ALLOWED_ORIGINS=http://localhost:5000,http://localhost:8501
PRODUCTION_ORIGINS=

# === 정적 파일 서빙 ===
# Flask가 정적 파일을 서빙할지 여부 (로컬: true, 프로덕션: false)
SERVE_STATIC_FILES=true
```

---

### 장기 조치 (Low Priority)

#### 7. API 모드 선택 UI 추가

Streamlit에서 API 모드를 선택할 수 있는 UI 추가:
```python
# app_streamlit.py
api_mode = st.sidebar.selectbox(
    'API 모드',
    ['Flask API', 'Supabase 직접 연결'],
    index=0
)
```

---

#### 8. 헬스 체크 개선

- 주기적 자동 재연결 시도
- 서버 상태 시각화 (온라인/오프라인 표시)
- 연결 상태 히스토리 표시

---

## 📝 권장 조치 사항

### 즉시 조치 (High Priority)

1. ✅ **API 모드 통일**: `js/config.js`의 `API_MODE`를 `'flask'`로 변경
2. ✅ **Streamlit API 연결 확인 로직 개선**: 구체적인 에러 메시지 제공
3. ✅ **배포 가이드 작성**: Streamlit Cloud 및 기존 웹 배포 시 환경 변수 설정 방법 문서화
4. ✅ **CORS 설정 개선**: 프로덕션 도메인 지원 강화

---

### 중기 조치 (Medium Priority)

1. **정적 파일 서빙 구조 개선**: 프로덕션 환경 대응
2. **환경 변수 문서화 강화**: `.env.example` 및 배포 가이드 업데이트
3. **에러 처리 개선**: 사용자 친화적인 에러 메시지 및 재시도 기능

---

### 장기 조치 (Low Priority)

1. **API 모드 선택 UI**: Streamlit에서 런타임 선택 가능
2. **헬스 체크 고도화**: 자동 재연결 및 상태 모니터링
3. **중복 파일 정리**: `app_streamlit.py`와 `streamlit_app.py` 통일

---

## 📊 영향도 분석

| 문제 | 심각도 | 영향 범위 | 우선순위 |
|------|--------|----------|---------|
| API 모드 설정 불일치 | 🔴 Critical | 전체 시스템, 데이터 일관성 | P0 |
| 배포 환경별 API URL 설정 부재 | 🔴 Critical | 배포 실패 가능 | P0 |
| Streamlit API 연결 확인 로직 문제 | 🟡 Medium | 사용자 경험 | P1 |
| CORS 설정의 배포 환경 대응 부족 | 🟡 Medium | 배포 시 CORS 오류 | P1 |
| 정적 파일 서빙 구조 문제 | 🟡 Medium | 프로덕션 성능 | P2 |
| 에러 처리 부족 | 🟢 Low | 사용자 경험 | P3 |

---

## 📌 결론

**주요 발견 사항**:
1. 🔴 **Critical**: Streamlit과 기존 웹이 서로 다른 API 모드 사용 (Supabase vs Flask)
2. 🔴 **Critical**: 배포 환경별 설정 방법이 문서화되지 않음
3. 🟡 **Medium**: API 연결 확인 로직의 에러 메시지가 불명확함
4. 🟡 **Medium**: CORS 설정이 프로덕션 환경을 고려하지 않음

**권장 사항**:
- **즉시**: API 모드를 Flask로 통일하고, 배포 가이드를 작성
- **중기**: 정적 파일 서빙 구조 개선 및 환경 변수 문서화 강화
- **장기**: API 모드 선택 UI 및 헬스 체크 고도화

**다음 단계**: 위 개선 사항을 순차적으로 적용하여 배포 안정성을 확보해야 합니다.

---

## 📎 참고 문서

- `streamlit_utils/api_client.py` - Streamlit API 클라이언트
- `js/config.js` - 프론트엔드 API 설정
- `api/app.py` - Flask API 서버
- `docs/DB_Logic_Frontend_연결_점검_보고서.md` - DB 스키마 관련 점검 보고서
- `Streamlit_운영_가이드.md` - Streamlit 운영 가이드