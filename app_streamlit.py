"""
현장배정 관리 시스템 - Streamlit 메인 진입점
실행: streamlit run app_streamlit.py
사이드바 미사용, 상단 네비게이션으로 페이지 이동.
"""
import streamlit as st
from streamlit_utils.theme import apply_localhost_theme, render_top_nav

st.set_page_config(
    page_title='현장배정 관리 시스템',
    page_icon='🏗️',
    layout='wide',
    initial_sidebar_state='collapsed',
)
apply_localhost_theme()
render_top_nav()

st.title('🏗️ 현장배정 관리 시스템')
st.caption('상단 메뉴에서 페이지를 선택하세요.')

st.markdown('---')
st.markdown('''
**사용 가능한 페이지:**
- **대시보드**: 통계 요약 및 시각화
- **현장 목록**: 필터·검색·테이블, 배정/해제
- **현장등록**: 새 현장 등록
- **자격증등록**: 새 자격증 등록
- **투입가능인원 상세**: 투입 가능한 인원 상세 정보
''')
