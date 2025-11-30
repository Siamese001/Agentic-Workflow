"""
Outreach Generation Endpoint
LEVEL 5 - API endpoint for generating personalized outreach messages
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

from ...services.pipelines.outreach_pipeline import OutreachPipeline
from ...services.utils.scoring import OutreachScorer
from ...workers.outreach_generate_worker import OutreachGenerateWorker, OutreachGenerateTask

router = APIRouter(prefix="/outreach", tags=["outreach"])

# Initialize services
outreach_pipeline = OutreachPipeline()
outreach_scorer = OutreachScorer()
outreach_worker = OutreachGenerateWorker()

class OutreachGenerationEndpoint:
    """Handles outreach message generation requests"""
    
    def __init__(self):
        self.pipeline = outreach_pipeline
        self.scorer = outreach_scorer
        self.worker = outreach_worker
    
    async def generate_outreach_message(
        self,
        request: Dict[str, Any],
        background_tasks: BackgroundTasks,
        priority: int = 2
    ) -> Dict[str, Any]:
        """
        Generate personalized outreach message
        
        Args:
            request: Outreach generation request
            background_tasks: FastAPI background tasks
            priority: Processing priority (1=high, 2=medium, 3=low)
            
        Returns:
            Generated outreach message with metadata
        """
        try:
            # Validate request
            validation_result = await self._validate_request(request)
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid request: {validation_result['error']}"
                )
            
            # Check if async processing is requested
            if request.get("async_processing", False):
                return await self._generate_async(request, background_tasks, priority)
            
            # Generate message synchronously
            result = await self._generate_sync(request)
            
            return {
                "success": True,
                "outreach_content": result["content"],
                "metadata": result["metadata"],
                "processing_time": result["processing_time"],
                "quality_score": result["quality_score"],
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate outreach message: {str(e)}"
            )
    
    async def _validate_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate outreach generation request"""
        required_fields = ["recipient_profile", "sender_profile", "outreach_type"]
        
        for field in required_fields:
            if field not in request:
                return {
                    "valid": False,
                    "error": f"Missing required field: {field}"
                }
        
        recipient = request.get("recipient_profile", {})
        sender = request.get("sender_profile", {})
        
        # Validate recipient profile
        if not recipient.get("name") or not recipient.get("company"):
            return {
                "valid": False,
                "error": "Recipient profile must include name and company"
            }
        
        # Validate sender profile
        if not sender.get("name") or not sender.get("role"):
            return {
                "valid": False,
                "error": "Sender profile must include name and role"
            }
        
        # Validate outreach type
        valid_types = ["email", "linkedin", "cold_call", "follow_up", "networking"]
        if request.get("outreach_type") not in valid_types:
            return {
                "valid": False,
                "error": f"Invalid outreach type. Must be one of: {valid_types}"
            }
        
        return {"valid": True}
    
    async def _generate_sync(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate outreach message synchronously"""
        # Execute outreach pipeline
        pipeline_result = await self.pipeline.execute(
            {
                "recipient_profile": request["recipient_profile"],
                "sender_profile": request["sender_profile"],
                "outreach_type": request["outreach_type"],
                "context": request.get("context", {}),
                "preferences": request.get("preferences", {})
            }
        )
        
        return {
            "content": pipeline_result.outreach_content,
            "metadata": pipeline_result.metadata,
            "processing_time": pipeline_result.processing_time,
            "quality_score": pipeline_result.quality_score
        }
    
    async def _generate_async(
        self,
        request: Dict[str, Any],
        background_tasks: BackgroundTasks,
        priority: int
    ) -> Dict[str, Any]:
        """Generate outreach message asynchronously"""
        # Create task for background processing
        task = OutreachGenerateTask(
            task_id=f"outreach_{datetime.utcnow().timestamp()}",
            user_id=request.get("user_id", "anonymous"),
            recipient_profile=request["recipient_profile"],
            sender_profile=request["sender_profile"],
            outreach_type=request["outreach_type"],
            context=request.get("context", {}),
            preferences=request.get("preferences", {}),
            priority=priority
        )
        
        # Add task to worker queue
        task_added = await self.worker.add_outreach_task(task)
        if not task_added:
            raise HTTPException(
                status_code=503,
                detail="Failed to queue outreach generation task"
            )
        
        # Add background task to monitor completion
        background_tasks.add_task(self._monitor_task_completion, task.task_id)
        
        return {
            "success": True,
            "task_id": task.task_id,
            "status": "queued",
            "message": "Outreach message generation started",
            "estimated_completion": "2-5 minutes",
            "task_url": f"/outreach/tasks/{task.task_id}"
        }
    
    async def _monitor_task_completion(self, task_id: str):
        """Monitor async task completion"""
        max_wait_time = 600  # 10 minutes
        start_time = datetime.utcnow()
        
        while True:
            # Check task status
            task_status = await self.worker.get_task_status(task_id)
            
            if task_status and task_status.get("status") in ["completed", "failed"]:
                break
            
            # Check timeout
            if (datetime.utcnow() - start_time).total_seconds() > max_wait_time:
                break
            
            await asyncio.sleep(30)  # Check every 30 seconds

# Create endpoint instance
outreach_endpoint = OutreachGenerationEndpoint()

@router.post("/generate")
async def generate_outreach(
    request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    priority: int = 2
):
    """Generate personalized outreach message"""
    return await outreach_endpoint.generate_outreach_message(request, background_tasks, priority)

@router.get("/tasks/{task_id}")
async def get_outreach_task_status(task_id: str):
    """Get status of outreach generation task"""
    task_status = await outreach_worker.get_task_status(task_id)
    
    if not task_status:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )
    
    return {
        "task_id": task_id,
        "status": task_status.get("status"),
        "created_at": task_status.get("created_at"),
        "started_at": task_status.get("started_at"),
        "completed_at": task_status.get("completed_at"),
        "error": task_status.get("error")
    }

@router.get("/tasks/{task_id}/result")
async def get_outreach_task_result(task_id: str):
    """Get result of completed outreach generation task"""
    task_status = await outreach_worker.get_task_status(task_id)
    
    if not task_status:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )
    
    if task_status.get("status") != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Task {task_id} not completed yet"
        )
    
    result = task_status.get("result", {})
    
    return {
        "task_id": task_id,
        "success": True,
        "outreach_content": result.get("outreach_content"),
        "metadata": result.get("metadata"),
        "quality_score": result.get("quality_score"),
        "processing_time": result.get("processing_time"),
        "completed_at": task_status.get("completed_at")
    }

__all__ = ["router", "OutreachGenerationEndpoint"]
