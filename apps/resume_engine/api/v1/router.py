"""
Resume Engine API v1 Router
LEVEL 4 - API routing configuration for resume generation endpoints
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
    APIException,
    ServiceUnavailableAPIException
)

# Import endpoint routers with error handling
try:
    from .endpoints import generate_resume, healthcheck
    VALIDATE_RESUME_AVAILABLE = False  # validate_resume doesn't exist yet
    GENERATE_RESUME_AVAILABLE = True
    HEALTHCHECK_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import some endpoint routers: {e}")
    GENERATE_RESUME_AVAILABLE = False
    HEALTHCHECK_AVAILABLE = False
    VALIDATE_RESUME_AVAILABLE = False
    generate_resume = None
    healthcheck = None

# Resume Engine API Router
router = APIRouter(prefix="/resume", tags=["resume"])

# Include all resume engine endpoints if available
if GENERATE_RESUME_AVAILABLE and generate_resume:
    router.include_router(generate_resume.router, prefix="/generate", tags=["resume-generation"])

if HEALTHCHECK_AVAILABLE and healthcheck:
    router.include_router(healthcheck.router, prefix="/health", tags=["health"])

@router.get("/")
@handle_errors()
@log_api_calls(log_level="info")
async def root():
    """Root endpoint for resume engine"""
    try:
        available_endpoints = []
        
        if HEALTHCHECK_AVAILABLE and healthcheck:
            available_endpoints.extend(["/health/ - Health check endpoints"])
        if GENERATE_RESUME_AVAILABLE and generate_resume:
            available_endpoints.extend(["/resume/generate/ - Generate resume"])
        if VALIDATE_RESUME_AVAILABLE:
            available_endpoints.extend(["/resume/validate/ - Validate resume"])
        
        return create_success_response(
            data={
                "engine": "resume_engine",
                "version": "1.0.0",
                "status": "active",
                "shared_api_integration": "agentic_core.api",
                "available_endpoints": available_endpoints,
                "integration_status": {
                    "healthcheck": HEALTHCHECK_AVAILABLE,
                    "generate_resume": GENERATE_RESUME_AVAILABLE,
                    "validate_resume": VALIDATE_RESUME_AVAILABLE
                }
            },
            message="Resume engine API is running"
        )
        
    except Exception as e:
        raise ServiceUnavailableAPIException(
            message="Root endpoint unavailable",
            error_code="ROOT_ENDPOINT_ERROR"
        )

@router.get("/status")
@handle_errors()
@log_api_calls(log_level="info")
async def engine_status():
    """Get overall engine status"""
    try:
        # Check which routers are available
        router_status = {
            "healthcheck_router": HEALTHCHECK_AVAILABLE,
            "generate_resume_router": GENERATE_RESUME_AVAILABLE,
            "validate_resume_router": VALIDATE_RESUME_AVAILABLE
        }
        
        # Calculate overall status
        available_routers = sum(router_status.values())
        total_routers = len(router_status)
        health_percentage = (available_routers / total_routers) * 100 if total_routers > 0 else 0
        
        status = "healthy" if health_percentage >= 100 else "degraded" if health_percentage >= 66 else "unhealthy"
        
        status_data = {
            "status": status,
            "health_percentage": health_percentage,
            "router_status": router_status,
            "available_routers": available_routers,
            "total_routers": total_routers,
            "shared_api_status": "integrated",
            "architectural_compliance": "L5 compliant"
        }
        
        return create_success_response(
            data=status_data,
            message=f"Engine status: {status}"
        )
        
    except Exception as e:
        raise ServiceUnavailableAPIException(
            message="Engine status unavailable",
            error_code="ENGINE_STATUS_ERROR"
        )

__all__ = ["router"]
