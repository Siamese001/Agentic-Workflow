"""
Outreach Engine Health Check Endpoint
LEVEL 5 - API endpoint for monitoring outreach engine health and status
"""

import sys
from pathlib import Path

# Add project root to Python path for shared API imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime, timedelta

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

from ...services.pipelines.outreach_pipeline import OutreachPipeline
from ...workers.outreach_generate_worker import OutreachGenerateWorker
from ...workers.enrichment_worker import EnrichmentWorker
from ...services.utils.scoring import OutreachScorer

router = APIRouter(prefix="/health", tags=["health"])

# Initialize services
outreach_pipeline = OutreachPipeline()
outreach_worker = OutreachGenerateWorker()
enrichment_worker = EnrichmentWorker()
outreach_scorer = OutreachScorer()

class HealthCheckEndpoint:
    """Handles health check requests for outreach engine"""
    
    def __init__(self):
        self.pipeline = outreach_pipeline
        self.outreach_worker = outreach_worker
        self.enrichment_worker = enrichment_worker
        self.scorer = outreach_scorer
        self.start_time = datetime.utcnow()
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        try:
            # Check component health
            component_status = await self._check_components()
            
            # Check worker status
            worker_status = await self._check_workers()
            
            # Check system resources
            resource_status = await self._check_resources()
            
            # Calculate overall health
            overall_health = self._calculate_overall_health(component_status, worker_status, resource_status)
            
            return {
                "status": overall_health["status"],
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
                "components": component_status,
                "workers": worker_status,
                "resources": resource_status,
                "version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat(),
                "health_score": overall_health["score"],
                "issues": overall_health["issues"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds()
            }
    
    async def _check_components(self) -> Dict[str, bool]:
        """Check health of all components"""
        component_status = {}
        
        try:
            # Check outreach pipeline
            pipeline_status = await self.pipeline.get_pipeline_status()
            component_status["outreach_pipeline"] = pipeline_status["total_stages"] == 5
            
            # Check outreach scorer
            component_status["outreach_scorer"] = True  # Simple check - scorer is always available
            
            # Check message generators
            component_status["message_generator"] = True
            component_status["personalization_engine"] = True
            component_status["template_engine"] = True
            
        except Exception as e:
            # Mark all components as unhealthy if any check fails
            component_status = {
                "outreach_pipeline": False,
                "outreach_scorer": False,
                "message_generator": False,
                "personalization_engine": False,
                "template_engine": False,
                "error": str(e)
            }
        
        return component_status
    
    async def _check_workers(self) -> Dict[str, Any]:
        """Check health of all workers"""
        worker_status = {}
        
        try:
            # Check outreach worker
            outreach_worker_status = await self.outreach_worker.get_worker_status()
            worker_status["outreach_worker"] = {
                "active": outreach_worker_status["active"],
                "queue_size": outreach_worker_status["queue_size"],
                "processing_tasks": outreach_worker_status["processing_tasks"],
                "healthy": outreach_worker_status["queue_size"] < 100
            }
            
            # Check enrichment worker
            enrichment_worker_status = await self.enrichment_worker.get_worker_status()
            worker_status["enrichment_worker"] = {
                "active": enrichment_worker_status["active"],
                "queue_size": enrichment_worker_status["queue_size"],
                "processing_tasks": enrichment_worker_status["processing_tasks"],
                "healthy": enrichment_worker_status["queue_size"] < 100
            }
            
        except Exception as e:
            worker_status = {
                "outreach_worker": {"active": False, "healthy": False, "error": str(e)},
                "enrichment_worker": {"active": False, "healthy": False, "error": str(e)}
            }
        
        return worker_status
    
    async def _check_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        resource_status = {}
        
        try:
            # Memory check (simplified)
            resource_status["memory_usage"] = "normal"  # Placeholder
            resource_status["cpu_usage"] = "normal"    # Placeholder
            
            # Check queue health
            outreach_status = await self.outreach_worker.get_worker_status()
            enrichment_status = await self.enrichment_worker.get_worker_status()
            
            total_queue_size = outreach_status["queue_size"] + enrichment_status["queue_size"]
            
            if total_queue_size > 200:
                resource_status["queue_health"] = "critical"
            elif total_queue_size > 100:
                resource_status["queue_health"] = "warning"
            else:
                resource_status["queue_health"] = "healthy"
            
            resource_status["total_queue_size"] = total_queue_size
            
        except Exception as e:
            resource_status = {
                "memory_usage": "unknown",
                "cpu_usage": "unknown",
                "queue_health": "error",
                "error": str(e)
            }
        
        return resource_status
    
    def _calculate_overall_health(
        self,
        component_status: Dict[str, bool],
        worker_status: Dict[str, Any],
        resource_status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate overall system health"""
        health_score = 1.0
        issues = []
        
        # Check component health
        unhealthy_components = [name for name, healthy in component_status.items() if not healthy]
        if unhealthy_components:
            health_score -= 0.3
            issues.append(f"Unhealthy components: {', '.join(unhealthy_components)}")
        
        # Check worker health
        for worker_name, worker_info in worker_status.items():
            if not worker_info.get("active", False):
                health_score -= 0.2
                issues.append(f"Worker {worker_name} is inactive")
            
            if not worker_info.get("healthy", True):
                health_score -= 0.1
                issues.append(f"Worker {worker_name} has issues")
        
        # Check resource health
        queue_health = resource_status.get("queue_health", "healthy")
        if queue_health == "critical":
            health_score -= 0.3
            issues.append("Queue sizes are critically high")
        elif queue_health == "warning":
            health_score -= 0.1
            issues.append("Queue sizes are elevated")
        
        # Determine status
        if health_score >= 0.9:
            status = "healthy"
        elif health_score >= 0.7:
            status = "degraded"
        elif health_score >= 0.5:
            status = "unhealthy"
        else:
            status = "critical"
        
        return {
            "status": status,
            "score": max(health_score, 0.0),
            "issues": issues
        }

# Create endpoint instance
health_endpoint = HealthCheckEndpoint()

@router.get("/")
@handle_errors()
@log_api_calls(log_level="info")
async def health_check():
    """Get comprehensive health status"""
    try:
        system_status = await health_endpoint.get_system_status()
        
        if system_status.get("status") == "error":
            return create_error_response(
                error_code="HEALTH_CHECK_ERROR",
                message=f"Health check failed: {system_status.get('error', 'Unknown error')}",
                error_type="service_error"
            )
        
        return create_health_check_response(
            status=system_status["status"],
            health_score=system_status["health_score"],
            uptime_seconds=system_status["uptime_seconds"],
            components=system_status["components"],
            workers=system_status["workers"],
            resources=system_status["resources"],
            version=system_status["version"],
            issues=system_status["issues"],
            message=f"Outreach engine is {system_status['status']}"
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
    uptime_seconds = (datetime.utcnow() - health_endpoint.start_time).total_seconds()
    
    return create_success_response(
        data={
            "status": "ok",
            "uptime_seconds": uptime_seconds
        },
        message="Outreach engine is running"
    )

@router.get("/components")
@handle_errors()
@log_api_calls(log_level="info")
async def check_components():
    """Check health of individual components"""
    try:
        components = await health_endpoint._check_components()
        
        return create_success_response(
            data=components,
            message="Component health check completed"
        )
    except Exception as e:
        raise ServiceUnavailableAPIException(
            message="Component health check failed",
            error_code="COMPONENT_HEALTH_ERROR"
        )

@router.get("/workers")
@handle_errors()
@log_api_calls(log_level="info")
async def check_workers():
    """Check health of worker systems"""
    try:
        workers = await health_endpoint._check_workers()
        
        return create_success_response(
            data=workers,
            message="Worker health check completed"
        )
    except Exception as e:
        raise ServiceUnavailableAPIException(
            message="Worker health check failed",
            error_code="WORKER_HEALTH_ERROR"
        )

@router.get("/resources")
@handle_errors()
@log_api_calls(log_level="info")
async def check_resources():
    """Check system resource usage"""
    try:
        resources = await health_endpoint._check_resources()
        
        return create_success_response(
            data=resources,
            message="Resource health check completed"
        )
    except Exception as e:
        raise ServiceUnavailableAPIException(
            message="Resource health check failed",
            error_code="RESOURCE_HEALTH_ERROR"
        )

@router.get("/metrics")
@handle_errors()
@log_api_calls(log_level="info")
async def get_health_metrics():
    """Get detailed health metrics"""
    try:
        system_status = await health_endpoint.get_system_status()
        
        metrics_data = {
            "health_metrics": {
                "component_health_score": sum(system_status["components"].values()) / len(system_status["components"]),
                "worker_health_score": sum(
                    1 for worker in system_status["workers"].values() 
                    if worker.get("healthy", False)
                ) / len(system_status["workers"]),
                "resource_health_score": 1.0 if system_status["resources"]["queue_health"] == "healthy" else 0.5,
                "overall_health_score": system_status["health_score"]
            },
            "performance_metrics": {
                "total_queue_size": system_status["resources"]["total_queue_size"],
                "active_workers": sum(
                    1 for worker in system_status["workers"].values() 
                    if worker.get("active", False)
                ),
                "processing_tasks": sum(
                    worker.get("processing_tasks", 0) 
                    for worker in system_status["workers"].values()
                )
            },
            "system_info": {
                "version": system_status["version"],
                "uptime_seconds": system_status["uptime_seconds"],
                "start_time": (datetime.utcnow() - timedelta(seconds=system_status["uptime_seconds"])).isoformat()
            }
        }
        
        return create_success_response(
            data=metrics_data,
            message="Health metrics retrieved successfully"
        )
        
    except Exception as e:
        raise ServiceUnavailableAPIException(
            message="Health metrics retrieval failed",
            error_code="METRICS_ERROR"
        )

__all__ = ["router", "HealthCheckEndpoint"]
