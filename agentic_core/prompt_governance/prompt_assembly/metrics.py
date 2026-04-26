"""PA Metrics Registry — 22 metric names from the spec (lines 1730-1751).

Each metric has a stable name, type, and description. The
:class:`PAMetricRegistry` exposes a counter / observation API; emission to
a real metrics sink is the caller's responsibility.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MetricType(str, Enum):
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"


@dataclass(frozen=True)
class MetricDefinition:
    name: str
    metric_type: MetricType
    description: str


PA_METRICS: tuple[MetricDefinition, ...] = (
    MetricDefinition("pa_assembly_started_total", MetricType.COUNTER, "PA pipeline starts"),
    MetricDefinition("pa_assembly_dispatched_total", MetricType.COUNTER, "Artifacts dispatched to L2"),
    MetricDefinition("pa_assembly_blocked_total", MetricType.COUNTER, "PA blocks emitted (any reason)"),
    MetricDefinition("pa_boundary_check_failures_total", MetricType.COUNTER, "PA.0 boundary check failures"),
    MetricDefinition("pa_bom_missing_slots_total", MetricType.COUNTER, "BOM resolution slot gaps"),
    MetricDefinition("pa_security_strip_total", MetricType.COUNTER, "C0 chunks STRIPPED"),
    MetricDefinition("pa_security_quarantine_total", MetricType.COUNTER, "C0 chunks QUARANTINED"),
    MetricDefinition("pa_security_reject_total", MetricType.COUNTER, "C0 chunks REJECTED"),
    MetricDefinition("pa_u0_injection_score", MetricType.HISTOGRAM, "U0 injection score distribution"),
    MetricDefinition("pa_h0_reentry_rejected_total", MetricType.COUNTER, "H0 healer hints rejected"),
    MetricDefinition("pa_validation_failures_total", MetricType.COUNTER, "PA.4 check failures"),
    MetricDefinition("pa_authority_violations_total", MetricType.COUNTER, "Authority-stack violations"),
    MetricDefinition("pa_budget_overflow_total", MetricType.COUNTER, "PA.5 overflow events"),
    MetricDefinition("pa_budget_input_tokens", MetricType.HISTOGRAM, "Final input token counts"),
    MetricDefinition("pa_budget_trim_actions_total", MetricType.COUNTER, "Trim actions executed"),
    MetricDefinition("pa_provider_render_total", MetricType.COUNTER, "Provider lane renders"),
    MetricDefinition("pa_signature_verification_total", MetricType.COUNTER, "Signature verifications"),
    MetricDefinition("pa_replay_mismatch_total", MetricType.COUNTER, "Replay-key mismatches"),
    MetricDefinition("pa_l2_handoff_violations_total", MetricType.COUNTER, "L2 handoff contract breaches"),
    MetricDefinition("pa_invariant_violations_total", MetricType.COUNTER, "PA invariants tripped"),
    MetricDefinition("pa_pipeline_latency_ms", MetricType.HISTOGRAM, "End-to-end PA pipeline latency"),
    MetricDefinition("pa_compiled_artifact_size_bytes", MetricType.HISTOGRAM, "Final artifact byte size"),
)


METRIC_NAMES: frozenset[str] = frozenset(m.name for m in PA_METRICS)


@dataclass
class PAMetricRegistry:
    """Lightweight in-memory metric collector for tests and the orchestrator."""

    counters: dict[str, int] = field(default_factory=dict)
    histograms: dict[str, list[float]] = field(default_factory=dict)
    gauges: dict[str, float] = field(default_factory=dict)

    def _validate(self, name: str, expected: MetricType) -> MetricDefinition:
        for m in PA_METRICS:
            if m.name == name:
                if m.metric_type is not expected:
                    raise ValueError(
                        "metric " + name + " is " + m.metric_type.value + ", not " + expected.value
                    )
                return m
        raise ValueError("unknown metric: " + name)

    def inc(self, name: str, amount: int = 1) -> None:
        self._validate(name, MetricType.COUNTER)
        self.counters[name] = self.counters.get(name, 0) + amount

    def observe(self, name: str, value: float) -> None:
        self._validate(name, MetricType.HISTOGRAM)
        self.histograms.setdefault(name, []).append(float(value))

    def set_gauge(self, name: str, value: float) -> None:
        self._validate(name, MetricType.GAUGE)
        self.gauges[name] = float(value)

    def snapshot(self) -> dict[str, Any]:
        return {
            "counters": dict(self.counters),
            "histograms": {k: list(v) for k, v in self.histograms.items()},
            "gauges": dict(self.gauges),
        }


__all__ = [
    "METRIC_NAMES",
    "MetricDefinition",
    "MetricType",
    "PA_METRICS",
    "PAMetricRegistry",
]
