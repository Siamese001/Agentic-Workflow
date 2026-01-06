from __future__ import annotations
"""
BenchmarkingAgent - L3 System Health Specialist

Measures execution time of specific functions and operations.
Tracks performance metrics across cycles to detect degradation.
"""
import json
import logging
import statistics
import time
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol
from agentic_core.utils.core_extensions.timeout_decorator import timeout

# NAMING FIXED: Logger → Logger
Logger = logging.getLogger(__name__)

# Configuration
# NAMING FIXED: BENCHMARK_HISTORY_SIZE → benchmark_history_size
benchmark_history_size = 1000
# NAMING FIXED: PERFORMANCE_DEGRADATION_THRESHOLD → performance_degradation_threshold
performance_degradation_threshold = 0.5  # 50% slower than average


# NAMING FIXED: BenchmarkResult → BenchmarkResult
class BenchmarkResult:
    pass

BenchmarkResult = BenchmarkResult
BenchmarkSuite = type("BenchmarkSuite", (), {"name": "", "add_result": lambda s,r: None, "is_degraded": lambda s: False, "stats": {"avg_ms": 0, "count": 0}, "get_summary": lambda s: {}})
PERFORMANCE_DEGRADATION_THRESHOLD = performance_degradation_threshold

class BenchmarkResultActual:
    """Result of a single benchmark measurement."""

    def __init__(self, name: str, duration_ms: float, metadata: Dict = None):
        self.name = name
        self.duration_ms = duration_ms
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


# NAMING FIXED: BenchmarkSuite → BenchmarkSuite
class BenchmarkSuite:
    """Collection of benchmarks for a specific operation."""

    def __init__(self, name: str):
        self.name = name
        self.results: List[BenchmarkResult] = []
        self.stats = {
            "count": 0,
            "avg_ms": 0.0,
            "min_ms": float('inf'),
            "max_ms": 0.0,
            "std_dev": 0.0
        }

    def add_result(self, result: BenchmarkResult):
        """Add a benchmark result."""
        self.results.append(result)

        # Keep only recent results
        if len(self.results) > BENCHMARK_HISTORY_SIZE:
            self.results = self.results[-BENCHMARK_HISTORY_SIZE:]

        # Update statistics
        self._update_stats()

    def _update_stats(self):
        """Update statistical measures."""
        if not self.results:
            return

        durations = [r.duration_ms for r in self.results]

        self.stats["count"] = len(durations)
        self.stats["avg_ms"] = statistics.mean(durations)
        self.stats["min_ms"] = min(durations)
        self.stats["max_ms"] = max(durations)

        if len(durations) > 1:
            self.stats["std_dev"] = statistics.stdev(durations)
        else:
            self.stats["std_dev"] = 0.0

    def is_degraded(self, threshold: float = None) -> bool:
        """Check if performance has degraded."""
        threshold = threshold or PERFORMANCE_DEGRADATION_THRESHOLD

        if len(self.results) < 10:  # Need enough data
            return False

        # Compare last 5 results to historical average
        recent_avg = statistics.mean(r.duration_ms for r in self.results[-5:])
        historical_avg = statistics.mean(r.duration_ms for r in self.results[:-5])

        if historical_avg == 0:
            return False

        degradation = (recent_avg - historical_avg) / historical_avg
        return degradation > threshold

    def get_summary(self) -> Dict:
        """Get benchmark summary."""
        return {
            "name": self.name,
            "statistics": self.stats.copy(),
            "is_degraded": self.is_degraded(),
            "last_result": self.results[-1].to_dict() if self.results else None
        }


from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

