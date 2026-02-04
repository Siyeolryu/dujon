"""
현장 목록 - 고급 필터, 검색, 페이지네이션, 정렬, 인라인 액션
200개 현장 대응: 페이지네이션, 정렬, 실시간 검색, 상태 시각화
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_utils.api_client import (
    get_sites,
    search_sites,
    get_site,
    get_personnel,
    get_certificates,
    assign_site,
    unassign_site,
    check_api_connection,
)
from streamlit_utils.theme import apply_localhost_theme, render_top_nav

apply_localhost_theme()
render_top_nav(current_page="2_site_list")

# 필터 탭 스타일 추가
st.markdown("""
<style>
    /* 필터 탭 스타일 */
    .filter-tab-group {
        margin-bottom: 16px;
    }
    .filter-tab-label {
        font-size: 12px;
        font-weight: 600;
        color: #495057;
        margin-bottom: 6px;
        display: block;
    }
    /* 라디오 탭 = theme.py 공통 (필터는 보조 계층 회색) */
    /* 필터 섹션 레이아웃 최적화 */
    .filter-section-container {
        background: #fff;
        border-radius: 12px;
        padding: 14px 18px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        margin-bottom: 20px;
    }
    /* 컬럼 간격 최적화 */
    [data-testid="column"] {
        padding-left: 8px !important;
        padding-right: 8px !important;
    }
    /* 필터 행 간격 조정 */
    .filter-row {
        margin-bottom: 12px;
    }
    /* 현장 목록 테이블 정렬 - 헤더/행 일치 */
    .site-table-wrap {
        overflow-x: auto;
        margin-top: 12px;
    }
    .site-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
        background: #fff;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .site-table th {
        text-align: left;
        padding: 12px 14px;
        background: #f8f9fa;
        color: #495057;
        font-weight: 600;
        border-bottom: 1px solid #e9ecef;
        white-space: nowrap;
    }
    .site-table td {
        padding: 12px 14px;
        border-bottom: 1px solid #f1f3f5;
        vertical-align: middle;
    }
    .site-table tbody tr:hover {
        background: #f8f9fa;
    }
    .site-table .cell-actions {
        white-space: nowrap;
    }
    .assign-panel-box {
        background: #fff;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'page_size' not in st.session_state:
    st.session_state.page_size = 20
if 'sort_column' not in st.session_state:
    st.session_state.sort_column = '등록일'
if 'sort_asc' not in st.session_state:
    st.session_state.sort_asc = False
if 'search_query' not in st.session_state:
    st.session_state.search_query = ''
if 'last_search_time' not in st.session_state:
    st.session_state.last_search_time = None
if 'selected_site_id' not in st.session_state:
    st.session_state.selected_site_id = None
if 'show_assign_modal' not in st.session_state:
    st.session_state.show_assign_modal = False

st.title('📋 현장 목록')

# API 연결 확인 (Supabase 모드일 때는 체크 건너뛰기)
import os
api_mode = os.getenv('API_MODE', '').strip().lower() or 'flask'
if api_mode != 'supabase':
    is_connected, error_msg = check_api_connection()
    if not is_connected:
        st.error(f'API 연결 실패: {error_msg}')
        st.info('💡 Flask 서버를 먼저 실행하세요: `python run_api.py`')
        st.stop()

# ========== 쿼리 파라미터에서 필터 읽기 ==========
query_params = st.query_params
initial_status = query_params.get('status', [''])[0] if 'status' in query_params else ''
initial_company = query_params.get('company', [''])[0] if 'company' in query_params else ''

# ========== 필터 섹션 ==========
st.markdown('<div class="filter-section-container">', unsafe_allow_html=True)
st.subheader('🔍 필터 및 검색')

# 필터 탭 그룹 - 최적화된 레이아웃
filter_row1 = st.columns([1.1, 1.1, 1.3, 2.5])
with filter_row1[0]:
    st.markdown('<div class="filter-tab-label">회사구분</div>', unsafe_allow_html=True)
    company_options = ['', '더존종합건설', '더존하우징']
    company_index = 1 if initial_company == '더존종합건설' else (2 if initial_company == '더존하우징' else 0)
    company_radio = st.radio(
        '회사구분',
        company_options,
        format_func=lambda x: {'': '전체', '더존종합건설': '종합건설', '더존하우징': '하우징'}.get(x, x),
        key='filter_company_radio',
        index=company_index,
        horizontal=True,
        label_visibility='collapsed'
    )
    company = company_radio

with filter_row1[1]:
    st.markdown('<div class="filter-tab-label">배정상태</div>', unsafe_allow_html=True)
    status_options = ['', '배정완료', '미배정']
    status_index = status_options.index(initial_status) if initial_status in status_options else 0
    status_radio = st.radio(
        '배정상태',
        status_options,
        format_func=lambda x: x or '전체',
        key='filter_status_radio',
        index=status_index,
        horizontal=True,
        label_visibility='collapsed'
    )
    status = status_radio

with filter_row1[2]:
    st.markdown('<div class="filter-tab-label">현장상태</div>', unsafe_allow_html=True)
    state_options = ['', '건축허가', '착공예정', '공사 중', '공사 중단', '준공']
    state_radio = st.radio(
        '현장상태',
        state_options,
        format_func=lambda x: x or '전체',
        key='filter_state_radio',
        horizontal=True,
        label_visibility='collapsed'
    )
    state = state_radio

with filter_row1[3]:
    search_input = st.text_input(
        '현장명·주소 검색',
        placeholder='검색어 입력 (실시간 검색)',
        key='search_input',
        value=st.session_state.search_query,
    )

st.markdown('</div>', unsafe_allow_html=True)

# 실시간 검색 debounce 처리
if search_input != st.session_state.search_query:
    st.session_state.search_query = search_input
    st.session_state.last_search_time = datetime.now()
    st.session_state.current_page = 1  # 검색 시 첫 페이지로

# 고급 필터 (접을 수 있는 섹션)
selected_manager = ''
date_start = None
date_end = None
with st.expander('📅 고급 필터 (날짜 범위, 담당소장)', expanded=False):
    adv_col1, adv_col2, adv_col3 = st.columns(3)
    
    with adv_col1:
        # 담당소장명 필터를 위해 인력 목록 가져오기
        personnel_list, _ = get_personnel(role='소장')
        manager_names = [''] + sorted(list(set([p.get('성명', '') for p in (personnel_list or []) if p.get('성명')])))
        selected_manager = st.selectbox(
            '담당소장명',
            manager_names,
            format_func=lambda x: x or '전체',
            key='filter_manager',
        )
    
    with adv_col2:
        date_start = st.date_input(
            '착공예정일 시작',
            value=None,
            key='filter_date_start',
        )
    
    with adv_col3:
        date_end = st.date_input(
            '착공예정일 종료',
            value=None,
            key='filter_date_end',
        )
    
    if st.button('🔄 필터 초기화', use_container_width=True):
        st.session_state.filter_company_radio = ''
        st.session_state.filter_status_radio = ''
        st.session_state.filter_state_radio = ''
        st.session_state.filter_manager = ''
        st.session_state.filter_date_start = None
        st.session_state.filter_date_end = None
        st.session_state.search_query = ''
        st.session_state.search_input = ''
        st.session_state.current_page = 1
        st.rerun()

# 필터 초기화 시 페이지 리셋
if company == '' and status == '' and state == '' and selected_manager == '':
    if st.session_state.current_page != 1:
        st.session_state.current_page = 1

# ========== 데이터 로드 (서버 사이드 페이지네이션) ==========
# 페이지네이션 파라미터 계산
page_size = st.session_state.page_size
current_page = st.session_state.current_page
offset = (current_page - 1) * page_size

if st.session_state.search_query and st.session_state.search_query.strip():
    # 검색은 클라이언트 사이드 (검색 결과가 적을 것으로 예상)
    sites, err = search_sites(st.session_state.search_query.strip())
    total_count = len(sites) if sites else 0
else:
    # 서버 사이드 페이지네이션 사용
    result, err = get_sites(
        company=company or None,
        status=status or None,
        state=state or None,
        limit=page_size,
        offset=offset,
    )
    if not err and result:
        sites = result.get('data', [])
        total_count = result.get('total', len(sites))
    else:
        sites = []
        total_count = 0

if err:
    st.error(f'데이터 로드 실패: {err}')
    st.stop()

if not sites:
    st.info('조건에 맞는 현장이 없습니다.')
    st.stop()

# ========== 추가 필터링 (담당소장명, 날짜 범위) ==========
filtered_sites = sites.copy()

# 담당소장명 필터
if selected_manager and selected_manager.strip():
    filtered_sites = [
        s for s in filtered_sites
        if s.get('담당소장명', '').strip() == selected_manager.strip()
    ]

# 날짜 범위 필터
if date_start:
    filtered_sites = [
        s for s in filtered_sites
        if s.get('착공예정일') and s.get('착공예정일') >= date_start.strftime('%Y-%m-%d')
    ]
if date_end:
    filtered_sites = [
        s for s in filtered_sites
        if s.get('착공예정일') and s.get('착공예정일') <= date_end.strftime('%Y-%m-%d')
    ]

# ========== 데이터프레임 생성 및 정렬 ==========
display_cols = ['현장명', '회사구분', '배정상태', '현장상태', '담당소장명', '착공예정일', '등록일', '현장ID']
rows = []
for s in filtered_sites:
    row = {k: s.get(k, '') for k in display_cols}
    # 회사구분 표시 정규화
    if row.get('회사구분') == '더존종합건설':
        row['회사구분'] = '종합건설'
    elif row.get('회사구분') == '더존하우징':
        row['회사구분'] = '하우징'
    rows.append(row)

df = pd.DataFrame(rows)

# 정렬 적용
if st.session_state.sort_column in df.columns:
    df = df.sort_values(
        by=st.session_state.sort_column,
        ascending=st.session_state.sort_asc,
        na_position='last',
    )

# ========== 상태 배지 스타일 함수 ==========
def render_status_badge(status, badge_type='assignment'):
    """상태 배지 렌더링"""
    colors = {
        'assignment': {
            '배정완료': ('#10b981', '#d1fae5'),  # 초록
            '미배정': ('#ef4444', '#fee2e2'),    # 빨강
        },
        'site_state': {
            '건축허가': ('#6b7280', '#f3f4f6'),  # 회색
            '착공예정': ('#3b82f6', '#dbeafe'),  # 파란색
            '공사 중': ('#f59e0b', '#fef3c7'),    # 주황색
            '공사 중단': ('#ef4444', '#fee2e2'),  # 빨강
            '준공': ('#10b981', '#d1fae5'),      # 초록
        }
    }
    
    color_map = colors.get(badge_type, {})
    if status in color_map:
        text_color, bg_color = color_map[status]
        return f'<span style="background-color: {bg_color}; color: {text_color}; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500;">{status}</span>'
    return status

# ========== 페이지네이션 계산 ==========
total_pages = max(1, (total_count + st.session_state.page_size - 1) // st.session_state.page_size)


def _render_pagination(key_suffix='', bottom_only=False):
    """페이지네이션 컨트롤 렌더. bottom_only=True면 캡션+이전/다음만 (목록 하단용)."""
    if bottom_only:
        c1, c2, c3 = st.columns([2, 3, 2])
        with c1:
            st.write('')
        with c2:
            st.caption(f'📊 총 {total_count}개 현장 | 페이지 {st.session_state.current_page}/{total_pages}')
        with c3:
            prev_col, next_col = st.columns(2)
            with prev_col:
                if st.button('◀ 이전', disabled=st.session_state.current_page <= 1, use_container_width=True, key=f'prev{key_suffix}'):
                    st.session_state.current_page -= 1
                    st.rerun()
            with next_col:
                if st.button('다음 ▶', disabled=st.session_state.current_page >= total_pages, use_container_width=True, key=f'next{key_suffix}'):
                    st.session_state.current_page += 1
                    st.rerun()
        return
    c1, c2, c3 = st.columns([2, 3, 2])
    with c1:
        page_size_options = [20, 50, 100]
        new_page_size = st.selectbox(
            '페이지당 항목 수',
            page_size_options,
            index=page_size_options.index(st.session_state.page_size) if st.session_state.page_size in page_size_options else 0,
            key=f'page_size_select{key_suffix}',
        )
        if new_page_size != st.session_state.page_size:
            st.session_state.page_size = new_page_size
            st.session_state.current_page = 1
            st.rerun()
    with c2:
        st.caption(f'📊 총 {total_count}개 현장 | 페이지 {st.session_state.current_page}/{total_pages}')
    with c3:
        prev_col, next_col = st.columns(2)
        with prev_col:
            if st.button('◀ 이전', disabled=st.session_state.current_page <= 1, use_container_width=True, key=f'prev{key_suffix}'):
                st.session_state.current_page -= 1
                st.rerun()
        with next_col:
            if st.button('다음 ▶', disabled=st.session_state.current_page >= total_pages, use_container_width=True, key=f'next{key_suffix}'):
                st.session_state.current_page += 1
                st.rerun()


# ========== 소장 배정 패널 (필터 바로 아래, 목록 위 · 항상 눈에 띄게) ==========
if st.session_state.show_assign_modal and st.session_state.selected_site_id:
    with st.expander('📌 소장 배정', expanded=True):
        st.markdown('<div class="assign-panel-box">', unsafe_allow_html=True)
        site_id = st.session_state.selected_site_id
        detail, err = get_site(site_id)
        if err and not detail:
            st.error(err)
        elif detail:
            st.info(f"**{detail.get('현장명', '')}** · 현장ID: `{site_id}`")
            version = detail.get('version', '')
            personnel_list, _ = get_personnel(status='투입가능')
            cert_list, _ = get_certificates(available=True)
            if not personnel_list:
                st.warning('투입가능 인력이 없습니다.')
            elif not cert_list:
                st.warning('사용가능 자격증이 없습니다.')
            else:
                manager_options = {
                    f"{p.get('성명', '')} ({p.get('인력ID', '')})": p.get('인력ID')
                    for p in personnel_list
                }
                cert_options = {
                    f"{c.get('자격증명', '')} / {c.get('소유자명', '')} ({c.get('자격증ID', '')})": c.get('자격증ID')
                    for c in cert_list
                }
                c1, c2, c3 = st.columns([2, 2, 1])
                with c1:
                    sel_manager = st.selectbox('담당 소장', list(manager_options.keys()), key='assign_manager')
                with c2:
                    sel_cert = st.selectbox('사용 자격증', list(cert_options.keys()), key='assign_cert')
                with c3:
                    st.write('')
                    st.write('')
                    col_assign, col_cancel = st.columns(2)
                    with col_assign:
                        if st.button('✅ 배정하기', use_container_width=True, type='primary', key='btn_assign_do'):
                            mid = manager_options.get(sel_manager)
                            cid = cert_options.get(sel_cert)
                            if mid and cid:
                                result, err = assign_site(site_id, mid, cid, version=version or None)
                                if err:
                                    st.error(err)
                                else:
                                    st.success('배정되었습니다.')
                                    st.session_state.show_assign_modal = False
                                    st.session_state.selected_site_id = None
                                    st.rerun()
                            else:
                                st.error('소장 또는 자격증을 선택하세요.')
                    with col_cancel:
                        if st.button('❌ 취소', use_container_width=True, key='btn_assign_cancel'):
                            st.session_state.show_assign_modal = False
                            st.session_state.selected_site_id = None
                            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ========== 페이지네이션 컨트롤 (상단) ==========
_render_pagination(key_suffix='_top')

# ========== 현장 목록 테이블 (정렬된 데이터프레임 + 행별 액션) ==========
st.markdown('### 현장 목록')

# 표시용 데이터프레임 (액션 제외)
df_display = df[['현장명', '회사구분', '배정상태', '현장상태', '담당소장명', '착공예정일', '등록일', '현장ID']].copy()
df_display.columns = ['현장명', '회사구분', '배정상태', '현장상태', '담당소장명', '착공예정일', '등록일', '현장ID']

# 현장 선택 + 액션 버튼 (한 줄 툴바)
site_options = list(df_display['현장명'].astype(str) + ' (' + df_display['현장ID'].astype(str) + ')')
site_id_map = dict(zip(site_options, df_display['현장ID']))
tool_col1, tool_col2, tool_col3, tool_col4 = st.columns([3, 1, 1, 1])
with tool_col1:
    selected_label = st.selectbox(
        '현장 선택 (액션 적용)',
        options=[''] + site_options,
        format_func=lambda x: x or '— 선택하세요 —',
        key='site_select_toolbar'
    )
with tool_col2:
    do_assign = st.button('배정', use_container_width=True, key='tool_assign')
with tool_col3:
    do_detail = st.button('상세', use_container_width=True, key='tool_detail')
with tool_col4:
    do_copy = st.button('복사', use_container_width=True, key='tool_copy')

if selected_label and selected_label in site_id_map:
    selected_site_id = site_id_map[selected_label]
    if do_assign:
        st.session_state.selected_site_id = selected_site_id
        st.session_state.show_assign_modal = True
        st.rerun()
    if do_detail:
        st.session_state.selected_site_id = selected_site_id
        st.session_state.show_assign_modal = False
        st.rerun()
    if do_copy:
        st.toast(f'현장ID 복사됨: {selected_site_id}')

# 행별 배정/해제 버튼은 테이블 아래 "빠른 액션"으로
st.dataframe(
    df_display[['현장명', '회사구분', '배정상태', '현장상태', '담당소장명', '착공예정일', '등록일']],
    use_container_width=True,
    hide_index=True,
    column_config={
        '현장명': st.column_config.TextColumn('현장명', width='medium'),
        '회사구분': st.column_config.TextColumn('회사구분', width='small'),
        '배정상태': st.column_config.TextColumn('배정상태', width='small'),
        '현장상태': st.column_config.TextColumn('현장상태', width='small'),
        '담당소장명': st.column_config.TextColumn('담당소장명', width='small'),
        '착공예정일': st.column_config.TextColumn('착공예정일', width='small'),
        '등록일': st.column_config.TextColumn('등록일', width='small'),
    }
)

# 빠른 액션: 행별 배정/해제/상세 (접이식, 테이블 가독성 우선)
with st.expander('🔧 빠른 액션 (행별 배정·해제·상세)', expanded=False):
    st.caption('위 "현장 선택 (액션 적용)" 드롭다운으로도 동일한 액션을 사용할 수 있습니다.')
    for idx, row in df.iterrows():
        site_id = row['현장ID']
        ac1, ac2, ac3, ac4 = st.columns([2, 1, 1, 1])
        with ac1:
            st.caption(f"**{row['현장명']}** (ID: `{site_id}`)")
        with ac2:
            if row['배정상태'] == '배정완료':
                if st.button('해제', key=f'unassign_{site_id}', use_container_width=True):
                    detail, _ = get_site(site_id)
                    version = detail.get('version', '') if detail else ''
                    _, err = unassign_site(site_id, version=version or None)
                    if err:
                        st.error(err)
                    else:
                        st.success('배정 해제됨')
                        st.rerun()
            else:
                if st.button('배정', key=f'assign_{site_id}', use_container_width=True):
                    st.session_state.selected_site_id = site_id
                    st.session_state.show_assign_modal = True
                    st.rerun()
        with ac3:
            if st.button('상세', key=f'detail_{site_id}', use_container_width=True):
                st.session_state.selected_site_id = site_id
                st.session_state.show_assign_modal = False
                st.rerun()
        with ac4:
            if st.button('복사', key=f'copy_{site_id}', use_container_width=True):
                st.toast(f'현장ID 복사됨: {site_id}')

# ========== 페이지네이션 컨트롤 (하단: 스크롤 후에도 전환 가능) ==========
_render_pagination(key_suffix='_bottom', bottom_only=True)

# ========== 상세 정보 표시 ==========
if st.session_state.selected_site_id and not st.session_state.show_assign_modal:
    st.markdown('---')
    st.subheader('📄 현장 상세 정보')
    
    detail, err = get_site(st.session_state.selected_site_id)
    if err and not detail:
        st.error(err)
    elif detail:
        detail_col1, detail_col2 = st.columns(2)
        
        with detail_col1:
            st.markdown(f"**현장명**: {detail.get('현장명', '')}")
            st.markdown(f"**현장ID**: `{detail.get('현장ID', '')}`")
            st.markdown(f"**회사구분**: {detail.get('회사구분', '')}")
            st.markdown(f"**주소**: {detail.get('주소', '')}")
            st.markdown(f"**건축주명**: {detail.get('건축주명', '')}")
            st.markdown(f"**현장상태**: {detail.get('현장상태', '')}")
            st.markdown(f"**배정상태**: {detail.get('배정상태', '')}")
        
        with detail_col2:
            st.markdown(f"**건축허가일**: {detail.get('건축허가일', '')}")
            st.markdown(f"**착공예정일**: {detail.get('착공예정일', '')}")
            st.markdown(f"**준공일**: {detail.get('준공일', '')}")
            st.markdown(f"**담당소장명**: {detail.get('담당소장명', '')}")
            st.markdown(f"**담당소장연락처**: {detail.get('담당소장연락처', '')}")
            st.markdown(f"**자격증명**: {detail.get('자격증명', '')}")
            st.markdown(f"**등록일**: {detail.get('등록일', '')}")
            st.markdown(f"**수정일**: {detail.get('수정일', '')}")
        
        if detail.get('특이사항'):
            st.markdown(f"**특이사항**: {detail.get('특이사항', '')}")
        
        if st.button('상세 정보 닫기'):
            st.session_state.selected_site_id = None
            st.rerun()
