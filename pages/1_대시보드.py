"""
대시보드 - 통계 요약
GET /api/stats 사용. UI/UX: 로컬호스트 기준.
"""
import streamlit as st
from streamlit_utils.api_client import get_stats, check_api_connection
from streamlit_utils.theme import apply_localhost_theme

apply_localhost_theme()
st.title('📊 대시보드')

if not check_api_connection():
    st.error('API에 연결할 수 없습니다. Flask 서버를 먼저 실행하세요.')
    st.stop()

data, err = get_stats()
if err:
    st.error(err)
    st.stop()

if not data:
    st.info('통계 데이터가 없습니다.')
    st.stop()

sites = data.get('sites', {})
personnel = data.get('personnel', {})
certificates = data.get('certificates', {})

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric('전체 현장', sites.get('total', 0))
with col2:
    st.metric('미배정 현장', sites.get('unassigned', 0))
with col3:
    st.metric('배정완료', sites.get('assigned', 0))
with col4:
    st.metric('투입가능 인력', personnel.get('available', 0))
with col5:
    st.metric('사용가능 자격증', certificates.get('available', 0))

st.markdown('---')
st.subheader('현장 현황')
st.json({
    '회사별': sites.get('by_company', {}),
    '현장상태별': sites.get('by_state', {}),
})

st.subheader('인력 현황')
st.json(personnel.get('by_role', {}))
