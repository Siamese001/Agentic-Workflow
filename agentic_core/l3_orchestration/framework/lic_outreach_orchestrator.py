"""Outreach orchestrator framework for L3 orchestration."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import asyncio

@dataclass
class OutreachPipelineResult:
    """Result from outreach pipeline execution."""
    pipeline_id: str = ""
    status: str = "completed"
    contacts_processed: int = 0
    messages_generated: int = 0
    success_rate: float = 0.0
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ConcurrencyConfig:
    """Configuration for concurrent outreach operations."""
    max_concurrent_contacts: int = 5
    max_concurrent_messages: int = 10
    rate_limit_per_second: float = 1.0
    timeout_seconds: int = 300
    retry_attempts: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)

class OutreachOrchestrator:
    """Main orchestrator for outreach campaigns with concurrency support."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize orchestrator with configuration."""
        self.config = config or {}
        self.concurrency_config = ConcurrencyConfig(**self.config.get("concurrency", {}))
        self.active_pipelines = {}
        self.semaphore_contacts = asyncio.Semaphore(self.concurrency_config.max_concurrent_contacts)
        self.semaphore_messages = asyncio.Semaphore(self.concurrency_config.max_concurrent_messages)
    
    async def execute_outreach_pipeline(self, 
                                       contacts: List[Dict[str, Any]], 
                                       message_templates: List[str],
                                       pipeline_id: str = None) -> OutreachPipelineResult:
        """Execute outreach pipeline with concurrency controls."""
        if pipeline_id is None:
            pipeline_id = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        start_time = datetime.now()
        
        try:
            # Process contacts concurrently with rate limiting
            processed_contacts = await self._process_contacts_concurrently(contacts)
            
            # Generate messages concurrently
            generated_messages = await self._generate_messages_concurrently(
                processed_contacts, message_templates
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return OutreachPipelineResult(
                pipeline_id=pipeline_id,
                status="completed",
                contacts_processed=len(processed_contacts),
                messages_generated=len(generated_messages),
                success_rate=len(generated_messages) / len(contacts) if contacts else 1.0,
                execution_time=execution_time,
                metadata={
                    "concurrency_config": self.concurrency_config,
                    "processed_at": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return OutreachPipelineResult(
                pipeline_id=pipeline_id,
                status="failed",
                contacts_processed=0,
                messages_generated=0,
                success_rate=0.0,
                errors=[str(e)],
                execution_time=execution_time,
                metadata={"error_occurred": True}
            )
    
    async def _process_contacts_concurrently(self, contacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process contacts with concurrency limits."""
        async def process_single_contact(contact):
            async with self.semaphore_contacts:
                # Simulate rate limiting
                await asyncio.sleep(1.0 / self.concurrency_config.rate_limit_per_second)
                # Mock processing
                return {
                    **contact,
                    "processed": True,
                    "processing_timestamp": datetime.now().isoformat()
                }
        
        tasks = [process_single_contact(contact) for contact in contacts]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _generate_messages_concurrently(self, 
                                              processed_contacts: List[Dict[str, Any]], 
                                              templates: List[str]) -> List[Dict[str, Any]]:
        """Generate messages with concurrency limits."""
        async def generate_single_message(contact):
            async with self.semaphore_messages:
                # Simulate rate limiting
                await asyncio.sleep(1.0 / self.concurrency_config.rate_limit_per_second)
                # Mock message generation
                template = templates[0] if templates else "Default message"
                return {
                    "contact_id": contact.get("id", "unknown"),
                    "message": f"{template} for {contact.get('name', 'contact')}",
                    "generated_at": datetime.now().isoformat(),
                    "template_used": template
                }
        
        # Filter out exceptions from contact processing
        valid_contacts = [c for c in processed_contacts if not isinstance(c, Exception)]
        tasks = [generate_single_message(contact) for contact in valid_contacts]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_pipeline_status(self, pipeline_id: str) -> Optional[OutreachPipelineResult]:
        """Get status of a specific pipeline."""
        return self.active_pipelines.get(pipeline_id)
    
    def update_concurrency_config(self, new_config: Dict[str, Any]) -> None:
        """Update concurrency configuration."""
        self.concurrency_config = ConcurrencyConfig(**new_config)
        self.semaphore_contacts = asyncio.Semaphore(self.concurrency_config.max_concurrent_contacts)
        self.semaphore_messages = asyncio.Semaphore(self.concurrency_config.max_concurrent_messages)
    
    async def handle_pipeline_failure(self, pipeline_id: str, error: Exception) -> OutreachPipelineResult:
        """Handle pipeline failure with cleanup and reporting."""
        if pipeline_id in self.active_pipelines:
            result = self.active_pipelines[pipeline_id]
            result.status = "failed"
            result.errors.append(str(error))
            result.metadata["failure_timestamp"] = datetime.now().isoformat()
            return result
        
        return OutreachPipelineResult(
            pipeline_id=pipeline_id,
            status="failed",
            contacts_processed=0,
            messages_generated=0,
            success_rate=0.0,
            errors=[str(error)],
            metadata={"failure_timestamp": datetime.now().isoformat()}
        )
