"""
캐싱된 API 클라이언트 래퍼
Streamlit @st.cache_data를 사용하여 API 호출 최적화
"""
import streamlit as st
from streamlit_utils.api_client import (
    get_sites as _get_sites,
    get_personnel as _get_personnel,
    get_certificates as _get_certificates,
    get_stats as _get_stats,
    get_site as _get_site,
    search_sites as _search_sites,
    check_api_connection as _check_api_connection,
)


# ========== 캐싱 설정 ==========
# TTL (Time To Live): 캐시 유효 시간 (초)
CACHE_TTL_SHORT = 30  # 30초 - 자주 변경되는 데이터 (통계)
CACHE_TTL_MEDIUM = 60  # 1분 - 중간 빈도 (현장 목록, 인력 목록)
CACHE_TTL_LONG = 300  # 5분 - 거의 변경되지 않는 데이터 (자격증 목록)


# ========== 통계 (짧은 캐시) ==========
@st.cache_data(ttl=CACHE_TTL_SHORT, show_spinner="통계 로딩 중...")
def get_stats_cached():
    """통계 조회 (30초 캐시)
    
    Returns:
        tuple: (data, error)
    """
    return _get_stats()


# ========== 현장 목록 (중간 캐시) ==========
@st.cache_data(ttl=CACHE_TTL_MEDIUM, show_spinner="현장 목록 로딩 중...")
def get_sites_cached(company=None, status=None, state=None, limit=None, offset=None):
    """현장 목록 조회 (1분 캐시)
    
    Args:
        company: 회사구분 필터
        status: 배정상태 필터
        state: 현장상태 필터
        limit: 최대 개수
        offset: 시작 위치
        
    Returns:
        tuple: (data, error)
    """
    return _get_sites(company, status, state, limit, offset)


@st.cache_data(ttl=CACHE_TTL_MEDIUM, show_spinner="현장 검색 중...")
def search_sites_cached(q):
    """현장 검색 (1분 캐시)
    
    Args:
        q: 검색어
        
    Returns:
        tuple: (data, error)
    """
    return _search_sites(q)


@st.cache_data(ttl=CACHE_TTL_MEDIUM, show_spinner="현장 상세 로딩 중...")
def get_site_cached(site_id):
    """현장 상세 조회 (1분 캐시)
    
    Args:
        site_id: 현장 ID
        
    Returns:
        tuple: (data, error)
    """
    return _get_site(site_id)


# ========== 인력 목록 (중간 캐시) ==========
@st.cache_data(ttl=CACHE_TTL_MEDIUM, show_spinner="인력 목록 로딩 중...")
def get_personnel_cached(status=None, role=None):
    """인력 목록 조회 (1분 캐시)
    
    Args:
        status: 현재상태 필터
        role: 직책 필터
        
    Returns:
        tuple: (data, error)
    """
    return _get_personnel(status, role)


# ========== 자격증 목록 (긴 캐시) ==========
@st.cache_data(ttl=CACHE_TTL_LONG, show_spinner="자격증 목록 로딩 중...")
def get_certificates_cached(available=None):
    """자격증 목록 조회 (5분 캐시)
    
    Args:
        available: 사용가능여부 필터
        
    Returns:
        tuple: (data, error)
    """
    return _get_certificates(available)


# ========== API 연결 확인 (캐시 없음) ==========
def check_api_connection_cached():
    """API 연결 확인 (캐시 없음)
    
    Returns:
        tuple: (is_connected, error_message)
    """
    return _check_api_connection()


# ========== 캐시 관리 함수 ==========
def clear_all_caches():
    """모든 캐시 초기화"""
    st.cache_data.clear()


def clear_stats_cache():
    """통계 캐시만 초기화"""
    get_stats_cached.clear()


def clear_sites_cache():
    """현장 관련 캐시 초기화"""
    get_sites_cached.clear()
    search_sites_cached.clear()
    get_site_cached.clear()


def clear_personnel_cache():
    """인력 캐시 초기화"""
    get_personnel_cached.clear()


def clear_certificates_cache():
    """자격증 캐시 초기화"""
    get_certificates_cached.clear()


# ========== 캐시 상태 표시 ==========
def render_cache_info():
    """캐시 정보 표시 (디버깅용)"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔄 캐시 관리")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("전체 초기화", use_container_width=True, key="clear_all"):
            clear_all_caches()
            st.rerun()
    
    with col2:
        if st.button("통계만", use_container_width=True, key="clear_stats"):
            clear_stats_cache()
            st.rerun()
    
    st.sidebar.caption(f"""
    **캐시 TTL:**
    - 통계: {CACHE_TTL_SHORT}초
    - 현장/인력: {CACHE_TTL_MEDIUM}초
    - 자격증: {CACHE_TTL_LONG}초
    """)


# ========== 사용 가이드 ==========
"""
# 캐싱된 API 사용법

## 기본 사용
```python
from streamlit_utils.cached_api import get_sites_cached, get_personnel_cached

# 캐싱된 API 호출
sites_data, sites_err = get_sites_cached()
personnel_data, personnel_err = get_personnel_cached(status='투입가능')
```

## 캐시 초기화
```python
from streamlit_utils.cached_api import clear_sites_cache, clear_all_caches

# 특정 캐시만 초기화
clear_sites_cache()

# 모든 캐시 초기화
clear_all_caches()
```

## 캐시 TTL 설정
- `CACHE_TTL_SHORT = 30`: 통계 (30초)
- `CACHE_TTL_MEDIUM = 60`: 현장/인력 (1분)
- `CACHE_TTL_LONG = 300`: 자격증 (5분)

## 주의사항
1. 데이터 수정 후에는 해당 캐시를 초기화해야 함
2. 배정/해제 후에는 `clear_sites_cache()` 호출 권장
3. 실시간 데이터가 필요한 경우 캐시 없는 원본 함수 사용
"""
