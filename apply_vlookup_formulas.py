"""
현장배정 관리 시스템 - VLOOKUP 수식 자동화

시트1(현장정보)에 담당소장/자격증 조회용 컬럼 5개를 추가하고
VLOOKUP 수식을 적용합니다.
- 담당소장명, 담당소장연락처 (담당소장ID → 시트2)
- 자격증명, 자격증소유자명, 자격증소유자연락처 (사용자격증ID → 시트3)
"""

import sys
import os

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Google API는 get_google_sheets_service() 호출 시 지연 import (테스트 시 모듈 로드만으로 통과 가능)
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', '15fAEzkC9FCLA6sG1N--f69r-32WHoYLvmXcwED5xWzM')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# 시트1 기본 17컬럼: A~Q. L=11 담당소장ID, M=12 사용자격증ID
# 5개 컬럼 역순 삽입: 17,16,15,13,12 → 삽입 후 사용자격증ID는 O열(14)
COLUMNS_TO_ADD = [
    {'insert_at': 12, 'header': '담당소장명', 'formula_tpl': '=IF(ISBLANK(L{row}),"",IFERROR(VLOOKUP(L{row},시트2!A:B,2,FALSE),""))'},
    {'insert_at': 13, 'header': '담당소장연락처', 'formula_tpl': '=IF(ISBLANK(L{row}),"",IFERROR(VLOOKUP(L{row},시트2!A:E,5,FALSE),""))'},
    {'insert_at': 15, 'header': '자격증명', 'formula_tpl': '=IF(ISBLANK(O{row}),"",IFERROR(VLOOKUP(O{row},시트3!A:B,2,FALSE),""))'},
    {'insert_at': 16, 'header': '자격증소유자명', 'formula_tpl': '=IF(ISBLANK(O{row}),"",IFERROR(VLOOKUP(O{row},시트3!A:E,5,FALSE),""))'},
    {'insert_at': 17, 'header': '자격증소유자연락처', 'formula_tpl': '=IF(ISBLANK(O{row}),"",IFERROR(VLOOKUP(O{row},시트3!A:F,6,FALSE),""))'},
]


def get_google_sheets_service():
    """Google Sheets API 서비스 생성"""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        import pickle
    except ImportError:
        print("❌ 필요한 패키지가 설치되지 않았습니다.")
        print("pip install google-api-python-client google-auth-oauthlib google-auth-httplib2")
        sys.exit(1)

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_secret_file = None
            for f in os.listdir('.'):
                if f.startswith('client_secret') and f.endswith('.json'):
                    client_secret_file = f
                    break
            if not client_secret_file:
                print("❌ client_secret 파일을 찾을 수 없습니다.")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('sheets', 'v4', credentials=creds)


def get_sheet_id_by_name(service, sheet_name):
    """시트 이름으로 시트 ID 찾기"""
    spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    for sheet in spreadsheet['sheets']:
        if sheet['properties']['title'] == sheet_name:
            return sheet['properties']['sheetId']
    return None


def get_sheet1_row_count(service):
    """시트1 데이터 행 수 (헤더 제외)"""
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='시트1!A2:A',
    ).execute()
    values = result.get('values', [])
    return max(len(values), 1)


def insert_column(sheet_id, col_index):
    """컬럼 삽입"""
    return {
        'insertDimension': {
            'range': {
                'sheetId': sheet_id,
                'dimension': 'COLUMNS',
                'startIndex': col_index,
                'endIndex': col_index + 1,
            },
            'inheritFromBefore': False,
        }
    }


def add_header(sheet_id, col_index, header_text):
    """헤더 텍스트 추가"""
    return {
        'updateCells': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': 0,
                'endRowIndex': 1,
                'startColumnIndex': col_index,
                'endColumnIndex': col_index + 1,
            },
            'rows': [{
                'values': [{
                    'userEnteredValue': {'stringValue': header_text},
                    'userEnteredFormat': {
                        'textFormat': {'bold': True},
                        'horizontalAlignment': 'CENTER',
                    },
                }]
            }],
            'fields': 'userEnteredValue,userEnteredFormat',
        }
    }


def apply_formula_column(service, sheet_id, col_index, formula_tpl, num_rows):
    """한 컬럼에 행별 수식 적용 (2행 ~ num_rows+1행)"""
    rows = []
    for r in range(1, 1 + num_rows):
        row_num = r + 1  # 2-based
        formula = formula_tpl.format(row=row_num)
        rows.append({
            'values': [{
                'userEnteredValue': {'formulaValue': formula},
            }]
        })
    return {
        'updateCells': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': 1,
                'endRowIndex': 1 + num_rows,
                'startColumnIndex': col_index,
                'endColumnIndex': col_index + 1,
            },
            'rows': rows,
            'fields': 'userEnteredValue.formulaValue',
        }
    }


def main():
    print("=" * 60)
    print("📋 VLOOKUP 수식 자동화")
    print("=" * 60)
    print()

    print("🔑 Google Sheets API 인증 중...")
    try:
        service = get_google_sheets_service()
        print("✅ 인증 완료")
        print()
    except Exception as e:
        print(f"❌ 인증 실패: {e}")
        return

    sheet_id = get_sheet_id_by_name(service, '시트1')
    if sheet_id is None:
        print("❌ 시트1을 찾을 수 없습니다.")
        return

    # 현재 컬럼 수 확인 (선택)
    try:
        meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID, fields='sheets(properties(gridProperties(columnCount)))').execute()
        col_count = meta['sheets'][0]['properties']['gridProperties'].get('columnCount', 17)
    except Exception:
        col_count = 17
    print(f"🔍 시트1 (현장정보) 분석 중...")
    print(f"   현재 컬럼 수: {col_count}개")
    print()
    print("📝 5개 VLOOKUP 컬럼 추가 예정:")
    for i, col in enumerate(COLUMNS_TO_ADD, 1):
        print(f"   {i}. {col['header']}")
    print()

    num_rows = get_sheet1_row_count(service)
    print(f"   데이터 행 수: {num_rows}행")
    print()
    print("🚀 컬럼 추가 및 수식 적용 중...")

    # 역순으로 삽입 (인덱스 변경 방지)
    for col_info in reversed(COLUMNS_TO_ADD):
        insert_at = col_info['insert_at']
        header = col_info['header']
        formula_tpl = col_info['formula_tpl']

        requests = []
        requests.append(insert_column(sheet_id, insert_at))
        requests.append(add_header(sheet_id, insert_at, header))
        # 수식은 삽입 후 같은 인덱스에 적용
        requests.append(apply_formula_column(service, sheet_id, insert_at, formula_tpl, num_rows))

        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'requests': requests},
        ).execute()
        print(f"   ✅ {header}")

    print()
    print("=" * 60)
    print("✅ VLOOKUP 수식 자동화 완료!")
    print("=" * 60)
    print(f"   추가된 컬럼: 5개")
    print(f"   적용된 수식: {5 * num_rows}개 (5컬럼 × {num_rows}행)")
    print(f"   최종 컬럼 수: {col_count + 5}개")
    print()
    print("🔍 테스트: 시트1 L열(담당소장ID), P열(사용자격증ID) 입력 시 M,N / Q,R,S 자동 표시 확인")


if __name__ == '__main__':
    main()
