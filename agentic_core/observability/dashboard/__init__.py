"""
Dashboard Module - Consolidated dashboard components for autonomy observability.

Contains:
- dashboard_template.html: Self-contained HTML dashboard template
- dashboard_api.py: FastAPI endpoints for dashboard metrics
- dashboard_server.py: Full dashboard server with static file serving

Output Location:
- Generated dashboards are written to: reports/autonomy_dashboard.html
"""

from pathlib import Path

# Dashboard module paths
DASHBOARD_MODULE_DIR = Path(__file__).parent
TEMPLATE_PATH = DASHBOARD_MODULE_DIR / "dashboard_template.html"
