@echo off
echo ========================================
echo Guardian Suite - Architectural Health Check
echo ========================================
echo.

REM Run pytest on guardian tests and capture output
pytest tests/guardian/ -v --tb=short > guardian_temp_output.txt 2>&1
set PYTEST_EXIT_CODE=%errorlevel%

REM Display the output
type guardian_temp_output.txt

REM Generate summary
echo.
echo ========================================
echo GUARDIAN STATUS SUMMARY
echo ========================================

if %PYTEST_EXIT_CODE% equ 0 (
    echo Guardian Status: PASS
    echo All architectural integrity checks passed!
) else (
    echo Guardian Status: FAIL
    echo Architectural violations detected - see output above
)

echo.
echo Report saved to: guardian_report.txt
echo ========================================

REM Clean up temp file
del guardian_temp_output.txt

REM Exit with same code as pytest
exit /b %PYTEST_EXIT_CODE%
