"""
대시보드 (개선 버전) - Phase 1 UI/UX 적용
스마트 KPI 카드, 도넛 차트, 빠른 액션, 알림
"""
import os
import streamlit as st
from streamlit_utils.api_client import check_api_connection, get_stats
from streamlit_utils.theme import apply_localhost_theme
from streamlit_utils.components import render_kpi_grid_start, render_kpi_grid_end
from streamlit_utils.advanced_components import (
    render_smart_kpi_card, render_alert_card, render_quick_actions,
    render_stat_grid
)
from streamlit_utils.charts import render_donut_chart, render_bar_chart

apply_localhost_theme()
st.title("📊 대시보드")

def _normalize_stats(raw):
    """Flask API 형식 또는 Supabase 플랫 형식을 통일."""
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
is_connected, error_msg = check_api_connection()

if not is_connected and api_mode != 'supabase':
    st.error(f"**API 연결 실패**: {error_msg}")
    st.info(
        """
    **해결 방법:**
    1. **Flask 서버 실행**: 터미널에서 `python run_api.py` 실행
    2. **환경 변수 확인**: `.env`에 `API_BASE_URL=http://localhost:5000/api` 확인
    3. **Supabase 사용 시**: `API_MODE=supabase` 및 Supabase 키 설정 후 재시도
    """
    )

# 통계 조회
raw_stats, stats_err = get_stats()
stats = _normalize_stats(raw_stats)
if stats_err and (is_connected or api_mode == 'supabase'):
    st.warning(f"통계 조회 실패: {stats_err}. 0으로 표시합니다.")

# ========== 빠른 액션 ==========
st.markdown("### 빠른 액션")
render_quick_actions([
    {"icon": "🚨", "text": "미배정 현장", "url": "/현장_목록"},
    {"icon": "➕", "text": "현장 등록", "url": "/현장등록"},
    {"icon": "📜", "text": "자격증 등록", "url": "/자격증등록"},
    {"icon": "👷", "text": "인원 상세", "url": "/투입가능인원_상세"},
])

st.markdown("---")

# ========== 알림 카드 ==========
if stats["unassigned"] >= 5:
    render_alert_card(
        title="⚠️ 미배정 현장 주의",
        message=f"미배정 현장이 {stats['unassigned']}건 있습니다. 즉시 배정이 필요합니다.",
        alert_type="warning",
        action_url="/현장_목록",
        action_text="지금 배정하기"
    )
elif stats["unassigned"] > 0:
    render_alert_card(
        title="📌 미배정 현장 안내",
        message=f"미배정 현장이 {stats['unassigned']}건 있습니다.",
        alert_type="info",
        action_url="/현장_목록",
        action_text="현장 목록 보기"
    )

# ========== 스마트 KPI 카드 ==========
st.markdown("### 현황 요약")

# 샘플 트렌드 데이터 (실제로는 이전 달 데이터와 비교)
prev_total = max(0, stats["total_sites"] - 5)
prev_unassigned = max(0, stats["unassigned"] + 2)
prev_personnel = max(0, stats["total_personnel"] - 3)

render_kpi_grid_start()

# 전체 현장
trend_sites = stats["total_sites"] - prev_total
render_smart_kpi_card(
    label="전체 현장",
    value=stats["total_sites"],
    trend=f"{trend_sites:+d}" if trend_sites != 0 else "→",
    trend_direction="up" if trend_sites > 0 else "down" if trend_sites < 0 else "neutral",
    sparkline_data=[prev_total, prev_total + 1, prev_total + 3, prev_total + 4, stats["total_sites"]],
    link_url="/현장_목록",
    link_text="상세 보기",
    status="info",
    icon="🏗️"
)

# 미배정 현장
trend_unassigned = stats["unassigned"] - prev_unassigned
render_smart_kpi_card(
    label="미배정 현장",
    value=stats["unassigned"],
    trend=f"{trend_unassigned:+d}" if trend_unassigned != 0 else "→",
    trend_direction="down" if trend_unassigned < 0 else "up" if trend_unassigned > 0 else "neutral",
    sparkline_data=[prev_unassigned, prev_unassigned - 1, stats["unassigned"] + 1, stats["unassigned"], stats["unassigned"]],
    link_url="/현장_목록",
    link_text="배정하기",
    status="danger" if stats["unassigned"] > 0 else "success",
    icon="⚠️" if stats["unassigned"] > 0 else "✅"
)

