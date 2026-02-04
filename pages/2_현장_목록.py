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
from streamlit_utils.theme import apply_localhost_theme

apply_localhost_theme()

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
st.subheader('🔍 필터 및 검색')

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([1.2, 1.2, 1.2, 2])
with filter_col1:
    company = st.selectbox(
        '회사구분',
        ['', '더존종합건설', '더존하우징'],
        format_func=lambda x: {'': '전체', '더존종합건설': '종합건설', '더존하우징': '하우징'}.get(x, x),
        key='filter_company',
        index=1 if initial_company == '더존종합건설' else (2 if initial_company == '더존하우징' else 0),
    )
with filter_col2:
    status_options = ['', '배정완료', '미배정']
    status_index = status_options.index(initial_status) if initial_status in status_options else 0
    status = st.selectbox(
        '배정상태',
        status_options,
        format_func=lambda x: x or '전체',
        key='filter_status',
        index=status_index,
    )
with filter_col3:
    state = st.selectbox(
        '현장상태',
        ['', '건축허가', '착공예정', '공사 중', '공사 중단', '준공'],
        format_func=lambda x: x or '전체',
        key='filter_state',
    )
with filter_col4:
    search_input = st.text_input(
        '현장명·주소 검색',
        placeholder='검색어 입력 (실시간 검색)',
        key='search_input',
        value=st.session_state.search_query,
    )

# 실시간 검색 debounce 처리
if search_input != st.session_state.search_query:
    st.session_state.search_query = search_input
    st.session_state.last_search_time = datetime.now()
    st.session_state.current_page = 1  # 검색 시 첫 페이지로

# 고급 필터 (접을 수 있는 섹션)
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
        st.session_state.filter_company = ''
        st.session_state.filter_status = ''
        st.session_state.filter_state = ''
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

