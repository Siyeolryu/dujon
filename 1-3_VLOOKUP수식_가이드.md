# VLOOKUP 수식 자동화 개발 가이드

## 🎯 목표
ID만 입력하면 관련 정보가 자동으로 표시되는 똑똑한 데이터베이스 구축

---

## 📊 추가할 컬럼 및 수식

### 시트1: 현장정보에 추가할 5개 컬럼

| 위치 | 새 컬럼명 | VLOOKUP 대상 | 조회 시트 | 조회 정보 |
|------|----------|-------------|----------|----------|
| M열 | 담당소장명 | 담당소장ID (L열) | 시트2 (인력풀) | 성명 (B열) |
| N열 | 담당소장연락처 | 담당소장ID (L열) | 시트2 (인력풀) | 연락처 (E열) |
| R열 | 자격증명 | 사용자격증ID (P열) | 시트3 (자격증풀) | 자격증명 (B열) |
| S열 | 자격증소유자명 | 사용자격증ID (P열) | 시트3 (자격증풀) | 소유자명 (E열) |
| T열 | 자격증소유자연락처 | 사용자격증ID (P열) | 시트3 (자격증풀) | 소유자연락처 (F열) |

### 수식 예시

**담당소장명 (M열)**:
```excel
=IF(ISBLANK(L2),"",VLOOKUP(L2,시트2!A:B,2,FALSE))
```

**담당소장연락처 (N열)**:
```excel
=IF(ISBLANK(L2),"",VLOOKUP(L2,시트2!A:E,5,FALSE))
```

**자격증명 (R열)**:
```excel
=IF(ISBLANK(P2),"",VLOOKUP(P2,시트3!A:B,2,FALSE))
```

**자격증소유자명 (S열)**:
```excel
=IF(ISBLANK(P2),"",VLOOKUP(P2,시트3!A:E,5,FALSE))
```

**자격증소유자연락처 (T열)**:
```excel
=IF(ISBLANK(P2),"",VLOOKUP(P2,시트3!A:F,6,FALSE))
```

---

## 🔧 VLOOKUP 수식 해부

### 기본 구조
```
=VLOOKUP(검색값, 검색범위, 열번호, 정확히일치여부)
```

### 파라미터 설명

1. **검색값**: 찾고자 하는 값 (예: L2 - 담당소장ID)
2. **검색범위**: 검색할 테이블 범위 (예: 시트2!A:B)
3. **열번호**: 반환할 값이 있는 열 (1부터 시작)
4. **정확히일치여부**: 
   - `FALSE` 또는 `0` = 정확히 일치
   - `TRUE` 또는 `1` = 근사값 일치

### IF 함수로 감싸는 이유
```excel
=IF(ISBLANK(L2),"",VLOOKUP(...))
```

- `ISBLANK(L2)`: L2 셀이 비어있는지 확인
- 비어있으면 `""` (빈 문자열) 반환
- 안 비어있으면 VLOOKUP 실행
- **목적**: ID가 없을 때 #N/A 오류 방지

---

## 📝 구현 방법

### 1. 컬럼 삽입

**API 요청 구조**:
```python
{
    'insertDimension': {
        'range': {
            'sheetId': sheet_id,
            'dimension': 'COLUMNS',
            'startIndex': col_index,  # 삽입할 위치
            'endIndex': col_index + 1
        },
        'inheritFromBefore': False  # 오른쪽 컬럼 스타일 상속
    }
}
```

**실제 적용 예시**:
```python
def insert_column(sheet_id, col_index):
    """컬럼 삽입"""
    return {
        'insertDimension': {
            'range': {
                'sheetId': sheet_id,
                'dimension': 'COLUMNS',
                'startIndex': col_index,
                'endIndex': col_index + 1
            },
            'inheritFromBefore': False
        }
    }

# M열 삽입 (L열 다음, 0-based로 12번 인덱스)
insert_column(sheet_id, 12)
```

---

### 2. 헤더 추가

