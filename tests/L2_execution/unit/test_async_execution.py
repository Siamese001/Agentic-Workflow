"""
L2 Execution Layer Unit Tests - Async Execution

Tests for asynchronous tool execution and concurrency without planning logic.
Focuses on async/await patterns, concurrency control, and resource management.
"""

import pytest
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import time
import threading
import uuid

# Mark all tests in this module as L2 execution unit tests
pytestmark = [pytest.mark.unit, pytest.mark.l2, pytest.mark.execution, pytest.mark.asyncio]


class ExecutionStatus(Enum):
    """Execution status codes for async testing."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class MockAsyncTask:
    """Mock async task for execution testing."""
    task_id: str
    task_name: str
    parameters: Dict[str, Any]
    status: ExecutionStatus
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    start_time: Optional[float]
    end_time: Optional[float]
    execution_time: Optional[float]


class TestAsyncExecutionPatterns:
    """Test async execution patterns and coroutines."""
    
    async def test_basic_async_execution(self):
        """Test basic async function execution."""
        
        async def mock_tool_execution(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
            """Mock async tool execution."""
            await asyncio.sleep(0.01)  # Simulate async work
            return {
                "tool": tool_name,
                "parameters": parameters,
                "result": f"Executed {tool_name} successfully",
                "execution_id": str(uuid.uuid4())
            }
        
        # Test basic async execution
        result = await mock_tool_execution("text_analyzer", {"text": "test content"})
        
        assert result["tool"] == "text_analyzer"
        assert result["parameters"]["text"] == "test content"
        assert "execution_id" in result
        assert "successfully" in result["result"]
    
    async def test_concurrent_async_execution(self):
        """Test concurrent execution of multiple async tasks."""
        
        async def mock_parallel_task(task_id: int, duration: float) -> Dict[str, Any]:
            """Mock task that runs for specified duration."""
            await asyncio.sleep(duration)
            return {
                "task_id": task_id,
                "completed_at": time.time(),
                "duration": duration
            }
        
        # Create tasks with different durations
        tasks = [
            mock_parallel_task(1, 0.05),
            mock_parallel_task(2, 0.03),
            mock_parallel_task(3, 0.04),
            mock_parallel_task(4, 0.02)
        ]
        
        # Execute concurrently and measure time
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Validate concurrent execution
        assert len(results) == 4
        
        # Should complete in roughly the time of the longest task
        longest_task_duration = 0.05
        assert total_time < longest_task_duration + 0.02  # Allow some tolerance
        
        # Validate all tasks completed
        task_ids = [result["task_id"] for result in results]
        assert set(task_ids) == {1, 2, 3, 4}
    
    async def test_async_error_propagation(self):
        """Test error handling in async execution."""
        
        async def failing_async_task(should_fail: bool, error_message: str = "Async error"):
            """Mock async task that can fail."""
            await asyncio.sleep(0.01)
            if should_fail:
                raise ValueError(error_message)
            return {"success": True, "data": "completed"}
        
        # Test successful execution
        success_result = await failing_async_task(False)
        assert success_result["success"] is True
        
        # Test error propagation
        with pytest.raises(ValueError, match="Async error"):
            await failing_async_task(True)
        
        # Test error handling with try/catch
        try:
            await failing_async_task(True, "Custom error message")
        except ValueError as e:
            assert str(e) == "Custom error message"
        else:
            pytest.fail("Expected ValueError was not raised")
    
    async def test_async_timeout_handling(self):
        """Test timeout handling in async operations."""
        
        async def long_running_task(duration: float):
            """Task that runs for specified duration."""
            await asyncio.sleep(duration)
            return {"completed": True, "duration": duration}
        
        # Test with sufficient timeout
        result = await asyncio.wait_for(long_running_task(0.1), timeout=0.2)
        assert result["completed"] is True
        
        # Test with insufficient timeout
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(long_running_task(0.3), timeout=0.1)
    
    async def test_async_cancellation(self):
        """Test task cancellation in async context."""
        
        async def cancellable_task(duration: float):
            """Task that can be cancelled."""
            try:
                for i in range(int(duration * 10)):  # Check cancellation every 0.1s
                    await asyncio.sleep(0.1)
                return {"completed": True}
            except asyncio.CancelledError:
                return {"cancelled": True}
        
        # Create and cancel task
        task = asyncio.create_task(cancellable_task(1.0))
        await asyncio.sleep(0.25)  # Let it run for a bit
        task.cancel()
        
        try:
            result = await task
            assert result["cancelled"] is True
        except asyncio.CancelledError:
            # Task was cancelled before completing
            pass


class TestConcurrencyControl:
    """Test concurrency control and resource management."""
    
    async def test_semaphore_limited_concurrency(self):
        """Test limiting concurrency with semaphore."""
        
        class ConcurrencyLimiter:
            def __init__(self, max_concurrent: int):
                self.semaphore = asyncio.Semaphore(max_concurrent)
                self.concurrent_count = 0
                self.max_concurrent_reached = 0
            
            async def execute_with_limit(self, task_id: int, duration: float):
                """Execute task with concurrency limit."""
                async with self.semaphore:
                    self.concurrent_count += 1
                    self.max_concurrent_reached = max(self.max_concurrent_reached, self.concurrent_count)
                    
                    try:
                        await asyncio.sleep(duration)
                        return {"task_id": task_id, "completed": True}
                    finally:
                        self.concurrent_count -= 1
        
        limiter = ConcurrencyLimiter(max_concurrent=3)
        
        # Create many tasks that should be limited
        tasks = [
            limiter.execute_with_limit(i, 0.1)
            for i in range(10)
        ]
        
        # Execute all tasks
        results = await asyncio.gather(*tasks)
        
        # Validate concurrency was limited
        assert len(results) == 10
        assert limiter.max_concurrent_reached == 3
        assert limiter.concurrent_count == 0  # All tasks completed
        
        # Validate all tasks completed successfully
        assert all(result["completed"] for result in results)
    
    async def test_task_queue_management(self):
        """Test async task queue management."""
        
        class AsyncTaskQueue:
            def __init__(self, max_size: int = 100):
                self.queue = asyncio.Queue(maxsize=max_size)
                self.processing = False
                self.completed_tasks = []
            
            async def add_task(self, task_data: Dict[str, Any]):
                """Add task to queue."""
                await self.queue.put(task_data)
            
            async def process_tasks(self, worker_count: int = 2):
                """Process tasks with multiple workers."""
                self.processing = True
                workers = [self._worker(f"worker_{i}") for i in range(worker_count)]
                await asyncio.gather(*workers)
                self.processing = False
            
            async def _worker(self, worker_id: str):
                """Worker that processes tasks from queue."""
                while True:
                    try:
                        # Get task with timeout
                        task = await asyncio.wait_for(self.queue.get(), timeout=0.1)
                        
                        # Process task
                        await asyncio.sleep(0.01)  # Simulate processing
                        result = {
                            "worker_id": worker_id,
                            "task_id": task["task_id"],
                            "processed_at": time.time()
                        }
                        self.completed_tasks.append(result)
                        
                        # Mark task as done
                        self.queue.task_done()
                        
                    except asyncio.TimeoutError:
                        # No more tasks
                        break
        
            async def get_completed_count(self):
                """Get number of completed tasks."""
                return len(self.completed_tasks)
        
        # Test queue processing
        task_queue = AsyncTaskQueue()
        
        # Add tasks to queue
        for i in range(10):
            await task_queue.add_task({"task_id": f"task_{i}"})
        
        # Process tasks with 2 workers
        await task_queue.process_tasks(worker_count=2)
        
        # Validate processing
        completed_count = await task_queue.get_completed_count()
        assert completed_count == 10
        
        # Validate work distribution
        worker_tasks = {}
        for result in task_queue.completed_tasks:
            worker_id = result["worker_id"]
            worker_tasks[worker_id] = worker_tasks.get(worker_id, 0) + 1
        
        assert len(worker_tasks) == 2  # 2 workers used
        assert all(count > 0 for count in worker_tasks.values())  # Both workers did work
    
    async def test_resource_pool_management(self):
        """Test async resource pool management."""
        
        class AsyncResourcePool:
            def __init__(self, resource_count: int):
                self.resources = [f"resource_{i}" for i in range(resource_count)]
                self.available_resources = asyncio.Queue()
                self.usage_log = []
                
                # Initialize queue with resources
                for resource in self.resources:
                    self.available_resources.put_nowait(resource)
            
            async def acquire_resource(self, user_id: str) -> str:
                """Acquire a resource from the pool."""
                resource = await self.available_resources.get()
                self.usage_log.append({
                    "action": "acquire",
                    "user_id": user_id,
                    "resource": resource,
                    "timestamp": time.time()
                })
                return resource
            
            async def release_resource(self, resource: str, user_id: str):
                """Release a resource back to the pool."""
                await self.available_resources.put(resource)
                self.usage_log.append({
                    "action": "release",
                    "user_id": user_id,
                    "resource": resource,
                    "timestamp": time.time()
                })
            
            async def use_resource(self, user_id: str, duration: float):
                """Use a resource for specified duration."""
                resource = await self.acquire_resource(user_id)
                try:
                    await asyncio.sleep(duration)
                    return {"user_id": user_id, "resource": resource, "used": True}
                finally:
                    await self.release_resource(resource, user_id)
        
        # Test resource pool
        resource_pool = AsyncResourcePool(resource_count=3)
        
        # Create concurrent resource usage tasks
        usage_tasks = [
            resource_pool.use_resource(f"user_{i}", 0.05)
            for i in range(8)  # More users than resources
        ]
        
        # Execute all tasks
        results = await asyncio.gather(*usage_tasks)
        
        # Validate resource usage
        assert len(results) == 8
        assert all(result["used"] for result in results)
        
        # Validate all resources were released
        assert resource_pool.available_resources.qsize() == 3
        
        # Validate usage log
        acquire_actions = [log for log in resource_pool.usage_log if log["action"] == "acquire"]
        release_actions = [log for log in resource_pool.usage_log if log["action"] == "release"]
        
        assert len(acquire_actions) == 8
        assert len(release_actions) == 8


class TestAsyncExecutionEngine:
    """Test async execution engine implementation."""
    
    async def test_execution_engine_task_management(self):
        """Test async execution engine task management."""
        
        class AsyncExecutionEngine:
            def __init__(self):
                self.tasks = {}
                self.execution_log = []
                self.task_counter = 0
            
            async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
                """Execute tool asynchronously."""
                task_id = f"task_{self.task_counter}"
                self.task_counter += 1
                
                task = MockAsyncTask(
                    task_id=task_id,
                    task_name=tool_name,
                    parameters=parameters,
                    status=ExecutionStatus.RUNNING,
                    result=None,
                    error=None,
                    start_time=time.time(),
                    end_time=None,
                    execution_time=None
                )
                
                self.tasks[task_id] = task
                self.execution_log.append({"action": "start", "task_id": task_id, "timestamp": time.time()})
                
                try:
                    # Simulate tool execution
                    await asyncio.sleep(0.01)
                    
                    result = {
                        "tool": tool_name,
                        "parameters": parameters,
                        "result": f"Mock result for {tool_name}",
                        "execution_id": str(uuid.uuid4())
                    }
                    
                    # Update task with success
                    end_time = time.time()
                    execution_time = end_time - task.start_time
                    
                    updated_task = task._replace(
                        status=ExecutionStatus.COMPLETED,
                        result=result,
                        end_time=end_time,
                        execution_time=execution_time
                    )
                    self.tasks[task_id] = updated_task
                    
                    self.execution_log.append({"action": "complete", "task_id": task_id, "timestamp": time.time()})
                    
                    return result
                    
                except Exception as e:
                    # Update task with failure
                    end_time = time.time()
                    execution_time = end_time - task.start_time
                    
                    updated_task = task._replace(
                        status=ExecutionStatus.FAILED,
                        error=str(e),
                        end_time=end_time,
                        execution_time=execution_time
                    )
                    self.tasks[task_id] = updated_task
                    
                    self.execution_log.append({"action": "fail", "task_id": task_id, "timestamp": time.time()})
                    raise
            
            async def get_task_status(self, task_id: str) -> Optional[MockAsyncTask]:
                """Get current status of a task."""
                return self.tasks.get(task_id)
            
            def get_execution_summary(self) -> Dict[str, Any]:
                """Get summary of all executions."""
                completed_tasks = [t for t in self.tasks.values() if t.status == ExecutionStatus.COMPLETED]
                failed_tasks = [t for t in self.tasks.values() if t.status == ExecutionStatus.FAILED]
                
                return {
                    "total_tasks": len(self.tasks),
                    "completed": len(completed_tasks),
                    "failed": len(failed_tasks),
                    "success_rate": len(completed_tasks) / len(self.tasks) if self.tasks else 0.0
                }
        
        # Test execution engine
        engine = AsyncExecutionEngine()
        
        # Execute multiple tools
        tools_to_execute = [
            ("text_analyzer", {"text": "sample text"}),
            ("similarity_matcher", {"text1": "A", "text2": "B"}),
            ("content_generator", {"prompt": "generate content"}),
            ("data_validator", {"data": {"key": "value"}})
        ]
        
        execution_tasks = [
            engine.execute_tool(tool_name, params)
            for tool_name, params in tools_to_execute
        ]
        
        results = await asyncio.gather(*execution_tasks)
        
        # Validate execution results
        assert len(results) == 4
        assert all("result" in result for result in results)
        
        # Validate task tracking
        summary = engine.get_execution_summary()
        assert summary["total_tasks"] == 4
        assert summary["completed"] == 4
        assert summary["failed"] == 0
        assert summary["success_rate"] == 1.0
        
        # Validate execution log
        start_actions = [log for log in engine.execution_log if log["action"] == "start"]
        complete_actions = [log for log in engine.execution_log if log["action"] == "complete"]
        
        assert len(start_actions) == 4
        assert len(complete_actions) == 4
    
    async def test_execution_engine_error_handling(self):
        """Test execution engine error handling and recovery."""
        
        class AsyncExecutionEngineWithErrors:
            def __init__(self):
                self.failure_simulation = {}
                self.execution_attempts = []
            
            def simulate_failure(self, tool_name: str, error_message: str):
                """Configure tool to fail."""
                self.failure_simulation[tool_name] = error_message
            
            async def execute_tool_with_retry(self, tool_name: str, parameters: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
                """Execute tool with retry logic."""
                for attempt in range(max_retries + 1):
                    self.execution_attempts.append({"tool": tool_name, "attempt": attempt})
                    
                    try:
                        if tool_name in self.failure_simulation:
                            raise ValueError(self.failure_simulation[tool_name])
                        
                        # Simulate successful execution
                        await asyncio.sleep(0.01)
                        return {
                            "tool": tool_name,
                            "parameters": parameters,
                            "result": f"Success for {tool_name}",
                            "attempts": attempt + 1
                        }
                    
                    except Exception as e:
                        if attempt == max_retries:
                            # Final attempt failed
                            return {
                                "tool": tool_name,
                                "parameters": parameters,
                                "error": str(e),
                                "attempts": attempt + 1,
                                "success": False
                            }
                        else:
                            # Retry after delay
                            await asyncio.sleep(0.01)
        
        # Test error handling
        engine = AsyncExecutionEngineWithErrors()
        
        # Configure some tools to fail
        engine.simulate_failure("failing_tool", "Simulated failure")
        
        # Test successful tool
        success_result = await engine.execute_tool_with_retry("working_tool", {"param": "value"})
        assert success_result["success"] is not True  # No success field in success case
        assert "Success" in success_result["result"]
        assert success_result["attempts"] == 1
        
        # Test failing tool with retries
        failure_result = await engine.execute_tool_with_retry("failing_tool", {"param": "value"})
        assert failure_result["success"] is False
        assert "Simulated failure" in failure_result["error"]
        assert failure_result["attempts"] == 4  # 1 initial + 3 retries
        
        # Validate attempt tracking
        assert len(engine.execution_attempts) == 5  # 1 for success + 4 for failure


class TestAsyncPerformanceOptimization:
    """Test async performance optimization techniques."""
    
    async def test_batch_processing_optimization(self):
        """Test batch processing for performance optimization."""
        
        class AsyncBatchProcessor:
            def __init__(self, batch_size: int = 5):
                self.batch_size = batch_size
                self.processing_times = []
            
            async def process_single_item(self, item_id: int) -> Dict[str, Any]:
                """Process individual item."""
                start_time = time.time()
                await asyncio.sleep(0.01)  # Simulate processing time
                end_time = time.time()
                
                self.processing_times.append(end_time - start_time)
                return {"item_id": item_id, "processed": True}
            
            async def process_batch(self, items: List[int]) -> List[Dict[str, Any]]:
                """Process items in batches for better performance."""
                results = []
                
                for i in range(0, len(items), self.batch_size):
                    batch = items[i:i + self.batch_size]
                    batch_tasks = [self.process_single_item(item_id) for item_id in batch]
                    batch_results = await asyncio.gather(*batch_tasks)
                    results.extend(batch_results)
                
                return results
        
        # Test batch processing
        processor = AsyncBatchProcessor(batch_size=3)
        
        items_to_process = list(range(10))
        start_time = time.time()
        results = await processor.process_batch(items_to_process)
        total_time = time.time() - start_time
        
        # Validate batch processing
        assert len(results) == 10
        assert all(result["processed"] for result in results)
        
        # Validate performance improvement
        # Should be faster than processing all sequentially
        sequential_time_estimate = len(items_to_process) * 0.01  # Rough estimate
        assert total_time < sequential_time_estimate * 0.8  # Should be significantly faster
    
    async def test_async_caching_mechanism(self):
        """Test async caching for performance optimization."""
        
        class AsyncCache:
            def __init__(self, ttl: float = 1.0):
                self.cache = {}
                self.ttl = ttl
                self.cache_hits = 0
                self.cache_misses = 0
            
            async def get(self, key: str) -> Optional[Any]:
                """Get value from cache."""
                if key in self.cache:
                    entry = self.cache[key]
                    if time.time() - entry["timestamp"] < self.ttl:
                        self.cache_hits += 1
                        return entry["value"]
                    else:
                        # Expired entry
                        del self.cache[key]
                
                self.cache_misses += 1
                return None
            
            async def set(self, key: str, value: Any):
                """Set value in cache."""
                self.cache[key] = {
                    "value": value,
                    "timestamp": time.time()
                }
            
            def get_stats(self) -> Dict[str, Any]:
                """Get cache statistics."""
                total_requests = self.cache_hits + self.cache_misses
                hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0.0
                
                return {
                    "hits": self.cache_hits,
                    "misses": self.cache_misses,
                    "hit_rate": hit_rate,
                    "cache_size": len(self.cache)
                }
        
        class CachedAsyncProcessor:
            def __init__(self):
                self.cache = AsyncCache(ttl=2.0)
                self.processing_count = 0
            
            async def process_with_cache(self, input_data: str) -> Dict[str, Any]:
                """Process with caching."""
                # Try cache first
                cached_result = await self.cache.get(input_data)
                if cached_result is not None:
                    return cached_result
                
                # Process and cache result
                self.processing_count += 1
                await asyncio.sleep(0.01)  # Simulate processing
                
                result = {
                    "input": input_data,
                    "processed": True,
                    "processing_id": self.processing_count
                }
                
                await self.cache.set(input_data, result)
                return result
        
        # Test caching
        processor = CachedAsyncProcessor()
        
        # Process same input multiple times
        test_inputs = ["input_1", "input_2", "input_1", "input_3", "input_2", "input_1"]
        
        results = []
        for input_data in test_inputs:
            result = await processor.process_with_cache(input_data)
            results.append(result)
        
        # Validate caching behavior
        assert len(results) == 6
        
        # Should only process unique inputs
        assert processor.processing_count == 3  # input_1, input_2, input_3
        
        # Validate cache statistics
        stats = processor.cache.get_stats()
        assert stats["hits"] == 3  # input_1 (2nd, 3rd), input_2 (2nd)
        assert stats["misses"] == 3  # input_1, input_2, input_3 (first times)
        assert stats["hit_rate"] == 0.5  # 3 hits out of 6 total requests
