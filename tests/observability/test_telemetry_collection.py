"""
Telemetry Collection for Observability Testing

Collects metrics, performance data, and quality trends from existing test suite.
Wraps unit/integration/E2E/golden tests to track execution patterns and quality over time.
"""

import pytest
import time
import json
import statistics
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import threading
import queue

# Mark all tests as observability tests
pytestmark = [pytest.mark.observability, pytest.mark.integration]


class MetricType(Enum):
    """Types of metrics collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass(frozen=True)
class MetricPoint:
    """Single metric data point."""
    name: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ExecutionMetrics:
    """Metrics collected from test execution."""
    test_name: str
    test_type: str  # unit, integration, e2e, golden
    execution_time: float
    success: bool
    error_message: Optional[str] = None
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    assertions_count: int = 0
    mock_calls_count: int = 0


@dataclass(frozen=True)
class QualityMetrics:
    """Quality metrics from scoring harness."""
    domain: str
    overall_score: float
    component_scores: Dict[str, float]
    evaluation_time: float
    quality_level: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class SystemMetrics:
    """System-level metrics."""
    timestamp: datetime
    total_tests_run: int
    success_rate: float
    average_execution_time: float
    total_execution_time: float
    memory_peak: float
    cpu_peak: float
    error_count: int


class TelemetryCollector:
    """Collects and aggregates telemetry data from test executions."""

    def __init__(self):
        self.metrics_buffer: List[MetricPoint] = []
        self.test_metrics: List[ExecutionMetrics] = []
        self.quality_metrics: List[QualityMetrics] = []
        self.system_metrics: List[SystemMetrics] = []
        self.collection_lock = threading.Lock()

        # Metric aggregation
        self.counters: Dict[str, float] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = {}
        self.timers: Dict[str, List[float]] = {}

        # Performance optimization: cache system metrics
        self._cached_system_metrics: Optional[SystemMetrics] = None
        self._metrics_count_at_cache: int = 0

        # Performance optimization: cache statistics per metric key
        self._stats_cache: Dict[str, Dict[str, float]] = {}

    def _invalidate_caches(self) -> None:
        """Invalidate caches when underlying metrics change."""
        self._cached_system_metrics = None
        self._metrics_count_at_cache = 0
        self._stats_cache.clear()

    def record_metric(
        self,
        name: str,
        metric_type: MetricType,
        value: float,
        tags: Dict[str, str] = None,
        metadata: Dict[str, Any] = None,
    ):
        """Record a single metric point."""
        metric = MetricPoint(
            name=name,
            metric_type=metric_type,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {},
            metadata=metadata or {},
        )

        with self.collection_lock:
            self.metrics_buffer.append(metric)
            self._aggregate_metric(metric)
            # Any new metric invalidates statistics & system metrics cache
            self._invalidate_caches()

    def record_test_execution(self, test_metrics: ExecutionMetrics):
        """Record test execution metrics."""
        with self.collection_lock:
            self.test_metrics.append(test_metrics)

            # Update system-related metrics as timer/counters
            self.record_metric(
                "test_execution_time",
                MetricType.TIMER,
                test_metrics.execution_time,
                tags={"test_type": test_metrics.test_type, "success": str(test_metrics.success)},
            )
            self.record_metric(
                "test_success",
                MetricType.COUNTER,
                1.0 if test_metrics.success else 0.0,
                tags={"test_type": test_metrics.test_type},
            )

            if not test_metrics.success:
                self.record_metric(
                    "test_failures",
                    MetricType.COUNTER,
                    1.0,
                    tags={"test_type": test_metrics.test_type},
                )

    def record_quality_metrics(self, quality_metrics: QualityMetrics):
        """Record quality scoring metrics."""
        with self.collection_lock:
            self.quality_metrics.append(quality_metrics)

            # Record quality scores as metrics
            self.record_metric(
                "quality_overall_score",
                MetricType.GAUGE,
                quality_metrics.overall_score,
                tags={"domain": quality_metrics.domain, "level": quality_metrics.quality_level},
            )

            for component, score in quality_metrics.component_scores.items():
                self.record_metric(
                    "quality_component_score",
                    MetricType.GAUGE,
                    score,
                    tags={"domain": quality_metrics.domain, "component": component},
                )

            self.record_metric(
                "quality_evaluation_time",
                MetricType.TIMER,
                quality_metrics.evaluation_time,
                tags={"domain": quality_metrics.domain},
            )

    def _aggregate_metric(self, metric: MetricPoint):
        """Aggregate metric for statistical analysis."""
        key = f"{metric.name}:{hash(tuple(sorted(metric.tags.items())))}"

        if metric.metric_type == MetricType.COUNTER:
            self.counters[key] = self.counters.get(key, 0.0) + metric.value
        elif metric.metric_type == MetricType.GAUGE:
            self.gauges[key] = metric.value
        elif metric.metric_type == MetricType.HISTOGRAM:
            if key not in self.histograms:
                self.histograms[key] = []
            self.histograms[key].append(metric.value)
        elif metric.metric_type == MetricType.TIMER:
            if key not in self.timers:
                self.timers[key] = []
            self.timers[key].append(metric.value)

    def get_system_metrics(self) -> SystemMetrics:
        """Calculate current system metrics with caching."""
        with self.collection_lock:
            current_metrics_count = len(self.test_metrics)

            # Return cached metrics if no new metrics were added
            if (
                self._cached_system_metrics is not None
                and current_metrics_count == self._metrics_count_at_cache
            ):
                return self._cached_system_metrics

            if not self.test_metrics:
                system_metrics = SystemMetrics(
                    timestamp=datetime.now(),
                    total_tests_run=0,
                    success_rate=0.0,
                    average_execution_time=0.0,
                    total_execution_time=0.0,
                    memory_peak=0.0,
                    cpu_peak=0.0,
                    error_count=0,
                )
            else:
                total_tests = current_metrics_count
                successful_tests = sum(1 for tm in self.test_metrics if tm.success)
                success_rate = successful_tests / total_tests if total_tests > 0 else 0.0

                # Local variables for performance optimization
                execution_times = [tm.execution_time for tm in self.test_metrics]
                values_len = len(execution_times)
                if values_len:
                    values_sum = sum(execution_times)
                    average_execution_time = values_sum / values_len
                    total_execution_time = values_sum
                else:
                    average_execution_time = 0.0
                    total_execution_time = 0.0

                memory_usage = [tm.memory_usage for tm in self.test_metrics]
                memory_peak = max(memory_usage) if memory_usage else 0.0

                cpu_usage = [tm.cpu_usage for tm in self.test_metrics]
                cpu_peak = max(cpu_usage) if cpu_usage else 0.0

                error_count = total_tests - successful_tests

                system_metrics = SystemMetrics(
                    timestamp=datetime.now(),
                    total_tests_run=total_tests,
                    success_rate=success_rate,
                    average_execution_time=average_execution_time,
                    total_execution_time=total_execution_time,
                    memory_peak=memory_peak,
                    cpu_peak=cpu_peak,
                    error_count=error_count,
                )

            # Update cache only
            self._cached_system_metrics = system_metrics
            self._metrics_count_at_cache = current_metrics_count
            return system_metrics

    def get_metric_statistics(
        self,
        metric_name: str,
        metric_type: MetricType,
        tags: Dict[str, str] = None,
    ) -> Dict[str, float]:
        """Get statistical summary for a specific metric with caching."""
        key = f"{metric_name}:{hash(tuple(sorted((tags or {}).items())))}"

        # Check cache first
        if key in self._stats_cache:
            return self._stats_cache[key]

        result: Dict[str, float] = {}

        if metric_type == MetricType.HISTOGRAM and key in self.histograms:
            values = self.histograms[key]
            if values:
                values_len = len(values)
                values_sum = sum(values)
                values_sorted = sorted(values)

                mean = values_sum / values_len
                if values_len % 2 == 1:
                    median = values_sorted[values_len // 2]
                else:
                    median = (
                        values_sorted[values_len // 2 - 1]
                        + values_sorted[values_len // 2]
                    ) / 2

                if values_len > 1:
                    var = sum((x - mean) ** 2 for x in values) / values_len
                    std_dev = var ** 0.5
                else:
                    std_dev = 0.0

                result = {
                    "count": values_len,
                    "sum": values_sum,
                    "mean": mean,
                    "median": median,
                    "min": values_sorted[0],
                    "max": values_sorted[-1],
                    "std_dev": std_dev,
                }

        elif metric_type == MetricType.TIMER and key in self.timers:
            values = self.timers[key]
            if values:
                values_len = len(values)
                values_sum = sum(values)
                values_sorted = sorted(values)
                mean = values_sum / values_len
                if values_len % 2 == 1:
                    median = values_sorted[values_len // 2]
                else:
                    median = (
                        values_sorted[values_len // 2 - 1]
                        + values_sorted[values_len // 2]
                    ) / 2

                result = {
                    "count": values_len,
                    "sum": values_sum,
                    "mean": mean,
                    "median": median,
                    "min": values_sorted[0],
                    "max": values_sorted[-1],
                    "p95": self._percentile_fast(values_sorted, 95),
                    "p99": self._percentile_fast(values_sorted, 99),
                }

        # Cache the result
        self._stats_cache[key] = result
        return result

    def _percentile_fast(self, sorted_values: List[float], percentile: int) -> float:
        """Fast percentile calculation for pre-sorted values."""
        if not sorted_values:
            return 0.0

        values_len = len(sorted_values)
        index = (percentile / 100) * (values_len - 1)

        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower_index = int(index)
            upper_index = lower_index + 1
            lower_val = sorted_values[lower_index]
            upper_val = sorted_values[upper_index]
            return lower_val + (upper_val - lower_val) * (index - lower_index)

    def export_metrics(self) -> Dict[str, Any]:
        """Export all collected metrics for analysis."""
        with self.collection_lock:
            return {
                "timestamp": datetime.now().isoformat(),
                "counters": self.counters,
                "gauges": self.gauges,
                "histograms": {
                    k: self.get_metric_statistics(k.split(":")[0], MetricType.HISTOGRAM)
                    for k in self.histograms.keys()
                },
                "timers": {
                    k: self.get_metric_statistics(k.split(":")[0], MetricType.TIMER)
                    for k in self.timers.keys()
                },
                "test_metrics": [asdict(tm) for tm in self.test_metrics],
                "quality_metrics": [asdict(qm) for qm in self.quality_metrics],
                "system_metrics": [asdict(sm) for sm in self.system_metrics],
            }

    def clear_metrics(self):
        """Clear all collected metrics and caches."""
        with self.collection_lock:
            self.metrics_buffer.clear()
            self.test_metrics.clear()
            self.quality_metrics.clear()
            self.counters.clear()
            self.gauges.clear()
            self.histograms.clear()
            self.timers.clear()
            self.system_metrics.clear()
            # Clear caches
            self._invalidate_caches()


class TestTelemetryCollection:
    """Test telemetry collection functionality."""

    def setup_method(self):
        """Setup fresh telemetry collector for each test."""
        self.collector = TelemetryCollector()

    def test_metric_recording_and_aggregation(self):
        """Test basic metric recording and aggregation."""
        # Record different types of metrics
        self.collector.record_metric(
            "test_counter", MetricType.COUNTER, 1.0, tags={"test": "unit"}
        )
        self.collector.record_metric(
            "test_counter", MetricType.COUNTER, 2.0, tags={"test": "unit"}
        )
        self.collector.record_metric(
            "test_gauge", MetricType.GAUGE, 42.5, tags={"test": "unit"}
        )
        self.collector.record_metric(
            "test_histogram", MetricType.HISTOGRAM, 1.0, tags={"test": "unit"}
        )
        self.collector.record_metric(
            "test_histogram", MetricType.HISTOGRAM, 3.0, tags={"test": "unit"}
        )
        self.collector.record_metric(
            "test_timer", MetricType.TIMER, 0.1, tags={"test": "unit"}
        )
        self.collector.record_metric(
            "test_timer", MetricType.TIMER, 0.2, tags={"test": "unit"}
        )

        # Check aggregation
        # Find the actual hash key for test_counter with unit tags
        counter_keys = [
            k for k in self.collector.counters.keys() if "test_counter" in k
        ]
        assert len(counter_keys) == 1
        actual_counter_key = counter_keys[0]
        assert self.collector.counters.get(actual_counter_key) == 3.0

        # Find actual hash keys for other metrics
        gauge_keys = [k for k in self.collector.gauges.keys() if "test_gauge" in k]
        assert len(gauge_keys) == 1
        actual_gauge_key = gauge_keys[0]
        assert self.collector.gauges.get(actual_gauge_key) == 42.5

        histogram_keys = [
            k for k in self.collector.histograms.keys() if "test_histogram" in k
        ]
        assert len(histogram_keys) == 1
        actual_histogram_key = histogram_keys[0]
        assert len(self.collector.histograms.get(actual_histogram_key, [])) == 2

        timer_keys = [k for k in self.collector.timers.keys() if "test_timer" in k]
        assert len(timer_keys) == 1
        actual_timer_key = timer_keys[0]
        assert len(self.collector.timers.get(actual_timer_key, [])) == 2

        # Check statistics
        timer_stats = self.collector.get_metric_statistics(
            "test_timer", MetricType.TIMER, {"test": "unit"}
        )
        assert timer_stats["count"] == 2
        assert timer_stats["mean"] == pytest.approx(0.15)
        assert timer_stats["p95"] == pytest.approx(
            0.195
        )  # 95th percentile of [0.1, 0.2] is 0.195

    def test_test_execution_metrics(self):
        """Test test execution metrics collection."""
        # Record test execution metrics
        test_metrics = ExecutionMetrics(
            test_name="test_sample",
            test_type="unit",
            execution_time=0.05,
            success=True,
            assertions_count=5,
            mock_calls_count=3,
        )

        self.collector.record_test_execution(test_metrics)

        # Check recorded metrics
        assert len(self.collector.test_metrics) == 1
        assert self.collector.test_metrics[0].test_name == "test_sample"
        assert self.collector.test_metrics[0].success is True

        # Check system metrics
        system_metrics = self.collector.get_system_metrics()
        assert system_metrics.total_tests_run == 1
        assert system_metrics.success_rate == 1.0
        assert system_metrics.average_execution_time == 0.05
        assert system_metrics.error_count == 0

    def test_quality_metrics_collection(self):
        """Test quality metrics collection from scoring harness."""
        # Record quality metrics
        quality_metrics = QualityMetrics(
            domain="resume_analysis",
            overall_score=0.85,
            component_scores={"structural": 0.9, "skill_coverage": 0.8},
            evaluation_time=0.001,
            quality_level="good",
        )

        self.collector.record_quality_metrics(quality_metrics)

        # Check recorded metrics
        assert len(self.collector.quality_metrics) == 1
        assert self.collector.quality_metrics[0].domain == "resume_analysis"
        assert self.collector.quality_metrics[0].overall_score == 0.85

        # Check metric aggregation
        gauge_keys = [k for k in self.collector.gauges.keys() if "quality" in k]
        assert len(gauge_keys) >= 2  # overall score + component scores

    def test_system_metrics_calculation(self):
        """Test system metrics calculation across multiple test executions."""
        # Record multiple test executions
        test_executions = [
            ExecutionMetrics("test1", "unit", 0.1, True, memory_usage=50.0, cpu_usage=0.5),
            ExecutionMetrics("test2", "unit", 0.2, True, memory_usage=75.0, cpu_usage=0.8),
            ExecutionMetrics(
                "test3", "integration", 0.15, False, memory_usage=60.0, cpu_usage=0.6
            ),
            ExecutionMetrics("test4", "e2e", 0.5, True, memory_usage=100.0, cpu_usage=1.2),
            ExecutionMetrics("test5", "golden", 0.05, True, memory_usage=40.0, cpu_usage=0.3),
        ]

        for te in test_executions:
            self.collector.record_test_execution(te)

        # Calculate system metrics
        system_metrics = self.collector.get_system_metrics()

        # Validate calculations
        assert system_metrics.total_tests_run == 5
        assert system_metrics.success_rate == 0.8  # 4/5
        assert system_metrics.average_execution_time == 0.2  # (0.1+0.2+0.15+0.5+0.05)/5
        assert system_metrics.total_execution_time == 1.0
        assert system_metrics.memory_peak == 100.0
        assert system_metrics.cpu_peak == 1.2
        assert system_metrics.error_count == 1

    def test_trend_analysis_simulation(self):
        """Test trend analysis across multiple time periods."""
        # Period 1: Good performance
        period1_metrics = [
            ExecutionMetrics(f"test_{i}", "unit", 0.1 + i * 0.01, True)
            for i in range(5)
        ]

        # Period 2: Performance degradation
        period2_metrics = [
            ExecutionMetrics(f"test_{i}", "unit", 0.2 + i * 0.02, i % 3 != 0)  # Some failures
            for i in range(5)
        ]

        # Period 3: Recovery
        period3_metrics = [
            ExecutionMetrics(f"test_{i}", "unit", 0.08 + i * 0.01, True)
            for i in range(5)
        ]

        # Collect metrics for each period
        for te in period1_metrics:
            self.collector.record_test_execution(te)

        system1 = self.collector.get_system_metrics()
        initial_success_rate = system1.success_rate
        initial_avg_time = system1.average_execution_time

        # Clear and collect period 2
        self.collector.clear_metrics()
        for te in period2_metrics:
            self.collector.record_test_execution(te)

        system2 = self.collector.get_system_metrics()
        degraded_success_rate = system2.success_rate
        degraded_avg_time = system2.average_execution_time

        # Clear and collect period 3
        self.collector.clear_metrics()
        for te in period3_metrics:
            self.collector.record_test_execution(te)

        system3 = self.collector.get_system_metrics()
        recovery_success_rate = system3.success_rate
        recovery_avg_time = system3.average_execution_time

        # Validate trend detection
        assert initial_success_rate > degraded_success_rate  # Performance degraded
        assert initial_avg_time < degraded_avg_time  # Execution time increased
        assert recovery_success_rate > degraded_success_rate  # Performance recovered
        assert recovery_avg_time < degraded_avg_time  # Execution time improved

    def test_metric_export_and_analysis(self):
        """Test metric export and analysis capabilities."""
        # Record comprehensive metrics
        test_metrics = ExecutionMetrics(
            "export_test", "unit", 0.12, True, memory_usage=80.0
        )
        quality_metrics = QualityMetrics(
            "job_matching",
            0.75,
            {"alignment": 0.8, "coverage": 0.7},
            0.002,
            "good",
        )

        self.collector.record_test_execution(test_metrics)
        self.collector.record_quality_metrics(quality_metrics)
        self.collector.record_metric(
            "custom_metric", MetricType.GAUGE, 42.0, tags={"type": "custom"}
        )

        # Export metrics
        exported = self.collector.export_metrics()

        # Validate export structure
        assert "timestamp" in exported
        assert "counters" in exported
        assert "gauges" in exported
        assert "test_metrics" in exported
        assert "quality_metrics" in exported
        assert "system_metrics" in exported

        # Validate content
        assert len(exported["test_metrics"]) == 1
        assert len(exported["quality_metrics"]) == 1
        assert len(exported["gauges"]) >= 1  # custom_metric + quality metrics

        # Validate JSON serializability
        json_str = json.dumps(exported, default=str)
        assert isinstance(json_str, str)
        assert len(json_str) > 0


class TestObservabilityIntegration:
    """Test observability integration with existing test infrastructure."""

    def test_unit_test_observability_wrapper(self):
        """Test observability wrapper for unit tests."""
        collector = TelemetryCollector()

        # Mock unit test execution
        def mock_unit_test(test_name: str, success: bool, execution_time: float):
            start_time = time.time()

            # Simulate test execution (no sleep needed for testing)
            # time.sleep(0.001)

            actual_time = time.time() - start_time

            # Record metrics
            test_metrics = ExecutionMetrics(
                test_name=test_name,
                test_type="unit",
                execution_time=actual_time,
                success=success,
                assertions_count=3 if success else 0,
                mock_calls_count=5,
            )

            collector.record_test_execution(test_metrics)
            return success

        # Execute mock unit tests
        test_results = [
            mock_unit_test("test_resume_parsing", True, 0.01),
            mock_unit_test("test_skill_extraction", True, 0.02),
            mock_unit_test("test_job_matching", False, 0.015),
            mock_unit_test("test_format_validation", True, 0.008),
            mock_unit_test("test_error_handling", True, 0.012),
        ]

        # Analyze collected metrics
        system_metrics = collector.get_system_metrics()

        # Validate observability data
        assert system_metrics.total_tests_run == 5
        assert system_metrics.success_rate == 0.8  # 4/5 passed
        assert system_metrics.average_execution_time > 0.001
        assert system_metrics.error_count == 1

        # Check specific test metrics
        failed_tests = [tm for tm in collector.test_metrics if not tm.success]
        assert len(failed_tests) == 1
        assert failed_tests[0].test_name == "test_job_matching"

    def test_e2e_workflow_observability(self):
        """Test observability integration with E2E workflow."""
        collector = TelemetryCollector()

        # Mock E2E workflow execution phases
        def mock_e2e_phase(phase_name: str, duration: float, success: bool):
            start_time = time.time()

            # Simulate phase work (no sleep needed for testing)
            # time.sleep(min(duration, 0.01))

            actual_time = time.time() - start_time

            # Record phase metrics
            phase_metrics = ExecutionMetrics(
                test_name=f"e2e_{phase_name}",
                test_type="e2e",
                execution_time=actual_time,
                success=success,
                memory_usage=100.0 + duration * 10,
                cpu_usage=0.5 + duration * 0.1,
            )

            collector.record_test_execution(phase_metrics)
            return success

        # Execute E2E workflow phases
        phases = [
            ("planning_phase", 0.1, True),
            ("execution_phase", 0.3, True),
            ("orchestration_phase", 0.2, True),
            ("validation_phase", 0.15, True),
        ]

        workflow_success = all(
            mock_e2e_phase(name, duration, success)
            for name, duration, success in phases
        )

        # Analyze E2E metrics
        system_metrics = collector.get_system_metrics()

        # Validate E2E observability
        assert system_metrics.total_tests_run == 4
        assert system_metrics.success_rate == 1.0
        assert system_metrics.average_execution_time > 0.01
        assert system_metrics.memory_peak > 100.0

        # Check phase-specific metrics
        phase_metrics_map = {tm.test_name: tm for tm in collector.test_metrics}
        assert "e2e_planning_phase" in phase_metrics_map
        assert "e2e_execution_phase" in phase_metrics_map

        # Execution phase should take longest
        execution_time = phase_metrics_map["e2e_execution_phase"].execution_time
        planning_time = phase_metrics_map["e2e_planning_phase"].execution_time
        assert execution_time > planning_time

    def test_quality_scoring_observability(self):
        """Test observability integration with quality scoring."""
        collector = TelemetryCollector()

        # Mock quality scoring execution
        def mock_quality_scoring(domain: str, score: float, eval_time: float):
            # Simulate scoring work (no sleep needed for testing)
            # time.sleep(min(eval_time, 0.001))

            # Create quality metrics
            quality_metrics = QualityMetrics(
                domain=domain,
                overall_score=score,
                component_scores={
                    "completeness": score * 0.9,
                    "accuracy": score * 0.85,
                    "format": score * 0.95,
                },
                evaluation_time=eval_time,
                quality_level="good" if score > 0.7 else "acceptable",
            )

            collector.record_quality_metrics(quality_metrics)
            return quality_metrics

        # Execute quality scoring for different domains
        scoring_results = [
            mock_quality_scoring("resume_analysis", 0.85, 0.001),
            mock_quality_scoring("job_matching", 0.78, 0.0015),
            mock_quality_scoring("skill_extraction", 0.72, 0.0008),
            mock_quality_scoring("resume_analysis", 0.91, 0.0012),
            mock_quality_scoring("job_matching", 0.83, 0.0011),
        ]

        # Analyze quality metrics
        assert len(collector.quality_metrics) == 5

        # Check domain-specific metrics
        resume_scores = [
            qm.overall_score for qm in collector.quality_metrics if qm.domain == "resume_analysis"
        ]
        job_scores = [
            qm.overall_score for qm in collector.quality_metrics if qm.domain == "job_matching"
        ]

        assert len(resume_scores) == 2
        assert len(job_scores) == 2
        assert all(score > 0.7 for score in resume_scores)
        assert all(score > 0.7 for score in job_scores)

        # Check aggregated metrics
        gauge_keys = [
            k for k in collector.gauges.keys() if "quality_overall_score" in k
        ]
        assert len(gauge_keys) >= 2  # resume_analysis + job_matching

        # Check timer metrics for evaluation time
        timer_stats = collector.get_metric_statistics(
            "quality_evaluation_time", MetricType.TIMER
        )
        assert timer_stats["count"] == 5
        assert timer_stats["mean"] > 0.0005
        assert timer_stats["max"] > timer_stats["min"]

    def test_observability_dashboard_simulation(self):
        """Test observability dashboard data simulation."""
        collector = TelemetryCollector()

        # Simulate comprehensive test execution
        test_scenarios = [
            # Unit tests (fast, high success)
            *[
                ExecutionMetrics(f"unit_test_{i}", "unit", 0.01 + i * 0.002, i % 10 != 0)
                for i in range(20)
            ],
            # Integration tests (medium speed, moderate success)
            *[
                ExecutionMetrics(
                    f"integration_test_{i}",
                    "integration",
                    0.05 + i * 0.01,
                    i % 5 != 0,
                )
                for i in range(10)
            ],
            # E2E tests (slower, high success)
            *[
                ExecutionMetrics(f"e2e_test_{i}", "e2e", 0.2 + i * 0.05, i % 8 != 0)
                for i in range(5)
            ],
            # Golden evals (fastest, perfect success)
            *[
                ExecutionMetrics(f"golden_test_{i}", "golden", 0.005 + i * 0.001, True)
                for i in range(5)
            ],
        ]

        # Record all test metrics
        for tm in test_scenarios:
            collector.record_test_execution(tm)

        # Generate dashboard data
        system_metrics = collector.get_system_metrics()
        exported_metrics = collector.export_metrics()

        # Simulate dashboard KPIs
        dashboard_kpis = {
            "total_tests": system_metrics.total_tests_run,
            "overall_success_rate": f"{system_metrics.success_rate:.1%}",
            "avg_execution_time": f"{system_metrics.average_execution_time:.3f}s",
            "total_execution_time": f"{system_metrics.total_execution_time:.2f}s",
            "error_count": system_metrics.error_count,
            # Test type breakdown
            "unit_tests": len(
                [tm for tm in collector.test_metrics if tm.test_type == "unit"]
            ),
            "integration_tests": len(
                [tm for tm in collector.test_metrics if tm.test_type == "integration"]
            ),
            "e2e_tests": len(
                [tm for tm in collector.test_metrics if tm.test_type == "e2e"]
            ),
            "golden_tests": len(
                [tm for tm in collector.test_metrics if tm.test_type == "golden"]
            ),
            # Performance metrics
            "fastest_test": min(
                tm.execution_time for tm in collector.test_metrics
            ),
            "slowest_test": max(
                tm.execution_time for tm in collector.test_metrics
            ),
            "memory_peak": f"{system_metrics.memory_peak:.1f}MB",
            "cpu_peak": f"{system_metrics.cpu_peak:.2f}%",
        }

        # Validate dashboard data
        assert dashboard_kpis["total_tests"] == 40
        assert dashboard_kpis["unit_tests"] == 20
        assert dashboard_kpis["integration_tests"] == 10
        assert dashboard_kpis["e2e_tests"] == 5
        assert dashboard_kpis["golden_tests"] == 5

        # Validate performance insights
        assert float(dashboard_kpis["avg_execution_time"]) > 0.01
        assert float(dashboard_kpis["fastest_test"]) < float(
            dashboard_kpis["slowest_test"]
        )

        # Validate export contains dashboard data
        assert "test_metrics" in exported_metrics
        assert len(exported_metrics["test_metrics"]) == 40

        # Validate JSON export for dashboard consumption
        dashboard_json = json.dumps(dashboard_kpis)
        dashboard_data = json.loads(dashboard_json)
        assert dashboard_data["total_tests"] == 40
