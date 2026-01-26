:: File: execute_sovereignty.bat
:: Path: C:\Git\Agentic-Workflow\execute_sovereignty.bat
:: Status: New Deployment Harness
:: Rationale: 
::    With 640 violations detected, a raw execution is dangerous. 
::    This script enforces a mandatory "Test -> Dry-Run -> Ack" pipeline.

@echo off
setlocal

echo ========================================================
echo   PASCAL SOVEREIGNTY: DEPLOYMENT PROTOCOL
echo ========================================================
echo.

:: Step 1: Pre-Flight Checks (Run the Test Suite)
echo [Step 1/3] Running Safety Tests...
python tests/test_pascal_sovereignty.py
if %errorlevel% neq 0 (
    echo [FATAL] Tests failed. Aborting deployment to protect the repo.
    exit /b %errorlevel%
)
echo [PASS] All logic verified.
echo.

:: Step 2: Dry Run (Generate Impact Report)
echo [Step 2/3] Generating Impact Report (Dry Run)...
python PascalSovereigntyFixer.py --dry-run > sovereignty_impact_report.txt
type sovereignty_impact_report.txt
echo.
echo [INFO] Detailed report saved to sovereignty_impact_report.txt
echo.

:: Step 3: The Gatekeeper
echo ========================================================
echo   WARNING: You are about to rename ~640 files.
echo   This action modifies import paths across the entire core.
echo   Ensure you have a clean git state before proceeding.
echo ========================================================
echo.
set /p "Auth=Type 'YES' to execute the Pascal Sovereignty enforcement: "

if /i "%Auth%" neq "YES" (
    echo [ABORT] Deployment cancelled by user.
    exit /b 0
)

:: Step 4: Execution
echo.
echo [Step 3/3] Enforcing Sovereignty...
python PascalSovereigntyFixer.py
echo.
echo [SUCCESS] File structure refactored.
echo [NEXT] Please review 'git status' and run full integration tests.
pause
