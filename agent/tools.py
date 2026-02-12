"""
15개 도구 정의 + 핸들러.
Anthropic tool-use 스펙에 맞는 JSON Schema 정의와
비동기 핸들러 함수를 함께 제공합니다.
"""
import json
from agent.api_helpers import api


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Tool JSON Schema 정의
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TOOLS = [
    # 1. 현장 목록 조회
    {
        "name": "get_sites",
        "description": "현장 목록을 조회합니다. 회사구분·배정상태·현장상태로 필터링할 수 있습니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "company": {
                    "type": "string",
                    "description": "회사구분 필터 (더존종합건설 / 더존하우징)",
                    "enum": ["더존종합건설", "더존하우징"]
                },
                "status": {
                    "type": "string",
                    "description": "배정상태 필터 (배정완료 / 미배정)",
                    "enum": ["배정완료", "미배정"]
                },
                "state": {
                    "type": "string",
                    "description": "현장상태 필터",
                    "enum": ["건축허가", "착공예정", "공사 중", "공사 중단", "준공"]
                },
                "limit": {
                    "type": "integer",
                    "description": "조회 개수 제한 (기본값: 전체)"
                },
                "offset": {
                    "type": "integer",
                    "description": "페이지 오프셋 (0부터 시작)"
                }
            },
            "required": []
        }
    },
    # 2. 현장 검색
    {
        "name": "search_sites",
        "description": "현장명 또는 주소 키워드로 현장을 검색합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "검색 키워드 (현장명 또는 주소)"
                }
            },
            "required": ["q"]
        }
    },
    # 3. 현장 상세 조회
    {
        "name": "get_site_detail",
        "description": "특정 현장의 상세 정보를 조회합니다. 담당소장·자격증 배정 정보 포함.",
        "input_schema": {
            "type": "object",
            "properties": {
                "site_id": {
                    "type": "string",
                    "description": "현장ID"
                }
            },
            "required": ["site_id"]
        }
    },
    # 4. 현장 등록
    {
        "name": "create_site",
        "description": "새 현장을 등록합니다. 현장명·회사구분·주소는 필수입니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "현장명": {"type": "string", "description": "현장 이름 (필수)"},
                "회사구분": {
                    "type": "string",
                    "description": "회사구분 (필수)",
                    "enum": ["더존종합건설", "더존하우징"]
                },
                "주소": {"type": "string", "description": "현장 주소 (필수)"},
                "건축주명": {"type": "string", "description": "건축주 이름"},
                "건축허가일": {"type": "string", "description": "건축허가일 (YYYY-MM-DD)"},
                "착공예정일": {"type": "string", "description": "착공예정일 (YYYY-MM-DD)"},
                "준공일": {"type": "string", "description": "준공일 (YYYY-MM-DD)"},
                "현장상태": {
                    "type": "string",
                    "enum": ["건축허가", "착공예정", "공사 중", "공사 중단", "준공"]
                },
                "특이사항": {"type": "string", "description": "특이사항 메모"}
            },
            "required": ["현장명", "회사구분", "주소"]
        }
    },
    # 5. 현장 수정
    {
        "name": "update_site",
        "description": "현장 정보를 수정합니다. 변경할 필드만 전달합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "site_id": {"type": "string", "description": "현장ID (필수)"},
                "현장명": {"type": "string"},
                "회사구분": {"type": "string", "enum": ["더존종합건설", "더존하우징"]},
                "주소": {"type": "string"},
                "건축주명": {"type": "string"},
                "건축허가일": {"type": "string"},
                "착공예정일": {"type": "string"},
                "준공일": {"type": "string"},
                "현장상태": {
                    "type": "string",
                    "enum": ["건축허가", "착공예정", "공사 중", "공사 중단", "준공"]
                },
                "특이사항": {"type": "string"}
            },
            "required": ["site_id"]
        }
    },
    # 6. 소장+자격증 배정
    {
        "name": "assign_manager",
        "description": "현장에 소장과 자격증을 배정합니다. 소장ID와 자격증ID가 모두 필요합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "site_id": {"type": "string", "description": "현장ID"},
                "manager_id": {"type": "string", "description": "소장(인력) ID"},
                "certificate_id": {"type": "string", "description": "자격증ID"}
            },
            "required": ["site_id", "manager_id", "certificate_id"]
        }
    },
    # 7. 배정 해제
    {
        "name": "unassign_manager",
        "description": "현장의 소장·자격증 배정을 해제합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "site_id": {"type": "string", "description": "현장ID"}
            },
            "required": ["site_id"]
        }
    },
    # 8. 인력 목록 조회
    {
        "name": "get_personnel",
        "description": "인력 목록을 조회합니다. 상태·직책으로 필터링할 수 있습니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "인력 상태 필터",
                    "enum": ["투입가능", "투입중", "휴가", "퇴사"]
                },
                "role": {
                    "type": "string",
                    "description": "직책 필터 (예: 소장, 대리)"
                }
            },
            "required": []
        }
    },
    # 9. 인력 상세 조회
    {
        "name": "get_personnel_detail",
        "description": "특정 인력의 상세 정보를 조회합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "personnel_id": {"type": "string", "description": "인력ID"}
            },
            "required": ["personnel_id"]
        }
    },
    # 10. 인력 정보 수정
    {
        "name": "update_personnel",
        "description": "인력 정보를 수정합니다. 변경할 필드만 전달합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "personnel_id": {"type": "string", "description": "인력ID (필수)"},
                "성명": {"type": "string"},
                "직책": {"type": "string"},
                "소속": {"type": "string"},
                "연락처": {"type": "string"},
                "이메일": {"type": "string"},
                "현재상태": {
                    "type": "string",
                    "enum": ["투입가능", "투입중", "휴가", "퇴사"]
                },
                "비고": {"type": "string"}
            },
            "required": ["personnel_id"]
        }
    },
    # 11. 자격증 목록 조회
    {
        "name": "get_certificates",
        "description": "자격증 목록을 조회합니다. 사용가능 여부로 필터링할 수 있습니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "available": {
                    "type": "string",
                    "description": "사용가능 필터 (true=사용가능만 / false=사용중만)",
                    "enum": ["true", "false"]
                }
            },
            "required": []
        }
    },
    # 12. 자격증 상세 조회
    {
        "name": "get_certificate_detail",
        "description": "특정 자격증의 상세 정보를 조회합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cert_id": {"type": "string", "description": "자격증ID"}
            },
            "required": ["cert_id"]
        }
    },
    # 13. 자격증 등록
    {
        "name": "create_certificate",
        "description": "새 자격증을 등록합니다. 자격증명·소유자명은 필수입니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "자격증명": {"type": "string", "description": "자격증 이름 (필수, 예: 건축기사)"},
                "소유자명": {"type": "string", "description": "소유자 이름 (필수)"},
                "자격증번호": {"type": "string"},
                "소유자연락처": {"type": "string"},
                "발급기관": {"type": "string"},
                "취득일": {"type": "string", "description": "YYYY-MM-DD"},
                "유효기간": {"type": "string", "description": "YYYY-MM-DD"},
                "비고": {"type": "string"}
            },
            "required": ["자격증명", "소유자명"]
        }
    },
    # 14. 자격증 수정
    {
        "name": "update_certificate",
        "description": "자격증 정보를 수정합니다. 변경할 필드만 전달합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cert_id": {"type": "string", "description": "자격증ID (필수)"},
                "자격증명": {"type": "string"},
                "자격증번호": {"type": "string"},
                "소유자명": {"type": "string"},
                "소유자연락처": {"type": "string"},
                "발급기관": {"type": "string"},
                "취득일": {"type": "string"},
                "유효기간": {"type": "string"},
                "사용가능여부": {"type": "string", "enum": ["사용가능", "사용중"]},
                "비고": {"type": "string"}
            },
            "required": ["cert_id"]
        }
    },
    # 15. 전체 통계
    {
        "name": "get_statistics",
        "description": "현장·인력·자격증 전체 통계를 조회합니다.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 도구 핸들러 (비동기)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _fmt(label: str, data) -> str:
    """결과를 한국어로 포맷팅."""
    if isinstance(data, list):
        if not data:
            return f"{label}: 결과가 없습니다."
        lines = [f"{label} ({len(data)}건)"]
        for i, item in enumerate(data, 1):
            lines.append(f"\n[{i}] " + json.dumps(item, ensure_ascii=False, indent=2))
        return "\n".join(lines)
    if isinstance(data, dict):
        return f"{label}:\n" + json.dumps(data, ensure_ascii=False, indent=2)
    return f"{label}: {data}"


def _err(msg: str) -> str:
    return f"❌ 오류: {msg}"


async def handle_tool(name: str, input_data: dict) -> str:
    """도구 이름과 입력 데이터로 핸들러를 호출하고 결과 문자열을 반환."""

    # ── 현장 ──
    if name == "get_sites":
        data, err = await api.get_sites(
            company=input_data.get("company"),
            status=input_data.get("status"),
            state=input_data.get("state"),
            limit=input_data.get("limit"),
            offset=input_data.get("offset"),
        )
        if err:
            return _err(err)
        return _fmt("현장 목록", data)

    if name == "search_sites":
        data, err = await api.search_sites(input_data["q"])
        if err:
            return _err(err)
        return _fmt(f"'{input_data['q']}' 검색 결과", data)

    if name == "get_site_detail":
        data, err = await api.get_site(input_data["site_id"])
        if err:
            return _err(err)
        return _fmt("현장 상세", data)

    if name == "create_site":
        payload = {k: v for k, v in input_data.items()}
        data, err = await api.create_site(payload)
        if err:
            return _err(err)
        return _fmt("현장 등록 완료", data)

    if name == "update_site":
        site_id = input_data.pop("site_id")
        data, err = await api.update_site(site_id, input_data)
        if err:
            return _err(err)
        return _fmt("현장 수정 완료", data)

    # ── 배정 ──
    if name == "assign_manager":
        data, err = await api.assign_site(
            input_data["site_id"],
            input_data["manager_id"],
            input_data["certificate_id"],
        )
        if err:
            return _err(err)
        return _fmt("배정 완료", data)

    if name == "unassign_manager":
        data, err = await api.unassign_site(input_data["site_id"])
        if err:
            return _err(err)
        return _fmt("배정 해제 완료", data)

    # ── 인력 ──
    if name == "get_personnel":
        data, err = await api.get_personnel(
            status=input_data.get("status"),
            role=input_data.get("role"),
        )
        if err:
            return _err(err)
        return _fmt("인력 목록", data)

    if name == "get_personnel_detail":
        data, err = await api.get_personnel_detail(input_data["personnel_id"])
        if err:
            return _err(err)
        return _fmt("인력 상세", data)

    if name == "update_personnel":
        pid = input_data.pop("personnel_id")
        data, err = await api.update_personnel(pid, input_data)
        if err:
            return _err(err)
        return _fmt("인력 수정 완료", data)

    # ── 자격증 ──
    if name == "get_certificates":
        data, err = await api.get_certificates(
            available=input_data.get("available"),
        )
        if err:
            return _err(err)
        return _fmt("자격증 목록", data)

    if name == "get_certificate_detail":
        data, err = await api.get_certificate_detail(input_data["cert_id"])
        if err:
            return _err(err)
        return _fmt("자격증 상세", data)

    if name == "create_certificate":
        payload = {k: v for k, v in input_data.items()}
        data, err = await api.create_certificate(payload)
        if err:
            return _err(err)
        return _fmt("자격증 등록 완료", data)

    if name == "update_certificate":
        cid = input_data.pop("cert_id")
        data, err = await api.update_certificate(cid, input_data)
        if err:
            return _err(err)
        return _fmt("자격증 수정 완료", data)

    # ── 통계 ──
    if name == "get_statistics":
        data, err = await api.get_stats()
        if err:
            return _err(err)
        return _fmt("전체 통계", data)

    return _err(f"알 수 없는 도구: {name}")
