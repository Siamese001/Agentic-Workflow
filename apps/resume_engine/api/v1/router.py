"""
Resume Engine API v1 Router
LEVEL 4 - API routing configuration for resume generation endpoints
"""

from fastapi import APIRouter
from .endpoints import generate_resume, validate_resume, healthcheck

# Resume Engine API Router
router = APIRouter(prefix="/resume", tags=["resume"])

# Include all resume engine endpoints
router.include_router(generate_resume.router, prefix="/generate", tags=["resume-generation"])
router.include_router(validate_resume.router, prefix="/validate", tags=["resume-validation"])
router.include_router(healthcheck.router, prefix="/health", tags=["health"])

__all__ = ["router"]
