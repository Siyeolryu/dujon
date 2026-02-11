"""
대시보드 - 통계 요약 및 시각화 (임원용)
KPI 카드 + 배정/현장상태/인력 차트 (API/Supabase 연동)
Modern UI: 호버 효과, 반응형 그리드, 버튼 스타일 네비게이션
"""
import os
import streamlit as st
from streamlit_utils.cached_api import check_api_connection_cached, get_stats_cached

from streamlit_utils.theme import apply_localhost_theme
from streamlit_utils.components import (
    render_kpi_card,
    render_kpi_grid_start,
    render_kpi_grid_end,
    render_section_header,
)

apply_localhost_theme()
st.title("대시보드")


def _normalize_stats(raw):
    """Flask API 형식(sites/personnel/certificates) 또는 Supabase 플랫 형식을 통일."""
    if not raw:
        return {
            "total_sites": 0,
            "unassigned": 0,
            "assigned": 0,
            "total_personnel": 0,
            "available_personnel": 0,
            "deployed_personnel": 0,
            "total_certificates": 0,
            "available_certificates": 0,
        }
    if "sites" in raw:
        sites = raw.get("sites") or {}
        personnel = raw.get("personnel") or {}
        certs = raw.get("certificates") or {}
        return {
            "total_sites": sites.get("total", 0),
            "unassigned": sites.get("unassigned", 0),
            "assigned": sites.get("assigned", 0),
            "total_personnel": personnel.get("total", 0),
            "available_personnel": personnel.get("available", 0),
            "deployed_personnel": personnel.get("deployed", 0),
            "total_certificates": certs.get("total", 0),
            "available_certificates": certs.get("available", 0),
        }
    return {
        "total_sites": raw.get("total_sites", 0),
        "unassigned": raw.get("unassigned_sites", 0),
        "assigned": raw.get("assigned_sites", 0),
        "total_personnel": raw.get("total_personnel", 0),
        "available_personnel": raw.get("available_personnel", 0),
        "deployed_personnel": raw.get("deployed", 0),
        "total_certificates": raw.get("total_certificates", 0),
        "available_certificates": raw.get("available_certificates", 0),
    }


# 차트 색상 팔레트
CHART_COLORS = {
    "primary": "#3b82f6",
    "success": "#10b981",
    "danger": "#ef4444",
    "warning": "#f59e0b",
    "info": "#06b6d4",
    "secondary": "#6b7280",
}

# API / DB 연결 상태
api_mode = os.getenv('API_MODE', '').strip().lower() or 'flask'
is_connected, error_msg = check_api_connection_cached()

if not is_connected and api_mode != 'supabase':
    st.error(f"**API 연결 실패**: {error_msg}")
    st.info(
        """
    **해결 방법:**
    1. **Flask 서버 실행**: 터미널에서 `python run_api.py` 실행
    2. **환경 변수 확인**: `.env`에 `API_BASE_URL=http://localhost:5000/api` 확인
    3. **Supabase 사용 시**: `API_MODE=supabase` 및 Supabase 키 설정 후 재시도

    아래 대시보드는 데이터 없음(0)으로 표시됩니다.
    """
    )

# 통계 조회
raw_stats, stats_err = get_stats_cached()
stats = _normalize_stats(raw_stats)
if stats_err and (is_connected or api_mode == 'supabase'):
    st.warning(f"통계 조회 실패: {stats_err}. 0으로 표시합니다.")

# ========== 상단 KPI 카드 그리드 ==========
st.markdown("### 현황 요약")

render_kpi_grid_start()

# 전체 현장
render_kpi_card(
    label="전체 현장",
    value=stats["total_sites"],
    link_text="현장 목록",
    link_url="/현장_목록",
    status_class="info",
)

# 미배정 (위험 표시)
render_kpi_card(
    label="미배정",
    value=stats["unassigned"],
    link_text="미배정 보기",
    link_url="/현장_목록",
    status_class="danger" if stats["unassigned"] > 0 else "",
)

# 배정완료 (성공 표시)
render_kpi_card(
    label="배정완료",
    value=stats["assigned"],
    link_text="배정완료 보기",
    link_url="/현장_목록",
    status_class="success" if stats["assigned"] > 0 else "",
)

