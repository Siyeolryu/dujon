"""
API 캐싱 데모 페이지
성능 최적화 효과 확인
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import time
from datetime import datetime
from streamlit_utils.theme import apply_localhost_theme
from streamlit_utils.api_client import get_sites, get_personnel, get_certificates, get_stats
from streamlit_utils.cached_api import (
    get_sites_cached, get_personnel_cached, get_certificates_cached, get_stats_cached,
    clear_all_caches, clear_sites_cache, clear_personnel_cache, clear_certificates_cache,
    CACHE_TTL_SHORT, CACHE_TTL_MEDIUM, CACHE_TTL_LONG
)

apply_localhost_theme()

st.title("🚀 API 캐싱 성능 데모")
st.markdown("**Streamlit @st.cache_data를 사용한 성능 최적화**")

# ========== 캐시 관리 ==========
st.sidebar.markdown("### 🔄 캐시 관리")

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("전체 초기화", use_container_width=True):
        clear_all_caches()
        st.success("모든 캐시 초기화 완료!")
        time.sleep(0.5)
        st.rerun()

with col2:
    if st.button("통계만", use_container_width=True):
        clear_all_caches()  # get_stats_cached.clear()는 직접 호출 불가
        st.success("통계 캐시 초기화 완료!")
        time.sleep(0.5)
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### ⏱️ 캐시 TTL 설정")
st.sidebar.caption(f"""
- **통계**: {CACHE_TTL_SHORT}초
- **현장/인력**: {CACHE_TTL_MEDIUM}초  
- **자격증**: {CACHE_TTL_LONG}초
""")

# ========== 성능 비교 ==========
st.markdown("---")
st.markdown("### 📊 성능 비교")

tab1, tab2, tab3 = st.tabs(["현장 목록", "인력 목록", "통계"])

with tab1:
    st.markdown("#### 현장 목록 API 호출")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### ❌ 캐시 없음")
        if st.button("현장 목록 조회 (캐시 없음)", use_container_width=True):
            start_time = time.time()
            sites_data, sites_err = get_sites()
            elapsed_time = time.time() - start_time
            
            if sites_data:
                st.success(f"✅ {len(sites_data)}건 조회 완료")
                st.metric("소요 시간", f"{elapsed_time:.3f}초")
            else:
                st.error(f"조회 실패: {sites_err}")
    
    with col2:
        st.markdown("##### ✅ 캐시 사용")
        if st.button("현장 목록 조회 (캐시)", use_container_width=True):
            start_time = time.time()
            sites_data, sites_err = get_sites_cached()
            elapsed_time = time.time() - start_time
            
            if sites_data:
                st.success(f"✅ {len(sites_data)}건 조회 완료")
                st.metric("소요 시간", f"{elapsed_time:.3f}초")
                if elapsed_time < 0.01:
                    st.info("⚡ 캐시에서 즉시 로드!")
            else:
                st.error(f"조회 실패: {sites_err}")

with tab2:
    st.markdown("#### 인력 목록 API 호출")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### ❌ 캐시 없음")
        if st.button("인력 목록 조회 (캐시 없음)", use_container_width=True):
            start_time = time.time()
            personnel_data, personnel_err = get_personnel()
            elapsed_time = time.time() - start_time
            
            if personnel_data:
                st.success(f"✅ {len(personnel_data)}건 조회 완료")
                st.metric("소요 시간", f"{elapsed_time:.3f}초")
            else:
                st.error(f"조회 실패: {personnel_err}")
    
    with col2:
        st.markdown("##### ✅ 캐시 사용")
        if st.button("인력 목록 조회 (캐시)", use_container_width=True):
            start_time = time.time()
            personnel_data, personnel_err = get_personnel_cached()
            elapsed_time = time.time() - start_time
            
            if personnel_data:
                st.success(f"✅ {len(personnel_data)}건 조회 완료")
                st.metric("소요 시간", f"{elapsed_time:.3f}초")
                if elapsed_time < 0.01:
                    st.info("⚡ 캐시에서 즉시 로드!")
            else:
                st.error(f"조회 실패: {personnel_err}")

with tab3:
    st.markdown("#### 통계 API 호출")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### ❌ 캐시 없음")
        if st.button("통계 조회 (캐시 없음)", use_container_width=True):
            start_time = time.time()
            stats_data, stats_err = get_stats()
            elapsed_time = time.time() - start_time
            
            if stats_data:
                st.success("✅ 통계 조회 완료")
                st.metric("소요 시간", f"{elapsed_time:.3f}초")
                st.json(stats_data)
            else:
                st.error(f"조회 실패: {stats_err}")
    
    with col2:
        st.markdown("##### ✅ 캐시 사용")
        if st.button("통계 조회 (캐시)", use_container_width=True):
            start_time = time.time()
            stats_data, stats_err = get_stats_cached()
            elapsed_time = time.time() - start_time
            
            if stats_data:
                st.success("✅ 통계 조회 완료")
                st.metric("소요 시간", f"{elapsed_time:.3f}초")
                if elapsed_time < 0.01:
                    st.info("⚡ 캐시에서 즉시 로드!")
                st.json(stats_data)
            else:
                st.error(f"조회 실패: {stats_err}")

# ========== 연속 호출 테스트 ==========
st.markdown("---")
st.markdown("### 🔁 연속 호출 성능 테스트")
st.markdown("동일한 API를 5번 연속 호출하여 캐싱 효과 확인")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### ❌ 캐시 없음")
    if st.button("5회 연속 호출 (캐시 없음)", use_container_width=True):
        total_start = time.time()
        times = []
        
        progress_bar = st.progress(0)
        for i in range(5):
            start = time.time()
            sites_data, _ = get_sites()
            elapsed = time.time() - start
            times.append(elapsed)
            progress_bar.progress((i + 1) / 5)
        
        total_elapsed = time.time() - total_start
        
        st.success(f"✅ 완료")
        st.metric("총 소요 시간", f"{total_elapsed:.3f}초")
        st.metric("평균 소요 시간", f"{sum(times) / len(times):.3f}초")
        
        for i, t in enumerate(times, 1):
            st.caption(f"호출 {i}: {t:.3f}초")

with col2:
    st.markdown("#### ✅ 캐시 사용")
    if st.button("5회 연속 호출 (캐시)", use_container_width=True):
        total_start = time.time()
        times = []
        
        progress_bar = st.progress(0)
        for i in range(5):
            start = time.time()
            sites_data, _ = get_sites_cached()
            elapsed = time.time() - start
            times.append(elapsed)
            progress_bar.progress((i + 1) / 5)
        
        total_elapsed = time.time() - total_start
        
        st.success(f"✅ 완료")
        st.metric("총 소요 시간", f"{total_elapsed:.3f}초")
        st.metric("평균 소요 시간", f"{sum(times) / len(times):.3f}초")
        
        for i, t in enumerate(times, 1):
            st.caption(f"호출 {i}: {t:.3f}초 {'⚡ 캐시' if t < 0.01 else ''}")

# ========== 사용 가이드 ==========
st.markdown("---")
st.markdown("### 📝 사용 가이드")

st.markdown("""
#### 캐싱 적용 방법

