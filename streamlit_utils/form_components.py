"""
폼 전용 UI 컴포넌트
에러 표시, 성공 메시지, 검증 상태 표시 등
"""
import streamlit as st
from typing import Optional, Dict, Any


def render_field_error(error_message: str, key_suffix: str = ""):
    """
    필드 에러 메시지 표시
    
    Args:
        error_message: 에러 메시지
        key_suffix: 고유 키 접미사
    """
    if error_message:
        st.markdown(
            f"""
            <div style="
                background-color: #fee;
                border-left: 4px solid #f44;
                padding: 8px 12px;
                margin: 4px 0 12px 0;
                border-radius: 4px;
                font-size: 13px;
                color: #c33;
            ">
                ❌ {error_message}
            </div>
            """,
            unsafe_allow_html=True
        )


def render_field_success(message: str):
    """
    필드 성공 메시지 표시
    
    Args:
        message: 성공 메시지
    """
    if message:
        st.markdown(
            f"""
            <div style="
                background-color: #efe;
                border-left: 4px solid #4a4;
                padding: 8px 12px;
                margin: 4px 0 12px 0;
                border-radius: 4px;
                font-size: 13px;
                color: #3a3;
            ">
                ✅ {message}
            </div>
            """,
            unsafe_allow_html=True
        )


def render_success_message(
    message: str, 
    redirect_url: Optional[str] = None,
    redirect_label: str = "페이지로 이동"
):
    """
    성공 메시지 + 리다이렉트 옵션
    
    Args:
        message: 성공 메시지
        redirect_url: 리다이렉트 URL (선택)
        redirect_label: 리다이렉트 버튼 라벨
    """
    st.success(f"✅ {message}")
    
    if redirect_url:
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button(f"📄 {redirect_label}", use_container_width=True, type="primary"):
                st.switch_page(redirect_url)
        with col2:
            if st.button("✏️ 계속 등록하기", use_container_width=True):
                st.rerun()


def render_form_summary(data: Dict[str, Any], title: str = "입력 내용 확인"):
    """
    입력 내용 요약 카드
    
    Args:
        data: 표시할 데이터 딕셔너리
        title: 제목
    """
    st.markdown(f"### {title}")
    
    st.markdown(
        """
        <div style="
            background: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin: 16px 0;
        ">
        """,
        unsafe_allow_html=True
    )
    
    for key, value in data.items():
        if value:  # 값이 있는 것만 표시
            st.markdown(
                f"""
                <div style="
                    display: flex;
                    padding: 8px 0;
                    border-bottom: 1px solid #f0f0f0;
                ">
                    <div style="
                        flex: 0 0 150px;
                        font-weight: 600;
                        color: #495057;
                    ">{key}</div>
                    <div style="
                        flex: 1;
                        color: #1a1d21;
                    ">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_validation_indicator(is_valid: bool, show: bool = True):
    """
    검증 상태 아이콘 표시 (✓/✗)
    
    Args:
        is_valid: 검증 결과
        show: 표시 여부
    """
    if not show:
        return
    
    if is_valid:
        st.markdown(
            '<span style="color: #28a745; font-size: 18px;">✓</span>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<span style="color: #dc3545; font-size: 18px;">✗</span>',
            unsafe_allow_html=True
        )


def render_step_indicator(current_step: int, total_steps: int, step_labels: list):
    """
    다단계 폼 진행 표시기
    
    Args:
        current_step: 현재 단계 (1부터 시작)
        total_steps: 전체 단계 수
        step_labels: 단계별 라벨 리스트
    """
    st.markdown(
        f"""
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 20px 0 30px 0;
            padding: 0 20px;
        ">
        """,
        unsafe_allow_html=True
    )
    
    for i in range(1, total_steps + 1):
        is_current = i == current_step
        is_completed = i < current_step
        
        # 단계 원 색상
        if is_completed:
            circle_color = "#28a745"  # 완료: 녹색
            text_color = "#28a745"
        elif is_current:
            circle_color = "#007bff"  # 현재: 파랑
            text_color = "#007bff"
        else:
            circle_color = "#dee2e6"  # 미완료: 회색
            text_color = "#6c757d"
        
        # 단계 라벨
        label = step_labels[i-1] if i-1 < len(step_labels) else f"Step {i}"
        
        st.markdown(
            f"""
            <div style="
                flex: 1;
                text-align: center;
                position: relative;
            ">
                <div style="
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    background-color: {circle_color};
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 8px auto;
                    font-weight: bold;
                    font-size: 16px;
                ">
                    {i if not is_completed else '✓'}
                </div>
                <div style="
                    font-size: 13px;
                    color: {text_color};
                    font-weight: {'600' if is_current else '400'};
                ">
                    {label}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # 단계 간 연결선 (마지막 단계 제외)
        if i < total_steps:
            line_color = "#28a745" if is_completed else "#dee2e6"
            st.markdown(
                f"""
                <div style="
                    flex: 0 0 60px;
                    height: 2px;
                    background-color: {line_color};
                    margin-top: 20px;
                "></div>
                """,
                unsafe_allow_html=True
            )
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_form_section_header(title: str, is_required: bool = False):
    """
    폼 섹션 헤더
    
    Args:
        title: 섹션 제목
        is_required: 필수 섹션 여부
    """
    required_badge = ""
    if is_required:
        required_badge = '<span style="color: #dc3545; margin-left: 8px;">*</span>'
    
    st.markdown(
        f"""
        <div style="
            font-size: 16px;
            font-weight: 600;
            color: #1a1d21;
            margin: 24px 0 16px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #007bff;
        ">
            {title}{required_badge}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_form_help_text(text: str):
    """
    폼 도움말 텍스트
    
    Args:
        text: 도움말 텍스트
    """
    st.markdown(
        f"""
        <div style="
            font-size: 13px;
            color: #6c757d;
            margin: -8px 0 16px 0;
            padding: 8px 12px;
            background-color: #f8f9fa;
            border-radius: 4px;
        ">
            💡 {text}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_form_error_summary(errors: Dict[str, str]):
    """
    폼 전체 에러 요약 (상단 표시)
    
    Args:
        errors: {field: error_message} 딕셔너리
    """
    if not errors:
        return
    
    st.markdown(
        f"""
        <div style="
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 8px;
            padding: 16px;
            margin: 16px 0;
        ">
            <div style="
                font-weight: 600;
                color: #856404;
                margin-bottom: 12px;
                font-size: 15px;
            ">
                ⚠️ 입력 내용을 확인해주세요 ({len(errors)}개 오류)
            </div>
            <ul style="
                margin: 0;
                padding-left: 20px;
                color: #856404;
                font-size: 14px;
            ">
        """,
        unsafe_allow_html=True
    )
    
    for field, error in errors.items():
        st.markdown(f"<li>{error}</li>", unsafe_allow_html=True)
    
    st.markdown("</ul></div>", unsafe_allow_html=True)
