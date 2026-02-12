"""
httpx 기반 비동기 Flask API 클라이언트.
기존 streamlit_utils/api_client.py 패턴을 async로 재구현.
"""
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000").rstrip("/")
TIMEOUT = 15.0


def _url(path: str) -> str:
    p = path if path.startswith("/") else "/" + path
    return f"{API_BASE_URL}{p}"


def _check(res: httpx.Response) -> tuple:
    """응답 검사. (data, error_message) 튜플 반환."""
    try:
        j = res.json()
    except Exception:
        j = {}
    if res.status_code >= 400:
        msg = j.get("error", {}).get("message") or res.reason_phrase or f"HTTP {res.status_code}"
        return None, msg
    if j.get("success") is False:
        msg = j.get("error", {}).get("message") or "처리 실패"
        return None, msg
    return j.get("data"), None


class ApiClient:
    """httpx.AsyncClient 래퍼. 모듈 전역 인스턴스로 사용."""

    def __init__(self):
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=TIMEOUT)
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # ── Stats & Health ──

    async def health_check(self) -> tuple:
        try:
            c = await self._get_client()
            r = await c.get(_url("/api/health"))
            if r.status_code == 200:
                return {"status": "healthy"}, None
            return None, f"HTTP {r.status_code}"
        except Exception as e:
            return None, f"연결 실패: {e}"

    async def get_stats(self) -> tuple:
        try:
            c = await self._get_client()
            r = await c.get(_url("/api/stats"))
            return _check(r)
        except Exception as e:
            return None, f"API 연결 실패: {e}"

    # ── Sites ──

    async def get_sites(self, company=None, status=None, state=None,
                        limit=None, offset=None) -> tuple:
        params = {}
        if company:
            params["company"] = company
        if status:
            params["status"] = status
        if state:
            params["state"] = state
        if limit:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        try:
            c = await self._get_client()
            r = await c.get(_url("/api/sites"), params=params)
            return _check(r)
        except Exception as e:
            return None, f"API 연결 실패: {e}"

    async def search_sites(self, q: str) -> tuple:
        if not q or not q.strip():
            return [], None
        try:
            c = await self._get_client()
            r = await c.get(_url("/api/sites/search"), params={"q": q.strip()})
            return _check(r)
        except Exception as e:
            return None, f"API 연결 실패: {e}"

    async def get_site(self, site_id: str) -> tuple:
        try:
            c = await self._get_client()
            r = await c.get(_url(f"/api/sites/{site_id}"))
            return _check(r)
        except Exception as e:
            return None, f"API 연결 실패: {e}"

    async def create_site(self, payload: dict) -> tuple:
        try:
            c = await self._get_client()
            r = await c.post(_url("/api/sites"), json=payload)
            return _check(r)
        except Exception as e:
            return None, f"API 연결 실패: {e}"

    async def update_site(self, site_id: str, payload: dict) -> tuple:
        try:
            c = await self._get_client()
            headers = {}
            if "version" in payload:
                headers["If-Match"] = payload["version"]
            r = await c.put(_url(f"/api/sites/{site_id}"), json=payload, headers=headers)
            return _check(r)
        except Exception as e:
            return None, f"API 연결 실패: {e}"

    async def assign_site(self, site_id: str, manager_id: str,
                          certificate_id: str, version: str | None = None) -> tuple:
        body = {"manager_id": manager_id, "certificate_id": certificate_id}
        headers = {}
        if version:
            body["version"] = version
            headers["If-Match"] = version
        try:
            c = await self._get_client()
            r = await c.post(_url(f"/api/sites/{site_id}/assign"), json=body, headers=headers)
            return _check(r)
        except Exception as e:
            return None, f"API 연결 실패: {e}"

    async def unassign_site(self, site_id: str, version: str | None = None) -> tuple:
        body = {}
        headers = {}
        if version:
            body["version"] = version
            headers["If-Match"] = version
        try:
            c = await self._get_client()
            r = await c.post(_url(f"/api/sites/{site_id}/unassign"),
                             json=body or None, headers=headers)
            return _check(r)
        except Exception as e:
            return None, f"API 연결 실패: {e}"

    # ── Personnel ──

    async def get_personnel(self, status=None, role=None) -> tuple:
        params = {}
        if status:
            params["status"] = status
        if role:
            params["role"] = role
        try:
            c = await self._get_client()
            r = await c.get(_url("/api/personnel"), params=params)
            return _check(r)
        except Exception as e:
            return None, f"API 연결 실패: {e}"

    async def get_personnel_detail(self, personnel_id: str) -> tuple:
        try:
            c = await self._get_client()
            r = await c.get(_url(f"/api/personnel/{personnel_id}"))
            return _check(r)
        except Exception as e:
            return None, f"API 연결 실패: {e}"

    async def update_personnel(self, personnel_id: str, payload: dict) -> tuple:
        try:
            c = await self._get_client()
            r = await c.put(_url(f"/api/personnel/{personnel_id}"), json=payload)
            return _check(r)
        except Exception as e:
            return None, f"API 연결 실패: {e}"

    # ── Certificates ──

    async def get_certificates(self, available: str | None = None) -> tuple:
        params = {}
        if available is not None:
            params["available"] = available
        try:
            c = await self._get_client()
            r = await c.get(_url("/api/certificates"), params=params)
            return _check(r)
        except Exception as e:
            return None, f"API 연결 실패: {e}"

    async def get_certificate_detail(self, cert_id: str) -> tuple:
        try:
            c = await self._get_client()
            r = await c.get(_url(f"/api/certificates/{cert_id}"))
            return _check(r)
        except Exception as e:
            return None, f"API 연결 실패: {e}"

    async def create_certificate(self, payload: dict) -> tuple:
        try:
            c = await self._get_client()
            r = await c.post(_url("/api/certificates"), json=payload)
            return _check(r)
        except Exception as e:
            return None, f"API 연결 실패: {e}"

    async def update_certificate(self, cert_id: str, payload: dict) -> tuple:
        try:
            c = await self._get_client()
            r = await c.put(_url(f"/api/certificates/{cert_id}"), json=payload)
            return _check(r)
        except Exception as e:
            return None, f"API 연결 실패: {e}"


# 모듈 전역 인스턴스
api = ApiClient()
