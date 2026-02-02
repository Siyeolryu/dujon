"""
Google Sheets 연동 서비스
- 시트1: 현장정보, 시트2: 인력풀, 시트3: 자격증풀
"""
import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# 프로젝트 루트에서 실행 가정 (python api/app.py)
DEFAULT_SPREADSHEET_ID = '15fAEzkC9FCLA6sG1N--f69r-32WHoYLvmXcwED5xWzM'
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', DEFAULT_SPREADSHEET_ID)


class SheetsService:
    """Google Sheets API 래퍼"""

    def __init__(self):
        self._service = None

    def _get_service(self):
        """Google Sheets API 서비스 생성 (인증 포함)"""
        if self._service is not None:
            return self._service

        creds = None
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        token_path = os.path.join(root, 'token.pickle')

        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                client_secret = None
                for f in os.listdir(root):
                    if f.startswith('client_secret') and f.endswith('.json'):
                        client_secret = os.path.join(root, f)
                        break
                if not client_secret:
                    raise FileNotFoundError(
                        "client_secret 파일을 찾을 수 없습니다. "
                        "프로젝트 루트에 client_secret_xxx.json을 넣어주세요."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        self._service = build('sheets', 'v4', credentials=creds)
        return self._service

    def read_sheet(self, range_name):
        """시트 범위 읽기. range_name 예: '시트1!A2:V'"""
        service = self._get_service()
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name
        ).execute()
        return result.get('values', [])

    def _pad_row(self, row, length, fill=''):
        """row 길이를 length까지 채움"""
        while len(row) < length:
            row.append(fill)
        return row

    def get_all_sites(self):
        """현장 정보 전체 조회 (시트1). 17컬럼(기본) / 22컬럼(VLOOKUP 적용) 모두 지원"""
        values = self.read_sheet('시트1!A2:V')
        if not values:
            return []

        sites = []
        for row in values:
            row = list(row)
            n = len(row)
            if n < 17:
                self._pad_row(row, 17)
            if n == 17:
                # 기본 17컬럼: VLOOKUP 컬럼 없음
                site = {
                    '현장ID': row[0],
                    '현장명': row[1],
                    '회사구분': row[2],
                    '주소': row[3],
                    '위도': row[4],
                    '경도': row[5],
                    '건축허가일': row[6],
                    '착공예정일': row[7],
                    '준공일': row[8],
                    '현장상태': row[9],
                    '특이사항': row[10],
                    '담당소장ID': row[11],
                    '담당소장명': '',
                    '담당소장연락처': '',
                    '사용자격증ID': row[12],
                    '자격증명': '',
                    '자격증소유자명': '',
                    '자격증소유자연락처': '',
                    '준공필증파일URL': row[13],
                    '배정상태': row[14],
                    '등록일': row[15],
                    '수정일': row[16],
                }
            else:
                self._pad_row(row, 22)
                site = {
                    '현장ID': row[0],
                    '현장명': row[1],
                    '회사구분': row[2],
                    '주소': row[3],
                    '위도': row[4],
                    '경도': row[5],
                    '건축허가일': row[6],
                    '착공예정일': row[7],
                    '준공일': row[8],
                    '현장상태': row[9],
                    '특이사항': row[10],
                    '담당소장ID': row[11],
                    '담당소장명': row[12],
                    '담당소장연락처': row[13],
                    '사용자격증ID': row[14],
                    '자격증명': row[15],
                    '자격증소유자명': row[16],
                    '자격증소유자연락처': row[17],
                    '준공필증파일URL': row[18],
                    '배정상태': row[19],
                    '등록일': row[20],
                    '수정일': row[21],
                }
            sites.append(site)
        return sites

    def get_site_by_id(self, site_id):
        """현장ID로 현장 정보 조회"""
        for site in self.get_all_sites():
            if site['현장ID'] == site_id:
                return site
        return None

    def get_all_personnel(self):
        """인력 정보 전체 조회 (시트2)"""
        values = self.read_sheet('시트2!A2:L')
        if not values:
            return []

        personnel_list = []
        for row in values:
            self._pad_row(row, 12)
            personnel_list.append({
                '인력ID': row[0],
                '성명': row[1],
                '직책': row[2],
                '소속': row[3],
                '연락처': row[4],
                '이메일': row[5],
                '보유자격증': row[6],
                '현재상태': row[7],
                '현재담당현장수': row[8],
                '비고': row[9],
                '입사일': row[10],
                '등록일': row[11],
            })
        return personnel_list

    def get_personnel_by_id(self, personnel_id):
        """인력ID로 인력 정보 조회"""
        for person in self.get_all_personnel():
            if person['인력ID'] == personnel_id:
                return person
        return None

    def get_all_certificates(self):
        """자격증 정보 전체 조회 (시트3)"""
        values = self.read_sheet('시트3!A2:M')
        if not values:
            return []

        certificates = []
        for row in values:
            self._pad_row(row, 13)
            certificates.append({
                '자격증ID': row[0],
                '자격증명': row[1],
                '자격증번호': row[2],
                '소유자ID': row[3],
                '소유자명': row[4],
                '소유자연락처': row[5],
                '발급기관': row[6],
                '취득일': row[7],
                '유효기간': row[8],
                '사용가능여부': row[9],
                '현재사용현장ID': row[10],
                '비고': row[11],
                '등록일': row[12],
            })
        return certificates

    def get_certificate_by_id(self, cert_id):
        """자격증ID로 자격증 정보 조회"""
        for cert in self.get_all_certificates():
            if cert['자격증ID'] == cert_id:
                return cert
        return None

    # ---------- 2-2 데이터 수정 API용 ----------

    def update_cell(self, range_name, value):
        """셀 1개 업데이트"""
        service = self._get_service()
        body = {'values': [[value]]}
        return service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body,
        ).execute()

    def update_row(self, range_name, values):
        """행(여러 셀) 업데이트"""
        service = self._get_service()
        body = {'values': [values]}
        return service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body,
        ).execute()

    def batch_update(self, updates):
        """여러 범위 일괄 업데이트. updates = [{'range': '시트1!A1', 'values': [[v]]}, ...]"""
        if not updates:
            return
        service = self._get_service()
        data = [{'range': u['range'], 'values': u['values']} for u in updates]
        body = {'valueInputOption': 'USER_ENTERED', 'data': data}
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=body,
        ).execute()

    def find_row_by_id(self, sheet_name, id_value):
        """ID 컬럼(A열)으로 행 번호 반환. 1-based, 헤더 다음이 2행."""
        values = self.read_sheet(f'{sheet_name}!A2:A')
        for idx, row in enumerate(values):
            if row and str(row[0]).strip() == str(id_value).strip():
                return idx + 2
        return None

    def append_row(self, sheet_name, values):
        """시트 마지막에 행 추가"""
        service = self._get_service()
        body = {'values': [values]}
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{sheet_name}!A:A',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body,
        ).execute()


# 싱글톤 인스턴스 (지연 초기화는 첫 요청 시 _get_service에서)
sheets_service = SheetsService()
