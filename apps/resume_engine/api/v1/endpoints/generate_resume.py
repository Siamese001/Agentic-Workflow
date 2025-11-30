"""
Resume Generation Endpoint
LEVEL 5 - Resume generation API endpoint implementation
"""

import sys
from pathlib import Path

# Add project root to Python path for shared API imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime

# Import shared API components from framework layer
from agentic_core.api import (
    BaseRequest,
    create_success_response,
    create_error_response,
    create_validation_response,
    handle_errors,
    log_api_calls,
    rate_limit,
    validate_request,
    APIException,
    ValidationAPIException,
    ServiceUnavailableAPIException
)

# Import resume engine schemas and services (with error handling)
try:
    from ...schemas.resume_request import ResumeRequest
    from ...schemas.resume_response import ResumeResponse
    SCHEMAS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import resume schemas: {e}")
    SCHEMAS_AVAILABLE = False
    # Create fallback request/response models
    class ResumeRequest(BaseRequest):
        user_profile: Dict[str, Any]
        job_description: str
    
    class ResumeResponse(BaseRequest):
        success: bool
        resume_content: Dict[str, Any]
        metadata: Dict[str, Any]
        processing_time: float

try:
    from ...services.generators.section_generator import SectionGenerator
    from ...services.pipelines.resume_pipeline import ResumePipeline
    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import resume engine services: {e}")
    SERVICES_AVAILABLE = False
    SectionGenerator = None
    ResumePipeline = None

router = APIRouter()

class ResumeGenerationEndpoint:
    """Handles resume generation requests with robust validation and processing"""
    
    def __init__(self):
        if SERVICES_AVAILABLE:
            self.section_generator = SectionGenerator()
            self.resume_pipeline = ResumePipeline()
        else:
            self.section_generator = None
            self.resume_pipeline = None
    
    async def generate_resume(
        self, 
        request: ResumeRequest
    ) -> Dict[str, Any]:
        """
        Generate a complete resume based on user input and job requirements
        
        Args:
            request: Resume generation request with user data and job info
            
        Returns:
            Dict containing generated resume with metadata
        """
        try:
            if not SERVICES_AVAILABLE:
                raise ServiceUnavailableAPIException(
                    message="Resume generation services not available",
                    error_code="SERVICES_UNAVAILABLE"
                )
            
            # Validate input data
            if not request.user_profile or not request.job_description:
                raise ValidationAPIException(
                    message="User profile and job description are required",
                    validation_errors=[
                        {"field": "user_profile", "message": "User profile is required"},
                        {"field": "job_description", "message": "Job description is required"}
                    ]
                )
            
            # Generate resume through pipeline
            result = await self.resume_pipeline.execute(request)
            
            return {
                "success": True,
                "resume_content": result["resume_content"],
                "metadata": result["metadata"],
                "processing_time": result["processing_time"],
                "resume_id": f"resume_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            }
            
        except ValidationAPIException as e:
            raise e
        except Exception as e:
            raise ServiceUnavailableAPIException(
                message=f"Resume generation failed: {str(e)}",
                error_code="RESUME_GENERATION_FAILED"
            )

# Create endpoint instance
resume_endpoint = ResumeGenerationEndpoint()

def validate_resume_request(request: ResumeRequest) -> None:
    """Validate resume generation request"""
    errors = []
    
    if not request.user_profile:
        errors.append({"field": "user_profile", "message": "User profile is required"})
    elif not isinstance(request.user_profile, dict):
        errors.append({"field": "user_profile", "message": "User profile must be a dictionary"})
    
    if not request.job_description:
        errors.append({"field": "job_description", "message": "Job description is required"})
    elif not isinstance(request.job_description, str):
        errors.append({"field": "job_description", "message": "Job description must be a string"})
    
    if errors:
        raise ValidationAPIException(
            message="Resume generation request validation failed",
            validation_errors=errors
        )

@router.post("/generate")
@rate_limit(requests_per_minute=5)  # Limit expensive generation operations
@validate_request(validate_resume_request)
@handle_errors()
@log_api_calls(log_level="info")
async def generate_resume_endpoint(request: ResumeRequest):
    """Generate resume endpoint"""
    try:
        result = await resume_endpoint.generate_resume(request)
        
        return create_success_response(
            data=result,
            message="Resume generated successfully"
        )
        
    except ValidationAPIException as e:
        raise e
    except ServiceUnavailableAPIException as e:
        raise e
    except Exception as e:
        raise ServiceUnavailableAPIException(
            message="Resume generation service temporarily unavailable",
            error_code="GENERATION_SERVICE_ERROR"
        )

__all__ = ["router", "ResumeGenerationEndpoint"]
