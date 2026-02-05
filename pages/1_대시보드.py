"""
대시보드 - 통계 요약 및 시각화 (임원용)
로컬호스트와 동일한 메트릭 카드 + 배정/현장상태/인력 차트 (API/Supabase 연동)
맵·이모지 없음, 밝은 색상·가독성 중심.
"""
import streamlit as st
from streamlit_utils.api_client import check_api_connection, get_stats
from streamlit_utils.theme import apply_localhost_theme

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


# 차트용 색상 (바탕색 #F8F9FA와 조화, 임원 가독성 유지)
CHART_COLORS_LIGHT = [
    "#e3f2fd",  # 연한 파랑
    "#e8f5e9",  # 연한 녹색
    "#fff3e0",  # 연한 주황
    "#f3e5f5",  # 연한 보라
    "#fce4ec",  # 연한 분홍
    "#f5f5f5",  # 연한 회색
]
# 바탕색과 조화되는 차분한 톤
BAR_COLOR_PRIMARY = "#5a9fd4"     # 차분한 블루 (배정완료, 현장상태)
BAR_COLOR_SECONDARY = "#81c784"   # 차분한 녹색 (직책별 인원)
BAR_COLOR_WARNING = "#ef9a9a"     # 차분한 레드 (미배정)


# API 연결 상태
is_connected, error_msg = check_api_connection()
if not is_connected:
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
else:
    st.success("API 서버 연결 성공")

# 통계 조회
raw_stats, stats_err = get_stats()
stats = _normalize_stats(raw_stats)
if stats_err and is_connected:
    st.warning(f"통계 조회 실패: {stats_err}. 0으로 표시합니다.")

# ----- 빠른 작업 버튼 섹션 -----
st.markdown("### 빠른 작업")
st.markdown('<div style="margin-bottom: 24px;"></div>', unsafe_allow_html=True)

quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)

