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
    
    css_files_processed = []
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
                    css_files_processed.append(css_path)
                except Exception as e:
                    print(f"⚠️ CSS 파일 로드 실패: {css_path}, {e}")
            else:
                print(f"⚠️ CSS 파일을 찾을 수 없습니다: {full_path}")
    
    # JS 파일 인라인화 (외부 CDN은 제외)
    js_pattern = r'<script[^>]*src=["\']([^"\']+)["\'][^>]*></script>'
    js_matches = re.finditer(js_pattern, html_content)
    
    js_files_processed = []
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
                js_files_processed.append(js_path)
            except Exception as e:
                print(f"⚠️ JS 파일 로드 실패: {js_path}, {e}")
        else:
            print(f"⚠️ JS 파일을 찾을 수 없습니다: {full_path}")
    
    # 처리 결과 로그 (디버깅용)
    if css_files_processed or js_files_processed:
        print(f"✅ 인라인화 완료: CSS {len(css_files_processed)}개, JS {len(js_files_processed)}개")
    
    return html_content


def prepare_html_for_streamlit(html_content, api_base_url='/api', api_mode='flask', supabase_url='', supabase_anon_key=''):
    """
    HTML을 Streamlit에서 사용할 수 있도록 준비
    
    Args:
        html_content: 원본 HTML 내용
        api_base_url: API 기본 URL (예: 'http://localhost:5000/api' 또는 '/api')
        api_mode: API 모드 ('flask' 또는 'supabase')
        supabase_url: Supabase URL (api_mode='supabase'일 때 필수)
        supabase_anon_key: Supabase Anon Key (api_mode='supabase'일 때 필수)
        
    Returns:
        Streamlit용 HTML 내용
    """
    # CSS/JS 인라인화
    try:
        html_content = inline_css_and_js(html_content)
    except Exception as e:
        import streamlit as st
        st.warning(f"CSS/JS 인라인화 중 일부 오류 발생: {str(e)} (계속 진행합니다)")
    
    # API 모드에 따라 설정 스크립트 생성
    if api_mode == 'supabase' and supabase_url and supabase_anon_key:
        # Supabase 직접 연결 모드
        api_config_script = f'''
    <script>
        // Streamlit 환경에서 Supabase 직접 연결 설정 (가장 먼저 실행)
        (function() {{
            // Supabase 설정 주입
            window.__SUPABASE_URL__ = '{supabase_url}';
            window.__SUPABASE_ANON_KEY__ = '{supabase_anon_key}';
            
            // CONFIG 객체 미리 생성 (config.js가 로드되기 전)
            if (!window.CONFIG) {{
                window.CONFIG = {{}};
            }}
            window.CONFIG.API_MODE = 'supabase';
            window.CONFIG.SUPABASE_URL = '{supabase_url}';
            window.CONFIG.SUPABASE_ANON_KEY = '{supabase_anon_key}';
            
            console.log('[Streamlit] Supabase 직접 연결 모드 설정 완료:', {{
                API_MODE: window.CONFIG.API_MODE,
                SUPABASE_URL: window.CONFIG.SUPABASE_URL
            }});
            
            // config.js 로드 후 CONFIG 객체 강제 업데이트
            setTimeout(function() {{
                if (window.CONFIG) {{
                    Object.assign(window.CONFIG, {{
                        API_MODE: 'supabase',
                        SUPABASE_URL: '{supabase_url}',
                        SUPABASE_ANON_KEY: '{supabase_anon_key}'
                    }});
                    console.log('[Streamlit] CONFIG 강제 업데이트 완료 (Supabase 모드):', window.CONFIG);
                }}
            }}, 100);
            
            // DOMContentLoaded 시에도 다시 확인
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', function() {{
                    if (window.CONFIG) {{
                        window.CONFIG.API_MODE = 'supabase';
                        window.CONFIG.SUPABASE_URL = '{supabase_url}';
                        window.CONFIG.SUPABASE_ANON_KEY = '{supabase_anon_key}';
                        console.log('[Streamlit] DOMContentLoaded 후 CONFIG 재설정 (Supabase 모드):', window.CONFIG);
                    }}
                }});
            }}
        }})();
    </script>
'''
    else:
        # Flask API 모드 (기본값)
        # API URL 정규화 (로컬호스트인 경우 명확하게 설정)
        is_localhost = api_base_url.startswith('http://localhost') or api_base_url.startswith('http://127.0.0.1')
        
        api_config_script = f'''
    <script>
        // Streamlit 환경에서 API URL 설정 (가장 먼저 실행)
        (function() {{
            // API URL 결정
            let apiUrl = '{api_base_url}';
            
            // 로컬호스트인 경우 그대로 사용
            if (apiUrl.startsWith('http://localhost') || apiUrl.startsWith('http://127.0.0.1')) {{
                // 이미 절대 URL이므로 그대로 사용
                console.log('[Streamlit] API URL 설정:', apiUrl);
            }} else if (apiUrl.startsWith('/')) {{
                // 상대 경로인 경우 현재 페이지의 프로토콜과 호스트 사용
                // Streamlit iframe 내부에서는 부모 창의 origin 사용 시도
                try {{
                    // 로컬 개발 환경에서는 localhost:5000 사용
                    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {{
                        // Streamlit은 보통 8501 포트, API는 5000 포트
                        apiUrl = 'http://localhost:5000' + apiUrl;
                    }} else if (window.parent && window.parent.location && window.parent !== window) {{
                        // 부모 창이 있으면 부모의 origin 사용
                        apiUrl = window.parent.location.origin + apiUrl;
                    }} else {{
                        apiUrl = window.location.origin + apiUrl;
                    }}
                }} catch(e) {{
                    // Cross-origin 제한으로 부모 접근 불가 시
                    // 로컬 개발 환경 가정
                    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {{
                        apiUrl = 'http://localhost:5000' + apiUrl;
                    }} else {{
                        apiUrl = window.location.origin + apiUrl;
                    }}
                }}
                console.log('[Streamlit] API URL 변환:', apiUrl);
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
            
            console.log('[Streamlit] CONFIG 설정 완료:', {{
                API_MODE: window.CONFIG.API_MODE,
                API_BASE_URL: window.CONFIG.API_BASE_URL
            }});
            
            // config.js 로드 후 CONFIG 객체 강제 업데이트
            setTimeout(function() {{
                if (window.CONFIG) {{
                    Object.assign(window.CONFIG, {{
                        API_MODE: 'flask',
                        API_BASE_URL: apiUrl
                    }});
                    console.log('[Streamlit] CONFIG 강제 업데이트 완료:', window.CONFIG);
                }}
            }}, 100);
            
            // DOMContentLoaded 시에도 다시 확인
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', function() {{
                    if (window.CONFIG) {{
                        window.CONFIG.API_MODE = 'flask';
                        window.CONFIG.API_BASE_URL = apiUrl;
                        console.log('[Streamlit] DOMContentLoaded 후 CONFIG 재설정:', window.CONFIG);
                    }}
                }});
            }}
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
    
    # API 호출 에러 핸들링 개선 스크립트 추가
    api_error_handler = '''
    <script>
        // API 호출 에러 핸들링 개선
        (function() {
            // 기존 fetch를 래핑하여 에러 처리 개선
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                const url = args[0];
                const options = args[1] || {};
                
                // API 호출인 경우 (로컬호스트 API)
                if (typeof url === 'string' && (url.includes('localhost:5000') || url.includes('127.0.0.1:5000'))) {
                    // CORS 에러 처리
                    return originalFetch.apply(this, args)
                        .catch(function(error) {
                            console.error('[Streamlit] API 호출 실패:', url, error);
                            // 네트워크 에러인 경우 사용자에게 알림
                            if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
                                console.warn('[Streamlit] API 서버가 실행되지 않았거나 연결할 수 없습니다.');
                                console.warn('[Streamlit] 해결 방법: 터미널에서 `python run_api.py` 실행');
                            }
                            throw error;
                        });
                }
                
                return originalFetch.apply(this, args);
            };
        })();
    </script>
'''
    if '</head>' in html_content:
        html_content = html_content.replace('</head>', api_error_handler + '</head>')
    
    return html_content