```python
def add_header(sheet_id, col_index, header_text):
    """헤더 텍스트 추가"""
    col_letter = number_to_column(col_index)
    return {
        'updateCells': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': 0,
                'endRowIndex': 1,
                'startColumnIndex': col_index,
                'endColumnIndex': col_index + 1
            },
            'rows': [{
                'values': [{
                    'userEnteredValue': {
                        'stringValue': header_text
                    },
                    'userEnteredFormat': {
                        'textFormat': {
                            'bold': True
                        },
                        'horizontalAlignment': 'CENTER'
                    }
                }]
            }],
            'fields': 'userEnteredValue,userEnteredFormat'
        }
    }
```

---

### 3. VLOOKUP 수식 적용

**방법 1: repeatCell (권장)**

```python
def apply_vlookup_formula(sheet_id, col_index, formula):
    """VLOOKUP 수식을 컬럼 전체에 적용"""
    return {
        'repeatCell': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': 1,      # 2행부터
                'endRowIndex': 1000,
                'startColumnIndex': col_index,
                'endColumnIndex': col_index + 1
            },
            'cell': {
                'userEnteredValue': {
                    'formulaValue': formula
                }
            },
            'fields': 'userEnteredValue.formulaValue'
        }
    }
```

**방법 2: updateCells (범위 지정)**

```python
def apply_formula_range(sheet_id, start_row, end_row, col_index, formula_template):
    """특정 범위에 수식 적용"""
    rows = []
    for row in range(start_row, end_row + 1):
        # 수식에서 행 번호만 변경
        formula = formula_template.replace('{row}', str(row))
        rows.append({
            'values': [{
                'userEnteredValue': {
                    'formulaValue': formula
                }
            }]
        })
    
    return {
        'updateCells': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': start_row - 1,
                'endRowIndex': end_row,
                'startColumnIndex': col_index,
                'endColumnIndex': col_index + 1
            },
            'rows': rows,
            'fields': 'userEnteredValue.formulaValue'
        }
    }
```

---

## 🎨 실전 적용: 5개 컬럼 추가 전체 과정

### 전체 스크립트

```python
def add_vlookup_columns_to_sheet1(service, sheet_id):
    """시트1에 5개 VLOOKUP 컬럼 추가"""
    
    # 추가할 컬럼 정의
    columns_to_add = [
        {
            'insert_after': 11,  # L열 다음 (0-based로 11)
            'header': '담당소장명',
            'formula': '=IF(ISBLANK(L{row}),"",IFERROR(VLOOKUP(L{row},시트2!A:B,2,FALSE),""))'
        },
        {
            'insert_after': 12,  # 방금 추가한 M열 다음
            'header': '담당소장연락처',
            'formula': '=IF(ISBLANK(L{row}),"",IFERROR(VLOOKUP(L{row},시트2!A:E,5,FALSE),""))'
        },
        {
            'insert_after': 16,  # P열 다음 (원래 15였지만 2개 추가되어 17)
            'header': '자격증명',
            'formula': '=IF(ISBLANK(P{row}),"",IFERROR(VLOOKUP(P{row},시트3!A:B,2,FALSE),""))'
        },
        {
            'insert_after': 17,
            'header': '자격증소유자명',
            'formula': '=IF(ISBLANK(P{row}),"",IFERROR(VLOOKUP(P{row},시트3!A:E,5,FALSE),""))'
        },
        {
            'insert_after': 18,
            'header': '자격증소유자연락처',
            'formula': '=IF(ISBLANK(P{row}),"",IFERROR(VLOOKUP(P{row},시트3!A:F,6,FALSE),""))'
        }
    ]
    
    requests = []
    
    # 컬럼을 역순으로 삽입 (인덱스 변경 방지)
    for col_info in reversed(columns_to_add):
        # 1. 컬럼 삽입
        col_index = col_info['insert_after'] + 1
        requests.append(insert_column(sheet_id, col_index))
        
        # 2. 헤더 추가
        requests.append(add_header(sheet_id, col_index, col_info['header']))
        
        # 3. 수식 적용
        requests.append(apply_vlookup_formula(
            sheet_id, 
            col_index, 
            col_info['formula'].replace('{row}', '2')  # 2행부터
        ))
    
    # 일괄 실행
    body = {'requests': requests}
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body=body
    ).execute()
    
    return len(requests)
```

---

### 단계별 실행 (안전 버전)

