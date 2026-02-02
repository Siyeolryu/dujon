"""
자격증 관련 API 라우트 (GET / POST / PUT)
"""
import uuid
from datetime import datetime
from flask import Blueprint, jsonify, request
from api.services.sheets_service import sheets_service, SHEET_CERTIFICATES
from api.services.validation import validate_certificate_data, ValidationError

bp = Blueprint('certificates', __name__)


def _generate_cert_id():
    """자격증ID 자동 부여 (중복 방지)"""
    ts = datetime.now().strftime('%Y%m%d%H%M%S')
    short = uuid.uuid4().hex[:6].upper()
    return f'CERT-{ts}-{short}'


def _generate_owner_id():
    """소유자ID 자동 부여"""
    ts = datetime.now().strftime('%Y%m%d%H%M%S')
    short = uuid.uuid4().hex[:4].upper()
    return f'O-{ts}-{short}'


@bp.route('/certificates', methods=['POST'])
def create_certificate():
    """자격증 등록 (Google Sheets 자격증풀 시트에 저장, 자격증ID·소유자ID 자동 부여)"""
    try:
        data = request.json or {}
        try:
            validate_certificate_data(data, is_update=False)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': {'code': 'VALIDATION_ERROR', 'message': str(e)},
            }), 400

        required = ['자격증명', '소유자명']
        for field in required:
            if field not in data or not str(data.get(field, '')).strip():
                return jsonify({
                    'success': False,
                    'error': {'code': 'MISSING_FIELD', 'message': f'{field}는 필수 입력 항목입니다'},
                }), 400

        cert_id = _generate_cert_id()
        owner_id = _generate_owner_id()
        while sheets_service.get_certificate_by_id(cert_id):
            cert_id = _generate_cert_id()

        now = datetime.now().strftime('%Y-%m-%d')
        row_data = [
            cert_id,
            data['자격증명'].strip(),
            data.get('자격증번호', ''),
            owner_id,
            data['소유자명'].strip(),
            data.get('소유자연락처', ''),
            data.get('발급기관', ''),
            data.get('취득일', ''),
            data.get('유효기간', ''),
            data.get('사용가능여부', '사용가능'),
            data.get('현재사용현장ID', ''),
            data.get('비고', ''),
            now,
        ]
        sheets_service.append_row(SHEET_CERTIFICATES, row_data)

        return jsonify({
            'success': True,
            'data': {'자격증ID': cert_id, '자격증명': data['자격증명'], '소유자ID': owner_id},
            'message': '자격증이 등록되었습니다',
            'timestamp': datetime.now().isoformat(),
        }), 201
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'CONFIG_REQUIRED', 'message': str(e)},
        }), 503
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'CREATE_ERROR', 'message': str(e)},
        }), 500


@bp.route('/certificates', methods=['GET'])
def get_certificates():
    """자격증 목록 조회. 쿼리: available (true/false)"""
    try:
        certificates = sheets_service.get_all_certificates()

        available = request.args.get('available')
        if available == 'true':
            certificates = [c for c in certificates if c['사용가능여부'] == '사용가능']
        elif available == 'false':
            certificates = [c for c in certificates if c['사용가능여부'] != '사용가능']

        return jsonify({
            'success': True,
            'data': certificates,
            'count': len(certificates),
            'timestamp': datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'FETCH_ERROR', 'message': str(e)},
        }), 500


@bp.route('/certificates/<cert_id>', methods=['GET'])
def get_certificate_detail(cert_id):
    """자격증 상세 조회"""
    try:
        cert = sheets_service.get_certificate_by_id(cert_id)
        if not cert:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'CERTIFICATE_NOT_FOUND',
                    'message': f'자격증ID {cert_id}를 찾을 수 없습니다',
                },
            }), 404

        return jsonify({
            'success': True,
            'data': cert,
            'timestamp': datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'FETCH_ERROR', 'message': str(e)},
        }), 500


@bp.route('/certificates/<cert_id>', methods=['PUT'])
def update_certificate(cert_id):
    """자격증 정보 수정 (Google Sheets 자격증풀 시트: A~M)"""
    try:
        cert = sheets_service.get_certificate_by_id(cert_id)
        if not cert:
            return jsonify({
                'success': False,
                'error': {'code': 'CERTIFICATE_NOT_FOUND', 'message': f'자격증ID {cert_id}를 찾을 수 없습니다'},
            }), 404

        row_num = sheets_service.find_row_by_id(SHEET_CERTIFICATES, cert_id)
        if not row_num:
            return jsonify({
                'success': False,
                'error': {'code': 'ROW_NOT_FOUND', 'message': '행을 찾을 수 없습니다'},
            }), 404

        data = request.json or {}
        try:
            validate_certificate_data(data, is_update=True)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': {'code': 'VALIDATION_ERROR', 'message': str(e)},
            }), 400

        column_map = {
            '자격증명': 'B', '자격증번호': 'C', '소유자ID': 'D', '소유자명': 'E', '소유자연락처': 'F',
            '발급기관': 'G', '취득일': 'H', '유효기간': 'I', '사용가능여부': 'J',
            '현재사용현장ID': 'K', '비고': 'L', '등록일': 'M',
        }
        updates = []
        for field, col in column_map.items():
            if field in data:
                updates.append({'range': f'{SHEET_CERTIFICATES}!{col}{row_num}', 'values': [[data[field]]]})

        if updates:
            sheets_service.batch_update(updates)

        return jsonify({
            'success': True,
            'data': {'자격증ID': cert_id, 'updated_fields': list(data.keys())},
            'message': '자격증 정보가 수정되었습니다',
            'timestamp': datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'UPDATE_ERROR', 'message': str(e)},
        }), 500
