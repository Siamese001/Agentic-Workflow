from __future__ import annotations
"""Resume Swarm Integration Examples.

Demonstrates how to use ResumeSwarm for CPU-intensive resume generation tasks
including PDF generation, heavy parsing, and document formatting.
"""

import logging
import time
from typing import Dict

from ResumeSwarm import ResumeResult, create_resume_swarm

logging.basicConfig(level=logging.INFO)
Logger = logging.getLogger(__name__)


def example_basic_batch_generation():
    """Example 1: Basic batch resume generation."""
    Logger.info("=== Example 1: Basic Batch Generation ===")

    # Create swarm with 6 workers
    swarm = create_resume_swarm(num_workers=6, enable_metrics=True)

    # Create 20 job payloads
    jobs = [
        {
            "job_id": f"job_{i}",
            "JobDescription": f"Senior Python Developer at Company {i}",
            "user_profile": {
                "name": "John Doe",
                "skills": ["Python", "AWS", "Docker"]
            },
            "output_format": "pdf"
        }
        for i in range(20)
    ]

    Logger.info(f"Generating {len(jobs)} resumes with 6 workers...")

    # Generate batch
    results = swarm.generate_batch(jobs)

    # Display results
    Logger.info(f"\nResults: {len(results)} resumes generated")
    for result in results[:5]:  # Show first 5
        Logger.info(
            f"  Job {result.job_id}: {result.status} "
            f"(worker: {result.worker_pid}, time: {result.execution_time:.2f}s)"
        )

    # Display metrics
    metrics = swarm.get_metrics()
    Logger.info(f"\nMetrics:")
    Logger.info(f"  Success rate: {swarm.get_success_rate():.1f}%")
    Logger.info(f"  Throughput: {metrics.throughput:.2f} resumes/sec")
    Logger.info(f"  Avg time per resume: {metrics.average_execution_time:.2f}s")
    Logger.info(f"  Total wall time: {metrics.end_time - metrics.start_time:.2f}s")


def example_streaming_generation():
    """Example 2: Streaming results as they complete."""
    Logger.info("\n=== Example 2: Streaming Generation ===")

    swarm = create_resume_swarm(num_workers=6)

    jobs = [
        {
            "job_id": f"stream_{i}",
            "JobDescription": f"Data Scientist role {i}",
            "user_profile": {"name": "Jane Smith"},
            "output_format": "pdf"
        }
        for i in range(15)
    ]

    Logger.info(f"Streaming {len(jobs)} resume generations...")

    completed = 0
    for result in swarm.generate_streaming(jobs, chunksize=1):
        completed += 1
        Logger.info(
            f"  [{completed}/{len(jobs)}] {result.job_id}: {result.status} "
            f"(worker: {result.worker_pid})"
        )


def example_error_handling():
    """Example 3: Error handling with mixed payloads."""
    Logger.info("\n=== Example 3: Error Handling ===")

    # Custom worker function that simulates failures
    def worker_with_failures(payload: Dict) -> ResumeResult:
                    
        job_id = payload.get('job_id', 'unknown')
        start_time = time.time()

        # Simulate failure for certain jobs
        if "fail" in job_id:
            return ResumeResult(
                job_id=job_id,
                status="failed",
                error=f"Simulated failure for {job_id}",
                worker_pid=0,
                execution_time=time.time() - start_time
            )

        # Success for others
        time.sleep(0.3)
        return ResumeResult(
            job_id=job_id,
            status="success",
            result={"output": f"resume_{job_id}.pdf"},
            worker_pid=0,
            execution_time=time.time() - start_time
        )

    swarm = create_resume_swarm(
        num_workers=4,
        worker_function=worker_with_failures
    )

    # Mix of successful and failing jobs
    jobs = [
        {"job_id": "success_1"},
        {"job_id": "fail_2"},
        {"job_id": "success_3"},
        {"job_id": "fail_4"},
        {"job_id": "success_5"},
        {"job_id": "success_6"}
    ]

    results = swarm.generate_batch(jobs)

    # Analyze results
    successful = [r for r in results if r.status == "success"]
    failed = [r for r in results if r.status == "failed"]

    Logger.info(f"\nResults:")
    Logger.info(f"  Successful: {len(successful)}")
    Logger.info(f"  Failed: {len(failed)}")

    for result in failed:
        Logger.info(f"  Failed job: {result.job_id} - {result.error}")


