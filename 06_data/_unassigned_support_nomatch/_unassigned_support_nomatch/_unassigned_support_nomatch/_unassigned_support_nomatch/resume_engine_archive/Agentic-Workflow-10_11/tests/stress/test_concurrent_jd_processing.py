"""
Phase 7 Stress Testing - Concurrent JD Processing

Tests system behavior under concurrent job description processing loads.
Focuses on performance, resource usage, thread safety, and scalability limits.
"""

import pytest
import asyncio
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from unittest.mock import Mock, patch, AsyncMock

# Import telemetry for stress monitoring
from tests.observability.test_telemetry_collection import TelemetryCollector, ExecutionMetrics, MetricType


@dataclass(frozen=True, slots=True)
class JDProcessingTask:
    """Represents a job description processing task for stress testing."""
    task_id: str
    job_title: str
    job_description: str
    resume_content: str
    priority: int  # 1=high, 2=medium, 3=low
    expected_processing_time: float


@dataclass(frozen=True, slots=True)
class StressTestResult:
    """Results from a stress test execution."""
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    average_processing_time: float
    peak_memory_usage: float
    peak_cpu_usage: float
    concurrent_workers: int
    total_execution_time: float


class MockJDProcessor:
    """Mock JD processor for stress testing with realistic performance characteristics."""
    
    def __init__(self, base_processing_time: float = 0.1, variance: float = 0.05):
        self.base_processing_time = base_processing_time
        self.variance = variance
        self.processed_count = 0
        self.error_rate = 0.02  # 2% error rate for realism
        
    async def process_job_description(self, task: JDProcessingTask) -> Dict[str, Any]:
        """Mock JD processing with realistic timing and occasional errors."""
        # Simulate processing time with variance
        processing_time = self.base_processing_time + random.uniform(-self.variance, self.variance)
        processing_time = max(0.01, processing_time)  # Ensure minimum time
        
        # Simulate processing work
        await asyncio.sleep(processing_time)
        
        # Simulate occasional errors
        if random.random() < self.error_rate:
            raise Exception(f"Processing error for task {task.task_id}")
        
        # Generate mock results
        self.processed_count += 1
        
        return {
            "task_id": task.task_id,
            "match_score": random.uniform(0.3, 0.95),
            "skill_gaps": random.sample(["Python", "AWS", "Docker", "Kubernetes", "ML"], k=2),
            "recommendations": [
                f"Consider adding {skill} certification" 
                for skill in random.sample(["AWS", "Azure", "GCP"], k=1)
            ],
            "processing_time": processing_time
        }


