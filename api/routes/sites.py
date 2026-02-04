"""
현장 관련 API 라우트 (GET / POST / PUT)
"""
import uuid
from datetime import datetime
from flask import Blueprint, jsonify, request
from api.services.db_service import get_db
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
    """현장 목록 조회. 쿼리: company, status, state, limit, offset"""
    try:
        db = get_db()
        
        # 페이지네이션 파라미터
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int, default=0)
        
        # 필터 파라미터
        company = request.args.get('company')
        status = request.args.get('status')
        state = request.args.get('state')

        # 서버 사이드 페이지네이션 지원 여부 확인
        if hasattr(db, 'get_sites_paginated'):
            # 페이지네이션 지원 메서드 사용
            result = db.get_sites_paginated(
                company=company,
                status=status,
                state=state,
                limit=limit,
                offset=offset,
            )
            sites = result.get('data', [])
            total_count = result.get('total', len(sites))
        else:
            # 기존 방식 (클라이언트 사이드 필터링)
            sites = db.get_all_sites()

            if company:
                sites = [s for s in sites if s['회사구분'] == company]
            if status:
                sites = [s for s in sites if s['배정상태'] == status]
            if state:
                sites = [s for s in sites if s['현장상태'] == state]

            total_count = len(sites)
            
            # 클라이언트 사이드 페이지네이션
            if limit:
                sites = sites[offset:offset + limit]

        return jsonify({
            'success': True,
            'data': sites,
            'count': len(sites),
            'total': total_count,
            'limit': limit,
            'offset': offset,
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

        db = get_db()
        sites = db.get_all_sites()
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
        db = get_db()
        site = db.get_site_by_id(site_id)
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
        db = get_db()
        if not data.get('현장ID') or not str(data.get('현장ID', '')).strip():
            data['현장ID'] = _generate_site_id()
            while db.get_site_by_id(data['현장ID']):
                data['현장ID'] = _generate_site_id()

        try:
            validate_site_data(data, is_update=False)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': {'code': 'VALIDATION_ERROR', 'message': str(e)},
            }), 400

        if db.get_site_by_id(data['현장ID']):
            return jsonify({
                'success': False,
                'error': {'code': 'DUPLICATE_ID', 'message': f"현장ID {data['현장ID']}가 이미 존재합니다"},
            }), 400

        now = datetime.now().strftime('%Y-%m-%d')
        row_data = {
            '현장ID': data['현장ID'],
            '현장명': data['현장명'],
            '건축주명': data.get('건축주명', ''),
            '회사구분': data['회사구분'],
            '주소': data['주소'],
            '위도': data.get('위도', ''),
            '경도': data.get('경도', ''),
            '건축허가일': data.get('건축허가일', ''),
            '착공예정일': data.get('착공예정일', ''),
            '준공일': data.get('준공일', ''),
            '현장상태': data.get('현장상태', '건축허가'),
            '특이사항': data.get('특이사항', ''),
            '담당소장ID': data.get('담당소장ID', ''),
            '담당소장명': '',
            '담당소장연락처': '',
            '사용자격증ID': data.get('사용자격증ID', ''),
            '자격증명': '',
            '자격증소유자명': '',
            '자격증소유자연락처': '',
            '준공필증파일URL': data.get('준공필증파일URL', ''),
            '배정상태': data.get('배정상태', '미배정'),
            '등록일': now,
            '수정일': now,
        }
        db.create_site(row_data)

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
    """현장 정보 수정. 2-3: If-Match 또는 body.version으로 버전 전달 시 충돌 검사"""
    try:
        db = get_db()
        site = db.get_site_by_id(site_id)
        if not site:
            return jsonify({
                'success': False,
                'error': {'code': 'SITE_NOT_FOUND', 'message': f'현장ID {site_id}를 찾을 수 없습니다'},
            }), 404

        data = request.json or {}
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

        allowed = {'현장명', '건축주명', '회사구분', '주소', '위도', '경도', '건축허가일', '착공예정일',
                   '준공일', '현장상태', '특이사항', '담당소장ID', '사용자격증ID', '준공필증파일URL', '배정상태'}
        update_data = {k: v for k, v in data.items() if k in allowed}
        now = datetime.now().strftime('%Y-%m-%d')
        update_data['수정일'] = now
        db.update_site(site_id, update_data)

        return jsonify({
            'success': True,
            'data': {'현장ID': site_id, 'updated_fields': list(update_data.keys()), 'version': now},
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
        db = get_db()
        site = db.get_site_by_id(site_id)
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

        manager = db.get_personnel_by_id(manager_id)
        if not manager:
            return jsonify({
                'success': False,
                'error': {'code': 'MANAGER_NOT_FOUND', 'message': f'인력ID {manager_id}를 찾을 수 없습니다'},
            }), 404

        certificate = db.get_certificate_by_id(certificate_id)
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

        version = request.headers.get('If-Match') or data.get('version')
        try:
            get_sync_manager().require_site_version(site_id, version)
        except ConflictError as e:
            return jsonify({
                'success': False,
                'error': {'code': 'CONFLICT', 'message': str(e)},
            }), 409

        db.assign_site(site_id, manager_id, certificate_id)

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
        db = get_db()
        site = db.get_site_by_id(site_id)
        if not site:
            return jsonify({
                'success': False,
                'error': {'code': 'SITE_NOT_FOUND', 'message': f'현장ID {site_id}를 찾을 수 없습니다'},
            }), 404

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

        db.unassign_site(site_id)

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
