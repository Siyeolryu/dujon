"""
로컬호스트(site-management.html + css/style.css) UI/UX 기준 Streamlit 커스텀 스타일.
Modern Minimal Premium: 배경 #F8F9FA, 카드 Soft Shadow, 상태색 파스텔.
"""
import streamlit as st

# 로컬호스트 style.css / components.css 와 동일한 톤으로 블록·버튼·테이블·폼 오버라이드
LOCALHOST_CSS = """
<style>
/* 전역: 로컬호스트 폰트/배경 톤 유지 */
[data-testid="stAppViewContainer"] {
    background-color: #F8F9FA;
    font-family: 'Segoe UI', 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
}
[data-testid="stHeader"] {
    background: #fff;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
/* 메인 영역 블록 = 카드 스타일 (Soft Shadow) */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"],
section[data-testid="stSidebar"] > div {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    padding: 20px 16px;
    margin-bottom: 16px;
}
/* 사이드바 */
section[data-testid="stSidebar"] {
    background: #fff;
    box-shadow: 1px 0 3px rgba(0,0,0,0.06);
}
section[data-testid="stSidebar"] .stMarkdown {
    color: #495057;
}
/* 제목 = 로컬 register-title / list-header h3 */
h1, h2, h3 {
    color: #1a1d21 !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em;
}
/* 캡션/보조 텍스트 */
[data-testid="stCaptionContainer"], .stCaption {
    color: #6c757d !important;
    font-size: 13px;
}
/* 버튼 = 로컬 search-btn / cert-type-btn.active */
[data-testid="stButton"] button {
    background: #495057 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 16px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    transition: background 0.2s;
}
[data-testid="stButton"] button:hover {
    background: #343a40 !important;
    color: #fff !important;
}
/* 입력 필드 = 로컬 register-form input */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] div,
.stSelectbox > div > div {
    border: 1px solid #dee2e6 !important;
    border-radius: 8px !important;
    padding: 10px 12px !important;
    font-size: 14px !important;
    background: #fff !important;
}
/* 메트릭/숫자 = 로컬 stat-number */
[data-testid="stMetricValue"] {
    font-size: 28px !important;
    font-weight: 700 !important;
    color: #1a1d21 !important;
    letter-spacing: -0.02em;
}
[data-testid="stMetricLabel"] {
    font-size: 13px !important;
    color: #6c757d !important;
}
/* 데이터프레임 = 로컬 site-table */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
[data-testid="stDataFrame"] table {
    font-size: 14px;
}
[data-testid="stDataFrame"] thead tr {
    background: #f8f9fa !important;
}
[data-testid="stDataFrame"] th {
    color: #495057 !important;
    font-weight: 600 !important;
    padding: 12px 14px !important;
    border-bottom: 1px solid #e9ecef !important;
}
[data-testid="stDataFrame"] td {
    padding: 12px 14px !important;
    border-bottom: 1px solid #f1f3f5 !important;
    color: #212529 !important;
}
[data-testid="stDataFrame"] tbody tr:hover {
    background: #f8f9fa !important;
}
/* 성공/경고/에러 메시지 박스 */
[data-testid="stAlert"] {
    border-radius: 8px;
    border-left: 4px solid #495057;
}
/* 구분선 */
hr {
    border-color: #e9ecef !important;
}
/* 폼 제출 버튼 영역 */
[data-testid="stFormSubmitButton"] button {
    background: #495057 !important;
    color: #fff !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    font-weight: 500 !important;
}
</style>
"""


def apply_localhost_theme():
    """로컬호스트 UI/UX 기준 스타일을 현재 페이지에 적용."""
    st.markdown(LOCALHOST_CSS, unsafe_allow_html=True)
