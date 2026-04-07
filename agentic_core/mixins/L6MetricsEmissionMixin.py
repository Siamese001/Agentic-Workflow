"""L6 Metrics Emission Mixin — Wave 5: Metric emission verification.

Provides standardized metric emission for all architectural layers (L0-L6).
Ensures Prometheus metrics are emitted from key ingress points.

Usage:
    class MyAgent(L6MetricsEmissionMixin, SovereignBaseAgent):
        def route_request(self, request):
            self.emit_routing_metric("routing_requests_total", 1)
            # ... routing logic
"""

from __future__ import annotations

from typing import Any

# Deferred imports for graceful degradation
try:
    from agentic_core.L6_observability.utils.metrics.prometheus_metrics import (
        AGENT_EXECUTION_DURATION_SECONDS,
        AGENTIC_REGISTRY,
        CIRCUIT_BREAKER_STATE,
        EVALUATION_METRICS_GAUGE,
        HEALING_DURATION_SECONDS,
        HUMAN_ESCALATIONS_TOTAL,
        L0_ROUTING_REQUESTS_TOTAL,
        L1_REASONING_REQUESTS_TOTAL,
        L2_EXECUTION_REQUESTS_TOTAL,
        L3_ORCHESTRATION_REQUESTS_TOTAL,
        L4_STATE_REQUESTS_TOTAL,
        L5_SAFETY_REQUESTS_TOTAL,
        L6_OBSERVABILITY_REQUESTS_TOTAL,
        POLICY_VIOLATIONS_TOTAL,
        RETRY_ATTEMPTS_TOTAL,
        SNAPSHOT_PERSISTENCE_DURATION_SECONDS,
        TOOL_INVOCATION_DURATION_SECONDS,
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    AGENTIC_REGISTRY = None  # type: ignore[misc, assignment]


class L6MetricsEmissionMixin:
    """Mixin providing standardized metric emission for all layers.

    Wave 5: Metric emission verification
    - Provides emit_* methods for each layer
    - Graceful degradation when Prometheus unavailable
    - Tracks key ingress points across L0-L6

    Attributes:
        _metrics_layer: Layer identifier (L0-L6)
        _metrics_enabled: Whether metrics are enabled
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize mixin."""
        super().__init__(*args, **kwargs)
        self._metrics_layer: str = getattr(self, "layer", "L0")
        self._metrics_enabled: bool = PROMETHEUS_AVAILABLE

    def emit_routing_metric(self, metric_name: str, value: float = 1.0, **labels: Any) -> None:
        """Emit L0 routing metric.

        Args:
            metric_name: Name of the metric
            value: Metric value
            **labels: Additional labels
        """
        if not self._metrics_enabled:
            return

        try:
            if metric_name == "routing_requests_total":
                L0_ROUTING_REQUESTS_TOTAL.labels(
                    layer="L0",
                    component=labels.get("component", "unknown"),
                    status=labels.get("status", "success"),
                ).inc(value)
        except Exception as e:

            import logging; logging.getLogger(__name__).debug("L6MetricsEmissionMixin: Exception swallowed at L81: %s", e)

    def emit_reasoning_metric(self, metric_name: str, value: float = 1.0, **labels: Any) -> None:
        """Emit L1 reasoning metric.

        Args:
            metric_name: Name of the metric
            value: Metric value
            **labels: Additional labels
        """
        if not self._metrics_enabled:
            return

        try:
            if metric_name == "reasoning_requests_total":
                L1_REASONING_REQUESTS_TOTAL.labels(
                    layer="L1",
                    component=labels.get("component", "unknown"),
                    status=labels.get("status", "success"),
                ).inc(value)
        except Exception as e:

            import logging; logging.getLogger(__name__).debug("L6MetricsEmissionMixin: Exception swallowed at L102: %s", e)

    def emit_execution_metric(self, metric_name: str, value: float = 1.0, **labels: Any) -> None:
        """Emit L2 execution metric.

        Args:
            metric_name: Name of the metric
            value: Metric value
            **labels: Additional labels
        """
        if not self._metrics_enabled:
            return

        try:
            if metric_name == "execution_requests_total":
                L2_EXECUTION_REQUESTS_TOTAL.labels(
                    layer="L2",
                    component=labels.get("component", "unknown"),
                    status=labels.get("status", "success"),
                ).inc(value)
        except Exception as e:

            import logging; logging.getLogger(__name__).debug("L6MetricsEmissionMixin: Exception swallowed at L123: %s", e)

    def emit_orchestration_metric(self, metric_name: str, value: float = 1.0, **labels: Any) -> None:
        """Emit L3 orchestration metric.

        Args:
            metric_name: Name of the metric
            value: Metric value
            **labels: Additional labels
        """
        if not self._metrics_enabled:
            return

        try:
            if metric_name == "orchestration_requests_total":
                L3_ORCHESTRATION_REQUESTS_TOTAL.labels(
                    layer="L3",
                    component=labels.get("component", "unknown"),
                    status=labels.get("status", "success"),
                ).inc(value)
        except Exception:
            pass  # guardian: allow-silent-swallow -- metrics emission is fire-and-forget; failure must not crash caller

    def emit_state_metric(self, metric_name: str, value: float = 1.0, **labels: Any) -> None:
        """Emit L4 state metric.

        Args:
            metric_name: Name of the metric
            value: Metric value
            **labels: Additional labels
        """
        if not self._metrics_enabled:
            return

        try:
            if metric_name == "state_requests_total":
                L4_STATE_REQUESTS_TOTAL.labels(
                    layer="L4",
                    component=labels.get("component", "unknown"),
                    status=labels.get("status", "success"),
                ).inc(value)
        except Exception:
            pass  # guardian: allow-silent-swallow -- metrics emission is fire-and-forget; failure must not crash caller

    def emit_safety_metric(self, metric_name: str, value: float = 1.0, **labels: Any) -> None:
        """Emit L5 safety metric.

        Args:
            metric_name: Name of the metric
            value: Metric value
            **labels: Additional labels
        """
        if not self._metrics_enabled:
            return

        try:
            if metric_name == "safety_requests_total":
                L5_SAFETY_REQUESTS_TOTAL.labels(
                    layer="L5",
                    component=labels.get("component", "unknown"),
                    status=labels.get("status", "success"),
                ).inc(value)
        except Exception:
            pass  # guardian: allow-silent-swallow -- metrics emission is fire-and-forget; failure must not crash caller

    def emit_observability_metric(self, metric_name: str, value: float = 1.0, **labels: Any) -> None:
        """Emit L6 observability metric.

        Args:
            metric_name: Name of the metric
            value: Metric value
            **labels: Additional labels
        """
        if not self._metrics_enabled:
            return

        try:
            if metric_name == "observability_requests_total":
                L6_OBSERVABILITY_REQUESTS_TOTAL.labels(
                    layer="L6",
                    component=labels.get("component", "unknown"),
                    status=labels.get("status", "success"),
                ).inc(value)
        except Exception:
            pass  # guardian: allow-silent-swallow -- metrics emission is fire-and-forget; failure must not crash caller

    def emit_tool_invocation_duration(self, duration: float, **labels: Any) -> None:
        """Emit tool invocation duration metric.

        Args:
            duration: Duration in seconds
            **labels: Additional labels
        """
        if not self._metrics_enabled:
            return

        try:
            TOOL_INVOCATION_DURATION_SECONDS.labels(
                layer=labels.get("layer", "L2"),
                component=labels.get("component", "unknown"),
                tool_name=labels.get("tool_name", "unknown"),
            ).observe(duration)
        except Exception:
            pass  # guardian: allow-silent-swallow -- metrics emission is fire-and-forget; failure must not crash caller

    def emit_healing_duration(self, duration: float, **labels: Any) -> None:
        """Emit healing duration metric.

        Args:
            duration: Duration in seconds
            **labels: Additional labels
        """
        if not self._metrics_enabled:
            return

        try:
            HEALING_DURATION_SECONDS.labels(
                layer=labels.get("layer", "L3"),
                component=labels.get("component", "unknown"),
                healing_type=labels.get("healing_type", "unknown"),
            ).observe(duration)
        except Exception:
            pass  # guardian: allow-silent-swallow -- metrics emission is fire-and-forget; failure must not crash caller

    def emit_policy_violation(self, violation_type: str, **labels: Any) -> None:
        """Emit policy violation metric.

        Args:
            violation_type: Type of violation
            **labels: Additional labels
        """
        if not self._metrics_enabled:
            return

        try:
            POLICY_VIOLATIONS_TOTAL.labels(
                layer=labels.get("layer", "L5"),
                component=labels.get("component", "unknown"),
                violation_type=violation_type,
            ).inc(1)
        except Exception:
            pass  # guardian: allow-silent-swallow -- metrics emission is fire-and-forget; failure must not crash caller

    def emit_human_escalation(self, escalation_reason: str, **labels: Any) -> None:
        """Emit human escalation metric.

        Args:
            escalation_reason: Reason for escalation
            **labels: Additional labels
        """
        if not self._metrics_enabled:
            return

        try:
            HUMAN_ESCALATIONS_TOTAL.labels(
                layer=labels.get("layer", "L5"),
                component=labels.get("component", "unknown"),
                escalation_reason=escalation_reason,
            ).inc(1)
        except Exception:
            pass  # guardian: allow-silent-swallow -- metrics emission is fire-and-forget; failure must not crash caller

    def emit_circuit_breaker_state(self, state: str, **labels: Any) -> None:
        """Emit circuit breaker state metric.

        Args:
            state: Circuit breaker state (CLOSED, OPEN, HALF_OPEN)
            **labels: Additional labels
        """
        if not self._metrics_enabled:
            return

        try:
            CIRCUIT_BREAKER_STATE.labels(
                layer=labels.get("layer", "L2"),
                component=labels.get("component", "unknown"),
                state=state,
            ).set(1 if state == "CLOSED" else 0)
        except Exception:
            pass  # guardian: allow-silent-swallow -- metrics emission is fire-and-forget; failure must not crash caller

    def emit_retry_attempt(self, **labels: Any) -> None:
        """Emit retry attempt metric.

        Args:
            **labels: Additional labels
        """
        if not self._metrics_enabled:
            return

        try:
            RETRY_ATTEMPTS_TOTAL.labels(
                layer=labels.get("layer", "L2"),
                component=labels.get("component", "unknown"),
                retry_type=labels.get("retry_type", "unknown"),
            ).inc(1)
        except Exception:
            pass  # guardian: allow-silent-swallow -- metrics emission is fire-and-forget; failure must not crash caller

    def emit_snapshot_persistence_duration(self, duration: float, **labels: Any) -> None:
        """Emit snapshot persistence duration metric.

        Args:
            duration: Duration in seconds
            **labels: Additional labels
        """
        if not self._metrics_enabled:
            return

        try:
            SNAPSHOT_PERSISTENCE_DURATION_SECONDS.labels(
                layer=labels.get("layer", "L4"),
                component=labels.get("component", "unknown"),
                persistence_type=labels.get("persistence_type", "local"),
            ).observe(duration)
        except Exception:
            pass  # guardian: allow-silent-swallow -- metrics emission is fire-and-forget; failure must not crash caller

    def get_metrics_status(self) -> dict[str, Any]:
        """Get current metrics emission status.

        Returns:
            Dictionary with status information
        """
        return {
            "metrics_enabled": self._metrics_enabled,
            "prometheus_available": PROMETHEUS_AVAILABLE,
            "layer": self._metrics_layer,
        }
