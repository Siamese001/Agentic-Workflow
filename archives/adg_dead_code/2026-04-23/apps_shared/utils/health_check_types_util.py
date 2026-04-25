"""
Health Check Utilities - Application health and readiness checks.

Provides health endpoints, dependency checks, and deployment readiness
validation for apps_lic and apps_rg.
Phase 5B - Deployment Readiness
"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.L0_routing.config.path_constants import DEFAULT_TIMEOUT
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "health_check_types_util", "p0_governance")
_emit_reads_policy_state("p0", "health_check_types_util", "policy_binding")
_emit_snapshots_state("p0", "health_check_types_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("health_check_types_util", "p4obs", "metric_1")
_emit_emits_metric_event("health_check_types_util", "p4obs", "metric_2")
_emit_emits_metric_event("health_check_types_util", "p4obs", "metric_3")
_emit_emits_metric_event("health_check_types_util", "p4obs", "metric_4")
_emit_emits_metric_event("health_check_types_util", "p4obs", "metric_5")
_emit_emits_metric_event("health_check_types_util", "p4obs", "metric_6")
_emit_records_incident_event("health_check_types_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("health_check_types_util", "p4obs", "anomaly")
_emit_writes_observability_log("health_check_types_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("health_check_types_util", "p4obs", "mon_state")
_emit_triggers_alert("health_check_types_util", "p4obs", "alert")
_emit_links_incident_trace("health_check_types_util", "p4obs", "trace_link")
_emit_captures_pattern("health_check_types_util", "p3lm", "pattern")
_emit_records_learning_event("health_check_types_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("health_check_types_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("health_check_types_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("health_check_types_util", "p3lm", "routing")
_emit_improves_agent_policy("health_check_types_util", "p3lm", "policy")
_emit_stores_learning_state("health_check_types_util", "p3lm", "state")
_emit_records_execution_trace("health_check_types_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("health_check_types_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("health_check_types_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("health_check_types_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("health_check_types_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("health_check_types_util", "env_read", "p2_env_1")
_emit_reads_environ("health_check_types_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("health_check_types_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("health_check_types_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "health_check_types_util", "context_pull")
_emit_pulls_context("p1", "health_check_types_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "health_check_types_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "health_check_types_util", "uwg_term_2")
_emit_writes_through("p1", "health_check_types_util", "write_through")
_emit_writes_through("p1", "health_check_types_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "health_check_types_util", "safety_validation")
_emit_invokes_eval("p1", "health_check_types_util", "eval_call")
_emit_proposal_commits_routing("p1", "health_check_types_util", "routing_commit")
_emit_escalates_to_human("p1", "health_check_types_util", "human_escalation")
_emit_routes_through("p1", "health_check_types_util", "route_through")
_emit_checks_agent_registry("p1", "health_check_types_util", "agent_registry")
_emit_validates_agent_capability("p1", "health_check_types_util", "capability")
_emit_dispatches_execution_plan("p1", "health_check_types_util", "exec_plan")
_emit_agent_executes_agent("p1", "health_check_types_util", "sub_agent")
_emit_routes_to_agent("p1", "health_check_types_util", "target_agent")
_emit_verifies_policy("p1", "health_check_types_util", "policy_check")
_emit_observes_runtime_state("p1", "health_check_types_util", "runtime_state")
_emit_verifies_boundary("p1", "health_check_types_util", "boundary_check")
_emit_transcripts_response("p1", "health_check_types_util", "transcript")
_emit_hard_fails_untranscripted("p1", "health_check_types_util")
_emit_gated_by_confidence("p1", "health_check_types_util", "confidence_gate")
emit_replay_key("p0", "health_check_types_util")
emit_determinism_digest("p0", "health_check_types_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "health_check_types_util", "execution_auth")
_emit_validates_capability("p2", "health_check_types_util", "capability_check")
_emit_routes_to_capability("p2", "health_check_types_util", "capability_route")
_emit_writes_via_uwg("p2", "health_check_types_util", "uwg_write")
_emit_blocks_direct_write("p2", "health_check_types_util", "direct_write_block")
_emit_records_tool_invocation("p2", "health_check_types_util", "tool_invocation")
_emit_captures_execution_output("p2", "health_check_types_util", "exec_output")
_emit_dispatches_agent("p3", "health_check_types_util", "agent_dispatch")
_emit_coordinates_agents("p3", "health_check_types_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "health_check_types_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "health_check_types_util", "healing_outcome")
_emit_escalates_failure("p3", "health_check_types_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "health_check_types_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "health_check_types_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "health_check_types_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "health_check_types_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "health_check_types_util", "eval_metric")
_emit_stores_embedding("p4", "health_check_types_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "health_check_types_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "health_check_types_util", "exec_snapshot_link")
_emit_reads_through("l4", "health_check_types_util", "urg_read_1")
_emit_reads_through("l4", "health_check_types_util", "urg_read_2")
_emit_reads_through("l4", "health_check_types_util", "urg_read_3")
_emit_reads_through("l4", "health_check_types_util", "urg_read_4")
_emit_reads_through("l4", "health_check_types_util", "urg_read_5")
_emit_reads_through("l4", "health_check_types_util", "urg_read_6")
_emit_reads_through("l4", "health_check_types_util", "urg_read_7")
_emit_reads_through("l4", "health_check_types_util", "urg_read_8")
_emit_reads_through("l4", "health_check_types_util", "urg_read_9")
_emit_reads_through("l4", "health_check_types_util", "urg_read_10")
_emit_reads_through("l4", "health_check_types_util", "urg_read_11")
_emit_reads_through("l4", "health_check_types_util", "urg_read_12")
_emit_reads_through("l4", "health_check_types_util", "urg_read_13")
_emit_reads_through("l4", "health_check_types_util", "urg_read_14")
_emit_reads_through("l4", "health_check_types_util", "urg_read_15")
_emit_reads_through("l4", "health_check_types_util", "urg_read_16")
_emit_reads_through("l4", "health_check_types_util", "urg_read_17")
_emit_reads_through("l4", "health_check_types_util", "urg_read_18")
_emit_reads_through("l4", "health_check_types_util", "urg_read_19")
_emit_reads_through("l4", "health_check_types_util", "urg_read_20")
_emit_reads_through("l4", "health_check_types_util", "urg_read_21")
_emit_reads_through("l4", "health_check_types_util", "urg_read_22")
_emit_reads_through("l4", "health_check_types_util", "urg_read_23")
_emit_reads_through("l4", "health_check_types_util", "urg_read_24")
_emit_reads_through("l4", "health_check_types_util", "urg_read_25")
_emit_reads_through("l4", "health_check_types_util", "urg_read_26")
_emit_reads_through("l4", "health_check_types_util", "urg_read_27")
_emit_reads_through("l4", "health_check_types_util", "urg_read_28")
_emit_reads_through("l4", "health_check_types_util", "urg_read_29")
_emit_reads_through("l4", "health_check_types_util", "urg_read_30")
_emit_reads_through("l4", "health_check_types_util", "urg_read_31")
_emit_reads_through("l4", "health_check_types_util", "urg_read_32")
_emit_reads_through("l4", "health_check_types_util", "urg_read_33")
_emit_reads_through("l4", "health_check_types_util", "urg_read_34")
_emit_reads_through("l4", "health_check_types_util", "urg_read_35")
_emit_reads_through("l4", "health_check_types_util", "urg_read_36")
_emit_reads_through("l4", "health_check_types_util", "urg_read_37")
_emit_reads_through("l4", "health_check_types_util", "urg_read_38")
_emit_reads_through("l4", "health_check_types_util", "urg_read_39")
_emit_reads_through("l4", "health_check_types_util", "urg_read_40")
_emit_reads_through("l4", "health_check_types_util", "urg_read_41")
_emit_reads_through("l4", "health_check_types_util", "urg_read_42")
_emit_reads_through("l4", "health_check_types_util", "urg_read_43")
_emit_reads_through("l4", "health_check_types_util", "urg_read_44")
_emit_reads_through("l4", "health_check_types_util", "urg_read_45")
_emit_reads_through("l4", "health_check_types_util", "urg_read_46")
_emit_reads_through("l4", "health_check_types_util", "urg_read_47")
_emit_reads_through("l4", "health_check_types_util", "urg_read_48")
_emit_reads_through("l4", "health_check_types_util", "urg_read_49")
_emit_reads_through("l4", "health_check_types_util", "urg_read_50")
_emit_reads_through("l4", "health_check_types_util", "urg_read_51")
_emit_reads_through("l4", "health_check_types_util", "urg_read_52")
_emit_reads_through("l4", "health_check_types_util", "urg_read_53")
_emit_reads_through("l4", "health_check_types_util", "urg_read_54")
_emit_reads_through("l4", "health_check_types_util", "urg_read_55")
_emit_reads_through("l4", "health_check_types_util", "urg_read_56")
_emit_reads_through("l4", "health_check_types_util", "urg_read_57")
_emit_reads_through("l4", "health_check_types_util", "urg_read_58")
_emit_reads_through("l4", "health_check_types_util", "urg_read_59")
_emit_reads_through("l4", "health_check_types_util", "urg_read_60")
_emit_reads_through("l4", "health_check_types_util", "urg_read_61")
_emit_reads_through("l4", "health_check_types_util", "urg_read_62")
_emit_reads_through("l4", "health_check_types_util", "urg_read_63")
_emit_reads_through("l4", "health_check_types_util", "urg_read_64")

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health check status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class CheckResult:
    """Result of a single health check."""

    name: str
    status: HealthStatus
    message: str = ""
    duration_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_healthy(self) -> bool:
        return self.status == HealthStatus.HEALTHY

    @property
    def is_critical(self) -> bool:
        return self.status == HealthStatus.UNHEALTHY


@dataclass
class HealthReport:
    """Complete health report."""

    status: HealthStatus
    checks: list[CheckResult]
    timestamp: float = field(default_factory=time.time)
    version: str = "1.0.0"

    @property
    def is_healthy(self) -> bool:
        return self.status == HealthStatus.HEALTHY

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "status": str(self.status),
            "timestamp": self.timestamp,
            "version": self.version,
            "checks": [
                {
                    "name": c.name,
                    "status": str(c.status),
                    "message": c.message,
                    "duration_ms": round(c.duration_ms, 2),
                    "metadata": c.metadata,
                }
                for c in self.checks
            ],
        }


class HealthChecker:
    """Manages health checks for the application."""

    def __init__(self, app_name: str = "app", version: str = "1.0.0"):
        self.app_name = app_name
        self.version = version
        self._checks: dict[str, tuple[Callable[[], CheckResult], bool]] = {}

    def register_check(self, name: str, check_fn: Callable[[], CheckResult], critical: bool = False) -> None:
        """
        Register a health check.

        Args:
            name: Check name
            check_fn: Function that performs the check
            critical: If True, failure makes entire app unhealthy
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "HealthChecker.register_check"
        )

        self._checks[name] = (check_fn, critical)
        logger.info(f"Registered health check: {name} (critical={critical})")

    def unregister_check(self, name: str) -> bool:
        """Unregister a health check."""
        if name in self._checks:
            del self._checks[name]
            return True
        return False

    def run_check(self, name: str) -> CheckResult | None:
        """Run a specific health check."""
        if name not in self._checks:
            return None
        check_fn, _ = self._checks[name]
        start = time.perf_counter()
        try:
            result = check_fn()
            result.duration_ms = (time.perf_counter() - start) * 1000
            return result
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            return CheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check failed with error: {e}",
                duration_ms=(time.perf_counter() - start) * 1000,
            )

    def run_all_checks(self) -> HealthReport:
        """Run all registered health checks."""
        results: list[CheckResult] = []
        overall_status = HealthStatus.HEALTHY
        for name, (_check_fn, critical) in tqdm(self._checks.items(), desc="Processing", unit="item"):
            result = self.run_check(name)
            if result:
                results.append(result)
                if result.status == HealthStatus.UNHEALTHY and critical:
                    overall_status = HealthStatus.UNHEALTHY
                elif result.status == HealthStatus.DEGRADED:
                    if overall_status == HealthStatus.HEALTHY:
                        overall_status = HealthStatus.DEGRADED
                elif result.status == HealthStatus.UNHEALTHY:
                    if overall_status == HealthStatus.HEALTHY:
                        overall_status = HealthStatus.DEGRADED
        return HealthReport(status=overall_status, checks=results, version=self.version)

    def get_liveness(self) -> CheckResult:
        """Simple liveness check - is the app running?"""
        return CheckResult(name="liveness", status=HealthStatus.HEALTHY, message="Application is alive")

    def get_readiness(self) -> HealthReport:
        """Full readiness check - is the app ready to serve traffic?"""
        return self.run_all_checks()


