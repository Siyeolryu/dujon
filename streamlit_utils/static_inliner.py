"""
정적 파일(CSS, JS)을 HTML에 인라인으로 포함시키는 유틸리티
Streamlit Cloud에서도 정적 파일 없이 동작하도록
"""
import os
from pathlib import Path
import re


def get_project_root():
    """프로젝트 루트 경로 반환"""
    current_file = Path(__file__).resolve()
    return current_file.parent.parent


def inline_css_and_js(html_content):
    """
    HTML의 외부 CSS/JS 파일을 인라인으로 변환
    
    Args:
        html_content: 원본 HTML 내용
        
    Returns:
        CSS/JS가 인라인으로 포함된 HTML 내용
    """
    root = get_project_root()
    
    # CSS 파일 인라인화
    css_pattern = r'<link[^>]*rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)["\'][^>]*>'
    css_matches = re.finditer(css_pattern, html_content)
    
    for match in reversed(list(css_matches)):  # 역순으로 처리하여 인덱스 변경 방지
        css_path = match.group(1)
        # 상대 경로 처리
        if not css_path.startswith('http') and not css_path.startswith('//'):
            # css/style.css -> css/style.css
            full_path = root / css_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        css_content = f.read()
                    # <style> 태그로 교체
                    style_tag = f'<style>\n{css_content}\n</style>'
                    html_content = html_content[:match.start()] + style_tag + html_content[match.end():]
                except Exception as e:
                    print(f"CSS 파일 로드 실패: {css_path}, {e}")
    
    # JS 파일 인라인화 (외부 CDN은 제외)
    js_pattern = r'<script[^>]*src=["\']([^"\']+)["\'][^>]*></script>'
    js_matches = re.finditer(js_pattern, html_content)
    
    for match in reversed(list(js_matches)):
        js_path = match.group(1)
        # CDN이나 외부 스크립트는 제외
        if js_path.startswith('http') or js_path.startswith('//'):
            continue
        
        # 상대 경로 처리
        if not js_path.startswith('/'):
            full_path = root / js_path
        else:
            full_path = root / js_path.lstrip('/')
            
        if full_path.exists():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    js_content = f.read()
                # <script> 태그로 교체
                script_tag = f'<script>\n{js_content}\n</script>'
                html_content = html_content[:match.start()] + script_tag + html_content[match.end():]
            except Exception as e:
                print(f"JS 파일 로드 실패: {js_path}, {e}")
    
    return html_content


def prepare_html_for_streamlit(html_content, api_base_url='/api'):
    """
    HTML을 Streamlit에서 사용할 수 있도록 준비
    
    Args:
        html_content: 원본 HTML 내용
        api_base_url: API 기본 URL
        
    Returns:
        Streamlit용 HTML 내용
    """
    # CSS/JS 인라인화
    try:
        html_content = inline_css_and_js(html_content)
    except Exception as e:
        import streamlit as st
        st.warning(f"CSS/JS 인라인화 중 일부 오류 발생: {str(e)} (계속 진행합니다)")
    
    # API 설정 주입 (기존 설정이 있으면 교체)
    # Streamlit iframe 내부에서도 올바른 API URL 사용하도록 설정
    api_config_script = f'''
    <script>
        // Streamlit 환경에서 API URL 설정 (가장 먼저 실행)
        (function() {{
            // 절대 URL 설정 (상대 경로인 경우 현재 호스트 사용)
            let apiUrl = '{api_base_url}';
            if (apiUrl.startsWith('/')) {{
                // 상대 경로인 경우 현재 페이지의 프로토콜과 호스트 사용
                // Streamlit iframe 내부에서는 부모 창의 origin 사용 시도
                try {{
                    if (window.parent && window.parent.location && window.parent !== window) {{
                        apiUrl = window.parent.location.origin + apiUrl;
                    }} else {{
                        apiUrl = window.location.origin + apiUrl;
                    }}
                }} catch(e) {{
                    // Cross-origin 제한으로 부모 접근 불가 시 현재 origin 사용
                    apiUrl = window.location.origin + apiUrl;
                }}
            }}
            
            // 전역 변수 설정 (config.js보다 먼저)
            window.__API_BASE_URL__ = apiUrl;
            window.__STREAMLIT_API_URL__ = apiUrl;  // 추가 백업
            
            // CONFIG 객체 미리 생성 (config.js가 로드되기 전)
            if (!window.CONFIG) {{
                window.CONFIG = {{}};
            }}
            window.CONFIG.API_MODE = 'flask';
            window.CONFIG.API_BASE_URL = apiUrl;
            
            // config.js가 로드된 후에도 이 값이 우선되도록 감시
            const originalConfig = window.CONFIG;
            let configProxy = new Proxy(originalConfig, {{
                get: function(target, prop) {{
                    if (prop === 'API_MODE') return 'flask';
                    if (prop === 'API_BASE_URL') return apiUrl;
                    return target[prop];
                }},
                set: function(target, prop, value) {{
                    if (prop === 'API_MODE' && value !== 'flask') {{
                        console.warn('API_MODE는 Streamlit 환경에서 flask로 고정됩니다.');
                        return true;
                    }}
                    if (prop === 'API_BASE_URL') {{
                        console.warn('API_BASE_URL은 Streamlit 환경에서 고정됩니다.');
                        return true;
                    }}
                    target[prop] = value;
                    return true;
                }}
            }});
            
            // config.js 로드 후 CONFIG 객체 교체
            setTimeout(function() {{
                if (window.CONFIG && window.CONFIG !== configProxy) {{
                    Object.assign(window.CONFIG, {{
                        API_MODE: 'flask',
                        API_BASE_URL: apiUrl
                    }});
                }}
            }}, 100);
        }})();
    </script>
'''
    
    # 기존 API 설정 스크립트 제거 후 새로 추가
    html_content = re.sub(
        r'<script[^>]*>.*?window\.__API_BASE_URL__.*?</script>',
        '',
        html_content,
        flags=re.DOTALL
    )
    
    # </head> 태그 바로 뒤에 API 설정 스크립트 추가 (가장 먼저 실행되도록)
    if '</head>' in html_content:
        html_content = html_content.replace('</head>', api_config_script + '</head>')
    elif '<head>' in html_content:
        # </head>가 없으면 <head> 태그 바로 뒤에 추가
        html_content = html_content.replace('<head>', '<head>' + api_config_script)
    elif '</body>' in html_content:
        # </body> 앞에 추가
        html_content = html_content.replace('</body>', api_config_script + '</body>')
    else:
        # 맨 앞에 추가
        html_content = api_config_script + html_content
    
    # Streamlit iframe 샌드박스 제한 해제를 위한 스타일 추가
    style_addition = '''
    <style>
        /* Streamlit iframe 내부 스타일 최적화 */
        html, body {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow-x: hidden;
        }
        /* 스크롤바 스타일 */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
    </style>
'''
    if '</head>' in html_content:
        html_content = html_content.replace('</head>', style_addition + '</head>')
    
    return html_content
