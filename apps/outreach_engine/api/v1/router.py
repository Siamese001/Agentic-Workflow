"""
Outreach Engine API v1 Router
LEVEL 4 - API routing configuration for outreach communication endpoints
"""

from fastapi import APIRouter
from .endpoints import send_outreach, preview_message, healthcheck

# Outreach Engine API Router
router = APIRouter(prefix="/outreach", tags=["outreach"])

# Include all outreach engine endpoints
router.include_router(send_outreach.router, prefix="/send", tags=["outreach-sending"])
router.include_router(preview_message.router, prefix="/preview", tags=["outreach-preview"])
router.include_router(healthcheck.router, prefix="/health", tags=["health"])

__all__ = ["router"]