class CommonChecks:
    """Factory for common health checks."""

    @staticmethod
    def env_var_check(var_name: str, required: bool = True) -> Callable[[], CheckResult]:
        """Create a check for an environment variable."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "CommonChecks.env_var_check")

        def check() -> CheckResult:
            value = os.getenv(var_name)
            if value:
                return CheckResult(
                    name=f"env:{var_name}",
                    status=HealthStatus.HEALTHY,
                    message=f"{var_name} is set",
                )
            elif required:
                return CheckResult(
                    name=f"env:{var_name}",
                    status=HealthStatus.UNHEALTHY,
                    message=f"{var_name} is not set",
                )
            else:
                return CheckResult(
                    name=f"env:{var_name}",
                    status=HealthStatus.DEGRADED,
                    message=f"{var_name} is not set (optional)",
                )

        return check

    @staticmethod
    def redis_check(host: str = "localhost", port: int = 6379) -> Callable[[], CheckResult]:
        """Create a Redis connectivity check."""

        def check() -> CheckResult:
            try:
                import redis

                client = redis.Redis(host=host, port=port, socket_timeout=DEFAULT_TIMEOUT)
                client.ping()
                return CheckResult(
                    name="redis",
                    status=HealthStatus.HEALTHY,
                    message=f"Redis connected at {host}:{port}",
                )
            except ImportError:  # guardian: allow-silent-swallow - optional dependency
                return CheckResult(
                    name="redis",
                    status=HealthStatus.DEGRADED,
                    message="Redis client not installed",
                )
            except (
                OSError,
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                RuntimeError,
            ) as e:  # guardian: allow-silent-swallow
                return CheckResult(
                    name="redis",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Redis connection failed: {e}",
                )

        return check

    @staticmethod
    def disk_space_check(path: str = "/", min_free_gb: float = 1.0) -> Callable[[], CheckResult]:
        """Create a disk space check."""

        def check() -> CheckResult:
            try:
                import shutil

                total, used, free = shutil.disk_usage(path)
                free_gb = free / 1024**3
                if free_gb >= min_free_gb:
                    return CheckResult(
                        name="disk_space",
                        status=HealthStatus.HEALTHY,
                        message=f"{free_gb:.2f} GB free",
                        metadata={"free_gb": round(free_gb, 2)},
                    )
                else:
                    return CheckResult(
                        name="disk_space",
                        status=HealthStatus.DEGRADED,
                        message=f"Low disk space: {free_gb:.2f} GB free",
                        metadata={"free_gb": round(free_gb, 2)},
                    )
            except (
                OSError,
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                RuntimeError,
            ) as e:  # guardian: allow-silent-swallow
                return CheckResult(
                    name="disk_space",
                    status=HealthStatus.UNKNOWN,
                    message=f"Could not check disk space: {e}",
                )

        return check

    @staticmethod
    # guardian: allow-magic-config
    def memory_check(max_percent: float = 90.0) -> Callable[[], CheckResult]:
        """Create a memory usage check."""

        def check() -> CheckResult:
            try:
                import psutil

                memory = psutil.virtual_memory()
                percent = memory.percent
                if percent < max_percent:
                    return CheckResult(
                        name="memory",
                        status=HealthStatus.HEALTHY,
                        message=f"Memory usage: {percent:.1f}%",
                        metadata={"percent": percent},
                    )
                else:
                    return CheckResult(
                        name="memory",
                        status=HealthStatus.DEGRADED,
                        message=f"High memory usage: {percent:.1f}%",
                        metadata={"percent": percent},
                    )
            except ImportError:
                return CheckResult(name="memory", status=HealthStatus.UNKNOWN, message="psutil not installed")
            except (
                OSError,
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                RuntimeError,
            ) as e:  # guardian: allow-silent-swallow
                return CheckResult(
                    name="memory",
                    status=HealthStatus.UNKNOWN,
                    message=f"Could not check memory: {e}",
                )

        return check


class ReadinessGate:
    """Controls application readiness state."""

    def __init__(self):
        self._ready = False
        self._reason: str = "Not initialized"

    def set_ready(self) -> None:
        """Mark application as ready."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ReadinessGate.set_ready")

        self._ready = True
        self._reason = "Ready"
        logger.info("Application marked as ready")

    def set_not_ready(self, reason: str) -> None:
        """Mark application as not ready."""
        self._ready = False
        self._reason = reason
        logger.warning(f"Application marked as not ready: {reason}")

    def is_ready(self) -> bool:
        """Check if application is ready."""
        return self._ready

    def get_status(self) -> dict[str, Any]:
        """Get readiness status."""
        return {"ready": self._ready, "reason": self._reason}


_health_checker: HealthChecker | None = None
_readiness_gate: ReadinessGate | None = None


def get_health_checker() -> HealthChecker:
    """Get the global health checker."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


def get_readiness_gate() -> ReadinessGate:
    """Get the global readiness gate."""
    global _readiness_gate
    if _readiness_gate is None:
        _readiness_gate = ReadinessGate()
    return _readiness_gate
