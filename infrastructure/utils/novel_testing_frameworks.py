"""Novel Testing Methods: Chaos Engineering, Property-Based Testing, and Temporal Invariants

Advanced testing methodologies with mathematical guarantees and innovative validation techniques.
"""

import hashlib
import logging
import random
import statistics
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class NovelTestType(Enum):
    """Classification of novel testing methods."""

    CHAOS_ENGINEERING = 1
    PROPERTY_BASED = 2
    TEMPORAL_INVARIANT = 3
    STRESS_BOUNDARY = 4
    FAULT_INJECTION = 5
    PERFORMANCE_CANARY = 6


@dataclass
class ChaosExperiment:
    """Chaos engineering experiment with controlled failure injection."""

    name: str
    description: str
    fault_type: str
    severity: float  # 0.0 to 1.0
    duration_seconds: int
    target_components: list[str]
    success_criteria: dict[str, Any]
    rollback_procedure: str


@dataclass
class PropertyInvariant:
    """Property-based testing invariant with formal specification."""

    name: str
    description: str
    property_function: Callable[[Any], bool]
    generation_strategy: str
    sample_size: int
    failure_threshold: float


@dataclass
class TemporalInvariant:
    """Temporal invariant with time-based guarantees."""

    name: str
    description: str
    time_window: timedelta
    invariant_function: Callable[[datetime, datetime, Any], bool]
    violation_tolerance: int


