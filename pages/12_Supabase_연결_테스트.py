"""
Supabase 연결 및 데이터 테스트 페이지
CSV/DB 연동 상태 확인
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from datetime import datetime
from streamlit_utils.theme import apply_localhost_theme

apply_localhost_theme()

st.title("🔌 Supabase 연결 테스트")
st.markdown("**데이터베이스 연결 상태 및 데이터 동기화 확인**")

# ========== 환경 변수 확인 ==========
st.markdown("---")
st.markdown("### 1️⃣ 환경 변수 확인")

api_mode = os.getenv('API_MODE', '').strip().lower() or 'flask'
supabase_url = os.getenv('SUPABASE_URL', '').strip()
supabase_anon_key = os.getenv('SUPABASE_ANON_KEY', '').strip()
api_base_url = os.getenv('API_BASE_URL', '').strip()

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 설정 상태")
    st.markdown(f"""
    <div class="info-card">
        <div class="info-row">
            <span class="info-label">API 모드</span>
            <span class="info-value">{api_mode or '미설정'}</span>
        </div>
        <div class="info-row">
            <span class="info-label">Supabase URL</span>
            <span class="info-value">{'✅ 설정됨' if supabase_url else '❌ 미설정'}</span>
        </div>
        <div class="info-row">
            <span class="info-label">Supabase Key</span>
            <span class="info-value">{'✅ 설정됨' if supabase_anon_key else '❌ 미설정'}</span>
        </div>
        <div class="info-row">
            <span class="info-label">API Base URL</span>
            <span class="info-value">{api_base_url or '미설정'}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("#### 권장 설정")
    st.code("""
# .env 파일 또는 환경 변수

# Supabase 직접 연결 모드
API_MODE=supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# 또는 Flask API 모드
API_MODE=flask
API_BASE_URL=http://localhost:5000
    """, language="bash")

# ========== API 연결 테스트 ==========
st.markdown("---")
st.markdown("### 2️⃣ API 연결 테스트")

from streamlit_utils.api_client import check_api_connection

is_connected, error_msg = check_api_connection()

if is_connected:
    st.success(f"✅ API 연결 성공 (모드: {api_mode})")
else:
    st.error(f"❌ API 연결 실패: {error_msg}")
    st.info("""
    **해결 방법:**
    - **Flask 모드**: `python run_api.py`로 Flask 서버 실행
    - **Supabase 모드**: `.env` 파일에 Supabase 설정 추가
    """)

# ========== 데이터 조회 테스트 ==========
st.markdown("---")
st.markdown("### 3️⃣ 데이터 조회 테스트")

