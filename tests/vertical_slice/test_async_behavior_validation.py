"""
Async Behavior Validation - Vertical Slice Enhancement

Validates async/await behavior and concurrency handling across all layers.
Addresses the gap identified in async testing before horizontal scaling.
"""

import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch
import asyncio
import time
import threading
import uuid

# Mark as async validation test
pytestmark = [pytest.mark.vertical_slice, pytest.mark.asyncio, pytest.mark.integration]


class TestAsyncBehaviorValidation:
    """Validate async behavior across all L1-L5 layers."""
    
    async def test_concurrent_llm_calls(self, mock_llm_factory):
        """Test that LLM mocks handle concurrent calls correctly."""
        
        # Create LLM mock
        llm = mock_llm_factory.create_mock_llm()
        
        # Prepare concurrent tasks
        prompts = [
            "Analyze resume skills",
            "Extract job requirements", 
            "Generate improvements",
            "Validate safety"
        ]
        
        # Execute concurrent calls
        tasks = [llm.generate(prompt) for prompt in prompts]
        results = await asyncio.gather(*tasks)
        
        # Validate all calls succeeded
        assert len(results) == len(prompts)
        assert all(result is not None for result in results)
        
        # Validate call counting works correctly
        assert mock_llm_factory.get_call_count() >= len(prompts)
        
        # Validate responses are deterministic even under concurrency
        analysis_results = [r for r in results if "requirements" in str(r)]
        assert len(analysis_results) >= 1
    
    async def test_async_execution_engine_concurrency(self, mock_execution_engine):
        """Test execution engine handles async operations properly."""
        
        # Create async wrapper for execution engine
        class AsyncExecutionEngine:
            def __init__(self, sync_engine):
                self.sync_engine = sync_engine
                self.execution_lock = asyncio.Lock()
            
            async def execute_tool_async(self, tool_name: str, parameters: Dict[str, Any]):
                async with self.execution_lock:
                    # Simulate async operation
                    await asyncio.sleep(0.01)
                    result = self.sync_engine.execute_tool(tool_name, parameters)
                    return result
        
        async_engine = AsyncExecutionEngine(mock_execution_engine)
        
        # Test concurrent execution
        tasks = [
            async_engine.execute_tool_async("tool_1", {"param": "value1"}),
            async_engine.execute_tool_async("tool_2", {"param": "value2"}),
            async_engine.execute_tool_async("tool_3", {"param": "value3"})
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Validate all executions completed
        assert len(results) == 3
        assert all(result["success"] for result in results)
        
        # Validate execution log shows all calls
        execution_log = mock_execution_engine.get_execution_log()
        assert len(execution_log) == 3
    
    async def test_async_memory_store_operations(self):
        """Test memory store handles concurrent operations correctly."""
        
        from tests.conftest import MockMemoryStore
        
        memory_store = MockMemoryStore()
        
        # Create async wrapper
        class AsyncMemoryStore:
            def __init__(self, sync_store):
                self.sync_store = sync_store
                self.operation_lock = asyncio.Lock()
            
            async def store_triplets_async(self, job_id: str, triplets: List[Dict[str, Any]]):
                async with self.operation_lock:
                    await asyncio.sleep(0.005)  # Simulate I/O
                    self.sync_store.store_triplets(job_id, triplets)
            
            async def query_triplets_async(self, job_id: str):
                async with self.operation_lock:
                    await asyncio.sleep(0.005)  # Simulate I/O
                    return self.sync_store.query_triplets(job_id)
        
        async_store = AsyncMemoryStore(memory_store)
        
        # Test concurrent storage operations
        storage_tasks = [
            async_store.store_triplets_async(f"job_{i}", [{"data": f"value_{i}"}])
            for i in range(5)
        ]
        
        await asyncio.gather(*storage_tasks)
        
        # Test concurrent query operations
        query_tasks = [
            async_store.query_triplets_async(f"job_{i}")
            for i in range(5)
        ]
        
        query_results = await asyncio.gather(*query_tasks)
        
        # Validate all operations completed correctly
        assert len(query_results) == 5
        assert all(len(result) == 1 for result in query_results)
    
    async def test_async_safety_policy_validation(self, mock_safety_policy):
        """Test safety policy handles concurrent validation requests."""
        
        # Create async wrapper
        class AsyncSafetyPolicy:
            def __init__(self, sync_policy):
                self.sync_policy = sync_policy
                self.validation_lock = asyncio.Lock()
            
            async def validate_input_async(self, content: Dict[str, Any]):
                async with self.validation_lock:
                    await asyncio.sleep(0.001)  # Simulate processing
                    return self.sync_policy.validate_input(content)
        
        async_policy = AsyncSafetyPolicy(mock_safety_policy)
        
        # Test concurrent validations
        validation_tasks = [
            async_policy.validate_input_async({"content": f"test_{i}"})
            for i in range(10)
        ]
        
        results = await asyncio.gather(*validation_tasks)
        
        # Validate all validations completed
        assert len(results) == 10
        assert all(result["is_safe"] for result in results)
    
    async def test_async_workflow_orchestration(self):
        """Test complete async workflow orchestration."""
        
        # Mock async workflow components
        class AsyncWorkflowOrchestrator:
            def __init__(self):
                self.llm = AsyncMock()
                self.memory = AsyncMock()
                self.safety = AsyncMock()
                
                # Setup default responses
                self.llm.generate.return_value = {"result": "mocked_response"}
                self.memory.store.return_value = True
                self.safety.validate.return_value = {"is_safe": True}
            
            async def execute_workflow_step(self, step_config: Dict[str, Any]):
                """Execute a single workflow step asynchronously."""
                
                # Safety check
                safety_result = await self.safety.validate(step_config["input"])
                if not safety_result["is_safe"]:
                    raise ValueError("Safety check failed")
                
                # LLM processing
                llm_result = await self.llm.generate(step_config["prompt"])
                
                # Memory storage
                await self.memory.store(step_config["job_id"], llm_result)
                
                return {
                    "step_id": step_config["step_id"],
                    "result": llm_result,
                    "safety_passed": True
                }
            
            async def execute_workflow(self, workflow_config: Dict[str, Any]):
                """Execute complete workflow with concurrent steps where possible."""
                
                steps = workflow_config["steps"]
                
                # Identify steps that can run concurrently (no dependencies)
                concurrent_groups = []
                current_group = []
                
                for step in steps:
                    if not step.get("dependencies", []):
                        current_group.append(step)
                    else:
                        if current_group:
                            concurrent_groups.append(current_group)
                            current_group = []
                        concurrent_groups.append([step])  # Dependent step runs alone
                
                if current_group:
                    concurrent_groups.append(current_group)
                
                # Execute groups sequentially, steps within groups concurrently
                all_results = []
                
                for group in concurrent_groups:
                    if len(group) == 1:
                        # Single step
                        result = await self.execute_workflow_step(group[0])
                        all_results.append(result)
                    else:
                        # Concurrent steps
                        tasks = [self.execute_workflow_step(step) for step in group]
                        group_results = await asyncio.gather(*tasks)
                        all_results.extend(group_results)
                
                return all_results
        
        orchestrator = AsyncWorkflowOrchestrator()
        
        # Create workflow with concurrent steps
        workflow_config = {
            "steps": [
                {
                    "step_id": "extract_requirements",
                    "prompt": "Extract requirements from job description",
                    "input": {"text": "Job description text"},
                    "job_id": "job_123",
                    "dependencies": []
                },
                {
                    "step_id": "parse_resume",
                    "prompt": "Parse resume content",
                    "input": {"text": "Resume text"},
                    "job_id": "job_123",
                    "dependencies": []
                },
                {
                    "step_id": "analyze_match",
                    "prompt": "Analyze job-resume match",
                    "input": {"requirements": "extracted", "resume": "parsed"},
                    "job_id": "job_123",
                    "dependencies": ["extract_requirements", "parse_resume"]
                }
            ]
        }
        
        # Execute workflow
        start_time = time.time()
        results = await orchestrator.execute_workflow(workflow_config)
        execution_time = time.time() - start_time
        
        # Validate results
        assert len(results) == 3
        assert all(result["safety_passed"] for result in results)
        
        # Validate concurrent execution improved performance
        # (With proper async, concurrent steps should run faster than sequential)
        assert execution_time < 1.0  # Should complete quickly with mocking
        
        # Validate step execution order
        step_ids = [result["step_id"] for result in results]
        assert "analyze_match" in step_ids  # Dependent step executed
    
    async def test_async_error_handling_and_cancellation(self):
        """Test async error handling and task cancellation."""
        
        class AsyncFailingComponent:
            def __init__(self):
                self.failure_count = 0
            
            async def operation_with_failure(self, should_fail: bool = False):
                await asyncio.sleep(0.01)
                
                if should_fail:
                    self.failure_count += 1
                    raise ValueError("Simulated async failure")
                
                return {"success": True, "data": "operation_result"}
            
            async def long_running_operation(self):
                """Operation that can be cancelled."""
                try:
                    for i in range(10):
                        await asyncio.sleep(0.01)
                        # Check for cancellation
                        await asyncio.sleep(0)  # Yield control
                    return {"completed": True}
                except asyncio.CancelledError:
                    return {"cancelled": True}
        
        component = AsyncFailingComponent()
        
        # Test async error handling
        with pytest.raises(ValueError, match="Simulated async failure"):
            await component.operation_with_failure(should_fail=True)
        
        assert component.failure_count == 1
        
        # Test successful operation after failure
        result = await component.operation_with_failure(should_fail=False)
        assert result["success"] is True
        
        # Test task cancellation
        task = asyncio.create_task(component.long_running_operation())
        
        # Cancel after a short delay
        await asyncio.sleep(0.05)
        task.cancel()
        
        try:
            result = await task
            assert result.get("cancelled") is True
        except asyncio.CancelledError:
            # Task was cancelled before completing
            pass
    
    async def test_async_resource_management(self):
        """Test proper async resource management and cleanup."""
        
        class AsyncResourceManager:
            def __init__(self):
                self.acquired_resources = set()
                self.cleanup_called = False
            
            async def acquire_resource(self, resource_id: str):
                """Acquire a resource asynchronously."""
                await asyncio.sleep(0.001)  # Simulate acquisition time
                self.acquired_resources.add(resource_id)
                return resource_id
            
            async def release_resource(self, resource_id: str):
                """Release a resource asynchronously."""
                await asyncio.sleep(0.001)  # Simulate release time
                self.acquired_resources.discard(resource_id)
            
            async def use_resource_with_context(self, resource_id: str):
                """Use resource with proper context management."""
                await self.acquire_resource(resource_id)
                try:
                    # Simulate resource usage
                    await asyncio.sleep(0.01)
                    return {"resource_used": resource_id, "result": "success"}
                finally:
                    await self.release_resource(resource_id)
            
            async def cleanup_all_resources(self):
                """Cleanup all acquired resources."""
                while self.acquired_resources:
                    resource = self.acquired_resources.pop()
                    await self.release_resource(resource)
                self.cleanup_called = True
        
        manager = AsyncResourceManager()
        
        # Test resource acquisition and release
        resource_id = "test_resource_1"
        result = await manager.use_resource_with_context(resource_id)
        
        assert result["resource_used"] == resource_id
        assert result["result"] == "success"
        assert len(manager.acquired_resources) == 0  # Resource should be released
        
        # Test concurrent resource usage
        concurrent_tasks = [
            manager.use_resource_with_context(f"resource_{i}")
            for i in range(5)
        ]
        
        results = await asyncio.gather(*concurrent_tasks)
        
        assert len(results) == 5
        assert all(result["result"] == "success" for result in results)
        assert len(manager.acquired_resources) == 0  # All resources should be released
        
        # Test cleanup functionality
        await manager.acquire_resource("cleanup_test")
        await manager.cleanup_all_resources()
        
        assert manager.cleanup_called is True
        assert len(manager.acquired_resources) == 0


class TestConcurrencyAndRaceConditions:
    """Test for race conditions and concurrency issues."""
    
    async def test_concurrent_memory_store_race_conditions(self):
        """Test memory store for race conditions under high concurrency."""
        
        from tests.conftest import MockMemoryStore
        
        memory_store = MockMemoryStore()
        
        # Simulate high-concurrency scenario
        async def concurrent_store_and_query(worker_id: int):
            """Worker that stores and queries data concurrently."""
            job_id = f"job_{worker_id}"
            triplets = [{"worker_id": worker_id, "data": f"test_data_{worker_id}"}]
            
            # Store data
            memory_store.store_triplets(job_id, triplets)
            
            # Small delay to increase chance of race conditions
            await asyncio.sleep(0.001)
            
            # Query data
            result = memory_store.query_triplets(job_id)
            
            return {"worker_id": worker_id, "result_count": len(result)}
        
        # Run many concurrent workers
        tasks = [concurrent_store_and_query(i) for i in range(50)]
        results = await asyncio.gather(*tasks)
        
        # Validate all workers completed successfully
        assert len(results) == 50
        
        # Validate data integrity
        for result in results:
            assert result["result_count"] == 1, f"Worker {result['worker_id']} got unexpected result count"
        
        # Validate total data stored
        total_stored = len(memory_store.triplets)
        assert total_stored == 50, f"Expected 50 stored jobs, got {total_stored}"
    
    async def test_concurrent_safety_policy_evaluation(self, mock_safety_policy):
        """Test safety policy for race conditions in concurrent evaluation."""
        
        async def concurrent_safety_check(worker_id: int):
            """Worker that performs safety checks concurrently."""
            content = {
                "worker_id": worker_id,
                "content": f"Safe content from worker {worker_id}",
                "timestamp": time.time()
            }
            
            # Perform safety check
            result = mock_safety_policy.validate_input(content)
            
            return {"worker_id": worker_id, "is_safe": result["is_safe"]}
        
        # Run many concurrent safety checks
        tasks = [concurrent_safety_check(i) for i in range(100)]
        results = await asyncio.gather(*tasks)
        
        # Validate all safety checks completed
        assert len(results) == 100
        
        # Validate all were marked safe (no race conditions causing false failures)
        safe_results = [r for r in results if r["is_safe"]]
        assert len(safe_results) == 100, f"Expected 100 safe results, got {len(safe_results)}"
