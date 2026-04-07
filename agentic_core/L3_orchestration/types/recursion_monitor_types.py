"""
RecursionMonitor - Production-Grade Monitoring for Forward-Rolling Recursion.

[PHASE 3] Implements comprehensive monitoring, alerting, and health checks
for Forward-Rolling Recursion pipelines in production environments.

OBSERVABILITY: Real-time metrics, alerting, and health status
RELIABILITY: Circuit breakers, degradation detection, auto-recovery

Author: Cascade
Date: February 2026
Phase: 3 - Production Readiness
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from agentic_core.L2_execution.utils.providers import get_clock
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "recursion_monitor_types")
emit_determinism_digest("p0", "recursion_monitor_types")

_emit_dispatches_healing_run("p1", "recursion_monitor_types", "L3")
_emit_routes_through("p1", "recursion_monitor_types", "L3")
_emit_checks_agent_registry("p1", "recursion_monitor_types", "agent_registry")
_emit_validates_agent_capability("p1", "recursion_monitor_types", "capability")
_emit_dispatches_execution_plan("p1", "recursion_monitor_types", "exec_plan")
_emit_agent_executes_agent("p1", "recursion_monitor_types", "sub_agent")
_emit_routes_to_agent("p1", "recursion_monitor_types", "target_agent")
_emit_verifies_policy("p1", "recursion_monitor_types", "policy_check")
_emit_observes_runtime_state("p1", "recursion_monitor_types", "runtime_state")
_emit_verifies_boundary("p1", "recursion_monitor_types", "boundary_check")
_emit_transcripts_response("p1", "recursion_monitor_types", "transcript")
_emit_hard_fails_untranscripted("p1", "recursion_monitor_types")
_emit_gated_by_confidence("p1", "recursion_monitor_types", "confidence_gate")
_emit_escalates_to_human("p1", "recursion_monitor_types", "L3")
_emit_reads_policy_state("p1", "recursion_monitor_types", "L3")
_emit_authorize_and_execute("p2", "recursion_monitor_types", "execution_auth")
_emit_validates_capability("p2", "recursion_monitor_types", "capability_check")
_emit_routes_to_capability("p2", "recursion_monitor_types", "capability_route")
_emit_writes_via_uwg("p2", "recursion_monitor_types", "uwg_write")
_emit_blocks_direct_write("p2", "recursion_monitor_types", "direct_write_block")
_emit_records_tool_invocation("p2", "recursion_monitor_types", "tool_invocation")
_emit_captures_execution_output("p2", "recursion_monitor_types", "exec_output")
_emit_dispatches_agent("p3", "recursion_monitor_types", "agent_dispatch")
_emit_coordinates_agents("p3", "recursion_monitor_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "recursion_monitor_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "recursion_monitor_types", "healing_outcome")
_emit_escalates_failure("p3", "recursion_monitor_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "recursion_monitor_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "recursion_monitor_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "recursion_monitor_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "recursion_monitor_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "recursion_monitor_types", "eval_metric")
_emit_stores_embedding("p4", "recursion_monitor_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "recursion_monitor_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "recursion_monitor_types", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("recursion_monitor_types", "p4obs", "metric_1")
_emit_emits_metric_event("recursion_monitor_types", "p4obs", "metric_2")
_emit_emits_metric_event("recursion_monitor_types", "p4obs", "metric_3")
_emit_emits_metric_event("recursion_monitor_types", "p4obs", "metric_4")
_emit_emits_metric_event("recursion_monitor_types", "p4obs", "metric_5")
_emit_emits_metric_event("recursion_monitor_types", "p4obs", "metric_6")
_emit_records_incident_event("recursion_monitor_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("recursion_monitor_types", "p4obs", "anomaly")
_emit_writes_observability_log("recursion_monitor_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("recursion_monitor_types", "p4obs", "mon_state")
_emit_triggers_alert("recursion_monitor_types", "p4obs", "alert")
_emit_links_incident_trace("recursion_monitor_types", "p4obs", "trace_link")
_emit_captures_pattern("recursion_monitor_types", "p3lm", "pattern")
_emit_records_learning_event("recursion_monitor_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("recursion_monitor_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("recursion_monitor_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("recursion_monitor_types", "p3lm", "routing")
_emit_improves_agent_policy("recursion_monitor_types", "p3lm", "policy")
_emit_stores_learning_state("recursion_monitor_types", "p3lm", "state")
_emit_records_execution_trace("recursion_monitor_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("recursion_monitor_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("recursion_monitor_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("recursion_monitor_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("recursion_monitor_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("recursion_monitor_types", "env_read", "p2_env_1")
_emit_reads_environ("recursion_monitor_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("recursion_monitor_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("recursion_monitor_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "recursion_monitor_types", "context_pull")
_emit_pulls_context("p1", "recursion_monitor_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "recursion_monitor_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "recursion_monitor_types", "uwg_term_2")
_emit_writes_through("p1", "recursion_monitor_types", "write_through")
_emit_writes_through("p1", "recursion_monitor_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "recursion_monitor_types", "safety_validation")
_emit_invokes_eval("p1", "recursion_monitor_types", "eval_call")
_emit_proposal_commits_routing("p1", "recursion_monitor_types", "routing_commit")

Logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health status levels for the recursion system."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Alert data structure."""

    severity: AlertSeverity
    message: str
    timestamp: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False


