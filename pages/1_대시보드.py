"""
대시보드 - 임원용 현황 관리
배정 관리 중심 설계: 미배정/배정완료, 소장 관리, 현장 현황
"""
import os
import streamlit as st
from streamlit_utils.cached_api import (
    check_api_connection_cached,
    get_stats_cached,
    get_personnel_cached,
)

from streamlit_utils.theme import apply_localhost_theme
from streamlit_utils.components import (
    render_kpi_card,
    render_kpi_grid_start,
    render_kpi_grid_end,
)

apply_localhost_theme()
st.title("📊 임원 대시보드")
st.caption("현장 배정 및 소장 관리 현황")


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

# ========== 상단 KPI 카드 그리드 (핵심 지표) ==========
st.markdown("### 📌 핵심 현황")

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
    link_text="즉시 배정",
    link_url="/현장_목록?status=미배정",
    status_class="danger" if stats["unassigned"] > 0 else "success",
)

# 배정완료 (성공 표시)
render_kpi_card(
    label="배정완료",
    value=stats["assigned"],
    link_text="배정 현황",
    link_url="/현장_목록?status=배정완료",
    status_class="success" if stats["assigned"] > 0 else "",
)

# 투입가능 인원
render_kpi_card(
    label="투입가능 인원",
    value=f"{stats['available_personnel']}명",
    link_text="인원 상세",
    link_url="/투입가능인원_상세",
    status_class="info",
    sublabel=f"전체 {stats['total_personnel']}명 중",
)

render_kpi_grid_end()

# 미배정 5건 이상 시 경고
if stats["unassigned"] >= 5 and (is_connected or api_mode == 'supabase'):
    st.error("🚨 **긴급**: 미배정 현장이 5건 이상입니다. 즉시 배정이 필요합니다!")
    st.markdown("[현장 목록에서 배정하기](/현장_목록?status=미배정)")

st.markdown("---")

# ========== 병렬 3단 레이아웃: 배정 현황 / 소장 관리 / 현장 현황 ==========
st.markdown("### 📊 상세 현황")

col_assignment, col_directors, col_sites = st.columns(3)

