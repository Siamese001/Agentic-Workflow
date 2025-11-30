"""
Enrichment Worker
LEVEL 5 - Background job processing for resume data enrichment and optimization
"""

from typing import Dict, List, Any, Optional
import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from ..services.enrichers.skill_expander import SkillExpander
from ..services.enrichers.job_alignment import JobAligner
from ..services.builders.ats_optimizer import ATSOptimizer

@dataclass
class EnrichmentTask:
    """Resume enrichment task data structure"""
    task_id: str
    resume_id: str
    resume_content: Dict[str, Any]
    enrichment_type: str  # "skills", "ats", "alignment", "comprehensive"
    job_description: Dict[str, Any] = None
    priority: int = 2
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class EnrichmentWorker:
    """Background worker for processing resume enrichment tasks"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.task_queue = asyncio.Queue()
        self.processing_tasks = {}
        self.max_concurrent_tasks = 4
        self.worker_active = False
        
        # Initialize enrichment services
        self.skill_expander = SkillExpander()
        self.job_aligner = JobAligner()
        self.ats_optimizer = ATSOptimizer()
        
        # Enrichment type configurations
        self.enrichment_configs = {
            "skills": {"estimated_time": 30, "retry_count": 2},
            "ats": {"estimated_time": 45, "retry_count": 2},
            "alignment": {"estimated_time": 60, "retry_count": 3},
            "comprehensive": {"estimated_time": 120, "retry_count": 3}
        }
    
    async def start_worker(self):
        """Start the background worker"""
        if self.worker_active:
            self.logger.warning("Enrichment worker is already active")
            return
        
        self.worker_active = True
        self.logger.info("Starting enrichment worker")
        
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
        self.logger.info("Stopping enrichment worker")
    
    async def add_enrichment_task(self, task: EnrichmentTask) -> bool:
        """Add an enrichment task to the queue"""
        try:
            await self.task_queue.put(task)
            self.logger.info(f"Added enrichment task: {task.task_id} ({task.enrichment_type})")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add enrichment task: {e}")
            return False
    
    async def get_worker_status(self) -> Dict[str, Any]:
        """Get current worker status"""
        return {
            "active": self.worker_active,
            "queue_size": self.task_queue.qsize(),
            "processing_tasks": len(self.processing_tasks),
            "max_concurrent": self.max_concurrent_tasks,
            "supported_enrichments": list(self.enrichment_configs.keys())
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
    
    async def _process_single_task(self, task: EnrichmentTask):
        """Process a single enrichment task"""
        task_id = task.task_id
        enrichment_config = self.enrichment_configs.get(task.enrichment_type, self.enrichment_configs["skills"])
        
        self.processing_tasks[task_id] = {
            "task": task,
            "started_at": datetime.utcnow(),
            "status": "processing",
            "retry_count": 0
        }
        
        try:
            self.logger.info(f"Processing enrichment task: {task_id} ({task.enrichment_type})")
            
            # Process with timeout
            result = await asyncio.wait_for(
                self._perform_enrichment(task),
                timeout=enrichment_config["estimated_time"] * 2  # Double the estimated time
            )
            
            # Update task status
            self.processing_tasks[task_id]["status"] = "completed"
            self.processing_tasks[task_id]["completed_at"] = datetime.utcnow()
            self.processing_tasks[task_id]["result"] = result
            
            self.logger.info(f"Completed enrichment task: {task_id}")
            
        except asyncio.TimeoutError:
            self.processing_tasks[task_id]["status"] = "timeout"
            self.processing_tasks[task_id]["error"] = "Enrichment task timed out"
            self.logger.error(f"Enrichment task {task_id} timed out")
            
        except Exception as e:
            # Check if we should retry
            retry_count = self.processing_tasks[task_id]["retry_count"]
            max_retries = enrichment_config["retry_count"]
            
            if retry_count < max_retries:
                self.processing_tasks[task_id]["retry_count"] += 1
                self.processing_tasks[task_id]["status"] = "retrying"
                
                # Re-queue the task
                await asyncio.sleep(10)  # Brief delay before retry
                await self.task_queue.put(task)
                
                self.logger.info(f"Retrying enrichment task {task_id} (attempt {retry_count + 1})")
            else:
                self.processing_tasks[task_id]["status"] = "failed"
                self.processing_tasks[task_id]["error"] = str(e)
                self.logger.error(f"Failed enrichment task {task_id}: {e}")
        
        finally:
            # Clean up after delay
            await asyncio.sleep(600)  # Keep status for 10 minutes
            if task_id in self.processing_tasks:
                del self.processing_tasks[task_id]
    
    async def _perform_enrichment(self, task: EnrichmentTask) -> Dict[str, Any]:
        """Perform the specific enrichment based on task type"""
        if task.enrichment_type == "skills":
            return await self._enrich_skills(task)
        elif task.enrichment_type == "ats":
            return await self._enrich_ats(task)
        elif task.enrichment_type == "alignment":
            return await self._enrich_alignment(task)
        elif task.enrichment_type == "comprehensive":
            return await self._enrich_comprehensive(task)
        else:
            raise ValueError(f"Unknown enrichment type: {task.enrichment_type}")
    
    async def _enrich_skills(self, task: EnrichmentTask) -> Dict[str, Any]:
        """Enrich resume with expanded skills"""
        # Extract current skills from resume
        current_skills = []
        for section in task.resume_content.values():
            if "skill" in str(section).lower():
                content = section.get("content", [])
                if isinstance(content, list):
                    current_skills.extend([item.replace("• ", "").strip() for item in content])
        
        # Create mock user profile for skill expansion
        user_profile = {"skills": current_skills}
        
        # Expand skills
        skill_analysis = await self.skill_expander.expand_skills(
            current_skills, 
            task.job_description or {}
        )
        
        # Update resume content with enriched skills
        enriched_resume = task.resume_content.copy()
        
        # Find and update skills section
        for section_name, section_content in enriched_resume.items():
            if "skill" in section_name.lower():
                enriched_skills = [
                    f"• {skill}" for skill in skill_analysis.expanded_skills[:10]
                ]
                section_content["content"] = enriched_skills
                break
        
        result = {
            "enrichment_type": "skills",
            "expanded_skills": skill_analysis.expanded_skills,
            "skill_categories": skill_analysis.skill_categories,
            "recommendations": skill_analysis.recommended_additions,
            "enriched_resume": enriched_resume
        }
        
        await self._store_enrichment_result(task.task_id, result)
        return result
    
    async def _enrich_ats(self, task: EnrichmentTask) -> Dict[str, Any]:
        """Enrich resume for ATS optimization"""
        ats_result = await self.ats_optimizer.optimize_resume(
            task.resume_content,
            task.job_description or {}
        )
        
        # Apply ATS recommendations to resume content
        enriched_resume = task.resume_content.copy()
        
        # Add ATS optimization notes
        enriched_resume["ats_optimization"] = {
            "score": ats_result.score,
            "recommendations": ats_result.recommendations,
            "keyword_density": ats_result.keyword_density
        }
        
        result = {
            "enrichment_type": "ats",
            "ats_score": ats_result.score,
            "recommendations": ats_result.recommendations,
            "keyword_density": ats_result.keyword_density,
            "compliance_score": ats_result.compliance_score,
            "enriched_resume": enriched_resume
        }
        
        await self._store_enrichment_result(task.task_id, result)
        return result
    
    async def _enrich_alignment(self, task: EnrichmentTask) -> Dict[str, Any]:
        """Enrich resume for job alignment"""
        if not task.job_description:
            raise ValueError("Job description required for alignment enrichment")
        
        alignment_result = await self.job_aligner.analyze_alignment(
            task.resume_content,
            task.job_description
        )
        
        # Apply alignment recommendations to resume content
        enriched_resume = task.resume_content.copy()
        
        # Add alignment optimization notes
        enriched_resume["job_alignment"] = {
            "score": alignment_result.alignment_score,
            "matched_requirements": alignment_result.matched_requirements,
            "missing_requirements": alignment_result.missing_requirements,
            "optimization_suggestions": alignment_result.optimization_suggestions
        }
        
        result = {
            "enrichment_type": "alignment",
            "alignment_score": alignment_result.alignment_score,
            "matched_requirements": alignment_result.matched_requirements,
            "missing_requirements": alignment_result.missing_requirements,
            "strength_areas": alignment_result.strength_areas,
            "improvement_areas": alignment_result.improvement_areas,
            "enriched_resume": enriched_resume
        }
        
        await self._store_enrichment_result(task.task_id, result)
        return result
    
    async def _enrich_comprehensive(self, task: EnrichmentTask) -> Dict[str, Any]:
        """Perform comprehensive enrichment (all types)"""
        results = {}
        enriched_resume = task.resume_content.copy()
        
        # Skills enrichment
        if not task.job_description:
            task.job_description = {}
        
        skills_result = await self._enrich_skills(task)
        results["skills"] = skills_result
        enriched_resume = skills_result["enriched_resume"]
        
        # ATS enrichment
        task.resume_content = enriched_resume
        ats_result = await self._enrich_ats(task)
        results["ats"] = ats_result
        enriched_resume = ats_result["enriched_resume"]
        
        # Alignment enrichment (if job description provided)
        if task.job_description:
            task.resume_content = enriched_resume
            alignment_result = await self._enrich_alignment(task)
            results["alignment"] = alignment_result
            enriched_resume = alignment_result["enriched_resume"]
        
        # Calculate comprehensive score
        scores = [
            results["skills"].get("expanded_skills", {}).get("__score__", 0.8),
            results["ats"].get("ats_score", 0.8),
            results.get("alignment", {}).get("alignment_score", 0.8)
        ]
        comprehensive_score = sum(scores) / len(scores)
        
        result = {
            "enrichment_type": "comprehensive",
            "individual_results": results,
            "comprehensive_score": comprehensive_score,
            "enriched_resume": enriched_resume,
            "total_recommendations": [
                rec for result in results.values() 
                for rec in result.get("recommendations", [])
            ][:10]  # Top 10 recommendations
        }
        
        await self._store_enrichment_result(task.task_id, result)
        return result
    
    async def _store_enrichment_result(self, task_id: str, result: Dict[str, Any]):
        """Store enrichment result"""
        # Simulate storing enrichment result
        await asyncio.sleep(0.1)
        
        # In real implementation, this would store to database
        storage_path = f"enrichments/{task_id}.json"
        
        self.logger.info(f"Stored enrichment result to: {storage_path}")
    
    async def _maintenance_loop(self):
        """Maintenance loop for cleanup and monitoring"""
        while self.worker_active:
            try:
                # Clean up old completed tasks
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(hours=2)
                
                old_tasks = [
                    task_id for task_id, task_info in self.processing_tasks.items()
                    if task_info.get("completed_at") and task_info["completed_at"] < cutoff_time
                ]
                
                for task_id in old_tasks:
                    del self.processing_tasks[task_id]
                
                # Monitor queue health
                queue_size = self.task_queue.qsize()
                if queue_size > 100:
                    self.logger.warning(f"High enrichment queue size: {queue_size}")
                
                # Log performance metrics
                processing_count = len(self.processing_tasks)
                if processing_count > 0:
                    self.logger.info(f"Processing {processing_count} enrichment tasks")
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Maintenance error: {e}")
                await asyncio.sleep(60)
    
    async def get_enrichment_metrics(self) -> Dict[str, Any]:
        """Get detailed enrichment metrics"""
        tasks_by_type = {}
        
        # Count tasks by enrichment type
        for task_info in self.processing_tasks.values():
            task = task_info.get("task")
            if task:
                enrichment_type = task.enrichment_type
                tasks_by_type[enrichment_type] = tasks_by_type.get(enrichment_type, 0) + 1
        
        return {
            "queue_size": self.task_queue.qsize(),
            "processing_by_type": tasks_by_type,
            "worker_utilization": len(self.processing_tasks) / self.max_concurrent_tasks,
            "average_processing_time": 60.0  # Placeholder
        }

# Global worker instance
enrichment_worker = EnrichmentWorker()

__all__ = ["EnrichmentWorker", "EnrichmentTask", "enrichment_worker"]
