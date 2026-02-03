"""
Phase 2 - 2-2 데이터 수정 API 검증 테스트

Google API/Flask 서버 없이 2-2 구조(Sheets 서비스, 라우트, 검증)만 검증합니다.
실행: python test_phase2_step2.py
"""

import sys
import os

# 프로젝트 루트를 path에 추가 (api 패키지 import용)
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def test_sheets_service():
    """DB 서비스(Supabase/Sheets) 통합 인터페이스 메서드 존재 확인"""
    print("[2-2] api.services.db_service (Supabase/Sheets) 검증 중...")
    try:
        from api.services.db_service import get_db
        db = get_db()
    except Exception as e:
        print(f"      실패: {e}")
        return False

    read_methods = ('get_all_sites', 'get_site_by_id', 'get_all_personnel', 'get_personnel_by_id',
                   'get_all_certificates', 'get_certificate_by_id')
    write_methods = ('create_site', 'update_site', 'create_personnel', 'update_personnel',
                     'create_certificate', 'update_certificate', 'assign_site', 'unassign_site')
    for method in read_methods + write_methods:
        if not hasattr(db, method):
            print(f"      누락: {method}")
            return False
    print("      통과")
    return True


def test_validation():
    """검증 모듈 (validate_site_data, validate_assignment) 확인"""
    print("[2-2] api.services.validation 검증 중...")
    try:
        from api.services.validation import (
            ValidationError,
            validate_site_data,
            validate_assignment,
        )
    except Exception as e:
        print(f"      실패: {e}")
        return False

    # validate_site_data: 필수 필드 없으면 ValidationError
    try:
        validate_site_data({}, is_update=False)
        print("      validate_site_data 필수필드 검증 누락")
        return False
    except ValidationError:
        pass

    # validate_assignment: 이미 배정완료면 ValidationError
    site = {'배정상태': '배정완료'}
    manager = {'현재상태': '투입가능'}
    cert = {'사용가능여부': '사용가능'}
    try:
        validate_assignment(site, manager, cert)
        print("      validate_assignment 배정완료 검증 누락")
        return False
    except ValidationError:
        pass

    print("      통과")
    return True


def test_sites_routes():
    """sites 라우트 POST/PUT/assign/unassign 핸들러 존재 확인"""
    print("[2-2] api.routes.sites (POST/PUT/assign/unassign) 검증 중...")
    try:
        from api.routes import sites
    except Exception as e:
        print(f"      실패: {e}")
        return False

    for name in ('create_site', 'update_site', 'assign_manager', 'unassign_manager'):
        if not hasattr(sites, name):
            print(f"      누락: {name}")
            return False

    # Blueprint에 등록된 룰 확인 (앱에 등록 후)
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(sites.bp, url_prefix='/api')
    rules = [r for r in app.url_map.iter_rules() if r.endpoint and r.endpoint.startswith('sites.')]
    methods_by_rule = {}
    for r in rules:
        key = r.rule
        if key not in methods_by_rule:
            methods_by_rule[key] = set()
        methods_by_rule[key].update(r.methods or set())
    want = [
        ('/api/sites', 'POST'),
        ('/api/sites/<site_id>', 'PUT'),
        ('/api/sites/<site_id>/assign', 'POST'),
        ('/api/sites/<site_id>/unassign', 'POST'),
    ]
    for rule, method in want:
        if rule not in methods_by_rule or method not in methods_by_rule[rule]:
            print(f"      엔드포인트 없음: {method} {rule}")
            return False

    print("      통과")
    return True


def test_personnel_put():
    """personnel PUT 라우트 확인"""
    print("[2-2] api.routes.personnel (PUT) 검증 중...")
    try:
        from api.routes import personnel
        from flask import Flask
    except Exception as e:
        print(f"      실패: {e}")
        return False

    if not hasattr(personnel, 'update_personnel'):
        print("      update_personnel 함수 없음")
        return False
    app = Flask(__name__)
    app.register_blueprint(personnel.bp, url_prefix='/api')
    rules = [r for r in app.url_map.iter_rules() if 'PUT' in (r.methods or set()) and 'personnel' in r.rule]
    if not rules:
        print("      PUT /personnel/<id> 없음")
        return False
    print("      통과")
    return True


def test_certificates_put():
    """certificates PUT 라우트 확인"""
    print("[2-2] api.routes.certificates (PUT) 검증 중...")
    try:
        from api.routes import certificates
        from flask import Flask
    except Exception as e:
        print(f"      실패: {e}")
        return False

    if not hasattr(certificates, 'update_certificate'):
        print("      update_certificate 함수 없음")
        return False
    app = Flask(__name__)
    app.register_blueprint(certificates.bp, url_prefix='/api')
    rules = [r for r in app.url_map.iter_rules() if 'PUT' in (r.methods or set()) and 'certificates' in r.rule]
    if not rules:
        print("      PUT /certificates/<id> 없음")
        return False
    print("      통과")
    return True


def main():
    print("=" * 60)
    print("Phase 2 - 2-2 데이터 수정 API 검증 테스트")
    print("=" * 60)
    print()

    results = []
    results.append(("Sheets 서비스 (update/batch/find/append)", test_sheets_service()))
    results.append(("Validation (validate_site_data, validate_assignment)", test_validation()))
    results.append(("Sites POST/PUT/assign/unassign", test_sites_routes()))
    results.append(("Personnel PUT", test_personnel_put()))
    results.append(("Certificates PUT", test_certificates_put()))

    print()
    print("-" * 60)
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    for name, ok in results:
        status = "OK" if ok else "FAIL"
        print(f"  {name}: {status}")
    print("-" * 60)
    print(f"결과: {passed}/{total} 통과")
    print()
    if passed == total:
        print("2-2 데이터 수정 API 검증 완료. 실제 호출은 run_api.py 실행 후 curl/Postman으로 테스트.")
        return 0
    print("일부 검증 실패. 위 메시지를 확인하세요.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
