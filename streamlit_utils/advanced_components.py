"""
고급 UI 컴포넌트 - Streamlit 최적화
스마트 KPI 카드, 인터랙티브 테이블, 스마트 폼,
확인 다이얼로그, 로딩 스피너, 토스트 알림, 에러 폴백 UI
"""
import streamlit as st
from typing import List, Dict, Any, Optional, Tuple
import plotly.graph_objects as go
from streamlit_utils.design_tokens import T


def render_smart_kpi_card(
    label: str,
    value: Any,
    trend: Optional[str] = None,
    trend_direction: Optional[str] = None,
    sparkline_data: Optional[List[float]] = None,
    link_url: Optional[str] = None,
    link_text: Optional[str] = None,
    status: str = "",
    sublabel: Optional[str] = None,
    icon: Optional[str] = None,
) -> None:
    """스마트 KPI 카드 렌더링 (트렌드, 스파크라인 포함)
    
    Args:
        label: 카드 제목
        value: 표시할 값
        trend: 트렌드 값 (예: "+5", "-3")
        trend_direction: 트렌드 방향 ("up", "down", "neutral")
        sparkline_data: 미니 차트 데이터 [45, 47, 48, 50]
        link_url: 링크 URL
        link_text: 링크 텍스트
        status: 상태 클래스 (danger, success, info, warning)
        sublabel: 부가 설명
        icon: 아이콘 (emoji)
    """
    # 트렌드 HTML
    trend_html = ""
    if trend and trend_direction:
        trend_color = {
            "up": "#10b981",
            "down": "#ef4444",
            "neutral": "#6b7280"
        }.get(trend_direction, "#6b7280")
        
        trend_icon = {
            "up": "↑",
            "down": "↓",
            "neutral": "→"
        }.get(trend_direction, "→")
        
        trend_html = f'''
        <div class="kpi-trend" style="color: {trend_color}; font-size: 14px; font-weight: 500; margin-top: 4px;">
            <span style="font-size: 16px;">{trend_icon}</span> {trend}
        </div>
        '''
    
    # 스파크라인 HTML
    sparkline_html = ""
    if sparkline_data and len(sparkline_data) > 1:
        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=sparkline_data,
                mode='lines',
                line=dict(color='#3b82f6', width=2),
                fill='tozeroy',
                fillcolor='rgba(59, 130, 246, 0.1)',
            ))
            fig.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                height=40,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                showlegend=False,
            )
            sparkline_html = f'''
            <div class="kpi-sparkline" style="margin-top: 8px; height: 40px;">
                {fig.to_html(include_plotlyjs=False, div_id=f"sparkline_{label.replace(' ', '_')}")}
            </div>
            '''
        except Exception:
            pass
    
    # 아이콘 HTML
    icon_html = ""
    if icon:
        icon_html = f'<div class="kpi-icon" style="font-size: 24px; margin-bottom: 8px;">{icon}</div>'
    
    # 링크 HTML
    link_html = ""
    if link_url and link_text:
        link_html = f'<a href="{link_url}" class="kpi-link-btn">{link_text}</a>'
    
    # 부가 설명 HTML
    sublabel_html = ""
    if sublabel:
        sublabel_html = f'<div class="kpi-sublabel">{sublabel}</div>'
    
    # 카드 HTML
    card_html = f'''
    <div class="kpi-card {status}" style="position: relative; overflow: hidden;">
        {icon_html}
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        {trend_html}
        {sublabel_html}
        {sparkline_html}
        {link_html}
    </div>
    '''
    
    st.markdown(card_html, unsafe_allow_html=True)


def render_metric_comparison(
    label: str,
    current_value: float,
    previous_value: float,
    format_str: str = "{:.0f}",
    unit: str = "",
) -> None:
    """비교 메트릭 렌더링 (전월 대비 등)
    
    Args:
        label: 메트릭 이름
        current_value: 현재 값
        previous_value: 이전 값
        format_str: 포맷 문자열
        unit: 단위
    """
    delta = current_value - previous_value
    delta_percent = (delta / previous_value * 100) if previous_value != 0 else 0
    
    trend_direction = "up" if delta > 0 else "down" if delta < 0 else "neutral"
    trend_text = f"{delta_percent:+.1f}%"
    
    formatted_value = format_str.format(current_value) + unit
    
    render_smart_kpi_card(
        label=label,
        value=formatted_value,
        trend=trend_text,
        trend_direction=trend_direction,
    )


