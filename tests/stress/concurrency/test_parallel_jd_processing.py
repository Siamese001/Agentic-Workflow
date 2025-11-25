"""
Stress Tests - Concurrency and Parallel JD Processing

Tests system behavior under concurrent load with multiple job descriptions processed simultaneously.
Validates race-free execution, data isolation, and resource safety under parallel workload.
"""

import pytest
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

# Mark all tests in this module as stress/concurrency tests
pytestmark = [pytest.mark.stress, pytest.mark.concurrency, pytest.mark.slow]


@dataclass(frozen=True)
class MockJobDescription:
    """Mock job description for concurrent processing tests."""
    job_id: str
    company: str
    title: str
    requirements: List[str]
    description: str
    processing_priority: int = 1


@dataclass(frozen=True)
class MockProcessingResult:
    """Mock processing result for concurrent job processing."""
    job_id: str
    success: bool
    result_data: Optional[Dict[str, Any]]
    error: Optional[str]
    processing_time: float
    thread_id: Optional[str]
    workflow_id: str


class TestParallelJDProcessing:
    """Test concurrent processing of multiple job descriptions."""
    
    def test_basic_parallel_execution(self):
        """Test basic parallel execution of multiple JDs."""
        # Create test job descriptions
        job_descriptions = [
            MockJobDescription(
                job_id=f"job_{i}",
                company=f"Company_{i}",
                title=f"Software Engineer_{i}",
                requirements=["Python", "SQL"],
                description=f"Job description {i}"
            )
            for i in range(5)
        ]
        
        # Mock processing function
        def process_single_job(job: MockJobDescription) -> MockProcessingResult:
            thread_id = threading.current_thread().ident
            start_time = time.time()
            
            # Simulate processing time
            time.sleep(0.1)
            
            processing_time = time.time() - start_time
            workflow_id = str(uuid.uuid4())
            
            return MockProcessingResult(
                job_id=job.job_id,
                success=True,
                result_data={"match_score": 0.8, "analysis": f"Analysis for {job.job_id}"},
                error=None,
                processing_time=processing_time,
                thread_id=str(thread_id),
                workflow_id=workflow_id
            )
        
        # Execute jobs in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_job = {
                executor.submit(process_single_job, job): job 
                for job in job_descriptions
            }
            
            results = []
            for future in as_completed(future_to_job):
                result = future.result()
                results.append(result)
        
        # Verify parallel execution
        assert len(results) == 5
        assert all(result.success for result in results)
        
        # Verify thread diversity (multiple threads were used)
        thread_ids = set(result.thread_id for result in results)
        assert len(thread_ids) >= 2  # Should use multiple threads
        
        # Verify job isolation
        job_ids = [result.job_id for result in results]
        assert len(set(job_ids)) == 5  # All unique job IDs
        assert all(result.workflow_id != results[0].workflow_id for result in results[1:])  # Unique workflow IDs
    
    def test_concurrent_state_isolation(self):
        """Test that concurrent jobs maintain isolated state."""
        # Shared state that should remain isolated per job
        shared_state_store = {}
        
        def process_job_with_isolated_state(job: MockJobDescription) -> MockProcessingResult:
            # Create job-specific state
            job_state = {
                "job_id": job.job_id,
                "processing_data": f"data_for_{job.job_id}",
                "intermediate_results": [],
                "thread_id": threading.current_thread().ident
            }
            
            # Simulate processing steps that modify state
            for step in range(3):
                step_result = f"step_{step}_result_for_{job.job_id}"
                job_state["intermediate_results"].append(step_result)
                time.sleep(0.05)  # Simulate processing time
            
            # Store in shared store (should be properly namespaced)
            shared_state_store[job.job_id] = job_state
            
            return MockProcessingResult(
                job_id=job.job_id,
                success=True,
                result_data=job_state,
                error=None,
                processing_time=0.15,
                thread_id=str(job_state["thread_id"]),
                workflow_id=str(uuid.uuid4())
            )
        
        # Create multiple jobs with similar content
        similar_jobs = [
            MockJobDescription(
                job_id=f"similar_job_{i}",
                company="TechCorp",  # Same company
                title="Software Engineer",  # Same title
                requirements=["Python", "SQL"],  # Same requirements
                description=f"Similar job description {i}"
            )
            for i in range(4)
        ]
        
        # Process jobs concurrently
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(process_job_with_isolated_state, job) 
                for job in similar_jobs
            ]
            results = [future.result() for future in futures]
        
        # Verify state isolation
        assert len(shared_state_store) == 4
        
        # Check that each job has its own isolated state
        for job_id, state in shared_state_store.items():
            assert state["job_id"] == job_id
            assert len(state["intermediate_results"]) == 3
            assert all(job_id in result for result in state["intermediate_results"])
        
        # Verify no cross-contamination
        for result in results:
            job_state = result.result_data
            assert all(job_state["job_id"] in other_result for other_result in job_state["intermediate_results"])
    
    def test_resource_contention_handling(self):
        """Test handling of resource contention under concurrent load."""
        # Mock shared resource with limited capacity
        class MockLimitedResource:
            def __init__(self, max_concurrent=2):
                self.max_concurrent = max_concurrent
                self.current_users = 0
                self.lock = threading.Lock()
                self.access_log = []
            
            def acquire(self, user_id: str):
                with self.lock:
                    if self.current_users >= self.max_concurrent:
                        return False
                    
                    self.current_users += 1
                    self.access_log.append(f"{user_id} acquired at {time.time()}")
                    return True
            
            def release(self, user_id: str):
                with self.lock:
                    if self.current_users > 0:
                        self.current_users -= 1
                        self.access_log.append(f"{user_id} released at {time.time()}")
        
        shared_resource = MockLimitedResource(max_concurrent=2)
        
        def process_job_with_resource_contention(job: MockJobDescription) -> MockProcessingResult:
            # Try to acquire shared resource
            if not shared_resource.acquire(job.job_id):
                return MockProcessingResult(
                    job_id=job.job_id,
                    success=False,
                    result_data=None,
                    error="Resource contention - could not acquire shared resource",
                    processing_time=0.01,
                    thread_id=str(threading.current_thread().ident),
                    workflow_id=str(uuid.uuid4())
                )
            
            try:
                # Simulate work while holding resource
                time.sleep(0.1)
                
                return MockProcessingResult(
                    job_id=job.job_id,
                    success=True,
                    result_data={"processed_with_resource": True},
                    error=None,
                    processing_time=0.1,
                    thread_id=str(threading.current_thread().ident),
                    workflow_id=str(uuid.uuid4())
                )
            finally:
                shared_resource.release(job.job_id)
        
        # Submit more jobs than resource capacity
        jobs = [
            MockJobDescription(f"job_{i}", f"Company_{i}", f"Title_{i}", [], f"Desc_{i}")
            for i in range(6)
        ]
        
        # Process with high concurrency
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(process_job_with_resource_contention, job) 
                for job in jobs
            ]
            results = [future.result() for future in futures]
        
        # Verify contention handling
        successful_jobs = [r for r in results if r.success]
        failed_jobs = [r for r in results if not r.success]
        
        # Some should succeed, some should fail due to contention
        assert len(successful_jobs) >= 2  # At least the resource capacity
        assert len(failed_jobs) >= 1     # Some should fail due to contention
        
        # Verify failed jobs have appropriate error messages
        assert all("Resource contention" in job.error for job in failed_jobs)
    
    def test_concurrent_safety_policy_enforcement(self):
        """Test safety policy enforcement under concurrent conditions."""
        # Mock safety policy that should be consistently applied
        class MockSafetyPolicy:
            def __init__(self):
                self.validation_count = 0
                self.blocked_count = 0
                self.lock = threading.Lock()
            
            def validate_input(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
                with self.lock:
                    self.validation_count += 1
                
                # Simulate safety check
                if "malicious" in job_data.get("description", "").lower():
                    with self.lock:
                        self.blocked_count += 1
                    return {"is_safe": False, "reason": "Malicious content detected"}
                
                return {"is_safe": True, "reason": "Content safe"}
        
        safety_policy = MockSafetyPolicy()
        
        def process_job_with_safety_check(job: MockJobDescription) -> MockProcessingResult:
            job_data = {
                "job_id": job.job_id,
                "description": job.description,
                "company": job.company
            }
            
            # Apply safety policy
            safety_result = safety_policy.validate_input(job_data)
            
            if not safety_result["is_safe"]:
                return MockProcessingResult(
                    job_id=job.job_id,
                    success=False,
                    result_data=None,
                    error=f"Blocked by safety policy: {safety_result['reason']}",
                    processing_time=0.01,
                    thread_id=str(threading.current_thread().ident),
                    workflow_id=str(uuid.uuid4())
                )
            
            # Process normally if safe
            time.sleep(0.05)
            return MockProcessingResult(
                job_id=job.job_id,
                success=True,
                result_data={"processed_safely": True},
                error=None,
                processing_time=0.05,
                thread_id=str(threading.current_thread().ident),
                workflow_id=str(uuid.uuid4())
            )
        
        # Mix of safe and malicious jobs
        mixed_jobs = [
            MockJobDescription(f"safe_job_{i}", f"Company_{i}", f"Title_{i}", [], f"Safe description {i}")
            for i in range(4)
        ] + [
            MockJobDescription(f"malicious_job_{i}", f"Company_{i}", f"Title_{i}", [], f"Malicious content {i}")
            for i in range(2)
        ]
        
        # Process concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(process_job_with_safety_check, job) 
                for job in mixed_jobs
            ]
            results = [future.result() for future in futures]
        
        # Verify safety enforcement
        safe_results = [r for r in results if r.success]
        blocked_results = [r for r in results if not r.success]
        
        assert len(safe_results) == 4  # All safe jobs should pass
        assert len(blocked_results) == 2  # All malicious jobs should be blocked
        
        # Verify safety policy was applied consistently
        assert safety_policy.validation_count == 6  # All jobs validated
        assert safety_policy.blocked_count == 2    # Malicious jobs blocked
        
        # Verify blocked jobs have appropriate error messages
        assert all("safety policy" in job.error for job in blocked_results)
    
    def test_memory_store_concurrency(self):
        """Test concurrent access to memory/store operations."""
        # Mock thread-safe memory store
        class MockMemoryStore:
            def __init__(self):
                self.data = {}
                self.access_log = []
                self.lock = threading.RLock()  # Reentrant lock for nested operations
            
            def store_triplets(self, job_id: str, triplets: List[Dict]):
                with self.lock:
                    if job_id not in self.data:
                        self.data[job_id] = []
                    self.data[job_id].extend(triplets)
                    self.access_log.append(f"{job_id} stored {len(triplets)} triplets")
            
            def query_triplets(self, job_id: str) -> List[Dict]:
                with self.lock:
                    result = self.data.get(job_id, [])
                    self.access_log.append(f"{job_id} queried {len(result)} triplets")
                    return result.copy()
            
            def get_job_count(self) -> int:
                with self.lock:
                    return len(self.data)
        
        memory_store = MockMemoryStore()
        
        def process_job_with_memory_operations(job: MockJobDescription) -> MockProcessingResult:
            thread_id = threading.current_thread().ident
            
            # Generate job-specific triplets
            triplets = [
                {"subject": f"Person_{job.job_id}", "predicate": "has_skill", "object": skill}
                for skill in job.requirements
            ]
            
            # Store triplets
            memory_store.store_triplets(job.job_id, triplets)
            
            # Simulate processing delay
            time.sleep(0.05)
            
            # Query back triplets
            retrieved_triplets = memory_store.query_triplets(job.job_id)
            
            return MockProcessingResult(
                job_id=job.job_id,
                success=True,
                result_data={
                    "stored_triplets": len(triplets),
                    "retrieved_triplets": len(retrieved_triplets),
                    "triplets_match": len(triplets) == len(retrieved_triplets)
                },
                error=None,
                processing_time=0.05,
                thread_id=str(thread_id),
                workflow_id=str(uuid.uuid4())
            )
        
        # Create jobs with varying requirements
        concurrent_jobs = [
            MockJobDescription(
                job_id=f"memory_job_{i}",
                company=f"Company_{i}",
                title=f"Title_{i}",
                requirements=[f"Skill_{i}_{j}" for j in range(3)],
                description=f"Description {i}"
            )
            for i in range(8)
        ]
        
        # Process with high concurrency
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(process_job_with_memory_operations, job) 
                for job in concurrent_jobs
            ]
            results = [future.result() for future in futures]
        
        # Verify memory operations
        assert all(result.success for result in results)
        assert memory_store.get_job_count() == 8
        
        # Verify data integrity
        for result in results:
            data = result.result_data
            assert data["stored_triplets"] == 3
            assert data["retrieved_triplets"] == 3
            assert data["triplets_match"] is True
        
        # Verify all jobs have isolated data
        for job in concurrent_jobs:
            job_triplets = memory_store.query_triplets(job.job_id)
            assert len(job_triplets) == 3
            assert all(f"Person_{job.job_id}" in t["subject"] for t in job_triplets)


