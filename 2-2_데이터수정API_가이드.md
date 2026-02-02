# 2-2. 데이터 수정 API 개발 가이드

## 🎯 목표
Google Sheets 데이터를 HTTP POST/PUT 요청으로 수정하는 API 구축

---

## 📋 구현할 엔드포인트

### 데이터 수정
- `POST /api/sites` - 현장 생성
- `PUT /api/sites/{id}` - 현장 수정
- `POST /api/sites/{id}/assign` - 소장 배정
- `POST /api/sites/{id}/unassign` - 소장 배정 해제
- `PUT /api/personnel/{id}` - 인력 정보 수정
- `PUT /api/certificates/{id}` - 자격증 정보 수정

---

## 🔧 1단계: Sheets 서비스 확장

### api/services/sheets_service.py에 추가

```python
def update_cell(self, range_name, value):
    """셀 업데이트"""
    body = {
        'values': [[value]]
    }
    
    result = self.service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_name,
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
    
    return result

def update_row(self, range_name, values):
    """행 업데이트 (여러 셀)"""
    body = {
        'values': [values]
    }
    
    result = self.service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_name,
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
    
    return result

def batch_update(self, updates):
    """여러 셀 일괄 업데이트"""
    data = []
    for update in updates:
        data.append({
            'range': update['range'],
            'values': update['values']
        })
    
    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': data
    }
    
    result = self.service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body=body
    ).execute()
    
    return result

def find_row_by_id(self, sheet_name, id_value):
    """ID로 행 번호 찾기 (2행부터 시작, 0-based)"""
    values = self.read_sheet(f'{sheet_name}!A2:A')
    
    for idx, row in enumerate(values):
        if row and row[0] == id_value:
            return idx + 2  # 헤더 + 1 (0-based -> 1-based)
    
    return None

def append_row(self, sheet_name, values):
    """행 추가 (마지막에)"""
    body = {
        'values': [values]
    }
    
    result = self.service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f'{sheet_name}!A:A',
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
    
    return result
```

---

## 🛣️ 2단계: 현장 수정 라우트

### api/routes/sites.py에 추가

