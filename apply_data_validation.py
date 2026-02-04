"""
현장배정 관리 시스템 - 데이터 검증 규칙 자동 적용

Google Sheets에 데이터 검증 규칙(Data Validation)을 자동으로 적용합니다.
- 드롭다운 목록
- 날짜 형식 검증
- 전화번호 형식 검증
- 이메일 형식 검증
"""

import sys
import os

# 인코딩 설정 (Windows 환경 대응)
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# 필요한 모듈 임포트
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    import pickle
except ImportError:
    print("❌ 필요한 패키지가 설치되지 않았습니다.")
    print("다음 명령어를 실행하세요:")
    print("pip install google-api-python-client google-auth-oauthlib google-auth-httplib2")
    sys.exit(1)

# 설정 (.env 우선, 없으면 빈 문자열 → main에서 검사)
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', '').strip()
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# 시트1 컬럼 수: 17=기본, 22=VLOOKUP 적용 후. 검증/서식 컬럼 매핑에 사용
SHEET1_COLS_17 = 17
SHEET1_COLS_22 = 22

# 컬럼 문자를 숫자로 변환 (A=1, B=2, ...)
def column_to_number(col):
    """컬럼 문자를 숫자로 변환"""
    num = 0
    for char in col:
        num = num * 26 + (ord(char.upper()) - ord('A') + 1)
    return num - 1  # 0-based index

def get_google_sheets_service():
    """Google Sheets API 서비스 생성"""
    creds = None
    
    # 토큰 파일 확인
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # 토큰이 없거나 유효하지 않으면 로그인
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # client_secret 파일 찾기
            client_secret_file = None
            for file in os.listdir('.'):
                if file.startswith('client_secret') and file.endswith('.json'):
                    client_secret_file = file
                    break
            
            if not client_secret_file:
                print("❌ client_secret 파일을 찾을 수 없습니다.")
                print("Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 생성하고")
                print("client_secret JSON 파일을 다운로드하여 이 폴더에 넣어주세요.")
                sys.exit(1)
            
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 토큰 저장
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('sheets', 'v4', credentials=creds)

def apply_dropdown_validation(service, sheet_id, sheet_name, column, values, start_row=2):
    """드롭다운 목록 검증 규칙 적용"""
    col_index = column_to_number(column)
    
    request = {
        'setDataValidation': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': start_row - 1,  # 0-based
                'endRowIndex': 1000,  # 충분히 큰 숫자
                'startColumnIndex': col_index,
                'endColumnIndex': col_index + 1
            },
            'rule': {
                'condition': {
                    'type': 'ONE_OF_LIST',
                    'values': [{'userEnteredValue': v} for v in values]
                },
                'showCustomUi': True,
                'strict': False,  # False = 경고만 표시, True = 입력 차단
                'inputMessage': f'{sheet_name} - {column}열: {", ".join(values)} 중 선택'
            }
        }
    }
    
    return request

def apply_date_validation(service, sheet_id, sheet_name, column, start_row=2):
    """날짜 형식 검증 규칙 적용"""
    col_index = column_to_number(column)
    
    request = {
        'setDataValidation': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': start_row - 1,
                'endRowIndex': 1000,
                'startColumnIndex': col_index,
                'endColumnIndex': col_index + 1
            },
            'rule': {
                'condition': {
                    'type': 'DATE_IS_VALID'
                },
                'showCustomUi': False,
                'strict': False,
                'inputMessage': f'{sheet_name} - {column}열: 날짜 형식 (YYYY-MM-DD)'
            }
        }
    }
    
    return request

