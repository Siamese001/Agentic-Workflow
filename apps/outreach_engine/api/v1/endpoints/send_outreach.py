"""
Outreach Engine - Send Outreach Endpoint
LEVEL 5 - API endpoint for sending outreach messages
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
    handle_errors,
    log_api_calls,
    rate_limit,
    validate_request,
    ValidationAPIException,
    NotFoundAPIException,
    ServiceUnavailableAPIException
)

from ...services.planners.message_planner import MessagePlanner
from ...services.generators.outreach_generator import OutreachGenerator
from ...services.generators.personalization_engine import PersonalizationEngine
from ...workers.linkedin_send_worker import LinkedInSendWorker
from ...workers.email_send_worker import EmailSendWorker

router = APIRouter(prefix="/outreach", tags=["outreach"])

# Initialize services
message_planner = MessagePlanner()
outreach_generator = OutreachGenerator()
personalization_engine = PersonalizationEngine()
linkedin_worker = LinkedInSendWorker()
email_worker = EmailSendWorker()

class OutreachRequest(BaseRequest):
    """Request model for sending outreach messages"""
    recipient_id: str
    recipient_type: str  # "linkedin" or "email"
    message_type: str    # "connection_request", "follow_up", "cold_outreach"
    template_id: str
    personalization_data: Dict[str, Any]
    send_immediately: bool = True
    scheduled_time: str = None

class OutreachResponse(BaseRequest):
    """Response model for outreach operations"""
    outreach_id: str
    status: str
    message_content: str
    delivery_status: str
    sent_at: str

class OutreachEndpoint:
    """Handles outreach message sending operations"""

    def __init__(self):
        self.message_planner = message_planner
        self.outreach_generator = outreach_generator
        self.personalization_engine = personalization_engine
        self.linkedin_worker = linkedin_worker
        self.email_worker = email_worker

    async def send_outreach_message(self, request: OutreachRequest) -> Dict[str, Any]:
        """Send an outreach message"""
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

            # Apply personalization
            personalized_content = await self.personalization_engine.personalize(
                content=message_content,
                recipient_data=request.personalization_data
            )

            # Send the message
            if request.recipient_type == "linkedin":
                delivery_result = await self.linkedin_worker.send_message(
                    recipient_id=request.recipient_id,
                    content=personalized_content
                )
            elif request.recipient_type == "email":
                delivery_result = await self.email_worker.send_message(
                    recipient_id=request.recipient_id,
                    content=personalized_content
                )
            else:
                raise ValidationAPIException(
                    message="Invalid recipient type",
                    validation_errors=[{
                        "field": "recipient_type",
                        "message": "Must be 'linkedin' or 'email'"
                    }]
                )

            # Create outreach record
            outreach_id = f"outreach_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

            return {
                "outreach_id": outreach_id,
                "status": "sent" if delivery_result["success"] else "failed",
                "message_content": personalized_content,
                "delivery_status": delivery_result["status"],
                "sent_at": datetime.utcnow().isoformat(),
                "delivery_details": delivery_result
            }

        except Exception as e:
            raise ServiceUnavailableAPIException(
                message=f"Failed to send outreach message: {str(e)}",
                error_code="OUTREACH_SEND_FAILED"
            )

# Create endpoint instance
outreach_endpoint = OutreachEndpoint()

def validate_outreach_request(request: OutreachRequest) -> None:
    """Validate outreach request"""
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
            message="Outreach request validation failed",
            validation_errors=errors
        )

@router.post("/send")
@rate_limit(requests_per_minute=10)  # Limit outreach sending
@validate_request(validate_outreach_request)
@handle_errors()
@log_api_calls(log_level="info")
async def send_outreach(request: OutreachRequest):
    """Send an outreach message"""
    try:
        result = await outreach_endpoint.send_outreach_message(request)

        return create_success_response(
            data=result,
            message="Outreach message sent successfully"
        )

    except ValidationAPIException as e:
        raise e
    except ServiceUnavailableAPIException as e:
        raise e
    except Exception:
        raise ServiceUnavailableAPIException(
            message="Outreach service temporarily unavailable",
            error_code="OUTREACH_SERVICE_ERROR"
        )

@router.get("/status/{outreach_id}")
@handle_errors()
@log_api_calls(log_level="info")
async def get_outreach_status(outreach_id: str):
    """Get status of a specific outreach message"""
    try:
        # Mock status check - in real implementation would query database
        if not outreach_id or outreach_id == "invalid":
            raise NotFoundAPIException(
                message="Outreach message not found",
                error_code="OUTREACH_NOT_FOUND"
            )

        # Mock status data
        status_data = {
            "outreach_id": outreach_id,
            "status": "delivered",
            "delivery_status": "success",
            "sent_at": "2025-11-30T12:00:00Z",
            "delivered_at": "2025-11-30T12:01:00Z",
            "recipient_engagement": "opened"
        }

        return create_success_response(
            data=status_data,
            message="Outreach status retrieved successfully"
        )

    except NotFoundAPIException as e:
        raise e
    except Exception:
        raise ServiceUnavailableAPIException(
            message="Status check failed",
            error_code="STATUS_CHECK_ERROR"
        )

@router.get("/list")
@handle_errors()
@log_api_calls(log_level="info")
async def list_outreach():
    """List recent outreach messages"""
    try:
        # Mock list data - in real implementation would query database
        outreach_list = [
            {
                "outreach_id": "outreach_20251130_120000",
                "recipient_id": "user_123",
                "recipient_type": "linkedin",
                "message_type": "connection_request",
                "status": "delivered",
                "sent_at": "2025-11-30T12:00:00Z"
            },
            {
                "outreach_id": "outreach_20251130_115000",
                "recipient_id": "user_456",
                "recipient_type": "email",
                "message_type": "follow_up",
                "status": "sent",
                "sent_at": "2025-11-30T11:50:00Z"
            }
        ]

        return create_success_response(
            data=outreach_list,
            message="Outreach list retrieved successfully"
        )

    except Exception:
        raise ServiceUnavailableAPIException(
            message="Failed to retrieve outreach list",
            error_code="OUTREACH_LIST_ERROR"
        )

__all__ = ["router", "OutreachEndpoint", "OutreachRequest", "OutreachResponse"]
