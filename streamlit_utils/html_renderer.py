"""
Streamlit에서 로컬호스트 HTML/JS UI를 렌더링하는 유틸리티
로컬호스트의 site-management.html을 Streamlit에 직접 통합
"""
import os
import re
from pathlib import Path
import streamlit.components.v1 as components
from streamlit_utils.static_inliner import prepare_html_for_streamlit


def get_project_root():
    """프로젝트 루트 경로 반환"""
    current_file = Path(__file__).resolve()
    # streamlit_utils/html_renderer.py -> 프로젝트 루트
    return current_file.parent.parent


def load_html_file(filename='site-management.html'):
    """HTML 파일을 읽어서 문자열로 반환"""
    root = get_project_root()
    html_path = root / filename
    
    if not html_path.exists():
        raise FileNotFoundError(f"HTML 파일을 찾을 수 없습니다: {html_path}")
    
    with open(html_path, 'r', encoding='utf-8') as f:
        return f.read()


def _detect_streamlit_cloud():
    """Streamlit Cloud 환경 감지"""
    return (
        os.getenv('STREAMLIT_SERVER_HEADLESS') == 'true' or
        os.getenv('STREAMLIT_SERVER_PORT') is not None or
        (os.getenv('HOSTNAME') and 'streamlit' in os.getenv('HOSTNAME', '').lower())
    )


def render_html_app(html_file='site-management.html', height=800, key=None):
    """
    HTML 앱을 Streamlit에 렌더링
    CSS/JS를 인라인으로 포함하여 Streamlit Cloud에서도 동작
    
    Args:
        html_file: 렌더링할 HTML 파일명
        height: 컴포넌트 높이 (픽셀)
        key: Streamlit 컴포넌트 키
    """
    try:
        html_content = load_html_file(html_file)
        
        # API 기본 URL 결정
        import os
        api_base_url = os.getenv('API_BASE_URL', '').strip()
        
        # Streamlit Cloud 환경 감지
        is_streamlit_cloud = _detect_streamlit_cloud()
        if is_streamlit_cloud:
            # 배포 환경에서는 상대 경로 사용 (같은 서버의 /api)
            # 또는 환경 변수로 설정된 URL 사용
            if not api_base_url:
                api_base_url = '/api'
        else:
            # 로컬 개발 환경
            if not api_base_url:
                api_base_url = 'http://localhost:5000'
        
        # CSS/JS 인라인화 및 Streamlit 준비
        html_content = prepare_html_for_streamlit(html_content, api_base_url)
        
        # Streamlit components로 렌더링
        return components.html(
            html_content,
            height=height,
            scrolling=True,
            key=key
        )
    except FileNotFoundError as e:
        import streamlit as st
        st.error(f"❌ HTML 파일을 찾을 수 없습니다: {html_file}")
        st.info(f"파일 경로를 확인하세요: {e}")
        return None
    except Exception as e:
        import streamlit as st
        import traceback
        st.error(f"❌ HTML 렌더링 오류: {str(e)}")
        with st.expander("상세 오류 정보"):
            st.code(traceback.format_exc())
        return None


def render_dashboard_only():
    """대시보드 섹션만 렌더링"""
    html_content = load_html_file()
    
    # 대시보드 섹션만 추출
    import re
    dashboard_match = re.search(
        r'<section id="dashboard"[^>]*>.*?</section>',
        html_content,
        re.DOTALL
    )
    
    if dashboard_match:
        dashboard_html = dashboard_match.group(0)
        # 필요한 CSS와 JS 포함
        head_match = re.search(r'<head>.*?</head>', html_content, re.DOTALL)
        head_content = head_match.group(0) if head_match else ''
        
        full_html = f'''
<!DOCTYPE html>
<html lang="ko">
{head_content}
<body>
    {dashboard_html}
    <script src="/js/config.js"></script>
    <script src="/js/api.js"></script>
    <script src="/js/dashboard.js"></script>
</body>
</html>
'''
        return components.html(full_html, height=600, scrolling=True)
    else:
        import streamlit as st
        st.error("대시보드 섹션을 찾을 수 없습니다.")
        return None
