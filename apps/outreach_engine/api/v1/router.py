"""
Outreach Engine API v1 Router
LEVEL 4 - API routing configuration for outreach communication endpoints
"""

import sys
from pathlib import Path

# Add project root to Python path for shared API imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import APIRouter

# Import shared API components from framework layer
from agentic_core.api import (
    create_success_response,
    create_error_response,
    handle_errors,
    log_api_calls,
    ServiceUnavailableAPIException
)

# Import endpoint routers with error handling
try:
    from .endpoints import send_outreach, preview_message, healthcheck
    ENDPOINTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import some endpoint routers: {e}")
    ENDPOINTS_AVAILABLE = False
    send_outreach = None
    preview_message = None
    healthcheck = None

# Outreach Engine API Router
router = APIRouter(prefix="/outreach", tags=["outreach"])

# Include all outreach engine endpoints if available
if ENDPOINTS_AVAILABLE:
    if send_outreach:
        router.include_router(send_outreach.router, prefix="/send", tags=["outreach-sending"])
    if preview_message:
        router.include_router(preview_message.router, prefix="/preview", tags=["outreach-preview"])
    if healthcheck:
        router.include_router(healthcheck.router, prefix="/health", tags=["health"])

@router.get("/")
@handle_errors()
@log_api_calls(log_level="info")
async def root():
    """Root endpoint for outreach engine"""
    try:
        if not ENDPOINTS_AVAILABLE:
            return create_error_response(
                error_code="ENDPOINTS_UNAVAILABLE",
                message="Some endpoint routers are not available",
                error_type="configuration_error"
            )

        available_endpoints = []
        if healthcheck:
            available_endpoints.extend(["/health/ - Health check endpoints"])
        if send_outreach:
            available_endpoints.extend(["/outreach/send - Send outreach message"])
        if preview_message:
            available_endpoints.extend(["/outreach/preview - Message preview"])

        return create_success_response(
            data={
                "engine": "outreach_engine",
                "version": "1.0.0",
                "status": "active",
                "shared_api_integration": "agentic_core.api",
                "available_endpoints": available_endpoints
            },
            message="Outreach engine API is running"
        )

    except Exception:
        raise ServiceUnavailableAPIException(
            message="Root endpoint unavailable",
            error_code="ROOT_ENDPOINT_ERROR"
        )

__all__ = ["router"]
