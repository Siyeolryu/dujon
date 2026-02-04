"""
자격증등록 - 새 자격증 등록
POST /api/certificates (자격증ID·소유자ID는 API에서 자동 부여). UI/UX: 로컬호스트 기준.
"""
import streamlit as st
import os
from streamlit_utils.api_client import create_certificate, check_api_connection
from streamlit_utils.theme import apply_localhost_theme

apply_localhost_theme()

# 페이지 제목 및 설명
st.title('📜 자격증등록')
st.caption('자격증ID는 자동으로 부여됩니다.')

# API 연결 확인 (Supabase 모드일 때는 체크 건너뛰기)
api_mode = os.getenv('API_MODE', '').strip().lower() or 'flask'
if api_mode != 'supabase':
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
    [data-testid="stRadio"] > div > label:has(input[type="radio"]:checked),
    [data-testid="stRadio"] > div > label:has(input[checked]) {
        background: #495057 !important;
        border-color: #495057 !important;
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

# 자격증 종류 (화면 표시용)
CERT_OPTIONS = [
    '건설초급',
    '건설중급',
    '건설고급',
    '건설특급',
]

with st.form('cert_form'):
    # 필수 입력 섹션
    st.markdown('<div class="required-section-title">필수 입력</div>', unsafe_allow_html=True)
    
    # 자격증 종류 (탭 형태)
    st.markdown('<div class="tab-select-label">자격증 종류 *</div>', unsafe_allow_html=True)
    cert_name_radio = st.radio(
        '자격증 종류',
        CERT_OPTIONS,
        help='등록할 자격증 종류를 선택하세요.',
        horizontal=True,
        label_visibility='collapsed'
    )
    cert_name = cert_name_radio
    
    # 소유자 정보 (2열 레이아웃)
    col1, col2 = st.columns(2)
    with col1:
        owner_name = st.text_input(
            '소유자 명 *',
            placeholder='자격증 소유자 성명',
            help='자격증 소유자의 성명을 입력하세요'
        )
    with col2:
        owner_phone = st.text_input(
            '연락처',
            placeholder='전화번호 (예: 010-1234-5678)',
            help='소유자의 연락처를 입력하세요'
        )
    
    # 자격증 번호 (전체 너비)
    cert_number = st.text_input(
        '자격증 번호',
        placeholder='자격증 번호를 입력하세요 (선택사항)',
        help='자격증 고유 번호를 입력하세요'
    )
    
    # 선택 입력 섹션
    st.markdown('<div class="form-section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="optional-section-title">선택 입력</div>', unsafe_allow_html=True)
    
    # 날짜 필드들을 2열로 배치
    col3, col4 = st.columns(2)
    with col3:
        issued_date = st.text_input(
            '취득일',
            placeholder='YYYY-MM-DD',
            help='자격증 취득일을 입력하세요 (예: 2024-01-15)'
        )
    with col4:
        expiry_date = st.text_input(
            '유효기간',
            placeholder='YYYY-MM-DD',
            help='자격증 유효기간 만료일을 입력하세요 (예: 2029-01-15)'
        )
    
    # 사용여부 (탭 형태)
    st.markdown('<div class="tab-select-label">사용여부</div>', unsafe_allow_html=True)
    use_status = st.radio(
        '사용여부',
        ['사용가능', '사용중', '만료'],
        index=0,
        help='자격증의 현재 사용 상태를 선택하세요',
        horizontal=True,
        label_visibility='collapsed'
    )
    
    # 비고는 전체 너비
    remark = st.text_area(
        '비고',
        placeholder='비고 및 특이사항을 입력하세요',
        height=100,
        help='자격증 관련 특이사항이나 비고를 입력하세요'
    )

    # 제출 버튼
    st.markdown('<div class="form-submit-area"></div>', unsafe_allow_html=True)
    submitted = st.form_submit_button('등록', use_container_width=False, type='primary')

if submitted:
    if not (owner_name and owner_name.strip()):
        st.error('소유자 명을 입력하세요.')
    else:
        payload = {
            '자격증명': cert_name,
            '소유자명': owner_name.strip(),
            '소유자연락처': (owner_phone or '').strip(),
            '사용가능여부': use_status,
            '비고': (remark or '').strip(),
        }
        # 선택 입력 필드 추가
        if cert_number and cert_number.strip():
            payload['자격증번호'] = cert_number.strip()
        if issued_date and issued_date.strip():
            payload['취득일'] = issued_date.strip()
        if expiry_date and expiry_date.strip():
            payload['유효기간'] = expiry_date.strip()
        
        data, err = create_certificate(payload)
        if err:
            st.error(err)
        else:
            st.success('자격증이 등록되었습니다.')
            if data:
                st.info(f"부여된 자격증ID: {data.get('자격증ID', '-')}, 소유자ID: {data.get('소유자ID', '-')}")