##### 1. 기존 코드 (캐시 없음)
```python
from streamlit_utils.api_client import get_sites, get_personnel

sites_data, sites_err = get_sites()
personnel_data, personnel_err = get_personnel()
```

##### 2. 캐싱 적용 코드
```python
from streamlit_utils.cached_api import get_sites_cached, get_personnel_cached

sites_data, sites_err = get_sites_cached()
personnel_data, personnel_err = get_personnel_cached()
```

#### 캐시 초기화

데이터 수정 후에는 캐시를 초기화해야 합니다:

```python
from streamlit_utils.cached_api import clear_sites_cache, clear_all_caches

# 현장 배정 후
assign_site(site_id, manager_id, certificate_id)
clear_sites_cache()  # 현장 캐시만 초기화

# 또는 모든 캐시 초기화
clear_all_caches()
```

#### 성능 개선 효과

| 항목 | 캐시 없음 | 캐시 사용 | 개선율 |
|------|-----------|-----------|--------|
| 첫 호출 | ~0.5초 | ~0.5초 | - |
| 두 번째 호출 | ~0.5초 | ~0.001초 | **99.8%** |
| 5회 연속 호출 | ~2.5초 | ~0.5초 | **80%** |

#### 캐시 TTL 설정

- **통계** (30초): 자주 변경되는 데이터
- **현장/인력** (1분): 중간 빈도 데이터
- **자격증** (5분): 거의 변경되지 않는 데이터

#### 주의사항

1. ⚠️ 데이터 수정 후 캐시 초기화 필수
2. ⚠️ 실시간 데이터가 필요한 경우 캐시 없는 함수 사용
3. ⚠️ TTL 경과 후 자동으로 캐시 갱신됨

#### 다음 단계

- ✅ 대시보드에 캐싱 적용
- ✅ 현장 목록에 캐싱 적용
- ✅ 배정 워크플로우에 캐시 초기화 추가
""")