class TestConcurrencyPerformanceAndScaling:
    """Test performance characteristics under concurrent load."""
    
    def test_scalability_analysis(self):
        """Test scalability with increasing concurrent load."""
        def process_job(job: MockJobDescription) -> MockProcessingResult:
            start_time = time.time()
            time.sleep(0.1)  # Simulate consistent processing time
            processing_time = time.time() - start_time
            
            return MockProcessingResult(
                job_id=job.job_id,
                success=True,
                result_data={"processed": True},
                error=None,
                processing_time=processing_time,
                thread_id=str(threading.current_thread().ident),
                workflow_id=str(uuid.uuid4())
            )
        
        # Test with different concurrency levels
        concurrency_levels = [1, 2, 4, 8]
        jobs_per_level = 8
        
        performance_results = {}
        
        for max_workers in concurrency_levels:
            jobs = [
                MockJobDescription(f"job_{i}", f"Company_{i}", f"Title_{i}", [], f"Desc_{i}")
                for i in range(jobs_per_level)
            ]
            
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(process_job, job) 
                    for job in jobs
                ]
                results = [future.result() for future in futures]
            
            total_time = time.time() - start_time
            
            performance_results[max_workers] = {
                "total_time": total_time,
                "avg_processing_time": sum(r.processing_time for r in results) / len(results),
                "throughput": jobs_per_level / total_time,
                "threads_used": len(set(r.thread_id for r in results))
            }
        
        # Verify scalability improvements
        assert performance_results[1]["total_time"] > performance_results[2]["total_time"]
        assert performance_results[2]["total_time"] > performance_results[4]["total_time"]
        
        # Throughput should increase with concurrency (up to a point)
        assert performance_results[4]["throughput"] > performance_results[1]["throughput"]
        
        # Thread utilization should increase with max_workers
        assert performance_results[8]["threads_used"] >= performance_results[1]["threads_used"]
    
    def test_performance_degradation_under_contention(self):
        """Test performance degradation when resource contention occurs."""
        # Mock resource with high contention potential
        class MockContentedResource:
            def __init__(self):
                self.lock = threading.Lock()
                self.access_count = 0
            
            def slow_operation(self, job_id: str):
                with self.lock:
                    self.access_count += 1
                    time.sleep(0.2)  # Slow operation holding lock
        
        contested_resource = MockContentedResource()
        
        def process_job_with_contention(job: MockJobDescription) -> MockProcessingResult:
            start_time = time.time()
            
            # All jobs compete for the same slow resource
            contested_resource.slow_operation(job.job_id)
            
            processing_time = time.time() - start_time
            
            return MockProcessingResult(
                job_id=job.job_id,
                success=True,
                result_data={"processed": True},
                error=None,
                processing_time=processing_time,
                thread_id=str(threading.current_thread().ident),
                workflow_id=str(uuid.uuid4())
            )
        
        # Process with high concurrency to induce contention
        jobs = [
            MockJobDescription(f"contented_job_{i}", f"Company_{i}", f"Title_{i}", [], f"Desc_{i}")
            for i in range(6)
        ]
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(process_job_with_contention, job) 
                for job in jobs
            ]
            results = [future.result() for future in futures]
        
        total_time = time.time() - start_time
        
        # Under contention, total time should be much higher than ideal parallel time
        ideal_parallel_time = 0.2  # Single operation time
        actual_time_per_job = [r.processing_time for r in results]
        
        assert total_time > ideal_parallel_time * 2  # Should show contention impact
        assert contested_resource.access_count == 6  # All jobs accessed resource
        
        # Processing times should vary due to contention
        assert max(actual_time_per_job) > min(actual_time_per_job)


