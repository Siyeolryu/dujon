@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === Phase 2 Step 1 - Script check ===
python test_phase2_step1.py
if errorlevel 1 (
  echo Test failed. Fix errors before applying.
  pause
  exit /b 1
)
echo.
echo === 1-1 Data validation ===
python apply_data_validation.py
if errorlevel 1 goto :eof
echo.
echo === 1-2 Conditional formatting ===
python apply_conditional_formatting.py
if errorlevel 1 goto :eof
echo.
echo === 1-3 VLOOKUP formulas ===
python apply_vlookup_formulas.py
echo.
echo === Phase 2 Step 1 done ===
