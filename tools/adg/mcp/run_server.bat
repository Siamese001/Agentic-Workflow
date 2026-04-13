@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%..\..\.."

pushd "%REPO_ROOT%" >nul 2>&1 || (
    echo Failed to resolve repository root from "%SCRIPT_DIR%"
    exit /b 1
)

if not exist "tools\adg\mcp\server.py" (
    echo Could not find tools\adg\mcp\server.py under "%CD%"
    popd >nul
    exit /b 1
)

set "PYTHONPATH=%CD%;%PYTHONPATH%"
python -m tools.adg.mcp.server
set "EXIT_CODE=%ERRORLEVEL%"

popd >nul
exit /b %EXIT_CODE%