# ==================== 1. 배정 현황 섹션 ====================
with col_assignment:
    st.markdown("#### 배정 현황")
    
    total = stats["total_sites"]
    assigned = stats["assigned"]
    unassigned = stats["unassigned"]
    
    # 배정률 계산
    assignment_rate = int(assigned / total * 100) if total > 0 else 0
    
    # 요약 카드
    st.markdown(f"""
    <div class="info-card">
        <div class="info-row">
            <span class="info-label">배정률</span>
            <span class="info-value" style="color: {'#10b981' if assignment_rate >= 80 else '#f59e0b' if assignment_rate >= 50 else '#ef4444'}; font-size: 28px; font-weight: 800;">{assignment_rate}%</span>
        </div>
        <div class="info-row">
            <span class="info-label">배정완료</span>
            <span class="info-value" style="color: #10b981;">{assigned}개</span>
        </div>
        <div class="info-row">
            <span class="info-label">미배정</span>
            <span class="info-value" style="color: #ef4444;">{unassigned}개</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 도넛 차트
    if total > 0:
        try:
            import plotly.graph_objects as go
            
            fig_donut = go.Figure(
                data=[
                    go.Pie(
                        labels=["배정완료", "미배정"],
                        values=[assigned, unassigned],
                        hole=0.5,
                        marker=dict(
                            colors=[CHART_COLORS["success"], CHART_COLORS["danger"]]
                        ),
                        textinfo="label+percent",
                        textfont=dict(size=12),
                        hovertemplate="<b>%{label}</b><br>%{value}개<br>%{percent}<extra></extra>",
                    )
                ],
            )
            fig_donut.update_layout(
                annotations=[
                    dict(
                        text=f"{assignment_rate}%",
                        x=0.5,
                        y=0.5,
                        font_size=24,
                        font_color="#1a1d21",
                        font_weight=700,
                        showarrow=False,
                    )
                ],
                height=280,
                margin=dict(t=20, b=20, l=20, r=20),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.15,
                    xanchor="center",
                    x=0.5,
                ),
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_donut, use_container_width=True, key="dashboard_assignment_donut")
        except ImportError:
            st.warning("Plotly가 설치되지 않았습니다.")
        except Exception as e:
            st.warning(f"차트 오류: {e}")
    else:
        st.info("현장 데이터가 없습니다.")
    
    # 빠른 액션
    st.markdown("""
    <a href="/현장_목록" class="nav-btn nav-btn-primary" style="display: inline-block; margin-top: 12px; width: 100%;">
        현장 목록 보기
    </a>
    """, unsafe_allow_html=True)

# ==================== 2. 소장 관리 섹션 ====================
with col_directors:
    st.markdown("#### 소장 관리")
    
    # 인력 데이터 가져오기
    personnel, pers_err = get_personnel_cached()
    
    if pers_err:
        st.error(f"인력 데이터 조회 실패: {pers_err}")
        directors = []
    else:
        # 소장만 필터링
        directors = [p for p in (personnel or []) if p.get('직책') == '소장']
    
    # 상태별 집계
    available_directors = [d for d in directors if d.get('현재상태') == '투입가능']
    deployed_directors = [d for d in directors if d.get('현재상태') == '투입중']
    
    total_directors = len(directors)
    available_count = len(available_directors)
    deployed_count = len(deployed_directors)
    
    # 요약 카드
    st.markdown(f"""
    <div class="info-card">
        <div class="info-row">
            <span class="info-label">전체 소장</span>
            <span class="info-value">{total_directors}명</span>
        </div>
        <div class="info-row">
            <span class="info-label">배정가능</span>
            <span class="info-value" style="color: #10b981;">{available_count}명</span>
        </div>
        <div class="info-row">
            <span class="info-label">배정중</span>
            <span class="info-value" style="color: #3b82f6;">{deployed_count}명</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 소장별 담당 현장 수 막대 차트
    if directors:
        # 소장별 담당 현장 수 계산
        director_data = []
        for d in directors:
            name = d.get('성명', '이름없음')
            workload = d.get('현재담당현장수', 0)
            director_data.append({
                'name': name,
                'workload': workload,
            })
        
        # 담당 현장 수로 정렬 (내림차순)
        director_data = sorted(director_data, key=lambda x: x['workload'], reverse=True)
        
        # 상위 5명만 표시
        top_directors = director_data[:5]
        director_names = [d['name'] for d in top_directors]
        director_counts = [d['workload'] for d in top_directors]
        
        # 색상: 담당 현장 수에 따라
        colors = [
            "#6b7280" if count == 0 else "#10b981" if count <= 2 else "#f59e0b"
            for count in director_counts
        ]
        
        try:
            import plotly.graph_objects as go
            
            fig_directors = go.Figure(
                data=[
                    go.Bar(
                        x=director_counts,
                        y=director_names,
                        orientation="h",
                        marker_color=colors,
                        text=director_counts,
                        textposition="outside",
                        textfont=dict(size=12),
                        hovertemplate="<b>%{y}</b><br>담당 현장: %{x}개<extra></extra>",
                    )
                ],
            )
            fig_directors.update_layout(
                title=dict(
                    text="소장별 담당 현장 수 (Top 5)",
                    font=dict(size=12),
                ),
                xaxis_title="현장 수",
                height=max(250, len(director_names) * 50),
                margin=dict(t=50, b=40, l=100, r=40),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(
                    gridcolor="#f1f3f5",
                ),
                yaxis=dict(
                    tickfont=dict(size=11),
                ),
            )
            st.plotly_chart(fig_directors, use_container_width=True, key="dashboard_directors_bar")
        except ImportError:
            st.warning("Plotly가 설치되지 않았습니다.")
        except Exception as e:
            st.warning(f"차트 오류: {e}")
    else:
        st.info("소장 데이터가 없습니다.")
    
    # 빠른 액션
    st.markdown("""
    <a href="/투입가능인원_상세" class="nav-btn nav-btn-secondary" style="display: inline-block; margin-top: 12px; width: 100%;">
        소장 상세 보기
    </a>
    """, unsafe_allow_html=True)

# ==================== 3. 현장 현황 섹션 ====================
with col_sites:
    st.markdown("#### 현장 현황")
    
    # 현장 상태별 집계
    by_state = {}
    if raw_stats and isinstance(raw_stats, dict) and "sites" in raw_stats:
        by_state = (raw_stats.get("sites") or {}).get("by_state") or {}
    
    state_order = ["건축허가", "착공예정", "공사 중", "공사 중단", "준공"]
    
    # 요약 카드
    st.markdown(f"""
    <div class="info-card">
        <div class="info-row">
            <span class="info-label">건축허가</span>
            <span class="info-value">{by_state.get('건축허가', 0)}개</span>
        </div>
        <div class="info-row">
            <span class="info-label">착공예정</span>
            <span class="info-value" style="color: #3b82f6;">{by_state.get('착공예정', 0)}개</span>
        </div>
        <div class="info-row">
            <span class="info-label">공사 중</span>
            <span class="info-value" style="color: #f59e0b;">{by_state.get('공사 중', 0)}개</span>
        </div>
        <div class="info-row">
            <span class="info-label">공사 중단</span>
            <span class="info-value" style="color: #ef4444;">{by_state.get('공사 중단', 0)}개</span>
        </div>
        <div class="info-row">
            <span class="info-label">준공</span>
            <span class="info-value" style="color: #10b981;">{by_state.get('준공', 0)}개</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 현장 상태별 막대 차트
    state_labels = [s for s in state_order if by_state.get(s, 0) > 0]
    state_labels += [k for k in sorted(by_state.keys()) if k not in state_order and by_state.get(k, 0) > 0]
    state_values = [by_state.get(lb, 0) for lb in state_labels]
    
    # 상태별 색상 매핑
    state_colors_map = {
        "건축허가": "#6b7280",
        "착공예정": "#3b82f6",
        "공사 중": "#f59e0b",
        "공사 중단": "#ef4444",
        "준공": "#10b981",
    }
    
    if state_labels:
        try:
            import plotly.graph_objects as go
            
            bar_colors = [state_colors_map.get(s, CHART_COLORS["primary"]) for s in state_labels]
            
            fig_state = go.Figure(
                data=[
                    go.Bar(
                        x=state_values,
                        y=state_labels,
                        orientation="h",
                        marker_color=bar_colors,
                        text=state_values,
                        textposition="outside",
                        textfont=dict(size=12),
                        hovertemplate="<b>%{y}</b><br>현장 수: %{x}개<extra></extra>",
                    )
                ],
            )
            fig_state.update_layout(
                title=dict(
                    text="현장 상태별 현황",
                    font=dict(size=12),
                ),
                xaxis_title="현장 수",
                height=max(250, len(state_labels) * 50),
                margin=dict(t=50, b=40, l=100, r=40),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(
                    gridcolor="#f1f3f5",
                ),
                yaxis=dict(
                    tickfont=dict(size=11),
                ),
            )
            st.plotly_chart(fig_state, use_container_width=True, key="dashboard_state_bar")
        except ImportError:
            st.warning("Plotly가 설치되지 않았습니다.")
        except Exception as e:
            st.warning(f"차트 오류: {e}")
    else:
        st.info("현장 상태 데이터가 없습니다.")
    
    # 빠른 액션
    st.markdown("""
    <a href="/현장등록" class="nav-btn nav-btn-success" style="display: inline-block; margin-top: 12px; width: 100%;">
        새 현장 등록
    </a>
    """, unsafe_allow_html=True)

st.markdown("---")

# ========== 하단: 인력 및 자격증 요약 ==========
st.markdown("### 📈 인력 및 자격증")

summary_col1, summary_col2 = st.columns(2)

with summary_col1:
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
            <span class="info-value" style="color: #3b82f6;">{stats.get('deployed_personnel', 0)}명</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 직책별 인원 (간략 표시)
    by_role = {}
    if raw_stats and isinstance(raw_stats, dict) and "personnel" in raw_stats:
        by_role = (raw_stats.get("personnel") or {}).get("by_role") or {}
    
    if by_role:
        st.caption("**직책별 인원**")
        role_text = " | ".join([f"{role}: {count}명" for role, count in sorted(by_role.items())])
        st.caption(role_text)

with summary_col2:
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
    
    # 사용률
    cert_usage_rate = int((stats['total_certificates'] - stats['available_certificates']) / stats['total_certificates'] * 100) if stats['total_certificates'] > 0 else 0
    st.caption(f"**자격증 사용률**: {cert_usage_rate}%")

st.markdown("---")

# ========== 빠른 액션 (하단) ==========
st.markdown("### ⚡ 빠른 액션")

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
