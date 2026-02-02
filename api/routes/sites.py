"""
현장 관련 API 라우트 (GET / POST / PUT)
"""
import uuid
from datetime import datetime
from flask import Blueprint, jsonify, request
from api.services.sheets_service import (
    sheets_service,
    SHEET_SITES,
    SHEET_PERSONNEL,
    SHEET_CERTIFICATES,
)
from api.services.validation import validate_site_data, validate_assignment, ValidationError
from api.services.sync_manager import get_sync_manager, ConflictError

bp = Blueprint('sites', __name__)


def _generate_site_id():
    """현장ID 자동 부여 (중복 방지)"""
    ts = datetime.now().strftime('%Y%m%d%H%M%S')
    short = uuid.uuid4().hex[:6].upper()
    return f'SITE-{ts}-{short}'


@bp.route('/sites', methods=['GET'])
def get_sites():
    """현장 목록 조회. 쿼리: company, status, state"""
    try:
        sites = sheets_service.get_all_sites()

        company = request.args.get('company')
        status = request.args.get('status')
        state = request.args.get('state')

        if company:
            sites = [s for s in sites if s['회사구분'] == company]
        if status:
            sites = [s for s in sites if s['배정상태'] == status]
        if state:
            sites = [s for s in sites if s['현장상태'] == state]

        return jsonify({
            'success': True,
            'data': sites,
            'count': len(sites),
            'timestamp': datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'FETCH_ERROR', 'message': str(e)},
        }), 500


@bp.route('/sites/search', methods=['GET'])
def search_sites():
    """현장 검색. 쿼리: q (현장명 또는 주소)"""
    try:
        query = (request.args.get('q') or '').strip().lower()
        if not query:
            return jsonify({
                'success': False,
                'error': {'code': 'INVALID_QUERY', 'message': '검색어를 입력해주세요 (q=)'},
            }), 400

        sites = sheets_service.get_all_sites()
        results = [
            s for s in sites
            if query in (s.get('현장명') or '').lower() or query in (s.get('주소') or '').lower()
        ]
        return jsonify({
            'success': True,
            'data': results,
            'count': len(results),
            'query': query,
            'timestamp': datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'SEARCH_ERROR', 'message': str(e)},
        }), 500


@bp.route('/sites/<site_id>', methods=['GET'])
def get_site_detail(site_id):
    """현장 상세 조회 (관계 데이터 포함)"""
    try:
        site = sheets_service.get_site_by_id(site_id)
        if not site:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SITE_NOT_FOUND',
                    'message': f'현장ID {site_id}를 찾을 수 없습니다',
                },
            }), 404

        site = dict(site)
        # 2-3: 낙관적 잠금용 버전(수정일). 수정/배정 시 If-Match 또는 body.version으로 전달
        site['version'] = site.get('수정일') or ''
        if site.get('담당소장ID'):
            site['manager'] = {
                'id': site['담당소장ID'],
                'name': site.get('담당소장명') or '',
                'phone': site.get('담당소장연락처') or '',
            }
        if site.get('사용자격증ID'):
            site['certificate'] = {
                'id': site['사용자격증ID'],
                'name': site.get('자격증명') or '',
                'owner': site.get('자격증소유자명') or '',
                'phone': site.get('자격증소유자연락처') or '',
            }

        return jsonify({
            'success': True,
            'data': site,
            'timestamp': datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'FETCH_ERROR', 'message': str(e)},
        }), 500


# ---------- 2-2 데이터 수정 API ----------

@bp.route('/sites', methods=['POST'])
def create_site():
    """현장 생성"""
    try:
        data = request.json or {}
        required = ['현장명', '회사구분', '주소']
        for field in required:
            if field not in data or not str(data.get(field, '')).strip():
                return jsonify({
                    'success': False,
                    'error': {'code': 'MISSING_FIELD', 'message': f'{field}는 필수 입력 항목입니다'},
                }), 400

        # 현장ID 미제공 시 자동 부여
        if not data.get('현장ID') or not str(data.get('현장ID', '')).strip():
            data['현장ID'] = _generate_site_id()
            while sheets_service.get_site_by_id(data['현장ID']):
                data['현장ID'] = _generate_site_id()

        try:
            validate_site_data(data, is_update=False)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': {'code': 'VALIDATION_ERROR', 'message': str(e)},
            }), 400

        if sheets_service.get_site_by_id(data['현장ID']):
            return jsonify({
                'success': False,
                'error': {'code': 'DUPLICATE_ID', 'message': f"현장ID {data['현장ID']}가 이미 존재합니다"},
            }), 400

        now = datetime.now().strftime('%Y-%m-%d')
        row_data = [
            data['현장ID'],
            data['현장명'],
            data.get('건축주명', ''),
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
            '',  # M 담당소장명 (VLOOKUP)
            '',  # N 담당소장연락처 (VLOOKUP)
            data.get('사용자격증ID', ''),
            '',  # P 자격증명 (VLOOKUP)
            '',  # Q 자격증소유자명 (VLOOKUP)
            '',  # R 자격증소유자연락처 (VLOOKUP)
            data.get('준공필증파일URL', ''),
            data.get('배정상태', '미배정'),
            now,
            now,
        ]
        sheets_service.append_row(SHEET_SITES, row_data)

        return jsonify({
            'success': True,
            'data': {'현장ID': data['현장ID'], '현장명': data['현장명']},
            'message': '현장이 생성되었습니다',
            'timestamp': datetime.now().isoformat(),
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'CREATE_ERROR', 'message': str(e)},
        }), 500