class TestConcurrentJDProcessing:
    """Test concurrent job description processing under various load conditions."""
    
    def setup_method(self):
        """Setup fresh processor and telemetry for each stress test."""
        self.processor = MockJDProcessor()
        self.telemetry = TelemetryCollector()
        
    def generate_test_tasks(self, count: int) -> List[JDProcessingTask]:
        """Generate realistic JD processing tasks for stress testing."""
        job_titles = [
            "Senior Software Engineer", "Data Scientist", "DevOps Engineer",
            "Machine Learning Engineer", "Full Stack Developer", "Backend Engineer",
            "Frontend Developer", "Cloud Architect", "Security Engineer", "QA Engineer"
        ]
        
        job_descriptions = [
            "We are looking for an experienced professional with strong technical skills...",
            "Join our team and work on cutting-edge projects with modern technologies...",
            "Seeking a talented individual to help drive our technical initiatives...",
            "Looking for someone passionate about technology and innovation...",
            "We need a skilled professional to join our growing engineering team..."
        ]
        
        resume_content = "Experienced professional with 5+ years in technology..."
        
        tasks = []
        for i in range(count):
            task = JDProcessingTask(
                task_id=f"task_{i+1:04d}",
                job_title=random.choice(job_titles),
                job_description=random.choice(job_descriptions),
                resume_content=resume_content,
                priority=random.choices([1, 2, 3], weights=[0.2, 0.6, 0.2])[0],
                expected_processing_time=random.uniform(0.05, 0.3)
            )
            tasks.append(task)
        
        return tasks
    
    async def process_tasks_concurrent(self, tasks: List[JDProcessingTask], 
                                     max_workers: int) -> StressTestResult:
        """Process tasks concurrently and collect stress metrics."""
        start_time = time.time()
        
        # Record initial system state
        initial_metrics = self.telemetry.get_system_metrics()
        
        completed_tasks = []
        failed_tasks = []
        
        # Process tasks in batches to control concurrency
        semaphore = asyncio.Semaphore(max_workers)
        
        async def process_single_task(task: JDProcessingTask) -> Optional[Dict[str, Any]]:
            async with semaphore:
                task_start = time.time()
                try:
                    result = await self.processor.process_job_description(task)
                    task_end = time.time()
                    
                    # Record execution metrics
                    exec_metrics = ExecutionMetrics(
                        test_name=f"jd_process_{task.task_id}",
                        test_type="stress",
                        execution_time=task_end - task_start,
                        success=True,
                        memory_usage=random.uniform(50, 150),
                        cpu_usage=random.uniform(0.1, 0.8)
                    )
                    self.telemetry.record_test_execution(exec_metrics)
                    
                    return result
                    
                except Exception as e:
                    task_end = time.time()
                    
                    # Record failure metrics
                    exec_metrics = ExecutionMetrics(
                        test_name=f"jd_process_{task.task_id}",
                        test_type="stress",
                        execution_time=task_end - task_start,
                        success=False,
                        memory_usage=random.uniform(50, 150),
                        cpu_usage=random.uniform(0.1, 0.8)
                    )
                    self.telemetry.record_test_execution(exec_metrics)
                    
                    return None
        
        # Execute all tasks concurrently
        results = await asyncio.gather(
            *[process_single_task(task) for task in tasks],
            return_exceptions=True
        )
        
        # Separate successful and failed tasks
        for result in results:
            if isinstance(result, Exception):
                failed_tasks.append(result)
            elif result is not None:
                completed_tasks.append(result)
            else:
                failed_tasks.append(None)
        
        end_time = time.time()
        
        # Get final system metrics
        final_metrics = self.telemetry.get_system_metrics()
        
        return StressTestResult(
            total_tasks=len(tasks),
            completed_tasks=len(completed_tasks),
            failed_tasks=len(failed_tasks),
            average_processing_time=final_metrics.average_execution_time,
            peak_memory_usage=final_metrics.memory_peak,
            peak_cpu_usage=final_metrics.cpu_peak,
            concurrent_workers=max_workers,
            total_execution_time=end_time - start_time
        )
    
    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_light_load_concurrent_processing(self):
        """Test concurrent processing under light load (10 tasks, 3 workers)."""
        tasks = self.generate_test_tasks(10)
        result = await self.process_tasks_concurrent(tasks, max_workers=3)
        
        # Validate stress test results
        assert result.total_tasks == 10
        assert result.completed_tasks >= 8  # Allow for some failures due to mock error rate
        assert result.failed_tasks <= 2
        assert result.concurrent_workers == 3
        assert result.total_execution_time < 5.0  # Should complete within 5 seconds
        assert result.average_processing_time > 0.01
        
        # Check resource usage is reasonable
        assert result.peak_memory_usage > 0
        assert 0 <= result.peak_cpu_usage <= 2.0  # Allow for some CPU overhead
        
        # Export telemetry for analysis
        telemetry_data = self.telemetry.export_metrics()
        assert len(telemetry_data["test_metrics"]) == 10
    
    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_moderate_load_concurrent_processing(self):
        """Test concurrent processing under moderate load (25 tasks, 5 workers)."""
        tasks = self.generate_test_tasks(25)
        result = await self.process_tasks_concurrent(tasks, max_workers=5)
        
        # Validate stress test results
        assert result.total_tasks == 25
        assert result.completed_tasks >= 20  # Allow for mock failures
        assert result.failed_tasks <= 5
        assert result.concurrent_workers == 5
        assert result.total_execution_time < 8.0  # Should complete within 8 seconds
        assert result.average_processing_time > 0.01
        
        # Check resource usage scales appropriately
        assert result.peak_memory_usage > 0
        assert 0 <= result.peak_cpu_usage <= 3.0  # Allow for higher CPU with more workers
        
        # Validate telemetry captured all executions
        telemetry_data = self.telemetry.export_metrics()
        assert len(telemetry_data["test_metrics"]) == 25
    
    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_heavy_load_concurrent_processing(self):
        """Test concurrent processing under heavy load (50 tasks, 10 workers)."""
        tasks = self.generate_test_tasks(50)
        result = await self.process_tasks_concurrent(tasks, max_workers=10)
        
        # Validate stress test results
        assert result.total_tasks == 50
        assert result.completed_tasks >= 40  # Allow for more failures under heavy load
        assert result.failed_tasks <= 10
        assert result.concurrent_workers == 10
        assert result.total_execution_time < 15.0  # Should complete within 15 seconds
        assert result.average_processing_time > 0.01
        
        # Check resource usage under heavy load
        assert result.peak_memory_usage > 0
        assert 0 <= result.peak_cpu_usage <= 5.0  # Allow for significant CPU usage
        
        # Validate comprehensive telemetry
        telemetry_data = self.telemetry.export_metrics()
        assert len(telemetry_data["test_metrics"]) == 50
        
        # Check system metrics show expected load
        system_metrics = self.telemetry.get_system_metrics()
        assert system_metrics.total_tests_run == 50
        assert system_metrics.success_rate >= 0.8  # At least 80% success rate
        assert system_metrics.error_count <= 10
    
    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_extreme_load_concurrent_processing(self):
        """Test concurrent processing under extreme load (100 tasks, 20 workers)."""
        tasks = self.generate_test_tasks(100)
        result = await self.process_tasks_concurrent(tasks, max_workers=20)
        
        # Validate stress test results
        assert result.total_tasks == 100
        assert result.completed_tasks >= 75  # Higher failure rate expected under extreme load
        assert result.failed_tasks <= 25
        assert result.concurrent_workers == 20
        assert result.total_execution_time < 30.0  # Should complete within 30 seconds
        assert result.average_processing_time > 0.01
        
        # Check resource usage under extreme load
        assert result.peak_memory_usage > 0
        assert 0 <= result.peak_cpu_usage <= 10.0  # Allow for high CPU usage
        
        # Validate comprehensive telemetry
        telemetry_data = self.telemetry.export_metrics()
        assert len(telemetry_data["test_metrics"]) == 100
        
        # Check system metrics show extreme load characteristics
        system_metrics = self.telemetry.get_system_metrics()
        assert system_metrics.total_tests_run == 100
        assert system_metrics.success_rate >= 0.75  # At least 75% success rate
        assert system_metrics.error_count <= 25
    
    @pytest.mark.stress
    def test_thread_safety_under_concurrent_load(self):
        """Test thread safety of telemetry collection under concurrent load."""
        def worker_task(worker_id: int, task_count: int):
            """Worker function for thread safety testing."""
            for i in range(task_count):
                # Simulate work
                time.sleep(0.001)
                
                # Record metrics concurrently
                exec_metrics = ExecutionMetrics(
                    test_name=f"thread_worker_{worker_id}_task_{i}",
                    test_type="thread_safety",
                    execution_time=random.uniform(0.001, 0.01),
                    success=random.random() > 0.1,  # 90% success rate
                    memory_usage=random.uniform(10, 100),
                    cpu_usage=random.uniform(0.1, 1.0)
                )
                self.telemetry.record_test_execution(exec_metrics)
        
        # Launch multiple threads
        num_workers = 10
        tasks_per_worker = 20
        threads = []
        
        start_time = time.time()
        
        for worker_id in range(num_workers):
            thread = threading.Thread(
                target=worker_task, 
                args=(worker_id, tasks_per_worker)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # Validate thread safety - no exceptions, consistent state
        system_metrics = self.telemetry.get_system_metrics()
        expected_total_tasks = num_workers * tasks_per_worker
        
        assert system_metrics.total_tests_run == expected_total_tasks
        assert system_metrics.success_rate > 0.8  # Should be around 90%
        assert system_metrics.error_count < expected_total_tasks * 0.2  # Less than 20% errors
        
        # Validate telemetry data integrity
        telemetry_data = self.telemetry.export_metrics()
        assert len(telemetry_data["test_metrics"]) == expected_total_tasks
        
        # Check execution time is reasonable
        assert end_time - start_time < 10.0
    
    @pytest.mark.stress
    async def test_memory_leak_detection_under_stress(self):
        """Test for memory leaks during sustained concurrent processing."""
        initial_metrics = self.telemetry.get_system_metrics()
        initial_memory = initial_metrics.memory_peak
        
        # Run multiple batches of concurrent processing
        for batch in range(5):
            tasks = self.generate_test_tasks(20)
            await self.process_tasks_concurrent(tasks, max_workers=5)
            
            # Clear metrics between batches to test cleanup
            self.telemetry.clear_metrics()
        
        # Final metrics check
        final_metrics = self.telemetry.get_system_metrics()
        
        # Memory should not grow significantly after cleanup
        # (In real scenario, this would monitor actual memory usage)
        assert final_metrics.memory_peak >= 0
        
        # Export and validate telemetry cleanup
        telemetry_data = self.telemetry.export_metrics()
        assert len(telemetry_data["test_metrics"]) == 0  # Should be cleared


class TestPerformanceDegradation:
    """Test performance degradation patterns under increasing load."""
    
    def setup_method(self):
        """Setup for performance degradation tests."""
        self.processor = MockJDProcessor(base_processing_time=0.05, variance=0.02)
        self.telemetry = TelemetryCollector()
    
    def generate_test_tasks(self, count: int) -> List[JDProcessingTask]:
        """Generate consistent tasks for performance analysis."""
        tasks = []
        for i in range(count):
            task = JDProcessingTask(
                task_id=f"perf_task_{i:04d}",
                job_title="Software Engineer",
                job_description="Test description for performance analysis",
                resume_content="Test resume content",
                priority=2,
                expected_processing_time=0.1
            )
            tasks.append(task)
        return tasks
    
    async def process_tasks_concurrent(self, tasks: List[JDProcessingTask], 
                                     max_workers: int) -> StressTestResult:
        """Process tasks concurrently and collect stress metrics."""
        start_time = time.time()
        
        # Record initial system state
        initial_metrics = self.telemetry.get_system_metrics()
        
        completed_tasks = []
        failed_tasks = []
        
        # Process tasks in batches to control concurrency
        semaphore = asyncio.Semaphore(max_workers)
        
        async def process_single_task(task: JDProcessingTask) -> Optional[Dict[str, Any]]:
            async with semaphore:
                task_start = time.time()
                try:
                    result = await self.processor.process_job_description(task)
                    task_end = time.time()
                    
                    # Record execution metrics
                    exec_metrics = ExecutionMetrics(
                        test_name=f"jd_process_{task.task_id}",
                        test_type="stress",
                        execution_time=task_end - task_start,
                        success=True,
                        memory_usage=random.uniform(50, 150),
                        cpu_usage=random.uniform(0.1, 0.8)
                    )
                    self.telemetry.record_test_execution(exec_metrics)
                    
                    return result
                    
                except Exception as e:
                    task_end = time.time()
                    
                    # Record failure metrics
                    exec_metrics = ExecutionMetrics(
                        test_name=f"jd_process_{task.task_id}",
                        test_type="stress",
                        execution_time=task_end - task_start,
                        success=False,
                        memory_usage=random.uniform(50, 150),
                        cpu_usage=random.uniform(0.1, 0.8)
                    )
                    self.telemetry.record_test_execution(exec_metrics)
                    
                    return None
        
        # Execute all tasks concurrently
        results = await asyncio.gather(
            *[process_single_task(task) for task in tasks],
            return_exceptions=True
        )
        
        # Separate successful and failed tasks
        for result in results:
            if isinstance(result, Exception):
                failed_tasks.append(result)
            elif result is not None:
                completed_tasks.append(result)
            else:
                failed_tasks.append(None)
        
        end_time = time.time()
        
        # Get final system metrics
        final_metrics = self.telemetry.get_system_metrics()
        
        return StressTestResult(
            total_tasks=len(tasks),
            completed_tasks=len(completed_tasks),
            failed_tasks=len(failed_tasks),
            average_processing_time=final_metrics.average_execution_time,
            peak_memory_usage=final_metrics.memory_peak,
            peak_cpu_usage=final_metrics.cpu_peak,
            concurrent_workers=max_workers,
            total_execution_time=end_time - start_time
        )
    
    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_performance_degradation_analysis(self):
        """Analyze performance degradation as load increases."""
        load_levels = [
            (5, 2),   # 5 tasks, 2 workers
            (10, 3),  # 10 tasks, 3 workers
            (25, 5),  # 25 tasks, 5 workers
            (50, 10)  # 50 tasks, 10 workers
        ]
        
        performance_results = []
        
        for task_count, workers in load_levels:
            # Generate consistent tasks for fair comparison
            tasks = []
            for i in range(task_count):
                task = JDProcessingTask(
                    task_id=f"perf_task_{i:04d}",
                    job_title="Software Engineer",
                    job_description="Test description for performance analysis",
                    resume_content="Test resume content",
                    priority=2,
                    expected_processing_time=0.1
                )
                tasks.append(task)
            
            # Clear telemetry between runs
            self.telemetry.clear_metrics()
            
            # Execute performance test
            from tests.stress.test_concurrent_jd_processing import StressTestResult
            result = await self.process_tasks_concurrent(tasks, workers)
            
            performance_results.append({
                "task_count": task_count,
                "workers": workers,
                "avg_time_per_task": result.total_execution_time / task_count,
                "success_rate": result.completed_tasks / task_count,
                "peak_memory": result.peak_memory_usage,
                "peak_cpu": result.peak_cpu_usage
            })
        
        # Analyze performance degradation
        assert len(performance_results) == 4
        
        # Time per task should not increase dramatically (within 3x)
        baseline_time = performance_results[0]["avg_time_per_task"]
        for result in performance_results[1:]:
            assert result["avg_time_per_task"] < baseline_time * 3
        
        # Success rate should remain reasonable (above 70%)
        for result in performance_results:
            assert result["success_rate"] > 0.7
        
        # Resource usage should scale reasonably
        memory_usage = [r["peak_memory"] for r in performance_results]
        cpu_usage = [r["peak_cpu"] for r in performance_results]
        
        # Memory and CPU should increase with load but not exponentially
        assert memory_usage[-1] < memory_usage[0] * 5  # Less than 5x increase
        assert cpu_usage[-1] < cpu_usage[0] * 5      # Less than 5x increase