```python
def add_vlookup_columns_step_by_step(service, sheet_id):
    """단계별로 컬럼 추가 (디버깅 용이)"""
    
    print("1단계: 담당소장명 컬럼 추가...")
    # M열에 담당소장명 추가
    requests = []
    requests.append(insert_column(sheet_id, 12))
    requests.append(add_header(sheet_id, 12, '담당소장명'))
    requests.append(apply_vlookup_formula(
        sheet_id, 12,
        '=IF(ISBLANK(L2),"",IFERROR(VLOOKUP(L2,시트2!A:B,2,FALSE),""))'
    ))
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'requests': requests}
    ).execute()
    print("   ✅ 완료")
    
    print("2단계: 담당소장연락처 컬럼 추가...")
    # N열에 담당소장연락처 추가
    requests = []
    requests.append(insert_column(sheet_id, 13))
    requests.append(add_header(sheet_id, 13, '담당소장연락처'))
    requests.append(apply_vlookup_formula(
        sheet_id, 13,
        '=IF(ISBLANK(L2),"",IFERROR(VLOOKUP(L2,시트2!A:E,5,FALSE),""))'
    ))
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'requests': requests}
    ).execute()
    print("   ✅ 완료")
    
    # 나머지 3개 컬럼도 동일하게...
    print("\n모든 컬럼 추가 완료! ✅")
```

---

## 🧪 테스트 방법

### 1. 자동 조회 테스트
```
1. 시트1에서 L열 (담당소장ID)에 "P001" 입력
2. M열 (담당소장명)에 "김현장" 자동 표시 확인 ✅
3. N열 (담당소장연락처)에 "010-1234-5678" 자동 표시 확인 ✅
```

### 2. 오류 처리 테스트
```
1. 존재하지 않는 ID 입력 (예: "P999")
2. 빈 문자열 ("") 표시 확인 (오류 아님) ✅
3. #N/A 오류가 안 보이면 성공 ✅
```

### 3. 빈 셀 테스트
```
1. L열을 비워둠 (삭제)
2. M열, N열도 자동으로 비워짐 확인 ✅
3. 오류 메시지 없음 확인 ✅
```

---

## 🎯 VLOOKUP 최적화 팁

### 1. IFERROR 추가
```excel
=IF(ISBLANK(L2),"",IFERROR(VLOOKUP(L2,시트2!A:B,2,FALSE),""))
```
- VLOOKUP 오류 시 빈 문자열 반환
- 더 안전한 수식

### 2. 범위 최소화
```excel
# 나쁜 예: 전체 컬럼
=VLOOKUP(L2,시트2!A:Z,2,FALSE)

# 좋은 예: 필요한 컬럼만
=VLOOKUP(L2,시트2!A:E,2,FALSE)
```
- 검색 속도 향상
- 메모리 사용 감소

### 3. 절대 참조 사용
```excel
=IF(ISBLANK(L2),"",VLOOKUP(L2,시트2!$A:$E,5,FALSE))
```
- `$` 기호로 범위 고정
- 수식 복사 시 범위 변경 방지

---

## 🔍 고급 기능

### 1. INDEX-MATCH (VLOOKUP 대체)

**장점**: 왼쪽 열도 조회 가능, 더 빠름

```excel
=IF(ISBLANK(L2),"",IFERROR(INDEX(시트2!B:B,MATCH(L2,시트2!A:A,0)),""))
```

### 2. 다중 조건 조회

```excel
# 회사구분 + 현장ID로 조회
=IF(ISBLANK(L2),"",VLOOKUP(C2&L2,시트2!A:E,5,FALSE))
```

**주의**: 시트2의 A열도 결합된 값이어야 함

### 3. 조건부 VLOOKUP

```excel
# 배정완료인 경우만 조회
=IF(O2="배정완료",VLOOKUP(L2,시트2!A:B,2,FALSE),"")
```

---

## 📋 완성된 시트1 구조

### Before (원래 구조)
```
A: 현장ID
B: 현장명
C: 회사구분
...
L: 담당소장ID
M: 특이사항
N: 사용자격증ID
O: 준공필증파일URL
P: 배정상태
Q: 등록일
R: 수정일
```

### After (VLOOKUP 추가 후)
```
A: 현장ID
B: 현장명
C: 회사구분
...
L: 담당소장ID
M: 담당소장명 ⭐ (새로 추가)
N: 담당소장연락처 ⭐ (새로 추가)
O: 특이사항
P: 사용자격증ID
Q: 자격증명 ⭐ (새로 추가)
R: 자격증소유자명 ⭐ (새로 추가)
S: 자격증소유자연락처 ⭐ (새로 추가)
T: 준공필증파일URL
U: 배정상태
V: 등록일
W: 수정일
```