@bp.route('/sites/<site_id>', methods=['PUT'])
def update_site(site_id):
    """현장 정보 수정 (22컬럼 시트 기준). 2-3: If-Match 또는 body.version으로 버전 전달 시 충돌 검사"""
    try:
        site = sheets_service.get_site_by_id(site_id)
        if not site:
            return jsonify({
                'success': False,
                'error': {'code': 'SITE_NOT_FOUND', 'message': f'현장ID {site_id}를 찾을 수 없습니다'},
            }), 404

        row_num = sheets_service.find_row_by_id(SHEET_SITES, site_id)
        if not row_num:
            return jsonify({
                'success': False,
                'error': {'code': 'ROW_NOT_FOUND', 'message': '행을 찾을 수 없습니다'},
            }), 404

        data = request.json or {}
        # 2-3: 낙관적 잠금 - 버전 있으면 검사
        version = request.headers.get('If-Match') or data.get('version')
        try:
            get_sync_manager().require_site_version(site_id, version)
        except ConflictError as e:
            return jsonify({
                'success': False,
                'error': {'code': 'CONFLICT', 'message': str(e)},
            }), 409

        try:
            validate_site_data(data, is_update=True)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': {'code': 'VALIDATION_ERROR', 'message': str(e)},
            }), 400

        # 23컬럼 기준: A=현장ID, B=현장명, C=건축주명, D~W
        column_map = {
            '현장명': 'B', '건축주명': 'C', '회사구분': 'D', '주소': 'E', '위도': 'F', '경도': 'G',
            '건축허가일': 'H', '착공예정일': 'I', '준공일': 'J',
            '현장상태': 'K', '특이사항': 'L', '담당소장ID': 'M',
            '사용자격증ID': 'P', '준공필증파일URL': 'T', '배정상태': 'U',
        }
        updates = []
        for field, col in column_map.items():
            if field in data:
                val = data[field]
                updates.append({'range': f'{SHEET_SITES}!{col}{row_num}', 'values': [[val]]})

        now = datetime.now().strftime('%Y-%m-%d')
        updates.append({'range': f'{SHEET_SITES}!W{row_num}', 'values': [[now]]})

        if updates:
            sheets_service.batch_update(updates)

        return jsonify({
            'success': True,
            'data': {'현장ID': site_id, 'updated_fields': list(data.keys()), 'version': now},
            'message': '현장 정보가 수정되었습니다',
            'timestamp': datetime.now().isoformat(),
        })
    except ConflictError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'CONFLICT', 'message': str(e)},
        }), 409
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'UPDATE_ERROR', 'message': str(e)},
        }), 500


@bp.route('/sites/<site_id>/assign', methods=['POST'])
def assign_manager(site_id):
    """소장 배정. 2-3: If-Match 또는 body.version으로 버전 전달 시 충돌 검사"""
    try:
        site = sheets_service.get_site_by_id(site_id)
        if not site:
            return jsonify({
                'success': False,
                'error': {'code': 'SITE_NOT_FOUND', 'message': f'현장ID {site_id}를 찾을 수 없습니다'},
            }), 404

        data = request.json or {}
        manager_id = data.get('manager_id')
        certificate_id = data.get('certificate_id')

        if not manager_id or not certificate_id:
            return jsonify({
                'success': False,
                'error': {'code': 'MISSING_PARAMS', 'message': 'manager_id와 certificate_id가 필요합니다'},
            }), 400

        manager = sheets_service.get_personnel_by_id(manager_id)
        if not manager:
            return jsonify({
                'success': False,
                'error': {'code': 'MANAGER_NOT_FOUND', 'message': f'인력ID {manager_id}를 찾을 수 없습니다'},
            }), 404

        certificate = sheets_service.get_certificate_by_id(certificate_id)
        if not certificate:
            return jsonify({
                'success': False,
                'error': {'code': 'CERTIFICATE_NOT_FOUND', 'message': f'자격증ID {certificate_id}를 찾을 수 없습니다'},
            }), 404

        if certificate.get('사용가능여부') != '사용가능':
            return jsonify({
                'success': False,
                'error': {'code': 'CERTIFICATE_NOT_AVAILABLE', 'message': f'자격증 {certificate_id}는 사용할 수 없습니다'},
            }), 400

        try:
            validate_assignment(site, manager, certificate)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': {'code': 'VALIDATION_ERROR', 'message': str(e)},
            }), 400

        # 2-3: 낙관적 잠금
        data = request.json or {}
        version = request.headers.get('If-Match') or data.get('version')
        try:
            get_sync_manager().require_site_version(site_id, version)
        except ConflictError as e:
            return jsonify({
                'success': False,
                'error': {'code': 'CONFLICT', 'message': str(e)},
            }), 409

        site_row = sheets_service.find_row_by_id(SHEET_SITES, site_id)
        manager_row = sheets_service.find_row_by_id(SHEET_PERSONNEL, manager_id)
        cert_row = sheets_service.find_row_by_id(SHEET_CERTIFICATES, certificate_id)
        if not site_row or not manager_row or not cert_row:
            return jsonify({
                'success': False,
                'error': {'code': 'ROW_NOT_FOUND', 'message': '행을 찾을 수 없습니다'},
            }), 404

        now = datetime.now().strftime('%Y-%m-%d')
        updates = [
            {'range': f'{SHEET_SITES}!M{site_row}', 'values': [[manager_id]]},
            {'range': f'{SHEET_SITES}!P{site_row}', 'values': [[certificate_id]]},
            {'range': f'{SHEET_SITES}!U{site_row}', 'values': [['배정완료']]},
            {'range': f'{SHEET_SITES}!W{site_row}', 'values': [[now]]},
            {'range': f'{SHEET_PERSONNEL}!I{manager_row}', 'values': [[int(manager.get('현재담당현장수') or 0) + 1]]},
            {'range': f'{SHEET_PERSONNEL}!H{manager_row}', 'values': [['투입중']]},
            {'range': f'{SHEET_CERTIFICATES}!J{cert_row}', 'values': [['사용중']]},
            {'range': f'{SHEET_CERTIFICATES}!K{cert_row}', 'values': [[site_id]]},
        ]
        sheets_service.batch_update(updates)

        now = datetime.now().strftime('%Y-%m-%d')
        return jsonify({
            'success': True,
            'data': {
                '현장ID': site_id,
                '현장명': site.get('현장명', ''),
                '담당소장': manager.get('성명', ''),
                '자격증': certificate.get('자격증명', ''),
                'version': now,
            },
            'message': '소장이 배정되었습니다',
            'timestamp': datetime.now().isoformat(),
        })
    except ConflictError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'CONFLICT', 'message': str(e)},
        }), 409
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'ASSIGN_ERROR', 'message': str(e)},
        }), 500