# 투입가능 인원
render_kpi_card(
    label="투입가능 인원",
    value=f"{stats['available_personnel']}",
    link_text="인원 상세",
    link_url="/투입가능인원_상세",
    status_class="info",
    sublabel=f"전체 {stats['total_personnel']}명 중",
)

# 사용가능 자격증
render_kpi_card(
    label="사용가능 자격증",
    value=stats["available_certificates"],
    status_class="info",
    sublabel=f"전체 {stats['total_certificates']}개 중",
)

# 전체 자격증
render_kpi_card(
    label="전체 자격증",
    value=stats["total_certificates"],
)

render_kpi_grid_end()

# 미배정 5건 이상 시 경고
if stats["unassigned"] >= 5 and (is_connected or api_mode == 'supabase'):
    st.warning("⚠️ 미배정 현장이 5건 이상입니다. 현장 목록에서 배정을 진행해 주세요.")

st.markdown("---")

# ========== 2단 레이아웃: 좌 현장 현황 / 우 인력·자격증 ==========
left_col, right_col = st.columns(2)

with left_col:
    st.markdown("#### 배정 현황")
    total = stats["total_sites"]
    assigned = stats["assigned"]
    unassigned = stats["unassigned"]

    if total == 0:
        st.info("표시할 현장 데이터가 없습니다.")
    else:
        try:
            import plotly.graph_objects as go

            fig_bar = go.Figure(
                data=[
                    go.Bar(
                        name="배정완료",
                        x=assign_labels,
                        y=assign_values,
                        marker_color=[
                            CHART_COLORS["danger"] if lb == "미배정" else CHART_COLORS["success"]
                            for lb in assign_labels
                        ],
                        text=assign_values,
                        textposition="outside",
                        textfont=dict(size=14, color="#1a1d21", family="Pretendard"),
                    )
                ],
            )
            fig_bar.update_layout(
                title=dict(
                    text="배정 현황",
                    xanchor="center",
                    x=0.5,
                    font=dict(size=12),
                ),
                margin=dict(t=50, b=40, l=40, r=40),
                height=300,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(size=13, color="#495057"),
                xaxis=dict(
                    tickfont=dict(size=13),
                    showgrid=False,
                ),
                yaxis=dict(
                    title="건수",
                    title_font=dict(size=13),
                    gridcolor="#f1f3f5",
                    gridwidth=1,
                ),
            )
            st.plotly_chart(fig_bar, use_container_width=True, key="dashboard_assign_bar")
        except ImportError:
            st.warning("Plotly가 설치되지 않았습니다. `pip install plotly` 실행 후 다시 시도해주세요.")
        except Exception as e:
            st.warning(f"차트를 그리지 못했습니다: {e}")

    st.markdown("#### 현장상태별 현황")
    by_state = {}
    if raw_stats and isinstance(raw_stats, dict) and "sites" in raw_stats:
        by_state = (raw_stats.get("sites") or {}).get("by_state") or {}
    state_order = ["건축허가", "착공예정", "공사 중", "공사 중단", "준공"]
    state_labels = [s for s in state_order if by_state.get(s, 0) > 0]
    state_labels += [k for k in sorted(by_state.keys()) if k not in state_order]
    state_values = [by_state.get(lb, 0) for lb in state_labels]

    # 상태별 색상 매핑
    state_colors = {
        "건축허가": "#6b7280",
        "착공예정": "#3b82f6",
        "공사 중": "#f59e0b",
        "공사 중단": "#ef4444",
        "준공": "#10b981",
    }

    if not state_labels:
        st.caption("현장상태 데이터가 없습니다.")
    else:
        try:
            import plotly.graph_objects as go

            bar_colors = [state_colors.get(s, CHART_COLORS["primary"]) for s in state_labels]

            fig_state = go.Figure(
                data=[
                    go.Bar(
                        x=state_values,
                        y=state_labels,
                        orientation="h",
                        marker_color=bar_colors,
                        text=state_values,
                        textposition="outside",
                        textfont=dict(size=13, color="#1a1d21"),
                    )
                ],
            )
            fig_state.update_layout(
                margin=dict(t=24, b=40, l=100, r=40),
                height=max(220, len(state_labels) * 45),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(size=13, color="#495057"),
                xaxis=dict(
                    title="건수",
                    title_font=dict(size=13),
                    gridcolor="#f1f3f5",
                ),
                yaxis=dict(
                    tickfont=dict(size=13),
                    autorange="reversed",
                ),
            )
            st.plotly_chart(fig_state, use_container_width=True, key="dashboard_state_bar")
        except ImportError:
            st.warning("Plotly가 설치되지 않았습니다.")
        except Exception as e:
            st.warning(f"현장상태 차트 오류: {e}")

