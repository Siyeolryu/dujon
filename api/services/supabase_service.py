"""
Supabase DB 연동 서비스
- sites(현장정보), personnel(인력풀), certificates(자격증풀)
- Google Sheets API와 동일한 반환 형식으로 API 라우트 호환
"""
import os
from typing import List, Dict, Any, Optional

# 환경 변수: SUPABASE_URL, SUPABASE_KEY (또는 SUPABASE_ANON_KEY)
SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").strip()
SUPABASE_KEY = (os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY") or "").strip()

# 테이블 이름 (시트1/2/3 대응)
TABLE_SITES = "sites"
TABLE_PERSONNEL = "personnel"
TABLE_CERTIFICATES = "certificates"


def _client():
    """Supabase 클라이언트 (지연 생성)"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "SUPABASE_URL, SUPABASE_KEY를 설정해 주세요. .env에 추가하세요."
        )
    try:
        from supabase import create_client
    except ImportError:
        raise ImportError("supabase 패키지가 필요합니다. pip install supabase")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def _row_to_site(row: Dict) -> Dict:
    """DB 행 -> API 현장 딕셔너리 (Sheets 응답과 동일 키)"""
    if not row:
        return {}
    return {
        "현장ID": row.get("현장ID") or "",
        "현장명": row.get("현장명") or "",
        "건축주명": row.get("건축주명") or "",
        "회사구분": row.get("회사구분") or "",
        "주소": row.get("주소") or "",
        "위도": row.get("위도") or "",
        "경도": row.get("경도") or "",
        "건축허가일": row.get("건축허가일") or "",
        "착공예정일": row.get("착공예정일") or "",
        "준공일": row.get("준공일") or "",
        "현장상태": row.get("현장상태") or "",
        "특이사항": row.get("특이사항") or "",
        "담당소장ID": row.get("담당소장ID") or "",
        "담당소장명": row.get("담당소장명") or "",
        "담당소장연락처": row.get("담당소장연락처") or "",
        "사용자격증ID": row.get("사용자격증ID") or "",
        "자격증명": row.get("자격증명") or "",
        "자격증소유자명": row.get("자격증소유자명") or "",
        "자격증소유자연락처": row.get("자격증소유자연락처") or "",
        "준공필증파일URL": row.get("준공필증파일URL") or "",
        "배정상태": row.get("배정상태") or "",
        "등록일": row.get("등록일") or "",
        "수정일": row.get("수정일") or "",
    }


def _row_to_personnel(row: Dict) -> Dict:
    """DB 행 -> API 인력 딕셔너리"""
    if not row:
        return {}
    return {
        "인력ID": row.get("인력ID") or "",
        "성명": row.get("성명") or "",
        "직책": row.get("직책") or "",
        "소속": row.get("소속") or "",
        "연락처": row.get("연락처") or "",
        "이메일": row.get("이메일") or "",
        "보유자격증": row.get("보유자격증") or "",
        "현재상태": row.get("현재상태") or "",
        "현재담당현장수": row.get("현재담당현장수") or "",
        "비고": row.get("비고") or "",
        "입사일": row.get("입사일") or "",
        "등록일": row.get("등록일") or "",
    }


def _row_to_certificate(row: Dict) -> Dict:
    """DB 행 -> API 자격증 딕셔너리"""
    if not row:
        return {}
    return {
        "자격증ID": row.get("자격증ID") or "",
        "자격증명": row.get("자격증명") or "",
        "자격증번호": row.get("자격증번호") or "",
        "소유자ID": row.get("소유자ID") or "",
        "소유자명": row.get("소유자명") or "",
        "소유자연락처": row.get("소유자연락처") or "",
        "발급기관": row.get("발급기관") or "",
        "취득일": row.get("취득일") or "",
        "유효기간": row.get("유효기간") or "",
        "사용가능여부": row.get("사용가능여부") or "",
        "현재사용현장ID": row.get("현재사용현장ID") or "",
        "비고": row.get("비고") or "",
        "등록일": row.get("등록일") or "",
    }


class SupabaseService:
    """SheetsService와 호환되는 Supabase 백엔드"""

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            self._client = _client()
        return self._client

    # ---- 읽기 (SheetsService와 동일 시그니처) ----
    def get_all_sites(self) -> List[Dict]:
        r = self._get_client().table(TABLE_SITES).select("*").order("현장ID").execute()
        return [_row_to_site(row) for row in (r.data or [])]

    def get_site_by_id(self, site_id: str) -> Optional[Dict]:
        r = self._get_client().table(TABLE_SITES).select("*").eq("현장ID", site_id).limit(1).execute()
        rows = r.data or []
        return _row_to_site(rows[0]) if rows else None

    def get_all_personnel(self) -> List[Dict]:
        r = self._get_client().table(TABLE_PERSONNEL).select("*").order("인력ID").execute()
        return [_row_to_personnel(row) for row in (r.data or [])]

    def get_personnel_by_id(self, personnel_id: str) -> Optional[Dict]:
        r = self._get_client().table(TABLE_PERSONNEL).select("*").eq("인력ID", personnel_id).limit(1).execute()
        rows = r.data or []
        return _row_to_personnel(rows[0]) if rows else None

    def get_all_certificates(self) -> List[Dict]:
        r = self._get_client().table(TABLE_CERTIFICATES).select("*").order("자격증ID").execute()
        return [_row_to_certificate(row) for row in (r.data or [])]

    def get_certificate_by_id(self, cert_id: str) -> Optional[Dict]:
        r = self._get_client().table(TABLE_CERTIFICATES).select("*").eq("자격증ID", cert_id).limit(1).execute()
        rows = r.data or []
        return _row_to_certificate(rows[0]) if rows else None

    # ---- 쓰기: 통합 인터페이스 (라우트에서 사용) ----
    def create_site(self, data: Dict[str, Any]) -> None:
        """현장 한 건 추가"""
        payload = {k: (v or "") for k, v in data.items()}
        self._get_client().table(TABLE_SITES).insert(payload).execute()

    def update_site(self, site_id: str, data: Dict[str, Any]) -> None:
        """현장 수정 (수정일 자동 갱신 가능)"""
        if not data:
            return
        payload = {k: v for k, v in data.items()}
        self._get_client().table(TABLE_SITES).update(payload).eq("현장ID", site_id).execute()

    def create_personnel(self, data: Dict[str, Any]) -> None:
        self._get_client().table(TABLE_PERSONNEL).insert({k: (v or "") for k, v in data.items()}).execute()

    def update_personnel(self, personnel_id: str, data: Dict[str, Any]) -> None:
        if not data:
            return
        self._get_client().table(TABLE_PERSONNEL).update(data).eq("인력ID", personnel_id).execute()

    def create_certificate(self, data: Dict[str, Any]) -> None:
        self._get_client().table(TABLE_CERTIFICATES).insert({k: (v or "") for k, v in data.items()}).execute()

    def update_certificate(self, cert_id: str, data: Dict[str, Any]) -> None:
        if not data:
            return
        self._get_client().table(TABLE_CERTIFICATES).update(data).eq("자격증ID", cert_id).execute()

    def assign_site(self, site_id: str, manager_id: str, certificate_id: str) -> None:
        """소장·자격증 배정: 현장/인력/자격증 테이블 일괄 업데이트"""
        now = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        client = self._get_client()

        site = self.get_site_by_id(site_id)
        manager = self.get_personnel_by_id(manager_id)
        cert = self.get_certificate_by_id(certificate_id)
        if not site or not manager or not cert:
            raise ValueError("site/manager/certificate not found")

        # 현장: 담당소장ID, 담당소장명/연락처, 사용자격증ID, 자격증명/소유자명/연락처, 배정상태, 수정일
        client.table(TABLE_SITES).update({
            "담당소장ID": manager_id,
            "담당소장명": manager.get("성명") or "",
            "담당소장연락처": manager.get("연락처") or "",
            "사용자격증ID": certificate_id,
            "자격증명": cert.get("자격증명") or "",
            "자격증소유자명": cert.get("소유자명") or "",
            "자격증소유자연락처": cert.get("소유자연락처") or "",
            "배정상태": "배정완료",
            "수정일": now,
        }).eq("현장ID", site_id).execute()

        # 인력: 현재상태, 현재담당현장수
        cur_count = int(manager.get("현재담당현장수") or 0) + 1
        client.table(TABLE_PERSONNEL).update({
            "현재상태": "투입중",
            "현재담당현장수": str(cur_count),
        }).eq("인력ID", manager_id).execute()

        # 자격증: 사용가능여부, 현재사용현장ID
        client.table(TABLE_CERTIFICATES).update({
            "사용가능여부": "사용중",
            "현재사용현장ID": site_id,
        }).eq("자격증ID", certificate_id).execute()

    def unassign_site(self, site_id: str) -> None:
        """소장 배정 해제"""
        site = self.get_site_by_id(site_id)
        if not site:
            raise ValueError("site not found")
        manager_id = (site.get("담당소장ID") or "").strip()
        cert_id = (site.get("사용자격증ID") or "").strip()
        now = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        client = self._get_client()

        client.table(TABLE_SITES).update({
            "담당소장ID": "",
            "담당소장명": "",
            "담당소장연락처": "",
            "사용자격증ID": "",
            "자격증명": "",
            "자격증소유자명": "",
            "자격증소유자연락처": "",
            "배정상태": "미배정",
            "수정일": now,
        }).eq("현장ID", site_id).execute()

        if manager_id:
            manager = self.get_personnel_by_id(manager_id)
            if manager:
                cur_count = max(0, int(manager.get("현재담당현장수") or 0) - 1)
                upd = {"현재담당현장수": str(cur_count)}
                if cur_count <= 0:
                    upd["현재상태"] = "투입가능"
                client.table(TABLE_PERSONNEL).update(upd).eq("인력ID", manager_id).execute()

        if cert_id:
            client.table(TABLE_CERTIFICATES).update({
                "사용가능여부": "사용가능",
                "현재사용현장ID": "",
            }).eq("자격증ID", cert_id).execute()


supabase_service = SupabaseService()
