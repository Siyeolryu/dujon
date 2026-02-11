"""
투입가능 인원 상세 - 전체 인원 / 투입가능 인원 탭
인원 정보와 각 인원의 자격증 표시
"""
import streamlit as st
import pandas as pd
from streamlit_utils.cached_api import (
    get_personnel_cached,
    get_certificates_cached,
    check_api_connection_cached,
)
from streamlit_utils.theme import apply_localhost_theme
from streamlit_utils.export import render_quick_export_buttons, prepare_personnel_export

apply_localhost_theme()
st.title('투입가능 인원')

is_connected, error_msg = check_api_connection_cached()
if not is_connected:
    st.error(f'API 연결 실패: {error_msg}')
    st.info('Flask 서버를 먼저 실행하세요: `python run_api.py`')
    st.stop()

# 탭: 전체 인원 / 투입가능 인원
tab1, tab2 = st.tabs(['전체 인원', '투입가능 인원'])

# 전체 인원 탭
with tab1:
    st.subheader('전체 인원 목록')
    
    personnel_list, err = get_personnel_cached()
    if err:
        st.error(err)
        st.stop()
    
    if not personnel_list:
        st.info('등록된 인원이 없습니다.')
        st.stop()
    
    # 검색 및 필터
    col1, col2 = st.columns([3, 1])
    with col1:
        search_name = st.text_input('이름 검색', placeholder='인원 이름 입력', key='search_all')
    with col2:
        role_filter = st.selectbox(
            '직책 필터',
            ['전체'] + list(set([p.get('직책', '') for p in personnel_list if p.get('직책')])),
            key='role_filter_all'
        )
    
    # 필터링
    filtered_personnel = personnel_list
    if search_name and search_name.strip():
        filtered_personnel = [p for p in filtered_personnel if search_name.strip().lower() in (p.get('성명', '') or '').lower()]
    if role_filter != '전체':
        filtered_personnel = [p for p in filtered_personnel if p.get('직책') == role_filter]
    
    st.caption(f'총 {len(filtered_personnel)}명')
    
    # 데이터 내보내기
    if filtered_personnel:
        export_df = prepare_personnel_export(filtered_personnel)
        render_quick_export_buttons(
            data=export_df,
            filename_prefix="전체인원",
            key_suffix="all_personnel"
        )

    # 자격증 목록을 루프 밖에서 1회만 호출 (N+1 방지)
    all_certs_tab1, _ = get_certificates_cached()

    # 인원별 상세 정보 표시
    for person in filtered_personnel:
        with st.expander(f"{person.get('성명', '-')} ({person.get('인력ID', '-')}) - {person.get('직책', '-')}", expanded=False):
            col_info, col_certs = st.columns([1, 1])

            with col_info:
                st.markdown('**인원 정보**')
                st.write(f"**인력ID**: {person.get('인력ID', '-')}")
                st.write(f"**성명**: {person.get('성명', '-')}")
                st.write(f"**직책**: {person.get('직책', '-')}")
                st.write(f"**소속**: {person.get('소속', '-')}")
                st.write(f"**연락처**: {person.get('연락처', '-')}")
                st.write(f"**이메일**: {person.get('이메일', '-')}")
                st.write(f"**현재상태**: {person.get('현재상태', '-')}")
                st.write(f"**현재담당현장수**: {person.get('현재담당현장수', '0')}개")
                st.write(f"**보유자격증**: {person.get('보유자격증', '-')}")
                st.write(f"**입사일**: {person.get('입사일', '-')}")
                st.write(f"**등록일**: {person.get('등록일', '-')}")
                if person.get('비고'):
                    st.write(f"**비고**: {person.get('비고')}")

            with col_certs:
                st.markdown('**보유 자격증**')
                # 해당 인원의 자격증 찾기 (소유자명으로 매칭, 전체 목록 재사용)
                person_name = person.get('성명', '')
                person_certs = [c for c in (all_certs_tab1 or []) if c.get('소유자명') == person_name]

                if person_certs:
                    cert_data = []
                    for cert in person_certs:
                        cert_data.append({
                            '자격증ID': cert.get('자격증ID', '-'),
                            '자격증명': cert.get('자격증명', '-'),
                            '자격증번호': cert.get('자격증번호', '-'),
                            '발급기관': cert.get('발급기관', '-'),
                            '취득일': cert.get('취득일', '-'),
                            '유효기간': cert.get('유효기간', '-'),
                            '사용가능여부': cert.get('사용가능여부', '-'),
                            '현재사용현장ID': cert.get('현재사용현장ID', '-'),
                        })
                    cert_df = pd.DataFrame(cert_data)
                    st.dataframe(cert_df, use_container_width=True, hide_index=True)
                else:
                    st.info('보유 자격증이 없습니다.')

