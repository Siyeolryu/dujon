"""
현장 목록 - 필터, 검색, 테이블, 배정/해제
GET /api/sites, GET /api/sites/search, POST assign/unassign, GET /api/personnel. UI/UX: 로컬호스트 기준.
"""
import streamlit as st
import pandas as pd
from streamlit_utils.api_client import (
    get_sites,
    search_sites,
    get_site,
    get_personnel,
    get_certificates,
    assign_site,
    unassign_site,
    check_api_connection,
)
from streamlit_utils.theme import apply_localhost_theme

apply_localhost_theme()
st.title('📋 현장 목록')

if not check_api_connection():
    st.error('API에 연결할 수 없습니다. Flask 서버를 먼저 실행하세요.')
    st.stop()

# 필터
col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
with col1:
    company = st.selectbox(
        '회사',
        ['', '더존종합건설', '더존하우징'],
        format_func=lambda x: {'': '전체', '더존종합건설': '종합건설', '더존하우징': '하우징'}.get(x, x),
    )
with col2:
    status = st.selectbox('배정상태', ['', '배정완료', '미배정'], format_func=lambda x: x or '전체')
with col3:
    state = st.selectbox(
        '현장상태',
        ['', '건축허가', '착공예정', '착공중', '준공'],
        format_func=lambda x: x or '전체',
    )
with col4:
    search_q = st.text_input('현장명·주소 검색', placeholder='검색어 입력 후 Enter')

if search_q and search_q.strip():
    sites, err = search_sites(search_q)
else:
    sites, err = get_sites(
        company=company or None,
        status=status or None,
        state=state or None,
    )

if err:
    st.error(err)
    st.stop()

if not sites:
    st.info('조건에 맞는 현장이 없습니다.')
    st.stop()

# 테이블용 컬럼만 추출
display_cols = ['현장명', '회사구분', '배정상태', '현장상태', '담당소장명', '현장ID']
rows = []
for s in sites:
    row = {k: s.get(k, '') for k in display_cols}
    # 회사구분 표시: 더존종합건설 -> 종합건설
    if row.get('회사구분') == '더존종합건설':
        row['회사구분'] = '종합건설'
    elif row.get('회사구분') == '더존하우징':
        row['회사구분'] = '하우징'
    rows.append(row)

df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown('---')
st.subheader('현장 상세 / 배정')

site_id = st.text_input('현장ID (상세 조회 또는 배정/해제할 현장)', placeholder='예: SITE-20260202120000-ABC123')
if not site_id or not site_id.strip():
    st.caption('위 테이블에서 현장ID를 복사해 입력하세요.')
    st.stop()

detail, err = get_site(site_id.strip())
if err and not detail:
    st.error(err)
    st.stop()

if detail:
    st.json(detail)
    version = detail.get('version', '')

    if detail.get('배정상태') == '배정완료':
        if st.button('배정 해제'):
            out, err = unassign_site(site_id.strip(), version=version or None)
            if err:
                st.error(err)
            else:
                st.success('배정이 해제되었습니다.')
                st.rerun()
    else:
        personnel_list, _ = get_personnel(status='투입가능')
        cert_list, _ = get_certificates(available=True)
        if not personnel_list:
            st.warning('투입가능 인력이 없습니다.')
        elif not cert_list:
            st.warning('사용가능 자격증이 없습니다.')
        else:
            manager_options = {f"{p.get('성명', '')} ({p.get('인력ID', '')})": p.get('인력ID') for p in personnel_list}
            cert_options = {f"{c.get('자격증명', '')} / {c.get('소유자명', '')} ({c.get('자격증ID', '')})": c.get('자격증ID') for c in cert_list}
            sel_manager = st.selectbox('담당 소장', list(manager_options.keys()))
            sel_cert = st.selectbox('사용 자격증', list(cert_options.keys()))
            if st.button('소장 배정'):
                mid = manager_options.get(sel_manager)
                cid = cert_options.get(sel_cert)
                if mid and cid:
                    out, err = assign_site(site_id.strip(), mid, cid, version=version or None)
                    if err:
                        st.error(err)
                    else:
                        st.success('배정되었습니다.')
                        st.rerun()
                else:
                    st.error('소장 또는 자격증을 선택하세요.')
