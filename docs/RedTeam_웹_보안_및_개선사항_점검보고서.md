# Red Team 웹 보안 및 개선사항 점검 보고서

**작성일**: 2026년 2월 4일  
**점검자**: Red Team (보안/UX/성능 전문가)  
**점검 범위**: 웹 애플리케이션 보안, UX/UI, 성능, 접근성, 코드 품질

---

## 📋 실행 요약

로컬호스트 테스트 후 Red Team 관점에서 웹 애플리케이션을 점검한 결과, **Critical 보안 취약점**과 **중요한 UX/성능 개선 사항**을 다수 발견했습니다. 특히 API 키 하드코딩, XSS 취약점 가능성, CSRF 보호 부재, 보안 헤더 미설정 등이 발견되었습니다.

---

## 🔴 Critical 보안 취약점

### 1. **API 키 하드코딩 (Critical - CWE-798)**

#### 문제 상황
```javascript
// js/config.js
SUPABASE_URL: 'https://hhpofxpnztzibtpkpiar.supabase.co',
SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',  // 하드코딩됨
KAKAO_APP_KEY: '797d955e0a50c6f827d5bfe3ab6ee26e',  // 하드코딩됨
```

**위험도**: 🔴 **Critical**  
**영향**: 
- 소스 코드에 API 키가 노출되어 버전 관리 시스템에 커밋될 수 있음
- 악의적인 사용자가 API 키를 악용하여 비용 발생 또는 서비스 남용 가능
- Supabase anon key는 RLS로 보호되지만, Kakao Maps API 키는 도메인 제한 없이 사용 시 남용 가능

**권장 조치**:
```javascript
// js/config.js - 개선안
const CONFIG = {
    // 환경 변수 또는 빌드 시 주입
    SUPABASE_URL: window.__SUPABASE_URL__ || 'https://hhpofxpnztzibtpkpiar.supabase.co',
    SUPABASE_ANON_KEY: window.__SUPABASE_ANON_KEY__ || '',
    KAKAO_APP_KEY: window.__KAKAO_APP_KEY__ || '',
    ...
};
```

```html
<!-- site-management.html - 배포 시 주입 -->
<script>
    // 서버에서 환경 변수로 주입 (빌드 시 또는 런타임)
    window.__SUPABASE_URL__ = '{{ SUPABASE_URL }}';
    window.__SUPABASE_ANON_KEY__ = '{{ SUPABASE_ANON_KEY }}';
    window.__KAKAO_APP_KEY__ = '{{ KAKAO_APP_KEY }}';
</script>
```

---

### 2. **XSS 취약점 가능성 (High - CWE-79)**

#### 문제 상황
```javascript
// js/ui.js
showModal(title, contentHTML) {
    bodyEl.innerHTML = contentHTML;  // ⚠️ 사용자 입력이 직접 삽입될 수 있음
}

// js/assign.js
preview.innerHTML = `
    <p><strong>${p['성명'] || '-'}</p>  // ⚠️ 데이터가 이스케이프되지 않음
    ...
`;
```

**위험도**: 🟠 **High**  
**영향**: 
- 악의적인 스크립트가 삽입되어 사용자 세션 탈취, 데이터 유출 가능
- 현재 `escapeHtml()` 함수가 있지만 모든 곳에서 사용되지 않음

**권장 조치**:
```javascript
// 모든 innerHTML 사용 시 escapeHtml() 적용
preview.innerHTML = `
    <p><strong>${escapeHtml(p['성명'] || '-')}</strong></p>
    <p>직책: ${escapeHtml(p['직책'] || '-')}</p>
    ...
`;

// 또는 DOMPurify 같은 라이브러리 사용
import DOMPurify from 'dompurify';
bodyEl.innerHTML = DOMPurify.sanitize(contentHTML);
```

---

### 3. **CSRF 보호 부재 (High - CWE-352)**

#### 문제 상황
- 모든 POST/PUT/DELETE 요청에 CSRF 토큰 검증 없음
- SameSite 쿠키 설정 없음
- API가 상태 변경 작업을 수행하지만 CSRF 보호 없음

**위험도**: 🟠 **High**  
**영향**: 
- 악의적인 사이트에서 사용자 모르게 배정 변경, 현장 삭제 등 가능
- 사용자가 악의적인 링크를 클릭하면 자동으로 악의적인 요청 실행

**권장 조치**:
```python
# api/app.py
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# 또는 Double Submit Cookie 패턴
@app.before_request
def csrf_protect():
    if request.method in ['POST', 'PUT', 'DELETE']:
        token = request.headers.get('X-CSRF-Token')
        if not token or token != session.get('csrf_token'):
            return jsonify({'error': 'CSRF token mismatch'}), 403
```

