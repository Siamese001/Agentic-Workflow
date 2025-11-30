"""
Resume Engine Health Check Endpoint
LEVEL 5 - System health monitoring and status reporting
"""

import sys
from pathlib import Path

# Add project root to Python path for shared API imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import APIRouter
from typing import Dict, Any
import asyncio
import time
from datetime import datetime

# Import shared API components from framework layer
from agentic_core.api import (
    create_health_check_response,
    create_success_response,
    create_error_response,
    handle_errors,
    log_api_calls,
    APIException,
    ServiceUnavailableAPIException
)

router = APIRouter()

class HealthCheckEndpoint:
    """Monitors resume engine system health and component status"""
    
    def __init__(self):
        self.start_time = time.time()
        self.component_status = {
            "section_generator": True,
            "resume_pipeline": True,
            "ats_optimizer": True,
            "skill_expander": True
        }
    
    async def check_component_health(self, component_name: str) -> bool:
        """Check health of specific component"""
        # Simulate component health check
        await asyncio.sleep(0.01)  # Simulate async operation
        return self.component_status.get(component_name, False)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        current_time = time.time()
        uptime = current_time - self.start_time
        
        # Check all components
        component_health = {}
        for component in self.component_status:
            component_health[component] = await self.check_component_health(component)
        
        overall_health = all(component_health.values())
        
        return {
            "status": "healthy" if overall_health else "degraded",
            "uptime_seconds": uptime,
            "components": component_health,
            "version": "1.0.0",
            "timestamp": current_time
        }

@router.get("/")
@handle_errors()
@log_api_calls(log_level="info")
async def health_check():
    """Get comprehensive health status"""
    try:
        health_checker = HealthCheckEndpoint()
        system_status = await health_checker.get_system_status()
        
        # Convert to match shared API response format
        health_score = 1.0 if system_status["status"] == "healthy" else 0.7
        issues = [] if system_status["status"] == "healthy" else ["Some components degraded"]
        
        return create_health_check_response(
            status=system_status["status"],
            health_score=health_score,
            uptime_seconds=system_status["uptime_seconds"],
            components=system_status["components"],
            workers={},  # No workers in current implementation
            resources={},  # No resource monitoring in current implementation
            version=system_status["version"],
            issues=issues,
            message=f"Resume engine is {system_status['status']}"
        )
        
    except Exception as e:
        raise ServiceUnavailableAPIException(
            message="Health check service unavailable",
            error_code="HEALTH_SERVICE_UNAVAILABLE"
        )

@router.get("/ping")
@handle_errors()
@log_api_calls(log_level="debug")
async def ping():
    """Simple ping endpoint for basic connectivity check"""
    health_checker = HealthCheckEndpoint()
    uptime_seconds = time.time() - health_checker.start_time
    
    return create_success_response(
        data={
            "status": "ok",
            "uptime_seconds": uptime_seconds
        },
        message="Resume engine is running"
    )

@router.get("/components")
@handle_errors()
@log_api_calls(log_level="info")
async def check_components():
    """Check health of individual components"""
    try:
        health_checker = HealthCheckEndpoint()
        components = {}
        
        for component in health_checker.component_status:
            components[component] = await health_checker.check_component_health(component)
        
        return create_success_response(
            data=components,
            message="Component health check completed"
        )
    except Exception as e:
        raise ServiceUnavailableAPIException(
            message="Component health check failed",
            error_code="COMPONENT_HEALTH_ERROR"
        )

__all__ = ["router", "HealthCheckEndpoint"]