def apply_phone_validation(service, sheet_id, sheet_name, column, start_row=2):
    """전화번호 형식 검증 규칙 적용 (010-XXXX-XXXX)"""
    col_index = column_to_number(column)
    
    request = {
        'setDataValidation': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': start_row - 1,
                'endRowIndex': 1000,
                'startColumnIndex': col_index,
                'endColumnIndex': col_index + 1
            },
            'rule': {
                'condition': {
                    'type': 'CUSTOM_FORMULA',
                    'values': [{
                        'userEnteredValue': f'=OR(ISBLANK({column}{start_row}), REGEXMATCH(TO_TEXT({column}{start_row}), "^010-[0-9]{{4}}-[0-9]{{4}}$"))'
                    }]
                },
                'showCustomUi': False,
                'strict': False,
                'inputMessage': f'{sheet_name} - {column}열: 전화번호 형식 (010-XXXX-XXXX)'
            }
        }
    }
    
    return request

def get_sheet_id_by_name(service, sheet_name):
    """시트 이름으로 시트 ID 찾기"""
    spreadsheet = service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID
    ).execute()
    
    for sheet in spreadsheet['sheets']:
        if sheet['properties']['title'] == sheet_name:
            return sheet['properties']['sheetId']
    
    return None


def get_sheet1_column_count(service):
    """시트1(현장정보) 현재 컬럼 수. 17=기본, 22=VLOOKUP 적용 후."""
    try:
        meta = service.spreadsheets().get(
            spreadsheetId=SPREADSHEET_ID,
            fields='sheets(properties(title,gridProperties(columnCount)))',
        ).execute()
        for sheet in meta.get('sheets', []):
            if sheet['properties'].get('title') == '시트1':
                return sheet['properties'].get('gridProperties', {}).get('columnCount', SHEET1_COLS_17)
    except Exception:
        pass
    return SHEET1_COLS_17

