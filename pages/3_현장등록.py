"""
현장등록 - 새 현장 등록
POST /api/sites (현장ID는 API에서 자동 부여). UI/UX: 로컬호스트 기준.
"""
import streamlit as st
from streamlit_utils.api_client import create_site, check_api_connection
from streamlit_utils.theme import apply_localhost_theme, render_top_nav

apply_localhost_theme()
render_top_nav()

# 페이지 제목 및 설명
st.title('➕ 현장등록')
st.caption('현장ID는 자동으로 부여됩니다.')

is_connected, error_msg = check_api_connection()
if not is_connected:
    st.error(f'API 연결 실패: {error_msg}')
    st.info('💡 Flask 서버를 먼저 실행하세요: `python run_api.py`')
    st.stop()

# 폼 스타일링 추가
st.markdown("""
<style>
    /* 폼 섹션 구분선 */
    .form-section-divider {
        border-top: 1px solid #e9ecef;
        margin: 24px 0 20px 0;
        padding-top: 20px;
    }
    /* 필수 입력 섹션 제목 */
    .required-section-title {
        font-size: 16px;
        font-weight: 600;
        color: #1a1d21;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 2px solid #e9ecef;
    }
    /* 선택 입력 섹션 제목 */
    .optional-section-title {
        font-size: 16px;
        font-weight: 600;
        color: #6c757d;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid #e9ecef;
    }
    /* 필드 간격 조정 */
    .stForm {
        max-width: 800px;
        margin: 0 auto;
    }
    /* 제출 버튼 영역 */
    .form-submit-area {
        margin-top: 24px;
        padding-top: 20px;
        border-top: 1px solid #e9ecef;
    }
    /* 제출 버튼 오른쪽 정렬 */
    [data-testid="stForm"] [data-testid="stFormSubmitButton"] {
        display: flex;
        justify-content: flex-end;
        margin-top: 20px;
    }
    [data-testid="stForm"] [data-testid="stFormSubmitButton"] button {
        margin-left: auto;
    }
    /* 탭 형태 선택 버튼 스타일 */
    .tab-select-label {
        font-size: 13px;
        font-weight: 600;
        color: #495057;
        margin-bottom: 12px;
        display: block;
    }
    /* Radio 버튼을 탭처럼 스타일링 */
    [data-testid="stRadio"] {
        margin-bottom: 20px !important;
        padding-bottom: 16px !important;
        border-bottom: 1px solid #e9ecef !important;
    }
    [data-testid="stRadio"] > div {
        display: flex !important;
        flex-wrap: wrap;
        gap: 8px !important;
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    [data-testid="stRadio"] > div > label {
        padding: 10px 16px !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 8px !important;
        background: #fff !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #495057 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        margin: 0 !important;
        flex: 0 0 auto !important;
        min-width: auto !important;
        width: auto !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    [data-testid="stRadio"] > div > label:hover {
        background: #f8f9fa !important;
        border-color: #adb5bd !important;
    }
    /* 활성 탭 스타일 - :has() 선택자 사용 (다른 탭과 동일한 파란 계열) */
    [data-testid="stRadio"] > div > label:has(input[type="radio"]:checked),
    [data-testid="stRadio"] > div > label:has(input[checked]) {
        background: #3b82f6 !important;
        border-color: #3b82f6 !important;
        color: #fff !important;
    }
    /* 활성 탭 스타일 - 호환성을 위한 대체 방법 */
    [data-testid="stRadio"] input[type="radio"]:checked + span,
    [data-testid="stRadio"] input[checked] + span {
        color: #fff !important;
    }
    /* JavaScript로 활성 상태 추가를 위한 클래스 */
    [data-testid="stRadio"] > div > label.tab-active {
        background: #3b82f6 !important;
        border-color: #3b82f6 !important;
        color: #fff !important;
    }
    [data-testid="stRadio"] input[type="radio"] {
        margin: 0 8px 0 0 !important;
        width: auto !important;
        cursor: pointer !important;
    }
    [data-testid="stRadio"] input[type="radio"]:checked {
        accent-color: #fff !important;
    }
    [data-testid="stRadio"] > div > label > div[data-testid="stMarkdownContainer"] {
        margin: 0 !important;
        padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

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
    
    # 날짜 필드들을 2열로 배치
    col3, col4 = st.columns(2)
    with col3:
        permit_date = st.text_input('건축허가일', placeholder='YYYY-MM-DD', help='건축허가일을 입력하세요 (예: 2024-01-15)')
    with col4:
        start_plan = st.text_input('착공예정일', placeholder='YYYY-MM-DD', help='착공 예정일을 입력하세요 (예: 2024-02-01)')
    
    # 준공일은 단일 컬럼
    completion_date = st.text_input('준공일', placeholder='YYYY-MM-DD', help='준공일을 입력하세요 (예: 2025-12-31)')
    
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
