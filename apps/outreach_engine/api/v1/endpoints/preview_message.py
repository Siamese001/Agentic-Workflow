"""
Outreach Engine - Preview Message Endpoint
LEVEL 5 - API endpoint for previewing outreach messages before sending
"""

import sys
from pathlib import Path

# Add project root to Python path for shared API imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import APIRouter
from typing import Dict, Any, List
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

from ...services.planners.message_planner import MessagePlanner
from ...services.generators.outreach_generator import OutreachGenerator
from ...services.generators.personalization_engine import PersonalizationEngine

router = APIRouter(prefix="/preview", tags=["preview"])

# Initialize services
message_planner = MessagePlanner()
outreach_generator = OutreachGenerator()
personalization_engine = PersonalizationEngine()

class PreviewRequest(BaseRequest):
    """Request model for message preview"""
    recipient_id: str
    recipient_type: str  # "linkedin" or "email"
    message_type: str    # "connection_request", "follow_up", "cold_outreach"
    template_id: str
    personalization_data: Dict[str, Any]
    include_personalization_notes: bool = True

class PreviewResponse(BaseRequest):
    """Response model for message preview"""
    preview_id: str
    message_content: str
    personalization_notes: List[str]
    template_used: str
    personalization_score: float
    generated_at: str

class PreviewEndpoint:
    """Handles message preview operations"""
    
    def __init__(self):
        self.message_planner = message_planner
        self.outreach_generator = outreach_generator
        self.personalization_engine = personalization_engine
    
    async def generate_preview(self, request: PreviewRequest) -> Dict[str, Any]:
        """Generate a preview of the outreach message"""
        try:
            # Plan the message
            message_plan = await self.message_planner.plan_message(
                recipient_id=request.recipient_id,
                message_type=request.message_type,
                template_id=request.template_id,
                personalization_data=request.personalization_data
            )
            
            # Generate the message content
            message_content = await self.outreach_generator.generate_message(
                plan=message_plan,
                personalization_data=request.personalization_data
            )
            
            # Apply personalization and get notes
            personalization_result = await self.personalization_engine.personalize_with_notes(
                content=message_content,
                recipient_data=request.personalization_data,
                include_notes=request.include_personalization_notes
            )
            
            personalized_content = personalization_result["content"]
            personalization_notes = personalization_result.get("notes", [])
            personalization_score = personalization_result.get("score", 0.8)
            
            # Create preview record
            preview_id = f"preview_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            return {
                "preview_id": preview_id,
                "message_content": personalized_content,
                "personalization_notes": personalization_notes,
                "template_used": request.template_id,
                "personalization_score": personalization_score,
                "generated_at": datetime.utcnow().isoformat(),
                "message_type": request.message_type,
                "recipient_type": request.recipient_type
            }
            
        except Exception as e:
            raise ServiceUnavailableAPIException(
                message=f"Failed to generate message preview: {str(e)}",
                error_code="PREVIEW_GENERATION_FAILED"
            )

# Create endpoint instance
preview_endpoint = PreviewEndpoint()

def validate_preview_request(request: PreviewRequest) -> None:
    """Validate preview request"""
    errors = []
    
    if not request.recipient_id or len(request.recipient_id.strip()) < 3:
        errors.append({"field": "recipient_id", "message": "Valid recipient ID is required"})
    
    if request.recipient_type not in ["linkedin", "email"]:
        errors.append({"field": "recipient_type", "message": "Must be 'linkedin' or 'email'"})
    
    if not request.message_type:
        errors.append({"field": "message_type", "message": "Message type is required"})
    
    if not request.template_id:
        errors.append({"field": "template_id", "message": "Template ID is required"})
    
    if not request.personalization_data:
        errors.append({"field": "personalization_data", "message": "Personalization data is required"})
    
    if errors:
        raise ValidationAPIException(
            message="Preview request validation failed",
            validation_errors=errors
        )

@router.post("/generate")
@rate_limit(requests_per_minute=30)  # Higher limit for previews
@validate_request(validate_preview_request)
@handle_errors()
@log_api_calls(log_level="info")
async def generate_preview(request: PreviewRequest):
    """Generate a preview of an outreach message"""
    try:
        result = await preview_endpoint.generate_preview(request)
        
        return create_success_response(
            data=result,
            message="Message preview generated successfully"
        )
        
    except ValidationAPIException as e:
        raise e
    except ServiceUnavailableAPIException as e:
        raise e
    except Exception as e:
        raise ServiceUnavailableAPIException(
            message="Preview service temporarily unavailable",
            error_code="PREVIEW_SERVICE_ERROR"
        )