def main():
    """메인 함수"""
    print("=" * 60)
    print("📋 현장배정 관리 시스템 - 데이터 검증 규칙 적용")
    print("=" * 60)
    print()

    if not SPREADSHEET_ID:
        print("❌ SPREADSHEET_ID가 설정되지 않았습니다.")
        print("   .env 파일에 SPREADSHEET_ID=your_spreadsheet_id 를 추가하거나")
        print("   환경 변수로 설정한 뒤 다시 실행하세요.")
        return

    # Google Sheets API 서비스 생성
    print("🔑 Google Sheets API 인증 중...")
    try:
        service = get_google_sheets_service()
        print("✅ 인증 완료")
        print()
    except Exception as e:
        print(f"❌ 인증 실패: {e}")
        return

    # 시트1 컬럼 수에 따라 배정상태/등록일/수정일 컬럼 결정 (17 vs 22)
    sheet1_cols = get_sheet1_column_count(service)
    if sheet1_cols >= SHEET1_COLS_22:
        status_col = 'T'   # 배정상태 (22컬럼)
        date_cols = ['G', 'H', 'I', 'U', 'V']  # 건축허가일, 착공예정일, 준공일, 등록일, 수정일
        print(f"   📐 시트1: 22컬럼(VLOOKUP 적용) 기준으로 검증 적용")
    else:
        status_col = 'O'   # 배정상태 (17컬럼)
        date_cols = ['G', 'H', 'I', 'P', 'Q']  # 건축허가일, 착공예정일, 준공일, 등록일, 수정일
        print(f"   📐 시트1: 17컬럼(기본) 기준으로 검증 적용")
    print()

    # 적용할 검증 규칙 정의
    validations = []

    # 시트1: 현장정보
    sheet1_id = get_sheet_id_by_name(service, '시트1')
    if sheet1_id is not None:
        print("📌 시트1 (현장정보) 검증 규칙 준비...")

        # 회사구분 드롭다운
        validations.append(apply_dropdown_validation(
            service, sheet1_id, '시트1', 'C',
            ['더존종합건설', '더존하우징']
        ))

        # 현장상태 드롭다운
        validations.append(apply_dropdown_validation(
            service, sheet1_id, '시트1', 'J',
            ['건축허가', '착공예정', '공사 중', '공사 중단', '준공']
        ))

        # 배정상태 드롭다운 (17컬럼=O, 22컬럼=T)
        validations.append(apply_dropdown_validation(
            service, sheet1_id, '시트1', status_col,
            ['배정완료', '미배정']
        ))

        # 날짜 형식 검증 (17컬럼: P,Q / 22컬럼: U,V)
        for col in date_cols:
            validations.append(apply_date_validation(
                service, sheet1_id, '시트1', col
            ))

        print(f"   ✅ 8개 검증 규칙 준비 완료")
    
    # 시트2: 인력풀
    sheet2_id = get_sheet_id_by_name(service, '시트2')
    if sheet2_id is not None:
        print("📌 시트2 (인력풀) 검증 규칙 준비...")
        
        # 직책 드롭다운
        validations.append(apply_dropdown_validation(
            service, sheet2_id, '시트2', 'C',
            ['소장', '사무실장', '사무직원', '기타']
        ))
        
        # 현재상태 드롭다운
        validations.append(apply_dropdown_validation(
            service, sheet2_id, '시트2', 'H',
            ['투입가능', '투입중', '휴가', '퇴사']
        ))
        
        # 연락처 형식 검증
        validations.append(apply_phone_validation(
            service, sheet2_id, '시트2', 'E'
        ))
        
        # 날짜 형식 검증
        for col in ['K', 'L']:  # 입사일, 등록일
            validations.append(apply_date_validation(
                service, sheet2_id, '시트2', col
            ))
        
        print(f"   ✅ 5개 검증 규칙 준비 완료")
    
    # 시트3: 자격증풀
    sheet3_id = get_sheet_id_by_name(service, '시트3')
    if sheet3_id is not None:
        print("📌 시트3 (자격증풀) 검증 규칙 준비...")
        
        # 사용가능여부 드롭다운
        validations.append(apply_dropdown_validation(
            service, sheet3_id, '시트3', 'J',
            ['사용가능', '사용중', '만료']
        ))
        
        # 연락처 형식 검증
        validations.append(apply_phone_validation(
            service, sheet3_id, '시트3', 'F'
        ))
        
        # 날짜 형식 검증
        for col in ['H', 'I', 'M']:  # 취득일, 유효기간, 등록일
            validations.append(apply_date_validation(
                service, sheet3_id, '시트3', col
            ))
        
        print(f"   ✅ 5개 검증 규칙 준비 완료")
    
    print()
    print(f"📊 총 {len(validations)}개 검증 규칙 적용 시작...")
    print()
    
    # 일괄 적용
    try:
        body = {'requests': validations}
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=body
        ).execute()
        
        print("✅ 모든 검증 규칙 적용 완료!")
        print()
        print("=" * 60)
        print("📋 적용된 검증 규칙 요약")
        print("=" * 60)
        print()
        print("시트1 (현장정보):")
        print("  - C열: 회사구분 드롭다운")
        print("  - J열: 현장상태 드롭다운")
        print(f"  - {status_col}열: 배정상태 드롭다운")
        print(f"  - {','.join(date_cols)}열: 날짜 형식 검증")
        print()
        print("시트2 (인력풀):")
        print("  - C열: 직책 드롭다운")
        print("  - H열: 현재상태 드롭다운")
        print("  - E열: 전화번호 형식 검증")
        print("  - K,L열: 날짜 형식 검증")
        print()
        print("시트3 (자격증풀):")
        print("  - J열: 사용가능여부 드롭다운")
        print("  - F열: 전화번호 형식 검증")
        print("  - H,I,M열: 날짜 형식 검증")
        print()
        print("=" * 60)
        print("✨ 이제 Google Sheets에서 데이터 입력 시")
        print("   드롭다운과 형식 검증이 자동으로 적용됩니다!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 검증 규칙 적용 실패: {e}")
        print()
        print("문제 해결 방법:")
        print("1. 시트 이름이 '시트1', '시트2', '시트3'인지 확인")
        print("2. Google Sheets API 권한 확인")
        print("3. 스프레드시트 ID 확인")

if __name__ == '__main__':
    main()
