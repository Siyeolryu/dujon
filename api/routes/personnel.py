"""
인력 관련 API 라우트 (GET / PUT)
"""
from datetime import datetime
from flask import Blueprint, jsonify, request
from api.services.db_service import get_db

bp = Blueprint('personnel', __name__)


@bp.route('/personnel', methods=['GET'])
def get_personnel():
    """인력 목록 조회. 쿼리: status, role"""
    try:
        db = get_db()
        personnel = db.get_all_personnel()

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
        db = get_db()
        person = db.get_personnel_by_id(personnel_id)
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
    """인력 정보 수정"""
    try:
        db = get_db()
        person = db.get_personnel_by_id(personnel_id)
        if not person:
            return jsonify({
                'success': False,
                'error': {'code': 'PERSONNEL_NOT_FOUND', 'message': f'인력ID {personnel_id}를 찾을 수 없습니다'},
            }), 404

        data = request.json or {}
        allowed = {'성명', '직책', '소속', '연락처', '이메일', '보유자격증', '현재상태', '현재담당현장수', '비고', '입사일', '등록일'}
        update_data = {k: v for k, v in data.items() if k in allowed}
        if update_data:
            db.update_personnel(personnel_id, update_data)

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