---

## 🐛 트러블슈팅

### 문제 1: #N/A 오류 표시
**원인**: ID가 시트2/시트3에 없음  
**해결**: IFERROR로 감싸기
```excel
=IFERROR(VLOOKUP(...),"")
```

### 문제 2: 수식이 텍스트로 표시
**원인**: 셀 형식이 "텍스트"로 설정됨  
**해결**: 
1. 셀 선택
2. 서식 → 숫자 → 자동
3. F2 키 누르고 Enter (수식 재입력)

### 문제 3: 잘못된 값 반환
**원인**: 열 번호 오류  
**해결**: 
- 시트2의 A열부터 세어서 정확한 열 번호 확인
- A=1, B=2, C=3, D=4, E=5

### 문제 4: 컬럼 삽입 후 기존 수식 깨짐
**원인**: 상대 참조 문제  
**해결**: 
- 절대 참조 사용 (`$A:$E`)
- 컬럼을 역순으로 삽입

---

## 📊 실행 결과 예시

```
====================================================================
📋 VLOOKUP 수식 자동화 - 시작
====================================================================

🔍 시트1 (현장정보) 분석 중...
   현재 컬럼 수: 17개

📝 5개 VLOOKUP 컬럼 추가 예정:
   1. M열: 담당소장명
   2. N열: 담당소장연락처
   3. R열: 자격증명
   4. S열: 자격증소유자명
   5. T열: 자격증소유자연락처

🚀 컬럼 추가 및 수식 적용 중...

✅ 1/5 완료: 담당소장명
✅ 2/5 완료: 담당소장연락처
✅ 3/5 완료: 자격증명
✅ 4/5 완료: 자격증소유자명
✅ 5/5 완료: 자격증소유자연락처

====================================================================
🎉 VLOOKUP 수식 자동화 완료!
====================================================================

📊 결과:
   - 추가된 컬럼: 5개
   - 적용된 수식: 5,000개 (5컬럼 × 1,000행)
   - 최종 컬럼 수: 22개

🔍 테스트 방법:
   1. 시트1의 L열에 소장ID 입력 (예: P001)
   2. M열과 N열에 자동으로 정보 표시 확인
   3. P열에 자격증ID 입력 (예: C001)
   4. R, S, T열에 자동으로 정보 표시 확인

====================================================================
✨ 이제 ID만 입력하면 모든 정보가 자동으로 표시됩니다!
====================================================================
```

---

## 🎯 체크리스트

실행 전:
- [ ] 시트2, 시트3에 데이터 있음 확인
- [ ] 시트1에 담당소장ID, 사용자격증ID 있음 확인
- [ ] 기존 시트1 백업 완료

실행 후:
- [ ] 5개 컬럼 모두 추가됨
- [ ] 헤더 텍스트 확인
- [ ] VLOOKUP 수식 정상 작동
- [ ] 오류 메시지 없음 (#N/A, #REF! 등)
- [ ] 기존 데이터 영향 없음

---

## 💡 활용 시나리오

### 시나리오 1: 신규 현장 등록
```
1. 새 행 추가
2. 현장ID, 현장명 등 기본 정보 입력
3. 담당소장ID만 입력 (예: P005)
4. 소장명, 연락처 자동 표시 ✅
5. 자격증ID만 입력 (예: C012)
6. 자격증 정보 자동 표시 ✅
```

### 시나리오 2: 소장 교체
```
1. 담당소장ID 변경 (P001 → P003)
2. 모든 관련 정보 자동 업데이트 ✅
3. 자격증ID도 함께 변경
4. 자격증 정보도 자동 업데이트 ✅
```

### 시나리오 3: 데이터 일관성 체크
```
1. 시트2에서 소장 연락처 변경
2. 시트1의 모든 해당 현장 자동 업데이트 ✅
3. 일일이 수정할 필요 없음
4. 데이터 정합성 100% 유지 ✅
```

---

**완료 시간**: 약 1시간  
**난이도**: ⭐⭐⭐☆☆  
**다음 단계**: Flask API 서버 개발