class TestConcurrencyErrorRecovery:
    """Test error recovery and resilience under concurrent conditions."""
    
    def test_partial_failure_isolation(self):
        """Test that failures in some jobs don't affect others."""
        failure_rate = 0.3  # 30% of jobs should fail
        
        def process_job_with_random_failures(job: MockJobDescription) -> MockProcessingResult:
            # Simulate random failures based on job ID
            job_number = int(job.job_id.split("_")[-1])
            should_fail = (job_number % 10) < (failure_rate * 10)
            
            if should_fail:
                return MockProcessingResult(
                    job_id=job.job_id,
                    success=False,
                    result_data=None,
                    error="Simulated processing failure",
                    processing_time=0.01,
                    thread_id=str(threading.current_thread().ident),
                    workflow_id=str(uuid.uuid4())
                )
            
            time.sleep(0.05)
            return MockProcessingResult(
                job_id=job.job_id,
                success=True,
                result_data={"processed": True},
                error=None,
                processing_time=0.05,
                thread_id=str(threading.current_thread().ident),
                workflow_id=str(uuid.uuid4())
            )
        
        # Process batch of jobs
        jobs = [
            MockJobDescription(f"job_{i}", f"Company_{i}", f"Title_{i}", [], f"Desc_{i}")
            for i in range(10)
        ]
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(process_job_with_random_failures, job) 
                for job in jobs
            ]
            results = [future.result() for future in futures]
        
        # Verify failure isolation
        successful_jobs = [r for r in results if r.success]
        failed_jobs = [r for r in results if not r.success]
        
        # Should have both successes and failures
        assert len(successful_jobs) > 0
        assert len(failed_jobs) > 0
        assert len(successful_jobs) + len(failed_jobs) == 10
        
        # Failed jobs should have specific error messages
        assert all(job.error == "Simulated processing failure" for job in failed_jobs)
        
        # Successful jobs should have valid results
        assert all(job.result_data is not None for job in successful_jobs)
    
    def test_timeout_handling_under_load(self):
        """Test timeout handling when system is under load."""
        timeout_threshold = 0.15  # 150ms timeout
        
        def process_job_with_variable_delay(job: MockJobDescription) -> MockProcessingResult:
            start_time = time.time()
            
            # Simulate variable processing delays
            job_number = int(job.job_id.split("_")[-1])
            delay = 0.1 + (job_number % 5) * 0.05  # Variable delay: 0.1s to 0.3s
            
            time.sleep(delay)
            
            processing_time = time.time() - start_time
            
            # Check if exceeded timeout
            if processing_time > timeout_threshold:
                return MockProcessingResult(
                    job_id=job.job_id,
                    success=False,
                    result_data=None,
                    error=f"Processing timeout: {processing_time:.3f}s > {timeout_threshold}s",
                    processing_time=processing_time,
                    thread_id=str(threading.current_thread().ident),
                    workflow_id=str(uuid.uuid4())
                )
            
            return MockProcessingResult(
                job_id=job.job_id,
                success=True,
                result_data={"processed": True},
                error=None,
                processing_time=processing_time,
                thread_id=str(threading.current_thread().ident),
                workflow_id=str(uuid.uuid4())
            )
        
        # Process jobs with variable delays
        jobs = [
            MockJobDescription(f"job_{i}", f"Company_{i}", f"Title_{i}", [], f"Desc_{i}")
            for i in range(8)
        ]
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(process_job_with_variable_delay, job) 
                for job in jobs
            ]
            results = [future.result() for future in futures]
        
        # Verify timeout handling
        successful_jobs = [r for r in results if r.success]
        timeout_jobs = [r for r in results if not r.success and "timeout" in r.error]
        
        # Should have both successful and timed-out jobs
        assert len(successful_jobs) > 0
        assert len(timeout_jobs) > 0
        
        # Verify timeout error messages
        assert all("timeout" in job.error for job in timeout_jobs)
        assert all(job.processing_time > timeout_threshold for job in timeout_jobs)
        
        # Successful jobs should be within timeout
        assert all(job.processing_time <= timeout_threshold for job in successful_jobs)
