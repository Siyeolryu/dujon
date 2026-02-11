"""
UI/UX 데모 페이지 - 새로운 컴포넌트 쇼케이스
Phase 1 구현: 스마트 KPI 카드, 차트, 빠른 액션
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from streamlit_utils.theme import apply_localhost_theme
from streamlit_utils.advanced_components import (
    render_smart_kpi_card, render_progress_card, render_alert_card,
    render_quick_actions, render_metric_comparison, render_stat_grid,
    render_info_card, render_empty_state
)
from streamlit_utils.charts import (
    render_donut_chart, render_bar_chart, render_line_chart, render_timeline_chart
)
from datetime import datetime, timedelta

apply_localhost_theme()

st.title("🎨 UI/UX 컴포넌트 데모")
st.markdown("**Phase 1 구현**: Modern Minimal Premium 디자인 컴포넌트")

# ========== 빠른 액션 ==========
st.markdown("---")
st.markdown("### 빠른 액션")

render_quick_actions([
    {"icon": "🚨", "text": "미배정 현장", "url": "/현장_목록"},
    {"icon": "➕", "text": "현장 등록", "url": "/현장등록"},
    {"icon": "📊", "text": "통계 보기", "url": "/대시보드"},
    {"icon": "🔍", "text": "통합 검색", "url": "#"},
])

# ========== 알림 카드 ==========
st.markdown("---")
st.markdown("### 알림 카드")

col1, col2 = st.columns(2)

with col1:
    render_alert_card(
        title="⚠️ 미배정 현장 5건",
        message="즉시 배정이 필요한 현장이 있습니다.",
        alert_type="warning",
        action_url="/현장_목록",
        action_text="지금 배정하기"
    )

with col2:
    render_alert_card(
        title="✅ 이번 달 목표 달성",
        message="모든 현장 배정이 완료되었습니다!",
        alert_type="success",
    )

# ========== 스마트 KPI 카드 ==========
st.markdown("---")
st.markdown("### 스마트 KPI 카드 (트렌드 & 스파크라인)")

cols = st.columns(4)

with cols[0]:
    render_smart_kpi_card(
        label="전체 현장",
        value=50,
        trend="+5",
        trend_direction="up",
        sparkline_data=[45, 47, 46, 48, 50],
        link_url="/현장_목록",
        link_text="상세 보기",
        status="info",
        icon="🏗️"
    )

with cols[1]:
    render_smart_kpi_card(
        label="미배정 현장",
        value=5,
        trend="-2",
        trend_direction="down",
        sparkline_data=[7, 6, 7, 5, 5],
        link_url="/현장_목록",
        link_text="배정하기",
        status="danger",
        icon="⚠️"
    )

with cols[2]:
    render_smart_kpi_card(
        label="투입 인력",
        value=45,
        trend="+3",
        trend_direction="up",
        sparkline_data=[42, 43, 44, 44, 45],
        link_url="/투입가능인원_상세",
        link_text="인원 보기",
        status="success",
        icon="👷"
    )

with cols[3]:
    render_smart_kpi_card(
        label="자격증 사용률",
        value="85%",
        trend="→",
        trend_direction="neutral",
        sparkline_data=[82, 83, 85, 84, 85],
        status="info",
        icon="📜"
    )

# ========== 진행률 카드 ==========
st.markdown("---")
st.markdown("### 진행률 카드")

cols = st.columns(3)

with cols[0]:
    render_progress_card(
        label="배정 완료율",
        current=45,
        total=50,
        status="success"
    )

with cols[1]:
    render_progress_card(
        label="자격증 사용률",
        current=34,
        total=40,
        status="info"
    )

with cols[2]:
    render_progress_card(
        label="이번 달 착공",
        current=8,
        total=12,
        status="warning"
    )

# ========== 통계 그리드 ==========
st.markdown("---")
st.markdown("### 통계 그리드")

render_stat_grid([
    ("전체 현장", 50, "개"),
    ("투입 인력", 45, "명"),
    ("사용 자격증", 34, "개"),
    ("이번 달 착공", 8, "건"),
])

# ========== 차트 ==========
st.markdown("---")
st.markdown("### 차트 시각화")

tab1, tab2, tab3, tab4 = st.tabs(["도넛 차트", "막대 차트", "라인 차트", "타임라인"])

with tab1:
    st.markdown("#### 배정 현황 (도넛 차트)")
    render_donut_chart(
        labels=["배정완료", "미배정"],
        values=[45, 5],
        colors=["#10b981", "#ef4444"],
        title="",
        center_text="90%",
        height=350
    )

with tab2:
    st.markdown("#### 현장 상태별 현황")
    render_bar_chart(
        labels=["건축허가", "착공예정", "착공중", "준공"],
        values=[12, 18, 15, 5],
        title="",
        orientation="h",
        color="#3b82f6",
        height=300
    )

with tab3:
    st.markdown("#### 월별 현장 추이")
    render_line_chart(
        x_data=["1월", "2월", "3월", "4월", "5월", "6월"],
        y_data=[42, 45, 47, 48, 49, 50],
        title="",
        x_label="월",
        y_label="현장 수",
        color="#10b981",
        fill=True,
        height=300
    )

with tab4:
    st.markdown("#### 현장 타임라인")
    
    # 샘플 타임라인 데이터
    today = datetime.now().date()
    timeline_data = [
        {
            "name": "평택 푸르지오",
            "start": today - timedelta(days=30),
            "end": today + timedelta(days=365),
            "status": "착공중"
        },
        {
            "name": "수원 힐스테이트",
            "start": today + timedelta(days=15),
            "end": today + timedelta(days=400),
            "status": "착공예정"
        },
        {
            "name": "용인 동백 자이",
            "start": today - timedelta(days=60),
            "end": today - timedelta(days=10),
            "status": "준공"
        },
        {
            "name": "성남 판교 센트럴",
            "start": today - timedelta(days=90),
            "end": today + timedelta(days=180),
            "status": "착공중"
        },
    ]
    
    render_timeline_chart(
        data=timeline_data,
        title="",
        height=350
    )

# ========== 정보 카드 ==========
st.markdown("---")
st.markdown("### 정보 카드")

col1, col2 = st.columns(2)

with col1:
    render_info_card(
        title="현장 정보",
        items=[
            ("현장명", "평택 푸르지오"),
            ("회사구분", "더존종합건설"),
            ("현장상태", "착공중"),
            ("담당소장", "김현장"),
        ],
        footer_text="상세 정보 보기 →",
        footer_url="/현장_목록"
    )

with col2:
    render_info_card(
        title="인력 현황",
        items=[
            ("전체 인원", "50명"),
            ("투입가능", "15명"),
            ("투입중", "35명"),
            ("소장", "10명"),
        ],
        footer_text="인원 상세 보기 →",
        footer_url="/투입가능인원_상세"
    )

# ========== 빈 상태 ==========
st.markdown("---")
st.markdown("### 빈 상태 (Empty State)")

render_empty_state(
    icon="📭",
    title="데이터가 없습니다",
    message="아직 등록된 현장이 없습니다. 새 현장을 등록해보세요.",
    action_text="현장 등록하기",
    action_url="/현장등록"
)

# ========== 메트릭 비교 ==========
st.markdown("---")
st.markdown("### 메트릭 비교 (전월 대비)")

cols = st.columns(4)

with cols[0]:
    render_metric_comparison(
        label="전체 현장",
        current_value=50,
        previous_value=45,
        format_str="{:.0f}",
        unit="개"
    )

with cols[1]:
    render_metric_comparison(
        label="미배정 현장",
        current_value=5,
        previous_value=7,
        format_str="{:.0f}",
        unit="개"
    )

with cols[2]:
    render_metric_comparison(
        label="투입 인력",
        current_value=45,
        previous_value=42,
        format_str="{:.0f}",
        unit="명"
    )

with cols[3]:
    render_metric_comparison(
        label="자격증 사용률",
        current_value=85,
        previous_value=82,
        format_str="{:.1f}",
        unit="%"
    )

# ========== 푸터 ==========
st.markdown("---")
st.markdown("""
### 📝 구현 완료 항목

✅ **스마트 KPI 카드**: 트렌드 표시, 스파크라인, 아이콘  
✅ **진행률 카드**: 프로그레스 바, 퍼센트 표시  
✅ **알림 카드**: 4가지 타입 (warning, danger, info, success)  
✅ **빠른 액션**: 아이콘 버튼 그리드  
✅ **차트**: 도넛, 막대, 라인, 타임라인  
✅ **정보 카드**: 키-값 쌍 표시  
✅ **빈 상태**: Empty state UI  
✅ **메트릭 비교**: 전월 대비 증감률  

### 🚀 다음 단계

이 컴포넌트들을 기존 페이지에 통합:
1. 대시보드 - 스마트 KPI + 도넛 차트
2. 현장 목록 - 알림 카드 + 빠른 액션
3. 현장 등록 - 진행률 표시
4. 투입가능인원 - 정보 카드 + 통계 그리드
""")
