# Supabase Publishable Key vs Secret Key 차이점 가이드

## 📋 개요

Supabase는 두 가지 유형의 API 키를 제공합니다:
1. **Publishable Key (퍼블리셔블 키)** - 클라이언트 측(프론트엔드)에서 사용
2. **Secret Key (시크릿 키)** - 서버 측(백엔드)에서만 사용

---

## 🔑 두 키의 차이점

### 1. Publishable Key (퍼블리셔블 키)

**형식**: `sb_publishable_...` 또는 JWT 형식 (`eyJhbGci...`)

**특징**:
- ✅ **브라우저에서 안전하게 사용 가능**
- ✅ **공개적으로 공유 가능** (RLS 정책이 설정되어 있다면)
- ✅ **프론트엔드(JavaScript)에서 사용**
- ⚠️ **RLS(Row Level Security) 정책의 제약을 받음**
- ⚠️ **제한된 권한** - 사용자가 접근할 수 있는 데이터만 조회/수정 가능

**사용 위치**:
- 브라우저 JavaScript 코드
- React, Vue 등 프론트엔드 프레임워크
- 모바일 앱 클라이언트
- `js/supabaseClient.js`, `js/config.js` 등

**보안**:
- RLS 정책이 올바르게 설정되어 있으면 브라우저에 노출되어도 안전
- 공개적으로 공유 가능 (예: GitHub에 커밋 가능)

---

### 2. Secret Key (시크릿 키)

**형식**: `sb_secret_...`

**특징**:
- ❌ **절대 브라우저에 노출되면 안 됨**
- ❌ **공개적으로 공유 금지**
- ✅ **서버 측에서만 사용**
- ✅ **RLS 정책을 우회** - 모든 데이터에 대한 완전한 접근 권한
- ✅ **관리자 권한** - 데이터베이스의 모든 작업 수행 가능

**사용 위치**:
- Flask API 서버 (`api/services/supabase_service.py`)
- Python 백엔드 스크립트
- 서버 사이드 함수
- `.env` 파일 (Git에 커밋하지 않음)

**보안**:
- **절대 공개하지 마세요!**
- `.gitignore`에 `.env` 파일이 포함되어 있는지 확인
- GitHub, 공개 저장소에 절대 커밋하지 않음
- 노출 시 즉시 키 재생성 필요

---

## 📝 프로젝트에서의 사용

### 현재 설정

#### 1. Publishable Key (Anon Key)
- **위치**: `.env` → `SUPABASE_ANON_KEY`
- **값**: JWT 형식의 anon key
- **사용처**:
  - `js/supabaseClient.js` - 브라우저 클라이언트
  - `js/config.js` - 프론트엔드 설정
  - `streamlit_secrets.toml` - Streamlit Cloud 배포용

#### 2. Secret Key (Service Role Key)
- **위치**: `.env` → `SUPABASE_KEY`
- **값**: `sb_secret_...` (실제 키는 Supabase 대시보드에서 확인)
- **사용처**:
  - `api/services/supabase_service.py` - 백엔드 서비스
  - Flask API 서버 (`run_api.py`)
  - Streamlit 백엔드 작업

---

## 🔒 보안 체크리스트

### ✅ 올바른 사용

- [x] Publishable Key는 브라우저에서 사용
- [x] Secret Key는 서버에서만 사용
- [x] `.env` 파일이 `.gitignore`에 포함됨
- [x] `streamlit_secrets.toml`은 Streamlit Cloud Secrets에만 업로드

### ❌ 절대 하지 말아야 할 것

- [ ] Secret Key를 브라우저 코드에 포함
- [ ] Secret Key를 GitHub에 커밋
- [ ] Secret Key를 공개 문서에 게시
- [ ] Publishable Key를 서버에서 사용 (RLS 제약 때문에)

---

## 🛠️ 키 확인 방법

### Supabase 대시보드에서 확인

1. [Supabase Dashboard](https://supabase.com/dashboard) 접속
2. 프로젝트 선택
3. **Project Settings** → **API** 메뉴
4. 다음 키들을 확인:
   - **Publishable key**: `sb_publishable_...` 또는 JWT 형식
   - **Secret keys** → **service_role**: `sb_secret_...`

---

## 📚 참고 자료

- [Supabase 공식 문서 - API Keys](https://supabase.com/docs/guides/api/api-keys)
- [Supabase RLS 가이드](https://supabase.com/docs/guides/auth/row-level-security)
- 프로젝트 내 문서:
  - `Supabase_연동_가이드.md`
  - `Supabase_클라이언트_사용법.md`

---

## 💡 요약

| 항목 | Publishable Key | Secret Key |
|------|----------------|------------|
| **사용 위치** | 프론트엔드 (브라우저) | 백엔드 (서버) |
| **공개 가능** | ✅ 예 (RLS 설정 시) | ❌ 절대 안 됨 |
| **권한** | 제한적 (RLS 적용) | 완전한 권한 |
| **보안** | RLS로 보호 | 환경 변수로 보호 |
| **프로젝트 변수명** | `SUPABASE_ANON_KEY` | `SUPABASE_KEY` |

**핵심 원칙**: 
- **Publishable Key** = 클라이언트에서 사용, 공개 가능
- **Secret Key** = 서버에서만 사용, 절대 공개 금지
