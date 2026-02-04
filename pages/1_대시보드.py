"""
대시보드 - 통계 요약 및 시각화
GET /api/stats 사용. UI/UX: 로컬호스트 기준.
차트: 현장 상태별 파이 차트, 회사별 막대 그래프
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_utils.api_client import get_stats, check_api_connection
from streamlit_utils.theme import apply_localhost_theme

apply_localhost_theme()
st.title('📊 대시보드')

is_connected, error_msg = check_api_connection()
if not is_connected:
    st.error(f'API 연결 실패: {error_msg}')
    st.info('💡 Flask 서버를 먼저 실행하세요: `python run_api.py`')
    st.stop()

data, err = get_stats()
if err:
    st.error(err)
    st.stop()

if not data:
    st.info('통계 데이터가 없습니다.')
    st.stop()

sites = data.get('sites', {})
personnel = data.get('personnel', {})
certificates = data.get('certificates', {})

# ========== 주요 지표 카드 ==========
st.subheader('📈 주요 지표')
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button('전체 현장', key='btn_total_sites', use_container_width=True):
        st.switch_page('pages/2_현장_목록.py')
    st.metric('', sites.get('total', 0), label_visibility='collapsed')

with col2:
    if st.button('미배정 현장', key='btn_unassigned', use_container_width=True):
        st.switch_page('pages/2_현장_목록.py')
        # 쿼리 파라미터는 페이지 로드 후 적용
    st.metric('', sites.get('unassigned', 0), delta=f"-{sites.get('assigned', 0)}", delta_color="inverse", label_visibility='collapsed')

with col3:
    if st.button('배정완료', key='btn_assigned', use_container_width=True):
        st.switch_page('pages/2_현장_목록.py')
        # 쿼리 파라미터는 페이지 로드 후 적용
    st.metric('', sites.get('assigned', 0), delta=f"+{sites.get('assigned', 0)}", label_visibility='collapsed')

with col4:
    total_personnel = personnel.get('total', 0)
    available_personnel = personnel.get('available', 0)
    if st.button('투입가능 인원', key='btn_personnel', use_container_width=True):
        st.switch_page('pages/8_투입가능인원_상세.py')
    st.metric('', f"{available_personnel} / {total_personnel}", label_visibility='collapsed')
    st.caption(f'전체 {total_personnel}명 · 투입가능 {available_personnel}명')

st.markdown('---')

# ========== 차트 섹션 ==========
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader('현장 상태별 분포')
    by_state = sites.get('by_state', {})
    if by_state:
        # 파이 차트
        labels = list(by_state.keys())
        values = list(by_state.values())
        
        # 색상 매핑
        color_map = {
            '건축허가': '#6b7280',
            '착공예정': '#3b82f6',
            '착공중': '#f59e0b',
            '공사 중단': '#ef4444',
            '준공': '#10b981',
        }
        colors = [color_map.get(label, '#9ca3af') for label in labels]
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(colors=colors),
            textinfo='label+percent',
            textposition='outside',
        )])
        fig_pie.update_layout(
            showlegend=True,
            height=400,
            margin=dict(l=20, r=20, t=20, b=20),
            font=dict(family='Segoe UI, Malgun Gothic', size=12),
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info('현장 상태 데이터가 없습니다.')

with chart_col2:
    st.subheader('회사별 현장 수')
    by_company = sites.get('by_company', {})
    if by_company:
        # 막대 그래프
        companies = []
        counts = []
        for company, count in by_company.items():
            display_name = '종합건설' if company == '더존종합건설' else '하우징' if company == '더존하우징' else company
            companies.append(display_name)
            counts.append(count)
        
        fig_bar = go.Figure(data=[go.Bar(
            x=companies,
            y=counts,
            marker=dict(color=['#3b82f6', '#10b981']),
            text=counts,
            textposition='outside',
        )])
        fig_bar.update_layout(
            xaxis_title='회사구분',
            yaxis_title='현장 수',
            height=400,
            margin=dict(l=20, r=20, t=20, b=20),
            font=dict(family='Segoe UI, Malgun Gothic', size=12),
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info('회사별 데이터가 없습니다.')

st.markdown('---')

# ========== 배정 현황 ==========
st.subheader('배정 현황')
assign_col1, assign_col2 = st.columns(2)

with assign_col1:
    st.markdown('**배정 상태**')
    assigned_count = sites.get('assigned', 0)
    unassigned_count = sites.get('unassigned', 0)
    total_sites = sites.get('total', 0)
    
    if total_sites > 0:
        assigned_pct = (assigned_count / total_sites) * 100
        unassigned_pct = (unassigned_count / total_sites) * 100
        
        # 인터랙티브 도넛 차트 (Plotly)
        import plotly.graph_objects as go
        fig_assignment = go.Figure(data=[go.Pie(
            labels=['배정완료', '미배정'],
            values=[assigned_count, unassigned_count],
            hole=0.6,
            marker=dict(colors=['#10b981', '#ef4444']),
            textinfo='label+value+percent',
            textposition='outside',
            hovertemplate='<b>%{label}</b><br>%{value}개 (%{percent})<extra></extra>',
        )])
        fig_assignment.update_layout(
            showlegend=True,
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            font=dict(family='Segoe UI, Malgun Gothic', size=12),
        )
        st.plotly_chart(fig_assignment, use_container_width=True)
        
        # 배정률 표시
        st.metric('배정률', f'{assigned_pct:.1f}%', delta=f'{assigned_count}/{total_sites}')
        
        # 클릭 가능한 링크
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button('📋 배정완료 현장 보기', key='btn_view_assigned', use_container_width=True):
                st.switch_page('pages/2_현장_목록.py')
        with col_b:
            if st.button('⚠️ 미배정 현장 보기', key='btn_view_unassigned', use_container_width=True):
                st.switch_page('pages/2_현장_목록.py')
    else:
        st.info('현장 데이터가 없습니다.')

with assign_col2:
    st.markdown('**인력 현황**')
    by_role = personnel.get('by_role', {})
    if by_role:
        role_df_data = {'직책': list(by_role.keys()), '인원수': list(by_role.values())}
        import pandas as pd
        role_df = pd.DataFrame(role_df_data)
        st.dataframe(role_df, use_container_width=True, hide_index=True)
    else:
        st.info('인력 데이터가 없습니다.')

st.markdown('---')

# ========== 상세 통계 (접을 수 있는 섹션) ==========
with st.expander('📋 상세 통계 데이터', expanded=False):
    detail_col1, detail_col2 = st.columns(2)
    
    with detail_col1:
        st.markdown('**현장 현황**')
        st.json({
            '회사별': sites.get('by_company', {}),
            '현장상태별': sites.get('by_state', {}),
        })
    
    with detail_col2:
        st.markdown('**인력 현황**')
        st.json(personnel.get('by_role', {}))
        
        st.markdown('**자격증 현황**')
        st.json({
            '전체': certificates.get('total', 0),
            '사용가능': certificates.get('available', 0),
            '사용중': certificates.get('in_use', 0),
            '만료': certificates.get('expired', 0),
        })

# ========== 핫스팟 경고 ==========
st.markdown('---')
st.subheader('⚠️ 주의사항')

hotspot_col1, hotspot_col2 = st.columns(2)

with hotspot_col1:
    unassigned_ratio = (sites.get('unassigned', 0) / max(sites.get('total', 1), 1)) * 100
    if unassigned_ratio > 30:
        st.warning(f'🚨 미배정 현장 비율이 높습니다 ({unassigned_ratio:.1f}%)')
    elif unassigned_ratio > 10:
        st.info(f'💡 미배정 현장: {sites.get("unassigned", 0)}개 ({unassigned_ratio:.1f}%)')
    else:
        st.success(f'✅ 배정 상태 양호: 미배정 {sites.get("unassigned", 0)}개 ({unassigned_ratio:.1f}%)')

with hotspot_col2:
    available_personnel = personnel.get('available', 0)
    unassigned_sites = sites.get('unassigned', 0)
    if unassigned_sites > 0 and available_personnel < unassigned_sites:
        st.error(f'⚠️ 투입 가능 인력 부족: 인력 {available_personnel}명 < 미배정 현장 {unassigned_sites}개')
    elif available_personnel == 0 and unassigned_sites > 0:
        st.error('🚨 투입 가능 인력이 없습니다!')
    else:
        st.success(f'✅ 인력 여유: 투입가능 {available_personnel}명')