with right_col:
    st.markdown("#### 인력 현황")

    # 인력 현황 요약 카드
    st.markdown(f"""
    <div class="info-card">
        <div class="info-row">
            <span class="info-label">전체 인원</span>
            <span class="info-value">{stats['total_personnel']}명</span>
        </div>
        <div class="info-row">
            <span class="info-label">투입가능</span>
            <span class="info-value" style="color: #10b981;">{stats['available_personnel']}명</span>
        </div>
        <div class="info-row">
            <span class="info-label">투입중</span>
            <span class="info-value" style="color: #f59e0b;">{stats.get('deployed_personnel', 0)}명</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 버튼 스타일 링크
    st.markdown("""
    <a href="/투입가능인원_상세" class="nav-btn nav-btn-primary" style="display: inline-block; margin-top: 8px;">
        투입가능인원 상세 보기
    </a>
    """, unsafe_allow_html=True)

    st.markdown("#### 직책별 인원")
    by_role = {}
    if raw_stats and isinstance(raw_stats, dict) and "personnel" in raw_stats:
        by_role = (raw_stats.get("personnel") or {}).get("by_role") or {}
    role_labels = sorted(by_role.keys()) if by_role else []
    role_values = [by_role.get(r, 0) for r in role_labels]

    if not role_labels:
        st.caption("직책별 데이터가 없습니다.")
    else:
        try:
            import plotly.graph_objects as go

            fig_role = go.Figure(
                data=[
                    go.Bar(
                        x=role_labels,
                        y=role_values,
                        marker_color=CHART_COLORS["primary"],
                        text=role_values,
                        textposition="outside",
                        textfont=dict(size=13, color="#1a1d21"),
                    )
                ],
            )
            fig_role.update_layout(
                margin=dict(t=24, b=70, l=40, r=40),
                height=max(250, len(role_labels) * 50),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(size=13, color="#495057"),
                xaxis=dict(
                    tickangle=-30,
                    tickfont=dict(size=12),
                ),
                yaxis=dict(
                    title="인원",
                    title_font=dict(size=13),
                    gridcolor="#f1f3f5",
                ),
            )
            st.plotly_chart(fig_role, use_container_width=True, key="dashboard_role_bar")
        except ImportError:
            st.warning("Plotly가 설치되지 않았습니다.")
        except Exception as e:
            st.warning(f"직책별 차트 오류: {e}")

    st.markdown("#### 자격증 요약")
    st.markdown(f"""
    <div class="info-card">
        <div class="info-row">
            <span class="info-label">전체 자격증</span>
            <span class="info-value">{stats['total_certificates']}개</span>
        </div>
        <div class="info-row">
            <span class="info-label">사용가능</span>
            <span class="info-value" style="color: #10b981;">{stats['available_certificates']}개</span>
        </div>
        <div class="info-row">
            <span class="info-label">사용중</span>
            <span class="info-value" style="color: #f59e0b;">{stats['total_certificates'] - stats['available_certificates']}개</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ========== 하단: 빠른 액션 ==========
st.markdown("---")
st.markdown("### 빠른 액션")

st.markdown("""
<div class="quick-actions">
    <a href="/현장등록" class="quick-action-btn">
        <span class="quick-action-icon">🏗️</span>
        <span class="quick-action-text">현장 등록</span>
    </a>
    <a href="/자격증등록" class="quick-action-btn">
        <span class="quick-action-icon">📜</span>
        <span class="quick-action-text">자격증 등록</span>
    </a>
    <a href="/현장_목록" class="quick-action-btn">
        <span class="quick-action-icon">📋</span>
        <span class="quick-action-text">현장 목록</span>
    </a>
    <a href="/투입가능인원_상세" class="quick-action-btn">
        <span class="quick-action-icon">👷</span>
        <span class="quick-action-text">인원 상세</span>
    </a>
</div>
""", unsafe_allow_html=True)
