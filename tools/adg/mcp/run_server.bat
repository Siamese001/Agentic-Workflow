@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%..\..\.."

pushd "%REPO_ROOT%" >nul 2>&1 || (
    echo Failed to resolve repository root from "%SCRIPT_DIR%"
    exit /b 1
)

if not exist "tools\mcp\launch_adg_sqlite_mcp.py" (
    echo Could not find tools\mcp\launch_adg_sqlite_mcp.py under "%CD%"
    popd >nul
    exit /b 1
)

set "PYTHONPATH=%CD%;%PYTHONPATH%"
python -m tools.mcp.launch_adg_sqlite_mcp
set "EXIT_CODE=%ERRORLEVEL%"

popd >nul
exit /b %EXIT_CODE%
