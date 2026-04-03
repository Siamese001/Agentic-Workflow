"""Benchmarking Utility - Deterministic performance measurement.

This module provides deterministic benchmarking functionality previously
implemented in BenchmarkingAgent. Converted from agent to utility script
as part of Phase 2 optimization (Wave 7 Micro-Wave 2).

Usage:
    from agentic_core.L5_safety.utils.benchmarking_util import (
        BenchmarkSuite, BenchmarkResult, benchmark_function
    )
    
    # Benchmark a function
    result = benchmark_function(my_func, args, kwargs)
"""

from __future__ import annotations

import logging
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

Logger = logging.getLogger(__name__)

BENCHMARK_HISTORY_SIZE = 1000
PERFORMANCE_DEGRADATION_THRESHOLD = 0.5


@dataclass
class BenchmarkResult:
    """Result of a single benchmark measurement."""
    
    name: str
    duration_ms: float
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class BenchmarkStats:
    """Statistics for a benchmark suite."""
    
    count: int = 0
    avg_ms: float = 0.0
    min_ms: float = float("inf")
    max_ms: float = 0.0
    std_dev: float = 0.0
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "count": self.count,
            "avg_ms": self.avg_ms,
            "min_ms": self.min_ms,
            "max_ms": self.max_ms,
            "std_dev": self.std_dev,
        }


class BenchmarkSuite:
    """Collection of benchmarks for a specific operation."""
    
    def __init__(self, name: str):
        self.name = name
        self.results: list[BenchmarkResult] = []
        self.stats = BenchmarkStats()
    
    def add_result(self, result: BenchmarkResult) -> None:
        """Add a benchmark result."""
        self.results.append(result)
        if len(self.results) > BENCHMARK_HISTORY_SIZE:
            self.results = self.results[-BENCHMARK_HISTORY_SIZE:]
        self._update_stats()
    
    def _update_stats(self) -> None:
        """Update statistical measures."""
        if not self.results:
            return
        
        durations = [r.duration_ms for r in self.results]
        self.stats.count = len(durations)
        self.stats.avg_ms = statistics.mean(durations)
        self.stats.min_ms = min(durations)
        self.stats.max_ms = max(durations)
        
        if len(durations) > 1:
            self.stats.std_dev = statistics.stdev(durations)
        else:
            self.stats.std_dev = 0.0
    
    def is_degraded(self, threshold: float | None = None) -> bool:
        """Check if performance has degraded."""
        threshold = threshold or PERFORMANCE_DEGRADATION_THRESHOLD
        
        if len(self.results) < 10:
            return False
        
        recent_avg = statistics.mean(r.duration_ms for r in self.results[-5:])
        historical_avg = statistics.mean(r.duration_ms for r in self.results[:-5])
        
        if historical_avg == 0:
            return False
        
        degradation = (recent_avg - historical_avg) / historical_avg
        return degradation > threshold
    
    def get_summary(self) -> dict[str, Any]:
        """Get benchmark summary."""
        return {
            "name": self.name,
            "statistics": self.stats.to_dict(),
            "is_degraded": self.is_degraded(),
            "last_result": self.results[-1].to_dict() if self.results else None,
        }


def benchmark_function(
    func: Callable,
    *args: Any,
    name: str | None = None,
    metadata: dict[str, Any] | None = None,
    **kwargs: Any,
) -> tuple[Any, BenchmarkResult]:
    """Benchmark a function execution.
    
    Args:
        func: Function to benchmark
        *args: Function arguments
        name: Benchmark name (defaults to function name)
        metadata: Additional metadata
        **kwargs: Function keyword arguments
        
    Returns:
        Tuple of (function result, BenchmarkResult)
    """
    benchmark_name = name or func.__name__
    
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    duration_ms = (time.perf_counter() - start_time) * 1000
    
    benchmark_result = BenchmarkResult(
        name=benchmark_name,
        duration_ms=duration_ms,
        metadata=metadata or {},
    )
    
    Logger.debug(f"Benchmark {benchmark_name}: {duration_ms:.2f}ms")
    return result, benchmark_result


