"""
로컬호스트(site-management.html + css/style.css) UI/UX 기준 Streamlit 커스텀 스타일.
Modern Minimal Premium: 배경 #F8F9FA, 카드 Soft Shadow, 상태색 파스텔.
"""
import streamlit as st

# 로컬호스트 style.css / components.css 와 동일한 톤·정렬(패딩 24px, 전체 너비) 적용
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
/* 메인 콘텐츠 영역 = 로컬호스트 .main-content / .dashboard-section (padding 20px 24px, 전체 너비) */
.main .block-container,
.reportview-container .main .block-container {
    max-width: 100% !important;
    padding: 20px 24px 32px 24px !important;
}
/* Streamlit 1.40+ 대비: main 직하위 컨테이너 */
[data-testid="stAppViewContainer"] main > div {
    max-width: 100% !important;
    padding-left: 24px !important;
    padding-right: 24px !important;
    padding-top: 20px !important;
    padding-bottom: 32px !important;
}
/* 메인 영역 블록 = 카드 스타일 (Soft Shadow), 로컬 .stat-card / .register-section 톤 */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"],
section[data-testid="stSidebar"] > div {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    padding: 20px 16px;
    margin-bottom: 16px;
}
/* 대시보드 메트릭 행 = 로컬 .stats-grid (gap 16px) */
[data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"] {
    gap: 16px;
}
[data-testid="column"] {
    background: #fff;
    border-radius: 12px;
    padding: 20px 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
/* 사이드바 */
section[data-testid="stSidebar"] {
    background: #fff;
    box-shadow: 1px 0 3px rgba(0,0,0,0.06);
}
section[data-testid="stSidebar"] .stMarkdown {
    color: #495057;
}
/* 제목 = 로컬 .app-header h1 / .register-title / .list-header h3 (여백 동기화) */
[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3 {
    color: #1a1d21 !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em;
}
[data-testid="stAppViewContainer"] h1 {
    font-size: 20px;
    margin-top: 0;
    padding-top: 0;
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
    padding: 10px 24px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    min-width: 120px !important;
}
[data-testid="stFormSubmitButton"] button:hover {
    background: #343a40 !important;
}
/* 폼 컨테이너 최적화 */
[data-testid="stForm"] {
    max-width: 800px !important;
    margin: 0 auto !important;
}
/* 컬럼 간격 조정 */
[data-testid="column"] {
    gap: 16px;
}
/* 입력 필드 간격 조정 */
[data-testid="stTextInput"],
[data-testid="stSelectbox"],
[data-testid="stTextArea"] {
    margin-bottom: 16px;
}
/* 섹션 제목 스타일 */
.stSubheader {
    font-size: 16px !important;
    font-weight: 600 !important;
    color: #1a1d21 !important;
    margin-top: 24px !important;
    margin-bottom: 16px !important;
    padding-bottom: 8px !important;
    border-bottom: 1px solid #e9ecef !important;
}
/* 상태 배지 스타일 */
.status-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
    white-space: nowrap;
}
.status-badge-assigned {
    background-color: #d1fae5;
    color: #10b981;
}
.status-badge-unassigned {
    background-color: #fee2e2;
    color: #ef4444;
}
.status-badge-permit {
    background-color: #f3f4f6;
    color: #6b7280;
}
.status-badge-scheduled {
    background-color: #dbeafe;
    color: #3b82f6;
}
.status-badge-progress {
    background-color: #fef3c7;
    color: #f59e0b;
}
.status-badge-completed {
    background-color: #d1fae5;
    color: #10b981;
}
/* 테이블 행 호버 효과 */
.stMarkdown:has(> div) {
    transition: background-color 0.2s;
}
/* 페이지네이션 버튼 스타일 */
[data-testid="stButton"] button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}
/* 사이드바 스타일 개선 */
section[data-testid="stSidebar"] {
    padding: 20px;
}
section[data-testid="stSidebar"] .stButton > button {
    width: 100%;
}
/* 라디오 탭 스타일 - 선택 시 파란 계열(다른 탭과 동일) */
[data-testid="stRadio"] > div > label:has(input[type="radio"]:checked),
[data-testid="stRadio"] > div > label:has(input[checked]) {
    background: #3b82f6 !important;
    border-color: #3b82f6 !important;
    color: #fff !important;
}
[data-testid="stRadio"] > div > label.tab-active {
    background: #3b82f6 !important;
    border-color: #3b82f6 !important;
    color: #fff !important;
}
[data-testid="stRadio"] > div > label:hover {
    background: #f8f9fa !important;
    border-color: #adb5bd !important;
}
/* 사이드바 완전 숨김 (사용 안 함) */
section[data-testid="stSidebar"],
[data-testid="stSidebar"] {
    display: none !important;
}
/* 메인 영역 전체 너비 사용 */
[data-testid="stAppViewContainer"] main .block-container {
    max-width: 100% !important;
    padding-left: 24px !important;
    padding-right: 24px !important;
}
/* 사이드바 토글 버튼 숨김 */
button[kind="header"] {
    display: none !important;
}
[data-testid="collapsedControl"] {
    display: none !important;
}
</style>
"""

# 상단 네비게이션 링크 (사이드바 대체)
NAV_LINKS = [
    ('🏠 대시보드', '대시보드'),
    ('📋 현장 목록', '현장_목록'),
    ('➕ 현장등록', '현장등록'),
    ('📜 자격증등록', '자격증등록'),
    ('👥 투입가능인원 상세', '투입가능인원_상세'),
]


def apply_localhost_theme():
    """로컬호스트 UI/UX 기준 스타일을 현재 페이지에 적용."""
    st.markdown(LOCALHOST_CSS, unsafe_allow_html=True)


def render_top_nav():
    """상단 네비게이션 바 렌더링 (사이드바 미사용 시 페이지 이동용)."""
    st.markdown("""
    <style>
    .top-nav {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 20px;
        padding: 12px 0;
        border-bottom: 1px solid #e9ecef;
    }
    .top-nav a {
        color: #495057;
        text-decoration: none;
        padding: 8px 14px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        background: #fff;
        border: 1px solid #dee2e6;
        transition: all 0.2s;
    }
    .top-nav a:hover {
        background: #f8f9fa;
        border-color: #3b82f6;
        color: #3b82f6;
    }
    </style>
    <nav class="top-nav">
        <a href="/">🏗️ 홈</a>
        <a href="/대시보드">🏠 대시보드</a>
        <a href="/현장_목록">📋 현장 목록</a>
        <a href="/현장등록">➕ 현장등록</a>
        <a href="/자격증등록">📜 자격증등록</a>
        <a href="/투입가능인원_상세">👥 투입가능인원 상세</a>
    </nav>
    """, unsafe_allow_html=True)
