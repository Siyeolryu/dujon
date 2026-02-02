# -*- coding: utf-8 -*-
"""
전체 테스트 실행 후 HTML 리포트 생성
실행: python run_all_tests.py
생성: test_report.html (브라우저에서 열어 결과 확인)
"""
import sys
import os
import io
import json
import urllib.request
import urllib.error
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _html_escape(s):
    """HTML 속성/내용용 이스케이프"""
    if s is None:
        return ""
    s = str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("\n", "<br>")
    return s


def run_with_capture(func, *args, **kwargs):
    """함수 실행 시 stdout/stderr 캡처 후 (반환값, 캡처된 출력) 반환"""
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = buf = io.StringIO()
    sys.stderr = buf_err = io.StringIO()
    try:
        ret = func(*args, **kwargs)
        out = buf.getvalue().strip() + "\n" + buf_err.getvalue().strip()
        return ret, out
    except SystemExit as e:
        out = (buf.getvalue() + buf_err.getvalue()).strip() + "\n종료코드: " + str(e.code)
        return False, out
    except Exception as e:
        out = (buf.getvalue() + buf_err.getvalue()).strip() + "\n예외: " + str(e)
        return False, out
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def collect_step1():
    """1단계 스크립트 검증 테스트 수집"""
    results = []
    try:
        import test_phase2_step1 as t1
    except Exception as e:
        results.append({"suite": "1단계", "name": "모듈 로드", "passed": False, "detail": str(e)})
        return results

    for label, func in [
        ("1-1 데이터 검증 규칙", t1.test_1_1_data_validation),
        ("1-2 조건부 서식", t1.test_1_2_conditional_formatting),
        ("1-3 VLOOKUP 수식", t1.test_1_3_vlookup_formulas),
    ]:
        passed, detail = run_with_capture(func)
        results.append({"suite": "1단계", "name": label, "passed": passed, "detail": detail or ("통과" if passed else "실패")})
    return results


def collect_step2():
    """2단계 API 검증 테스트 수집"""
    results = []
    try:
        import test_phase2_step2 as t2
    except Exception as e:
        results.append({"suite": "2단계", "name": "모듈 로드", "passed": False, "detail": str(e)})
        return results

    for label, func in [
        ("Sheets 서비스 (update/batch/find/append)", t2.test_sheets_service),
        ("Validation (validate_site_data, validate_assignment)", t2.test_validation),
        ("Sites POST/PUT/assign/unassign", t2.test_sites_routes),
        ("Personnel PUT", t2.test_personnel_put),
        ("Certificates PUT", t2.test_certificates_put),
    ]:
        passed, detail = run_with_capture(func)
        results.append({"suite": "2단계", "name": label, "passed": passed, "detail": detail or ("통과" if passed else "실패")})
    return results


def check_api_health():
    """API 서버 헬스 체크 (선택, 서버 실행 중일 때만)"""
    try:
        req = urllib.request.Request("http://localhost:5000/api/health")
        with urllib.request.urlopen(req, timeout=2) as res:
            data = json.loads(res.read().decode())
            ok = data.get("status") in ("healthy", "ok")
            return ok, data.get("status", "") if ok else str(data)
    except urllib.error.URLError as e:
        return False, "서버 미실행 또는 연결 실패: " + str(e.reason)
    except Exception as e:
        return False, str(e)


def build_report(all_results, api_ok, api_detail):
    """HTML 리포트 문자열 생성"""
    passed_total = sum(1 for r in all_results if r.get("passed"))
    total = len(all_results)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows = []
    for r in all_results:
        status = "pass" if r.get("passed") else "fail"
        status_text = "통과" if r.get("passed") else "실패"
        detail = _html_escape(r.get("detail"))
        rows.append(
            f'<tr class="{status}"><td>{r.get("suite", "")}</td><td>{r.get("name", "")}</td>'
            f'<td><span class="badge {status}">{status_text}</span></td><td class="detail">{detail}</td></tr>'
        )
    rows_html = "\n".join(rows)

    api_row = ""
    if api_ok is not None:
        api_status = "pass" if api_ok else "fail"
        api_text = "연결됨" if api_ok else "미연결"
        api_detail_esc = _html_escape(api_detail)
        api_row = f'<tr class="{api_status}"><td>API</td><td>헬스 체크 (localhost:5000)</td><td><span class="badge {api_status}">{api_text}</span></td><td class="detail">{api_detail_esc}</td></tr>'

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>테스트 리포트 - 현장배정 관리 시스템</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', 'Malgun Gothic', sans-serif; margin: 0; padding: 24px; background: #f5f6fa; color: #2c3e50; }}
        h1 {{ font-size: 24px; margin-bottom: 8px; }}
        .meta {{ color: #7f8c8d; font-size: 14px; margin-bottom: 24px; }}
        .summary {{ display: flex; gap: 24px; flex-wrap: wrap; margin-bottom: 24px; }}
        .summary-card {{ background: #fff; padding: 16px 24px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
        .summary-card .num {{ font-size: 28px; font-weight: bold; }}
        .summary-card.pass .num {{ color: #27ae60; }}
        .summary-card.fail .num {{ color: #e74c3c; }}
        .summary-card .label {{ font-size: 13px; color: #7f8c8d; margin-top: 4px; }}
        table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); overflow: hidden; }}
        th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #2c3e50; color: #fff; font-size: 13px; }}
        td {{ font-size: 14px; }}
        tr.pass {{ background: #fff; }}
        tr.fail {{ background: #fff5f5; }}
        td.detail {{ font-size: 12px; color: #555; max-width: 400px; word-break: break-all; }}
        .badge {{ display: inline-block; padding: 4px 10px; border-radius: 8px; font-size: 12px; font-weight: 600; }}
        .badge.pass {{ background: #d4edda; color: #155724; }}
        .badge.fail {{ background: #f8d7da; color: #721c24; }}
    </style>
</head>
<body>
    <h1>테스트 리포트</h1>
    <p class="meta">생성 시각: {ts} | 현장배정 관리 시스템 Phase 2</p>

    <div class="summary">
        <div class="summary-card pass"><div class="num">{passed_total}</div><div class="label">통과</div></div>
        <div class="summary-card fail"><div class="num">{total - passed_total}</div><div class="label">실패</div></div>
        <div class="summary-card"><div class="num">{total}</div><div class="label">전체</div></div>
    </div>

    <table>
        <thead><tr><th>구분</th><th>테스트 항목</th><th>결과</th><th>상세</th></tr></thead>
        <tbody>
            {rows_html}
            {api_row}
        </tbody>
    </table>
</body>
</html>"""
    return html


def main():
    os.chdir(ROOT)
    print("전체 테스트 실행 중...")
    all_results = []
    all_results.extend(collect_step1())
    all_results.extend(collect_step2())

    api_ok = None
    api_detail = ""
    try:
        api_ok, api_detail = check_api_health()
    except Exception:
        api_ok = False
        api_detail = "체크 중 오류"

    report_path = os.path.join(ROOT, "test_report.html")
    html = build_report(all_results, api_ok, api_detail)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"리포트 저장: {report_path}")

    passed = sum(1 for r in all_results if r.get("passed"))
    total = len(all_results)
    print(f"결과: {passed}/{total} 통과")
    if api_ok is not None:
        print(f"API 헬스: {'연결됨' if api_ok else '미연결'}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