# ========== 페이지네이션 컨트롤 ==========
# total_count는 이미 서버에서 받아온 값 사용
total_pages = max(1, (total_count + st.session_state.page_size - 1) // st.session_state.page_size)

pagination_col1, pagination_col2, pagination_col3 = st.columns([2, 3, 2])
with pagination_col1:
    page_size_options = [20, 50, 100]
    new_page_size = st.selectbox(
        '페이지당 항목 수',
        page_size_options,
        index=page_size_options.index(st.session_state.page_size) if st.session_state.page_size in page_size_options else 0,
        key='page_size_select',
    )
    if new_page_size != st.session_state.page_size:
        st.session_state.page_size = new_page_size
        st.session_state.current_page = 1
        st.rerun()

with pagination_col2:
    st.caption(f'📊 총 {total_count}개 현장 | 페이지 {st.session_state.current_page}/{total_pages}')

with pagination_col3:
    prev_col, next_col = st.columns(2)
    with prev_col:
        if st.button('◀ 이전', disabled=st.session_state.current_page <= 1, use_container_width=True):
            st.session_state.current_page -= 1
            st.rerun()
    with next_col:
        if st.button('다음 ▶', disabled=st.session_state.current_page >= total_pages, use_container_width=True):
            st.session_state.current_page += 1
            st.rerun()

# ========== 테이블 헤더 및 정렬 ==========
st.markdown('---')
st.markdown('### 현장 목록')

# 정렬 가능한 헤더
sortable_columns = ['현장명', '회사구분', '배정상태', '현장상태', '담당소장명', '착공예정일', '등록일']
header_cols = st.columns([2, 1, 1.2, 1.2, 1.5, 1.2, 1.2, 2.5])

header_labels = {
    '현장명': '현장명',
    '회사구분': '회사구분',
    '배정상태': '배정상태',
    '현장상태': '현장상태',
    '담당소장명': '담당소장명',
    '착공예정일': '착공예정일',
    '등록일': '등록일',
    'actions': '액션',
}

for idx, (col, label_key) in enumerate(zip(header_cols[:-1], list(header_labels.keys())[:-1])):
    with col:
        if label_key in sortable_columns:
            sort_icon = ''
            if st.session_state.sort_column == label_key:
                sort_icon = ' ↑' if st.session_state.sort_asc else ' ↓'
            
            if st.button(f'{header_labels[label_key]}{sort_icon}', key=f'sort_{label_key}', use_container_width=True):
                if st.session_state.sort_column == label_key:
                    st.session_state.sort_asc = not st.session_state.sort_asc
                else:
                    st.session_state.sort_column = label_key
                    st.session_state.sort_asc = True
                st.rerun()
        else:
            st.markdown(f'**{header_labels[label_key]}**')

with header_cols[-1]:
    st.markdown('**액션**')

# ========== 테이블 본문 (서버 사이드 페이지네이션으로 이미 필터링됨) ==========
# df는 이미 페이지네이션된 데이터이므로 그대로 사용
# 테이블 행 렌더링
for idx, row in df.iterrows():
    row_cols = st.columns([2, 1, 1.2, 1.2, 1.5, 1.2, 1.2, 2.5])
    
    with row_cols[0]:
        st.markdown(f"**{row['현장명']}**")
        st.caption(f"ID: `{row['현장ID']}`")
    
    with row_cols[1]:
        st.markdown(row['회사구분'] or '-')
    
    with row_cols[2]:
        st.markdown(render_status_badge(row['배정상태'], 'assignment'), unsafe_allow_html=True)
    
    with row_cols[3]:
        st.markdown(render_status_badge(row['현장상태'], 'site_state'), unsafe_allow_html=True)
    
    with row_cols[4]:
        st.markdown(row['담당소장명'] or '-')
    
    with row_cols[5]:
        st.markdown(row['착공예정일'] or '-')
    
    with row_cols[6]:
        st.markdown(row['등록일'] or '-')
    
    with row_cols[7]:
        action_col1, action_col2, action_col3 = st.columns(3)
        site_id = row['현장ID']
        
        with action_col1:
            if row['배정상태'] == '배정완료':
                if st.button('해제', key=f'unassign_{site_id}', use_container_width=True):
                    detail, _ = get_site(site_id)
                    if detail:
                        version = detail.get('version', '')
                        result, err = unassign_site(site_id, version=version or None)
                        if err:
                            st.error(err)
                        else:
                            st.success('배정이 해제되었습니다.')
                            st.rerun()
            else:
                if st.button('배정', key=f'assign_{site_id}', use_container_width=True):
                    st.session_state.selected_site_id = site_id
                    st.session_state.show_assign_modal = True
                    st.rerun()
        
        with action_col2:
            if st.button('상세', key=f'detail_{site_id}', use_container_width=True):
                st.session_state.selected_site_id = site_id
                st.rerun()
        
        with action_col3:
            if st.button('복사', key=f'copy_{site_id}', use_container_width=True):
                st.write(f'현장ID 복사됨: `{site_id}`')
    
    st.markdown('<hr style="margin: 8px 0; border-color: #e9ecef;">', unsafe_allow_html=True)

# ========== 배정 모달 (사이드바 스타일) ==========
if st.session_state.show_assign_modal and st.session_state.selected_site_id:
    with st.sidebar:
        st.subheader('소장 배정')
        site_id = st.session_state.selected_site_id
        
        detail, err = get_site(site_id)
        if err and not detail:
            st.error(err)
        elif detail:
            st.info(f"**{detail.get('현장명', '')}**\n\n현장ID: `{site_id}`")
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
                
                sel_manager = st.selectbox('담당 소장', list(manager_options.keys()))
                sel_cert = st.selectbox('사용 자격증', list(cert_options.keys()))
                
                col_assign, col_cancel = st.columns(2)
                with col_assign:
                    if st.button('✅ 배정하기', use_container_width=True, type='primary'):
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
                    if st.button('❌ 취소', use_container_width=True):
                        st.session_state.show_assign_modal = False
                        st.session_state.selected_site_id = None
                        st.rerun()

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