```python
@bp.route('/sites', methods=['POST'])
def create_site():
    """현장 생성"""
    try:
        data = request.json
        
        # 필수 필드 검증
        required_fields = ['현장ID', '현장명', '회사구분', '주소']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'MISSING_FIELD',
                        'message': f'{field}는 필수 입력 항목입니다'
                    }
                }), 400
        
        # 중복 체크
        existing = sheets_service.get_site_by_id(data['현장ID'])
        if existing:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'DUPLICATE_ID',
                    'message': f"현장ID {data['현장ID']}가 이미 존재합니다"
                }
            }), 400
        
        # 새 행 데이터 준비
        now = datetime.now().strftime('%Y-%m-%d')
        row_data = [
            data['현장ID'],
            data['현장명'],
            data['회사구분'],
            data['주소'],
            data.get('위도', ''),
            data.get('경도', ''),
            data.get('건축허가일', ''),
            data.get('착공예정일', ''),
            data.get('준공일', ''),
            data.get('현장상태', '건축허가'),
            data.get('특이사항', ''),
            data.get('담당소장ID', ''),
            # M, N열: VLOOKUP (자동)
            '',  # 담당소장명
            '',  # 담당소장연락처
            data.get('사용자격증ID', ''),
            # P, Q, R열: VLOOKUP (자동)
            '',  # 자격증명
            '',  # 자격증소유자명
            '',  # 자격증소유자연락처
            data.get('준공필증파일URL', ''),
            data.get('배정상태', '미배정'),
            now,  # 등록일
            now   # 수정일
        ]
        
        # 행 추가
        sheets_service.append_row('시트1', row_data)
        
        return jsonify({
            'success': True,
            'data': {
                '현장ID': data['현장ID'],
                '현장명': data['현장명']
            },
            'message': '현장이 생성되었습니다',
            'timestamp': datetime.now().isoformat()
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'CREATE_ERROR',
                'message': str(e)
            }
        }), 500

@bp.route('/sites/<site_id>', methods=['PUT'])
def update_site(site_id):
    """현장 정보 수정"""
    try:
        # 현장 존재 확인
        site = sheets_service.get_site_by_id(site_id)
        if not site:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SITE_NOT_FOUND',
                    'message': f'현장ID {site_id}를 찾을 수 없습니다'
                }
            }), 404
        
        # 행 번호 찾기
        row_num = sheets_service.find_row_by_id('시트1', site_id)
        if not row_num:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'ROW_NOT_FOUND',
                    'message': '행을 찾을 수 없습니다'
                }
            }), 404
        
        data = request.json
        updates = []
        
        # 컬럼 매핑 (수정 가능한 필드만)
        column_map = {
            '현장명': 'B',
            '주소': 'D',
            '위도': 'E',
            '경도': 'F',
            '건축허가일': 'G',
            '착공예정일': 'H',
            '준공일': 'I',
            '현장상태': 'J',
            '특이사항': 'K',
            '담당소장ID': 'L',
            '사용자격증ID': 'O',
            '준공필증파일URL': 'S',
            '배정상태': 'T'
        }
        
        # 수정할 필드만 업데이트 준비
        for field, column in column_map.items():
            if field in data:
                updates.append({
                    'range': f'시트1!{column}{row_num}',
                    'values': [[data[field]]]
                })
        
        # 수정일 자동 업데이트
        now = datetime.now().strftime('%Y-%m-%d')
        updates.append({
            'range': f'시트1!V{row_num}',  # 수정일 컬럼
            'values': [[now]]
        })
        
        # 일괄 업데이트
        if updates:
            sheets_service.batch_update(updates)
        
        return jsonify({
            'success': True,
            'data': {
                '현장ID': site_id,
                'updated_fields': list(data.keys())
            },
            'message': '현장 정보가 수정되었습니다',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'UPDATE_ERROR',
                'message': str(e)
            }
        }), 500

@bp.route('/sites/<site_id>/assign', methods=['POST'])
def assign_manager(site_id):
    """소장 배정"""
    try:
        # 현장 존재 확인
        site = sheets_service.get_site_by_id(site_id)
        if not site:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SITE_NOT_FOUND',
                    'message': f'현장ID {site_id}를 찾을 수 없습니다'
                }
            }), 404
        
        data = request.json
        manager_id = data.get('manager_id')
        certificate_id = data.get('certificate_id')
        
        # 필수 파라미터 확인
        if not manager_id or not certificate_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_PARAMS',
                    'message': 'manager_id와 certificate_id가 필요합니다'
                }
            }), 400
        
        # 소장 존재 확인
        manager = sheets_service.get_personnel_by_id(manager_id)
        if not manager:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MANAGER_NOT_FOUND',
                    'message': f'인력ID {manager_id}를 찾을 수 없습니다'
                }
            }), 404
        
        # 자격증 존재 확인
        certificate = sheets_service.get_certificate_by_id(certificate_id)
        if not certificate:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'CERTIFICATE_NOT_FOUND',
                    'message': f'자격증ID {certificate_id}를 찾을 수 없습니다'
                }
            }), 404
        
        # 자격증 사용 가능 여부 확인
        if certificate['사용가능여부'] != '사용가능':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'CERTIFICATE_NOT_AVAILABLE',
                    'message': f'자격증 {certificate_id}는 사용할 수 없습니다'
                }
            }), 400
        
        # 행 번호 찾기
        site_row = sheets_service.find_row_by_id('시트1', site_id)
        manager_row = sheets_service.find_row_by_id('시트2', manager_id)
        cert_row = sheets_service.find_row_by_id('시트3', certificate_id)
        
        # 배정 실행 (일괄 업데이트)
        now = datetime.now().strftime('%Y-%m-%d')
        updates = []
        
        # 1. 현장에 소장 배정
        updates.append({
            'range': f'시트1!L{site_row}',  # 담당소장ID
            'values': [[manager_id]]
        })
        updates.append({
            'range': f'시트1!O{site_row}',  # 사용자격증ID
            'values': [[certificate_id]]
        })
        updates.append({
            'range': f'시트1!T{site_row}',  # 배정상태
            'values': [['배정완료']]
        })
        updates.append({
            'range': f'시트1!V{site_row}',  # 수정일
            'values': [[now]]
        })
        
        # 2. 소장 상태 업데이트
        current_count = int(manager['현재담당현장수'] or 0)
        updates.append({
            'range': f'시트2!I{manager_row}',  # 현재담당현장수
            'values': [[current_count + 1]]
        })
        updates.append({
            'range': f'시트2!H{manager_row}',  # 현재상태
            'values': [['투입중']]
        })
        
        # 3. 자격증 상태 업데이트
        updates.append({
            'range': f'시트3!J{cert_row}',  # 사용가능여부
            'values': [['사용중']]
        })
        updates.append({
            'range': f'시트3!K{cert_row}',  # 현재사용현장ID
            'values': [[site_id]]
        })
        
        # 일괄 업데이트 실행
        sheets_service.batch_update(updates)
        
        return jsonify({
            'success': True,
            'data': {
                '현장ID': site_id,
                '현장명': site['현장명'],
                '담당소장': manager['성명'],
                '자격증': certificate['자격증명']
            },
            'message': '소장이 배정되었습니다',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'ASSIGN_ERROR',
                'message': str(e)
            }
        }), 500

@bp.route('/sites/<site_id>/unassign', methods=['POST'])
def unassign_manager(site_id):
    """소장 배정 해제"""
    try:
        # 현장 정보 조회
        site = sheets_service.get_site_by_id(site_id)
        if not site:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SITE_NOT_FOUND',
                    'message': f'현장ID {site_id}를 찾을 수 없습니다'
                }
            }), 404
        
        # 배정된 소장이 없으면 에러
        if not site['담당소장ID']:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_ASSIGNED',
                    'message': '배정된 소장이 없습니다'
                }
            }), 400
        
        manager_id = site['담당소장ID']
        cert_id = site['사용자격증ID']
        
        # 행 번호 찾기
        site_row = sheets_service.find_row_by_id('시트1', site_id)
        manager_row = sheets_service.find_row_by_id('시트2', manager_id)
        cert_row = sheets_service.find_row_by_id('시트3', cert_id)
        
        # 소장 정보 조회
        manager = sheets_service.get_personnel_by_id(manager_id)
        
        # 배정 해제 (일괄 업데이트)
        now = datetime.now().strftime('%Y-%m-%d')
        updates = []
        
        # 1. 현장에서 소장 제거
        updates.append({
            'range': f'시트1!L{site_row}',  # 담당소장ID
            'values': [['']]
        })
        updates.append({
            'range': f'시트1!O{site_row}',  # 사용자격증ID
            'values': [['']]
        })
        updates.append({
            'range': f'시트1!T{site_row}',  # 배정상태
            'values': [['미배정']]
        })
        updates.append({
            'range': f'시트1!V{site_row}',  # 수정일
            'values': [[now]]
        })
        
        # 2. 소장 상태 업데이트
        current_count = int(manager['현재담당현장수'] or 0)
        new_count = max(0, current_count - 1)
        updates.append({
            'range': f'시트2!I{manager_row}',  # 현재담당현장수
            'values': [[new_count]]
        })
        
        # 담당 현장이 없으면 투입가능으로 변경
        if new_count == 0:
            updates.append({
                'range': f'시트2!H{manager_row}',  # 현재상태
                'values': [['투입가능']]
            })
        
        # 3. 자격증 상태 업데이트
        if cert_id:
            updates.append({
                'range': f'시트3!J{cert_row}',  # 사용가능여부
                'values': [['사용가능']]
            })
            updates.append({
                'range': f'시트3!K{cert_row}',  # 현재사용현장ID
                'values': [['']]
            })
        
        # 일괄 업데이트 실행
        sheets_service.batch_update(updates)
        
        return jsonify({
            'success': True,
            'data': {
                '현장ID': site_id,
                '현장명': site['현장명']
            },
            'message': '소장 배정이 해제되었습니다',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'UNASSIGN_ERROR',
                'message': str(e)
            }
        }), 500
```

