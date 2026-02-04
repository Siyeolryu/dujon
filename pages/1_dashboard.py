"""
대시보드 - 통계 요약 및 시각화
로컬호스트와 동일한 메트릭 카드 + 배정 현황 차트 (API/Supabase 연동)
"""
import streamlit as st
from streamlit_utils.api_client import check_api_connection, get_stats
from streamlit_utils.theme import apply_localhost_theme, render_top_nav

apply_localhost_theme()
render_top_nav(current_page="1_dashboard")
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
            "total_certificates": certs.get("total", 0),
            "available_certificates": certs.get("available", 0),
        }
    return {
        "total_sites": raw.get("total_sites", 0),
        "unassigned": raw.get("unassigned_sites", 0),
        "assigned": raw.get("assigned_sites", 0),
        "total_personnel": raw.get("total_personnel", 0),
        "available_personnel": raw.get("available_personnel", 0),
        "total_certificates": raw.get("total_certificates", 0),
        "available_certificates": raw.get("available_certificates", 0),
    }


# API 연결 상태
is_connected, error_msg = check_api_connection()
if not is_connected:
    st.error(f"❌ **API 연결 실패**: {error_msg}")
    st.info(
        """
    💡 **해결 방법:**
    1. **Flask 서버 실행**: 터미널에서 `python run_api.py` 실행
    2. **환경 변수 확인**: `.env`에 `API_BASE_URL=http://localhost:5000/api` 확인
    3. **Supabase 사용 시**: `API_MODE=supabase` 및 Supabase 키 설정 후 재시도
    
    ⚠️ 아래 대시보드는 데이터 없음(0)으로 표시됩니다.
    """
    )
else:
    st.success("✅ API 서버 연결 성공")

# 통계 조회
raw_stats, stats_err = get_stats()
stats = _normalize_stats(raw_stats)
if stats_err and is_connected:
    st.warning(f"통계 조회 실패: {stats_err}. 0으로 표시합니다.")

# ----- 로컬호스트와 동일한 4개 메트릭 카드 -----
st.markdown("### 현황 요약")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="전체 현장", value=stats["total_sites"])

with col2:
    st.metric(label="미배정 현장", value=stats["unassigned"])

with col3:
    st.metric(label="배정완료", value=stats["assigned"])

with col4:
    st.metric(
        label="투입가능 인원",
        value=f"{stats['available_personnel']} / {stats['total_personnel']}",
        delta=None,
    )
    st.caption(f"전체 {stats['total_personnel']}명 · 투입가능 {stats['available_personnel']}명")

# 사용가능 자격증 (로컬 명세서에 있던 5번째 항목)
st.markdown("### 자격증")
c1, c2, _ = st.columns([1, 1, 2])
with c1:
    st.metric(label="사용가능 자격증", value=stats["available_certificates"])
with c2:
    st.metric(label="전체 자격증", value=stats["total_certificates"])

# ----- 배정 현황 도넛 차트 (로컬 dashboard.js renderChart와 동일) -----
st.markdown("### 배정 현황")
total = stats["total_sites"]
assigned = stats["assigned"]
unassigned = stats["unassigned"]

if total == 0:
    st.info("표시할 현장 데이터가 없습니다.")
else:
    try:
        import plotly.graph_objects as go

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=["배정완료", "미배정"],
                    values=[assigned, unassigned],
                    hole=0.6,
                    marker_colors=["#c3e6cb", "#f5c6cb"],
                    textinfo="label+value",
                    textposition="outside",
                    hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
                )
            ],
            layout=go.Layout(
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
                margin=dict(t=40, b=40, l=40, r=40),
                height=320,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(size=13),
            ),
        )
        assigned_pct = (assigned / total * 100) if total else 0
        fig.add_annotation(
            text=f"전체 {total}<br>배정률 {assigned_pct:.1f}%",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14),
        )
        st.plotly_chart(fig, use_container_width=True, key="dashboard_pie")
    except Exception as e:
        st.warning(f"차트를 그리지 못했습니다: {e}")
        st.caption(f"배정완료 {assigned} · 미배정 {unassigned} · 배정률 {assigned/total*100:.1f}%" if total else "")

# 미배정 5건 이상 시 강조 (로컬 highlight-warning)
if stats["unassigned"] >= 5 and is_connected:
    st.warning("⚠️ 미배정 현장이 5건 이상입니다. 현장 목록에서 배정을 진행해 주세요.")
