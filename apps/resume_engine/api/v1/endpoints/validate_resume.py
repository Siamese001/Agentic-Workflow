"""
Resume Validation Endpoint
LEVEL 5 - Resume validation and scoring API endpoint
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from ...schemas.resume_request import ResumeRequest
from ...schemas.resume_response import ResumeResponse
from ...services.utils.scoring import ResumeScorer
from ...services.pipelines.validation_pipeline import ValidationPipeline

router = APIRouter()

class ResumeValidationEndpoint:
    """Handles resume validation with ATS optimization checks"""
    
    def __init__(self):
        self.resume_scorer = ResumeScorer()
        self.validation_pipeline = ValidationPipeline()
    
    async def validate_resume(
        self, 
        request: ResumeRequest
    ) -> ResumeResponse:
        """
        Validate resume content and provide optimization recommendations
        
        Args:
            request: Resume validation request with current content
            
        Returns:
            ResumeResponse: Validation results with scoring and recommendations
        """
        try:
            # Perform ATS validation
            ats_score = await self.resume_scorer.calculate_ats_score(request.resume_content)
            
            # Run validation pipeline
            validation_results = await self.validation_pipeline.validate(request)
            
            return ResumeResponse(
                success=True,
                resume_content=request.resume_content,
                metadata={
                    "ats_score": ats_score,
                    "validation_results": validation_results,
                    "recommendations": validation_results.get("recommendations", [])
                },
                processing_time=validation_results.get("processing_time", 0)
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Resume validation failed: {str(e)}"
            )

@router.post("/validate", response_model=ResumeResponse)
async def validate_resume_endpoint(request: ResumeRequest):
    """Validate resume endpoint"""
    validator = ResumeValidationEndpoint()
    return await validator.validate_resume(request)

__all__ = ["router", "ResumeValidationEndpoint"]