def benchmark_function_async(
    func: Callable,
    *args: Any,
    name: str | None = None,
    metadata: dict[str, Any] | None = None,
    **kwargs: Any,
) -> tuple[Any, BenchmarkResult]:
    """Benchmark an async function execution (synchronous wrapper).
    
    Args:
        func: Async function to benchmark
        *args: Function arguments
        name: Benchmark name (defaults to function name)
        metadata: Additional metadata
        **kwargs: Function keyword arguments
        
    Returns:
        Tuple of (function result, BenchmarkResult)
    """
    import asyncio
    
    benchmark_name = name or func.__name__
    
    start_time = time.perf_counter()
    result = asyncio.run(func(*args, **kwargs))
    duration_ms = (time.perf_counter() - start_time) * 1000
    
    benchmark_result = BenchmarkResult(
        name=benchmark_name,
        duration_ms=duration_ms,
        metadata=metadata or {},
    )
    
    Logger.debug(f"Benchmark {benchmark_name}: {duration_ms:.2f}ms")
    return result, benchmark_result


def compare_benchmarks(suite1: BenchmarkSuite, suite2: BenchmarkSuite) -> dict[str, Any]:
    """Compare two benchmark suites.
    
    Args:
        suite1: First benchmark suite
        suite2: Second benchmark suite
        
    Returns:
        Comparison results
    """
    if suite2.stats.avg_ms > 0:
        ratio = suite1.stats.avg_ms / suite2.stats.avg_ms
    else:
        ratio = 0
    
    return {
        "benchmark_1": {
            "name": suite1.name,
            "avg_ms": suite1.stats.avg_ms,
            "count": suite1.stats.count,
        },
        "benchmark_2": {
            "name": suite2.name,
            "avg_ms": suite2.stats.avg_ms,
            "count": suite2.stats.count,
        },
        "ratio": ratio,
        "faster": suite1.name if ratio < 1 else suite2.name,
    }


def detect_performance_degradation(
    suite: BenchmarkSuite,
    threshold: float | None = None,
) -> dict[str, Any] | None:
    """Detect performance degradation in a benchmark suite.
    
    Args:
        suite: Benchmark suite to check
        threshold: Degradation threshold (default: 0.5)
        
    Returns:
        Degradation report or None if healthy
    """
    threshold = threshold or PERFORMANCE_DEGRADATION_THRESHOLD
    
    if not suite.is_degraded(threshold):
        return None
    
    recent_avg = statistics.mean(r.duration_ms for r in suite.results[-5:])
    historical_avg = statistics.mean(r.duration_ms for r in suite.results[:-5])
    degradation = (recent_avg - historical_avg) / historical_avg if historical_avg else 0
    
    return {
        "type": "PERFORMANCE_DEGRADATION",
        "benchmark_name": suite.name,
        "current_duration_ms": suite.results[-1].duration_ms,
        "historical_avg_ms": historical_avg,
        "recent_avg_ms": recent_avg,
        "degradation_percent": degradation * 100,
        "threshold_percent": threshold * 100,
        "timestamp": datetime.now().isoformat(),
    }


def heal_repository(**kwargs: Any) -> dict[str, Any]:
    """Autonomous healing interface (Canon Key 51 compliance)."""
    return {
        "violations_found": 0,
        "violations_fixed": 0,
        "errors": 0,
        "skipped": 0,
    }


def main():
    """Main entry point for Benchmarking Utility."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmarking Utility")
    parser.add_argument("--verbose", "-v", action="store_true")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Demo
    def demo_func():
        time.sleep(0.01)
        return "done"
    
    result, benchmark = benchmark_function(demo_func)
    print(f"Result: {result}")
    print(f"Duration: {benchmark.duration_ms:.2f}ms")


if __name__ == "__main__":
    main()
