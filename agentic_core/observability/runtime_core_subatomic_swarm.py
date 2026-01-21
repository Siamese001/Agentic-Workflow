from __future__ import annotations

"""Subatomic Swarm - Parallel HOP execution with concurrency control.

Orchestrates multiple SubatomicHop instances running in parallel using asyncio.Semaphore
to prevent API throttling and rate limiting. Optimized for 32GB/8-core WSL2 environment.
"""
import asyncio
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

Logger: Any = logging.getLogger(__name__)

@dataclass
class SwarmResult:
    """Result from a single HOP execution in the swarm."""
    hop_id: str
    status: str
    result: dict[str, Any] | None = None
    error: str | None = None
    execution_time: float = 0.0
    timestamp: float = field(default_factory=time.time)

@dataclass
class SwarmMetrics:
    """Metrics for swarm execution."""
    total_hops: int = 0
    successful: int = 0
    failed: int = 0
    timeout: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    max_execution_time: float = 0.0
    min_execution_time: float = float('inf')
    start_time: float | None = None
    end_time: float | None = None

class SubatomicSwarm:
    """Orchestrates multiple SubatomicHop instances in parallel.

    Uses asyncio.Semaphore to limit concurrent LLM API calls and prevent
    rate limiting. Provides error isolation so one HOP failure doesn't
    crash the entire swarm.
    """

    def __init__(self, max_concurrency: int=5, timeout_per_hop: float=300.0, enable_metrics: bool=True):
        """Initialize the SubatomicSwarm.

        Args:
            max_concurrency: Maximum number of concurrent HOPs (default: 5)
            timeout_per_hop: Timeout in seconds for each HOP (default: 300s)
            enable_metrics: Enable metrics collection (default: True)
        """
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.timeout_per_hop = timeout_per_hop
        self.enable_metrics = enable_metrics
        self.metrics = SwarmMetrics()
        Logger.info(f'Initialized SubatomicSwarm: max_concurrency={max_concurrency}, timeout_per_hop={timeout_per_hop}s')

    async def _run_guarded_hop(self, hop: Any, hop_id: str, **kwargs) -> SwarmResult:
        """Wrap a single HOP execution with semaphore guard and error handling.

        Args:
            hop: SubatomicHop instance to execute
            hop_id: Unique identifier for this HOP
            **kwargs: Arguments to pass to hop.run()

        Returns:
            SwarmResult with execution status and result/error
        """
        start_time = time.time()
        async with self.semaphore:
            try:
                Logger.debug(f'Starting HOP {hop_id}')
                result = await asyncio.wait_for(hop.run(**kwargs), timeout=self.timeout_per_hop)
                execution_time = time.time() - start_time
                Logger.info(f'HOP {hop_id} completed successfully in {execution_time:.2f}s')
                return SwarmResult(hop_id=hop_id, status='success', result=result, execution_time=execution_time)
            except asyncio.TimeoutError:
                execution_time = time.time() - start_time
                error_msg = f'HOP {hop_id} timed out after {self.timeout_per_hop}s'
                Logger.error(error_msg)
                return SwarmResult(hop_id=hop_id, status='timeout', error=error_msg, execution_time=execution_time)
            except Exception as e:
                execution_time = time.time() - start_time
                error_msg = f'HOP {hop_id} failed: {str(e)}'
                Logger.error(error_msg, exc_info=True)
                return SwarmResult(hop_id=hop_id, status='failed', error=error_msg, execution_time=execution_time)

    async def execute_swarm(self, hops: list[Any], inputs: list[dict[str, Any]], hop_ids: list[str] | None=None) -> list[SwarmResult]:
        """Run a list of HOPs in parallel against a list of inputs.

        Args:
            hops: List of SubatomicHop instances to execute
            inputs: List of input dictionaries (one per HOP)
            hop_ids: Optional list of HOP identifiers (auto-generated if None)

        Returns:
            List of SwarmResult objects

        Raises:
            ValueError: If number of HOPs doesn't match number of inputs

        Example:
            >>> swarm = SubatomicSwarm(max_concurrency=5)
            >>> results = await swarm.execute_swarm(
            ...     hops=[hop1, hop2, hop3],
            ...     inputs=[{"data": "input1"}, {"data": "input2"}, {"data": "input3"}]
            ... )
        """
        if len(hops) != len(inputs):
            raise ValueError(f'Number of HOPs ({len(hops)}) must match number of inputs ({len(inputs)})')
        if hop_ids is None:
            hop_ids: Any = [f'hop_{i}' for i in range(len(hops))]
        elif len(hop_ids) != len(hops):
            raise ValueError(f'Number of hop_ids ({len(hop_ids)}) must match number of HOPs ({len(hops)})')
        if self.enable_metrics:
            self.metrics = SwarmMetrics(total_hops=len(hops), start_time=time.time())
        Logger.info(f'Starting swarm execution: {len(hops)} HOPs')
        tasks: Any = [self._run_guarded_hop(hop, hop_id, **input_data) for hop, hop_id, input_data in zip(hops, hop_ids, inputs, strict=False)]
        results: Any = await asyncio.gather(*tasks, return_exceptions=True)
        if self.enable_metrics:
            self._update_metrics(results)
        Logger.info(f'Swarm execution complete: {self.metrics.successful}/{self.metrics.total_hops} successful, {self.metrics.failed} failed, {self.metrics.timeout} timeout')
        return results

    async def execute_batch(self, hop_factory: Callable[[], Any], inputs: list[dict[str, Any]], batch_size: int | None=None) -> list[SwarmResult]:
        """Execute a batch of inputs using a HOP factory function.

        Useful when you need to create fresh HOP instances for each input
        to avoid state contamination.

        Args:
            hop_factory: Function that returns a new SubatomicHop instance
            inputs: List of input dictionaries
            batch_size: Optional batch size (defaults to max_concurrency)

        Returns:
            List of SwarmResult objects

        Example:
            >>> def create_resume_hop():
            ...     return SubatomicHop(hop_function=generate_resume)
            >>>
            >>> swarm = SubatomicSwarm(max_concurrency=5)
            >>> results = await swarm.execute_batch(
            ...     hop_factory=create_resume_hop,
            ...     inputs=[{"job_desc": desc} for desc in job_descriptions]
            ... )
        """
        hops: Any = [hop_factory() for _ in inputs]
        if batch_size and batch_size < len(inputs):
            all_results: Any = []
            for i in range(0, len(inputs), batch_size):
                batch_hops: Any = hops[i:i + batch_size]
                batch_inputs: Any = inputs[i:i + batch_size]
                Logger.info(f'Processing batch {i // batch_size + 1}: {len(batch_hops)} HOPs')
                batch_results: Any = await self.execute_swarm(hops=batch_hops, inputs=batch_inputs)
                all_results.extend(batch_results)
            return all_results
        else:
            return await self.execute_swarm(hops=hops, inputs=inputs)

    def _update_metrics(self, results: list[SwarmResult]) -> None:
        """Update swarm metrics based on results.

        Args:
            results: List of SwarmResult objects
        """
        self.metrics.end_time = time.time()
        for result in results:
            if isinstance(result, SwarmResult):
                if result.status == 'success':
                    self.metrics.successful += 1
                elif result.status == 'failed':
                    self.metrics.failed += 1
                elif result.status == 'timeout':
                    self.metrics.timeout += 1
                self.metrics.total_execution_time += result.execution_time
                self.metrics.max_execution_time = max(self.metrics.max_execution_time, result.execution_time)
                self.metrics.min_execution_time = min(self.metrics.min_execution_time, result.execution_time)
        if self.metrics.total_hops > 0:
            self.metrics.average_execution_time = self.metrics.total_execution_time / self.metrics.total_hops

    def get_metrics(self) -> SwarmMetrics:
        """Get current swarm metrics.

        Returns:
            SwarmMetrics object with execution statistics
        """
        return self.metrics

    def get_success_rate(self) -> float:
        """Get success rate as a percentage.

        Returns:
            Success rate (0.0 to 100.0)
        """
        if self.metrics.total_hops == 0:
            return 0.0
        return self.metrics.successful / self.metrics.total_hops * 100

    def reset_metrics(self) -> None:
        """Reset metrics for a new swarm execution."""
        self.metrics = SwarmMetrics()

def create_subatomic_swarm(max_concurrency: int=5, timeout_per_hop: float=300.0, enable_metrics: bool=True) -> SubatomicSwarm:
    """Create a SubatomicSwarm instance.

    Args:
        max_concurrency: Maximum number of concurrent HOPs
        timeout_per_hop: Timeout in seconds for each HOP
        enable_metrics: Enable metrics collection

    Returns:
        Configured SubatomicSwarm instance
    """
    return SubatomicSwarm(max_concurrency=max_concurrency, timeout_per_hop=timeout_per_hop, enable_metrics=enable_metrics)
