"""
Autonomy Dashboard Server
Serves the autonomy dashboard with metrics API integration

SAFETY: Run ../dashboard/run_tests.sh after ANY change to this file
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import logging
from agentic_core.observability.metrics.shared_counters import get_layer_counts

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Autonomy Dashboard", version="1.0.0")

# Get the directory where this file is located
DASHBOARD_DIR = Path(__file__).parent
STATIC_DIR = DASHBOARD_DIR / "static"

# Ensure static directory exists
STATIC_DIR.mkdir(exist_ok=True, parents=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
async def root():
    """Serve the main dashboard HTML"""
    dashboard_html = STATIC_DIR / "autonomy_dashboard.html"
    if dashboard_html.exists():
        return FileResponse(str(dashboard_html), media_type="text/html")
    else:
        return {
            "error": "Dashboard not found",
            "expected_path": str(dashboard_html),
            "static_dir_exists": STATIC_DIR.exists(),
            "static_dir_contents": list(STATIC_DIR.glob("*")) if STATIC_DIR.exists() else []
        }

@app.get("/api/metrics")
async def get_metrics():
    """Get layer activation counts for CoverageAgent and dashboard visualization"""
    try:
        layer_counts = get_layer_counts()
        return {
            "status": "success",
            "layer_counts": layer_counts,
            "total_activations": sum(layer_counts.values())
        }
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        return {
            "status": "error",
            "message": str(e),
            "layer_counts": {}
        }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "autonomy-dashboard",
        "static_dir": str(STATIC_DIR),
        "static_dir_exists": STATIC_DIR.exists()
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
    logger.info(f"Starting dashboard server from {DASHBOARD_DIR}")
    logger.info(f"Static files directory: {STATIC_DIR}")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
