"""
폼 검증 유틸리티 모듈
실시간 필드 검증 및 에러 메시지 생성
"""
import re
from typing import Tuple, Optional
from datetime import datetime, date


def validate_required(value: Optional[str], field_name: str) -> Tuple[bool, str]:
    """
    필수 필드 검증
    
    Args:
        value: 검증할 값
        field_name: 필드 이름 (에러 메시지용)
    
    Returns:
        (is_valid, error_message)
    """
    if not value or not value.strip():
        return False, f"{field_name}을(를) 입력해주세요."
    return True, ""


def validate_phone(phone: Optional[str]) -> Tuple[bool, str]:
    """
    전화번호 형식 검증 (010-XXXX-XXXX)
    
    Args:
        phone: 전화번호
    
    Returns:
        (is_valid, error_message)
    """
    if not phone or not phone.strip():
        return True, ""  # 선택 필드인 경우
    
    # 010-XXXX-XXXX 형식 검증
    pattern = r'^010-\d{4}-\d{4}$'
    if not re.match(pattern, phone.strip()):
        return False, "전화번호는 010-XXXX-XXXX 형식으로 입력해주세요. (예: 010-1234-5678)"
    
    return True, ""


def validate_text_length(
    text: Optional[str], 
    min_len: int = 0, 
    max_len: int = 1000,
    field_name: str = "입력값"
) -> Tuple[bool, str]:
    """
    텍스트 길이 검증
    
    Args:
        text: 검증할 텍스트
        min_len: 최소 길이
        max_len: 최대 길이
        field_name: 필드 이름
    
    Returns:
        (is_valid, error_message)
    """
    if not text:
        text = ""
    
    text_len = len(text.strip())
    
    if text_len < min_len:
        return False, f"{field_name}은(는) 최소 {min_len}자 이상 입력해주세요. (현재: {text_len}자)"
    
    if text_len > max_len:
        return False, f"{field_name}은(는) 최대 {max_len}자까지 입력 가능합니다. (현재: {text_len}자)"
    
    return True, ""


def validate_korean_name(name: Optional[str]) -> Tuple[bool, str]:
    """
    한글 이름 검증 (2-10자)
    
    Args:
        name: 이름
    
    Returns:
        (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "이름을 입력해주세요."
    
    name = name.strip()
    
    # 한글만 허용 (공백 제외)
    if not re.match(r'^[가-힣]+$', name):
        return False, "이름은 한글만 입력 가능합니다."
    
    # 길이 검증 (2-10자)
    if len(name) < 2:
        return False, "이름은 최소 2자 이상 입력해주세요."
    
    if len(name) > 10:
        return False, "이름은 최대 10자까지 입력 가능합니다."
    
    return True, ""


def validate_date_range(
    start_date: Optional[date], 
    end_date: Optional[date],
    start_label: str = "시작일",
    end_label: str = "종료일"
) -> Tuple[bool, str]:
    """
    날짜 범위 검증 (시작일 < 종료일)
    
    Args:
        start_date: 시작 날짜
        end_date: 종료 날짜
        start_label: 시작일 라벨
        end_label: 종료일 라벨
    
    Returns:
        (is_valid, error_message)
    """
    # 둘 다 없으면 검증 통과
    if not start_date and not end_date:
        return True, ""
    
    # 하나만 있으면 검증 통과
    if not start_date or not end_date:
        return True, ""
    
    # 시작일이 종료일보다 늦으면 에러
    if start_date > end_date:
        return False, f"{start_label}은(는) {end_label}보다 이전이어야 합니다."
    
    return True, ""


def validate_alphanumeric(
    value: Optional[str],
    field_name: str = "입력값",
    allow_hyphen: bool = True
) -> Tuple[bool, str]:
    """
    영숫자 검증 (자격증 번호 등)
    
    Args:
        value: 검증할 값
        field_name: 필드 이름
        allow_hyphen: 하이픈(-) 허용 여부
    
    Returns:
        (is_valid, error_message)
    """
    if not value or not value.strip():
        return True, ""  # 선택 필드
    
    value = value.strip()
    
    if allow_hyphen:
        pattern = r'^[A-Za-z0-9\-]+$'
        error_msg = f"{field_name}은(는) 영문, 숫자, 하이픈(-)만 입력 가능합니다."
    else:
        pattern = r'^[A-Za-z0-9]+$'
        error_msg = f"{field_name}은(는) 영문, 숫자만 입력 가능합니다."
    
    if not re.match(pattern, value):
        return False, error_msg
    
    return True, ""


def validate_address(address: Optional[str]) -> Tuple[bool, str]:
    """
    주소 검증
    
    Args:
        address: 주소
    
    Returns:
        (is_valid, error_message)
    """
    if not address or not address.strip():
        return False, "주소를 입력해주세요."
    
    address = address.strip()
    
    # 최소 길이 검증 (10자)
    if len(address) < 10:
        return False, "주소는 최소 10자 이상 입력해주세요. (예: 서울특별시 강남구 테헤란로 123)"
    
    return True, ""


def validate_site_name(name: Optional[str]) -> Tuple[bool, str]:
    """
    현장명 검증
    
    Args:
        name: 현장명
    
    Returns:
        (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "현장명을 입력해주세요."
    
    name = name.strip()
    
    # 길이 검증 (2-50자)
    if len(name) < 2:
        return False, "현장명은 최소 2자 이상 입력해주세요."
    
    if len(name) > 50:
        return False, "현장명은 최대 50자까지 입력 가능합니다."
    
    return True, ""


def validate_form_data(data: dict, rules: dict) -> Tuple[bool, dict]:
    """
    폼 데이터 일괄 검증
    
    Args:
        data: 검증할 데이터 딕셔너리
        rules: 검증 규칙 딕셔너리
            예: {
                'name': ('required', 'korean_name'),
                'phone': ('phone',),
                'address': ('required', 'address')
            }
    
    Returns:
        (is_valid, errors) - errors는 {field: error_message} 형태
    """
    errors = {}
    
    for field, field_rules in rules.items():
        value = data.get(field)
        
        for rule in field_rules:
            is_valid = True
            error_msg = ""
            
            if rule == 'required':
                is_valid, error_msg = validate_required(value, field)
            elif rule == 'phone':
                is_valid, error_msg = validate_phone(value)
            elif rule == 'korean_name':
                is_valid, error_msg = validate_korean_name(value)
            elif rule == 'address':
                is_valid, error_msg = validate_address(value)
            elif rule == 'site_name':
                is_valid, error_msg = validate_site_name(value)
            
            if not is_valid:
                errors[field] = error_msg
                break  # 첫 번째 에러만 표시
    
    return len(errors) == 0, errors


def format_validation_message(is_valid: bool, message: str) -> str:
    """
    검증 메시지 포맷팅 (이모지 추가)
    
    Args:
        is_valid: 검증 결과
        message: 메시지
    
    Returns:
        포맷팅된 메시지
    """
    if is_valid:
        return f"✅ {message}" if message else ""
    else:
        return f"❌ {message}" if message else ""
