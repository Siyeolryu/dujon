"""
인력 관련 API 라우트 (GET)
"""
from datetime import datetime
from flask import Blueprint, jsonify, request
from api.services.sheets_service import sheets_service, SHEET_PERSONNEL

bp = Blueprint('personnel', __name__)


@bp.route('/personnel', methods=['GET'])
def get_personnel():
    """인력 목록 조회. 쿼리: status, role"""
    try:
        personnel = sheets_service.get_all_personnel()

        status = request.args.get('status')
        role = request.args.get('role')

        if status:
            personnel = [p for p in personnel if p['현재상태'] == status]
        if role:
            personnel = [p for p in personnel if p['직책'] == role]

        return jsonify({
            'success': True,
            'data': personnel,
            'count': len(personnel),
            'timestamp': datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'FETCH_ERROR', 'message': str(e)},
        }), 500


@bp.route('/personnel/<personnel_id>', methods=['GET'])
def get_personnel_detail(personnel_id):
    """인력 상세 조회"""
    try:
        person = sheets_service.get_personnel_by_id(personnel_id)
        if not person:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PERSONNEL_NOT_FOUND',
                    'message': f'인력ID {personnel_id}를 찾을 수 없습니다',
                },
            }), 404

        return jsonify({
            'success': True,
            'data': person,
            'timestamp': datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'FETCH_ERROR', 'message': str(e)},
        }), 500


@bp.route('/personnel/<personnel_id>', methods=['PUT'])
def update_personnel(personnel_id):
    """인력 정보 수정 (시트2: A~L)"""
    try:
        person = sheets_service.get_personnel_by_id(personnel_id)
        if not person:
            return jsonify({
                'success': False,
                'error': {'code': 'PERSONNEL_NOT_FOUND', 'message': f'인력ID {personnel_id}를 찾을 수 없습니다'},
            }), 404

        row_num = sheets_service.find_row_by_id(SHEET_PERSONNEL, personnel_id)
        if not row_num:
            return jsonify({
                'success': False,
                'error': {'code': 'ROW_NOT_FOUND', 'message': '행을 찾을 수 없습니다'},
            }), 404

        data = request.json or {}
        column_map = {
            '성명': 'B', '직책': 'C', '소속': 'D', '연락처': 'E', '이메일': 'F',
            '보유자격증': 'G', '현재상태': 'H', '현재담당현장수': 'I', '비고': 'J',
            '입사일': 'K', '등록일': 'L',
        }
        updates = []
        for field, col in column_map.items():
            if field in data:
                updates.append({'range': f'{SHEET_PERSONNEL}!{col}{row_num}', 'values': [[data[field]]]})

        if updates:
            sheets_service.batch_update(updates)

        return jsonify({
            'success': True,
            'data': {'인력ID': personnel_id, 'updated_fields': list(data.keys())},
            'message': '인력 정보가 수정되었습니다',
            'timestamp': datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'UPDATE_ERROR', 'message': str(e)},
        }), 500
