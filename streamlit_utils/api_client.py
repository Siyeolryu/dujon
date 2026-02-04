"""
Streamlit용 REST API 클라이언트.
환경에 따라 Flask API 또는 Supabase 직접 연결을 사용합니다.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def _detect_environment():
    """배포 환경 감지"""
    # Streamlit Cloud 감지 (여러 방법 시도)
    if os.getenv('STREAMLIT_SERVER_HEADLESS') == 'true':
        return 'streamlit_cloud'
    if os.getenv('STREAMLIT_SERVER_PORT'):
        return 'streamlit_cloud'
    if os.getenv('HOSTNAME') and 'streamlit' in os.getenv('HOSTNAME', '').lower():
        return 'streamlit_cloud'
    # Streamlit 실행 환경 확인
    try:
        import streamlit as st
        # Streamlit Cloud에서는 특정 옵션이 설정됨
        if hasattr(st, 'config') and st.config.get_option('server.headless'):
            return 'streamlit_cloud'
    except:
        pass
    # 로컬 개발 환경
    return 'local'

def _get_api_base():
    """환경에 맞는 API 기본 URL 반환"""
    env = _detect_environment()
    
    # 환경 변수에서 명시적으로 설정된 경우 우선 사용
    explicit_url = os.getenv('API_BASE_URL', '').strip()
    if explicit_url:
        # /api가 포함되어 있으면 그대로 사용, 없으면 추가
        if not explicit_url.endswith('/api'):
            explicit_url = explicit_url.rstrip('/') + '/api'
        return explicit_url.rstrip('/api')  # /api 제거 (나중에 _url에서 추가)
    
    # 배포 환경에서는 상대 경로 사용 (같은 서버의 /api)
    if env == 'streamlit_cloud':
        return ''  # 상대 경로 사용
    
    # 로컬 개발 환경 - 명확하게 localhost:5000 사용
    return 'http://localhost:5000'

API_BASE = _get_api_base()
TIMEOUT = 15
HEADERS = {'Content-Type': 'application/json'}

# API 모드 확인 및 Supabase 서비스 초기화
_api_mode = os.getenv('API_MODE', '').strip().lower() or 'flask'
_supabase_service = None

if _api_mode == 'supabase':
    try:
        from api.services.supabase_service import supabase_service
        _supabase_service = supabase_service
    except ImportError:
        # Supabase 서비스가 없으면 Flask API 사용
        _api_mode = 'flask'


def _url(path):
    """경로 앞에 / 없으면 붙임. /api 로 시작하는 path 사용."""
    p = path if path.startswith('/') else '/' + path
    
    # API_BASE가 비어있으면 상대 경로 사용 (배포 환경)
    if not API_BASE:
        return p
    
    return f"{API_BASE}{p}"


def _check(res, allow_404=False):
    """응답 검사. 성공이면 data 반환, 실패면 (None, error_message)."""
    try:
        j = res.json()
    except Exception:
        j = {}
    if allow_404 and res.status_code == 404:
        return None, (j.get('error', {}).get('message') or res.text or 'Not Found')
    if res.status_code >= 400:
        msg = j.get('error', {}).get('message') or res.reason or f'HTTP {res.status_code}'
        return None, msg
    if j.get('success') is False:
        msg = j.get('error', {}).get('message') or '처리 실패'
        return None, msg
    return j.get('data'), None


# --- Stats ---
def get_stats():
    """GET /api/stats 또는 Supabase 직접 통계 계산"""
    # Supabase 직접 연결 모드일 때
    if _api_mode == 'supabase' and _supabase_service:
        try:
            sites = _supabase_service.get_all_sites()
            personnel = _supabase_service.get_all_personnel()
            certificates = _supabase_service.get_all_certificates()
            
            # 통계 계산
            stats = {
                'total_sites': len(sites),
                'assigned_sites': len([s for s in sites if s.get('배정상태') == '배정완료']),
                'unassigned_sites': len([s for s in sites if s.get('배정상태') == '미배정']),
                'total_personnel': len(personnel),
                'available_personnel': len([p for p in personnel if p.get('현재상태') == '투입가능']),
                'total_certificates': len(certificates),
                'available_certificates': len([c for c in certificates if c.get('사용가능여부') == '사용가능']),
            }
            return stats, None
        except Exception as e:
            return None, f"Supabase 통계 계산 실패: {str(e)}"
    
    # Flask API 모드
    try:
        r = requests.get(_url('/api/stats'), timeout=TIMEOUT, headers=HEADERS)
        return _check(r)
    except Exception as e:
        return None, f"API 연결 실패: {str(e)}"


# --- Sites ---
def get_sites(company=None, status=None, state=None, limit=None, offset=None):
    """GET /api/sites 또는 Supabase 직접 조회"""
    # Supabase 직접 연결 모드일 때
    if _api_mode == 'supabase' and _supabase_service:
        try:
            result = _supabase_service.get_sites_paginated(
                company=company,
                status=status,
                state=state,
                limit=limit,
                offset=offset or 0
            )
            return result, None
        except Exception as e:
            return None, f"Supabase 조회 실패: {str(e)}"
    
    # Flask API 모드
    params = {}
    if company:
        params['company'] = company
    if status:
        params['status'] = status
    if state:
        params['state'] = state
    if limit:
        params['limit'] = limit
    if offset is not None:
        params['offset'] = offset
    try:
        r = requests.get(_url('/api/sites'), params=params, timeout=TIMEOUT, headers=HEADERS)
        return _check(r)
    except Exception as e:
        return None, f"API 연결 실패: {str(e)}"


def search_sites(q):
    """GET /api/sites/search 또는 Supabase 직접 검색"""
    if not (q or str(q).strip()):
        return [], None
    
    # Supabase 직접 연결 모드일 때
    if _api_mode == 'supabase' and _supabase_service:
        try:
            all_sites = _supabase_service.get_all_sites()
            # 클라이언트 사이드 검색
            query = q.strip().lower()
            filtered = [
                s for s in all_sites
                if query in (s.get('현장명', '') or '').lower() or
                   query in (s.get('주소', '') or '').lower()
            ]
            return filtered, None
        except Exception as e:
            return None, f"Supabase 검색 실패: {str(e)}"
    
    # Flask API 모드
    try:
        r = requests.get(_url('/api/sites/search'), params={'q': q.strip()}, timeout=TIMEOUT, headers=HEADERS)
        return _check(r)
    except Exception as e:
        return None, f"API 연결 실패: {str(e)}"


def get_site(site_id):
    """GET /api/sites/<id> 또는 Supabase 직접 조회"""
    # Supabase 직접 연결 모드일 때
    if _api_mode == 'supabase' and _supabase_service:
        try:
            site = _supabase_service.get_site_by_id(site_id)
            if site:
                return site, None
            else:
                return None, "현장을 찾을 수 없습니다"
        except Exception as e:
            return None, f"Supabase 조회 실패: {str(e)}"
    
    # Flask API 모드
    try:
        r = requests.get(_url(f'/api/sites/{site_id}'), timeout=TIMEOUT, headers=HEADERS)
        return _check(r, allow_404=True)
    except Exception as e:
        return None, f"API 연결 실패: {str(e)}"


def create_site(payload):
    """POST /api/sites. 현장ID는 서버에서 자동 부여 가능."""
    r = requests.post(_url('/api/sites'), json=payload, timeout=TIMEOUT, headers=HEADERS)
    return _check(r)


def assign_site(site_id, manager_id, certificate_id, version=None):
    """POST /api/sites/<id>/assign 또는 Supabase 직접 배정"""
    # Supabase 직접 연결 모드일 때
    if _api_mode == 'supabase' and _supabase_service:
        try:
            _supabase_service.assign_site(site_id, manager_id, certificate_id)
            return {'success': True}, None
        except Exception as e:
            return None, f"Supabase 배정 실패: {str(e)}"
    
    # Flask API 모드
    body = {'manager_id': manager_id, 'certificate_id': certificate_id}
    if version:
        body['version'] = version
    h = dict(HEADERS)
    if version:
        h['If-Match'] = version
    try:
        r = requests.post(_url(f'/api/sites/{site_id}/assign'), json=body, timeout=TIMEOUT, headers=h)
        return _check(r)
    except Exception as e:
        return None, f"API 연결 실패: {str(e)}"


def unassign_site(site_id, version=None):
    """POST /api/sites/<id>/unassign 또는 Supabase 직접 해제"""
    # Supabase 직접 연결 모드일 때
    if _api_mode == 'supabase' and _supabase_service:
        try:
            _supabase_service.unassign_site(site_id)
            return {'success': True}, None
        except Exception as e:
            return None, f"Supabase 해제 실패: {str(e)}"
    
    # Flask API 모드
    body = {}
    if version:
        body['version'] = version
    h = dict(HEADERS)
    if version:
        h['If-Match'] = version
    try:
        r = requests.post(_url(f'/api/sites/{site_id}/unassign'), json=body or None, timeout=TIMEOUT, headers=h)
        return _check(r)
    except Exception as e:
        return None, f"API 연결 실패: {str(e)}"


# --- Personnel ---
def get_personnel(status=None, role=None):
    """GET /api/personnel 또는 Supabase 직접 조회"""
    # Supabase 직접 연결 모드일 때
    if _api_mode == 'supabase' and _supabase_service:
        try:
            personnel_list = _supabase_service.get_all_personnel()
            # 필터링 (클라이언트 사이드)
            if status:
                personnel_list = [p for p in personnel_list if p.get('현재상태', '') == status]
            if role:
                # role 필터는 직책(position)으로 필터링
                personnel_list = [p for p in personnel_list if p.get('직책', '') == role]
            return personnel_list, None
        except Exception as e:
            return None, f"Supabase 조회 실패: {str(e)}"
    
    # Flask API 모드
    params = {}
    if status:
        params['status'] = status
    if role:
        params['role'] = role
    try:
        r = requests.get(_url('/api/personnel'), params=params or None, timeout=TIMEOUT, headers=HEADERS)
        return _check(r)
    except Exception as e:
        return None, f"API 연결 실패: {str(e)}"


# --- Certificates ---
def get_certificates(available=None):
    """GET /api/certificates 또는 Supabase 직접 조회"""
    # Supabase 직접 연결 모드일 때
    if _api_mode == 'supabase' and _supabase_service:
        try:
            cert_list = _supabase_service.get_all_certificates()
            # 필터링 (클라이언트 사이드)
            if available is True or available == 'true':
                cert_list = [c for c in cert_list if c.get('사용가능여부', '') == '사용가능']
            elif available is False or available == 'false':
                cert_list = [c for c in cert_list if c.get('사용가능여부', '') != '사용가능']
            return cert_list, None
        except Exception as e:
            return None, f"Supabase 조회 실패: {str(e)}"
    
    # Flask API 모드
    params = {}
    if available is True or available == 'true':
        params['available'] = 'true'
    elif available is False or available == 'false':
        params['available'] = 'false'
    try:
        r = requests.get(_url('/api/certificates'), params=params or None, timeout=TIMEOUT, headers=HEADERS)
        return _check(r)
    except Exception as e:
        return None, f"API 연결 실패: {str(e)}"


def create_certificate(payload):
    """POST /api/certificates. 자격증ID·소유자ID는 서버에서 자동 부여."""
    r = requests.post(_url('/api/certificates'), json=payload, timeout=TIMEOUT, headers=HEADERS)
    return _check(r)


def check_api_connection():
    """
    GET /api/health 로 연결 확인.
    배포 환경에서는 실패해도 UI는 표시되도록 처리.
    Supabase 직접 연결 모드일 때는 체크를 건너뜀.
    
    Returns:
        tuple: (is_connected: bool, error_message: str | None)
        - is_connected: 연결 성공 여부
        - error_message: 실패 시 구체적인 에러 메시지, 성공 시 None
    """
    env = _detect_environment()
    
    # API 모드 확인
    api_mode = os.getenv('API_MODE', '').strip().lower() or 'flask'
    
    # Supabase 직접 연결 모드일 때는 API 연결 체크 불필요
    if api_mode == 'supabase':
        supabase_url = os.getenv('SUPABASE_URL', '').strip()
        supabase_anon_key = os.getenv('SUPABASE_ANON_KEY', '').strip()
        if supabase_url and supabase_anon_key:
            # Supabase 설정이 있으면 성공으로 처리 (브라우저에서 직접 연결)
            return True, None
        else:
            return False, "Supabase 설정이 없습니다. SUPABASE_URL과 SUPABASE_ANON_KEY를 확인하세요."
    
    # 배포 환경에서는 API 연결 체크를 건너뛰거나 더 관대하게 처리
    if env == 'streamlit_cloud':
        # 배포 환경에서는 API가 별도 서버에 있을 수 있으므로
        # 연결 실패해도 UI는 표시
        try:
            r = requests.get(_url('/api/health'), timeout=3)
            if r.status_code == 200:
                return True, None
        except:
            # 배포 환경에서는 조용히 실패 처리
            return False, "API 서버 연결 실패 (배포 환경에서는 별도 API 서버 필요)"
    
    # 로컬 개발 환경에서는 상세한 에러 메시지 제공
    try:
        r = requests.get(_url('/api/health'), timeout=5)
        if r.status_code == 200:
            return True, None
        else:
            return False, f"API 서버 응답 오류: HTTP {r.status_code}"
    except requests.exceptions.Timeout:
        api_url = _url('/api/health')
        return False, f"API 서버 연결 시간 초과 (5초). 서버가 실행 중인지 확인하세요. ({api_url})"
    except requests.exceptions.ConnectionError:
        api_url = _url('/api/health')
        return False, f"API 서버에 연결할 수 없습니다. Flask 서버가 실행 중인지 확인하세요. ({api_url})"
    except Exception as e:
        return False, f"연결 확인 중 오류 발생: {str(e)}"
