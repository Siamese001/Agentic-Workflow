#!/bin/bash
# Quick launcher for Autonomy Dashboard
# Opens dashboard directly in default browser (no server needed)

echo ""
echo "========================================"
echo "  Autonomy Compliance Dashboard"
echo "========================================"
echo ""
echo "Opening dashboard in default browser..."
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DASHBOARD_PATH="$SCRIPT_DIR/agentic_core/L6_observability/dashboards/autonomy_dashboard.html"

# Open in default browser (cross-platform)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "$DASHBOARD_PATH"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "$DASHBOARD_PATH"
else
    # Windows Git Bash
    start "$DASHBOARD_PATH"
fi

echo ""
echo "Dashboard opened!"
echo ""
echo "NOTE: Charts require internet connection."
echo "      All data tables work offline."
echo ""
echo "To update dashboard data:"
echo "  1. python scripts/full_agent_discovery.py"
echo "  2. python agentic_core/L6_observability/dashboards/generate_dashboard.py"
echo "  3. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)"
echo ""
