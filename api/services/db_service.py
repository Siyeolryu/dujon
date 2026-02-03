"""
통합 DB 서비스 - Supabase 또는 Google Sheets 백엔드

환경 변수:
- DB_BACKEND=supabase  → Supabase 사용 (기본값으로 준비)
- DB_BACKEND=sheets    → Google Sheets 사용
- SUPABASE_URL, SUPABASE_KEY  → Supabase 연동 시 필수
"""
import os
from typing import List, Dict, Any, Optional

_BACKEND = (os.getenv("DB_BACKEND") or "supabase").strip().lower()
_USE_SUPABASE = _BACKEND == "supabase" or (os.getenv("USE_SUPABASE", "").strip().lower() in ("1", "true", "yes"))


def _get_backend():
    """현재 백엔드 서비스 반환 (SheetsService 호환 읽기 + create/update/assign/unassign)"""
    if _USE_SUPABASE:
        from api.services.supabase_service import supabase_service
        return supabase_service
    from api.services.sheets_service import sheets_service
    return _SheetsAdapter(sheets_service)


class _SheetsAdapter:
    """SheetsService를 create_site/update_site/assign_site/unassign_site 인터페이스로 감쌈"""
    def __init__(self, sheets):
        self._s = sheets
        from api.services.sheets_service import SHEET_SITES, SHEET_PERSONNEL, SHEET_CERTIFICATES
        self._sites = SHEET_SITES
        self._personnel = SHEET_PERSONNEL
        self._certs = SHEET_CERTIFICATES

    def get_all_sites(self): return self._s.get_all_sites()
    def get_site_by_id(self, site_id): return self._s.get_site_by_id(site_id)
    def get_all_personnel(self): return self._s.get_all_personnel()
    def get_personnel_by_id(self, pid): return self._s.get_personnel_by_id(pid)
    def get_all_certificates(self): return self._s.get_all_certificates()
    def get_certificate_by_id(self, cid): return self._s.get_certificate_by_id(cid)

    def create_site(self, data: Dict[str, Any]) -> None:
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d")
        row = [
            data.get("현장ID", ""),
            data.get("현장명", ""),
            data.get("건축주명", ""),
            data.get("회사구분", ""),
            data.get("주소", ""),
            data.get("위도", ""),
            data.get("경도", ""),
            data.get("건축허가일", ""),
            data.get("착공예정일", ""),
            data.get("준공일", ""),
            data.get("현장상태", "건축허가"),
            data.get("특이사항", ""),
            data.get("담당소장ID", ""),
            data.get("담당소장명", ""),
            data.get("담당소장연락처", ""),
            data.get("사용자격증ID", ""),
            data.get("자격증명", ""),
            data.get("자격증소유자명", ""),
            data.get("자격증소유자연락처", ""),
            data.get("준공필증파일URL", ""),
            data.get("배정상태", "미배정"),
            now,
            now,
        ]
        self._s.append_row(self._sites, row)

    def update_site(self, site_id: str, data: Dict[str, Any]) -> None:
        from datetime import datetime
        row_num = self._s.find_row_by_id(self._sites, site_id)
        if not row_num:
            raise ValueError(f"현장을 찾을 수 없습니다: {site_id}")
        column_map = {
            "현장명": "B", "건축주명": "C", "회사구분": "D", "주소": "E", "위도": "F", "경도": "G",
            "건축허가일": "H", "착공예정일": "I", "준공일": "J",
            "현장상태": "K", "특이사항": "L", "담당소장ID": "M",
            "사용자격증ID": "P", "준공필증파일URL": "T", "배정상태": "U",
        }
        updates = []
        for field, col in column_map.items():
            if field in data:
                updates.append({"range": f"{self._sites}!{col}{row_num}", "values": [[data[field]]]})
        now = datetime.now().strftime("%Y-%m-%d")
        updates.append({"range": f"{self._sites}!W{row_num}", "values": [[now]]})
        if updates:
            self._s.batch_update(updates)

    def create_personnel(self, data: Dict[str, Any]) -> None:
        row = [
            data.get("인력ID", ""),
            data.get("성명", ""),
            data.get("직책", ""),
            data.get("소속", ""),
            data.get("연락처", ""),
            data.get("이메일", ""),
            data.get("보유자격증", ""),
            data.get("현재상태", ""),
            data.get("현재담당현장수", ""),
            data.get("비고", ""),
            data.get("입사일", ""),
            data.get("등록일", ""),
        ]
        self._s.append_row(self._personnel, row)

    def update_personnel(self, personnel_id: str, data: Dict[str, Any]) -> None:
        row_num = self._s.find_row_by_id(self._personnel, personnel_id)
        if not row_num:
            raise ValueError(f"인력을 찾을 수 없습니다: {personnel_id}")
        column_map = {
            "성명": "B", "직책": "C", "소속": "D", "연락처": "E", "이메일": "F",
            "보유자격증": "G", "현재상태": "H", "현재담당현장수": "I", "비고": "J",
            "입사일": "K", "등록일": "L",
        }
        updates = [{"range": f"{self._personnel}!{col}{row_num}", "values": [[data[field]]]}
                   for field, col in column_map.items() if field in data]
        if updates:
            self._s.batch_update(updates)

    def create_certificate(self, data: Dict[str, Any]) -> None:
        row = [
            data.get("자격증ID", ""),
            data.get("자격증명", ""),
            data.get("자격증번호", ""),
            data.get("소유자ID", ""),
            data.get("소유자명", ""),
            data.get("소유자연락처", ""),
            data.get("발급기관", ""),
            data.get("취득일", ""),
            data.get("유효기간", ""),
            data.get("사용가능여부", "사용가능"),
            data.get("현재사용현장ID", ""),
            data.get("비고", ""),
            data.get("등록일", ""),
        ]
        self._s.append_row(self._certs, row)

    def update_certificate(self, cert_id: str, data: Dict[str, Any]) -> None:
        row_num = self._s.find_row_by_id(self._certs, cert_id)
        if not row_num:
            raise ValueError(f"자격증을 찾을 수 없습니다: {cert_id}")
        column_map = {
            "자격증명": "B", "자격증번호": "C", "소유자ID": "D", "소유자명": "E", "소유자연락처": "F",
            "발급기관": "G", "취득일": "H", "유효기간": "I", "사용가능여부": "J",
            "현재사용현장ID": "K", "비고": "L", "등록일": "M",
        }
        updates = [{"range": f"{self._certs}!{col}{row_num}", "values": [[data[field]]]}
                   for field, col in column_map.items() if field in data]
        if updates:
            self._s.batch_update(updates)

    def assign_site(self, site_id: str, manager_id: str, certificate_id: str) -> None:
        from datetime import datetime
        site_row = self._s.find_row_by_id(self._sites, site_id)
        manager_row = self._s.find_row_by_id(self._personnel, manager_id)
        cert_row = self._s.find_row_by_id(self._certs, certificate_id)
        if not site_row or not manager_row or not cert_row:
            raise ValueError("site/manager/certificate row not found")
        manager = self._s.get_personnel_by_id(manager_id)
        now = datetime.now().strftime("%Y-%m-%d")
        cur_count = int(manager.get("현재담당현장수") or 0) + 1
        updates = [
            {"range": f"{self._sites}!M{site_row}", "values": [[manager_id]]},
            {"range": f"{self._sites}!P{site_row}", "values": [[certificate_id]]},
            {"range": f"{self._sites}!U{site_row}", "values": [["배정완료"]]},
            {"range": f"{self._sites}!W{site_row}", "values": [[now]]},
            {"range": f"{self._personnel}!I{manager_row}", "values": [[cur_count]]},
            {"range": f"{self._personnel}!H{manager_row}", "values": [["투입중"]]},
            {"range": f"{self._certs}!J{cert_row}", "values": [["사용중"]]},
            {"range": f"{self._certs}!K{cert_row}", "values": [[site_id]]},
        ]
        self._s.batch_update(updates)

    def unassign_site(self, site_id: str) -> None:
        from datetime import datetime
        site = self._s.get_site_by_id(site_id)
        if not site:
            raise ValueError("site not found")
        manager_id = (site.get("담당소장ID") or "").strip()
        cert_id = (site.get("사용자격증ID") or "").strip()
        site_row = self._s.find_row_by_id(self._sites, site_id)
        if not site_row:
            raise ValueError("site row not found")
        now = datetime.now().strftime("%Y-%m-%d")
        updates = [
            {"range": f"{self._sites}!M{site_row}", "values": [[""]]},
            {"range": f"{self._sites}!P{site_row}", "values": [[""]]},
            {"range": f"{self._sites}!U{site_row}", "values": [["미배정"]]},
            {"range": f"{self._sites}!W{site_row}", "values": [[now]]},
        ]
        if manager_id:
            manager_row = self._s.find_row_by_id(self._personnel, manager_id)
            if manager_row:
                manager = self._s.get_personnel_by_id(manager_id)
                cur_count = max(0, int(manager.get("현재담당현장수") or 0) - 1)
                updates.append({"range": f"{self._personnel}!I{manager_row}", "values": [[cur_count]]})
                if cur_count <= 1:
                    updates.append({"range": f"{self._personnel}!H{manager_row}", "values": [["투입가능"]]})
        if cert_id:
            cert_row = self._s.find_row_by_id(self._certs, cert_id)
            if cert_row:
                updates.append({"range": f"{self._certs}!J{cert_row}", "values": [["사용가능"]]})
                updates.append({"range": f"{self._certs}!K{cert_row}", "values": [[""]]})
        self._s.batch_update(updates)


# 싱글톤: 라우트에서 db 사용
_db = None


def get_db():
    """통합 DB 서비스 (Supabase 또는 Sheets)"""
    global _db
    if _db is None:
        _db = _get_backend()
    return _db
