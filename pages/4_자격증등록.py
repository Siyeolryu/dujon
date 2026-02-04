"""
자격증등록 - 새 자격증 등록
POST /api/certificates (자격증ID·소유자ID는 API에서 자동 부여). UI/UX: 로컬호스트 기준.
"""
import streamlit as st
from streamlit_utils.api_client import create_certificate, check_api_connection
from streamlit_utils.theme import apply_localhost_theme

apply_localhost_theme()
st.title('📜 자격증등록')

is_connected, error_msg = check_api_connection()
if not is_connected:
    st.error(f'API 연결 실패: {error_msg}')
    st.info('💡 Flask 서버를 먼저 실행하세요: `python run_api.py`')
    st.stop()

# 자격증 종류 (화면 표시용)
CERT_OPTIONS = [
    '건설초급',
    '건설중급',
    '건설고급',
    '건설특급',
]

with st.form('cert_form'):
    st.subheader('자격증 정보')
    cert_name = st.selectbox(
        '자격증 종류 *',
        CERT_OPTIONS,
        help='등록할 자격증 종류를 선택하세요.',
    )
    st.subheader('소유자 정보')
    owner_name = st.text_input('소유자 명 *', placeholder='자격증 소유자 성명')
    owner_phone = st.text_input('연락처', placeholder='전화번호')
    use_status = st.selectbox('사용여부', ['사용가능', '사용중', '만료'], index=0)
    remark = st.text_area('비고', placeholder='비고')

    submitted = st.form_submit_button('등록')

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
        data, err = create_certificate(payload)
        if err:
            st.error(err)
        else:
            st.success('자격증이 등록되었습니다.')
            if data:
                st.info(f"부여된 자격증ID: {data.get('자격증ID', '-')}, 소유자ID: {data.get('소유자ID', '-')}")
