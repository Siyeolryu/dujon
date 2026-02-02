"""
현장배정 관리 시스템 - 조건부 서식 자동 적용

Google Sheets에 조건부 서식(Conditional Formatting)을 자동으로 적용합니다.
- 배정상태/현장상태/현재상태별 색상
- 착공예정일·유효기간 지남 경고
- 헤더 행·줄무늬 효과
"""

import sys
import os

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

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

SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', '15fAEzkC9FCLA6sG1N--f69r-32WHoYLvmXcwED5xWzM')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def get_google_sheets_service():
    """Google Sheets API 서비스 생성"""
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


def create_header_format(sheet_id):
    """헤더 행 회색 배경 + 굵게"""
    return {
        'repeatCell': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': 0,
                'endRowIndex': 1,
            },
            'cell': {
                'userEnteredFormat': {
                    'backgroundColor': {'red': 0.95, 'green': 0.95, 'blue': 0.95},
                    'textFormat': {'bold': True, 'fontSize': 10},
                    'horizontalAlignment': 'CENTER',
                    'verticalAlignment': 'MIDDLE',
                }
            },
            'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)',
        }
    }


def create_striped_rows_format(sheet_id):
    """홀수 행에 옅은 회색 배경"""
    return {
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{
                    'sheetId': sheet_id,
                    'startRowIndex': 1,
                    'endRowIndex': 1000,
                }],
                'booleanRule': {
                    'condition': {
                        'type': 'CUSTOM_FORMULA',
                        'values': [{'userEnteredValue': '=MOD(ROW(),2)=1'}],
                    },
                    'format': {
                        'backgroundColor': {'red': 0.98, 'green': 0.98, 'blue': 0.98},
                    },
                },
            },
            'index': 100,
        }
    }


def apply_sheet1_formatting(sheet_id):
    """시트1 (현장정보) 조건부 서식"""
    requests = []
    requests.append(create_header_format(sheet_id))

    # 배정상태 (O열 = 14)
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000,
                           'startColumnIndex': 14, 'endColumnIndex': 15}],
                'booleanRule': {
                    'condition': {'type': 'TEXT_EQ', 'values': [{'userEnteredValue': '배정완료'}]},
                    'format': {'backgroundColor': {'red': 0.85, 'green': 0.92, 'blue': 0.83}},
                },
            },
            'index': 0,
        }
    })
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000,
                           'startColumnIndex': 14, 'endColumnIndex': 15}],
                'booleanRule': {
                    'condition': {'type': 'TEXT_EQ', 'values': [{'userEnteredValue': '미배정'}]},
                    'format': {'backgroundColor': {'red': 0.96, 'green': 0.8, 'blue': 0.8}},
                },
            },
            'index': 1,
        }
    })

    # 현장상태 (J열 = 9)
    status_colors = [
        ('건축허가', {'red': 0.81, 'green': 0.89, 'blue': 0.95}),
        ('착공예정', {'red': 0.99, 'green': 0.9, 'blue': 0.8}),
        ('착공중', {'red': 1.0, 'green': 0.95, 'blue': 0.8}),
        ('준공', {'red': 0.85, 'green': 0.92, 'blue': 0.83}),
    ]
    for idx, (status, color) in enumerate(status_colors):
        requests.append({
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000,
                               'startColumnIndex': 9, 'endColumnIndex': 10}],
                    'booleanRule': {
                        'condition': {'type': 'TEXT_EQ', 'values': [{'userEnteredValue': status}]},
                        'format': {'backgroundColor': color},
                    },
                },
                'index': 2 + idx,
            }
        })

    # 착공예정일 지남 (H열 = 7)
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000,
                           'startColumnIndex': 7, 'endColumnIndex': 8}],
                'booleanRule': {
                    'condition': {
                        'type': 'CUSTOM_FORMULA',
                        'values': [{'userEnteredValue': '=AND(NOT(ISBLANK(H2)), H2<TODAY())'}],
                    },
                    'format': {
                        'backgroundColor': {'red': 1.0, 'green': 0.4, 'blue': 0.4},
                        'textFormat': {
                            'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                            'bold': True,
                        },
                    },
                },
            },
            'index': 6,
        }
    })

    # 회사구분 (C열 = 2)
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000,
                           'startColumnIndex': 2, 'endColumnIndex': 3}],
                'booleanRule': {
                    'condition': {'type': 'TEXT_EQ', 'values': [{'userEnteredValue': '더존종합건설'}]},
                    'format': {'backgroundColor': {'red': 0.9, 'green': 0.95, 'blue': 1.0}},
                },
            },
            'index': 7,
        }
    })
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000,
                           'startColumnIndex': 2, 'endColumnIndex': 3}],
                'booleanRule': {
                    'condition': {'type': 'TEXT_EQ', 'values': [{'userEnteredValue': '더존하우징'}]},
                    'format': {'backgroundColor': {'red': 1.0, 'green': 0.95, 'blue': 0.9}},
                },
            },
            'index': 8,
        }
    })

    requests.append(create_striped_rows_format(sheet_id))
    return requests