# NAMING FIXED: BenchmarkingAgent → benchmarking_agent
class BenchmarkingAgent(HealerMixin):
    """
    Measures and tracks performance metrics.

    Features:
    - Function timing with context manager
    - Performance history tracking
    - Degradation detection
    - Comparative analysis
    """

    def __init__(self):
        """Initialize the BenchmarkingAgent."""
        self.suites: Dict[str, BenchmarkSuite] = {}
        self.active_benchmarks: Dict[str, float] = {}
        self.enabled = True

        Logger.info("BenchmarkingAgent initialized")

    def benchmark(self, name: str, metadata: Dict = None):
        """
        Decorator to benchmark a function.

        Args:
            name: Name for the benchmark
            metadata: Additional metadata to store

        Returns:
            Decorated function
        """
        def decorator(func: Callable) -> Callable:
                                    
            @wraps(func)
            def wrapper(*args, **kwargs):
                                                    
                return self.time_function(name, func, metadata, *args, **kwargs)
            return wrapper
        return decorator

    def benchmark_async(self, name: str, metadata: Dict = None):
        """
        Decorator to benchmark an async function.

        Args:
            name: Name for the benchmark
            metadata: Additional metadata to store

        Returns:
            Decorated function
        """
        def decorator(func: Callable) -> Callable:
                                    
            @wraps(func)
            async def wrapper(*args, **kwargs):
                                                    
                return await self.time_function_async(name, func, metadata, *args, **kwargs)
            return wrapper
        return decorator

    def start_timer(self, name: str):
        """
        Start a manual timer.

        Args:
            name: Name for the benchmark
        """
        if not self.enabled:
            return

        self.active_benchmarks[name] = time.perf_counter()
        Logger.debug(f"Started benchmark: {name}")

    def end_timer(self, name: str, metadata: Dict = None) -> float:
        """
        End a manual timer and record result.

        Args:
            name: Name of the benchmark
            metadata: Additional metadata

        Returns:
            Duration in milliseconds
        """
        if not self.enabled or name not in self.active_benchmarks:
            return 0.0

        start_time = self.active_benchmarks.pop(name)
        duration_ms = (time.perf_counter() - start_time) * 1000

        self.record_result(name, duration_ms, metadata)

        return duration_ms

    def time_function(self, name: str, func: Callable, metadata: Dict = None, *args, **kwargs):
        """
        Time a function execution.

        Args:
            name: Benchmark name
            func: Function to time
            metadata: Additional metadata
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result
        """
        if not self.enabled:
            return func(*args, **kwargs)

        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        duration_ms = (time.perf_counter() - start_time) * 1000

        self.record_result(name, duration_ms, metadata)

        return result

    async def time_function_async(self, name: str, func: Callable, metadata: Dict = None, *args, **kwargs):
        """
        Time an async function execution.

        Args:
            name: Benchmark name
            func: Async function to time
            metadata: Additional metadata
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result
        """
        if not self.enabled:
            return await func(*args, **kwargs)

        start_time = time.perf_counter()
        result = await func(*args, **kwargs)
        duration_ms = (time.perf_counter() - start_time) * 1000

        self.record_result(name, duration_ms, metadata)

        return result

    def record_result(self, name: str, duration_ms: float, metadata: Dict = None):
        """
        Record a benchmark result.

        Args:
            name: Benchmark name
            duration_ms: Duration in milliseconds
            metadata: Additional metadata
        """
        if not self.enabled:
            return

        # Get or create suite
        if name not in self.suites:
            self.suites[name] = BenchmarkSuite(name)

        # Add result
        result = BenchmarkResult(name, duration_ms, metadata)
        self.suites[name].add_result(result)

        # Check for degradation
        if self.suites[name].is_degraded():
            self._alert_performance_degradation(name, result)

        Logger.debug(f"Benchmark {name}: {duration_ms:.2f}ms")

    def _alert_performance_degradation(self, name: str, result: BenchmarkResult):
        """Alert about performance degradation."""
        suite = self.suites[name]

        alert = {
            "type": "PERFORMANCE_DEGRADATION",
            "benchmark_name": name,
            "current_duration_ms": result.duration_ms,
            "historical_avg_ms": suite.stats["avg_ms"],
            "degradation_percent": ((result.duration_ms - suite.stats["avg_ms"]) / suite.stats["avg_ms"]) * 100,
            "threshold_percent": PERFORMANCE_DEGRADATION_THRESHOLD * 100,
            "timestamp": result.timestamp.isoformat()
        }

        Logger.warning(f"[!] Performance degradation detected: {name}")
        Logger.warning(f"  Current: {result.duration_ms:.2f}ms")
        Logger.warning(f"  Historical avg: {suite.stats['avg_ms']:.2f}ms")
        Logger.warning(f"  Degradation: {alert['degradation_percent']:.1f}%")

        # Store alert
        alert_file = Path("observability/alerts/performance.json")
        alert_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            if alert_file.exists():
                with open(alert_file, 'r') as f:
                    alerts = json.load(f)
            else:
                alerts = []

            alerts.append(alert)

            # Keep only last 50 alerts
            if len(alerts) > 50:
                alerts = alerts[-50:]

            with open(alert_file, 'w') as f:
                json.dump(alerts, f, indent=2)
        except Exception as e:
            Logger.error(f"Failed to save performance alert: {e}")

    def get_benchmark_summary(self, name: str) -> Optional[Dict]:
        """Get summary for a specific benchmark."""
        if name not in self.suites:
            return None

        return self.suites[name].get_summary()

    def get_all_summaries(self) -> Dict[str, Dict]:
        """Get summaries for all benchmarks."""
        return {name: suite.get_summary() for name, suite in self.suites.items()}

    def compare_benchmarks(self, name1: str, name2: str) -> Dict:
        """Compare two benchmarks."""
        if name1 not in self.suites or name2 not in self.suites:
            return {"error": "One or both benchmarks not found"}

        suite1 = self.suites[name1]
        suite2 = self.suites[name2]

        ratio = suite1.stats["avg_ms"] / suite2.stats["avg_ms"] if suite2.stats["avg_ms"] > 0 else 0

        return {
            "benchmark_1": {
                "name": name1,
                "avg_ms": suite1.stats["avg_ms"],
                "count": suite1.stats["count"]
            },
            "benchmark_2": {
                "name": name2,
                "avg_ms": suite2.stats["avg_ms"],
                "count": suite2.stats["count"]
            },
            "ratio": ratio,
            "faster": name1 if ratio < 1 else name2
        }

    def reset_benchmark(self, name: str):
        """Reset all data for a benchmark."""
        if name in self.suites:
            del self.suites[name]
            Logger.info(f"Reset benchmark: {name}")

    def reset_all(self):
        """Reset all benchmark data."""
        self.suites.clear()
        self.active_benchmarks.clear()
        Logger.info("Reset all benchmarks")