```javascript
// js/api.js
async request(endpoint, options = {}) {
    // CSRF 토큰 추가
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
    if (csrfToken && ['POST', 'PUT', 'DELETE'].includes(method)) {
        options.headers = {
            ...options.headers,
            'X-CSRF-Token': csrfToken
        };
    }
    ...
}
```

---

### 4. **보안 헤더 미설정 (Medium - CWE-693)**

#### 문제 상황
- `Content-Security-Policy` 헤더 없음
- `X-Frame-Options` 헤더 없음
- `X-Content-Type-Options` 헤더 없음
- `Strict-Transport-Security` 헤더 없음

**위험도**: 🟡 **Medium**  
**영향**: 
- Clickjacking 공격 가능
- MIME 타입 스니핑 공격 가능
- XSS 공격 완화 기회 상실

**권장 조치**:
```python
# api/app.py
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://dapi.kakao.com https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' https://*.supabase.co;"
    )
    return response
```

---

### 5. **디버깅 로그가 외부 서버로 전송 (Medium)**

#### 문제 상황
```javascript
// js/api.js
_logConnectionProblem(payload) {
    fetch('http://127.0.0.1:7242/ingest/2aca0e8f-d16b-480b-8f72-96be3c2a5d6c', {
        method: 'POST',
        body: JSON.stringify({
            url, method, status, errorCode, message, request_id  // 민감 정보 포함 가능
        }),
    })
}
```

**위험도**: 🟡 **Medium**  
**영향**: 
- 프로덕션 환경에서도 디버깅 로그가 전송될 수 있음
- 민감한 정보(URL, 에러 메시지 등)가 외부 서버로 전송됨
- 로컬호스트 주소가 하드코딩되어 프로덕션에서 동작하지 않음

**권장 조치**:
```javascript
_logConnectionProblem(payload) {
    // 개발 환경에서만 로깅
    if (process.env.NODE_ENV === 'development' || window.location.hostname === 'localhost') {
        // 로컬 로깅만 수행
        console.warn('[FE↔BE]', payload);
    }
    // 프로덕션에서는 외부 서버로 전송하지 않음
}
```

---

### 6. **인증/인가 부재 (Critical - CWE-306)**

#### 문제 상황
- 모든 API 엔드포인트가 인증 없이 접근 가능
- 사용자 식별 및 권한 검증 없음
- 누구나 현장 생성, 배정 변경, 삭제 가능

**위험도**: 🔴 **Critical**  
**영향**: 
- 무단 데이터 조작 가능
- 데이터 무결성 훼손
- 비즈니스 로직 우회

**권장 조치**:
```python
# api/app.py
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

jwt = JWTManager(app)

@app.before_request
def require_auth():
    # /api/health는 제외
    if request.path.startswith('/api/') and request.path != '/api/health':
        # JWT 토큰 검증
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not verify_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
```

```javascript
// js/api.js
async request(endpoint, options = {}) {
    const token = localStorage.getItem('auth_token');
    if (token) {
        options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        };
    }
    ...
}
```

---

## 🟡 Medium 보안/UX 문제점

### 7. **입력 검증 부족 (Medium)**

#### 문제 상황
- 클라이언트 측 입력 검증이 일부만 구현됨
- 서버 측 검증은 있지만, 클라이언트에서 사전 차단하지 않아 불필요한 요청 발생

**권장 조치**:
```javascript
// js/tabs.js 또는 폼 검증 모듈
function validateSiteForm(data) {
    const errors = [];
    if (!data['현장명']?.trim()) errors.push('현장명은 필수입니다');
    if (!data['주소']?.trim()) errors.push('주소는 필수입니다');
    if (data['회사구분'] && !['더존종합건설', '더존하우징'].includes(data['회사구분'])) {
        errors.push('회사구분이 올바르지 않습니다');
    }
    // 날짜 형식 검증
    const dateFields = ['건축허가일', '착공예정일', '준공일'];
    dateFields.forEach(field => {
        if (data[field] && !/^\d{4}-\d{2}-\d{2}$/.test(data[field])) {
            errors.push(`${field}는 YYYY-MM-DD 형식이어야 합니다`);
        }
    });
    return errors;
}
```

---

### 8. **에러 메시지 정보 노출 (Low)**

#### 문제 상황
- 에러 메시지에 내부 구조 정보가 포함될 수 있음
- 스택 트레이스가 노출될 수 있음