class ChaosEngineeringFramework:
    """Advanced chaos engineering with precise failure injection and recovery."""

    def __init__(self):
        self.experiments: dict[str, ChaosExperiment] = {}
        self.active_experiments: set[str] = set()
        self.experiment_history: list[dict[str, Any]] = []
        self.metrics = defaultdict(lambda: defaultdict(list))
        self._chaos_rng = random.Random(42)  # Deterministic chaos

    def register_experiment(self, experiment: ChaosExperiment) -> None:
        """Register a chaos experiment with validation."""
        if experiment.name in self.experiments:
            raise ValueError(f"Experiment {experiment.name} already registered")

        if not 0.0 <= experiment.severity <= 1.0:
            raise ValueError("Severity must be between 0.0 and 1.0")

        if experiment.duration_seconds <= 0:
            raise ValueError("Duration must be positive")

        self.experiments[experiment.name] = experiment
        logger.info(f"Registered chaos experiment: {experiment.name}")

    def execute_experiment(self, experiment_name: str, system_under_test: Any) -> dict[str, Any]:
        """Execute chaos experiment with precise monitoring."""
        if experiment_name not in self.experiments:
            raise ValueError(f"Experiment {experiment_name} not found")

        if experiment_name in self.active_experiments:
            raise ValueError(f"Experiment {experiment_name} already active")

        experiment = self.experiments[experiment_name]
        self.active_experiments.add(experiment_name)

        start_time = datetime.now()
        results = {
            "experiment_name": experiment_name,
            "start_time": start_time.isoformat(),
            "status": "running",
            "metrics": {},
            "violations": [],
            "system_state": {},
        }

        try:
            # Capture baseline metrics
            baseline_metrics = self._capture_system_metrics(system_under_test)
            results["baseline_metrics"] = baseline_metrics

            # Inject fault based on type
            fault_result = self._inject_fault(experiment, system_under_test)
            results["fault_injection"] = fault_result

            # Monitor during experiment
            monitoring_results = self._monitor_during_experiment(
                experiment,
                system_under_test,
                experiment.duration_seconds,
            )
            results["monitoring"] = monitoring_results

            # Evaluate success criteria
            success_evaluation = self._evaluate_success_criteria(
                experiment,
                results,
                baseline_metrics,
            )
            results["success_evaluation"] = success_evaluation

            # Rollback if needed
            if not success_evaluation["passed"]:
                rollback_result = self._rollback_experiment(experiment, system_under_test)
                results["rollback"] = rollback_result

            results["status"] = "completed"

        except (AssertionError, RuntimeError, ValueError, TypeError, AttributeError, OSError) as e:
            results["status"] = "failed"
            results["error"] = str(e)
            logger.error(f"Chaos experiment {experiment_name} failed: {e}")

        finally:
            end_time = datetime.now()
            results["end_time"] = end_time.isoformat()
            results["duration_seconds"] = (end_time - start_time).total_seconds()

            self.active_experiments.discard(experiment_name)
            self.experiment_history.append(results)

        return results

    def _inject_fault(self, experiment: ChaosExperiment, system: Any) -> dict[str, Any]:
        """Inject fault with precise control."""
        fault_type = experiment.fault_type.lower()

        if fault_type == "network_latency":
            return self._inject_network_latency(experiment, system)
        elif fault_type == "packet_loss":
            return self._inject_packet_loss(experiment, system)
        elif fault_type == "service_crash":
            return self._inject_service_crash(experiment, system)
        elif fault_type == "resource_exhaustion":
            return self._inject_resource_exhaustion(experiment, system)
        elif fault_type == "data_corruption":
            return self._inject_data_corruption(experiment, system)
        else:
            raise ValueError(f"Unknown fault type: {fault_type}")

    def _inject_network_latency(self, experiment: ChaosExperiment, system: Any) -> dict[str, Any]:
        """Inject network latency with controlled distribution."""
        latency_ms = int(experiment.severity * 1000)  # 0-1000ms based on severity

        # In real implementation, this would modify network stack
        # For simulation, we add delay to system calls
        if hasattr(system, "add_network_delay"):
            system.add_network_delay(latency_ms)

        return {
            "fault_type": "network_latency",
            "latency_ms": latency_ms,
            "affected_components": experiment.target_components,
        }

    def _inject_packet_loss(self, experiment: ChaosExperiment, system: Any) -> dict[str, Any]:
        """Inject packet loss with controlled probability."""
        loss_rate = experiment.severity  # 0.0 to 1.0

        if hasattr(system, "set_packet_loss"):
            system.set_packet_loss(loss_rate)

        return {
            "fault_type": "packet_loss",
            "loss_rate": loss_rate,
            "affected_components": experiment.target_components,
        }

    def _inject_service_crash(self, experiment: ChaosExperiment, system: Any) -> dict[str, Any]:
        """Simulate service crash with controlled targeting."""
        crashed_components = []

        # Select components based on severity
        num_to_crash = max(1, int(len(experiment.target_components) * experiment.severity))
        selected = self._chaos_rng.sample(experiment.target_components, num_to_crash)

        for component in selected:
            if hasattr(system, "crash_component"):
                system.crash_component(component)
                crashed_components.append(component)

        return {
            "fault_type": "service_crash",
            "crashed_components": crashed_components,
            "total_targeted": len(experiment.target_components),
        }

    def _inject_resource_exhaustion(self, experiment: ChaosExperiment, system: Any) -> dict[str, Any]:
        """Inject resource exhaustion with controlled intensity."""
        exhaustion_level = experiment.severity

        if hasattr(system, "exhaust_resources"):
            system.exhaust_resources(exhaustion_level)

        return {
            "fault_type": "resource_exhaustion",
            "exhaustion_level": exhaustion_level,
            "affected_resources": ["cpu", "memory", "disk", "network"],
        }

    def _inject_data_corruption(self, experiment: ChaosExperiment, system: Any) -> dict[str, Any]:
        """Inject data corruption with controlled scope."""
        corruption_rate = experiment.severity

        if hasattr(system, "corrupt_data"):
            system.corrupt_data(corruption_rate, experiment.target_components)

        return {
            "fault_type": "data_corruption",
            "corruption_rate": corruption_rate,
            "affected_components": experiment.target_components,
        }

    def _monitor_during_experiment(
        self, experiment: ChaosExperiment, system: Any, duration: int
    ) -> dict[str, Any]:
        """Monitor system during chaos experiment."""
        monitoring_data = {
            "timestamps": [],
            "metrics": defaultdict(list),
            "anomalies": [],
        }

        start_time = time.time()
        end_time = start_time + duration

        while time.time() < end_time:
            current_time = time.time()
            timestamp = datetime.now().isoformat()
            monitoring_data["timestamps"].append(timestamp)

            # Capture system metrics
            metrics = self._capture_system_metrics(system)
            for key, value in metrics.items():
                monitoring_data["metrics"][key].append(value)

            # Detect anomalies
            anomalies = self._detect_anomalies(monitoring_data["metrics"])
            if anomalies:
                monitoring_data["anomalies"].extend(anomalies)

            time.sleep(1)  # Monitor every second

        return monitoring_data

    def _capture_system_metrics(self, system: Any) -> dict[str, float]:
        """Capture system metrics with precision."""
        metrics = {}

        # Basic metrics that should be available on any system
        if hasattr(system, "get_response_time"):
            metrics["response_time_ms"] = system.get_response_time()

        if hasattr(system, "get_error_rate"):
            metrics["error_rate"] = system.get_error_rate()

        if hasattr(system, "get_throughput"):
            metrics["throughput_rps"] = system.get_throughput()

        if hasattr(system, "get_cpu_usage"):
            metrics["cpu_usage_percent"] = system.get_cpu_usage()

        if hasattr(system, "get_memory_usage"):
            metrics["memory_usage_percent"] = system.get_memory_usage()

        # Default values if not available
        metrics.setdefault("response_time_ms", 0.0)
        metrics.setdefault("error_rate", 0.0)
        metrics.setdefault("throughput_rps", 0.0)
        metrics.setdefault("cpu_usage_percent", 0.0)
        metrics.setdefault("memory_usage_percent", 0.0)

        return metrics

    def _detect_anomalies(self, metrics_data: dict[str, list[float]]) -> list[dict[str, Any]]:
        """Detect anomalies using statistical methods."""
        anomalies = []

        for metric_name, values in metrics_data.items():
            if len(values) < 10:  # Need sufficient data for analysis
                continue

            # Calculate statistical properties
            mean = statistics.mean(values)
            stdev = statistics.stdev(values)

            # Detect outliers (3-sigma rule)
            for i, value in enumerate(values):
                if stdev > 0 and abs(value - mean) > 3 * stdev:
                    anomalies.append(
                        {
                            "metric": metric_name,
                            "timestamp_index": i,
                            "value": value,
                            "expected_range": [mean - 3 * stdev, mean + 3 * stdev],
                            "deviation": abs(value - mean) / stdev,
                        }
                    )

        return anomalies

    def _evaluate_success_criteria(
        self, experiment: ChaosExperiment, results: dict[str, Any], baseline: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate experiment success against criteria."""
        evaluation = {
            "passed": True,
            "criteria_results": {},
            "summary": "",
        }

        for criterion_name, criterion_config in experiment.success_criteria.items():
            criterion_result = self._evaluate_single_criterion(
                criterion_name,
                criterion_config,
                results,
                baseline,
            )
            evaluation["criteria_results"][criterion_name] = criterion_result

            if not criterion_result["passed"]:
                evaluation["passed"] = False

        evaluation["summary"] = "All criteria passed" if evaluation["passed"] else "Some criteria failed"
        return evaluation

    def _evaluate_single_criterion(
        self, name: str, config: dict[str, Any], results: dict[str, Any], baseline: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate individual success criterion."""
        criterion_type = config.get("type", "threshold")

        if criterion_type == "threshold":
            return self._evaluate_threshold_criterion(name, config, results, baseline)
        elif criterion_type == "availability":
            return self._evaluate_availability_criterion(name, config, results, baseline)
        elif criterion_type == "performance":
            return self._evaluate_performance_criterion(name, config, results, baseline)
        else:
            return {"passed": False, "error": f"Unknown criterion type: {criterion_type}"}

    def _evaluate_threshold_criterion(
        self, name: str, config: dict[str, Any], results: dict[str, Any], baseline: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate threshold-based criterion."""
        metric_name = config["metric"]
        threshold = config["threshold"]
        operator = config.get("operator", "lte")

        # Get metric values from monitoring data
        monitoring = results.get("monitoring", {})
        metrics_data = monitoring.get("metrics", {})
        values = metrics_data.get(metric_name, [])

        if not values:
            return {"passed": False, "error": f"No data for metric {metric_name}"}

        # Evaluate based on operator
        if operator == "lte":
            passed = max(values) <= threshold
        elif operator == "gte":
            passed = min(values) >= threshold
        elif operator == "avg_lte":
            passed = statistics.mean(values) <= threshold
        elif operator == "avg_gte":
            passed = statistics.mean(values) >= threshold
        else:
            return {"passed": False, "error": f"Unknown operator: {operator}"}

        return {
            "passed": passed,
            "metric": metric_name,
            "threshold": threshold,
            "operator": operator,
            "actual_value": max(values)
            if operator.startswith("max")
            else min(values)
            if operator.startswith("min")
            else statistics.mean(values),
            "samples": len(values),
        }

    def _evaluate_availability_criterion(
        self, name: str, config: dict[str, Any], results: dict[str, Any], baseline: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate availability criterion."""
        min_availability = config.get("min_availability", 0.99)

        # Calculate availability from error rates
        monitoring = results.get("monitoring", {})
        error_rates = monitoring.get("metrics", {}).get("error_rate", [])

        if not error_rates:
            return {"passed": False, "error": "No error rate data available"}

        # Availability = 1 - average error rate
        avg_error_rate = statistics.mean(error_rates)
        availability = 1.0 - avg_error_rate

        passed = availability >= min_availability

        return {
            "passed": passed,
            "availability": availability,
            "min_required": min_availability,
            "avg_error_rate": avg_error_rate,
            "samples": len(error_rates),
        }

    def _evaluate_performance_criterion(
        self, name: str, config: dict[str, Any], results: dict[str, Any], baseline: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate performance criterion."""
        max_degradation = config.get("max_degradation", 0.5)  # 50% degradation max
        metric_name = config["metric"]

        # Get baseline and current values
        baseline_value = baseline.get(metric_name, 0.0)
        monitoring = results.get("monitoring", {})
        current_values = monitoring.get("metrics", {}).get(metric_name, [])

        if not current_values:
            return {"passed": False, "error": f"No current data for metric {metric_name}"}

        avg_current = statistics.mean(current_values)

        if baseline_value == 0:
            # If baseline is 0, check absolute value
            passed = avg_current <= config.get("max_absolute", 1000.0)
        else:
            # Check relative degradation
            degradation = (avg_current - baseline_value) / baseline_value
            passed = degradation <= max_degradation

        return {
            "passed": passed,
            "baseline_value": baseline_value,
            "current_avg": avg_current,
            "degradation": (avg_current - baseline_value) / baseline_value if baseline_value > 0 else 0.0,
            "max_allowed_degradation": max_degradation,
            "samples": len(current_values),
        }

    def _rollback_experiment(self, experiment: ChaosExperiment, system: Any) -> dict[str, Any]:
        """Rollback experiment changes."""
        rollback_result = {
            "procedure": experiment.rollback_procedure,
            "actions_taken": [],
        }

        # Rollback based on fault type
        fault_type = experiment.fault_type.lower()

        if fault_type == "network_latency" and hasattr(system, "remove_network_delay"):
            system.remove_network_delay()
            rollback_result["actions_taken"].append("removed_network_delay")

        elif fault_type == "packet_loss" and hasattr(system, "set_packet_loss"):
            system.set_packet_loss(0.0)
            rollback_result["actions_taken"].append("reset_packet_loss")

        elif fault_type == "service_crash" and hasattr(system, "recover_components"):
            recovered = system.recover_components(experiment.target_components)
            rollback_result["actions_taken"].append(f"recovered_components: {recovered}")

        elif fault_type == "resource_exhaustion" and hasattr(system, "restore_resources"):
            system.restore_resources()
            rollback_result["actions_taken"].append("restored_resources")

        elif fault_type == "data_corruption" and hasattr(system, "restore_data"):
            system.restore_data()
            rollback_result["actions_taken"].append("restored_data")

        rollback_result["timestamp"] = datetime.now().isoformat()
        return rollback_result

    def get_chaos_summary(self) -> dict[str, Any]:
        """Get comprehensive chaos engineering summary."""
        total_experiments = len(self.experiment_history)
        successful_experiments = sum(1 for e in self.experiment_history if e.get("status") == "completed")

        return {
            "registered_experiments": len(self.experiments),
            "total_executed": total_experiments,
            "successful": successful_experiments,
            "success_rate": successful_experiments / max(1, total_experiments),
            "active_experiments": list(self.active_experiments),
            "experiment_types": list(
                set(
                    e["fault_injection"]["fault_type"]
                    for e in self.experiment_history
                    if "fault_injection" in e
                )
            ),
            "average_duration": statistics.mean([e["duration_seconds"] for e in self.experiment_history])
            if self.experiment_history
            else 0.0,
        }


class PropertyBasedTestingFramework:
    """Advanced property-based testing with mathematical invariants."""

    def __init__(self):
        self.invariants: dict[str, PropertyInvariant] = {}
        self.test_results: list[dict[str, Any]] = []
        self.generators = {}
        self._setup_default_generators()

    def _setup_default_generators(self) -> None:
        """Setup default data generators."""
        self.generators = {
            "strings": lambda: self._generate_string(),
            "integers": lambda: self._generate_integer(),
            "floats": lambda: self._generate_float(),
            "lists": lambda: self._generate_list(),
            "dictionaries": lambda: self._generate_dictionary(),
            "timestamps": lambda: self._generate_timestamp(),
            "uuids": lambda: self._generate_uuid(),
        }

    def _generate_string(self) -> str:
        """Generate random string with controlled properties."""
        length = random.randint(1, 100)
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return "".join(random.choice(chars) for _ in range(length))

    def _generate_integer(self) -> int:
        """Generate random integer with controlled range."""
        return random.randint(-1000000, 1000000)

    def _generate_float(self) -> float:
        """Generate random float with controlled precision."""
        return round(random.uniform(-1000000.0, 1000000.0), 6)

    def _generate_list(self) -> list[Any]:
        """Generate random list with mixed types."""
        length = random.randint(0, 20)
        generator_types = ["strings", "integers", "floats"]
        return [self.generators[random.choice(generator_types)]() for _ in range(length)]

    def _generate_dictionary(self) -> dict[str, Any]:
        """Generate random dictionary with mixed types."""
        size = random.randint(0, 10)
        generator_types = ["strings", "integers", "floats", "lists"]
        return {
            self._generate_string(): self.generators[random.choice(generator_types)]() for _ in range(size)
        }

    def _generate_timestamp(self) -> datetime:
        """Generate random timestamp within reasonable range."""
        start = datetime(2020, 1, 1)
        end = datetime(2030, 12, 31)
        delta = end - start
        random_days = random.randint(0, delta.days)
        random_seconds = random.randint(0, 86400)
        return start + timedelta(days=random_days, seconds=random_seconds)

    def _generate_uuid(self) -> str:
        """Generate UUID-like string."""
        return hashlib.md5(f"{random.random()}{time.time()}".encode()).hexdigest()

    def register_invariant(self, invariant: PropertyInvariant) -> None:
        """Register property invariant for testing."""
        if invariant.name in self.invariants:
            raise ValueError(f"Invariant {invariant.name} already registered")

        if invariant.sample_size <= 0:
            raise ValueError("Sample size must be positive")

        if not 0.0 <= invariant.failure_threshold <= 1.0:
            raise ValueError("Failure threshold must be between 0.0 and 1.0")

        self.invariants[invariant.name] = invariant
        logger.info(f"Registered property invariant: {invariant.name}")

    def test_invariant(self, invariant_name: str, system_under_test: Any) -> dict[str, Any]:
        """Test individual property invariant."""
        if invariant_name not in self.invariants:
            raise ValueError(f"Invariant {invariant_name} not found")

        invariant = self.invariants[invariant_name]

        test_result = {
            "invariant_name": invariant_name,
            "start_time": datetime.now().isoformat(),
            "sample_size": invariant.sample_size,
            "strategy": invariant.generation_strategy,
            "results": [],
        }

        failures = 0
        counterexamples = []

        for i in range(invariant.sample_size):
            # Generate test case based on strategy
            test_input = self._generate_test_case(invariant.generation_strategy)

            try:
                # Test the property
                property_result = invariant.property_function(test_input)

                result_entry = {
                    "sample_index": i,
                    "input": test_input,
                    "result": property_result,
                    "timestamp": datetime.now().isoformat(),
                }

                if not property_result:
                    failures += 1
                    counterexamples.append(test_input)
                    result_entry["status"] = "failed"
                else:
                    result_entry["status"] = "passed"

                test_result["results"].append(result_entry)

            except (AssertionError, RuntimeError, ValueError, TypeError, AttributeError) as e:
                failures += 1
                test_result["results"].append(
                    {
                        "sample_index": i,
                        "input": test_input,
                        "status": "error",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        # Calculate final results
        failure_rate = failures / invariant.sample_size
        passed = failure_rate <= invariant.failure_threshold

        test_result.update(
            {
                "end_time": datetime.now().isoformat(),
                "failures": failures,
                "failure_rate": failure_rate,
                "passed": passed,
                "counterexamples": counterexamples[:5],  # Limit to first 5
                "summary": f"Passed {invariant.sample_size - failures}/{invariant.sample_size} samples",
            }
        )

        self.test_results.append(test_result)
        return test_result

    def _generate_test_case(self, strategy: str) -> Any:
        """Generate test case based on strategy."""
        if strategy in self.generators:
            return self.generators[strategy]()
        elif strategy.startswith("tuple:"):
            types = strategy[6:].split(",")
            return tuple(self.generators[t.strip()]() for t in types)
        elif strategy.startswith("list:"):
            types = strategy[5:].split(",")
            return [self.generators[t.strip()]() for t in types]
        elif strategy.startswith("dict:"):
            parts = strategy[5:].split(",")
            return {parts[0]: self.generators[parts[1]]() for _ in range(random.randint(1, 5))}
        else:
            # Default to string generation
            return self._generate_string()

    def test_all_invariants(self, system_under_test: Any) -> dict[str, Any]:
        """Test all registered invariants."""
        all_results = {}

        for invariant_name in self.invariants:
            try:
                result = self.test_invariant(invariant_name, system_under_test)
                all_results[invariant_name] = result
            except (AssertionError, RuntimeError, ValueError, TypeError, AttributeError) as e:
                all_results[invariant_name] = {
                    "error": str(e),
                    "status": "failed",
                }

        # Calculate summary
        total_invariants = len(all_results)
        passed_invariants = sum(1 for r in all_results.values() if r.get("passed", False))

        return {
            "summary": {
                "total_invariants": total_invariants,
                "passed_invariants": passed_invariants,
                "pass_rate": passed_invariants / total_invariants,
                "timestamp": datetime.now().isoformat(),
            },
            "results": all_results,
        }

    def get_property_summary(self) -> dict[str, Any]:
        """Get comprehensive property-based testing summary."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for t in self.test_results if t.get("passed", False))

        return {
            "registered_invariants": len(self.invariants),
            "total_tests_executed": total_tests,
            "passed_tests": passed_tests,
            "pass_rate": passed_tests / max(1, total_tests),
            "invariant_names": list(self.invariants.keys()),
            "generation_strategies": list(set(t.get("strategy", "unknown") for t in self.test_results)),
        }


class TemporalInvariantTesting:
    """Advanced temporal invariant testing with time-based guarantees."""

    def __init__(self):
        self.invariants: dict[str, TemporalInvariant] = None
        self.invariants = {}
        self.violation_history: list[dict[str, Any]] = []
        self.time_series_data: dict[str, list[tuple[datetime, Any]]] = defaultdict(list)

    def register_temporal_invariant(self, invariant: TemporalInvariant) -> None:
        """Register temporal invariant for monitoring."""
        if invariant.name in self.invariants:
            raise ValueError(f"Temporal invariant {invariant.name} already registered")

        if invariant.time_window.total_seconds() <= 0:
            raise ValueError("Time window must be positive")

        if invariant.violation_tolerance < 0:
            raise ValueError("Violation tolerance must be non-negative")

        self.invariants[invariant.name] = invariant
        logger.info(f"Registered temporal invariant: {invariant.name}")

    def record_event(self, invariant_name: str, timestamp: datetime, data: Any) -> bool:
        """Record event and check temporal invariant."""
        if invariant_name not in self.invariants:
            raise ValueError(f"Temporal invariant {invariant_name} not found")

        # Store time series data
        self.time_series_data[invariant_name].append((timestamp, data))

        # Check invariant
        invariant = self.invariants[invariant_name]
        window_start = timestamp - invariant.time_window

        # Get events within time window
        events_in_window = [
            (ts, data) for ts, data in self.time_series_data[invariant_name] if ts >= window_start
        ]

        if len(events_in_window) < 2:
            return True  # Not enough data to check invariant

        # Check invariant function
        try:
            oldest_timestamp = min(ts for ts, _ in events_in_window)
            newest_timestamp = max(ts for ts, _ in events_in_window)

            invariant_holds = invariant.invariant_function(
                oldest_timestamp,
                newest_timestamp,
                events_in_window,
            )

            if not invariant_holds:
                self._record_violation(invariant_name, events_in_window, oldest_timestamp, newest_timestamp)

            return invariant_holds

        except (AssertionError, RuntimeError, ValueError, TypeError, AttributeError) as e:
            self._record_violation(invariant_name, events_in_window, window_start, timestamp, str(e))
            return False

    def _record_violation(
        self,
        invariant_name: str,
        events: list[tuple[datetime, Any]],
        start_time: datetime,
        end_time: datetime,
        error: str = "",
    ) -> None:
        """Record temporal invariant violation."""
        violation = {
            "invariant_name": invariant_name,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "event_count": len(events),
            "violation_time": datetime.now().isoformat(),
            "error": error,
        }

        self.violation_history.append(violation)
        logger.warning(f"Temporal invariant violation: {invariant_name}")

    def get_temporal_summary(self) -> dict[str, Any]:
        """Get comprehensive temporal invariant testing summary."""
        total_violations = len(self.violation_history)
        violations_by_invariant = defaultdict(int)

        for violation in self.violation_history:
            violations_by_invariant[violation["invariant_name"]] += 1

        return {
            "registered_invariants": len(self.invariants),
            "total_violations": total_violations,
            "violations_by_invariant": dict(violations_by_invariant),
            "invariant_names": list(self.invariants.keys()),
            "time_series_data_points": {name: len(data) for name, data in self.time_series_data.items()},
        }


# Export novel testing frameworks
__all__ = [
    "NovelTestType",
    "ChaosExperiment",
    "PropertyInvariant",
    "TemporalInvariant",
    "ChaosEngineeringFramework",
    "PropertyBasedTestingFramework",
    "TemporalInvariantTesting",
]
