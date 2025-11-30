"""
Resume Generate Worker
LEVEL 5 - Background job processing for resume generation tasks
"""

from typing import Dict, List, Any, Optional
import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from ..services.pipelines.resume_pipeline import ResumePipeline

@dataclass
class ResumeGenerateTask:
    """Resume generation task data structure"""
    task_id: str
    user_id: str
    user_profile: Dict[str, Any]
    job_description: Dict[str, Any]
    preferences: Dict[str, Any]
    priority: int = 1
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class ResumeGenerateWorker:
    """Background worker for processing resume generation tasks"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.task_queue = asyncio.Queue()
        self.processing_tasks = {}
        self.max_concurrent_tasks = 3
        self.worker_active = False
        self.resume_pipeline = ResumePipeline()
        
        # Task priority configurations
        self.priority_configs = {
            1: {"max_wait_time": 300, "retry_count": 3},  # High priority
            2: {"max_wait_time": 600, "retry_count": 2},  # Medium priority
            3: {"max_wait_time": 1200, "retry_count": 1}  # Low priority
        }
    
    async def start_worker(self):
        """Start the background worker"""
        if self.worker_active:
            self.logger.warning("Resume generate worker is already active")
            return
        
        self.worker_active = True
        self.logger.info("Starting resume generate worker")
        
        # Start worker tasks
        worker_tasks = [
            asyncio.create_task(self._process_tasks())
            for _ in range(self.max_concurrent_tasks)
        ]
        
        # Start maintenance task
        maintenance_task = asyncio.create_task(self._maintenance_loop())
        
        try:
            await asyncio.gather(*worker_tasks, maintenance_task)
        except Exception as e:
            self.logger.error(f"Worker error: {e}")
        finally:
            self.worker_active = False
    
    async def stop_worker(self):
        """Stop the background worker"""
        self.worker_active = False
        self.logger.info("Stopping resume generate worker")
    
    async def add_resume_task(self, task: ResumeGenerateTask) -> bool:
        """Add a resume generation task to the queue"""
        try:
            await self.task_queue.put(task)
            self.logger.info(f"Added resume task: {task.task_id} for user {task.user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add resume task: {e}")
            return False
    
    async def get_worker_status(self) -> Dict[str, Any]:
        """Get current worker status"""
        return {
            "active": self.worker_active,
            "queue_size": self.task_queue.qsize(),
            "processing_tasks": len(self.processing_tasks),
            "max_concurrent": self.max_concurrent_tasks,
            "pipeline_status": await self.resume_pipeline.get_pipeline_status()
        }
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific task"""
        if task_id in self.processing_tasks:
            task_info = self.processing_tasks[task_id].copy()
            # Remove the actual task data to avoid large responses
            task_info.pop("task", None)
            return task_info
        return None
    
    async def _process_tasks(self):
        """Main task processing loop"""
        while self.worker_active:
            try:
                # Wait for task with timeout
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                
                # Process the task
                await self._process_single_task(task)
                
            except asyncio.TimeoutError:
                # No task available, continue
                continue
            except Exception as e:
                self.logger.error(f"Task processing error: {e}")
    
    async def _process_single_task(self, task: ResumeGenerateTask):
        """Process a single resume generation task"""
        task_id = task.task_id
        priority_config = self.priority_configs.get(task.priority, self.priority_configs[2])
        
        self.processing_tasks[task_id] = {
            "task": task,
            "started_at": datetime.utcnow(),
            "status": "processing",
            "retry_count": 0
        }
        
        try:
            self.logger.info(f"Processing resume task: {task_id}")
            
            # Process with timeout
            result = await asyncio.wait_for(
                self._generate_resume(task),
                timeout=priority_config["max_wait_time"]
            )
            
            # Update task status
            self.processing_tasks[task_id]["status"] = "completed"
            self.processing_tasks[task_id]["completed_at"] = datetime.utcnow()
            self.processing_tasks[task_id]["result"] = result
            
            self.logger.info(f"Completed resume task: {task_id}")
            
        except asyncio.TimeoutError:
            self.processing_tasks[task_id]["status"] = "timeout"
            self.processing_tasks[task_id]["error"] = "Task timed out"
            self.logger.error(f"Resume task {task_id} timed out")
            
        except Exception as e:
            # Check if we should retry
            retry_count = self.processing_tasks[task_id]["retry_count"]
            max_retries = priority_config["retry_count"]
            
            if retry_count < max_retries:
                self.processing_tasks[task_id]["retry_count"] += 1
                self.processing_tasks[task_id]["status"] = "retrying"
                
                # Re-queue the task
                await asyncio.sleep(5)  # Brief delay before retry
                await self.task_queue.put(task)
                
                self.logger.info(f"Retrying resume task {task_id} (attempt {retry_count + 1})")
            else:
                self.processing_tasks[task_id]["status"] = "failed"
                self.processing_tasks[task_id]["error"] = str(e)
                self.logger.error(f"Failed resume task {task_id}: {e}")
        
        finally:
            # Clean up after delay
            await asyncio.sleep(300)  # Keep status for 5 minutes
            if task_id in self.processing_tasks:
                del self.processing_tasks[task_id]
    
    async def _generate_resume(self, task: ResumeGenerateTask) -> Dict[str, Any]:
        """Generate resume using the pipeline"""
        try:
            # Execute resume pipeline
            pipeline_result = await self.resume_pipeline.execute(
                {
                    "user_profile": task.user_profile,
                    "job_description": task.job_description
                },
                task.preferences
            )
            
            # Store result (in real implementation, this would save to storage)
            result_data = {
                "task_id": task.task_id,
                "user_id": task.user_id,
                "resume_content": pipeline_result.resume_content,
                "metadata": pipeline_result.metadata,
                "quality_score": pipeline_result.quality_score,
                "processing_time": pipeline_result.processing_time,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            await self._store_resume_result(result_data)
            
            return {
                "success": True,
                "resume_id": f"resume_{task.task_id}",
                "quality_score": pipeline_result.quality_score,
                "processing_time": pipeline_result.processing_time
            }
            
        except Exception as e:
            self.logger.error(f"Resume generation failed for task {task.task_id}: {e}")
            raise e
    
    async def _store_resume_result(self, result_data: Dict[str, Any]):
        """Store generated resume result"""
        # Simulate storing resume result
        await asyncio.sleep(0.1)
        
        # In real implementation, this would store to database or file system
        storage_path = f"resumes/{result_data['user_id']}/{result_data['task_id']}.json"
        
        self.logger.info(f"Stored resume result to: {storage_path}")
    
    async def _maintenance_loop(self):
        """Maintenance loop for cleanup and monitoring"""
        while self.worker_active:
            try:
                # Clean up old completed tasks
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(hours=1)
                
                old_tasks = [
                    task_id for task_id, task_info in self.processing_tasks.items()
                    if task_info.get("completed_at") and task_info["completed_at"] < cutoff_time
                ]
                
                for task_id in old_tasks:
                    del self.processing_tasks[task_id]
                
                # Monitor queue health
                queue_size = self.task_queue.qsize()
                if queue_size > 50:
                    self.logger.warning(f"High queue size: {queue_size}")
                
                # Log performance metrics
                processing_count = len(self.processing_tasks)
                if processing_count > 0:
                    self.logger.info(f"Processing {processing_count} tasks")
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Maintenance error: {e}")
                await asyncio.sleep(60)
    
    async def get_queue_metrics(self) -> Dict[str, Any]:
        """Get detailed queue metrics"""
        tasks_by_priority = {1: 0, 2: 0, 3: 0}
        
        # Count tasks by priority (simplified - would need to inspect queue)
        for task_info in self.processing_tasks.values():
            task = task_info.get("task")
            if task:
                tasks_by_priority[task.priority] = tasks_by_priority.get(task.priority, 0) + 1
        
        return {
            "queue_size": self.task_queue.qsize(),
            "processing_by_priority": tasks_by_priority,
            "worker_utilization": len(self.processing_tasks) / self.max_concurrent_tasks,
            "average_processing_time": 45.0  # Placeholder
        }

# Global worker instance
resume_generate_worker = ResumeGenerateWorker()

__all__ = ["ResumeGenerateWorker", "ResumeGenerateTask", "resume_generate_worker"]
