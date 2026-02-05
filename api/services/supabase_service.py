"""
Supabase DB 연동 서비스 (정규화된 스키마 v2)
- 정규화된 스키마 사용: UUID PK, JOIN을 통한 관계 데이터 조회
- Google Sheets API와 동일한 반환 형식으로 API 라우트 호환
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# 환경 변수: SUPABASE_URL, SUPABASE_KEY (또는 SUPABASE_ANON_KEY)
SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").strip()
SUPABASE_KEY = (os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY") or "").strip()

# 테이블 이름 (정규화된 스키마 v2)
TABLE_SITES = "sites"
TABLE_PERSONNEL = "personnel"
TABLE_CERTIFICATES = "certificates"
TABLE_COMPANIES = "companies"
TABLE_CERTIFICATE_TYPES = "certificate_types"
TABLE_SITE_ASSIGNMENTS = "site_assignments"
TABLE_CERTIFICATE_ASSIGNMENTS = "certificate_assignments"


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


def _transform_site(site_row: Dict, assignments: List[Dict] = None, cert_assignments: List[Dict] = None, company: Dict = None) -> Dict:
    """정규화된 스키마의 현장 데이터 -> API 응답 형식 (한글 키)"""
    if not site_row:
        return {}
    
    # 활성 배정 정보 추출
    active_assignment = None
    if assignments:
        active_assignment = next((a for a in assignments if a.get('status') == '배정중'), None)
    
    active_cert_assignment = None
    if cert_assignments:
        active_cert_assignment = next((ca for ca in cert_assignments if ca.get('status') == '배정중'), None)
    
    # 날짜 형식 변환
    def _format_date(date_val):
        if not date_val:
            return ""
        if isinstance(date_val, str):
            return date_val[:10] if len(date_val) >= 10 else date_val
        return str(date_val)
    
    return {
        "현장ID": site_row.get("legacy_id") or site_row.get("id") or "",
        "현장명": site_row.get("name") or "",
        "건축주명": site_row.get("owner_name") or "",
        "회사구분": (company.get("name") if company and isinstance(company, dict) else "") or (company.get("short_name") if company and isinstance(company, dict) else ""),
        "주소": site_row.get("address") or "",
        "위도": str(site_row.get("latitude")) if site_row.get("latitude") is not None else "",
        "경도": str(site_row.get("longitude")) if site_row.get("longitude") is not None else "",
        "건축허가일": _format_date(site_row.get("permit_date")),
        "착공예정일": _format_date(site_row.get("start_date")),
        "준공일": _format_date(site_row.get("end_date")),
        "현장상태": site_row.get("status") or "건축허가",
        "특이사항": site_row.get("notes") or "",
        "담당소장ID": (active_assignment.get("personnel") or {}).get("legacy_id") or (active_assignment.get("personnel") or {}).get("id") if active_assignment and active_assignment.get("personnel") else "",
        "담당소장명": (active_assignment.get("personnel") or {}).get("name") if active_assignment and active_assignment.get("personnel") else "",
        "담당소장연락처": (active_assignment.get("personnel") or {}).get("phone") if active_assignment and active_assignment.get("personnel") else "",
        "사용자격증ID": (active_cert_assignment.get("certificate") or {}).get("legacy_id") or (active_cert_assignment.get("certificate") or {}).get("id") if active_cert_assignment and active_cert_assignment.get("certificate") else "",
        "자격증명": ((active_cert_assignment.get("certificate") or {}).get("cert_type") or {}).get("name") if active_cert_assignment and active_cert_assignment.get("certificate") else "",
        "자격증소유자명": ((active_cert_assignment.get("certificate") or {}).get("personnel") or {}).get("name") if active_cert_assignment and active_cert_assignment.get("certificate") else "",
        "자격증소유자연락처": ((active_cert_assignment.get("certificate") or {}).get("personnel") or {}).get("phone") if active_cert_assignment and active_cert_assignment.get("certificate") else "",
        "준공필증파일URL": site_row.get("completion_doc_url") or "",
        "배정상태": site_row.get("assignment_status") or "미배정",
        "등록일": _format_date(site_row.get("created_at")),
        "수정일": _format_date(site_row.get("updated_at")),
    }


def _transform_personnel(personnel_row: Dict, company: Dict = None) -> Dict:
    """정규화된 스키마의 인력 데이터 -> API 응답 형식"""
    if not personnel_row:
        return {}
    
    def _format_date(date_val):
        if not date_val:
            return ""
        if isinstance(date_val, str):
            return date_val[:10] if len(date_val) >= 10 else date_val
        return str(date_val)
    
    return {
        "인력ID": personnel_row.get("legacy_id") or personnel_row.get("id") or "",
        "성명": personnel_row.get("name") or "",
        "직책": personnel_row.get("position") or "",
        "소속": (company.get("name") if company and isinstance(company, dict) else "") or (company.get("short_name") if company and isinstance(company, dict) else ""),
        "연락처": personnel_row.get("phone") or "",
        "이메일": personnel_row.get("email") or "",
        "보유자격증": "",  # 정규화된 스키마에서는 별도 조회 필요
        "현재상태": personnel_row.get("status") or "투입가능",
        "현재담당현장수": str(personnel_row.get("current_site_count") or 0),
        "비고": personnel_row.get("notes") or "",
        "입사일": _format_date(personnel_row.get("join_date")),
        "등록일": _format_date(personnel_row.get("created_at")),
    }


def _transform_certificate(cert_row: Dict, cert_type: Dict = None, personnel: Dict = None) -> Dict:
    """정규화된 스키마의 자격증 데이터 -> API 응답 형식"""
    if not cert_row:
        return {}
    
    def _format_date(date_val):
        if not date_val:
            return ""
        if isinstance(date_val, str):
            return date_val[:10] if len(date_val) >= 10 else date_val
        return str(date_val)
    
    # 현재 사용 중인 현장 ID 조회 (별도 쿼리 필요하지만 일단 빈 값)
    current_site_id = ""
    
    return {
        "자격증ID": cert_row.get("legacy_id") or cert_row.get("id") or "",
        "자격증명": cert_type.get("name") if cert_type else "",
        "자격증번호": cert_row.get("cert_number") or "",
        "소유자ID": personnel.get("legacy_id") or personnel.get("id") if personnel else "",
        "소유자명": personnel.get("name") if personnel else "",
        "소유자연락처": personnel.get("phone") if personnel else "",
        "발급기관": "",  # 정규화된 스키마에 없음
        "취득일": _format_date(cert_row.get("issued_date")),
        "유효기간": _format_date(cert_row.get("expiry_date")),
        "사용가능여부": cert_row.get("status") or "사용가능",
        "현재사용현장ID": current_site_id,
        "비고": cert_row.get("notes") or "",
        "등록일": _format_date(cert_row.get("created_at")),
    }


class SupabaseService:
    """정규화된 스키마(v2)를 사용하는 Supabase 백엔드"""

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            self._client = _client()
        return self._client

    # ---- 읽기 (정규화된 스키마 사용, JOIN 포함) ----
    def get_all_sites(self, limit=None, offset=0) -> List[Dict]:
        """모든 현장 조회 (JOIN을 통한 관계 데이터 포함, 페이지네이션 지원)"""
        client = self._get_client()
        try:
            # JOIN을 통한 관계 데이터 조회
            query = client.table(TABLE_SITES).select(
                """
                *,
                company:companies(id, name, short_name),
                assignments:site_assignments(
                    id, role, status,
                    personnel:personnel(id, legacy_id, name, phone)
                ),
                cert_assignments:certificate_assignments(
                    id, status,
                    certificate:certificates(
                        id, legacy_id,
                        cert_type:certificate_types(name),
                        personnel:personnel(id, legacy_id, name, phone)
                    )
                )
                """
            ).order("created_at", desc=True)
            
            # 페이지네이션 적용
            if limit:
                query = query.range(offset, offset + limit - 1)
            
            r = query.execute()
            
            sites = []
            for site_row in (r.data or []):
                site = _transform_site(
                    site_row,
                    assignments=site_row.get("assignments", []),
                    cert_assignments=site_row.get("cert_assignments", []),
                    company=site_row.get("company")
                )
                sites.append(site)
            return sites
        except Exception as e:
            # 폴백: 단순 조회 (정규화되지 않은 스키마 호환)
            try:
                query = client.table(TABLE_SITES).select("*").order("created_at", desc=True)
                if limit:
                    query = query.range(offset, offset + limit - 1)
                r = query.execute()
                return [_transform_site(row) for row in (r.data or [])]
            except Exception:
                raise e

    def get_sites_paginated(self, company=None, status=None, state=None, limit=None, offset=0) -> Dict:
        """페이지네이션 지원 현장 조회 (필터 + 페이지네이션)"""
        client = self._get_client()
        try:
            # 기본 쿼리 구성
            query = client.table(TABLE_SITES).select(
                """
                *,
                company:companies(id, name, short_name),
                assignments:site_assignments(
                    id, role, status,
                    personnel:personnel(id, legacy_id, name, phone)
                ),
                cert_assignments:certificate_assignments(
                    id, status,
                    certificate:certificates(
                        id, legacy_id,
                        cert_type:certificate_types(name),
                        personnel:personnel(id, legacy_id, name, phone)
                    )
                )
                """
            )
            
            # 필터 적용
            if company:
                # 회사 ID로 필터링 (회사명으로 조회)
                company_query = client.table("companies").select("id").or_(f"name.eq.{company},short_name.eq.{company}").limit(1).execute()
                if company_query.data:
                    query = query.eq("company_id", company_query.data[0]["id"])
            
            # 정렬
            query = query.order("created_at", desc=True)
            
            # 페이지네이션 적용
            if limit:
                query = query.range(offset, offset + limit - 1)
            
            r = query.execute()
            
            sites = []
            for site_row in (r.data or []):
                site = _transform_site(
                    site_row,
                    assignments=site_row.get("assignments", []),
                    cert_assignments=site_row.get("cert_assignments", []),
                    company=site_row.get("company")
                )
                
                # 배정상태 필터 (클라이언트 사이드)
                if status and site.get('배정상태') != status:
                    continue
                
                # 현장상태 필터 (클라이언트 사이드)
                if state and site.get('현장상태') != state:
                    continue
                
                sites.append(site)
            
            # 전체 개수 조회 (필터 적용 전, 서버 사이드 필터만 적용)
            # 클라이언트 사이드 필터(status, state)는 정확한 total 계산이 어려우므로
            # 서버 사이드 필터(company)만 적용한 total 반환
            count_query = client.table(TABLE_SITES).select("id", count="exact")
            if company:
                company_query = client.table("companies").select("id").or_(f"name.eq.{company},short_name.eq.{company}").limit(1).execute()
                if company_query.data:
                    count_query = count_query.eq("company_id", company_query.data[0]["id"])
            count_result = count_query.execute()
            total_count = count_result.count if hasattr(count_result, 'count') else len(count_result.data or [])
            
            return {
                'data': sites,
                'total': total_count,  # 주의: 클라이언트 사이드 필터(status, state)는 total에 반영되지 않음
            }
        except Exception as e:
            # 폴백: 기존 방식
            all_sites = self.get_all_sites(limit=limit, offset=offset)
            filtered = all_sites
            if company:
                filtered = [s for s in filtered if s.get('회사구분') == company]
            if status:
                filtered = [s for s in filtered if s.get('배정상태') == status]
            if state:
                filtered = [s for s in filtered if s.get('현장상태') == state]
            return {
                'data': filtered,
                'total': len(filtered),
            }

    def get_site_by_id(self, site_id: str) -> Optional[Dict]:
        """현장 상세 조회 (legacy_id 또는 id로 조회)"""
        client = self._get_client()
        try:
            r = client.table(TABLE_SITES).select(
                """
                *,
                company:companies(id, name, short_name),
                assignments:site_assignments(
                    id, role, status,
                    personnel:personnel(id, legacy_id, name, phone)
                ),
                cert_assignments:certificate_assignments(
                    id, status,
                    certificate:certificates(
                        id, legacy_id,
                        cert_type:certificate_types(name),
                        personnel:personnel(id, legacy_id, name, phone)
                    )
                )
                """
            ).or_(f"legacy_id.eq.{site_id},id.eq.{site_id}").limit(1).execute()
            
            rows = r.data or []
            if not rows:
                return None
            
            site_row = rows[0]
            return _transform_site(
                site_row,
                assignments=site_row.get("assignments", []),
                cert_assignments=site_row.get("cert_assignments", []),
                company=site_row.get("company")
            )
        except Exception as e:
            # 폴백: 단순 조회
            try:
                r = client.table(TABLE_SITES).select("*").or_(f"legacy_id.eq.{site_id},id.eq.{site_id}").limit(1).execute()
                rows = r.data or []
                return _transform_site(rows[0]) if rows else None
            except Exception:
                raise e

    def get_all_personnel(self) -> List[Dict]:
        """모든 인력 조회"""
        client = self._get_client()
        try:
            r = client.table(TABLE_PERSONNEL).select(
                """
                *,
                company:companies(id, name, short_name)
                """
            ).order("created_at", desc=True).execute()
            
            personnel_list = []
            for p_row in (r.data or []):
                p = _transform_personnel(p_row, company=p_row.get("company"))
                personnel_list.append(p)
            return personnel_list
        except Exception as e:
            # 폴백
            try:
                r = client.table(TABLE_PERSONNEL).select("*").order("created_at", desc=True).execute()
                return [_transform_personnel(row) for row in (r.data or [])]
            except Exception:
                raise e

    def get_personnel_by_id(self, personnel_id: str) -> Optional[Dict]:
        """인력 상세 조회 (legacy_id 또는 id로 조회)"""
        client = self._get_client()
        try:
            r = client.table(TABLE_PERSONNEL).select(
                """
                *,
                company:companies(id, name, short_name)
                """
            ).or_(f"legacy_id.eq.{personnel_id},id.eq.{personnel_id}").limit(1).execute()
            
            rows = r.data or []
            if not rows:
                return None
            
            p_row = rows[0]
            return _transform_personnel(p_row, company=p_row.get("company"))
        except Exception as e:
            # 폴백
            try:
                r = client.table(TABLE_PERSONNEL).select("*").or_(f"legacy_id.eq.{personnel_id},id.eq.{personnel_id}").limit(1).execute()
                rows = r.data or []
                return _transform_personnel(rows[0]) if rows else None
            except Exception:
                raise e

    def get_all_certificates(self) -> List[Dict]:
        """모든 자격증 조회"""
        client = self._get_client()
        try:
            r = client.table(TABLE_CERTIFICATES).select(
                """
                *,
                cert_type:certificate_types(id, name),
                personnel:personnel(id, legacy_id, name, phone)
                """
            ).order("created_at", desc=True).execute()
            
            cert_list = []
            for c_row in (r.data or []):
                c = _transform_certificate(
                    c_row,
                    cert_type=c_row.get("cert_type"),
                    personnel=c_row.get("personnel")
                )
                cert_list.append(c)
            return cert_list
        except Exception as e:
            # 폴백
            try:
                r = client.table(TABLE_CERTIFICATES).select("*").order("created_at", desc=True).execute()
                return [_transform_certificate(row) for row in (r.data or [])]
            except Exception:
                raise e

    def get_certificate_by_id(self, cert_id: str) -> Optional[Dict]:
        """자격증 상세 조회 (legacy_id 또는 id로 조회)"""
        client = self._get_client()
        try:
            r = client.table(TABLE_CERTIFICATES).select(
                """
                *,
                cert_type:certificate_types(id, name),
                personnel:personnel(id, legacy_id, name, phone)
                """
            ).or_(f"legacy_id.eq.{cert_id},id.eq.{cert_id}").limit(1).execute()
            
            rows = r.data or []
            if not rows:
                return None
            
            c_row = rows[0]
            return _transform_certificate(
                c_row,
                cert_type=c_row.get("cert_type"),
                personnel=c_row.get("personnel")
            )
        except Exception as e:
            # 폴백
            try:
                r = client.table(TABLE_CERTIFICATES).select("*").or_(f"legacy_id.eq.{cert_id},id.eq.{cert_id}").limit(1).execute()
                rows = r.data or []
                return _transform_certificate(rows[0]) if rows else None
            except Exception:
                raise e

    # ---- 쓰기: 정규화된 스키마 사용 ----
    def create_site(self, data: Dict[str, Any]) -> None:
        """현장 생성 (정규화된 스키마)"""
        client = self._get_client()
        
        # 회사 ID 조회
        company_id = None
        if data.get("회사구분"):
            company_name = data["회사구분"]
            try:
                company_r = client.table(TABLE_COMPANIES).select("id").or_(f"name.eq.{company_name},short_name.eq.{company_name}").limit(1).execute()
                if company_r.data:
                    company_id = company_r.data[0]["id"]
            except Exception:
                pass
        
        # 정규화된 스키마 형식으로 변환
        payload = {
            "legacy_id": data.get("현장ID"),
            "company_id": company_id,
            "name": data.get("현장명", ""),
            "owner_name": data.get("건축주명", ""),
            "address": data.get("주소", ""),
            "latitude": float(data["위도"]) if data.get("위도") and str(data["위도"]).strip() else None,
            "longitude": float(data["경도"]) if data.get("경도") and str(data["경도"]).strip() else None,
            "permit_date": data.get("건축허가일") or None,
            "start_date": data.get("착공예정일") or None,
            "end_date": data.get("준공일") or None,
            "status": data.get("현장상태", "건축허가"),
            "assignment_status": data.get("배정상태", "미배정"),
            "notes": data.get("특이사항", ""),
            "completion_doc_url": data.get("준공필증파일URL", ""),
        }
        client.table(TABLE_SITES).insert(payload).execute()

    def update_site(self, site_id: str, data: Dict[str, Any]) -> None:
        """현장 수정 (정규화된 스키마)"""
        if not data:
            return
        
        client = self._get_client()
        payload = {}
        
        # 회사 ID 조회 (회사구분 변경 시)
        if "회사구분" in data:
            company_name = data["회사구분"]
            try:
                company_r = client.table(TABLE_COMPANIES).select("id").or_(f"name.eq.{company_name},short_name.eq.{company_name}").limit(1).execute()
                if company_r.data:
                    payload["company_id"] = company_r.data[0]["id"]
            except Exception:
                pass
        
        # 필드 매핑
        field_map = {
            "현장명": "name",
            "건축주명": "owner_name",
            "주소": "address",
            "위도": "latitude",
            "경도": "longitude",
            "건축허가일": "permit_date",
            "착공예정일": "start_date",
            "준공일": "end_date",
            "현장상태": "status",
            "배정상태": "assignment_status",
            "특이사항": "notes",
            "준공필증파일URL": "completion_doc_url",
        }
        
        for korean_key, db_key in field_map.items():
            if korean_key in data:
                value = data[korean_key]
                if db_key in ("latitude", "longitude"):
                    payload[db_key] = float(value) if value and str(value).strip() else None
                else:
                    payload[db_key] = value if value else None
        
        payload["updated_at"] = datetime.now().isoformat()
        
        client.table(TABLE_SITES).update(payload).or_(f"legacy_id.eq.{site_id},id.eq.{site_id}").execute()

    def create_personnel(self, data: Dict[str, Any]) -> None:
        """인력 생성 (정규화된 스키마)"""
        client = self._get_client()
        
        # 회사 ID 조회
        company_id = None
        if data.get("소속"):
            company_name = data["소속"]
            try:
                company_r = client.table(TABLE_COMPANIES).select("id").or_(f"name.eq.{company_name},short_name.eq.{company_name}").limit(1).execute()
                if company_r.data:
                    company_id = company_r.data[0]["id"]
            except Exception:
                pass
        
        payload = {
            "legacy_id": data.get("인력ID"),
            "company_id": company_id,
            "name": data.get("성명", ""),
            "position": data.get("직책", "소장"),
            "phone": data.get("연락처", ""),
            "email": data.get("이메일", ""),
            "status": data.get("현재상태", "투입가능"),
            "current_site_count": int(data.get("현재담당현장수", 0) or 0),
            "join_date": data.get("입사일") or None,
            "notes": data.get("비고", ""),
        }
        client.table(TABLE_PERSONNEL).insert(payload).execute()

    def update_personnel(self, personnel_id: str, data: Dict[str, Any]) -> None:
        """인력 수정 (정규화된 스키마)"""
        if not data:
            return
        
        client = self._get_client()
        payload = {}
        
        # 회사 ID 조회
        if "소속" in data:
            company_name = data["소속"]
            try:
                company_r = client.table(TABLE_COMPANIES).select("id").or_(f"name.eq.{company_name},short_name.eq.{company_name}").limit(1).execute()
                if company_r.data:
                    payload["company_id"] = company_r.data[0]["id"]
            except Exception:
                pass
        
        field_map = {
            "성명": "name",
            "직책": "position",
            "연락처": "phone",
            "이메일": "email",
            "현재상태": "status",
            "현재담당현장수": "current_site_count",
            "입사일": "join_date",
            "비고": "notes",
        }
        
        for korean_key, db_key in field_map.items():
            if korean_key in data:
                value = data[korean_key]
                if db_key == "current_site_count":
                    payload[db_key] = int(value or 0)
                else:
                    payload[db_key] = value if value else None
        
        payload["updated_at"] = datetime.now().isoformat()
        client.table(TABLE_PERSONNEL).update(payload).or_(f"legacy_id.eq.{personnel_id},id.eq.{personnel_id}").execute()

    def create_certificate(self, data: Dict[str, Any]) -> None:
        """자격증 생성 (정규화된 스키마)"""
        client = self._get_client()
        
        # 자격증 종류 ID 조회
        cert_type_id = None
        if data.get("자격증명"):
            cert_type_name = data["자격증명"]
            try:
                cert_type_r = client.table(TABLE_CERTIFICATE_TYPES).select("id").eq("name", cert_type_name).limit(1).execute()
                if cert_type_r.data:
                    cert_type_id = cert_type_r.data[0]["id"]
            except Exception:
                pass
        
        # 소유자 ID 조회
        personnel_id = None
        if data.get("소유자명"):
            owner_name = data["소유자명"]
            try:
                personnel_r = client.table(TABLE_PERSONNEL).select("id").eq("name", owner_name).limit(1).execute()
                if personnel_r.data:
                    personnel_id = personnel_r.data[0]["id"]
            except Exception:
                pass
        
        payload = {
            "legacy_id": data.get("자격증ID"),
            "cert_type_id": cert_type_id,
            "personnel_id": personnel_id,
            "cert_number": data.get("자격증번호", ""),
            "issued_date": data.get("취득일") or None,
            "expiry_date": data.get("유효기간") or None,
            "status": data.get("사용가능여부", "사용가능"),
            "notes": data.get("비고", ""),
        }
        client.table(TABLE_CERTIFICATES).insert(payload).execute()

    def update_certificate(self, cert_id: str, data: Dict[str, Any]) -> None:
        """자격증 수정 (정규화된 스키마)"""
        if not data:
            return
        
        client = self._get_client()
        payload = {}
        
        # 자격증 종류 ID 조회
        if "자격증명" in data:
            cert_type_name = data["자격증명"]
            try:
                cert_type_r = client.table(TABLE_CERTIFICATE_TYPES).select("id").eq("name", cert_type_name).limit(1).execute()
                if cert_type_r.data:
                    payload["cert_type_id"] = cert_type_r.data[0]["id"]
            except Exception:
                pass
        
        # 소유자 ID 조회
        if "소유자명" in data:
            owner_name = data["소유자명"]
            try:
                personnel_r = client.table(TABLE_PERSONNEL).select("id").eq("name", owner_name).limit(1).execute()
                if personnel_r.data:
                    payload["personnel_id"] = personnel_r.data[0]["id"]
            except Exception:
                pass
        
        field_map = {
            "자격증번호": "cert_number",
            "취득일": "issued_date",
            "유효기간": "expiry_date",
            "사용가능여부": "status",
            "비고": "notes",
        }
        
        for korean_key, db_key in field_map.items():
            if korean_key in data:
                payload[db_key] = data[korean_key] if data[korean_key] else None
        
        payload["updated_at"] = datetime.now().isoformat()
        client.table(TABLE_CERTIFICATES).update(payload).or_(f"legacy_id.eq.{cert_id},id.eq.{cert_id}").execute()

    def assign_site(self, site_id: str, manager_id: str, certificate_id: str) -> None:
        """소장·자격증 배정 (정규화된 스키마: 배정 관계 테이블 사용)"""
        client = self._get_client()
        now = datetime.now().isoformat()

        # UUID 조회 (legacy_id 또는 id로)
        site_r = client.table(TABLE_SITES).select("id").or_(f"legacy_id.eq.{site_id},id.eq.{site_id}").limit(1).execute()
        if not site_r.data:
            raise ValueError(f"현장을 찾을 수 없습니다: {site_id}")
        site_uuid = site_r.data[0]["id"]

        manager_r = client.table(TABLE_PERSONNEL).select("id").or_(f"legacy_id.eq.{manager_id},id.eq.{manager_id}").limit(1).execute()
        if not manager_r.data:
            raise ValueError(f"인력을 찾을 수 없습니다: {manager_id}")
        manager_uuid = manager_r.data[0]["id"]

        cert_r = client.table(TABLE_CERTIFICATES).select("id").or_(f"legacy_id.eq.{certificate_id},id.eq.{certificate_id}").limit(1).execute()
        if not cert_r.data:
            raise ValueError(f"자격증을 찾을 수 없습니다: {certificate_id}")
        cert_uuid = cert_r.data[0]["id"]

        # 기존 배정 해제 (있는 경우)
        client.table(TABLE_SITE_ASSIGNMENTS).update({"status": "해제", "released_at": now}).eq("site_id", site_uuid).eq("status", "배정중").execute()
        client.table(TABLE_CERTIFICATE_ASSIGNMENTS).update({"status": "해제", "released_at": now}).eq("site_id", site_uuid).eq("status", "배정중").execute()

        # 새 배정 생성
        client.table(TABLE_SITE_ASSIGNMENTS).insert({
            "site_id": site_uuid,
            "personnel_id": manager_uuid,
            "role": "담당",
            "status": "배정중",
        }).execute()

        client.table(TABLE_CERTIFICATE_ASSIGNMENTS).insert({
            "certificate_id": cert_uuid,
            "site_id": site_uuid,
            "status": "배정중",
        }).execute()

        # 현장 배정상태 업데이트
        client.table(TABLE_SITES).update({
            "assignment_status": "배정완료",
            "updated_at": now,
        }).eq("id", site_uuid).execute()

        # 인력 상태 업데이트
        manager_data = client.table(TABLE_PERSONNEL).select("current_site_count").eq("id", manager_uuid).single().execute()
        cur_count = (manager_data.data.get("current_site_count") or 0) + 1
        client.table(TABLE_PERSONNEL).update({
            "status": "투입중",
            "current_site_count": cur_count,
            "updated_at": now,
        }).eq("id", manager_uuid).execute()

        # 자격증 상태 업데이트
        client.table(TABLE_CERTIFICATES).update({
            "status": "사용중",
            "updated_at": now,
        }).eq("id", cert_uuid).execute()

    def unassign_site(self, site_id: str) -> None:
        """소장 배정 해제 (정규화된 스키마)"""
        client = self._get_client()
        now = datetime.now().isoformat()

        # 현장 UUID 조회
        site_r = client.table(TABLE_SITES).select("id").or_(f"legacy_id.eq.{site_id},id.eq.{site_id}").limit(1).execute()
        if not site_r.data:
            raise ValueError(f"현장을 찾을 수 없습니다: {site_id}")
        site_uuid = site_r.data[0]["id"]

        # 배정 정보 조회
        assignment_r = client.table(TABLE_SITE_ASSIGNMENTS).select("personnel_id").eq("site_id", site_uuid).eq("status", "배정중").limit(1).execute()
        manager_uuid = assignment_r.data[0]["personnel_id"] if assignment_r.data else None

        cert_assignment_r = client.table(TABLE_CERTIFICATE_ASSIGNMENTS).select("certificate_id").eq("site_id", site_uuid).eq("status", "배정중").limit(1).execute()
        cert_uuid = cert_assignment_r.data[0]["certificate_id"] if cert_assignment_r.data else None

        # 배정 해제
        client.table(TABLE_SITE_ASSIGNMENTS).update({
            "status": "해제",
            "released_at": now,
        }).eq("site_id", site_uuid).eq("status", "배정중").execute()

        client.table(TABLE_CERTIFICATE_ASSIGNMENTS).update({
            "status": "해제",
            "released_at": now,
        }).eq("site_id", site_uuid).eq("status", "배정중").execute()

        # 현장 상태 업데이트
        client.table(TABLE_SITES).update({
            "assignment_status": "미배정",
            "updated_at": now,
        }).eq("id", site_uuid).execute()

        # 인력 상태 업데이트
        if manager_uuid:
            manager_data = client.table(TABLE_PERSONNEL).select("current_site_count").eq("id", manager_uuid).single().execute()
            cur_count = max(0, (manager_data.data.get("current_site_count") or 0) - 1)
            upd = {"current_site_count": cur_count, "updated_at": now}
            if cur_count <= 0:
                upd["status"] = "투입가능"
            client.table(TABLE_PERSONNEL).update(upd).eq("id", manager_uuid).execute()

        # 자격증 상태 업데이트
        if cert_uuid:
            client.table(TABLE_CERTIFICATES).update({
                "status": "사용가능",
                "updated_at": now,
            }).eq("id", cert_uuid).execute()


supabase_service = SupabaseService()