def apply_sheet2_formatting(sheet_id):
    """시트2 (인력풀) 조건부 서식"""
    requests = []
    requests.append(create_header_format(sheet_id))

    status_formats = [
        ('투입가능', {'red': 0.85, 'green': 0.92, 'blue': 0.83}, 0),
        ('투입중', {'red': 1.0, 'green': 0.95, 'blue': 0.8}, 1),
        ('휴가', {'red': 0.94, 'green': 0.94, 'blue': 0.94}, 2),
        ('퇴사', {'red': 0.96, 'green': 0.8, 'blue': 0.8}, 3),
    ]
    for status, color, idx in status_formats:
        requests.append({
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000,
                               'startColumnIndex': 7, 'endColumnIndex': 8}],
                    'booleanRule': {
                        'condition': {'type': 'TEXT_EQ', 'values': [{'userEnteredValue': status}]},
                        'format': {'backgroundColor': color},
                    },
                },
                'index': idx,
            }
        })

    # 현재담당현장수 >= 3 (I열 = 8)
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000,
                           'startColumnIndex': 8, 'endColumnIndex': 9}],
                'booleanRule': {
                    'condition': {'type': 'NUMBER_GREATER_THAN_EQ', 'values': [{'userEnteredValue': '3'}]},
                    'format': {'backgroundColor': {'red': 0.99, 'green': 0.9, 'blue': 0.8}},
                },
            },
            'index': 4,
        }
    })
    requests.append(create_striped_rows_format(sheet_id))
    return requests


def apply_sheet3_formatting(sheet_id):
    """시트3 (자격증풀) 조건부 서식"""
    requests = []
    requests.append(create_header_format(sheet_id))

    avail_formats = [
        ('사용가능', {'red': 0.85, 'green': 0.92, 'blue': 0.83}, 0),
        ('사용중', {'red': 1.0, 'green': 0.95, 'blue': 0.8}, 1),
        ('만료', {'red': 0.96, 'green': 0.8, 'blue': 0.8}, 2),
    ]
    for status, color, idx in avail_formats:
        requests.append({
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000,
                               'startColumnIndex': 9, 'endColumnIndex': 10}],
                    'booleanRule': {
                        'condition': {'type': 'TEXT_EQ', 'values': [{'userEnteredValue': status}]},
                        'format': {'backgroundColor': color},
                    },
                },
                'index': idx,
            }
        })

    # 유효기간 만료 (I열 = 8)
    requests.append({
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 1000,
                           'startColumnIndex': 8, 'endColumnIndex': 9}],
                'booleanRule': {
                    'condition': {
                        'type': 'CUSTOM_FORMULA',
                        'values': [{'userEnteredValue': '=AND(NOT(ISBLANK(I2)), I2<TODAY())'}],
                    },
                    'format': {
                        'backgroundColor': {'red': 1.0, 'green': 0.4, 'blue': 0.4},
                        'textFormat': {
                            'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                            'bold': True,
                        },
                    },
                },
            },
            'index': 3,
        }
    })
    requests.append(create_striped_rows_format(sheet_id))
    return requests


def main():
    print("=" * 60)
    print("📋 조건부 서식 자동 적용")
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

    all_requests = []
    sheet_names = [('시트1', apply_sheet1_formatting), ('시트2', apply_sheet2_formatting), ('시트3', apply_sheet3_formatting)]

    for name, apply_fn in sheet_names:
        sheet_id = get_sheet_id_by_name(service, name)
        if sheet_id is None:
            print(f"⚠️ {name}을(를) 찾을 수 없습니다. 건너뜁니다.")
            continue
        print(f"🎨 {name} 서식 적용 중...")
        reqs = apply_fn(sheet_id)
        all_requests.extend(reqs)
        print(f"   ✅ {len(reqs)}개 규칙 준비 완료")

    if not all_requests:
        print("적용할 규칙이 없습니다.")
        return

    print()
    print(f"📊 총 {len(all_requests)}개 규칙 적용 시작...")
    try:
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={'requests': all_requests},
        ).execute()
        print("✅ 모든 조건부 서식 적용 완료!")
    except Exception as e:
        print(f"❌ 적용 실패: {e}")


if __name__ == '__main__':
    main()
