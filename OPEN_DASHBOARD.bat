@echo off
REM Quick launcher for Autonomy Dashboard
REM Opens dashboard directly in default browser (no server needed)

echo.
echo ========================================
echo   Autonomy Compliance Dashboard
echo ========================================
echo.
echo Opening dashboard in default browser...
echo.

start "" "%~dp0agentic_core\L6_observability\dashboards\autonomy_dashboard.html"

echo.
echo Dashboard opened!
echo.
echo NOTE: Charts require internet connection.
echo       All data tables work offline.
echo.
echo To update dashboard data:
echo   1. python scripts\full_agent_discovery.py
echo   2. python agentic_core\L6_observability\dashboards\generate_dashboard.py
echo   3. Hard refresh browser (Ctrl+Shift+R)
echo.
pause
