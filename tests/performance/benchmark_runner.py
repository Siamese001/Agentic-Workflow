"""Qwen vLLM Benchmark Runner with Live GPU Monitoring.

Executes performance benchmarks with real-time GPU memory tracking
and dynamic load adjustment based on GPU pressure.
"""

from __future__ import annotations

import asyncio
import json
import logging
import signal
import sys
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
from agentic_core.L3_orchestration.inference.qwen_vllm.tools import get_gpu_monitor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark run."""
    base_url: str = "http://localhost:8000/v1"
    model: str = "Qwen/Qwen2.5-14B-Instruct-AWQ"

    # Test phases
    warmup_requests: int = 5
    sequential_requests: int = 20
    concurrent_levels: list[int] = field(default_factory=lambda: [4, 8, 16])
    concurrent_requests_per_level: int = 32

    # Stress test
    stress_concurrent: int = 32
    stress_duration_sec: float = 30.0

    # Monitoring
    gpu_monitor_interval_sec: float = 2.0

    # Hardening
    enable_hardened_client: bool = True
    circuit_failure_threshold: int = 5
    max_retries: int = 2


@dataclass
class LiveMetrics:
    """Live metrics during benchmark execution."""
    timestamp: float
    requests_completed: int
    requests_failed: int
    current_rps: float
    latency_p50_ms: float
    gpu_memory_used_mb: float
    gpu_utilization_percent: float
    circuit_state: str | None = None


class BenchmarkRunner:
    """Benchmark runner with live GPU monitoring."""

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.results: dict[str, Any] = {}
        self.live_metrics: list[LiveMetrics] = []
        self._stop_event = asyncio.Event()
        self._gpu_monitor = get_gpu_monitor()
        self._current_phase: str = "idle"

    async def run_full_benchmark(self) -> dict[str, Any]:
        """Execute complete benchmark suite."""
        logger.info("=" * 70)
        logger.info("QWEN VLLM BENCHMARK RUNNER")
        logger.info("=" * 70)
        logger.info(f"Target: {self.config.model}")
        logger.info(f"Endpoint: {self.config.base_url}")

        # Setup signal handlers for graceful shutdown
        for sig in (signal.SIGINT, signal.SIGTERM):
            asyncio.get_event_loop().add_signal_handler(
                sig, lambda: self._stop_event.set()
            )

        # Start GPU monitoring
        self._gpu_monitor.start()

        try:
            # Phase 1: Warmup
            await self._run_phase("warmup", self._phase_warmup)

            # Phase 2: Sequential baseline
            await self._run_phase("sequential", self._phase_sequential)

            # Phase 3: Concurrent load tests
            for level in self.config.concurrent_levels:
                await self._run_phase(
                    f"concurrent_{level}",
                    lambda: self._phase_concurrent(level)
                )

            # Phase 4: Stress test
            await self._run_phase("stress", self._phase_stress)

            # Phase 5: Hardened client test
            if self.config.enable_hardened_client:
                await self._run_phase("hardened", self._phase_hardened)

        finally:
            self._gpu_monitor.stop()

        # Generate final report
        return self._generate_report()

    async def _run_phase(self, name: str, phase_fn) -> None:
        """Execute a benchmark phase with monitoring."""
        if self._stop_event.is_set():
            return

        self._current_phase = name
        logger.info(f"\n{'─' * 70}")
        logger.info(f"PHASE: {name.upper()}")
        logger.info(f"{'─' * 70}")

        try:
            await phase_fn()
        except Exception as e:
            logger.error(f"Phase {name} failed: {e}")
            self.results[name] = {"error": str(e)}

    async def _phase_warmup(self) -> None:
        """Warmup phase - send initial requests to stabilize."""
        client = OptimizedVLLMClient(
            base_url=self.config.base_url,
            model=self.config.model,
        )
        await client.start()

        try:
            for i in range(self.config.warmup_requests):
                req = VLLMRequest(
                    prompt=f"Warmup {i}: What is 2+2?",
                    max_tokens=10,
                    temperature=0.0,
                )
                await client.infer(req)
                logger.info(f"  Warmup {i + 1}/{self.config.warmup_requests}")

            self.results["warmup"] = {"completed": self.config.warmup_requests}
        finally:
            await client.stop()

    async def _phase_sequential(self) -> None:
        """Sequential request baseline."""
        client = OptimizedVLLMClient(
            base_url=self.config.base_url,
            model=self.config.model,
        )
        await client.start()

        latencies = []
        successes = 0

        try:
            start = time.time()

            for i in range(self.config.sequential_requests):
                req = VLLMRequest(
                    prompt=f"Sequential {i}: Calculate {i} * {i + 1}",
                    max_tokens=15,
                    temperature=0.0,
                )

                req_start = time.time()
                resp = await client.infer(req)
                latencies.append(resp.latency_ms)

                if resp.success:
                    successes += 1

                # Record live metrics every 5 requests
                if (i + 1) % 5 == 0:
                    self._record_live_metrics(
                        requests_completed=i + 1,
                        requests_failed=(i + 1) - successes,
                        latencies=latencies,
                    )

                if (i + 1) % 10 == 0:
                    logger.info(f"  Progress: {i + 1}/{self.config.sequential_requests}")

            total_time = time.time() - start

            self.results["sequential"] = {
                "total_requests": self.config.sequential_requests,
                "successful": successes,
                "failed": self.config.sequential_requests - successes,
                "total_time_sec": total_time,
                "requests_per_second": self.config.sequential_requests / total_time,
                "latency_p50_ms": self._calculate_p50(latencies),
                "latency_p95_ms": self._calculate_p95(latencies),
                "latency_p99_ms": self._calculate_p99(latencies),
                "latency_mean_ms": sum(latencies) / len(latencies) if latencies else 0,
            }

        finally:
            await client.stop()

    async def _phase_concurrent(self, level: int) -> None:
        """Concurrent load test at specified concurrency level."""
        client = OptimizedVLLMClient(
            base_url=self.config.base_url,
            model=self.config.model,
            max_concurrent=level,
        )
        await client.start()

        latencies = []
        successes = 0
        completed = 0
        semaphore = asyncio.Semaphore(level)

        async def _make_request(i: int) -> None:
            nonlocal successes, completed
            async with semaphore:
                req = VLLMRequest(
                    prompt=f"Concurrent {level} req {i}: Summarize in 3 words",
                    max_tokens=15,
                    temperature=0.1,
                )

                resp = await client.infer(req)
                latencies.append(resp.latency_ms)
                completed += 1

                if resp.success:
                    successes += 1

                # Record live metrics periodically
                if completed % 10 == 0:
                    self._record_live_metrics(
                        requests_completed=completed,
                        requests_failed=completed - successes,
                        latencies=latencies,
                    )

        try:
            start = time.time()

            # Create all tasks
            tasks = [
                _make_request(i)
                for i in range(self.config.concurrent_requests_per_level)
            ]

            # Execute with progress logging
            logger.info(f"  Launching {len(tasks)} tasks at concurrency {level}")
            await asyncio.gather(*tasks, return_exceptions=True)

            total_time = time.time() - start

            self.results[f"concurrent_{level}"] = {
                "concurrency_level": level,
                "total_requests": self.config.concurrent_requests_per_level,
                "successful": successes,
                "failed": self.config.concurrent_requests_per_level - successes,
                "total_time_sec": total_time,
                "requests_per_second": self.config.concurrent_requests_per_level / total_time,
                "latency_p50_ms": self._calculate_p50(latencies),
                "latency_p95_ms": self._calculate_p95(latencies),
                "latency_p99_ms": self._calculate_p99(latencies),
            }

        finally:
            await client.stop()

    async def _phase_stress(self) -> None:
        """Stress test with sustained high concurrency."""
        logger.info(f"  Stress test: {self.config.stress_concurrent} concurrent for {self.config.stress_duration_sec}s")

        client = OptimizedVLLMClient(
            base_url=self.config.base_url,
            model=self.config.model,
            max_concurrent=self.config.stress_concurrent,
        )
        await client.start()

        latencies = []
        successes = 0
        request_count = 0
        semaphore = asyncio.Semaphore(self.config.stress_concurrent)
        running = True

        async def _stress_worker() -> None:
            nonlocal successes, request_count
            while running and not self._stop_event.is_set():
                async with semaphore:
                    req = VLLMRequest(
                        prompt=f"Stress {request_count}: Quick one word response",
                        max_tokens=5,
                        temperature=0.0,
                    )

                    resp = await client.infer(req)
                    latencies.append(resp.latency_ms)
                    request_count += 1

                    if resp.success:
                        successes += 1

                    # Record metrics every 20 requests
                    if request_count % 20 == 0:
                        self._record_live_metrics(
                            requests_completed=request_count,
                            requests_failed=request_count - successes,
                            latencies=latencies,
                        )

        try:
            # Run workers for specified duration
            start = time.time()
            workers = [
                asyncio.create_task(_stress_worker())
                for _ in range(self.config.stress_concurrent)
            ]

            # Wait for duration
            await asyncio.wait_for(
                self._stop_event.wait(),
                timeout=self.config.stress_duration_sec
            )

        except asyncio.TimeoutError:
            pass  # Expected
        finally:
            running = False
            for w in workers:
                w.cancel()
            await client.stop()

        total_time = time.time() - start

        self.results["stress"] = {
            "concurrency": self.config.stress_concurrent,
            "duration_sec": total_time,
            "total_requests": request_count,
            "successful": successes,
            "failed": request_count - successes,
            "requests_per_second": request_count / total_time if total_time > 0 else 0,
            "latency_p50_ms": self._calculate_p50(latencies),
            "latency_p95_ms": self._calculate_p95(latencies),
        }

    async def _phase_hardened(self) -> None:
        """Test hardened client with circuit breaker and retry."""
        logger.info("  Testing hardened client resilience")

        base_client = OptimizedVLLMClient(
            base_url=self.config.base_url,
            model=self.config.model,
        )
        await base_client.start()

        hardened = HardenedVLLMClient(
            base_client=base_client,
            retry_config=RetryConfig(
                max_retries=self.config.max_retries,
                base_delay_sec=0.5,
            ),
            circuit_config=CircuitBreakerConfig(
                failure_threshold=self.config.circuit_failure_threshold,
                recovery_timeout_sec=10.0,
            ),
        )

        latencies = []
        successes = 0

        try:
            for i in range(20):
                req = VLLMRequest(
                    prompt=f"Hardened {i}: Simple question",
                    max_tokens=10,
                    temperature=0.0,
                )

                resp = await hardened.infer(req)
                latencies.append(resp.latency_ms)

                if resp.success:
                    successes += 1

                # Record metrics with circuit state
                if (i + 1) % 5 == 0:
                    self._record_live_metrics(
                        requests_completed=i + 1,
                        requests_failed=(i + 1) - successes,
                        latencies=latencies,
                        circuit_state=hardened.circuit.state.name,
                    )

            # Get final hardening metrics
            hardening_metrics = hardened.get_metrics()

            self.results["hardened"] = {
                "total_requests": 20,
                "successful": successes,
                "failed": 20 - successes,
                "latency_p50_ms": self._calculate_p50(latencies),
                "hardening_metrics": hardening_metrics,
            }

        finally:
            await base_client.stop()

    def _record_live_metrics(
        self,
        requests_completed: int,
        requests_failed: int,
        latencies: list[float],
        circuit_state: str | None = None,
    ) -> None:
        """Record live metrics snapshot."""
        gpu_info = self._gpu_monitor.get_current_memory()

        # Calculate current RPS from recent window
        recent_latencies = latencies[-20:] if len(latencies) >= 20 else latencies
        avg_latency = sum(recent_latencies) / len(recent_latencies) if recent_latencies else 0
        current_rps = 1000.0 / avg_latency if avg_latency > 0 else 0

        metric = LiveMetrics(
            timestamp=time.time(),
            requests_completed=requests_completed,
            requests_failed=requests_failed,
            current_rps=current_rps,
            latency_p50_ms=self._calculate_p50(latencies) if latencies else 0,
            gpu_memory_used_mb=gpu_info.used_mb if gpu_info else 0,
            gpu_utilization_percent=gpu_info.utilization_percent if gpu_info else 0,
            circuit_state=circuit_state,
        )

        self.live_metrics.append(metric)

        # Log live status
        logger.info(
            f"  [LIVE] Phase: {self._current_phase} | "
            f"Req: {requests_completed} | "
            f"RPS: {current_rps:.1f} | "
            f"P50: {metric.latency_p50_ms:.0f}ms | "
            f"GPU: {metric.gpu_utilization_percent:.0f}%"
        )

    def _calculate_p50(self, values: list[float]) -> float:
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        return sorted_vals[len(sorted_vals) // 2]

    def _calculate_p95(self, values: list[float]) -> float:
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        idx = int(len(sorted_vals) * 0.95)
        return sorted_vals[idx] if idx < len(sorted_vals) else sorted_vals[-1]

    def _calculate_p99(self, values: list[float]) -> float:
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        idx = int(len(sorted_vals) * 0.99)
        return sorted_vals[idx] if idx < len(sorted_vals) else sorted_vals[-1]

    def _generate_report(self) -> dict[str, Any]:
        """Generate final benchmark report."""
        report = {
            "config": {
                "model": self.config.model,
                "base_url": self.config.base_url,
                "test_phases": list(self.results.keys()),
            },
            "timestamp": time.time(),
            "results": self.results,
            "live_metrics": [
                {
                    "timestamp": m.timestamp,
                    "phase": self._current_phase,
                    "requests": m.requests_completed,
                    "rps": m.current_rps,
                    "latency_p50_ms": m.latency_p50_ms,
                    "gpu_utilization": m.gpu_utilization_percent,
                    "circuit_state": m.circuit_state,
                }
                for m in self.live_metrics
            ],
            "summary": self._calculate_summary(),
        }

        # Save report
        report_path = "qwen_benchmark_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"\n{'=' * 70}")
        logger.info("BENCHMARK COMPLETE")
        logger.info(f"{'=' * 70}")
        logger.info(f"Report saved: {report_path}")
        logger.info("\nSummary:")
        for key, value in report["summary"].items():
            logger.info(f"  {key}: {value}")

        return report

    def _calculate_summary(self) -> dict[str, Any]:
        """Calculate summary statistics."""
        # Extract throughput from all phases
        throughputs = []
        latencies_p50 = []

        for phase, data in self.results.items():
            if isinstance(data, dict):
                if "requests_per_second" in data:
                    throughputs.append(data["requests_per_second"])
                if "latency_p50_ms" in data:
                    latencies_p50.append(data["latency_p50_ms"])

        return {
            "phases_completed": len(self.results),
            "peak_throughput_rps": max(throughputs) if throughputs else 0,
            "avg_throughput_rps": sum(throughputs) / len(throughputs) if throughputs else 0,
            "avg_latency_p50_ms": sum(latencies_p50) / len(latencies_p50) if latencies_p50 else 0,
            "total_requests": sum(
                data.get("total_requests", 0)
                for data in self.results.values()
                if isinstance(data, dict)
            ),
        }


async def main():
    """Run benchmark."""
    config = BenchmarkConfig()

    # Allow config override from command line
    if len(sys.argv) > 1:
        config.stress_duration_sec = float(sys.argv[1])

    runner = BenchmarkRunner(config)
    report = await runner.run_full_benchmark()

    # Print JSON to stdout for piping
    print("\n" + json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    asyncio.run(main())
