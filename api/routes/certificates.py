"""
자격증 관련 API 라우트 (GET)
"""
from datetime import datetime
from flask import Blueprint, jsonify, request
from api.services.sheets_service import sheets_service

bp = Blueprint('certificates', __name__)


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
    """자격증 정보 수정 (시트3: A~M)"""
    try:
        cert = sheets_service.get_certificate_by_id(cert_id)
        if not cert:
            return jsonify({
                'success': False,
                'error': {'code': 'CERTIFICATE_NOT_FOUND', 'message': f'자격증ID {cert_id}를 찾을 수 없습니다'},
            }), 404

        row_num = sheets_service.find_row_by_id('시트3', cert_id)
        if not row_num:
            return jsonify({
                'success': False,
                'error': {'code': 'ROW_NOT_FOUND', 'message': '행을 찾을 수 없습니다'},
            }), 404

        data = request.json or {}
        column_map = {
            '자격증명': 'B', '자격증번호': 'C', '소유자ID': 'D', '소유자명': 'E', '소유자연락처': 'F',
            '발급기관': 'G', '취득일': 'H', '유효기간': 'I', '사용가능여부': 'J',
            '현재사용현장ID': 'K', '비고': 'L', '등록일': 'M',
        }
        updates = []
        for field, col in column_map.items():
            if field in data:
                updates.append({'range': f'시트3!{col}{row_num}', 'values': [[data[field]]]})

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
