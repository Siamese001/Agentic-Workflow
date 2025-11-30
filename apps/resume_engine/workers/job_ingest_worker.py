"""
Job Ingest Worker
LEVEL 5 - Background job processing for job posting ingestion and analysis
"""

from typing import Dict, List, Any, Optional
import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

@dataclass
class JobIngestTask:
    """Job ingestion task data structure"""
    job_id: str
    job_url: str
    company: str
    title: str
    source: str
    priority: int = 1
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class JobIngestWorker:
    """Background worker for processing job posting ingestion tasks"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.task_queue = asyncio.Queue()
        self.processing_tasks = {}
        self.max_concurrent_tasks = 5
        self.worker_active = False
        
        # Job source configurations
        self.job_sources = {
            "linkedin": {"priority": 1, "rate_limit": 100},
            "indeed": {"priority": 2, "rate_limit": 200},
            "glassdoor": {"priority": 3, "rate_limit": 150},
            "company_careers": {"priority": 1, "rate_limit": 50}
        }
    
    async def start_worker(self):
        """Start the background worker"""
        if self.worker_active:
            self.logger.warning("Job ingest worker is already active")
            return
        
        self.worker_active = True
        self.logger.info("Starting job ingest worker")
        
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
        self.logger.info("Stopping job ingest worker")
    
    async def add_job_task(self, task: JobIngestTask) -> bool:
        """Add a job ingestion task to the queue"""
        try:
            await self.task_queue.put(task)
            self.logger.info(f"Added job task: {task.job_id} from {task.source}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add job task: {e}")
            return False
    
    async def get_worker_status(self) -> Dict[str, Any]:
        """Get current worker status"""
        return {
            "active": self.worker_active,
            "queue_size": self.task_queue.qsize(),
            "processing_tasks": len(self.processing_tasks),
            "max_concurrent": self.max_concurrent_tasks,
            "supported_sources": list(self.job_sources.keys())
        }
    
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
    
    async def _process_single_task(self, task: JobIngestTask):
        """Process a single job ingestion task"""
        task_id = task.job_id
        self.processing_tasks[task_id] = {
            "task": task,
            "started_at": datetime.utcnow(),
            "status": "processing"
        }
        
        try:
            self.logger.info(f"Processing job task: {task_id}")
            
            # Step 1: Fetch job posting
            job_data = await self._fetch_job_posting(task)
            if not job_data:
                raise Exception("Failed to fetch job posting")
            
            # Step 2: Parse and extract job details
            parsed_job = await self._parse_job_details(job_data, task)
            
            # Step 3: Enrich with additional data
            enriched_job = await self._enrich_job_data(parsed_job, task)
            
            # Step 4: Store processed job
            await self._store_job_data(enriched_job, task)
            
            # Update task status
            self.processing_tasks[task_id]["status"] = "completed"
            self.processing_tasks[task_id]["completed_at"] = datetime.utcnow()
            
            self.logger.info(f"Completed job task: {task_id}")
            
        except Exception as e:
            self.processing_tasks[task_id]["status"] = "failed"
            self.processing_tasks[task_id]["error"] = str(e)
            self.logger.error(f"Failed job task {task_id}: {e}")
        
        finally:
            # Clean up after delay
            await asyncio.sleep(60)  # Keep status for 1 minute
            if task_id in self.processing_tasks:
                del self.processing_tasks[task_id]
    
    async def _fetch_job_posting(self, task: JobIngestTask) -> Optional[Dict[str, Any]]:
        """Fetch job posting from source"""
        # Simulate fetching job posting
        await asyncio.sleep(0.5)  # Simulate network delay
        
        # Mock job data based on task
        mock_job_data = {
            "url": task.job_url,
            "title": task.title,
            "company": task.company,
            "source": task.source,
            "raw_content": f"Job description for {task.title} at {task.company}",
            "posted_date": datetime.utcnow().isoformat(),
            "scraped_at": datetime.utcnow().isoformat()
        }
        
        return mock_job_data
    
    async def _parse_job_details(self, job_data: Dict[str, Any], task: JobIngestTask) -> Dict[str, Any]:
        """Parse and extract structured job details"""
        # Simulate job parsing
        await asyncio.sleep(0.2)
        
        raw_content = job_data.get("raw_content", "")
        
        # Extract requirements (simplified)
        requirements = [
            "Bachelor's degree in relevant field",
            "3+ years of experience",
            "Strong communication skills",
            "Proficiency in relevant technologies"
        ]
        
        # Extract responsibilities (simplified)
        responsibilities = [
            "Develop and maintain software solutions",
            "Collaborate with cross-functional teams",
            "Participate in code reviews",
            "Troubleshoot and resolve technical issues"
        ]
        
        parsed_job = {
            "job_id": task.job_id,
            "title": task.title,
            "company": task.company,
            "location": "Remote",  # Default
            "requirements": requirements,
            "responsibilities": responsibilities,
            "qualifications": requirements[:2],  # Subset
            "skills_required": ["communication", "teamwork", "technical"],
            "experience_level": "Mid-level",
            "salary_range": None,
            "job_type": "Full-time",
            "source": task.source,
            "original_url": task.job_url,
            "parsed_at": datetime.utcnow().isoformat()
        }
        
        return parsed_job
    
    async def _enrich_job_data(self, parsed_job: Dict[str, Any], task: JobIngestTask) -> Dict[str, Any]:
        """Enrich job data with additional information"""
        # Simulate data enrichment
        await asyncio.sleep(0.1)
        
        enriched_job = parsed_job.copy()
        
        # Add enrichment data
        enriched_job.update({
            "enriched_skills": await self._extract_skills(parsed_job),
            "industry_classification": await self._classify_industry(parsed_job),
            "difficulty_score": await self._calculate_difficulty(parsed_job),
            "market_demand": await self._assess_market_demand(parsed_job),
            "enriched_at": datetime.utcnow().isoformat()
        })
        
        return enriched_job
    
    async def _store_job_data(self, enriched_job: Dict[str, Any], task: JobIngestTask):
        """Store processed job data"""
        # Simulate storing job data
        await asyncio.sleep(0.1)
        
        # In real implementation, this would store to database
        self.logger.info(f"Stored job data for: {task.job_id}")
    
    async def _extract_skills(self, job_data: Dict[str, Any]) -> List[str]:
        """Extract skills from job data"""
        # Simulate skill extraction
        return ["python", "javascript", "sql", "aws", "docker"]
    
    async def _classify_industry(self, job_data: Dict[str, Any]) -> str:
        """Classify job industry"""
        # Simulate industry classification
        return "Technology"
    
    async def _calculate_difficulty(self, job_data: Dict[str, Any]) -> float:
        """Calculate application difficulty score"""
        # Simulate difficulty calculation
        return 0.7
    
    async def _assess_market_demand(self, job_data: Dict[str, Any]) -> str:
        """Assess market demand level"""
        # Simulate demand assessment
        return "High"
    
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
                
                # Log status
                if self.task_queue.qsize() > 0:
                    self.logger.info(f"Queue size: {self.task_queue.qsize()}")
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Maintenance error: {e}")
                await asyncio.sleep(60)

# Global worker instance
job_ingest_worker = JobIngestWorker()

__all__ = ["JobIngestWorker", "JobIngestTask", "job_ingest_worker"]