def render_progress_card(
    label: str,
    current: int,
    total: int,
    status: str = "info",
) -> None:
    """진행률 카드 렌더링
    
    Args:
        label: 카드 제목
        current: 현재 값
        total: 전체 값
        status: 상태 클래스
    """
    percentage = (current / total * 100) if total > 0 else 0
    
    progress_html = f'''
    <div class="kpi-card {status}">
        <div class="kpi-value">{current}/{total}</div>
        <div class="kpi-label">{label}</div>
        <div style="margin-top: 12px;">
            <div style="background: #e9ecef; border-radius: 8px; height: 8px; overflow: hidden;">
                <div style="background: #3b82f6; height: 100%; width: {percentage}%; transition: width 0.3s ease;"></div>
            </div>
            <div style="text-align: right; font-size: 12px; color: #6b7280; margin-top: 4px;">
                {percentage:.1f}%
            </div>
        </div>
    </div>
    '''
    
    st.markdown(progress_html, unsafe_allow_html=True)


def render_alert_card(
    title: str,
    message: str,
    alert_type: str = "warning",
    action_url: Optional[str] = None,
    action_text: Optional[str] = None,
) -> None:
    """알림 카드 렌더링
    
    Args:
        title: 알림 제목
        message: 알림 메시지
        alert_type: 알림 타입 (warning, danger, info, success)
        action_url: 액션 버튼 URL
        action_text: 액션 버튼 텍스트
    """
    colors = {
        "warning": {"bg": "#fef3c7", "border": "#f59e0b", "text": "#92400e"},
        "danger": {"bg": "#fee2e2", "border": "#ef4444", "text": "#991b1b"},
        "info": {"bg": "#dbeafe", "border": "#3b82f6", "text": "#1e40af"},
        "success": {"bg": "#d1fae5", "border": "#10b981", "text": "#065f46"},
    }
    
    color = colors.get(alert_type, colors["info"])
    
    action_html = ""
    if action_url and action_text:
        action_html = f'''
        <a href="{action_url}" style="
            display: inline-block;
            margin-top: 12px;
            padding: 8px 16px;
            background: {color['border']};
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
        ">{action_text}</a>
        '''
    
    alert_html = f'''
    <div style="
        background: {color['bg']};
        border-left: 4px solid {color['border']};
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 16px;
    ">
        <div style="font-weight: 600; color: {color['text']}; margin-bottom: 4px;">
            {title}
        </div>
        <div style="color: {color['text']}; font-size: 14px;">
            {message}
        </div>
        {action_html}
    </div>
    '''
    
    st.markdown(alert_html, unsafe_allow_html=True)


def render_stat_grid(stats: List[Tuple[str, Any, Optional[str]]]) -> None:
    """통계 그리드 렌더링
    
    Args:
        stats: [(label, value, unit), ...] 리스트
    """
    cols = st.columns(len(stats))
    
    for col, (label, value, unit) in zip(cols, stats):
        with col:
            unit_str = f" {unit}" if unit else ""
            st.markdown(f'''
            <div style="text-align: center; padding: 16px; background: #f8f9fa; border-radius: 8px;">
                <div style="font-size: 28px; font-weight: 700; color: #1a1d21;">
                    {value}{unit_str}
                </div>
                <div style="font-size: 13px; color: #6b7280; margin-top: 4px;">
                    {label}
                </div>
            </div>
            ''', unsafe_allow_html=True)


