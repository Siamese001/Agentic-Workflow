"""Subatomic Swarm Integration Examples.

Demonstrates how to use SubatomicSwarm for parallel HOP execution
in resume generation and other agentic workflows.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Protocol

from subatomic_swarm import SwarmResult, create_subatomic_swarm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Mock SubatomicHop for demonstration
# NAMING FIXED: MockSubatomicHop → mock_subatomic_hop
class mock_subatomic_hop:
    """Mock SubatomicHop for testing swarm execution."""

    def __init__(self, hop_id: str, simulate_delay: float = 1.0):
        self.hop_id = hop_id
        self.simulate_delay = simulate_delay

    async def run(self, **kwargs) -> Dict[str, Any]:
        """Simulate HOP execution."""
        await asyncio.sleep(self.simulate_delay)

        # Simulate occasional failures
        if "fail" in kwargs.get("data", ""):
            raise ValueError(f"Simulated failure in {self.hop_id}")

        return {
            "hop_id": self.hop_id,
            "status": "completed",
            "result": f"Processed: {kwargs.get('data', 'no data')}",
            "input": kwargs
        }


async def example_basic_swarm():
    """Example 1: Basic swarm execution with multiple HOPs."""
    logger.info("=== Example 1: Basic Swarm Execution ===")

    # Create swarm with max 5 concurrent HOPs
    swarm = create_subatomic_swarm(max_concurrency=5, timeout_per_hop=10.0)

    # Create 10 HOPs
    hops = [MockSubatomicHop(f"hop_{i}", simulate_delay=2.0) for i in range(10)]

    # Create inputs
    inputs = [{"data": f"input_{i}"} for i in range(10)]

    # Execute swarm
    logger.info("Starting swarm with 10 HOPs (max 5 concurrent)...")
    results = await swarm.execute_swarm(hops=hops, inputs=inputs)

    # Display results
    logger.info(f"\nResults: {len(results)} HOPs completed")
    for i, result in enumerate(results):
        if isinstance(result, SwarmResult):
            logger.info(
                f"  HOP {i}: {result.status} "
                f"(time: {result.execution_time:.2f}s)"
            )

    # Display metrics
    metrics = swarm.get_metrics()
    logger.info(f"\nMetrics:")
    logger.info(f"  Success rate: {swarm.get_success_rate():.1f}%")
    logger.info(f"  Total time: {metrics.total_execution_time:.2f}s")
    logger.info(f"  Avg time per HOP: {metrics.average_execution_time:.2f}s")
    logger.info(f"  Max time: {metrics.max_execution_time:.2f}s")


async def example_error_handling():
    """Example 2: Error handling and isolation."""
    logger.info("\n=== Example 2: Error Handling ===")

    swarm = create_subatomic_swarm(max_concurrency=3)

    # Create HOPs with some that will fail
    hops = [MockSubatomicHop(f"hop_{i}") for i in range(6)]

    # Mix of successful and failing inputs
    inputs = [
        {"data": "success_1"},
        {"data": "fail_2"},  # Will fail
        {"data": "success_3"},
        {"data": "fail_4"},  # Will fail
        {"data": "success_5"},
        {"data": "success_6"}
    ]

    logger.info("Starting swarm with mixed success/failure inputs...")
    results = await swarm.execute_swarm(hops=hops, inputs=inputs)

    # Analyze results
    successful = [r for r in results if isinstance(r, SwarmResult) and r.status == "success"]
    failed = [r for r in results if isinstance(r, SwarmResult) and r.status == "failed"]

    logger.info(f"\nResults:")
    logger.info(f"  Successful: {len(successful)}")
    logger.info(f"  Failed: {len(failed)}")

    for result in failed:
        logger.info(f"  Failed HOP: {result.hop_id} - {result.error}")


async def example_batch_execution():
    """Example 3: Batch execution with HOP factory."""
    logger.info("\n=== Example 3: Batch Execution ===")

    swarm = create_subatomic_swarm(max_concurrency=5)

    # Factory function to create fresh HOPs
    def create_resume_hop():
                    '''Brief description of functionality and purpose.'''
                    
        return MockSubatomicHop("resume_hop", simulate_delay=1.5)

    # Simulate 20 resume generation tasks
    job_descriptions = [
        {"data": f"job_description_{i}", "role": f"Role {i}"}
        for i in range(20)
    ]

    logger.info("Processing 20 resume generation tasks...")
    results = await swarm.execute_batch(
        hop_factory=create_resume_hop,
        inputs=job_descriptions,
        batch_size=10  # Process in batches of 10
    )

    logger.info(f"\nProcessed {len(results)} resumes")
    logger.info(f"Success rate: {swarm.get_success_rate():.1f}%")


async def example_resume_generation_swarm():
    """Example 4: Real-world resume generation swarm."""
    logger.info("\n=== Example 4: Resume Generation Swarm ===")

    # Create swarm optimized for resume generation
    swarm = create_subatomic_swarm(
        max_concurrency=5,  # Limit to 5 concurrent LLM calls
        timeout_per_hop=300.0,  # 5 minutes per resume
        enable_metrics=True
    )

    # Simulate resume generation HOPs
    def create_resume_generator():
                    '''Brief description of functionality and purpose.'''
                    
        return MockSubatomicHop("resume_generator", simulate_delay=2.0)

    # Sample job descriptions
    jobs = [
        {
            "data": "Senior Python Developer",
            "company": "Tech Corp",
            "requirements": ["Python", "AWS", "Docker"]
        },
        {
            "data": "Data Scientist",
            "company": "AI Startup",
            "requirements": ["ML", "Python", "TensorFlow"]
        },
        {
            "data": "DevOps Engineer",
            "company": "Cloud Inc",
            "requirements": ["Kubernetes", "CI/CD", "AWS"]
        },
        {
            "data": "Full Stack Developer",
            "company": "Web Agency",
            "requirements": ["React", "Node.js", "MongoDB"]
        },
        {
            "data": "ML Engineer",
            "company": "Research Lab",
            "requirements": ["PyTorch", "NLP", "Distributed Systems"]
        }
    ] * 4  # 20 total jobs

    logger.info(f"Generating {len(jobs)} tailored resumes...")

    results = await swarm.execute_batch(
        hop_factory=create_resume_generator,
        inputs=jobs
    )

    # Analyze results
    successful_resumes = [
        r for r in results
        if isinstance(r, SwarmResult) and r.status == "success"
    ]

    logger.info(f"\nResume Generation Complete:")
    logger.info(f"  Total jobs: {len(jobs)}")
    logger.info(f"  Successful: {len(successful_resumes)}")
    logger.info(f"  Success rate: {swarm.get_success_rate():.1f}%")

    metrics = swarm.get_metrics()
    logger.info(f"\nPerformance Metrics:")
    logger.info(f"  Total execution time: {metrics.total_execution_time:.2f}s")
    logger.info(f"  Average per resume: {metrics.average_execution_time:.2f}s")
    logger.info(f"  Throughput: {len(jobs) / (metrics.end_time - metrics.start_time):.2f} resumes/sec")


async def example_progressive_scaling():
    """Example 5: Progressive scaling with different concurrency levels."""
    logger.info("\n=== Example 5: Progressive Scaling ===")

    # Test different concurrency levels
    concurrency_levels = [1, 3, 5, 8]
    num_hops = 20

    for concurrency in concurrency_levels:
        swarm = create_subatomic_swarm(max_concurrency=concurrency)

        hops = [MockSubatomicHop(f"hop_{i}", simulate_delay=1.0) for i in range(num_hops)]
        inputs = [{"data": f"input_{i}"} for i in range(num_hops)]

        logger.info(f"\nTesting with concurrency={concurrency}...")

        start_time = asyncio.get_event_loop().time()
        results = await swarm.execute_swarm(hops=hops, inputs=inputs)
        end_time = asyncio.get_event_loop().time()

        wall_time = end_time - start_time

        logger.info(f"  Wall time: {wall_time:.2f}s")
        logger.info(f"  Speedup vs sequential: {(num_hops * 1.0) / wall_time:.2f}x")


async def example_with_real_subatomic_hop():
    """Example 6: Integration with real SubatomicHop (if available)."""
    logger.info("\n=== Example 6: Real SubatomicHop Integration ===")

    try:
        # Try to import real SubatomicHop
        from scripts.runtime.core.subatomic_hop import SubatomicHop, SubatomicHopConfig

        logger.info("Real SubatomicHop found - creating swarm...")

        swarm = create_subatomic_swarm(max_concurrency=3)

        # Create real HOPs (example - adjust based on your actual implementation)
        def create_hop():
                                    '''Brief description of functionality and purpose.'''
                                    
            def sample_hop_function(**kwargs):
                                                    '''Brief description of functionality and purpose.'''
                                                    
                return {"result": f"Processed {kwargs.get('input', 'no input')}"}

            config = SubatomicHopConfig(
                enable_checkpoints=False,  # Disable for swarm execution
                enable_observability=True
            )

            return SubatomicHop(
                hop_function=sample_hop_function,
                config=config
            )

        inputs = [{"input": f"data_{i}"} for i in range(5)]

        results = await swarm.execute_batch(
            hop_factory=create_hop,
            inputs=inputs
        )

        logger.info(f"Executed {len(results)} real HOPs")
        logger.info(f"Success rate: {swarm.get_success_rate():.1f}%")

    except ImportError:
        logger.warning("Real SubatomicHop not available - skipping this example")


async def main():
    """Run all examples."""
    await example_basic_swarm()
    await example_error_handling()
    await example_batch_execution()
    await example_resume_generation_swarm()
    await example_progressive_scaling()
    await example_with_real_subatomic_hop()

    logger.info("\n=== All Examples Complete ===")


if __name__ == "__main__":
    asyncio.run(main())