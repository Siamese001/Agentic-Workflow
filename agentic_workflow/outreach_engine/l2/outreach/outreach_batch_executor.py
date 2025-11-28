"""
LIC Outreach Batch Executor

New file that wraps batch execution logic for LIC operations.
Provides batch processing capabilities for outreach workflows.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from l2.outreach.company_research_executor import CompanyResearchExecutor
from l2.outreach.contact_research_executor import ContactResearchExecutor
from l2.outreach.message_generation_executor import MessageGenerationExecutor
from l1.outreach_dataclasses import OutreachMission, ArchetypeContext
from core.models.models import ExecutionContext

logger = logging.getLogger(__name__)


@dataclass
class BatchRequest:
    """Individual request in a batch operation."""
    request_id: str
    mission: OutreachMission
    context: Optional[ExecutionContext] = None


@dataclass
class BatchResult:
    """Result of a batch operation."""
    request_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time_seconds: float = 0.0


@dataclass
class BatchConfig:
    """Configuration for batch operations."""
    max_concurrent_requests: int = 4
    timeout_seconds_per_request: int = 30
    enable_progress_tracking: bool = True
    continue_on_error: bool = True
    retry_failed_requests: bool = True
    max_retries: int = 2


class OutreachBatchExecutor:
    """
    Batch executor for outreach operations.
    
    Wraps batch execution logic for LIC workflows while keeping
    individual executors unchanged.
    """
    
    def __init__(self, config: Optional[BatchConfig] = None):
        """Initialize batch executor with configuration."""
        self.config = config or BatchConfig()
        
        # Initialize individual executors
        self.company_executor = CompanyResearchExecutor()
        self.contact_executor = ContactResearchExecutor()
        self.message_executor = MessageGenerationExecutor()
        
        logger.info(f"Initialized OutreachBatchExecutor with max_concurrent={self.config.max_concurrent_requests}")
    
    async def execute_company_research_batch(
        self, 
        requests: List[BatchRequest]
    ) -> List[BatchResult]:
        """
        Execute company research batch.
        
        Args:
            requests: List of batch requests
            
        Returns:
            List of batch results
        """
        return await self._execute_batch(
            requests, 
            self._execute_company_research_single
        )
    
    async def execute_contact_research_batch(
        self, 
        requests: List[BatchRequest]
    ) -> List[BatchResult]:
        """
        Execute contact research batch.
        
        Args:
            requests: List of batch requests
            
        Returns:
            List of batch results
        """
        return await self._execute_batch(
            requests,
            self._execute_contact_research_single
        )
    
    async def execute_message_generation_batch(
        self, 
        requests: List[BatchRequest]
    ) -> List[BatchResult]:
        """
        Execute message generation batch.
        
        Args:
            requests: List of batch requests
            
        Returns:
            List of batch results
        """
        return await self._execute_batch(
            requests,
            self._execute_message_generation_single
        )
    
    async def execute_full_outreach_batch(
        self, 
        requests: List[BatchRequest]
    ) -> List[BatchResult]:
        """
        Execute full outreach pipeline batch.
        
        Args:
            requests: List of batch requests
            
        Returns:
            List of batch results
        """
        results = []
        
        for request in requests:
            try:
                # Execute full pipeline sequentially for each request
                start_time = asyncio.get_event_loop().time()
                
                # Step 1: Company Research
                company_result = await self._execute_company_research_single(request)
                if not company_result.success and not self.config.continue_on_error:
                    results.append(company_result)
                    continue
                
                # Step 2: Contact Research  
                contact_result = await self._execute_contact_research_single(request)
                if not contact_result.success and not self.config.continue_on_error:
                    results.append(contact_result)
                    continue
                
                # Step 3: Message Generation
                message_result = await self._execute_message_generation_single(request)
                
                # Combine results
                execution_time = asyncio.get_event_loop().time() - start_time
                combined_result = BatchResult(
                    request_id=request.request_id,
                    success=message_result.success,
                    result={
                        'company_research': company_result.result,
                        'contact_research': contact_result.result,
                        'message_generation': message_result.result
                    },
                    error=message_result.error,
                    execution_time_seconds=execution_time
                )
                
                results.append(combined_result)
                
            except Exception as e:
                logger.error(f"Pipeline failed for request {request.request_id}: {e}")
                results.append(BatchResult(
                    request_id=request.request_id,
                    success=False,
                    error=str(e)
                ))
        
        return results
    
    async def _execute_batch(
        self, 
        requests: List[BatchRequest], 
        executor_func: Callable
    ) -> List[BatchResult]:
        """
        Execute batch with configured concurrency.
        
        Args:
            requests: List of batch requests
            executor_func: Function to execute for each request
            
        Returns:
            List of batch results
        """
        semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        
        async def execute_with_semaphore(request):
            async with semaphore:
                return await executor_func(request)
        
        tasks = [execute_with_semaphore(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(BatchResult(
                    request_id=requests[i].request_id,
                    success=False,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_company_research_single(self, request: BatchRequest) -> BatchResult:
        """Execute single company research request."""
        try:
            start_time = asyncio.get_event_loop().time()
            
            # This would call the actual company research logic
            # For now, return a placeholder result
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.company_executor.search_company_context(
                    query=request.mission.objective,
                    archetype_context=request.context
                )
            )
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return BatchResult(
                request_id=request.request_id,
                success=True,
                result=result,
                execution_time_seconds=execution_time
            )
            
        except Exception as e:
            logger.error(f"Company research failed for {request.request_id}: {e}")
            return BatchResult(
                request_id=request.request_id,
                success=False,
                error=str(e)
            )
    
    async def _execute_contact_research_single(self, request: BatchRequest) -> BatchResult:
        """Execute single contact research request."""
        try:
            start_time = asyncio.get_event_loop().time()
            
            # This would call the actual contact research logic
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.contact_executor.search_contact_profile(
                    query=request.mission.objective,
                    archetype_context=request.context
                )
            )
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return BatchResult(
                request_id=request.request_id,
                success=True,
                result=result,
                execution_time_seconds=execution_time
            )
            
        except Exception as e:
            logger.error(f"Contact research failed for {request.request_id}: {e}")
            return BatchResult(
                request_id=request.request_id,
                success=False,
                error=str(e)
            )
    
    async def _execute_message_generation_single(self, request: BatchRequest) -> BatchResult:
        """Execute single message generation request."""
        try:
            start_time = asyncio.get_event_loop().time()
            
            # This would call the actual message generation logic
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.message_executor.generate_message(
                    message_plan={},  # Placeholder
                    context=request.context
                )
            )
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return BatchResult(
                request_id=request.request_id,
                success=True,
                result=result,
                execution_time_seconds=execution_time
            )
            
        except Exception as e:
            logger.error(f"Message generation failed for {request.request_id}: {e}")
            return BatchResult(
                request_id=request.request_id,
                success=False,
                error=str(e)
            )
