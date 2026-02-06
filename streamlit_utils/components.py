"""
공통 UI 컴포넌트 - KPI 카드, 상태 배지, 네비게이션 버튼
"""
import streamlit as st


def render_kpi_card(
    label: str,
    value,
    link_text: str = None,
    link_url: str = None,
    status_class: str = "",
    sublabel: str = None,
) -> None:
    """KPI 카드 렌더링

    Args:
        label: 카드 제목 (예: "전체 현장")
        value: 표시할 값 (숫자 또는 문자열)
        link_text: 링크 버튼 텍스트 (예: "현장 목록")
        link_url: 링크 URL (예: "/2_현장_목록")
        status_class: 상태 클래스 (danger, success, info, warning)
        sublabel: 부가 설명 (예: "전체 10명, 투입가능 5명")
    """
    link_html = ""
    if link_url and link_text:
        link_html = f'<a href="{link_url}" class="kpi-link-btn">{link_text}</a>'

    sublabel_html = ""
    if sublabel:
        sublabel_html = f'<div class="kpi-sublabel">{sublabel}</div>'

    card_html = f'''
    <div class="kpi-card {status_class}">
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        {sublabel_html}
        {link_html}
    </div>
    '''
    st.markdown(card_html, unsafe_allow_html=True)


def render_kpi_grid_start() -> None:
    """KPI 그리드 컨테이너 시작"""
    st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)


def render_kpi_grid_end() -> None:
    """KPI 그리드 컨테이너 종료"""
    st.markdown('</div>', unsafe_allow_html=True)


def render_nav_button(text: str, url: str, primary: bool = False) -> None:
    """네비게이션 버튼 렌더링

    Args:
        text: 버튼 텍스트
        url: 이동할 URL
        primary: 주요 버튼 여부 (파란색)
    """
    btn_class = "nav-btn-primary" if primary else "nav-btn-secondary"
    st.markdown(f'''
    <a href="{url}" class="nav-btn {btn_class}">{text}</a>
    ''', unsafe_allow_html=True)


def render_nav_button_group(buttons: list) -> None:
    """네비게이션 버튼 그룹 렌더링

    Args:
        buttons: [(text, url, primary), ...] 리스트
    """
    st.markdown('<div class="nav-btn-group">', unsafe_allow_html=True)
    for btn in buttons:
        text, url = btn[0], btn[1]
        primary = btn[2] if len(btn) > 2 else False
        btn_class = "nav-btn-primary" if primary else "nav-btn-secondary"
        st.markdown(f'<a href="{url}" class="nav-btn {btn_class}">{text}</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_status_badge(status: str, badge_type: str = 'assignment') -> str:
    """상태 배지 HTML 반환

    Args:
        status: 상태 문자열 (예: "배정완료", "미배정")
        badge_type: 배지 유형 ('assignment' 또는 'site_state')

    Returns:
        HTML 문자열
    """
    class_map = {
        'assignment': {
            '배정완료': 'status-badge-assigned',
            '미배정': 'status-badge-unassigned',
        },
        'site_state': {
            '건축허가': 'status-badge-permit',
            '착공예정': 'status-badge-scheduled',
            '공사 중': 'status-badge-progress',
            '공사 중단': 'status-badge-unassigned',
            '준공': 'status-badge-completed',
        },
        'personnel': {
            '투입가능': 'status-badge-assigned',
            '투입중': 'status-badge-progress',
            '휴직': 'status-badge-permit',
            '퇴사': 'status-badge-unassigned',
        },
        'certificate': {
            '사용가능': 'status-badge-assigned',
            '사용중': 'status-badge-progress',
            '만료': 'status-badge-unassigned',
        },
    }
    css_class = class_map.get(badge_type, {}).get(status, '')
    return f'<span class="status-badge {css_class}">{status}</span>'


def render_section_header(title: str, subtitle: str = None) -> None:
    """섹션 헤더 렌더링

    Args:
        title: 섹션 제목
        subtitle: 부제목 (선택)
    """
    subtitle_html = f'<span class="section-subtitle">{subtitle}</span>' if subtitle else ''
    st.markdown(f'''
    <div class="section-header">
        <h3 class="section-title">{title}</h3>
        {subtitle_html}
    </div>
    ''', unsafe_allow_html=True)


def render_info_card(title: str, items: list) -> None:
    """정보 카드 렌더링 (키-값 목록)

    Args:
        title: 카드 제목
        items: [(label, value), ...] 리스트
    """
    items_html = ""
    for label, value in items:
        items_html += f'''
        <div class="info-row">
            <span class="info-label">{label}</span>
            <span class="info-value">{value}</span>
        </div>
        '''

    st.markdown(f'''
    <div class="info-card">
        <div class="info-card-title">{title}</div>
        {items_html}
    </div>
    ''', unsafe_allow_html=True)


def render_quick_actions(actions: list) -> None:
    """퀵 액션 버튼 그룹 렌더링

    Args:
        actions: [(icon, text, url), ...] 리스트
    """
    st.markdown('<div class="quick-actions">', unsafe_allow_html=True)
    for action in actions:
        icon, text, url = action
        st.markdown(f'''
        <a href="{url}" class="quick-action-btn">
            <span class="quick-action-icon">{icon}</span>
            <span class="quick-action-text">{text}</span>
        </a>
        ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