def render_quick_actions(actions: List[Dict[str, str]]) -> None:
    """빠른 액션 버튼 그룹 렌더링
    
    Args:
        actions: [{"icon": "🚨", "text": "미배정 현장", "url": "/..."}, ...]
    """
    st.markdown('<div class="quick-actions">', unsafe_allow_html=True)
    
    cols = st.columns(len(actions))
    
    for col, action in zip(cols, actions):
        with col:
            icon = action.get("icon", "")
            text = action.get("text", "")
            url = action.get("url", "#")
            
            st.markdown(f'''
            <a href="{url}" class="quick-action-btn">
                <div style="font-size: 24px; margin-bottom: 8px;">{icon}</div>
                <div style="font-size: 14px; font-weight: 500;">{text}</div>
            </a>
            ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_info_card(
    title: str,
    items: List[Tuple[str, str]],
    footer_text: Optional[str] = None,
    footer_url: Optional[str] = None,
) -> None:
    """정보 카드 렌더링
    
    Args:
        title: 카드 제목
        items: [(label, value), ...] 리스트
        footer_text: 푸터 텍스트
        footer_url: 푸터 링크 URL
    """
    items_html = ""
    for label, value in items:
        items_html += f'''
        <div class="info-row">
            <span class="info-label">{label}</span>
            <span class="info-value">{value}</span>
        </div>
        '''
    
    footer_html = ""
    if footer_text:
        if footer_url:
            footer_html = f'<a href="{footer_url}" class="info-footer-link">{footer_text}</a>'
        else:
            footer_html = f'<div class="info-footer">{footer_text}</div>'
    
    card_html = f'''
    <div class="info-card">
        <div class="info-card-title">{title}</div>
        {items_html}
        {footer_html}
    </div>
    '''
    
    st.markdown(card_html, unsafe_allow_html=True)


def render_empty_state(
    icon: str,
    title: str,
    message: str,
    action_text: Optional[str] = None,
    action_url: Optional[str] = None,
) -> None:
    """빈 상태 렌더링
    
    Args:
        icon: 아이콘 (emoji)
        title: 제목
        message: 메시지
        action_text: 액션 버튼 텍스트
        action_url: 액션 버튼 URL
    """
    action_html = ""
    if action_text and action_url:
        action_html = f'''
        <a href="{action_url}" style="
            display: inline-block;
            margin-top: 20px;
            padding: 12px 24px;
            background: #3b82f6;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 500;
        ">{action_text}</a>
        '''
    
    empty_html = f'''
    <div style="
        text-align: center;
        padding: 60px 20px;
        background: #f8f9fa;
        border-radius: 12px;
        margin: 40px 0;
    ">
        <div style="font-size: 64px; margin-bottom: 16px;">{icon}</div>
        <div style="font-size: 20px; font-weight: 600; color: #1a1d21; margin-bottom: 8px;">
            {title}
        </div>
        <div style="font-size: 14px; color: #6b7280;">
            {message}
        </div>
        {action_html}
    </div>
    '''
    
    st.markdown(empty_html, unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 확인 다이얼로그 · 로딩 · 토스트 · 에러 폴백
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_confirm_dialog(
    title: str,
    message: str,
    confirm_label: str = "확인",
    cancel_label: str = "취소",
    dialog_type: str = "warning",
    key: str = "confirm_dialog",
) -> Optional[bool]:
    """확인/취소 다이얼로그.

    Returns:
        True  → 사용자가 '확인' 클릭
        False → 사용자가 '취소' 클릭
        None  → 아직 선택하지 않음
    """
    colors = {
        "warning": {"bg": T.STATUS_WARNING_BG, "border": T.STATUS_WARNING, "text": T.STATUS_WARNING_TEXT, "icon": "⚠️"},
        "danger":  {"bg": T.STATUS_DANGER_BG,  "border": T.STATUS_DANGER,  "text": T.STATUS_DANGER_TEXT,  "icon": "🚨"},
        "info":    {"bg": T.STATUS_INFO_BG,    "border": T.STATUS_INFO,    "text": T.STATUS_INFO_TEXT,    "icon": "ℹ️"},
    }
    c = colors.get(dialog_type, colors["warning"])

    st.markdown(f'''
    <div style="
        background:{c['bg']}; border-left:4px solid {c['border']};
        padding:20px; border-radius:{T.RADIUS_MD}; margin:16px 0;
    ">
        <div style="font-size:18px; font-weight:{T.FONT_WEIGHT_SEMIBOLD}; color:{c['text']}; margin-bottom:8px;">
            {c['icon']} {title}
        </div>
        <div style="font-size:{T.FONT_SIZE_BASE}; color:{c['text']};">
            {message}
        </div>
    </div>
    ''', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        if st.button(cancel_label, key=f"{key}_cancel", use_container_width=True):
            return False
    with col3:
        if st.button(confirm_label, key=f"{key}_confirm", type="primary", use_container_width=True):
            return True
    return None


def render_loading_card(message: str = "데이터를 불러오는 중입니다...") -> None:
    """스켈레톤 느낌의 로딩 카드."""
    st.markdown(f'''
    <div style="
        text-align:center; padding:48px 20px;
        background:{T.BG_HOVER}; border-radius:{T.RADIUS_LG};
        margin:24px 0;
    ">
        <div style="
            width:40px; height:40px; margin:0 auto 16px auto;
            border:4px solid {T.BORDER_DEFAULT};
            border-top-color:{T.COLOR_PRIMARY};
            border-radius:50%;
            animation:spin 0.8s linear infinite;
        "></div>
        <div style="font-size:{T.FONT_SIZE_BASE}; color:{T.TEXT_MUTED};">
            {message}
        </div>
    </div>
    <style>@keyframes spin {{ 0% {{ transform:rotate(0deg) }} 100% {{ transform:rotate(360deg) }} }}</style>
    ''', unsafe_allow_html=True)


def render_toast(
    message: str,
    toast_type: str = "success",
    duration_ms: int = 3000,
    key: str = "toast",
) -> None:
    """자동 사라지는 토스트 알림 (CSS animation 기반).

    Args:
        message: 표시할 메시지
        toast_type: 'success' | 'danger' | 'warning' | 'info'
        duration_ms: 표시 시간 (ms)
        key: 고유 키
    """
    color_map = {
        "success": (T.STATUS_SUCCESS, T.STATUS_SUCCESS_BG, T.STATUS_SUCCESS_TEXT, "✅"),
        "danger":  (T.STATUS_DANGER,  T.STATUS_DANGER_BG,  T.STATUS_DANGER_TEXT,  "❌"),
        "warning": (T.STATUS_WARNING, T.STATUS_WARNING_BG, T.STATUS_WARNING_TEXT, "⚠️"),
        "info":    (T.STATUS_INFO,    T.STATUS_INFO_BG,    T.STATUS_INFO_TEXT,    "ℹ️"),
    }
    border, bg, text, icon = color_map.get(toast_type, color_map["info"])

    st.markdown(f'''
    <style>
    @keyframes toast_slide_{key} {{
        0% {{ transform:translateX(100%); opacity:0 }}
        10% {{ transform:translateX(0); opacity:1 }}
        90% {{ transform:translateX(0); opacity:1 }}
        100% {{ transform:translateX(100%); opacity:0 }}
    }}
    </style>
    <div style="
        position:fixed; top:20px; right:20px; z-index:10000;
        padding:14px 20px; border-radius:{T.RADIUS_MD};
        background:{bg}; border-left:4px solid {border};
        color:{text}; font-size:{T.FONT_SIZE_BASE}; font-weight:{T.FONT_WEIGHT_MEDIUM};
        box-shadow:{T.SHADOW_LG};
        animation:toast_slide_{key} {duration_ms}ms ease forwards;
        pointer-events:none;
    ">
        {icon} {message}
    </div>
    ''', unsafe_allow_html=True)


def render_error_fallback(
    error_message: str,
    retry_label: str = "다시 시도",
    help_text: str = "",
    key: str = "error_fallback",
) -> bool:
    """API 실패 등 에러 시 표시하는 폴백 UI.

    Returns:
        True if 사용자가 '다시 시도' 클릭
    """
    st.markdown(f'''
    <div style="
        text-align:center; padding:48px 20px;
        background:{T.STATUS_DANGER_BG}; border-radius:{T.RADIUS_LG};
        border:1px solid {T.STATUS_DANGER}20; margin:24px 0;
    ">
        <div style="font-size:48px; margin-bottom:12px;">⚠️</div>
        <div style="font-size:{T.FONT_SIZE_MD}; font-weight:{T.FONT_WEIGHT_SEMIBOLD}; color:{T.STATUS_DANGER_TEXT}; margin-bottom:8px;">
            문제가 발생했습니다
        </div>
        <div style="font-size:{T.FONT_SIZE_SM}; color:{T.STATUS_DANGER_TEXT}; margin-bottom:4px;">
            {error_message}
        </div>
    </div>
    ''', unsafe_allow_html=True)

    if help_text:
        st.caption(help_text)

    return st.button(f"🔄 {retry_label}", key=key, type="primary")


def render_status_pill(status: str, domain: str = "assignment") -> str:
    """상태값을 디자인 토큰 기반 HTML 필 배지로 반환.

    Args:
        status: '배정완료', '투입가능' 등
        domain: 'assignment' | 'site_state' | 'personnel' | 'certificate'

    Returns:
        HTML string (st.markdown unsafe_allow_html 필요)
    """
    c = T.status_color(status, domain)
    return (
        f'<span style="display:inline-block; padding:4px 10px; border-radius:{T.RADIUS_PILL};'
        f' font-size:{T.FONT_SIZE_XS}; font-weight:{T.FONT_WEIGHT_MEDIUM};'
        f' background:{c["bg"]}; color:{c["text"]};">{status}</span>'
    )


def render_data_table_header(
    title: str,
    total_count: int,
    filter_summary: str = "",
) -> None:
    """데이터 테이블 상단 헤더 (건수 표시 + 필터 요약)."""
    filter_html = ""
    if filter_summary:
        filter_html = f'<span style="font-size:{T.FONT_SIZE_SM}; color:{T.TEXT_MUTED}; margin-left:12px;">{filter_summary}</span>'

    st.markdown(f'''
    <div style="
        display:flex; align-items:baseline; justify-content:space-between;
        margin-bottom:16px; padding-bottom:12px;
        border-bottom:2px solid {T.BORDER_LIGHT};
    ">
        <div>
            <span style="font-size:{T.FONT_SIZE_LG}; font-weight:{T.FONT_WEIGHT_SEMIBOLD}; color:{T.TEXT_HEADING};">
                {title}
            </span>
            <span style="
                display:inline-block; margin-left:8px; padding:2px 10px;
                border-radius:{T.RADIUS_PILL}; background:{T.STATUS_INFO_BG};
                font-size:{T.FONT_SIZE_XS}; font-weight:{T.FONT_WEIGHT_SEMIBOLD}; color:{T.STATUS_INFO_TEXT};
            ">{total_count}건</span>
            {filter_html}
        </div>
    </div>
    ''', unsafe_allow_html=True)
