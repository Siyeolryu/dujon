"""
현장배정 관리 시스템 - Streamlit 앱
로컬호스트의 HTML/JS UI를 Streamlit에 직접 통합
UI/UX: 로컬호스트(site-management.html + style.css) 기준 적용.
"""
import os
import streamlit as st
from dotenv import load_dotenv
from streamlit_utils.html_renderer import render_html_app
from streamlit_utils.api_client import check_api_connection, _detect_environment
from streamlit_utils.theme import apply_localhost_theme, render_top_nav

load_dotenv()

# 주의: set_page_config는 메인 스크립트(app_streamlit.py)에서만 호출. 페이지에서는 호출 시 네비게이션 오류 발생.
apply_localhost_theme()
render_top_nav(current_page="9_streamlit_app")

# 환경 감지
env = _detect_environment()
is_deployed = env == 'streamlit_cloud'

# 로컬호스트의 HTML/JS UI를 Streamlit에 직접 통합
# API 연결 실패해도 UI는 먼저 표시
st.markdown('<div style="margin-bottom: 10px;"></div>', unsafe_allow_html=True)

try:
    # HTML 렌더링 시도 (항상 표시)
    render_result = render_html_app('site-management.html', height=900, key='main_app')
    
    if render_result is None:
        st.error('❌ HTML UI를 렌더링할 수 없습니다.')
    
except Exception as e:
    import traceback
    st.error(f'❌ HTML 렌더링 오류: {str(e)}')
    with st.expander("상세 오류 정보"):
        st.code(traceback.format_exc())
    
    st.info('''
    💡 **해결 방법:**
    1. `site-management.html` 파일이 프로젝트 루트에 있는지 확인
    2. 로컬 개발 시: Flask 서버 실행 (`python run_api.py`)
    3. 배포 환경: Streamlit Secrets에 `API_BASE_URL` 설정
    ''')

# API 연결 상태 확인 (HTML 렌더링 후)
api_mode = os.getenv('API_MODE', '').strip().lower() or 'flask'

if not is_deployed:
    # 로컬 개발 환경에서만 상세한 API 연결 체크
    is_connected, error_msg = check_api_connection()
    if not is_connected:
        st.error(f'❌ **API 연결 실패**: {error_msg}')
        st.info('''
        💡 **해결 방법:**
        1. **Flask 서버 실행**: 터미널에서 `python run_api.py` 실행
        2. **포트 확인**: 기본값은 5000번 포트입니다
        3. **환경 변수 확인**: `.env` 파일에 `API_BASE_URL=http://localhost:5000/api` 설정 확인
        4. **방화벽 확인**: 로컬호스트 연결이 차단되지 않았는지 확인
        
        ⚠️ **참고**: API 서버가 실행되지 않아도 UI는 표시되지만, 데이터를 불러올 수 없습니다.
        ''')
    else:
        st.success('✅ API 서버 연결 성공')
else:
    # 배포 환경 처리
    if api_mode == 'supabase':
        # Supabase 직접 연결 모드: API 연결 체크 불필요 (브라우저에서 직접 연결)
        supabase_url = os.getenv('SUPABASE_URL', '').strip()
        supabase_anon_key = os.getenv('SUPABASE_ANON_KEY', '').strip()
        if supabase_url and supabase_anon_key:
            st.success('✅ **Supabase 직접 연결 모드**: 브라우저에서 Supabase에 직접 연결합니다')
        else:
            st.warning('⚠️ **Supabase 설정 확인 필요**: `SUPABASE_URL`과 `SUPABASE_ANON_KEY`가 설정되어 있는지 확인하세요')
    else:
        # Flask API 모드: API 연결 체크 수행
        is_connected, error_msg = check_api_connection()
        if not is_connected:
            st.info('ℹ️ **참고**: API 서버 연결 확인 중... (배포 환경에서는 별도 API 서버가 필요할 수 있습니다)')
            st.caption(f'API URL: {os.getenv("API_BASE_URL", "/api")}')
        else:
            st.success('✅ API 서버 연결 성공')
