"""
데이터 내보내기 모듈
Excel, CSV 내보내기 기능
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
import io


def export_to_excel(
    data: pd.DataFrame,
    filename: str = "export",
    sheet_name: str = "Sheet1",
) -> bytes:
    """DataFrame을 Excel 파일로 변환
    
    Args:
        data: 내보낼 DataFrame
        filename: 파일명 (확장자 제외)
        sheet_name: 시트명
        
    Returns:
        Excel 파일 바이트
    """
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        data.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # 워크시트 가져오기
        worksheet = writer.sheets[sheet_name]
        
        # 컬럼 너비 자동 조정
        for idx, col in enumerate(data.columns):
            max_length = max(
                data[col].astype(str).apply(len).max(),
                len(str(col))
            )
            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
    
    output.seek(0)
    return output.getvalue()


def export_to_csv(
    data: pd.DataFrame,
    filename: str = "export",
    encoding: str = "utf-8-sig",  # Excel에서 한글 깨짐 방지
) -> bytes:
    """DataFrame을 CSV 파일로 변환
    
    Args:
        data: 내보낼 DataFrame
        filename: 파일명 (확장자 제외)
        encoding: 인코딩 (기본: utf-8-sig)
        
    Returns:
        CSV 파일 바이트
    """
    return data.to_csv(index=False, encoding=encoding).encode(encoding)


def render_export_button(
    data: pd.DataFrame,
    filename_prefix: str = "export",
    button_text: str = "📥 데이터 내보내기",
    formats: List[str] = ["Excel", "CSV"],
    key_suffix: str = "",
) -> None:
    """데이터 내보내기 버튼 렌더링
    
    Args:
        data: 내보낼 DataFrame
        filename_prefix: 파일명 접두사
        button_text: 버튼 텍스트
        formats: 내보내기 형식 리스트
        key_suffix: 고유 키 접미사
    """
    if data.empty:
        st.warning("내보낼 데이터가 없습니다.")
        return
    
    # 현재 시간으로 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 내보내기 형식 선택
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"**총 {len(data)}건의 데이터**")
    
    with col2:
        export_format = st.selectbox(
            "형식",
            formats,
            key=f"export_format_{key_suffix}",
            label_visibility="collapsed"
        )
    
    # 내보내기 버튼
    if export_format == "Excel":
        filename = f"{filename_prefix}_{timestamp}.xlsx"
        file_data = export_to_excel(data, filename)
        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:  # CSV
        filename = f"{filename_prefix}_{timestamp}.csv"
        file_data = export_to_csv(data, filename)
        mime_type = "text/csv"
    
    st.download_button(
        label=button_text,
        data=file_data,
        file_name=filename,
        mime=mime_type,
        key=f"download_{key_suffix}",
        use_container_width=True,
    )


def render_export_section(
    data: pd.DataFrame,
    title: str = "데이터 내보내기",
    filename_prefix: str = "export",
    show_preview: bool = True,
    preview_rows: int = 5,
    key_suffix: str = "",
) -> None:
    """데이터 내보내기 섹션 렌더링 (미리보기 포함)
    
    Args:
        data: 내보낼 DataFrame
        title: 섹션 제목
        filename_prefix: 파일명 접두사
        show_preview: 미리보기 표시 여부
        preview_rows: 미리보기 행 수
        key_suffix: 고유 키 접미사
    """
    with st.expander(f"📥 {title}", expanded=False):
        if data.empty:
            st.info("내보낼 데이터가 없습니다.")
            return
        
        # 데이터 정보
        st.markdown(f"""
        <div class="info-card">
            <div class="info-row">
                <span class="info-label">총 데이터 수</span>
                <span class="info-value">{len(data)}건</span>
            </div>
            <div class="info-row">
                <span class="info-label">컬럼 수</span>
                <span class="info-value">{len(data.columns)}개</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 미리보기
        if show_preview:
            st.markdown("#### 미리보기")
            st.dataframe(
                data.head(preview_rows),
                use_container_width=True,
                hide_index=True,
            )
        
        # 내보내기 버튼
        st.markdown("---")
        render_export_button(
            data=data,
            filename_prefix=filename_prefix,
            button_text="📥 내보내기",
            key_suffix=key_suffix,
        )


def prepare_sites_export(sites_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """현장 데이터를 내보내기용 DataFrame으로 변환
    
    Args:
        sites_data: 현장 데이터 리스트
        
    Returns:
        정리된 DataFrame
    """
    if not sites_data:
        return pd.DataFrame()
    
    df = pd.DataFrame(sites_data)
    
    # 컬럼 순서 정리
    column_order = [
        '현장ID', '현장명', '회사구분', '주소',
        '현장상태', '배정상태', '담당소장명', '담당소장연락처',
        '사용자격증명', '자격증소유자명',
        '건축허가일', '착공예정일', '준공일',
        '특이사항', '등록일', '수정일'
    ]
    
    # 존재하는 컬럼만 선택
    available_columns = [col for col in column_order if col in df.columns]
    df = df[available_columns]
    
    return df


def prepare_personnel_export(personnel_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """인력 데이터를 내보내기용 DataFrame으로 변환
    
    Args:
        personnel_data: 인력 데이터 리스트
        
    Returns:
        정리된 DataFrame
    """
    if not personnel_data:
        return pd.DataFrame()
    
    df = pd.DataFrame(personnel_data)
    
    # 컬럼 순서 정리
    column_order = [
        '인력ID', '성명', '직책', '소속',
        '연락처', '이메일', '보유자격증',
        '현재상태', '현재담당현장수',
        '입사일', '비고', '등록일'
    ]
    
    # 존재하는 컬럼만 선택
    available_columns = [col for col in column_order if col in df.columns]
    df = df[available_columns]
    
    return df


def prepare_certificates_export(certificates_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """자격증 데이터를 내보내기용 DataFrame으로 변환
    
    Args:
        certificates_data: 자격증 데이터 리스트
        
    Returns:
        정리된 DataFrame
    """
    if not certificates_data:
        return pd.DataFrame()
    
    df = pd.DataFrame(certificates_data)
    
    # 컬럼 순서 정리
    column_order = [
        '자격증ID', '자격증명', '자격증번호',
        '소유자명', '소유자연락처',
        '발급기관', '취득일', '유효기간',
        '사용가능여부', '현재사용현장명',
        '비고', '등록일'
    ]
    
    # 존재하는 컬럼만 선택
    available_columns = [col for col in column_order if col in df.columns]
    df = df[available_columns]
    
    return df


def render_quick_export_buttons(
    data: pd.DataFrame,
    filename_prefix: str = "export",
    key_suffix: str = "",
) -> None:
    """빠른 내보내기 버튼 (Excel, CSV 나란히)
    
    Args:
        data: 내보낼 DataFrame
        filename_prefix: 파일명 접두사
        key_suffix: 고유 키 접미사
    """
    if data.empty:
        st.caption("내보낼 데이터가 없습니다.")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Excel 내보내기
        excel_filename = f"{filename_prefix}_{timestamp}.xlsx"
        excel_data = export_to_excel(data, excel_filename)
        st.download_button(
            label="📊 Excel 다운로드",
            data=excel_data,
            file_name=excel_filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"excel_{key_suffix}",
            use_container_width=True,
        )
    
    with col2:
        # CSV 내보내기
        csv_filename = f"{filename_prefix}_{timestamp}.csv"
        csv_data = export_to_csv(data, csv_filename)
        st.download_button(
            label="📄 CSV 다운로드",
            data=csv_data,
            file_name=csv_filename,
            mime="text/csv",
            key=f"csv_{key_suffix}",
            use_container_width=True,
        )
