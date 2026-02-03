"""
통계 API 라우트 (GET)
"""
from datetime import datetime
from flask import Blueprint, jsonify
from api.services.db_service import get_db

bp = Blueprint('stats', __name__)


@bp.route('/stats', methods=['GET'])
def get_statistics():
    """전체 통계 (현장/인력/자격증)"""
    try:
        db = get_db()
        sites = db.get_all_sites()
        personnel = db.get_all_personnel()
        certificates = db.get_all_certificates()

        site_stats = {
            'total': len(sites),
            'assigned': len([s for s in sites if s['배정상태'] == '배정완료']),
            'unassigned': len([s for s in sites if s['배정상태'] == '미배정']),
            'by_company': {
                '더존종합건설': len([s for s in sites if s['회사구분'] == '더존종합건설']),
                '더존하우징': len([s for s in sites if s['회사구분'] == '더존하우징']),
            },
            'by_state': {},
        }
        for s in sites:
            st = s.get('현장상태') or ''
            site_stats['by_state'][st] = site_stats['by_state'].get(st, 0) + 1

        personnel_stats = {
            'total': len(personnel),
            'available': len([p for p in personnel if p['현재상태'] == '투입가능']),
            'deployed': len([p for p in personnel if p['현재상태'] == '투입중']),
            'by_role': {},
        }
        for p in personnel:
            role = p.get('직책') or ''
            personnel_stats['by_role'][role] = personnel_stats['by_role'].get(role, 0) + 1

        cert_stats = {
            'total': len(certificates),
            'available': len([c for c in certificates if c['사용가능여부'] == '사용가능']),
            'in_use': len([c for c in certificates if c['사용가능여부'] == '사용중']),
            'expired': len([c for c in certificates if c['사용가능여부'] == '만료']),
        }

        return jsonify({
            'success': True,
            'data': {
                'sites': site_stats,
                'personnel': personnel_stats,
                'certificates': cert_stats,
            },
            'timestamp': datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'STATS_ERROR', 'message': str(e)},
        }), 500
