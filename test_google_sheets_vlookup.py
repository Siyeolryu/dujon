# -*- coding: utf-8 -*-
"""
Google Sheets 연동 + VLOOKUP 전용 테스트

실행: python test_google_sheets_vlookup.py
- 1-3 VLOOKUP 수식 스크립트 구조 검증 (apply_vlookup_formulas.py)
- Sheets 서비스 메서드 검증 (api.services.sheets_service)
Google API 호출 없이 모듈/함수 존재 여부만 검증합니다.
"""
import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main():
    print("=" * 60)
    print("Google Sheets 연동 + VLOOKUP 테스트")
    print("=" * 60)

    results = []

    # 1-3 VLOOKUP 수식 검증
    try:
        import test_phase2_step1 as t1
        ok = t1.test_1_3_vlookup_formulas()
        results.append(("1-3 VLOOKUP 수식", ok))
    except Exception as e:
        results.append(("1-3 VLOOKUP 수식", False))
        print(f"[1-3] 예외: {e}")

    # Sheets 서비스 검증
    try:
        import test_phase2_step2 as t2
        ok = t2.test_sheets_service()
        results.append(("Sheets 서비스 (연동 구조)", ok))
    except Exception as e:
        results.append(("Sheets 서비스 (연동 구조)", False))
        print(f"[2-2] 예외: {e}")

    print()
    print("-" * 60)
    for name, passed in results:
        status = "통과" if passed else "실패"
        print(f"  {name}: {status}")
    print("-" * 60)
    all_ok = all(r[1] for r in results)
    print("결과:", "전체 통과" if all_ok else "일부 실패")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
