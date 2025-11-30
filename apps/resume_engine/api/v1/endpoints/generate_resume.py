"""
Resume Generation Endpoint
LEVEL 5 - Resume generation API endpoint implementation
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from ...schemas.resume_request import ResumeRequest
from ...schemas.resume_response import ResumeResponse
from ...services.generators.section_generator import SectionGenerator
from ...services.pipelines.resume_pipeline import ResumePipeline

router = APIRouter()

class ResumeGenerationEndpoint:
    """Handles resume generation requests with robust validation and processing"""
    
    def __init__(self):
        self.section_generator = SectionGenerator()
        self.resume_pipeline = ResumePipeline()
    
    async def generate_resume(
        self, 
        request: ResumeRequest
    ) -> ResumeResponse:
        """
        Generate a complete resume based on user input and job requirements
        
        Args:
            request: Resume generation request with user data and job info
            
        Returns:
            ResumeResponse: Generated resume with metadata
        """
        try:
            # Validate input data
            if not request.user_profile or not request.job_description:
                raise HTTPException(
                    status_code=400, 
                    detail="User profile and job description are required"
                )
            
            # Generate resume through pipeline
            result = await self.resume_pipeline.execute(request)
            
            return ResumeResponse(
                success=True,
                resume_content=result["resume_content"],
                metadata=result["metadata"],
                processing_time=result["processing_time"]
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Resume generation failed: {str(e)}"
            )

# Create endpoint instance
resume_endpoint = ResumeGenerationEndpoint()

@router.post("/generate", response_model=ResumeResponse)
async def generate_resume_endpoint(request: ResumeRequest):
    """Generate resume endpoint"""
    return await resume_endpoint.generate_resume(request)

__all__ = ["router", "ResumeGenerationEndpoint"]
