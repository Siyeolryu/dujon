"""
대시보드 - 통계 요약 및 시각화 (임원용)
로컬호스트와 동일한 메트릭 카드 + 배정/현장상태/인력 차트 (API/Supabase 연동)
맵·이모지 없음, 밝은 색상·가독성 중심.
"""
import streamlit as st
from streamlit_utils.api_client import (
    check_api_connection,
    get_stats,
    get_sites,
    get_personnel,
    get_certificates,
    assign_site
)
from streamlit_utils.theme import apply_localhost_theme

apply_localhost_theme()

# 커스텀 CSS 스타일 추가
st.markdown("""
<style>
    /* 섹션 헤더 스타일 */
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin: 20px 0 15px 0;
        font-size: 18px;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .section-header-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin: 20px 0 15px 0;
        font-size: 18px;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .section-header-blue {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin: 20px 0 15px 0;
        font-size: 18px;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .section-header-orange {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin: 20px 0 15px 0;
        font-size: 18px;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .section-header-teal {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin: 20px 0 15px 0;
        font-size: 18px;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* KPI 카드 스타일 개선 */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
        color: #1f77b4;
    }

    /* KPI 카드 컨테이너 정렬 — 안정적인 min-height 방식 */
    [data-testid="stMetric"] {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 16px 12px 8px 12px;
        min-height: 120px;
    }

    /* KPI 버튼 스타일 통일 */
    .stButton button {
        width: 100%;
        margin-top: 8px;
        font-size: 13px;
        padding: 6px 12px;
    }

    /* 차트 컨테이너 */
    .chart-container {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    /* 배정 섹션 스타일 */
    .stExpander {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin-bottom: 10px;
    }

    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 8px 20px;
        transition: all 0.3s ease;
    }

    .stButton button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 대시보드")


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


# 차트용 밝은 색상 (임원 가독성)
CHART_COLORS_LIGHT = [
    "#e3f2fd",  # 연한 파랑
    "#e8f5e9",  # 연한 녹색
    "#fff3e0",  # 연한 주황
    "#f3e5f5",  # 연한 보라
    "#fce4ec",  # 연한 분홍
    "#f5f5f5",  # 연한 회색
]
BAR_COLOR_PRIMARY = "#90caf9"
BAR_COLOR_SECONDARY = "#a5d6a7"


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

# ----- 빠른 배정 섹션 -----
if stats["unassigned"] > 0 and is_connected:
    st.markdown('<div class="section-header">⚡ 빠른 배정</div>', unsafe_allow_html=True)

    # 미배정 현장 가져오기
    unassigned_sites, sites_err = get_sites(status='미배정', limit=10)

    if sites_err:
        st.error(f"미배정 현장 조회 실패: {sites_err}")
    elif not unassigned_sites:
        st.info("미배정 현장이 없습니다.")
    else:
        # 투입 가능한 소장 목록
        available_personnel, personnel_err = get_personnel(status='투입가능')
        if personnel_err:
            st.warning(f"인력 목록 조회 실패: {personnel_err}")
            available_personnel = []

        # 사용 가능한 자격증 목록
        available_certificates, cert_err = get_certificates(available=True)
        if cert_err:
            st.warning(f"자격증 목록 조회 실패: {cert_err}")
            available_certificates = []

        # 소장만 필터링 (직책이 '소장'인 인력)
        managers = [p for p in available_personnel if p.get('직책') == '소장']

        if not managers:
            st.warning("투입 가능한 소장이 없습니다. 인력 목록에서 소장을 추가해주세요.")
        elif not available_certificates:
            st.warning("사용 가능한 자격증이 없습니다.")
        else:
            st.caption(f"🔹 미배정 현장 {len(unassigned_sites)}개 중 최대 10개를 표시합니다.")

            # 현장 목록을 테이블 형태로 표시
            for idx, site in enumerate(unassigned_sites):
                site_id = site.get('현장ID')
                site_name = site.get('현장명', '(이름 없음)')
                site_state = site.get('현장상태', '-')
                address = site.get('주소', '-')

                with st.expander(f"🏗️ {site_name} ({site_state})"):
                    col_info, col_assign = st.columns([2, 1])

                    with col_info:
                        st.markdown(f"**현장 정보**")
                        st.markdown(f"- 현장ID: `{site_id}`")
                        st.markdown(f"- 주소: {address}")
                        st.markdown(f"- 상태: {site_state}")

                    with col_assign:
                        st.markdown("**배정 설정**")

                        # 소장 선택
                        manager_options = {
                            f"{p.get('인력ID')} - {p.get('이름', '(이름없음)')}": p.get('인력ID')
                            for p in managers
                        }
                        selected_manager_key = st.selectbox(
                            "소장 선택",
                            options=list(manager_options.keys()),
                            key=f"manager_{site_id}_{idx}"
                        )
                        selected_manager_id = manager_options[selected_manager_key]

                        # 자격증 선택
                        cert_options = {
                            f"{c.get('자격증ID')} - {c.get('자격증명', '(이름없음)')} ({c.get('소유자', '-')})": c.get('자격증ID')
                            for c in available_certificates
                        }
                        selected_cert_key = st.selectbox(
                            "자격증 선택",
                            options=list(cert_options.keys()),
                            key=f"cert_{site_id}_{idx}"
                        )
                        selected_cert_id = cert_options[selected_cert_key]

                        # 배정 버튼
                        if st.button("✅ 배정하기", key=f"assign_btn_{site_id}_{idx}", type="primary"):
                            with st.spinner("배정 중..."):
                                result, error = assign_site(
                                    site_id=site_id,
                                    manager_id=selected_manager_id,
                                    certificate_id=selected_cert_id
                                )

                                if error:
                                    st.error(f"배정 실패: {error}")
                                else:
                                    st.success(f"✅ {site_name}이(가) 성공적으로 배정되었습니다!")
                                    st.balloons()
                                    # 대시보드 새로고침
                                    st.rerun()

    st.markdown("---")

# ----- 상단 KPI (한 줄 4~6개) -----
st.markdown('<div class="section-header">📌 현황 요약</div>', unsafe_allow_html=True)
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(label="전체 현장", value=stats["total_sites"])
    if st.button("📋 현장 목록", key="nav_sites_list", use_container_width=True):
        st.switch_page("pages/2_현장_목록.py")

with col2:
    st.metric(label="미배정", value=stats["unassigned"])
    if st.button("🔍 미배정 보기", key="link_unassigned", use_container_width=True):
        st.query_params["status"] = "미배정"
        st.switch_page("pages/2_현장_목록.py")

with col3:
    st.metric(label="배정완료", value=stats["assigned"])
    if st.button("✅ 배정완료 보기", key="link_assigned", use_container_width=True):
        st.query_params["status"] = "배정완료"
        st.switch_page("pages/2_현장_목록.py")

with col4:
    st.metric(
        label="투입가능 인원",
        value=f"{stats['available_personnel']} / {stats['total_personnel']}",
        delta=None,
    )
    if st.button("👥 인력 상세", key="nav_personnel", use_container_width=True):
        st.switch_page("pages/8_투입가능인원_상세.py")

with col5:
    st.metric(label="사용가능 자격증", value=stats["available_certificates"])

with col6:
    st.metric(label="전체 자격증", value=stats["total_certificates"])

# ----- 탭으로 구분된 상세 뷰 -----
st.markdown("---")
st.markdown('<div class="section-header">📈 상세 분석</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🏗️ 현장 현황", "👥 인력 현황", "📊 종합 뷰"])

# 탭 1: 현장 현황
with tab1:
    col_assign, col_state = st.columns(2)

    with col_assign:
        st.markdown("### 배정 현황")
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
                            marker_color="#a5d6a7",
                            text=[assigned],
                            textposition="outside",
                        ),
                        go.Bar(
                            name="미배정",
                            x=["미배정"],
                            y=[unassigned],
                            marker_color="#ef9a9a",
                            text=[unassigned],
                            textposition="outside",
                        ),
                    ],
                    layout=go.Layout(
                        barmode="group",
                        showlegend=True,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02),
                        margin=dict(t=40, b=40, l=40, r=40),
                        height=350,
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(size=13),
                        xaxis=dict(tickfont=dict(size=13)),
                        yaxis=dict(title="건수", title_font=dict(size=13)),
                    ),
                )
                st.plotly_chart(fig_bar, use_container_width=True, key="dashboard_assign_bar_tab")
            except Exception as e:
                st.warning(f"차트를 그리지 못했습니다: {e}")

    with col_state:
        st.markdown("### 현장상태별 현황")
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
                        margin=dict(t=24, b=40, l=100, r=40),
                        height=max(280, len(state_labels) * 50),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(size=13),
                        xaxis=dict(title="건수", title_font=dict(size=13)),
                        yaxis=dict(tickfont=dict(size=13)),
                    ),
                )
                st.plotly_chart(fig_state, use_container_width=True, key="dashboard_state_bar_tab")
            except Exception as e:
                st.warning(f"현장상태 차트 오류: {e}")

# 탭 2: 인력 현황
with tab2:
    col_personnel, col_role = st.columns(2)

    with col_personnel:
        st.markdown("### 인력 요약")
        st.metric(
            label="전체 / 투입가능 / 투입중",
            value=f"{stats['total_personnel']} / {stats['available_personnel']} / {stats.get('deployed_personnel', 0)}",
        )
        if st.button("👥 투입가능인원 상세", key="nav_personnel_tab2", use_container_width=True):
            st.switch_page("pages/8_투입가능인원_상세.py")

        st.markdown("### 자격증 요약")
        col_cert1, col_cert2 = st.columns(2)
        with col_cert1:
            st.metric(label="사용가능", value=stats['available_certificates'])
        with col_cert2:
            st.metric(label="전체", value=stats['total_certificates'])

    with col_role:
        st.markdown("### 직책별 인원")
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
                        margin=dict(t=24, b=80, l=40, r=40),
                        height=max(280, len(role_labels) * 50),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(size=13),
                        xaxis=dict(tickangle=-30, tickfont=dict(size=12)),
                        yaxis=dict(title="인원", title_font=dict(size=13)),
                    ),
                )
                st.plotly_chart(fig_role, use_container_width=True, key="dashboard_role_bar_tab")
            except Exception as e:
                st.warning(f"직책별 차트 오류: {e}")

# 탭 3: 종합 뷰 (기존 레이아웃)
with tab3:
    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown('<div class="section-header-green">🏗️ 배정 현황</div>', unsafe_allow_html=True)
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
                            marker_color="#a5d6a7",
                            text=[assigned],
                            textposition="outside",
                        ),
                        go.Bar(
                            name="미배정",
                            x=["미배정"],
                            y=[unassigned],
                            marker_color="#ef9a9a",
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

        st.markdown('<div class="section-header-blue">📊 현장상태별 현황</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="section-header-orange">👥 인력 현황</div>', unsafe_allow_html=True)
        st.metric(
            label="전체 / 투입가능 / 투입중",
            value=f"{stats['total_personnel']} / {stats['available_personnel']} / {stats.get('deployed_personnel', 0)}",
        )
        if st.button("👥 투입가능인원 상세", key="nav_personnel_tab3", use_container_width=True):
            st.switch_page("pages/8_투입가능인원_상세.py")