@router.post("/compare")
@rate_limit(requests_per_minute=20)
@handle_errors()
@log_api_calls(log_level="info")
async def compare_templates(request: PreviewRequest):
    """Compare message preview with different templates"""
    try:
        # Get available templates for the message type
        available_templates = await message_planner.get_templates_for_type(request.message_type)
        
        comparisons = []
        
        for template_id in available_templates[:3]:  # Limit to 3 templates for comparison
            comparison_request = PreviewRequest(
                **request.dict(),
                template_id=template_id
            )
            
            preview_result = await preview_endpoint.generate_preview(comparison_request)
            
            comparisons.append({
                "template_id": template_id,
                "preview_id": preview_result["preview_id"],
                "message_content": preview_result["message_content"],
                "personalization_score": preview_result["personalization_score"],
                "personalization_notes": preview_result["personalization_notes"]
            })
        
        # Sort by personalization score
        comparisons.sort(key=lambda x: x["personalization_score"], reverse=True)
        
        return create_success_response(
            data={
                "comparisons": comparisons,
                "recommended_template": comparisons[0]["template_id"] if comparisons else None,
                "comparison_summary": {
                    "total_templates": len(comparisons),
                    "best_score": comparisons[0]["personalization_score"] if comparisons else 0,
                    "score_range": {
                        "min": min(c["personalization_score"] for c in comparisons) if comparisons else 0,
                        "max": max(c["personalization_score"] for c in comparisons) if comparisons else 0
                    }
                }
            },
            message="Template comparison completed successfully"
        )
        
    except Exception as e:
        raise ServiceUnavailableAPIException(
            message="Template comparison failed",
            error_code="COMPARISON_ERROR"
        )

@router.get("/templates/{message_type}")
@handle_errors()
@log_api_calls(log_level="info")
async def get_templates_for_type(message_type: str):
    """Get available templates for a specific message type"""
    try:
        if not message_type:
            raise ValidationAPIException(
                message="Message type is required",
                validation_errors=[{
                    "field": "message_type",
                    "message": "Message type cannot be empty"
                }]
            )
        
        templates = await message_planner.get_templates_for_type(message_type)
        
        if not templates:
            return create_success_response(
                data=[],
                message=f"No templates found for message type: {message_type}"
            )
        
        # Get template details
        template_details = []
        for template_id in templates:
            template_info = await message_planner.get_template_info(template_id)
            template_details.append({
                "template_id": template_id,
                "name": template_info.get("name", template_id),
                "description": template_info.get("description", ""),
                "message_type": template_info.get("message_type", message_type),
                "personalization_fields": template_info.get("personalization_fields", []),
                "usage_count": template_info.get("usage_count", 0)
            })
        
        return create_success_response(
            data=template_details,
            message=f"Retrieved {len(template_details)} templates for {message_type}"
        )
        
    except ValidationAPIException as e:
        raise e
    except Exception as e:
        raise ServiceUnavailableAPIException(
            message="Failed to retrieve templates",
            error_code="TEMPLATE_RETRIEVAL_ERROR"
        )

@router.get("/history/{recipient_id}")
@rate_limit(requests_per_minute=60)
@handle_errors()
@log_api_calls(log_level="info")
async def get_preview_history(recipient_id: str):
    """Get preview history for a recipient"""
    try:
        if not recipient_id or len(recipient_id.strip()) < 3:
            raise ValidationAPIException(
                message="Valid recipient ID is required",
                validation_errors=[{
                    "field": "recipient_id",
                    "message": "Recipient ID must be at least 3 characters"
                }]
            )
        
        # Mock history data - in real implementation would query database
        preview_history = [
            {
                "preview_id": "preview_20251130_120000",
                "message_type": "connection_request",
                "template_id": "linkedin_connection_v1",
                "personalization_score": 0.85,
                "generated_at": "2025-11-30T12:00:00Z",
                "status": "sent"
            },
            {
                "preview_id": "preview_20251130_110000",
                "message_type": "follow_up",
                "template_id": "follow_up_v2",
                "personalization_score": 0.78,
                "generated_at": "2025-11-30T11:00:00Z",
                "status": "previewed"
            }
        ]
        
        return create_success_response(
            data=preview_history,
            message=f"Retrieved {len(preview_history)} preview records"
        )
        
    except ValidationAPIException as e:
        raise e
    except Exception as e:
        raise ServiceUnavailableAPIException(
            message="Failed to retrieve preview history",
            error_code="HISTORY_RETRIEVAL_ERROR"
        )

__all__ = ["router", "PreviewEndpoint", "PreviewRequest", "PreviewResponse"]
