"""
데이터 검증 로직 (2-2)
"""
from datetime import datetime


class ValidationError(Exception):
    """검증 오류"""
    pass


def validate_site_data(data, is_update=False):
    """현장 데이터 검증"""
    errors = []

    if not is_update:
        required = ['현장ID', '현장명', '회사구분', '주소']
        for field in required:
            if field not in data or not str(data.get(field, '')).strip():
                errors.append(f'{field}는 필수 입력 항목입니다')

    if '회사구분' in data and data['회사구분']:
        if data['회사구분'] not in ('더존종합건설', '더존하우징'):
            errors.append('회사구분은 "더존종합건설" 또는 "더존하우징"이어야 합니다')

    if '현장상태' in data and data['현장상태']:
        valid = ('건축허가', '착공예정', '착공중', '준공')
        if data['현장상태'] not in valid:
            errors.append(f'현장상태는 {", ".join(valid)} 중 하나여야 합니다')

    if '배정상태' in data and data['배정상태']:
        if data['배정상태'] not in ('배정완료', '미배정'):
            errors.append('배정상태는 "배정완료" 또는 "미배정"이어야 합니다')

    for field in ('건축허가일', '착공예정일', '준공일'):
        if field in data and data.get(field):
            try:
                datetime.strptime(str(data[field]).strip()[:10], '%Y-%m-%d')
            except ValueError:
                errors.append(f'{field}는 YYYY-MM-DD 형식이어야 합니다')

    if errors:
        raise ValidationError('; '.join(errors))
    return True


def validate_certificate_data(data, is_update=False):
    """자격증 데이터 검증 (Google Sheets 자격증풀 저장용)"""
    errors = []

    if not is_update:
        required = ['자격증명', '소유자명']
        for field in required:
            if field not in data or not str(data.get(field, '')).strip():
                errors.append(f'{field}는 필수 입력 항목입니다')

    if '사용가능여부' in data and data['사용가능여부']:
        if data['사용가능여부'] not in ('사용가능', '사용중'):
            errors.append('사용가능여부는 "사용가능" 또는 "사용중"이어야 합니다')

    for field in ('취득일', '유효기간'):
        if field in data and data.get(field):
            try:
                datetime.strptime(str(data[field]).strip()[:10], '%Y-%m-%d')
            except ValueError:
                errors.append(f'{field}는 YYYY-MM-DD 형식이어야 합니다')

    if errors:
        raise ValidationError('; '.join(errors))
    return True


def validate_assignment(site, manager, certificate):
    """배정 가능 여부 검증"""
    errors = []

    if site.get('배정상태') == '배정완료':
        errors.append('이미 소장이 배정된 현장입니다')

    if manager.get('현재상태') == '퇴사':
        errors.append('퇴사한 소장은 배정할 수 없습니다')

    if manager.get('현재상태') == '휴가':
        errors.append('휴가중인 소장은 배정할 수 없습니다')

    if certificate.get('사용가능여부') != '사용가능':
        errors.append(f"자격증이 '{certificate.get('사용가능여부', '')}' 상태입니다")

    if errors:
        raise ValidationError('; '.join(errors))
    return True
