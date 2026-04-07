"""Performance Test Suite for Qwen vLLM Optimization.

Measures throughput, latency percentiles, cache efficiency, and GPU utilization.
"""

from __future__ import annotations

import asyncio
import json
import logging
import statistics
import time
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L3_orchestration.inference.qwen_vllm.engines import (
    CircuitBreakerConfig,
    HardenedVLLMClient,
    OptimizedVLLMClient,
    RetryConfig,
    VLLMRequest,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LoadTestResult:
    """Results from a load test."""
    test_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_time_sec: float
    requests_per_second: float
    latencies_ms: list[float] = field(default_factory=list)
    cache_hits: int = 0
    cache_misses: int = 0
    gpu_metrics: dict[str, Any] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        return self.successful_requests / max(1, self.total_requests)

    @property
    def latency_p50_ms(self) -> float:
        if not self.latencies_ms:
            return 0.0
        return statistics.median(self.latencies_ms)

    @property
    def latency_p95_ms(self) -> float:
        if not self.latencies_ms:
            return 0.0
        sorted_lat = sorted(self.latencies_ms)
        idx = int(len(sorted_lat) * 0.95)
        return sorted_lat[idx] if idx < len(sorted_lat) else sorted_lat[-1]

    @property
    def latency_p99_ms(self) -> float:
        if not self.latencies_ms:
            return 0.0
        sorted_lat = sorted(self.latencies_ms)
        idx = int(len(sorted_lat) * 0.99)
        return sorted_lat[idx] if idx < len(sorted_lat) else sorted_lat[-1]

    @property
    def latency_mean_ms(self) -> float:
        if not self.latencies_ms:
            return 0.0
        return statistics.mean(self.latencies_ms)

    @property
    def latency_stdev_ms(self) -> float:
        if len(self.latencies_ms) < 2:
            return 0.0
        return statistics.stdev(self.latencies_ms)

    def to_dict(self) -> dict[str, Any]:
        return {
            "test_name": self.test_name,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": f"{self.success_rate:.2%}",
            "total_time_sec": f"{self.total_time_sec:.2f}",
            "requests_per_second": f"{self.requests_per_second:.2f}",
            "latency_mean_ms": f"{self.latency_mean_ms:.2f}",
            "latency_p50_ms": f"{self.latency_p50_ms:.2f}",
            "latency_p95_ms": f"{self.latency_p95_ms:.2f}",
            "latency_p99_ms": f"{self.latency_p99_ms:.2f}",
            "latency_stdev_ms": f"{self.latency_stdev_ms:.2f}",
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": f"{self.cache_hits / max(1, self.cache_hits + self.cache_misses):.2%}",
            "gpu_metrics": self.gpu_metrics,
        }


class QwenPerformanceTestSuite:
    """Performance testing suite for Qwen vLLM."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000/v1",
        model: str = "Qwen/Qwen2.5-14B-Instruct-AWQ",
    ):
        self.base_url = base_url
        self.model = model
        self.results: list[LoadTestResult] = []

    async def run_all_tests(self) -> list[LoadTestResult]:
        """Execute full performance test suite."""
        logger.info("=" * 60)
        logger.info("QWEN VLLM PERFORMANCE TEST SUITE")
        logger.info("=" * 60)

        # Test 1: Sequential baseline
        result1 = await self.test_sequential_baseline(count=20)
        self.results.append(result1)
        self._print_result(result1)

        # Test 2: Concurrent load (low)
        result2 = await self.test_concurrent_load(concurrent=4, total=20)
        self.results.append(result2)
        self._print_result(result2)

        # Test 3: Concurrent load (medium)
        result3 = await self.test_concurrent_load(concurrent=8, total=40)
        self.results.append(result3)
        self._print_result(result3)

        # Test 4: Batch efficiency
        result4 = await self.test_batch_efficiency(batch_sizes=[1, 2, 4, 8])
        self.results.append(result4)
        self._print_result(result4)

        # Test 5: Cache efficiency
        result5 = await self.test_cache_efficiency(unique_prompts=5, repeats_per_prompt=4)
        self.results.append(result5)
        self._print_result(result5)

        # Test 6: Hardened client resilience
        result6 = await self.test_hardened_client()
        self.results.append(result6)
        self._print_result(result6)

        return self.results

    async def test_sequential_baseline(self, count: int = 20) -> LoadTestResult:
        """Test sequential request baseline performance."""
        logger.info(f"\n[TEST] Sequential Baseline ({count} requests)")

        client = OptimizedVLLMClient(base_url=self.base_url, model=self.model)
        await client.start()

        latencies = []
        successes = 0

        start_time = time.time()

        for i in range(count):
            req = VLLMRequest(
                prompt=f"What is {i} + {i}? Answer with just the number.",
                max_tokens=10,
                temperature=0.0,
            )

            resp = await client.infer(req)
            latencies.append(resp.latency_ms)

            if resp.success:
                successes += 1

            if (i + 1) % 5 == 0:
                logger.info(f"  Progress: {i + 1}/{count}")

        total_time = time.time() - start_time

        await client.stop()

        return LoadTestResult(
            test_name="sequential_baseline",
            total_requests=count,
            successful_requests=successes,
            failed_requests=count - successes,
            total_time_sec=total_time,
            requests_per_second=count / total_time,
            latencies_ms=latencies,
        )

    async def test_concurrent_load(
        self,
        concurrent: int,
        total: int,
    ) -> LoadTestResult:
        """Test concurrent load performance."""
        logger.info(f"\n[TEST] Concurrent Load ({concurrent} concurrent, {total} total)")

        client = OptimizedVLLMClient(
            base_url=self.base_url,
            model=self.model,
            max_concurrent=concurrent,
        )
        await client.start()

        latencies = []
        successes = 0
        semaphore = asyncio.Semaphore(concurrent)

        async def _make_request(i: int) -> None:
            nonlocal successes
            async with semaphore:
                req = VLLMRequest(
                    prompt=f"Task {i}: Summarize 'The quick brown fox' in 5 words.",
                    max_tokens=20,
                    temperature=0.1,
                )

                resp = await client.infer(req)
                latencies.append(resp.latency_ms)

                if resp.success:
                    successes += 1

        start_time = time.time()

        # Create all tasks
        tasks = [_make_request(i) for i in range(total)]
        await asyncio.gather(*tasks, return_exceptions=True)

        total_time = time.time() - start_time

        await client.stop()

        return LoadTestResult(
            test_name=f"concurrent_{concurrent}",
            total_requests=total,
            successful_requests=successes,
            failed_requests=total - successes,
            total_time_sec=total_time,
            requests_per_second=total / total_time,
            latencies_ms=latencies,
        )

    async def test_batch_efficiency(
        self,
        batch_sizes: list[int],
    ) -> LoadTestResult:
        """Test batch processing efficiency."""
        logger.info(f"\n[TEST] Batch Efficiency (sizes: {batch_sizes})")

        latencies = []

        for batch_size in batch_sizes:
            logger.info(f"  Testing batch_size={batch_size}")

            client = OptimizedVLLMClient(
                base_url=self.base_url,
                model=self.model,
                batch_size=batch_size,
            )
            await client.start()

            # Create batch of requests
            requests = [
                VLLMRequest(
                    prompt=f"Batch test {i}: What is 2+2?",
                    max_tokens=10,
                    temperature=0.0,
                )
                for i in range(batch_size)
            ]

            start_time = time.time()
            responses = await client.infer_batch(requests)
            batch_time = (time.time() - start_time) * 1000

            latencies.append(batch_time / batch_size)  # Per-request latency

            logger.info(f"    Batch time: {batch_time:.1f}ms, per-req: {batch_time/batch_size:.1f}ms")

            await client.stop()

        return LoadTestResult(
            test_name="batch_efficiency",
            total_requests=len(batch_sizes),
            successful_requests=len(batch_sizes),
            failed_requests=0,
            total_time_sec=sum(latencies) / 1000,
            requests_per_second=0,  # Not meaningful for this test
            latencies_ms=latencies,
        )

    async def test_cache_efficiency(
        self,
        unique_prompts: int,
        repeats_per_prompt: int,
    ) -> LoadTestResult:
        """Test cache hit efficiency."""
        logger.info(f"\n[TEST] Cache Efficiency ({unique_prompts} unique × {repeats_per_prompt} repeats)")

        client = OptimizedVLLMClient(base_url=self.base_url, model=self.model)
        await client.start()

        latencies = []
        cache_hits = 0
        cache_misses = 0

        # Create unique prompts
        unique_requests = [
            VLLMRequest(
                prompt=f"Cache test prompt {i}: Calculate {i} * {i + 1}",
                max_tokens=15,
                temperature=0.0,
                request_id=f"cache_test_{i}",
            )
            for i in range(unique_prompts)
        ]

        start_time = time.time()

        # First pass: populate cache
        logger.info("  First pass (cache misses expected)")
        for req in unique_requests:
            resp = await client.infer(req)
            latencies.append(resp.latency_ms)
            if resp.cached:
                cache_hits += 1
            else:
                cache_misses += 1

        # Repeated passes: cache hits
        logger.info(f"  Repeated passes ({repeats_per_prompt - 1} each, cache hits expected)")
        for _ in range(repeats_per_prompt - 1):
            for req in unique_requests:
                resp = await client.infer(req)
                latencies.append(resp.latency_ms)
                if resp.cached:
                    cache_hits += 1
                else:
                    cache_misses += 1

        total_time = time.time() - start_time
        total_requests = unique_prompts * repeats_per_prompt

        await client.stop()

        return LoadTestResult(
            test_name="cache_efficiency",
            total_requests=total_requests,
            successful_requests=total_requests,
            failed_requests=0,
            total_time_sec=total_time,
            requests_per_second=total_requests / total_time,
            latencies_ms=latencies,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
        )

    async def test_hardened_client(self) -> LoadTestResult:
        """Test hardened client with retry and circuit breaker."""
        logger.info("\n[TEST] Hardened Client Resilience")

        base_client = OptimizedVLLMClient(base_url=self.base_url, model=self.model)
        await base_client.start()

        hardened = HardenedVLLMClient(
            base_client=base_client,
            retry_config=RetryConfig(max_retries=2, base_delay_sec=0.5),
            circuit_config=CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout_sec=10.0,
            ),
        )

        latencies = []
        successes = 0

        # Normal requests
        logger.info("  Testing normal operation")
        for i in range(10):
            req = VLLMRequest(
                prompt=f"Hardened test {i}: What is the capital of France?",
                max_tokens=10,
                temperature=0.0,
            )
            resp = await hardened.infer(req)
            latencies.append(resp.latency_ms)
            if resp.success:
                successes += 1

        # Get metrics
        metrics = hardened.get_metrics()
        logger.info(f"  Hardening metrics: {metrics}")

        await base_client.stop()

        return LoadTestResult(
            test_name="hardened_client",
            total_requests=10,
            successful_requests=successes,
            failed_requests=10 - successes,
            total_time_sec=sum(latencies) / 1000,
            requests_per_second=10 / (sum(latencies) / 1000),
            latencies_ms=latencies,
            gpu_metrics=metrics,
        )

    def _print_result(self, result: LoadTestResult) -> None:
        """Print test result in formatted table."""
        logger.info(f"\n  Results for: {result.test_name}")
        logger.info(f"  {'─' * 50}")
        logger.info(f"  Success Rate:     {result.success_rate:.1%} ({result.successful_requests}/{result.total_requests})")
        logger.info(f"  Throughput:       {result.requests_per_second:.2f} req/s")
        logger.info(f"  Latency (mean):   {result.latency_mean_ms:.1f} ms")
        logger.info(f"  Latency (p50):    {result.latency_p50_ms:.1f} ms")
        logger.info(f"  Latency (p95):    {result.latency_p95_ms:.1f} ms")
        logger.info(f"  Latency (p99):    {result.latency_p99_ms:.1f} ms")
        logger.info(f"  Latency (stdev):  {result.latency_stdev_ms:.1f} ms")

        if result.cache_hits + result.cache_misses > 0:
            hit_rate = result.cache_hits / (result.cache_hits + result.cache_misses)
            logger.info(f"  Cache Hit Rate:   {hit_rate:.1%}")

    def generate_report(self, output_path: str | None = None) -> str:
        """Generate JSON report of all test results."""
        report = {
            "timestamp": time.time(),
            "base_url": self.base_url,
            "model": self.model,
            "test_results": [r.to_dict() for r in self.results],
            "summary": {
                "total_tests": len(self.results),
                "avg_throughput": statistics.mean([
                    float(r.requests_per_second) for r in self.results
                ]) if self.results else 0,
                "avg_latency_p50": statistics.mean([
                    r.latency_p50_ms for r in self.results
                ]) if self.results else 0,
            },
        }

        json_report = json.dumps(report, indent=2)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(json_report)
            logger.info(f"\nReport saved to: {output_path}")

        return json_report


async def main():
    """Run performance test suite."""
    suite = QwenPerformanceTestSuite()

    try:
        await suite.run_all_tests()
        report = suite.generate_report(
            output_path="qwen_vllm_performance_report.json",
        )
        print("\n" + "=" * 60)
        print("FULL JSON REPORT")
        print("=" * 60)
        print(report)
    except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        logger.error(f"Test suite failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
