"""
Streamlit용 REST API 클라이언트.
기존 Flask API (API_BASE_URL)를 호출합니다.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv('API_BASE_URL', 'http://localhost:5000').rstrip('/')
TIMEOUT = 15
HEADERS = {'Content-Type': 'application/json'}


def _url(path):
    """경로 앞에 / 없으면 붙임. /api 로 시작하는 path 사용."""
    p = path if path.startswith('/') else '/' + path
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
    """GET /api/stats"""
    r = requests.get(_url('/api/stats'), timeout=TIMEOUT, headers=HEADERS)
    return _check(r)


# --- Sites ---
def get_sites(company=None, status=None, state=None, limit=None, offset=None):
    """GET /api/sites?company=&status=&state=&limit=&offset="""
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
    r = requests.get(_url('/api/sites'), params=params, timeout=TIMEOUT, headers=HEADERS)
    return _check(r)


def search_sites(q):
    """GET /api/sites/search?q="""
    if not (q or str(q).strip()):
        return [], None
    r = requests.get(_url('/api/sites/search'), params={'q': q.strip()}, timeout=TIMEOUT, headers=HEADERS)
    return _check(r)


def get_site(site_id):
    """GET /api/sites/<id>"""
    r = requests.get(_url(f'/api/sites/{site_id}'), timeout=TIMEOUT, headers=HEADERS)
    return _check(r, allow_404=True)


def create_site(payload):
    """POST /api/sites. 현장ID는 서버에서 자동 부여 가능."""
    r = requests.post(_url('/api/sites'), json=payload, timeout=TIMEOUT, headers=HEADERS)
    return _check(r)


def assign_site(site_id, manager_id, certificate_id, version=None):
    """POST /api/sites/<id>/assign"""
    body = {'manager_id': manager_id, 'certificate_id': certificate_id}
    if version:
        body['version'] = version
    h = dict(HEADERS)
    if version:
        h['If-Match'] = version
    r = requests.post(_url(f'/api/sites/{site_id}/assign'), json=body, timeout=TIMEOUT, headers=h)
    return _check(r)


def unassign_site(site_id, version=None):
    """POST /api/sites/<id>/unassign"""
    body = {}
    if version:
        body['version'] = version
    h = dict(HEADERS)
    if version:
        h['If-Match'] = version
    r = requests.post(_url(f'/api/sites/{site_id}/unassign'), json=body or None, timeout=TIMEOUT, headers=h)
    return _check(r)


# --- Personnel ---
def get_personnel(status=None, role=None):
    """GET /api/personnel"""
    params = {}
    if status:
        params['status'] = status
    if role:
        params['role'] = role
    r = requests.get(_url('/api/personnel'), params=params or None, timeout=TIMEOUT, headers=HEADERS)
    return _check(r)


# --- Certificates ---
def get_certificates(available=None):
    """GET /api/certificates. available: True/'true' | False/'false' | None(전체)"""
    params = {}
    if available is True or available == 'true':
        params['available'] = 'true'
    elif available is False or available == 'false':
        params['available'] = 'false'
    r = requests.get(_url('/api/certificates'), params=params or None, timeout=TIMEOUT, headers=HEADERS)
    return _check(r)


def create_certificate(payload):
    """POST /api/certificates. 자격증ID·소유자ID는 서버에서 자동 부여."""
    r = requests.post(_url('/api/certificates'), json=payload, timeout=TIMEOUT, headers=HEADERS)
    return _check(r)


def check_api_connection():
    """
    GET /api/health 로 연결 확인.
    
    Returns:
        tuple: (is_connected: bool, error_message: str | None)
        - is_connected: 연결 성공 여부
        - error_message: 실패 시 구체적인 에러 메시지, 성공 시 None
    """
    try:
        r = requests.get(_url('/api/health'), timeout=5)
        if r.status_code == 200:
            return True, None
        else:
            return False, f"API 서버 응답 오류: HTTP {r.status_code}"
    except requests.exceptions.Timeout:
        return False, f"API 서버 연결 시간 초과 (5초). 서버가 실행 중인지 확인하세요. ({API_BASE}/api/health)"
    except requests.exceptions.ConnectionError:
        return False, f"API 서버에 연결할 수 없습니다. Flask 서버가 실행 중인지 확인하세요. ({API_BASE}/api/health)"
    except Exception as e:
        return False, f"연결 확인 중 오류 발생: {str(e)}"
