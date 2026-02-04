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

# API 연결 확인 (streamlit_utils가 있는 경우)
try:
    from streamlit_utils.api_client import check_api_connection
    is_connected, error_msg = check_api_connection()
except ImportError:
    is_connected = False
    error_msg = "streamlit_utils 모듈을 찾을 수 없습니다"

# 메인 페이지 내용
st.title('🏗️ 현장배정 관리 시스템')
st.caption('좌측 사이드바에서 페이지를 선택하세요.')

# API 연결 상태 표시
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

# 페이지 안내
st.markdown('''
### 📋 사용 가능한 페이지

| 페이지 | 설명 |
|--------|------|
| **📊 대시보드** | 통계 요약 (전체 현장, 미배정, 배정완료, 투입가능 인력) |
| **📋 현장 목록** | 필터·검색·테이블, 배정/해제 |
| **➕ 현장등록** | 새 현장 등록 (현장ID 자동 부여) |
| **📜 자격증등록** | 새 자격증 등록 (자격증ID·소유자ID 자동 부여) |
| **👥 투입가능인원 상세** | 투입 가능한 인원 상세 정보 |

👈 **좌측 사이드바**에서 페이지를 선택하세요.
''')

# 기존 HTML 웹 UI 링크 (로컬 개발 시)
st.markdown('---')
st.markdown('### 🔗 기타')
st.markdown(f'HTML/JS 기반 화면(지도 포함)은 Flask 서버에서 확인: `{API_BASE_URL}/`')