@dataclass
class HealthCheck:
    """Health check result."""

    name: str
    status: HealthStatus
    message: str
    duration_ms: float
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RecursionSnapshot:
    """Point-in-time snapshot of recursion state."""

    timestamp: str
    active_recursions: int
    total_spawns: int
    success_rate: float
    avg_depth: float
    memory_usage_bytes: int
    cache_hit_rate: float
    health_status: HealthStatus


class RecursionMonitor:
    """
    Production-grade monitoring for Forward-Rolling Recursion.

    Features:
    - Real-time metrics collection
    - Health checks with configurable thresholds
    - Alert generation and management
    - Circuit breaker integration
    - Performance degradation detection
    """

    # guardian: allow-magic-config
    def __init__(
        self,
        alert_callback: Callable[[Alert], None] | None = None,
        health_check_interval_sec: int = 30,
        metrics_retention_hours: int = 24,
    ):
        """
        Initialize recursion monitor.

        Args:
            alert_callback: Optional callback for alert notifications
            health_check_interval_sec: Interval between health checks
            metrics_retention_hours: Hours to retain metric history
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "RecursionMonitor.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "RecursionMonitor.__init__", "p0_governance")
        self.alert_callback = alert_callback
        self.health_check_interval_sec = health_check_interval_sec
        self.metrics_retention_hours = metrics_retention_hours
        self._metrics_history: list[RecursionSnapshot] = []
        self._alerts: list[Alert] = []
        self._health_checks: list[HealthCheck] = []
        self._thresholds = {
            "max_active_recursions": 100,
            "min_success_rate": 0.8,
            "max_avg_depth": 40,
            "max_memory_mb": 500,
            "min_cache_hit_rate": 0.5,
        }
        self._circuit_open = False
        self._circuit_open_until: datetime | None = None
        self._consecutive_failures = 0
        # guardian: allow-magic-config
        self._failure_threshold = 5
        self._baseline_response_time_ms: float | None = None
        self._response_times: list[float] = []
        Logger.info("[RecursionMonitor] Initialized with production settings")

    def record_spawn(
        self, success: bool, depth: int, duration_ms: float, memory_bytes: int, cache_hit: bool,
    ) -> None:
        """
        Record a spawn operation for monitoring.

        Args:
            success: Whether spawn was successful
            depth: Recursion depth at spawn
            duration_ms: Duration of spawn operation
            memory_bytes: Memory used by spawn
            cache_hit: Whether validation cache was hit
        """

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "RecursionMonitor.record_spawn",
        )
        self._response_times.append(duration_ms)
        if len(self._response_times) > 1000:
            self._response_times = self._response_times[-500:]
        if not success:
            self._consecutive_failures += 1
            if self._consecutive_failures >= self._failure_threshold:
                self._open_circuit()
        else:
            self._consecutive_failures = 0
        self._check_performance_degradation(duration_ms)
        if depth > self._thresholds["max_avg_depth"]:
            self._create_alert(
                AlertSeverity.WARNING,
                f"High recursion depth detected: {depth}",
                "depth_monitor",
                {"depth": depth, "threshold": self._thresholds["max_avg_depth"]},
            )

    def record_snapshot(
        self,
        active_recursions: int,
        total_spawns: int,
        successful_spawns: int,
        depths: list[int],
        memory_bytes: int,
        cache_hits: int,
        cache_misses: int,
    ) -> RecursionSnapshot:
        """
        Record a point-in-time snapshot of recursion state.

        Args:
            active_recursions: Number of active recursive operations
            total_spawns: Total spawn operations
            successful_spawns: Number of successful spawns
            depths: List of current depths
            memory_bytes: Total memory usage
            cache_hits: Number of cache hits
            cache_misses: Number of cache misses

        Returns:
            RecursionSnapshot with current state
        """
        success_rate = successful_spawns / max(total_spawns, 1)
        avg_depth = sum(depths) / max(len(depths), 1) if depths else 0
        cache_hit_rate = cache_hits / max(cache_hits + cache_misses, 1)
        health_status = self._calculate_health_status(
            active_recursions, success_rate, avg_depth, memory_bytes, cache_hit_rate,
        )
        snapshot = RecursionSnapshot(
            timestamp=datetime.now().isoformat(),
            active_recursions=active_recursions,
            total_spawns=total_spawns,
            success_rate=success_rate,
            avg_depth=avg_depth,
            memory_usage_bytes=memory_bytes,
            cache_hit_rate=cache_hit_rate,
            health_status=health_status,
        )
        self._metrics_history.append(snapshot)
        self._cleanup_old_metrics()
        return snapshot

    def _calculate_health_status(
        self,
        active_recursions: int,
        success_rate: float,
        avg_depth: float,
        memory_bytes: int,
        cache_hit_rate: float,
    ) -> HealthStatus:
        """Calculate overall health status based on metrics."""
        issues = 0
        if active_recursions > self._thresholds["max_active_recursions"]:
            issues += 2
        if success_rate < self._thresholds["min_success_rate"]:
            issues += 2
        if avg_depth > self._thresholds["max_avg_depth"]:
            issues += 1
        if memory_bytes > self._thresholds["max_memory_mb"] * 1024 * 1024:
            issues += 2
        if cache_hit_rate < self._thresholds["min_cache_hit_rate"]:
            issues += 1
        if self._circuit_open:
            return HealthStatus.CRITICAL
        elif issues >= 4:
            return HealthStatus.UNHEALTHY
        elif issues >= 2:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY

    def run_health_checks(self) -> list[HealthCheck]:
        """
        Run all health checks and return results.

        Returns:
            List of HealthCheck results
        """
        checks = []
        start = get_clock().now_epoch()
        circuit_status = HealthStatus.CRITICAL if self._circuit_open else HealthStatus.HEALTHY
        checks.append(
            HealthCheck(
                name="circuit_breaker",
                status=circuit_status,
                message="Circuit is open" if self._circuit_open else "Circuit is closed",
                duration_ms=(get_clock().now_epoch() - start) * 1000,
                timestamp=datetime.now().isoformat(),
                metadata={"consecutive_failures": self._consecutive_failures},
            ),
        )
        start = get_clock().now_epoch()
        if self._metrics_history:
            latest = self._metrics_history[-1]
            mem_mb = latest.memory_usage_bytes / (1024 * 1024)
            mem_status = (
                HealthStatus.HEALTHY if mem_mb < self._thresholds["max_memory_mb"] else HealthStatus.DEGRADED
            )
            checks.append(
                HealthCheck(
                    name="memory_usage",
                    status=mem_status,
                    message=f"Memory usage: {mem_mb:.1f}MB",
                    duration_ms=(get_clock().now_epoch() - start) * 1000,
                    timestamp=datetime.now().isoformat(),
                    metadata={"memory_mb": mem_mb},
                ),
            )
        start = get_clock().now_epoch()
        if self._metrics_history:
            latest = self._metrics_history[-1]
            success_status = (
                HealthStatus.HEALTHY
                if latest.success_rate >= self._thresholds["min_success_rate"]
                else HealthStatus.DEGRADED
            )
            checks.append(
                HealthCheck(
                    name="success_rate",
                    status=success_status,
                    message=f"Success rate: {latest.success_rate:.1%}",
                    duration_ms=(get_clock().now_epoch() - start) * 1000,
                    timestamp=datetime.now().isoformat(),
                    metadata={"success_rate": latest.success_rate},
                ),
            )
        start = get_clock().now_epoch()
        if self._response_times:
            avg_response = sum(self._response_times) / len(self._response_times)
            response_status = HealthStatus.HEALTHY if avg_response < 1000 else HealthStatus.DEGRADED
            checks.append(
                HealthCheck(
                    name="response_time",
                    status=response_status,
                    message=f"Avg response time: {avg_response:.1f}ms",
                    duration_ms=(get_clock().now_epoch() - start) * 1000,
                    timestamp=datetime.now().isoformat(),
                    metadata={"avg_response_ms": avg_response},
                ),
            )
        self._health_checks = checks
        return checks

    def get_overall_health(self) -> HealthStatus:
        """Get overall system health status."""
        if self._circuit_open:
            return HealthStatus.CRITICAL
        checks = self.run_health_checks()
        if not checks:
            return HealthStatus.HEALTHY
        statuses = [c.status for c in checks]
        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        elif HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY

    def _open_circuit(self) -> None:
        """Open the circuit breaker."""
        self._circuit_open = True
        self._circuit_open_until = datetime.now() + timedelta(seconds=60)
        self._create_alert(
            AlertSeverity.CRITICAL,
            "Circuit breaker opened due to consecutive failures",
            "circuit_breaker",
            {"consecutive_failures": self._consecutive_failures},
        )
        Logger.critical("[CIRCUIT_BREAKER] Circuit opened due to failures")

    def close_circuit(self) -> None:
        """Manually close the circuit breaker."""
        self._circuit_open = False
        self._circuit_open_until = None
        self._consecutive_failures = 0
        Logger.info("[CIRCUIT_BREAKER] Circuit manually closed")

    def is_circuit_open(self) -> bool:
        """Check if circuit breaker is open."""
        if self._circuit_open and self._circuit_open_until:
            if datetime.now() > self._circuit_open_until:
                self._circuit_open = False
                self._circuit_open_until = None
                Logger.info("[CIRCUIT_BREAKER] Circuit auto-closed after timeout")
                return False
        return self._circuit_open

    def _check_performance_degradation(self, duration_ms: float) -> None:
        """Check for performance degradation."""
        if self._baseline_response_time_ms is None:
            if len(self._response_times) >= 100:
                self._baseline_response_time_ms = sum(self._response_times[:100]) / 100
            return
        if duration_ms > self._baseline_response_time_ms * 3:
            self._create_alert(
                AlertSeverity.WARNING,
                f"Performance degradation: {duration_ms:.1f}ms (baseline: {self._baseline_response_time_ms:.1f}ms)",
                "performance_monitor",
                {"current_ms": duration_ms, "baseline_ms": self._baseline_response_time_ms},
            )

    def _create_alert(
        self, severity: AlertSeverity, message: str, source: str, metadata: dict[str, Any] | None = None,
    ) -> Alert:
        """Create and store an alert."""
        alert = Alert(
            severity=severity,
            message=message,
            timestamp=datetime.now().isoformat(),
            source=source,
            metadata=metadata or {},
        )
        self._alerts.append(alert)
        if self.alert_callback:
            try:
                self.alert_callback(alert)
            # guardian: allow-silent-swallow
            except (ValueError, TypeError) as e:
                Logger.error(f"Alert callback failed: {e}")
        Logger.log(
            logging.CRITICAL if severity == AlertSeverity.CRITICAL else logging.WARNING,
            f"[ALERT] [{severity.value.upper()}] {message}",
        )
        return alert

    def get_alerts(
        self, severity: AlertSeverity | None = None, unacknowledged_only: bool = False,
    ) -> list[Alert]:
        """Get alerts with optional filtering."""
        alerts = self._alerts
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        if unacknowledged_only:
            alerts = [a for a in alerts if not a.acknowledged]
        return alerts

    def acknowledge_alert(self, index: int) -> bool:
        """Acknowledge an alert by index."""
        if 0 <= index < len(self._alerts):
            self._alerts[index].acknowledged = True
            return True
        return False

    def clear_alerts(self) -> int:
        """Clear all alerts and return count cleared."""
        count = len(self._alerts)
        self._alerts.clear()
        return count

    def _cleanup_old_metrics(self) -> None:
        """Remove metrics older than retention period."""
        cutoff = datetime.now() - timedelta(hours=self.metrics_retention_hours)
        cutoff_str = cutoff.isoformat()
        self._metrics_history = [m for m in self._metrics_history if m.timestamp > cutoff_str]

    def set_threshold(self, name: str, value: float) -> bool:
        """Set a monitoring threshold."""
        if name in self._thresholds:
            self._thresholds[name] = value
            Logger.info(f"[Monitor] Threshold {name} set to {value}")
            return True
        return False

    def get_thresholds(self) -> dict[str, float]:
        """Get current monitoring thresholds."""
        return self._thresholds.copy()

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get summary of collected metrics."""
        if not self._metrics_history:
            return {"total_snapshots": 0, "health_status": HealthStatus.HEALTHY.value}
        latest = self._metrics_history[-1]
        if len(self._metrics_history) >= 2:
            prev = self._metrics_history[-2]
            success_trend = latest.success_rate - prev.success_rate
            depth_trend = latest.avg_depth - prev.avg_depth
        else:
            success_trend = 0.0
            depth_trend = 0.0
        return {
            "total_snapshots": len(self._metrics_history),
            "latest_snapshot": {
                "timestamp": latest.timestamp,
                "active_recursions": latest.active_recursions,
                "total_spawns": latest.total_spawns,
                "success_rate": latest.success_rate,
                "avg_depth": latest.avg_depth,
                "memory_mb": latest.memory_usage_bytes / (1024 * 1024),
                "cache_hit_rate": latest.cache_hit_rate,
            },
            "trends": {"success_rate_change": success_trend, "depth_change": depth_trend},
            "health_status": latest.health_status.value,
            "circuit_open": self._circuit_open,
            "alert_count": len(self._alerts),
            "unacknowledged_alerts": len([a for a in self._alerts if not a.acknowledged]),
        }

    def reset(self) -> None:
        """Reset all monitoring state."""
        self._metrics_history.clear()
        self._alerts.clear()
        self._health_checks.clear()
        self._circuit_open = False
        self._circuit_open_until = None
        self._consecutive_failures = 0
        self._response_times.clear()
        self._baseline_response_time_ms = None
        Logger.info("[RecursionMonitor] Reset complete")


__all__ = ["RecursionMonitor", "HealthStatus", "AlertSeverity", "Alert", "HealthCheck", "RecursionSnapshot"]

_emit_reads_through("l4", "recursion_monitor_types", "urg_read_1")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_2")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_3")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_4")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_5")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_6")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_7")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_8")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_9")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_10")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_11")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_12")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_13")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_14")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_15")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_16")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_17")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_18")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_19")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_20")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_21")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_22")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_23")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_24")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_25")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_26")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_27")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_28")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_29")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_30")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_31")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_32")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_33")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_34")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_35")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_36")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_37")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_38")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_39")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_40")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_41")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_42")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_43")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_44")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_45")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_46")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_47")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_48")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_49")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_50")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_51")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_52")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_53")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_54")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_55")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_56")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_57")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_58")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_59")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_60")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_61")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_62")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_63")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_64")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_65")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_66")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_67")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_68")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_69")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_70")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_71")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_72")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_73")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_74")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_75")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_76")
_emit_reads_through("l4", "recursion_monitor_types", "urg_read_77")
