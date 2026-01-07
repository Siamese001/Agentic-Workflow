"""
Autonomy Dashboard Server
Serves the autonomy dashboard with metrics API integration

CONSOLIDATED LOCATION: agentic_core/observability/dashboard/
SAFETY: Run tests after ANY change to this file
FILESYSTEM COMPLIANCE: All file operations use safe_path_join from structure_blueprint
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import logging
# VIOLATION JUSTIFICATION: Exclusive reliance on the 283-agent SSOT Loader
# prevents metric drift between the filesystem and the UI.
from .dashboard_loader import load_agents, validate_sovereign_integrity, get_metrics_summary
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    get_validated_project_root,
    safe_path_join,
    validate_path_within_project
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Autonomy Dashboard", version="1.0.0")

# Get validated project root and build safe paths
try:
    PROJECT_ROOT = get_validated_project_root()
    # Dashboard module now at: agentic_core/observability/dashboard/
    DASHBOARD_DIR = safe_path_join(
        PROJECT_ROOT,
        "agentic_core", "observability", "dashboard"
    )
    # Reports output folder (generated dashboards)
    REPORTS_DIR = safe_path_join(PROJECT_ROOT, "reports")
except ValueError as e:
    logger.error(f"FILESYSTEM COMPLIANCE ERROR: {e}")
    raise

# Ensure reports directory exists
REPORTS_DIR.mkdir(exist_ok=True, parents=True)
logger.info(f"Dashboard module directory: {DASHBOARD_DIR}")
logger.info(f"Reports output directory: {REPORTS_DIR}")

# Mount reports folder as static files
app.mount("/static", StaticFiles(directory=str(REPORTS_DIR)), name="static")

@app.get("/")
async def root():
    """Serve the main dashboard HTML from reports folder"""
    dashboard_html = REPORTS_DIR / "autonomy_dashboard.html"
    if dashboard_html.exists():
        return FileResponse(str(dashboard_html), media_type="text/html")
    else:
        return {
            "error": "Dashboard not found - run: python canon_validator_agentic_v2_thin.py --report",
            "expected_path": str(dashboard_html),
            "reports_dir_exists": REPORTS_DIR.exists(),
            "reports_dir_contents": [f.name for f in REPORTS_DIR.glob("*.html")] if REPORTS_DIR.exists() else []
        }

@app.get("/api/metrics")
async def get_metrics():
    """
    Get canonical metrics from the 283-agent Sovereign Registry.
    All data sourced from agent_discovery_full.json SSOT.
    """
    try:
        agents = load_agents(refresh_if_stale=True)
        metrics = get_metrics_summary(agents)
        
        return {
            "status": "success",
            "total_agents": metrics["total_agents"],
            "healing_percentage": metrics["healing_percentage"],
            "testing_percentage": metrics["testing_percentage"],
            "layer_distribution": metrics["layer_distribution"],
            "top_folders": metrics["top_folders"],
            "baseline_status": metrics["baseline_status"],
            "expected_count": 283
        }
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        return {
            "status": "error",
            "message": str(e),
            "total_agents": 0,
            "layer_distribution": {}
        }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "autonomy-dashboard",
        "reports_dir": str(REPORTS_DIR),
        "reports_dir_exists": REPORTS_DIR.exists()
    }

@app.get("/api/config")
async def get_config():
    """Get dashboard configuration"""
    return {
        "dashboard_version": "1.0.0",
        "metrics_endpoint": "/api/metrics",
        "static_path": "/static",
        "layers": [
            "L0_maintenance", "L1_cognition", "L2_execution", "L3_orchestration",
            "L4_state", "L5_safety", "config", "schemas", "prompt_governance",
            "observability", "utils", "apps_rg", "apps_lic", "apps_shared"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    
    # Sovereign baseline integrity check on startup
    logger.info("Performing sovereign baseline integrity check...")
    if not validate_sovereign_integrity():
        logger.error(
            "FATAL: Sovereign baseline integrity check FAILED. "
            "Expected 283 agents. Run scripts/full_agent_discovery.py to verify."
        )
        raise RuntimeError("Dashboard startup aborted: Agent registry integrity violation")
    
    logger.info("✓ Sovereign baseline integrity verified (283 agents)")
    logger.info(f"Starting dashboard server from {DASHBOARD_DIR}")
    logger.info(f"Reports directory: {REPORTS_DIR}")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