---

## 🧪 테스트

### Postman / curl 테스트

```bash
# 1. 현장 생성
curl -X POST http://localhost:5000/api/sites \
  -H "Content-Type: application/json" \
  -d '{
    "현장ID": "S099",
    "현장명": "테스트 현장",
    "회사구분": "더존종합건설",
    "주소": "서울시 강남구",
    "현장상태": "건축허가"
  }'

# 2. 현장 정보 수정
curl -X PUT http://localhost:5000/api/sites/S099 \
  -H "Content-Type: application/json" \
  -d '{
    "현장명": "테스트 현장 (수정)",
    "현장상태": "착공예정",
    "착공예정일": "2026-03-01"
  }'

# 3. 소장 배정
curl -X POST http://localhost:5000/api/sites/S003/assign \
  -H "Content-Type: application/json" \
  -d '{
    "manager_id": "P001",
    "certificate_id": "C015"
  }'

# 4. 소장 배정 해제
curl -X POST http://localhost:5000/api/sites/S003/unassign

# 5. 배정 결과 확인
curl http://localhost:5000/api/sites/S003
```

---

## 🔒 검증 로직

### api/services/validation.py (새 파일)

```python
"""
데이터 검증 로직
"""

class ValidationError(Exception):
    """검증 오류"""
    pass

def validate_site_data(data, is_update=False):
    """현장 데이터 검증"""
    errors = []
    
    # 필수 필드 (생성 시)
    if not is_update:
        required = ['현장ID', '현장명', '회사구분', '주소']
        for field in required:
            if field not in data or not data[field]:
                errors.append(f'{field}는 필수 입력 항목입니다')
    
    # 회사구분 검증
    if '회사구분' in data:
        if data['회사구분'] not in ['더존종합건설', '더존하우징']:
            errors.append('회사구분은 "더존종합건설" 또는 "더존하우징"이어야 합니다')
    
    # 현장상태 검증
    if '현장상태' in data:
        valid_states = ['건축허가', '착공예정', '착공중', '준공']
        if data['현장상태'] not in valid_states:
            errors.append(f'현장상태는 {", ".join(valid_states)} 중 하나여야 합니다')
    
    # 배정상태 검증
    if '배정상태' in data:
        if data['배정상태'] not in ['배정완료', '미배정']:
            errors.append('배정상태는 "배정완료" 또는 "미배정"이어야 합니다')
    
    # 날짜 형식 검증 (YYYY-MM-DD)
    date_fields = ['건축허가일', '착공예정일', '준공일']
    for field in date_fields:
        if field in data and data[field]:
            try:
                from datetime import datetime
                datetime.strptime(data[field], '%Y-%m-%d')
            except ValueError:
                errors.append(f'{field}는 YYYY-MM-DD 형식이어야 합니다')
    
    if errors:
        raise ValidationError('; '.join(errors))
    
    return True

def validate_assignment(site, manager, certificate):
    """배정 가능 여부 검증"""
    errors = []
    
    # 현장이 이미 배정됨
    if site['배정상태'] == '배정완료':
        errors.append('이미 소장이 배정된 현장입니다')
    
    # 소장 상태 확인
    if manager['현재상태'] == '퇴사':
        errors.append('퇴사한 소장은 배정할 수 없습니다')
    
    if manager['현재상태'] == '휴가':
        errors.append('휴가중인 소장은 배정할 수 없습니다')
    
    # 자격증 사용 가능 여부
    if certificate['사용가능여부'] != '사용가능':
        errors.append(f"자격증이 '{certificate['사용가능여부']}' 상태입니다")
    
    # 자격증과 소장 일치 여부 (선택적)
    if certificate['소유자ID'] != manager['인력ID']:
        # 경고만 (사무직원 자격증 사용 가능)
        pass
    
    if errors:
        raise ValidationError('; '.join(errors))
    
    return True
```

---

## ✅ 체크리스트

### 기본 기능
- [ ] 현장 생성 API 작동
- [ ] 현장 수정 API 작동
- [ ] 소장 배정 API 작동
- [ ] 소장 배정 해제 API 작동

### 검증 로직
- [ ] 필수 필드 검증
- [ ] 중복 ID 체크
- [ ] 날짜 형식 검증
- [ ] 배정 가능 여부 검증

### 관계 데이터
- [ ] 소장 담당현장수 자동 증가
- [ ] 소장 상태 자동 변경
- [ ] 자격증 상태 자동 변경
- [ ] 배정 해제 시 자동 복구

### 에러 처리
- [ ] 404 에러 (리소스 없음)
- [ ] 400 에러 (잘못된 요청)
- [ ] 500 에러 (서버 오류)

---

**완료 시간**: 약 4시간  
**난이도**: ⭐⭐⭐⭐☆  
**다음 단계**: 실시간 동기화 (선택) 또는 HTML 앱 연동
