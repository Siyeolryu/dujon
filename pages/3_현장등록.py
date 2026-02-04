"""
현장등록 - 새 현장 등록
POST /api/sites (현장ID는 API에서 자동 부여). UI/UX: 로컬호스트 기준.
"""
import streamlit as st
from streamlit_utils.api_client import create_site, check_api_connection
from streamlit_utils.theme import apply_localhost_theme

apply_localhost_theme()
st.title('➕ 현장등록')

is_connected, error_msg = check_api_connection()
if not is_connected:
    st.error(f'API 연결 실패: {error_msg}')
    st.info('💡 Flask 서버를 먼저 실행하세요: `python run_api.py`')
    st.stop()

with st.form('site_form'):
    st.subheader('필수 입력')
    name = st.text_input('현장명 *', placeholder='예: OO아파트 신축공사')
    client_name = st.text_input('건축주 명', placeholder='건축주/발주처 명')
    company = st.selectbox(
        '회사구분 *',
        ['더존종합건설', '더존하우징'],
        format_func=lambda x: '종합건설' if x == '더존종합건설' else '하우징',
    )
    address = st.text_input('주소 *', placeholder='현장 주소')

    st.subheader('선택 입력')
    state = st.selectbox(
        '현장상태',
        ['건축허가', '착공예정', '공사 중', '공사 중단', '준공'],
        index=0,
    )
    permit_date = st.text_input('건축허가일', placeholder='YYYY-MM-DD')
    start_plan = st.text_input('착공예정일', placeholder='YYYY-MM-DD')
    completion_date = st.text_input('준공일', placeholder='YYYY-MM-DD')
    note = st.text_area('특이사항', placeholder='비고')

    submitted = st.form_submit_button('등록')

if submitted:
    if not (name and name.strip()):
        st.error('현장명을 입력하세요.')
    elif not (address and address.strip()):
        st.error('주소를 입력하세요.')
    else:
        payload = {
            '현장명': name.strip(),
            '건축주명': (client_name or '').strip(),
            '회사구분': company,
            '주소': address.strip(),
            '현장상태': state,
            '배정상태': '미배정',
        }
        if permit_date and permit_date.strip():
            payload['건축허가일'] = permit_date.strip()
        if start_plan and start_plan.strip():
            payload['착공예정일'] = start_plan.strip()
        if completion_date and completion_date.strip():
            payload['준공일'] = completion_date.strip()
        if note and note.strip():
            payload['특이사항'] = note.strip()

        data, err = create_site(payload)
        if err:
            st.error(err)
        else:
            st.success('현장이 등록되었습니다.')
            if data:
                st.info(f"부여된 현장ID: {data.get('현장ID', '-')}")
