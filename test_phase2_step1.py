"""
Phase 2 - 1단계 스크립트 검증 테스트

Google API 호출 없이 스크립트 구조·함수·요청 형식만 검증합니다.
실행: python test_phase2_step1.py
"""

import sys
import os

def test_1_1_data_validation():
    """1-1 데이터 검증 규칙 스크립트 검증"""
    print("[1-1] apply_data_validation.py 검증 중...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "apply_data_validation",
            os.path.join(os.path.dirname(__file__), "apply_data_validation.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as e:
        print(f"      실패: {e}")
        return False

    for name in ("get_google_sheets_service", "get_sheet_id_by_name", "apply_dropdown_validation", "main"):
        if not hasattr(mod, name):
            print(f"      누락: {name}")
            return False

    # column_to_number 동작 확인
    if mod.column_to_number("A") != 0 or mod.column_to_number("L") != 11:
        print("      column_to_number 동작 오류")
        return False

    print("      통과")
    return True


def test_1_2_conditional_formatting():
    """1-2 조건부 서식 스크립트 검증"""
    print("[1-2] apply_conditional_formatting.py 검증 중...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "apply_conditional_formatting",
            os.path.join(os.path.dirname(__file__), "apply_conditional_formatting.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as e:
        print(f"      실패: {e}")
        return False

    for name in ("get_google_sheets_service", "create_header_format", "apply_sheet1_formatting",
                 "apply_sheet2_formatting", "apply_sheet3_formatting", "main"):
        if not hasattr(mod, name):
            print(f"      누락: {name}")
            return False

    # 시트1 서식 요청 개수 (헤더 + 배정2 + 현장4 + 착공1 + 회사2 + 줄무늬)
    reqs = mod.apply_sheet1_formatting(sheet_id=0)
    if not isinstance(reqs, list) or len(reqs) < 10:
        print(f"      apply_sheet1_formatting 요청 개수 이상: {len(reqs)}")
        return False
    if not any("repeatCell" in str(r) for r in reqs):
        print("      repeatCell(헤더) 없음")
        return False
    if not any("addConditionalFormatRule" in str(r) for r in reqs):
        print("      addConditionalFormatRule 없음")
        return False

    print("      통과")
    return True


def test_1_3_vlookup_formulas():
    """1-3 VLOOKUP 수식 스크립트 검증"""
    print("[1-3] apply_vlookup_formulas.py 검증 중...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "apply_vlookup_formulas",
            os.path.join(os.path.dirname(__file__), "apply_vlookup_formulas.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as e:
        print(f"      실패: {e}")
        return False

    for name in ("get_google_sheets_service", "insert_column", "add_header",
                 "apply_formula_column", "COLUMNS_TO_ADD", "main"):
        if not hasattr(mod, name):
            print(f"      누락: {name}")
            return False

    if len(mod.COLUMNS_TO_ADD) != 5:
        print(f"      COLUMNS_TO_ADD 개수 오류: {len(mod.COLUMNS_TO_ADD)}")
        return False
    headers = {c["header"] for c in mod.COLUMNS_TO_ADD}
    expected = {"담당소장명", "담당소장연락처", "자격증명", "자격증소유자명", "자격증소유자연락처"}
    if headers != expected:
        print(f"      컬럼 헤더 불일치: {headers}")
        return False

    # insert_column 반환 구조
    r = mod.insert_column(sheet_id=0, col_index=12)
    if "insertDimension" not in r or r["insertDimension"]["range"]["startIndex"] != 12:
        print("      insert_column 반환 형식 오류")
        return False

    print("      통과")
    return True


def main():
    print("=" * 60)
    print("Phase 2 - 1단계 스크립트 검증 테스트")
    print("=" * 60)
    print()

    results = []
    results.append(("1-1 데이터 검증 규칙", test_1_1_data_validation()))
    results.append(("1-2 조건부 서식", test_1_2_conditional_formatting()))
    results.append(("1-3 VLOOKUP 수식", test_1_3_vlookup_formulas()))

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
        print("1단계 스크립트 검증 완료. 실제 적용은 run_phase2_step1.bat 실행.")
        return 0
    print("일부 검증 실패. 위 메시지를 확인하세요.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
