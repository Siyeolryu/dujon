@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 전체 테스트 실행 중...
python run_all_tests.py
if %ERRORLEVEL% equ 0 (
    echo.
    echo 리포트 생성 완료. test_report.html 을 브라우저에서 열어 확인하세요.
) else (
    echo.
    echo 일부 테스트 실패. test_report.html 에 상세 결과가 저장되었습니다.
)
pause
