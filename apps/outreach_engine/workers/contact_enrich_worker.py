"""
Contact Enrichment Worker
LEVEL 5 - Background worker for enriching contact data for outreach
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import uuid

from ..services.enrichers.personalization_engine import PersonalizationEngine
from ..services.enrichers.relationship_analyzer import RelationshipAnalyzer

@dataclass
class ContactEnrichmentTask:
    """Represents a contact enrichment task"""
    task_id: str
    task_type: str
    contact_data: Dict[str, Any]
    enrichment_sources: List[str]
    priority: int = 1
    created_at: datetime = None
    status: str = "pending"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class ContactEnrichmentResult:
    """Result of contact enrichment task"""
    task_id: str
    status: str
    enriched_contact: Optional[Dict[str, Any]] = None
    enrichment_metadata: Optional[Dict[str, Any]] = None
    personalization_insights: Optional[Dict[str, Any]] = None
    relationship_analysis: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    completed_at: datetime = None
    
    def __post_init__(self):
        if self.completed_at is None:
            self.completed_at = datetime.utcnow()

class ContactEnrichWorker:
    """Background worker for processing contact enrichment tasks"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize enrichment services
        self.personalization_engine = PersonalizationEngine()
        self.relationship_analyzer = RelationshipAnalyzer()
        
        # Worker configuration
        self.worker_config = {
            "max_concurrent_tasks": 3,
            "task_timeout": 180,  # 3 minutes
            "retry_attempts": 2,
            "retry_delay": 3,  # seconds
            "queue_size": 50
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
        
        # Enrichment data sources
        self.enrichment_sources = {
            "linkedin": {
                "enabled": True,
                "data_points": ["company", "role", "experience", "education", "skills"]
            },
            "company_website": {
                "enabled": True,
                "data_points": ["industry", "company_size", "location", "description"]
            },
            "professional_networks": {
                "enabled": True,
                "data_points": ["mutual_connections", "shared_interests", "group_memberships"]
            },
            "public_profiles": {
                "enabled": True,
                "data_points": ["background", "achievements", "publications", "speaking_events"]
            }
        }
    
    async def start(self):
        """Start the contact enrichment worker"""
        try:
            self.logger.info("Starting contact enrichment worker")
            
            if self.is_running:
                self.logger.warning("Worker is already running")
                return
            
            self.is_running = True
            self.stats["worker_start_time"] = datetime.utcnow()
            
            # Start worker tasks
            for i in range(self.worker_config["max_concurrent_tasks"]):
                worker_task = asyncio.create_task(self._worker_loop(f"enrich-worker-{i}"))
                self.worker_tasks.append(worker_task)
            
            # Start cleanup task
            cleanup_task = asyncio.create_task(self._cleanup_loop())
            self.worker_tasks.append(cleanup_task)
            
            self.logger.info(f"Started {self.worker_config['max_concurrent_tasks']} enrichment worker tasks")
            
        except Exception as e:
            self.logger.error(f"Failed to start enrichment worker: {e}")
            raise e
    
    async def stop(self):
        """Stop the contact enrichment worker"""
        try:
            self.logger.info("Stopping contact enrichment worker")
            
            if not self.is_running:
                self.logger.warning("Worker is not running")
                return
            
            self.is_running = False
            
            # Cancel all worker tasks
            for task in self.worker_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
            
            self.logger.info("Enrichment worker stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping enrichment worker: {e}")
            raise e
    
    async def submit_task(self, task_data: Dict[str, Any]) -> str:
        """Submit a new contact enrichment task"""
        try:
            # Create task
            task = ContactEnrichmentTask(
                task_id=str(uuid.uuid4()),
                task_type=task_data.get("task_type", "contact_enrichment"),
                contact_data=task_data["contact_data"],
                enrichment_sources=task_data.get("enrichment_sources", ["linkedin", "company_website"]),
                priority=task_data.get("priority", 1)
            )
            
            # Add to queue
            await self.task_queue.put(task)
            self.active_tasks[task.task_id] = task
            
            self.logger.info(f"Submitted enrichment task {task.task_id}")
            return task.task_id
            
        except Exception as e:
            self.logger.error(f"Failed to submit enrichment task: {e}")
            raise e
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific enrichment task"""
        try:
            # Check active tasks
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                return {
                    "task_id": task.task_id,
                    "status": task.status,
                    "created_at": task.created_at.isoformat(),
                    "task_type": task.task_type,
                    "enrichment_sources": task.enrichment_sources
                }
            
            # Check completed results
            if task_id in self.task_results:
                result = self.task_results[task_id]
                return {
                    "task_id": result.task_id,
                    "status": result.status,
                    "completed_at": result.completed_at.isoformat(),
                    "processing_time": result.processing_time,
                    "error_message": result.error_message
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get enrichment task status: {e}")
            return None
    
    async def get_task_result(self, task_id: str) -> Optional[ContactEnrichmentResult]:
        """Get result of a specific enrichment task"""
        return self.task_results.get(task_id)
    
    async def get_worker_stats(self) -> Dict[str, Any]:
        """Get enrichment worker statistics"""
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
            "worker_config": self.worker_config,
            "available_sources": list(self.enrichment_sources.keys())
        }
    
    async def _worker_loop(self, worker_name: str):
        """Main worker loop for processing enrichment tasks"""
        self.logger.info(f"Starting enrichment worker loop for {worker_name}")
        
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
                self.logger.error(f"Enrichment worker {worker_name} error: {e}")
                await asyncio.sleep(1)
        
        self.logger.info(f"Enrichment worker loop {worker_name} stopped")
    
    async def _process_task(self, task: ContactEnrichmentTask, worker_name: str):
        """Process a single contact enrichment task"""
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"{worker_name} processing enrichment task {task.task_id}")
            
            # Update task status
            task.status = "processing"
            
            # Enrich contact data
            enriched_contact = await self._enrich_contact_data(
                task.contact_data, task.enrichment_sources
            )
            
            # Generate personalization insights
            personalization_insights = await self._generate_personalization_insights(
                enriched_contact
            )
            
            # Analyze relationship potential
            relationship_analysis = await self._analyze_relationship_potential(
                enriched_contact
            )
            
            # Create enrichment metadata
            enrichment_metadata = await self._create_enrichment_metadata(
                task.contact_data, enriched_contact, task.enrichment_sources
            )
            
            # Create successful result
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = ContactEnrichmentResult(
                task_id=task.task_id,
                status="completed",
                enriched_contact=enriched_contact,
                enrichment_metadata=enrichment_metadata,
                personalization_insights=personalization_insights,
                relationship_analysis=relationship_analysis,
                processing_time=processing_time
            )
            
            # Store result
            self.task_results[task.task_id] = result
            self.completed_tasks[task.task_id] = task
            
            # Update stats
            self.stats["tasks_completed"] += 1
            self.stats["tasks_processed"] += 1
            self._update_average_processing_time(processing_time)
            
            # Remove from active tasks
            self.active_tasks.pop(task.task_id, None)
            
            self.logger.info(f"{worker_name} completed enrichment task {task.task_id} in {processing_time:.2f}s")
            
        except Exception as e:
            # Handle task failure
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            error_message = str(e)
            self.logger.error(f"{worker_name} failed enrichment task {task.task_id}: {error_message}")
            
            # Create failure result
            result = ContactEnrichmentResult(
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
    
    async def _enrich_contact_data(
        self,
        contact_data: Dict[str, Any],
        enrichment_sources: List[str]
    ) -> Dict[str, Any]:
        """Enrich contact data from various sources"""
        
        enriched = contact_data.copy()
        
        for source in enrichment_sources:
            if source in self.enrichment_sources:
                source_data = await self._fetch_from_source(source, contact_data)
                if source_data:
                    enriched.update(source_data)
        
        # Add enrichment summary
        enriched["enrichment_summary"] = {
            "sources_used": enrichment_sources,
            "fields_added": list(set(enriched.keys()) - set(contact_data.keys())),
            "enrichment_timestamp": datetime.utcnow().isoformat()
        }
        
        return enriched
    
    async def _fetch_from_source(self, source: str, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch enrichment data from a specific source"""
        
        # Simulate data fetching with mock data
        await asyncio.sleep(0.5)  # Simulate API call
        
        if source == "linkedin":
            return {
                "industry": contact_data.get("industry", "Technology"),
                "experience_years": 8,
                "skills": ["Project Management", "Leadership", "Strategy"],
                "education": "MBA from Top University",
                "background": {
                    "achievements": ["Led major initiatives", "Industry recognition"],
                    "current_focus": "Digital transformation"
                }
            }
        elif source == "company_website":
            return {
                "company_size": "1000-5000",
                "company_location": "San Francisco, CA",
                "company_description": "Leading technology company focused on innovation",
                "company_founded": 2010
            }
        elif source == "professional_networks":
            return {
                "mutual_connections": ["John Doe", "Jane Smith"],
                "shared_interests": ["Technology", "Innovation", "Leadership"],
                "group_memberships": ["Tech Leaders Network", "Innovation Forum"]
            }
        elif source == "public_profiles":
            return {
                "publications": ["Industry insights article", "Thought leadership piece"],
                "speaking_events": ["Tech Conference 2023", "Innovation Summit"],
                "awards": ["Industry Excellence Award", "Leadership Recognition"]
            }
        
        return {}
    
    async def _generate_personalization_insights(
        self,
        enriched_contact: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate personalization insights from enriched contact data"""
        
        insights = {
            "personalization_score": 0.0,
            "available_personalization_elements": [],
            "recommended_approach": "professional",
            "key_topics": [],
            "connection_points": []
        }
        
        # Analyze available personalization elements
        elements = []
        
        if enriched_contact.get("name"):
            elements.append("name_mention")
        
        if enriched_contact.get("company"):
            elements.append("company_reference")
        
        if enriched_contact.get("role"):
            elements.append("role_reference")
        
        if enriched_contact.get("mutual_connections"):
            elements.append("mutual_connections")
        
        if enriched_contact.get("shared_interests"):
            elements.append("shared_interests")
        
        insights["available_personalization_elements"] = elements
        insights["personalization_score"] = len(elements) / 5.0  # Normalize to 0-1
        
        # Determine recommended approach
        if insights["personalization_score"] > 0.7:
            insights["recommended_approach"] = "personalized"
        elif insights["personalization_score"] > 0.4:
            insights["recommended_approach"] = "contextual"
        else:
            insights["recommended_approach"] = "professional"
        
        # Extract key topics
        skills = enriched_contact.get("skills", [])
        industry = enriched_contact.get("industry", "")
        insights["key_topics"] = skills[:3] + [industry] if industry else skills[:3]
        
        # Identify connection points
        connection_points = []
        if enriched_contact.get("mutual_connections"):
            connection_points.append("network_connection")
        if enriched_contact.get("shared_interests"):
            connection_points.append("interest_alignment")
        if enriched_contact.get("company"):
            connection_points.append("industry_peer")
        
        insights["connection_points"] = connection_points
        
        return insights
    
    async def _analyze_relationship_potential(
        self,
        enriched_contact: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze relationship building potential"""
        
        analysis = {
            "relationship_strength_estimate": 0.2,  # Default for cold outreach
            "trust_indicators": [],
            "engagement_likelihood": 0.5,
            "optimal_outreach_type": "email",
            "follow_up_strategy": "professional"
        }
        
        # Assess trust indicators
        trust_indicators = []
        
        if enriched_contact.get("mutual_connections"):
            trust_indicators.append("mutual_network")
            analysis["relationship_strength_estimate"] += 0.2
        
        if enriched_contact.get("shared_interests"):
            trust_indicators.append("shared_interests")
            analysis["relationship_strength_estimate"] += 0.1
        
        if enriched_contact.get("industry") and enriched_contact.get("industry") in enriched_contact.get("background", {}).get("current_focus", ""):
            trust_indicators.append("industry_alignment")
            analysis["relationship_strength_estimate"] += 0.1
        
        analysis["trust_indicators"] = trust_indicators
        analysis["relationship_strength_estimate"] = min(analysis["relationship_strength_estimate"], 1.0)
        
        # Determine engagement likelihood
        if len(trust_indicators) >= 2:
            analysis["engagement_likelihood"] = 0.8
        elif len(trust_indicators) >= 1:
            analysis["engagement_likelihood"] = 0.6
        else:
            analysis["engagement_likelihood"] = 0.4
        
        # Recommend outreach type
        if analysis["relationship_strength_estimate"] > 0.6:
            analysis["optimal_outreach_type"] = "linkedin"
        elif analysis["relationship_strength_estimate"] > 0.4:
            analysis["optimal_outreach_type"] = "email"
        else:
            analysis["optimal_outreach_type"] = "email"
        
        # Determine follow-up strategy
        if analysis["engagement_likelihood"] > 0.7:
            analysis["follow_up_strategy"] = "relationship_building"
        elif analysis["engagement_likelihood"] > 0.5:
            analysis["follow_up_strategy"] = "professional"
        else:
            analysis["follow_up_strategy"] = "value_focused"
        
        return analysis
    
    async def _create_enrichment_metadata(
        self,
        original_contact: Dict[str, Any],
        enriched_contact: Dict[str, Any],
        sources_used: List[str]
    ) -> Dict[str, Any]:
        """Create metadata for the enrichment process"""
        
        return {
            "enrichment_timestamp": datetime.utcnow().isoformat(),
            "original_fields": list(original_contact.keys()),
            "enriched_fields": list(enriched_contact.keys()),
            "new_fields": list(set(enriched_contact.keys()) - set(original_contact.keys())),
            "sources_used": sources_used,
            "data_quality_score": await self._calculate_data_quality(enriched_contact),
            "enrichment_completeness": len(enriched_contact) / 15.0  # Target 15 fields
        }
    
    async def _calculate_data_quality(self, contact_data: Dict[str, Any]) -> float:
        """Calculate quality score of contact data"""
        
        quality_indicators = 0
        total_indicators = 0
        
        # Essential fields
        essential_fields = ["name", "email", "company", "role"]
        for field in essential_fields:
            total_indicators += 1
            if contact_data.get(field):
                quality_indicators += 1
        
        # Enrichment fields
        enrichment_fields = ["industry", "experience_years", "skills", "education"]
        for field in enrichment_fields:
            total_indicators += 1
            if contact_data.get(field):
                quality_indicators += 0.5
        
        # Relationship fields
        relationship_fields = ["mutual_connections", "shared_interests"]
        for field in relationship_fields:
            total_indicators += 1
            if contact_data.get(field):
                quality_indicators += 0.5
        
        return quality_indicators / total_indicators if total_indicators > 0 else 0.0
    
    async def _cleanup_loop(self):
        """Cleanup loop for removing old task results"""
        while self.is_running:
            try:
                await asyncio.sleep(600)  # Run every 10 minutes
                
                # Remove results older than 12 hours
                cutoff_time = datetime.utcnow() - timedelta(hours=12)
                
                old_task_ids = [
                    task_id for task_id, result in self.task_results.items()
                    if result.completed_at < cutoff_time
                ]
                
                for task_id in old_task_ids:
                    self.task_results.pop(task_id, None)
                    self.completed_tasks.pop(task_id, None)
                
                if old_task_ids:
                    self.logger.info(f"Cleaned up {len(old_task_ids)} old enrichment task results")
                
            except Exception as e:
                self.logger.error(f"Enrichment cleanup loop error: {e}")
    
    def _update_average_processing_time(self, processing_time: float):
        """Update average processing time statistic"""
        if self.stats["tasks_processed"] == 1:
            self.stats["average_processing_time"] = processing_time
        else:
            current_avg = self.stats["average_processing_time"]
            n = self.stats["tasks_processed"]
            self.stats["average_processing_time"] = ((current_avg * (n - 1)) + processing_time) / n

# Global enrichment worker instance
contact_enrich_worker = ContactEnrichWorker()

__all__ = [
    "ContactEnrichWorker",
    "ContactEnrichmentTask", 
    "ContactEnrichmentResult",
    "contact_enrich_worker"
]