@bp.route('/sites/<site_id>/unassign', methods=['POST'])
def unassign_manager(site_id):
    """소장 배정 해제. 2-3: If-Match 또는 body.version으로 버전 전달 시 충돌 검사"""
    try:
        site = sheets_service.get_site_by_id(site_id)
        if not site:
            return jsonify({
                'success': False,
                'error': {'code': 'SITE_NOT_FOUND', 'message': f'현장ID {site_id}를 찾을 수 없습니다'},
            }), 404

        # 2-3: 낙관적 잠금
        data = request.json or {}
        version = request.headers.get('If-Match') or data.get('version')
        try:
            get_sync_manager().require_site_version(site_id, version)
        except ConflictError as e:
            return jsonify({
                'success': False,
                'error': {'code': 'CONFLICT', 'message': str(e)},
            }), 409

        if not site.get('담당소장ID'):
            return jsonify({
                'success': False,
                'error': {'code': 'NOT_ASSIGNED', 'message': '배정된 소장이 없습니다'},
            }), 400

        manager_id = site['담당소장ID']
        cert_id = site.get('사용자격증ID') or ''
        manager = sheets_service.get_personnel_by_id(manager_id)

        site_row = sheets_service.find_row_by_id(SHEET_SITES, site_id)
        manager_row = sheets_service.find_row_by_id(SHEET_PERSONNEL, manager_id)
        cert_row = sheets_service.find_row_by_id(SHEET_CERTIFICATES, cert_id) if cert_id else None

        now = datetime.now().strftime('%Y-%m-%d')
        updates = [
            {'range': f'{SHEET_SITES}!M{site_row}', 'values': [['']]},
            {'range': f'{SHEET_SITES}!P{site_row}', 'values': [['']]},
            {'range': f'{SHEET_SITES}!U{site_row}', 'values': [['미배정']]},
            {'range': f'{SHEET_SITES}!W{site_row}', 'values': [[now]]},
            {'range': f'{SHEET_PERSONNEL}!I{manager_row}', 'values': [[max(0, int(manager.get('현재담당현장수') or 0) - 1)]]},
        ]
        if int(manager.get('현재담당현장수') or 0) <= 1:
            updates.append({'range': f'{SHEET_PERSONNEL}!H{manager_row}', 'values': [['투입가능']]})
        if cert_id and cert_row:
            updates.append({'range': f'{SHEET_CERTIFICATES}!J{cert_row}', 'values': [['사용가능']]})
            updates.append({'range': f'{SHEET_CERTIFICATES}!K{cert_row}', 'values': [['']]})

        sheets_service.batch_update(updates)

        now = datetime.now().strftime('%Y-%m-%d')
        return jsonify({
            'success': True,
            'data': {'현장ID': site_id, '현장명': site.get('현장명', ''), 'version': now},
            'message': '소장 배정이 해제되었습니다',
            'timestamp': datetime.now().isoformat(),
        })
    except ConflictError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'CONFLICT', 'message': str(e)},
        }), 409
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'UNASSIGN_ERROR', 'message': str(e)},
        }), 500
