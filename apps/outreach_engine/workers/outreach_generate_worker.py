"""
Outreach Generation Worker
LEVEL 5 - Background worker for processing outreach generation tasks
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import uuid

from ..services.pipelines.outreach_pipeline import OutreachPipeline
from ..services.pipelines.validation_pipeline import ValidationPipeline

@dataclass
class OutreachTask:
    """Represents an outreach generation task"""
    task_id: str
    task_type: str
    recipient_profile: Dict[str, Any]
    sender_profile: Dict[str, Any]
    outreach_type: str
    context: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    priority: int = 1
    created_at: datetime = None
    status: str = "pending"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class OutreachTaskResult:
    """Result of outreach generation task"""
    task_id: str
    status: str
    outreach_content: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None
    quality_score: Optional[float] = None
    validation_result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    completed_at: datetime = None
    
    def __post_init__(self):
        if self.completed_at is None:
            self.completed_at = datetime.utcnow()

class OutreachGenerateWorker:
    """Background worker for processing outreach generation tasks"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize pipelines
        self.outreach_pipeline = OutreachPipeline()
        self.validation_pipeline = ValidationPipeline()
        
        # Worker configuration
        self.worker_config = {
            "max_concurrent_tasks": 5,
            "task_timeout": 300,  # 5 minutes
            "retry_attempts": 3,
            "retry_delay": 5,  # seconds
            "queue_size": 100
        }
        
        # Task management
        self.task_queue = asyncio.Queue(maxsize=self.worker_config["queue_size"])
        self.active_tasks = {}
        self.completed_tasks = {}
        self.task_results = {}
        
        # Worker state
        self.is_running = False
        self.worker_tasks = []
        self.stats = {
            "tasks_processed": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_processing_time": 0.0,
            "worker_start_time": None
        }
    
    async def start(self):
        """Start the outreach generation worker"""
        try:
            self.logger.info("Starting outreach generation worker")
            
            if self.is_running:
                self.logger.warning("Worker is already running")
                return
            
            self.is_running = True
            self.stats["worker_start_time"] = datetime.utcnow()
            
            # Start worker tasks
            for i in range(self.worker_config["max_concurrent_tasks"]):
                worker_task = asyncio.create_task(self._worker_loop(f"worker-{i}"))
                self.worker_tasks.append(worker_task)
            
            # Start cleanup task
            cleanup_task = asyncio.create_task(self._cleanup_loop())
            self.worker_tasks.append(cleanup_task)
            
            self.logger.info(f"Started {self.worker_config['max_concurrent_tasks']} worker tasks")
            
        except Exception as e:
            self.logger.error(f"Failed to start worker: {e}")
            raise e
    
    async def stop(self):
        """Stop the outreach generation worker"""
        try:
            self.logger.info("Stopping outreach generation worker")
            
            if not self.is_running:
                self.logger.warning("Worker is not running")
                return
            
            self.is_running = False
            
            # Cancel all worker tasks
            for task in self.worker_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
            
            self.logger.info("Worker stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping worker: {e}")
            raise e
    
    async def submit_task(self, task_data: Dict[str, Any]) -> str:
        """Submit a new outreach generation task"""
        try:
            # Create task
            task = OutreachTask(
                task_id=str(uuid.uuid4()),
                task_type=task_data.get("task_type", "outreach_generation"),
                recipient_profile=task_data["recipient_profile"],
                sender_profile=task_data["sender_profile"],
                outreach_type=task_data["outreach_type"],
                context=task_data.get("context"),
                preferences=task_data.get("preferences"),
                priority=task_data.get("priority", 1)
            )
            
            # Add to queue
            await self.task_queue.put(task)
            self.active_tasks[task.task_id] = task
            
            self.logger.info(f"Submitted task {task.task_id}")
            return task.task_id
            
        except Exception as e:
            self.logger.error(f"Failed to submit task: {e}")
            raise e
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        try:
            # Check active tasks
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                return {
                    "task_id": task.task_id,
                    "status": task.status,
                    "created_at": task.created_at.isoformat(),
                    "task_type": task.task_type
                }
            
            # Check completed results
            if task_id in self.task_results:
                result = self.task_results[task_id]
                return {
                    "task_id": result.task_id,
                    "status": result.status,
                    "completed_at": result.completed_at.isoformat(),
                    "quality_score": result.quality_score,
                    "processing_time": result.processing_time,
                    "error_message": result.error_message
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get task status: {e}")
            return None
    
    async def get_task_result(self, task_id: str) -> Optional[OutreachTaskResult]:
        """Get result of a specific task"""
        return self.task_results.get(task_id)
    
    async def get_worker_stats(self) -> Dict[str, Any]:
        """Get worker statistics"""
        uptime = None
        if self.stats["worker_start_time"]:
            uptime = (datetime.utcnow() - self.stats["worker_start_time"]).total_seconds()
        
        return {
            "is_running": self.is_running,
            "active_tasks": len(self.active_tasks),
            "queue_size": self.task_queue.qsize(),
            "completed_tasks": len(self.task_results),
            "stats": self.stats.copy(),
            "uptime_seconds": uptime,
            "worker_config": self.worker_config
        }
    
    async def _worker_loop(self, worker_name: str):
        """Main worker loop for processing tasks"""
        self.logger.info(f"Starting worker loop for {worker_name}")
        
        while self.is_running:
            try:
                # Get task from queue
                task = await asyncio.wait_for(
                    self.task_queue.get(), 
                    timeout=1.0
                )
                
                # Process task
                await self._process_task(task, worker_name)
                
            except asyncio.TimeoutError:
                # No task available, continue
                continue
            except Exception as e:
                self.logger.error(f"Worker {worker_name} error: {e}")
                await asyncio.sleep(1)
        
        self.logger.info(f"Worker loop {worker_name} stopped")
    
    async def _process_task(self, task: OutreachTask, worker_name: str):
        """Process a single outreach generation task"""
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"{worker_name} processing task {task.task_id}")
            
            # Update task status
            task.status = "processing"
            
            # Prepare request data for pipeline
            request_data = {
                "recipient_profile": task.recipient_profile,
                "sender_profile": task.sender_profile,
                "outreach_type": task.outreach_type,
                "context": task.context,
                "preferences": task.preferences
            }
            
            # Execute outreach pipeline
            pipeline_result = await self.outreach_pipeline.execute(request_data)
            
            # Validate the generated content
            validation_result = await self.validation_pipeline.validate_outreach(
                pipeline_result.outreach_content,
                task.context
            )
            
            # Create successful result
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = OutreachTaskResult(
                task_id=task.task_id,
                status="completed",
                outreach_content=pipeline_result.outreach_content,
                metadata=pipeline_result.metadata,
                quality_score=pipeline_result.quality_score,
                validation_result=asdict(validation_result),
                processing_time=processing_time
            )
            
            # Store result
            self.task_results[task.task_id] = result
            
            # Update stats
            self.stats["tasks_completed"] += 1
            self.stats["tasks_processed"] += 1
            self._update_average_processing_time(processing_time)
            
            # Remove from active tasks
            self.active_tasks.pop(task.task_id, None)
            
            self.logger.info(f"{worker_name} completed task {task.task_id} in {processing_time:.2f}s")
            
        except Exception as e:
            # Handle task failure
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            error_message = str(e)
            self.logger.error(f"{worker_name} failed task {task.task_id}: {error_message}")
            
            # Create failure result
            result = OutreachTaskResult(
                task_id=task.task_id,
                status="failed",
                error_message=error_message,
                processing_time=processing_time
            )
            
            # Store result
            self.task_results[task.task_id] = result
            
            # Update stats
            self.stats["tasks_failed"] += 1
            self.stats["tasks_processed"] += 1
            
            # Remove from active tasks
            self.active_tasks.pop(task.task_id, None)
    
    async def _cleanup_loop(self):
        """Cleanup loop for removing old task results"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # Remove results older than 24 hours
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                
                old_task_ids = [
                    task_id for task_id, result in self.task_results.items()
                    if result.completed_at < cutoff_time
                ]
                
                for task_id in old_task_ids:
                    self.task_results.pop(task_id, None)
                
                if old_task_ids:
                    self.logger.info(f"Cleaned up {len(old_task_ids)} old task results")
                
            except Exception as e:
                self.logger.error(f"Cleanup loop error: {e}")
    
    def _update_average_processing_time(self, processing_time: float):
        """Update average processing time statistic"""
        if self.stats["tasks_processed"] == 1:
            self.stats["average_processing_time"] = processing_time
        else:
            current_avg = self.stats["average_processing_time"]
            n = self.stats["tasks_processed"]
            self.stats["average_processing_time"] = ((current_avg * (n - 1)) + processing_time) / n
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task"""
        try:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                if task.status == "pending":
                    # Mark as cancelled
                    task.status = "cancelled"
                    
                    # Create cancellation result
                    result = OutreachTaskResult(
                        task_id=task.task_id,
                        status="cancelled",
                        error_message="Task was cancelled by user"
                    )
                    
                    self.task_results[task.task_id] = result
                    self.active_tasks.pop(task_id, None)
                    
                    self.logger.info(f"Cancelled task {task_id}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to cancel task {task_id}: {e}")
            return False
    
    async def retry_task(self, task_id: str) -> Optional[str]:
        """Retry a failed task"""
        try:
            # Get original result
            original_result = self.task_results.get(task_id)
            if not original_result or original_result.status != "failed":
                return None
            
            # Get original task data (simplified - in production, store full task)
            original_task = self.completed_tasks.get(task_id)
            if not original_task:
                return None
            
            # Create new task with same data
            new_task_data = {
                "task_type": original_task.task_type,
                "recipient_profile": original_task.recipient_profile,
                "sender_profile": original_task.sender_profile,
                "outreach_type": original_task.outreach_type,
                "context": original_task.context,
                "preferences": original_task.preferences,
                "priority": original_task.priority
            }
            
            # Submit new task
            new_task_id = await self.submit_task(new_task_data)
            
            self.logger.info(f"Retried task {task_id} as {new_task_id}")
            return new_task_id
            
        except Exception as e:
            self.logger.error(f"Failed to retry task {task_id}: {e}")
            return None

# Global worker instance
outreach_worker = OutreachGenerateWorker()

__all__ = [
    "OutreachGenerateWorker",
    "OutreachTask", 
    "OutreachTaskResult",
    "outreach_worker"
]
