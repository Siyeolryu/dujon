"""
현장등록 - 새 현장 등록
POST /api/sites (현장ID는 API에서 자동 부여). UI/UX: 로컬호스트 기준.
"""
import streamlit as st
from streamlit_utils.api_client import create_site, check_api_connection
from streamlit_utils.theme import apply_localhost_theme

apply_localhost_theme()

# 페이지 제목 및 설명
st.title('현장등록')
st.caption('현장ID는 자동으로 부여됩니다.')

is_connected, error_msg = check_api_connection()
if not is_connected:
    st.error(f'API 연결 실패: {error_msg}')
    st.info('Flask 서버를 먼저 실행하세요: `python run_api.py`')
    st.stop()

# 폼/탭 스타일 = streamlit_utils.theme 공통 적용 (인라인 제거)

with st.form('site_form'):
    # 필수 입력 섹션
    st.markdown('<div class="required-section-title">필수 입력</div>', unsafe_allow_html=True)
    
    # 2열 레이아웃: 현장명, 건축주명
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input('현장명 *', placeholder='예: OO아파트 신축공사', help='현장명을 입력하세요')
    with col2:
        client_name = st.text_input('건축주 명', placeholder='건축주/발주처 명', help='건축주 또는 발주처 명을 입력하세요')
    
    # 회사구분 (탭 형태)
    st.markdown('<div class="tab-select-label">회사구분 *</div>', unsafe_allow_html=True)
    company_radio = st.radio(
        '회사구분',
        ['더존종합건설', '더존하우징'],
        format_func=lambda x: '종합건설' if x == '더존종합건설' else '하우징',
        help='회사 구분을 선택하세요',
        horizontal=True,
        label_visibility='collapsed'
    )
    company = company_radio
    
    # 주소는 전체 너비
    address = st.text_input('주소 *', placeholder='현장 주소를 입력하세요', help='현장의 상세 주소를 입력하세요')

    # 선택 입력 섹션
    st.markdown('<div class="form-section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="optional-section-title">선택 입력</div>', unsafe_allow_html=True)
    
    # 현장상태 (탭 형태)
    st.markdown('<div class="tab-select-label">현장상태</div>', unsafe_allow_html=True)
    state = st.radio(
        '현장상태',
        ['건축허가', '착공예정', '공사 중', '공사 중단', '준공'],
        index=0,
        help='현재 현장 상태를 선택하세요',
        horizontal=True,
        label_visibility='collapsed'
    )
    
    # 날짜 필드 (st.date_input으로 형식 오류 방지)
    col3, col4 = st.columns(2)
    with col3:
        permit_date = st.date_input('건축허가일', value=None, help='건축허가일을 선택하세요', format='YYYY-MM-DD')
    with col4:
        start_plan = st.date_input('착공예정일', value=None, help='착공 예정일을 선택하세요', format='YYYY-MM-DD')
    
    completion_date = st.date_input('준공일', value=None, help='준공일을 선택하세요', format='YYYY-MM-DD')
    
    # 특이사항은 전체 너비
    note = st.text_area('특이사항', placeholder='비고 및 특이사항을 입력하세요', height=100, help='현장 관련 특이사항이나 비고를 입력하세요')

    # 제출 버튼
    st.markdown('<div class="form-submit-area"></div>', unsafe_allow_html=True)
    submitted = st.form_submit_button('등록', use_container_width=False, type='primary')

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
        if permit_date:
            payload['건축허가일'] = permit_date.strftime('%Y-%m-%d')
        if start_plan:
            payload['착공예정일'] = start_plan.strftime('%Y-%m-%d')
        if completion_date:
            payload['준공일'] = completion_date.strftime('%Y-%m-%d')
        if note and note.strip():
            payload['특이사항'] = note.strip()

        data, err = create_site(payload)
        if err:
            st.error(err)
        else:
            st.success('현장이 등록되었습니다.')
            if data:
                st.info(f"부여된 현장ID: {data.get('현장ID', '-')}")
            st.caption('현장 목록에서 확인하세요.')
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button('다른 현장 등록', key='reg_again_site'):
                    st.rerun()
            with col_b:
                if st.button('📋 현장 목록으로 이동', key='nav_to_sites'):
                    st.switch_page('pages/2_현장_목록.py')