if st.button("🔄 데이터 조회 시작", use_container_width=True):
    from streamlit_utils.api_client import get_sites, get_personnel, get_certificates, get_stats
    
    with st.spinner("데이터 로딩 중..."):
        # 통계
        stats_data, stats_err = get_stats()
        
        # 현장
        sites_data, sites_err = get_sites()
        
        # 인력
        personnel_data, personnel_err = get_personnel()
        
        # 자격증
        certificates_data, certificates_err = get_certificates()
    
    # 결과 표시
    tab1, tab2, tab3, tab4 = st.tabs(["통계", "현장", "인력", "자격증"])
    
    with tab1:
        st.markdown("#### 📊 통계 데이터")
        if stats_data:
            st.success("✅ 통계 조회 성공")
            
            # 통계 표시
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("전체 현장", stats_data.get('sites', {}).get('total', 0))
                st.metric("배정완료", stats_data.get('sites', {}).get('assigned', 0))
                st.metric("미배정", stats_data.get('sites', {}).get('unassigned', 0))
            
            with col2:
                st.metric("전체 인력", stats_data.get('personnel', {}).get('total', 0))
                st.metric("투입가능", stats_data.get('personnel', {}).get('available', 0))
                st.metric("투입중", stats_data.get('personnel', {}).get('deployed', 0))
            
            with col3:
                st.metric("전체 자격증", stats_data.get('certificates', {}).get('total', 0))
                st.metric("사용가능", stats_data.get('certificates', {}).get('available', 0))
                st.metric("사용중", stats_data.get('certificates', {}).get('in_use', 0))
            
            with st.expander("전체 통계 데이터 (JSON)"):
                st.json(stats_data)
        else:
            st.error(f"❌ 통계 조회 실패: {stats_err}")
    
    with tab2:
        st.markdown("#### 🏗️ 현장 데이터")
        if sites_data:
            st.success(f"✅ 현장 {len(sites_data)}건 조회 성공")
            
            if len(sites_data) > 0:
                st.dataframe(
                    sites_data[:10],  # 처음 10개만 표시
                    use_container_width=True,
                    hide_index=True
                )
                st.caption(f"총 {len(sites_data)}건 중 10건 표시")
            else:
                st.info("현장 데이터가 없습니다.")
        else:
            st.error(f"❌ 현장 조회 실패: {sites_err}")
    
    with tab3:
        st.markdown("#### 👷 인력 데이터")
        if personnel_data:
            st.success(f"✅ 인력 {len(personnel_data)}건 조회 성공")
            
            if len(personnel_data) > 0:
                st.dataframe(
                    personnel_data[:10],
                    use_container_width=True,
                    hide_index=True
                )
                st.caption(f"총 {len(personnel_data)}건 중 10건 표시")
            else:
                st.info("인력 데이터가 없습니다.")
        else:
            st.error(f"❌ 인력 조회 실패: {personnel_err}")
    
    with tab4:
        st.markdown("#### 📜 자격증 데이터")
        if certificates_data:
            st.success(f"✅ 자격증 {len(certificates_data)}건 조회 성공")
            
            if len(certificates_data) > 0:
                st.dataframe(
                    certificates_data[:10],
                    use_container_width=True,
                    hide_index=True
                )
                st.caption(f"총 {len(certificates_data)}건 중 10건 표시")
            else:
                st.info("자격증 데이터가 없습니다.")
        else:
            st.error(f"❌ 자격증 조회 실패: {certificates_err}")

# ========== Supabase 직접 연결 테스트 ==========
if api_mode == 'supabase' and supabase_url and supabase_anon_key:
    st.markdown("---")
    st.markdown("### 4️⃣ Supabase 직접 연결 테스트")
    
    if st.button("🔌 Supabase 연결 테스트", use_container_width=True):
        try:
            from api.services.supabase_service import supabase_service
            
            st.success("✅ Supabase 서비스 임포트 성공")
            
            # 테이블 존재 확인
            with st.spinner("테이블 확인 중..."):
                try:
                    sites = supabase_service.get_all_sites()
                    st.success(f"✅ Sites 테이블 연결 성공 ({len(sites)}건)")
                except Exception as e:
                    st.error(f"❌ Sites 테이블 오류: {str(e)}")
                
                try:
                    personnel = supabase_service.get_all_personnel()
                    st.success(f"✅ Personnel 테이블 연결 성공 ({len(personnel)}건)")
                except Exception as e:
                    st.error(f"❌ Personnel 테이블 오류: {str(e)}")
                
                try:
                    certificates = supabase_service.get_all_certificates()
                    st.success(f"✅ Certificates 테이블 연결 성공 ({len(certificates)}건)")
                except Exception as e:
                    st.error(f"❌ Certificates 테이블 오류: {str(e)}")
        
        except ImportError as e:
            st.error(f"❌ Supabase 서비스 임포트 실패: {str(e)}")
            st.info("api/services/supabase_service.py 파일을 확인하세요.")

# ========== CSV 파일 확인 ==========
st.markdown("---")
st.markdown("### 5️⃣ CSV 파일 확인")

