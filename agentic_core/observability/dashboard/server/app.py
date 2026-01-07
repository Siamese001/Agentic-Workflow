"""
Unified Dashboard Server - Sovereign SSOT API (L6 Observability)
Consolidates duplicate implementations from /dashboard and /metrics.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
from agentic_core.observability.dashboard.core.data_generator import DashboardDataGenerator
from agentic_core.observability.dashboard.core.renderer import DashboardRenderer

app = FastAPI(title="Autonomy Compliance Dashboard API")
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent

@app.get("/api/v2/compliance")
async def get_compliance_data():
    """SSOT endpoint providing unified metrics for all consumers."""
    try:
        # ARCHITECTURAL HARDENING: Shared L6 Logic with AutonomyGuardianAgent
        generator = DashboardDataGenerator(PROJECT_ROOT, {})  # Territories resolved dynamically
        registry = generator.load_registry()
        return {"status": "healthy", "metrics": generator.registry_by_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    """Serves the consolidated L6 HTML template."""
    renderer = DashboardRenderer(PROJECT_ROOT)
    return renderer.load_template()
