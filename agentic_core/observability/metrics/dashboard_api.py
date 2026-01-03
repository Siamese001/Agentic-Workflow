"""
Dashboard API endpoints for metrics and telemetry
Provides REST API endpoints for the autonomy dashboard
"""

from fastapi import FastAPI
from typing import Dict, Any
from agentic_core.observability.metrics.shared_counters import get_layer_counts

app = FastAPI()

@app.get("/api/metrics")
def get_layer_metrics() -> Dict[str, Any]:
    """Get layer activation counts for CoverageAgent"""
    return {"layer_counts": get_layer_counts()}

@app.get("/api/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}

# Additional dashboard endpoints can be added here as needed
