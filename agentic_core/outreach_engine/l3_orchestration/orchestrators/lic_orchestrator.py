"""LIC Orchestrator for resume processing pipelines."""
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import time

@dataclass
class RecipientProfile:
    """Profile information for outreach recipients."""
    name: str = ""
    title: str = ""
    company: str = ""
    industry: str = ""
    seniority: str = ""
    department: str = ""
    skills: List[str] = field(default_factory=list)
    recent_activity: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LICPipelineResult:
    """Result from LIC pipeline execution."""
    pipeline_id: str = ""
    success: bool = True
    result_data: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class RetryPolicy:
    """Configuration for retry policies."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on_exceptions: List[type] = field(default_factory=lambda: [Exception])
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OrchestratorConfig:
    """Configuration for LIC orchestrator."""
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    timeout_seconds: int = 300
    max_concurrent_pipelines: int = 5
    enable_circuit_breaker: bool = True
    circuit_breaker_threshold: int = 5
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PipelineResult:
    """Result from pipeline execution."""
    pipeline_id: str = ""
    status: str = "completed"
    success: bool = True
    result_data: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    execution_time: float = 0.0
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class CircuitBreakerState:
    """Circuit breaker state tracking."""
    failure_count: int = 0
    last_failure_time: datetime = field(default_factory=datetime.now)
    is_open: bool = False
    half_open_attempts: int = 0

class LICOrchestrator:
    """LIC (Large Language Model Integration Controller) Orchestrator."""

    def __init__(self, config: Optional[OrchestratorConfig] = None):
        """Initialize orchestrator with configuration."""
        self.config = config or OrchestratorConfig()
        self.retry_policy = self.config.retry_policy
        self.active_pipelines = {}
        self.pipeline_history = []
        self.circuit_breaker_state = CircuitBreakerState()
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent_pipelines)

    async def execute_pipeline_with_retry(self,
                                         pipeline_id: str,
                                         pipeline_func: Callable,
                                         *args,
                                         **kwargs) -> PipelineResult:
        """Execute pipeline with retry policy and circuit breaker."""
        start_time = time.time()

        # Check circuit breaker
        if self.config.enable_circuit_breaker and self.circuit_breaker_state.is_open:
            if not self._should_attempt_circuit_breaker_reset():
                return PipelineResult(
                    pipeline_id=pipeline_id,
                    status="failed",
                    success=False,
                    error_message="Circuit breaker is open",
                    execution_time=time.time() - start_time,
                    metadata={"circuit_breaker_open": True}
                )

        # Execute with retry logic
        last_exception = None
        for attempt in range(self.retry_policy.max_attempts):
            try:
                async with self.semaphore:
                    result = await pipeline_func(*args, **kwargs)

                    # Success - reset circuit breaker
                    if self.config.enable_circuit_breaker:
                        self.circuit_breaker_state.failure_count = 0
                        self.circuit_breaker_state.is_open = False

                    execution_time = time.time() - start_time

                    pipeline_result = PipelineResult(
                        pipeline_id=pipeline_id,
                        status="completed",
                        success=True,
                        result_data=result if isinstance(result, dict) else {"result": result},
                        execution_time=execution_time,
                        retry_count=attempt,
                        metadata={"attempt": attempt + 1}
                    )

                    self.pipeline_history.append(pipeline_result)
                    return pipeline_result

            except Exception as e:
                last_exception = e

                # Check if exception should trigger retry
                should_retry = any(isinstance(e, exc_type) for exc_type in self.retry_policy.retry_on_exceptions)

                if not should_retry or attempt == self.retry_policy.max_attempts - 1:
                    # Update circuit breaker on final failure
                    if self.config.enable_circuit_breaker:
                        self._update_circuit_breaker_on_failure()

                    execution_time = time.time() - start_time
                    pipeline_result = PipelineResult(
                        pipeline_id=pipeline_id,
                        status="failed",
                        success=False,
                        error_message=str(e),
                        execution_time=execution_time,
                        retry_count=attempt + 1,
                        metadata={"final_attempt": True, "exception_type": type(e).__name__}
                    )

                    self.pipeline_history.append(pipeline_result)
                    return pipeline_result

                # Wait before retry
                delay = self._calculate_retry_delay(attempt)
                await asyncio.sleep(delay)

        # This should not be reached, but handle gracefully
        execution_time = time.time() - start_time
        return PipelineResult(
            pipeline_id=pipeline_id,
            status="failed",
            success=False,
            error_message=str(last_exception) if last_exception else "Unknown error",
            execution_time=execution_time,
            retry_count=self.retry_policy.max_attempts,
            metadata={"exhausted_retries": True}
        )

    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt."""
        delay = self.retry_policy.base_delay * (self.retry_policy.exponential_base ** attempt)
        delay = min(delay, self.retry_policy.max_delay)

        if self.retry_policy.jitter:
            # Add jitter to prevent thundering herd
            import random
            delay *= (0.5 + random.random() * 0.5)

        return delay

    def _should_attempt_circuit_breaker_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        if not self.circuit_breaker_state.is_open:
            return True

        # Simple time-based reset attempt
        time_since_failure = (datetime.now() - self.circuit_breaker_state.last_failure_time).total_seconds()
        return time_since_failure > self.retry_policy.max_delay * 2

    def _update_circuit_breaker_on_failure(self) -> None:
        """Update circuit breaker state on failure."""
        self.circuit_breaker_state.failure_count += 1
        self.circuit_breaker_state.last_failure_time = datetime.now()

        if self.circuit_breaker_state.failure_count >= self.config.circuit_breaker_threshold:
            self.circuit_breaker_state.is_open = True

    def get_retry_stats(self) -> Dict[str, Any]:
        """Get retry and circuit breaker statistics."""
        if not self.pipeline_history:
            return {"total_pipelines": 0, "message": "No pipeline history available"}

        successful_pipelines = [p for p in self.pipeline_history if p.success]
        failed_pipelines = [p for p in self.pipeline_history if not p.success]

        total_retries = sum(p.retry_count for p in self.pipeline_history)
        avg_execution_time = sum(p.execution_time for p in self.pipeline_history) / len(self.pipeline_history)

        return {
            "total_pipelines": len(self.pipeline_history),
            "successful_pipelines": len(successful_pipelines),
            "failed_pipelines": len(failed_pipelines),
            "success_rate": len(successful_pipelines) / len(self.pipeline_history),
            "total_retries": total_retries,
            "average_retries_per_pipeline": total_retries / len(self.pipeline_history),
            "average_execution_time": avg_execution_time,
            "circuit_breaker": {
                "is_open": self.circuit_breaker_state.is_open,
                "failure_count": self.circuit_breaker_state.failure_count,
                "threshold": self.config.circuit_breaker_threshold
            },
            "retry_policy": {
                "max_attempts": self.retry_policy.max_attempts,
                "base_delay": self.retry_policy.base_delay,
                "max_delay": self.retry_policy.max_delay
            }
        }

    def update_retry_policy(self, new_policy: Dict[str, Any]) -> None:
        """Update retry policy configuration."""
        if "max_attempts" in new_policy:
            self.retry_policy.max_attempts = new_policy["max_attempts"]
        if "base_delay" in new_policy:
            self.retry_policy.base_delay = new_policy["base_delay"]
        if "max_delay" in new_policy:
            self.retry_policy.max_delay = new_policy["max_delay"]
        if "exponential_base" in new_policy:
            self.retry_policy.exponential_base = new_policy["exponential_base"]
        if "jitter" in new_policy:
            self.retry_policy.jitter = new_policy["jitter"]

    def reset_circuit_breaker(self) -> None:
        """Manually reset circuit breaker state."""
        self.circuit_breaker_state = CircuitBreakerState()

    async def execute_resume_pipeline(self,
                                     resume_data: Dict[str, Any],
                                     processing_steps: List[str] = None) -> PipelineResult:
        """Execute resume processing pipeline with retry support."""
        pipeline_id = f"resume_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        async def resume_processing_func():
            """Mock resume processing function."""
            # Simulate resume processing
            await asyncio.sleep(0.1)

            processed_data = {
                "original_data": resume_data,
                "processed_sections": processing_steps or ["parsing", "analysis", "optimization"],
                "processing_timestamp": datetime.now().isoformat(),
                "quality_score": 0.85
            }

            return processed_data

        return await self.execute_pipeline_with_retry(
            pipeline_id, resume_processing_func
        )