with quick_col1:
    st.markdown("""
    <div style="background: #fff; padding: 16px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center;">
        <div style="font-size: 32px; margin-bottom: 8px;">📋</div>
        <div style="font-size: 14px; font-weight: 600; color: #1a1d21; margin-bottom: 4px;">현장 목록</div>
        <div style="font-size: 12px; color: #6c757d;">전체 현장 조회 및 관리</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("현장 목록 보기", key="btn_site_list", use_container_width=True):
        st.switch_page("pages/2_현장_목록.py")

with quick_col2:
    st.markdown("""
    <div style="background: #fff; padding: 16px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center;">
        <div style="font-size: 32px; margin-bottom: 8px;">➕</div>
        <div style="font-size: 14px; font-weight: 600; color: #1a1d21; margin-bottom: 4px;">현장 등록</div>
        <div style="font-size: 12px; color: #6c757d;">새로운 현장 추가</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("현장 등록하기", key="btn_site_register", use_container_width=True):
        st.switch_page("pages/3_현장등록.py")

with quick_col3:
    st.markdown("""
    <div style="background: #fff; padding: 16px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center;">
        <div style="font-size: 32px; margin-bottom: 8px;">🎓</div>
        <div style="font-size: 14px; font-weight: 600; color: #1a1d21; margin-bottom: 4px;">자격증 등록</div>
        <div style="font-size: 12px; color: #6c757d;">새로운 자격증 추가</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("자격증 등록하기", key="btn_cert_register", use_container_width=True):
        st.switch_page("pages/4_자격증등록.py")

with quick_col4:
    st.markdown("""
    <div style="background: #fff; padding: 16px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center;">
        <div style="font-size: 32px; margin-bottom: 8px;">👥</div>
        <div style="font-size: 14px; font-weight: 600; color: #1a1d21; margin-bottom: 4px;">투입가능인원</div>
        <div style="font-size: 12px; color: #6c757d;">인력 현황 상세 조회</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("인원 조회하기", key="btn_personnel", use_container_width=True):
        st.switch_page("pages/8_투입가능인원_상세.py")

st.markdown('<div style="margin: 32px 0; border-top: 2px solid #e9ecef;"></div>', unsafe_allow_html=True)

# ----- 상단 KPI (한 줄 4~6개) -----
st.markdown("### 현황 요약")
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(label="전체 현장", value=stats["total_sites"])

with col2:
    st.metric(label="미배정", value=stats["unassigned"], delta=f"-{stats['unassigned']}" if stats['unassigned'] > 0 else None, delta_color="inverse")

with col3:
    st.metric(label="배정완료", value=stats["assigned"], delta=f"+{stats['assigned']}" if stats['assigned'] > 0 else None)

with col4:
    st.metric(
        label="투입가능 인원",
        value=f"{stats['available_personnel']} / {stats['total_personnel']}",
        delta=None,
    )

with col5:
    st.metric(label="사용가능 자격증", value=stats["available_certificates"])

with col6:
    st.metric(label="전체 자격증", value=stats["total_certificates"])

st.markdown('<div style="margin: 32px 0; border-top: 2px solid #e9ecef;"></div>', unsafe_allow_html=True)

# ----- 2단: 좌 현장 현황 / 우 인력·자격증 -----
left_col, right_col = st.columns(2)

with left_col:
    st.markdown("#### 📊 배정 현황")
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
                        x=["배정완료"],
                        y=[assigned],
                        marker_color=BAR_COLOR_SECONDARY,
                        text=[assigned],
                        textposition="outside",
                    ),
                    go.Bar(
                        name="미배정",
                        x=["미배정"],
                        y=[unassigned],
                        marker_color=BAR_COLOR_WARNING,
                        text=[unassigned],
                        textposition="outside",
                    ),
                ],
                layout=go.Layout(
                    barmode="group",
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02),
                    margin=dict(t=40, b=40, l=40, r=40),
                    height=280,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(size=13),
                    xaxis=dict(tickfont=dict(size=13)),
                    yaxis=dict(title="건수", title_font=dict(size=13)),
                ),
            )
            st.plotly_chart(fig_bar, use_container_width=True, key="dashboard_assign_bar")
        except Exception as e:
            st.warning(f"차트를 그리지 못했습니다: {e}")

    st.markdown('<div style="margin: 24px 0;"></div>', unsafe_allow_html=True)
    st.markdown("#### 🏗️ 현장상태별 현황")
    by_state = {}
    if raw_stats and isinstance(raw_stats, dict) and "sites" in raw_stats:
        by_state = (raw_stats.get("sites") or {}).get("by_state") or {}
    state_order = ["건축허가", "착공예정", "공사 중", "공사 중단", "준공"]
    state_labels = [s for s in state_order if by_state.get(s, 0) > 0]
    state_labels += [k for k in sorted(by_state.keys()) if k not in state_order]
    state_values = [by_state.get(lb, 0) for lb in state_labels]

    if not state_labels:
        st.caption("현장상태 데이터가 없습니다.")
    else:
        try:
            import plotly.graph_objects as go

            fig_state = go.Figure(
                data=[
                    go.Bar(
                        x=state_values,
                        y=state_labels,
                        orientation="h",
                        marker_color=BAR_COLOR_PRIMARY,
                        text=state_values,
                        textposition="outside",
                    )
                ],
                layout=go.Layout(
                    margin=dict(t=24, b=40, l=80, r=40),
                    height=max(220, len(state_labels) * 36),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(size=13),
                    xaxis=dict(title="건수", title_font=dict(size=13)),
                    yaxis=dict(tickfont=dict(size=13)),
                ),
            )
            st.plotly_chart(fig_state, use_container_width=True, key="dashboard_state_bar")
        except Exception as e:
            st.warning(f"현장상태 차트 오류: {e}")

with right_col:
    st.markdown("#### 👥 인력 현황")
    st.metric(
        label="전체 / 투입가능 / 투입중",
        value=f"{stats['total_personnel']} / {stats['available_personnel']} / {stats.get('deployed_personnel', 0)}",
    )

    st.markdown('<div style="margin: 24px 0;"></div>', unsafe_allow_html=True)
    st.markdown("#### 👔 직책별 인원")
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
                        marker_color=BAR_COLOR_SECONDARY,
                        text=role_values,
                        textposition="outside",
                    )
                ],
                layout=go.Layout(
                    margin=dict(t=24, b=60, l=40, r=40),
                    height=max(220, len(role_labels) * 40),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(size=13),
                    xaxis=dict(tickangle=-30, tickfont=dict(size=12)),
                    yaxis=dict(title="인원", title_font=dict(size=13)),
                ),
            )
            st.plotly_chart(fig_role, use_container_width=True, key="dashboard_role_bar")
        except Exception as e:
            st.warning(f"직책별 차트 오류: {e}")

    st.markdown('<div style="margin: 24px 0;"></div>', unsafe_allow_html=True)
    st.markdown("#### 🎓 자격증 요약")
    st.caption(f"사용가능 {stats['available_certificates']} / 전체 {stats['total_certificates']}")

# 미배정 5건 이상 시 강조
if stats["unassigned"] >= 5 and is_connected:
    st.warning("미배정 현장이 5건 이상입니다. 현장 목록에서 배정을 진행해 주세요.")