**권장 조치**:
```python
# api/app.py
@app.errorhandler(500)
def internal_error(error):
    # 프로덕션에서는 상세 에러 숨김
    if os.getenv('FLASK_DEBUG', 'False').lower() != 'true':
        return jsonify({
            'success': False,
            'error': {'code': 'INTERNAL_ERROR', 'message': '서버 내부 오류가 발생했습니다'}
        }), 500
    # 개발 환경에서만 상세 에러 표시
    ...
```

---

### 9. **Rate Limiting 부재 (Medium)**

#### 문제 상황
- API 요청 횟수 제한 없음
- DDoS 공격에 취약

**권장 조치**:
```python
# api/app.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@bp.route('/sites', methods=['POST'])
@limiter.limit("10 per minute")
def create_site():
    ...
```

---

## 🟢 UX/UI 개선 사항

### 10. **접근성 부족 (WCAG 2.1 미준수)**

#### 문제 상황
- 키보드 네비게이션 불완전
- ARIA 속성 부족
- 색상 대비 부족 가능성
- 스크린 리더 지원 부족

**권장 조치**:
```html
<!-- site-management.html -->
<button 
    type="button" 
    class="tab-btn" 
    role="tab" 
    aria-selected="false"
    aria-controls="tab-site-list"
    tabindex="0">
    현장 목록
</button>

<!-- 키보드 이벤트 처리 -->
<script>
element.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        element.click();
    }
});
</script>
```

```css
/* css/style.css */
/* 포커스 표시 개선 */
button:focus-visible,
input:focus-visible,
select:focus-visible {
    outline: 2px solid #0066cc;
    outline-offset: 2px;
}

/* 색상 대비 개선 (WCAG AA 준수) */
.text-muted {
    color: #6c757d; /* 대비율 4.5:1 이상 */
}
```

---

### 11. **로딩 상태 표시 개선**

#### 문제 상황
- 일부 비동기 작업에서 로딩 표시가 없음
- 진행률 표시 없음

**권장 조치**:
```javascript
// js/ui.js
showLoading(message = '로딩 중...', progress = null) {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.innerHTML = `
            <div class="spinner"></div>
            <p>${message}</p>
            ${progress !== null ? `<progress value="${progress}" max="100"></progress>` : ''}
        `;
        overlay.classList.remove('hidden');
    }
}
```

---

### 12. **에러 복구 메커니즘 부족**

#### 문제 상황
- 네트워크 오류 시 자동 재시도 없음
- 사용자가 수동으로 새로고침해야 함

**권장 조치**:
```javascript
// js/api.js
async request(endpoint, options = {}, retries = 3) {
    for (let i = 0; i < retries; i++) {
        try {
            const res = await fetch(url, options);
            // 성공 시 반환
            ...
        } catch (err) {
            if (i === retries - 1) throw err;
            // 지수 백오프 재시도
            await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
        }
    }
}
```

---

### 13. **오프라인 지원 부재**

#### 문제 상황
- 네트워크 연결이 끊어지면 완전히 사용 불가
- Service Worker 없음

**권장 조치**:
```javascript
// service-worker.js
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        }).catch(() => {
            // 오프라인 페이지 표시
            return caches.match('/offline.html');
        })
    );
});
```

---

## 🔵 성능 개선 사항

### 14. **불필요한 API 호출**

#### 문제 상황
- 동일한 데이터를 여러 번 요청할 수 있음
- 캐싱 전략 부재

**권장 조치**:
```javascript
// js/api.js
const cache = new Map();
const CACHE_TTL = 60000; // 1분

async getSites(filters = {}) {
    const cacheKey = JSON.stringify(filters);
    const cached = cache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
        return cached.data;
    }
    const result = await this.request(`/sites?...`);
    cache.set(cacheKey, { data: result, timestamp: Date.now() });
    return result;
}
```

---

### 15. **리소스 최적화 부족**

#### 문제 상황
- 이미지 최적화 없음
- CSS/JS 번들 최적화 없음
- CDN 미사용

**권장 조치**:
- 이미지: WebP 형식 사용, lazy loading
- CSS/JS: Minification, Tree shaking
- CDN: 정적 파일 CDN 배포

---

### 16. **메모리 누수 가능성**

#### 문제 상황
- 이벤트 리스너가 제거되지 않을 수 있음
- 타이머가 정리되지 않을 수 있음

