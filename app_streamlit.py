"""
현장배정 관리 시스템 - Streamlit 메인 진입점
기존 Flask API(API_BASE_URL)를 호출하여 운영합니다.
UI/UX: 로컬호스트(site-management.html + style.css) 기준 적용.
실행: streamlit run app_streamlit.py
"""
import os
import streamlit as st
from dotenv import load_dotenv
from streamlit_utils.api_client import check_api_connection
from streamlit_utils.theme import apply_localhost_theme

load_dotenv()
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')

st.set_page_config(
    page_title='현장배정 관리 시스템',
    page_icon='🏗️',
    layout='wide',
    initial_sidebar_state='expanded',
)
apply_localhost_theme()

st.title('🏗️ 현장배정 관리 시스템')
st.caption('Streamlit 웹 UI · 좌측 사이드바에서 페이지를 선택하세요.')

# API 연결 상태
is_connected, error_msg = check_api_connection()
if is_connected:
    st.success(f'✅ API 연결됨: {API_BASE_URL}')
else:
    st.error(f'❌ API 연결 실패: {error_msg}')
    with st.expander('💡 해결 방법'):
        st.markdown('''
        1. **Flask 서버 실행**: 터미널에서 `python run_api.py` 실행
        2. **포트 확인**: 기본값은 5000번 포트입니다
        3. **환경 변수 확인**: `.env` 파일에 `API_BASE_URL`이 올바르게 설정되어 있는지 확인
        4. **방화벽 확인**: 로컬호스트 연결이 차단되지 않았는지 확인
        ''')

st.markdown('---')
st.markdown('''
**사용 방법**
- **대시보드**: 통계 요약(전체 현장, 미배정, 배정완료, 투입가능 인력, 사용가능 자격증)
- **현장 목록**: 필터·검색·테이블, 배정/해제
- **현장등록**: 새 현장 등록 (현장ID 자동 부여)
- **자격증등록**: 새 자격증 등록 (자격증ID·소유자ID 자동 부여)
''')

# 기존 HTML 웹 UI 링크
st.markdown('---')
st.markdown('### 기존 웹 UI')
st.markdown(f'HTML/JS 기반 화면(지도 포함)은 [여기]({API_BASE_URL}/)에서 열 수 있습니다.')
if st.button('기존 웹 UI 열기 (새 탭)'):
    st.markdown(f'[링크]({API_BASE_URL}/)', unsafe_allow_html=True)
