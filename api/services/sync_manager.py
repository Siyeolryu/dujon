"""
2-3 실시간 동기화 - 낙관적 잠금 (Optimistic Locking)

- 현장(시트1) 수정일(수정일)을 버전으로 사용
- 수정/배정/배정해제 시 클라이언트가 보낸 버전과 일치할 때만 적용
- 불일치 시 409 Conflict 반환 (다른 사용자가 먼저 수정함)
"""


class ConflictError(Exception):
    """버전 충돌 - 다른 사용자가 데이터를 수정한 상태"""
    pass


class SyncManager:
    """낙관적 잠금: 버전 확인 후 수정 허용"""

    def __init__(self, sheets_service):
        self._sheets = sheets_service

    def get_site_version(self, site_id):
        """
        현장의 현재 버전(수정일) 반환.
        GET 응답에 포함하여 클라이언트가 수정 시 If-Match로 보내도록 함.
        """
        site = self._sheets.get_site_by_id(site_id)
        if not site:
            return None
        return (site.get('수정일') or '').strip()

    def check_site_version(self, site_id, expected_version):
        """
        expected_version이 None/빈 문자열이면 검사 생략(옵션).
        일치하면 True, 불일치하면 False.
        """
        if expected_version is None or str(expected_version).strip() == '':
            return True
        current = self.get_site_version(site_id)
        return current == str(expected_version).strip()

    def require_site_version(self, site_id, expected_version):
        """
        버전이 일치하지 않으면 ConflictError 발생.
        수정/배정/배정해제 전에 호출.
        """
        if not self.check_site_version(site_id, expected_version):
            current = self.get_site_version(site_id)
            raise ConflictError(
                f'데이터가 다른 사용자에 의해 수정되었습니다. '
                f'현재 버전: {current}, 요청 버전: {expected_version}. 최신 데이터를 다시 조회한 뒤 시도하세요.'
            )


def get_sync_manager():
    """DB 서비스(Supabase/Sheets) 인스턴스로 SyncManager 생성 (api 라우트에서 사용)"""
    from api.services.db_service import get_db
    return SyncManager(get_db())