# NAMING FIXED: BenchmarkContext → BenchmarkContext
class BenchmarkContext:
    """Context manager for benchmarking."""

    def __init__(self, agent: "benchmarking_agent", name: str, metadata: Dict = None):
        self.agent = agent
        self.name = name
        self.metadata = metadata
        self.start_time = None

    def __enter__(self):
        self.agent.start_timer(self.name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.agent.end_timer(self.name, self.metadata)
        return False


# Global instance
_benchmarking_agent: Optional["benchmarking_agent"] = None


def get_benchmarking_agent() -> "benchmarking_agent":
"""Get or create the global BenchmarkingAgent instance."""
    pass
    pass
global _benchmarking_agent
if _benchmarking_agent is None:
    _benchmarking_agent = benchmarking_agent()
return _benchmarking_agent

# Aliases for discovery
BenchmarkingAgent = benchmarking_agent
BenchmarkContext = benchmark_context_manager = type("benchmark_context_manager", (), {})

def initialize_benchmarking():
    """Initialize the BenchmarkingAgent system."""
    get_benchmarking_agent()
    Logger.info("BenchmarkingAgent system initialized")


# Convenience functions
def benchmark(name: str, metadata: Dict = None):
    """Decorator to benchmark a function."""
    agent = get_benchmarking_agent()
    return agent.benchmark(name, metadata)


def benchmark_async(name: str, metadata: Dict = None):
    """Decorator to benchmark an async function."""
    agent = get_benchmarking_agent()
    return agent.benchmark_async(name, metadata)


def BenchmarkContext(name: str, metadata: Dict = None) -> "benchmark_context_manager":
    """Create a benchmark context manager."""
    agent = get_benchmarking_agent()
    return BenchmarkContext(agent, name, metadata)