# 배정완료
render_smart_kpi_card(
    label="배정완료",
    value=stats["assigned"],
    trend=f"+{stats['assigned'] - (prev_total - prev_unassigned)}" if stats["assigned"] > 0 else "→",
    trend_direction="up" if stats["assigned"] > (prev_total - prev_unassigned) else "neutral",
    link_url="/현장_목록",
    link_text="보기",
    status="success",
    icon="✅"
)

# 투입가능 인력
trend_personnel = stats["total_personnel"] - prev_personnel
render_smart_kpi_card(
    label="투입가능 인력",
    value=stats["available_personnel"],
    trend=f"{trend_personnel:+d}" if trend_personnel != 0 else "→",
    trend_direction="up" if trend_personnel > 0 else "down" if trend_personnel < 0 else "neutral",
    sparkline_data=[prev_personnel, prev_personnel + 1, prev_personnel + 2, stats["total_personnel"] - 1, stats["total_personnel"]],
    link_url="/투입가능인원_상세",
    link_text="인원 보기",
    status="info",
    icon="👷",
    sublabel=f"전체 {stats['total_personnel']}명 중"
)

# 사용가능 자격증
cert_usage_rate = int((stats["total_certificates"] - stats["available_certificates"]) / stats["total_certificates"] * 100) if stats["total_certificates"] > 0 else 0
render_smart_kpi_card(
    label="자격증 사용률",
    value=f"{cert_usage_rate}%",
    trend="→",
    trend_direction="neutral",
    status="info",
    icon="📜",
    sublabel=f"사용가능 {stats['available_certificates']}개"
)

# 전체 자격증
render_smart_kpi_card(
    label="전체 자격증",
    value=stats["total_certificates"],
    status="secondary",
    icon="📋"
)

render_kpi_grid_end()

st.markdown("---")

# ========== 통계 그리드 ==========
st.markdown("### 주요 지표")
render_stat_grid([
    ("전체 현장", stats["total_sites"], "개"),
    ("투입 인력", stats["deployed_personnel"], "명"),
    ("사용 자격증", stats["total_certificates"] - stats["available_certificates"], "개"),
    ("배정률", f"{int(stats['assigned'] / stats['total_sites'] * 100) if stats['total_sites'] > 0 else 0}", "%"),
])

st.markdown("---")

# ========== 차트 섹션 ==========
st.markdown("### 상세 분석")

tab1, tab2 = st.tabs(["배정 현황", "통계 차트"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 배정 현황 (도넛 차트)")
        if stats["total_sites"] > 0:
            assignment_rate = int(stats["assigned"] / stats["total_sites"] * 100)
            render_donut_chart(
                labels=["배정완료", "미배정"],
                values=[stats["assigned"], stats["unassigned"]],
                colors=[CHART_COLORS["success"], CHART_COLORS["danger"]],
                title="",
                center_text=f"{assignment_rate}%",
                height=350
            )
        else:
            st.caption("현장 데이터가 없습니다.")
    
    with col2:
        st.markdown("#### 인력 현황")
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
                <span class="info-value" style="color: #3b82f6;">{stats['deployed_personnel']}명</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 자격증 현황")
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

with tab2:
    st.markdown("#### 막대 차트 예시")
    st.caption("실제 데이터 연동 시 현장 상태별, 직책별 통계가 표시됩니다.")
    
    # 샘플 데이터
    render_bar_chart(
        labels=["건축허가", "착공예정", "착공중", "준공"],
        values=[12, 18, 15, 5],
        title="현장 상태별 현황 (샘플)",
        orientation="h",
        color=CHART_COLORS["primary"],
        height=300
    )

st.markdown("---")
st.caption("💡 **Tip**: 새로운 UI/UX 컴포넌트를 확인하려면 사이드바에서 'UI UX 데모' 페이지를 방문하세요.")