**권장 조치**:
```javascript
// js/app.js
class App {
    constructor() {
        this.listeners = [];
        this.timers = [];
    }
    
    addEventListener(element, event, handler) {
        element.addEventListener(event, handler);
        this.listeners.push({ element, event, handler });
    }
    
    cleanup() {
        this.listeners.forEach(({ element, event, handler }) => {
            element.removeEventListener(event, handler);
        });
        this.timers.forEach(timer => clearTimeout(timer));
    }
}
```

---

## 📊 우선순위별 개선 로드맵

### 즉시 조치 (P0 - Critical)

1. ✅ **API 키 환경 변수화**: 하드코딩된 키를 환경 변수로 이동
2. ✅ **XSS 방지**: 모든 `innerHTML` 사용 시 `escapeHtml()` 또는 DOMPurify 적용
3. ✅ **CSRF 보호 구현**: CSRF 토큰 검증 추가
4. ✅ **보안 헤더 설정**: Content-Security-Policy 등 보안 헤더 추가
5. ✅ **인증/인가 구현**: JWT 기반 인증 시스템 도입

---

### 단기 조치 (P1 - High)

6. **입력 검증 강화**: 클라이언트/서버 양쪽 검증
7. **Rate Limiting**: API 요청 제한 구현
8. **에러 처리 개선**: 프로덕션 환경에서 상세 에러 숨김
9. **디버깅 로그 제거**: 프로덕션 환경에서 외부 로그 전송 비활성화

---

### 중기 조치 (P2 - Medium)

10. **접근성 개선**: WCAG 2.1 AA 준수
11. **로딩 상태 개선**: 진행률 표시 및 사용자 피드백 강화
12. **에러 복구 메커니즘**: 자동 재시도 및 오프라인 지원
13. **성능 최적화**: 캐싱, 리소스 최적화

---

### 장기 조치 (P3 - Low)

14. **모니터링 및 로깅**: 에러 추적 시스템 도입
15. **테스트 자동화**: 보안 테스트, 성능 테스트 자동화
16. **문서화**: 보안 가이드, API 문서화

---

## 📝 권장 조치 사항 요약

### 보안 (Critical)

| 항목 | 현재 상태 | 권장 조치 | 우선순위 |
|------|----------|----------|---------|
| API 키 하드코딩 | ❌ 하드코딩됨 | 환경 변수로 이동 | P0 |
| XSS 방지 | ⚠️ 부분적 | 모든 innerHTML 이스케이프 | P0 |
| CSRF 보호 | ❌ 없음 | CSRF 토큰 구현 | P0 |
| 보안 헤더 | ❌ 없음 | CSP, X-Frame-Options 등 설정 | P0 |
| 인증/인가 | ❌ 없음 | JWT 기반 인증 도입 | P0 |

### UX/UI

| 항목 | 현재 상태 | 권장 조치 | 우선순위 |
|------|----------|----------|---------|
| 접근성 | ⚠️ 부분적 | WCAG 2.1 AA 준수 | P2 |
| 로딩 상태 | ⚠️ 기본적 | 진행률 표시 추가 | P2 |
| 에러 복구 | ❌ 없음 | 자동 재시도 구현 | P2 |
| 오프라인 지원 | ❌ 없음 | Service Worker 도입 | P3 |

### 성능

| 항목 | 현재 상태 | 권장 조치 | 우선순위 |
|------|----------|----------|---------|
| API 캐싱 | ❌ 없음 | 클라이언트 캐싱 구현 | P2 |
| 리소스 최적화 | ⚠️ 기본적 | 번들링, 압축, CDN | P2 |
| 메모리 관리 | ⚠️ 수동 | 자동 정리 메커니즘 | P2 |

---

## 📌 결론

**주요 발견 사항**:
1. 🔴 **Critical**: API 키 하드코딩, 인증/인가 부재, CSRF 보호 없음
2. 🟠 **High**: XSS 취약점 가능성, 보안 헤더 미설정
3. 🟡 **Medium**: Rate Limiting 부재, 입력 검증 부족
4. 🟢 **Low**: 접근성, 성능 최적화 여지

**권장 사항**:
- **즉시**: 보안 취약점(Critical) 수정
- **단기**: 보안 강화 및 UX 개선
- **중기**: 성능 최적화 및 접근성 개선
- **장기**: 모니터링 및 자동화

**다음 단계**: 위 개선 사항을 우선순위에 따라 순차적으로 적용하여 보안성과 사용성을 향상시켜야 합니다.

---

## 📎 참고 문서

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- WCAG 2.1: https://www.w3.org/WAI/WCAG21/quickref/
- CWE (Common Weakness Enumeration): https://cwe.mitre.org/
- Flask Security Best Practices: https://flask.palletsprojects.com/en/2.3.x/security/