def example_performance_comparison():
    """Example 4: Performance comparison - sequential vs parallel."""
    Logger.info("\n=== Example 4: Performance Comparison ===")

    num_jobs = 24
    jobs = [
        {
            "job_id": f"perf_{i}",
            "JobDescription": f"Role {i}",
            "user_profile": {"name": "Test User"}
        }
        for i in range(num_jobs)
    ]

    # Sequential processing (1 worker)
    Logger.info(f"\nSequential processing ({num_jobs} jobs)...")
    swarm_seq = create_resume_swarm(num_workers=1)
    start_seq = time.time()
    swarm_seq.generate_batch(jobs)
    time_seq = time.time() - start_seq

    Logger.info(f"  Time: {time_seq:.2f}s")
    Logger.info(f"  Throughput: {num_jobs / time_seq:.2f} jobs/sec")

    # Parallel processing (6 workers)
    Logger.info(f"\nParallel processing ({num_jobs} jobs, 6 workers)...")
    swarm_par = create_resume_swarm(num_workers=6)
    start_par = time.time()
    swarm_par.generate_batch(jobs)
    time_par = time.time() - start_par

    Logger.info(f"  Time: {time_par:.2f}s")
    Logger.info(f"  Throughput: {num_jobs / time_par:.2f} jobs/sec")
    Logger.info(f"  Speedup: {time_seq / time_par:.2f}x")


def example_large_batch():
    """Example 5: Large batch processing (100 resumes)."""
    Logger.info("\n=== Example 5: Large Batch Processing ===")

    swarm = create_resume_swarm(num_workers=6)

    # Generate 100 job payloads
    jobs = [
        {
            "job_id": f"batch_{i:03d}",
            "JobDescription": f"Position {i}",
            "user_profile": {
                "name": "Candidate",
                "experience": ["Python", "ML", "Cloud"]
            },
            "output_format": "pdf"
        }
        for i in range(100)
    ]

    Logger.info(f"Processing {len(jobs)} resumes...")

    start_time = time.time()
    results = swarm.generate_batch(jobs, chunksize=10)
    wall_time = time.time() - start_time

    metrics = swarm.get_metrics()

    Logger.info(f"\nBatch Complete:")
    Logger.info(f"  Total jobs: {len(jobs)}")
    Logger.info(f"  Successful: {metrics.successful}")
    Logger.info(f"  Failed: {metrics.failed}")
    Logger.info(f"  Success rate: {swarm.get_success_rate():.1f}%")
    Logger.info(f"  Wall time: {wall_time:.2f}s")
    Logger.info(f"  Throughput: {metrics.throughput:.2f} resumes/sec")
    Logger.info(f"  Avg time per resume: {metrics.average_execution_time:.2f}s")


def example_with_real_resume_engine():
    """Example 6: Integration with real resume engine (if available)."""
    Logger.info("\n=== Example 6: Real Resume Engine Integration ===")

    try:
        # Try to import real resume generator
        # from apps_rg.resume_engine.ResumeGenerator import generate_single_resume

        # Custom worker function using real engine
        def real_resume_worker(payload: Dict) -> ResumeResult:
                                    
            job_id = payload.get('job_id', 'unknown')
            start_time = time.time()

            try:
                # Call real resume generation
                # result = generate_single_resume(payload)

                # Placeholder for demonstration
                time.sleep(1.0)  # Simulate real work
                result = {
                    "job_id": job_id,
                    "output_path": f"/output/resume_{job_id}.pdf",
                    "sections": ["header", "summary", "experience", "skills"]
                }

                return ResumeResult(
                    job_id=job_id,
                    status="success",
                    result=result,
                    worker_pid=0,
                    execution_time=time.time() - start_time
                )

            except Exception as e:
                return ResumeResult(
                    job_id=job_id,
                    status="failed",
                    error=str(e),
                    worker_pid=0,
                    execution_time=time.time() - start_time
                )

        swarm = create_resume_swarm(
            num_workers=6,
            worker_function=real_resume_worker
        )

        jobs = [
            {
                "job_id": f"real_{i}",
                "JobDescription": "Senior Software Engineer",
                "company": "Tech Corp",
                "requirements": ["Python", "AWS", "Docker"]
            }
            for i in range(10)
        ]

        Logger.info(f"Generating {len(jobs)} real resumes...")
        results = swarm.generate_batch(jobs)

        Logger.info(f"Generated {len(results)} resumes")
        Logger.info(f"Success rate: {swarm.get_success_rate():.1f}%")

    except ImportError:
        Logger.warning("Real resume engine not available - skipping this example")


def example_async_with_callback():
    """Example 7: Async generation with progress callback."""
    Logger.info("\n=== Example 7: Async with Callback ===")

    swarm = create_resume_swarm(num_workers=6)

    # Progress tracking
    progress = {"completed": 0}

    def on_complete(results):
        """Callback when batch completes."""
        progress["completed"] = len(results)
        Logger.info(f"Batch complete: {len(results)} resumes generated")

    jobs = [
        {"job_id": f"async_{i}", "JobDescription": f"Role {i}"}
        for i in range(15)
    ]

    Logger.info(f"Starting async generation of {len(jobs)} resumes...")

    results = swarm.generate_batch_async(
        jobs,
        callback=on_complete,
        chunksize=5
    )

    Logger.info(f"Async generation complete: {progress['completed']} resumes")


def main():
    """Run all examples."""
    example_basic_batch_generation()
    example_streaming_generation()
    example_error_handling()
    example_performance_comparison()
    example_large_batch()
    example_with_real_resume_engine()
    example_async_with_callback()

    Logger.info("\n=== All Examples Complete ===")


if __name__ == "__main__":
    main()
