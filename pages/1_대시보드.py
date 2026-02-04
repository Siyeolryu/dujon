"""
대시보드 - 통계 요약 및 시각화
로컬호스트의 HTML/JS 대시보드를 Streamlit에 직접 통합
"""
import streamlit as st
from streamlit_utils.html_renderer import render_html_app
from streamlit_utils.api_client import check_api_connection
from streamlit_utils.theme import apply_localhost_theme

apply_localhost_theme()
st.title('📊 대시보드')

# API 연결 상태 확인 (오류 시에도 UI 표시)
is_connected, error_msg = check_api_connection()
if not is_connected:
    st.warning(f'⚠️ API 연결 실패: {error_msg} (로컬 개발 시 Flask 서버 실행 필요)')

# 로컬호스트의 전체 HTML/JS 앱을 렌더링
# 대시보드는 site-management.html 내부에 포함되어 있음
try:
    render_html_app('site-management.html', height=900, key='dashboard_app')
except Exception as e:
    import traceback
    st.error(f'대시보드 렌더링 오류: {str(e)}')
    with st.expander("상세 오류 정보"):
        st.code(traceback.format_exc())
    st.info('💡 로컬 개발 시 Flask 서버를 실행하면 전체 기능을 사용할 수 있습니다.')

# 주의: 아래 코드는 실행되지 않습니다. 
# 로컬호스트의 HTML/JS UI가 위에서 렌더링되며, 
# 모든 기능(대시보드, 차트, 통계 등)은 HTML/JS에서 처리됩니다.
