"""
현장배정 관리 시스템 - Streamlit 메인 진입점
GitHub/Streamlit Cloud에서 Main file path: streamlit_app.py
pages/ 폴더의 한글 페이지 파일들을 자동으로 사이드바에 표시합니다.
"""
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')
API_MODE = os.getenv('API_MODE', '').strip().lower() or 'flask'

# 페이지 설정 (반드시 첫 번째 Streamlit 명령어여야 함)
st.set_page_config(
    page_title='현장배정 관리 시스템',
    page_icon='🏗️',
    layout='wide',
    initial_sidebar_state='expanded',
)

# 테마 적용 (streamlit_utils가 있는 경우)
try:
    from streamlit_utils.theme import apply_localhost_theme
    apply_localhost_theme()
except ImportError:
    pass

# API / DB 연결 확인
is_connected = False
error_msg = ""
try:
    from streamlit_utils.api_client import check_api_connection
    is_connected, error_msg = check_api_connection()
except ImportError:
    error_msg = "streamlit_utils 모듈을 찾을 수 없습니다"

# 메인 페이지 내용
st.title('🏗️ 현장배정 관리 시스템')
st.caption('좌측 사이드바에서 페이지를 선택하거나, 아래 빠른 액션을 이용하세요.')

# 연결 상태 표시 (모드별 분기)
if is_connected:
    if API_MODE == 'supabase':
        st.success('✅ Supabase DB 연결됨')
    else:
        st.success(f'✅ API 연결됨: {API_BASE_URL}')
else:
    if API_MODE == 'supabase':
        st.warning(f'⚠️ Supabase 연결 확인 필요: {error_msg}')
        with st.expander('해결 방법'):
            st.markdown('''
            1. **`.env` 파일 확인**: `SUPABASE_URL`, `SUPABASE_ANON_KEY` (또는 `SUPABASE_KEY`) 설정
            2. **`API_MODE=supabase`** 가 설정되어 있는지 확인
            3. **네트워크 확인**: Supabase 프로젝트가 활성 상태인지 확인
            ''')
    else:
        st.error(f'❌ API 연결 실패: {error_msg}')
        with st.expander('해결 방법'):
            st.markdown('''
            1. **Flask 서버 실행**: 터미널에서 `python run_api.py` 실행
            2. **포트 확인**: 기본값은 5000번 포트입니다
            3. **환경 변수 확인**: `.env` 파일에 `API_BASE_URL`이 올바르게 설정되어 있는지 확인
            4. **방화벽 확인**: 로컬호스트 연결이 차단되지 않았는지 확인
            ''')

st.markdown('---')

# ========== 빠른 액션 (퀵 네비게이션) ==========
st.markdown('### 빠른 액션')

st.markdown("""
<div class="quick-actions">
    <a href="/대시보드" class="quick-action-btn">
        <span class="quick-action-icon">📊</span>
        <span class="quick-action-text">대시보드</span>
    </a>
    <a href="/현장_목록" class="quick-action-btn">
        <span class="quick-action-icon">📋</span>
        <span class="quick-action-text">현장 목록</span>
    </a>
    <a href="/현장등록" class="quick-action-btn">
        <span class="quick-action-icon">🏗️</span>
        <span class="quick-action-text">현장 등록</span>
    </a>
    <a href="/자격증등록" class="quick-action-btn">
        <span class="quick-action-icon">📜</span>
        <span class="quick-action-text">자격증 등록</span>
    </a>
    <a href="/투입가능인원_상세" class="quick-action-btn">
        <span class="quick-action-icon">👷</span>
        <span class="quick-action-text">인원 상세</span>
    </a>
</div>
""", unsafe_allow_html=True)

st.markdown('---')

# 페이지 안내
st.markdown('''
### 사용 가능한 페이지

| 페이지 | 설명 |
|--------|------|
| **📊 대시보드** | 통계 요약 (전체 현장, 미배정, 배정완료, 투입가능 인력), 차트 시각화 |
| **📋 현장 목록** | 필터·검색·테이블, 배정/해제 |
| **🏗️ 현장등록** | 새 현장 등록 (현장ID 자동 부여) |
| **📜 자격증등록** | 새 자격증 등록 (자격증ID·소유자ID 자동 부여) |
| **👷 투입가능인원 상세** | 투입 가능한 인원 상세 정보 및 자격증 현황 |

**좌측 사이드바**에서 페이지를 선택하세요.
''')

# 시스템 정보 (푸터)
st.markdown('---')
st.markdown(f"""
<div style="text-align: center; color: #6c757d; font-size: 12px; padding: 20px 0;">
    현장배정 관리 시스템 v2.0 | API 모드: {API_MODE.upper()} |
    <a href="https://github.com/Siyeolryu/dujon" target="_blank" style="color: #6c757d;">GitHub</a>
</div>
""", unsafe_allow_html=True)