csv_files = {
    "현장정보": "data/현장정보.csv",
    "인력풀": "data/인력풀.csv",
    "자격증풀": "data/자격증풀.csv",
}

csv_status = {}
for name, path in csv_files.items():
    full_path = os.path.join(os.path.dirname(__file__), '..', path)
    exists = os.path.exists(full_path)
    csv_status[name] = {
        "exists": exists,
        "path": path,
        "size": os.path.getsize(full_path) if exists else 0
    }

col1, col2, col3 = st.columns(3)

for idx, (name, status) in enumerate(csv_status.items()):
    with [col1, col2, col3][idx]:
        if status["exists"]:
            st.success(f"✅ {name}")
            st.caption(f"{status['size']:,} bytes")
        else:
            st.error(f"❌ {name}")
            st.caption("파일 없음")

# ========== 진단 요약 ==========
st.markdown("---")
st.markdown("### 📋 진단 요약")

# 점수 계산
score = 0
max_score = 0

# API 연결 (30점)
max_score += 30
if is_connected:
    score += 30
    api_status = "✅ 정상"
else:
    api_status = "❌ 실패"

# 환경 변수 (20점)
max_score += 20
if api_mode and (supabase_url or api_base_url):
    score += 20
    env_status = "✅ 설정됨"
else:
    env_status = "⚠️ 불완전"

# CSV 파일 (30점)
max_score += 30
csv_count = sum(1 for s in csv_status.values() if s["exists"])
score += (csv_count / len(csv_status)) * 30
csv_status_text = f"✅ {csv_count}/{len(csv_status)} 파일" if csv_count == len(csv_status) else f"⚠️ {csv_count}/{len(csv_status)} 파일"

# 데이터 조회 (20점) - 버튼 클릭 시에만 평가
max_score += 20
data_status = "⏸️ 미테스트"

# 요약 표시
st.markdown(f"""
<div class="info-card">
    <h4 style="margin-top: 0;">종합 점수: {score}/{max_score}점</h4>
    <div class="info-row">
        <span class="info-label">API 연결</span>
        <span class="info-value">{api_status}</span>
    </div>
    <div class="info-row">
        <span class="info-label">환경 변수</span>
        <span class="info-value">{env_status}</span>
    </div>
    <div class="info-row">
        <span class="info-label">CSV 파일</span>
        <span class="info-value">{csv_status_text}</span>
    </div>
    <div class="info-row">
        <span class="info-label">데이터 조회</span>
        <span class="info-value">{data_status}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 권장 사항
if score < max_score:
    st.markdown("---")
    st.markdown("### 💡 권장 사항")
    
    if not is_connected:
        st.warning("""
        **API 연결 실패**
        - Flask 모드: `python run_api.py` 실행
        - Supabase 모드: 환경 변수 설정 확인
        """)
    
    if not (supabase_url and supabase_anon_key) and api_mode == 'supabase':
        st.warning("""
        **Supabase 설정 미완료**
        - `.env` 파일에 `SUPABASE_URL`, `SUPABASE_ANON_KEY` 추가
        - Streamlit Cloud: Secrets에 환경 변수 추가
        """)
    
    if csv_count < len(csv_status):
        st.warning(f"""
        **CSV 파일 누락**
        - {len(csv_status) - csv_count}개 파일이 없습니다
        - `data/` 디렉토리에 CSV 파일 추가 필요
        """)

# ========== 다음 단계 ==========
st.markdown("---")
st.markdown("### 🚀 다음 단계")

if score >= max_score * 0.8:
    st.success("""
    ✅ **시스템 정상 작동 중**
    - 모든 기능을 사용할 수 있습니다
    - 기존 페이지에 캐싱 및 내보내기 통합 진행 가능
    """)
else:
    st.info("""
    ⚠️ **설정 완료 필요**
    - 위의 권장 사항을 따라 설정을 완료하세요
    - 설정 완료 후 이 페이지를 새로고침하세요
    """)