# 투입가능 인원 탭
with tab2:
    st.subheader('투입가능 인원 목록')
    
    personnel_list, err = get_personnel_cached(status='투입가능')
    if err:
        st.error(err)
        st.stop()
    
    if not personnel_list:
        st.info('투입가능 인원이 없습니다.')
        st.stop()
    
    # 검색 및 필터
    col1, col2 = st.columns([3, 1])
    with col1:
        search_name = st.text_input('이름 검색', placeholder='인원 이름 입력', key='search_available')
    with col2:
        role_filter = st.selectbox(
            '직책 필터',
            ['전체'] + list(set([p.get('직책', '') for p in personnel_list if p.get('직책')])),
            key='role_filter_available'
        )
    
    # 필터링
    filtered_personnel = personnel_list
    if search_name and search_name.strip():
        filtered_personnel = [p for p in filtered_personnel if search_name.strip().lower() in (p.get('성명', '') or '').lower()]
    if role_filter != '전체':
        filtered_personnel = [p for p in filtered_personnel if p.get('직책') == role_filter]
    
    st.caption(f'투입가능 인원: {len(filtered_personnel)}명')
    
    # 데이터 내보내기
    if filtered_personnel:
        export_df = prepare_personnel_export(filtered_personnel)
        render_quick_export_buttons(
            data=export_df,
            filename_prefix="투입가능인원",
            key_suffix="available_personnel"
        )

    # 자격증 목록을 루프 밖에서 1회만 호출 (N+1 방지)
    all_certs_tab2, _ = get_certificates_cached()

    # 인원별 상세 정보 표시
    for person in filtered_personnel:
        with st.expander(f"{person.get('성명', '-')} ({person.get('인력ID', '-')}) - {person.get('직책', '-')}", expanded=False):
            col_info, col_certs = st.columns([1, 1])

            with col_info:
                st.markdown('**인원 정보**')
                st.write(f"**인력ID**: {person.get('인력ID', '-')}")
                st.write(f"**성명**: {person.get('성명', '-')}")
                st.write(f"**직책**: {person.get('직책', '-')}")
                st.write(f"**소속**: {person.get('소속', '-')}")
                st.write(f"**연락처**: {person.get('연락처', '-')}")
                st.write(f"**이메일**: {person.get('이메일', '-')}")
                st.write(f"**현재상태**: {person.get('현재상태', '-')}")
                st.write(f"**현재담당현장수**: {person.get('현재담당현장수', '0')}개")
                st.write(f"**보유자격증**: {person.get('보유자격증', '-')}")
                st.write(f"**입사일**: {person.get('입사일', '-')}")
                st.write(f"**등록일**: {person.get('등록일', '-')}")
                if person.get('비고'):
                    st.write(f"**비고**: {person.get('비고')}")

            with col_certs:
                st.markdown('**보유 자격증**')
                # 해당 인원의 자격증 찾기 (소유자명으로 매칭, 전체 목록 재사용)
                person_name = person.get('성명', '')
                person_certs = [c for c in (all_certs_tab2 or []) if c.get('소유자명') == person_name]

                if person_certs:
                    cert_data = []
                    for cert in person_certs:
                        cert_data.append({
                            '자격증ID': cert.get('자격증ID', '-'),
                            '자격증명': cert.get('자격증명', '-'),
                            '자격증번호': cert.get('자격증번호', '-'),
                            '발급기관': cert.get('발급기관', '-'),
                            '취득일': cert.get('취득일', '-'),
                            '유효기간': cert.get('유효기간', '-'),
                            '사용가능여부': cert.get('사용가능여부', '-'),
                            '현재사용현장ID': cert.get('현재사용현장ID', '-'),
                        })
                    cert_df = pd.DataFrame(cert_data)
                    st.dataframe(cert_df, use_container_width=True, hide_index=True)
                else:
                    st.info('보유 자격증이 없습니다.')
