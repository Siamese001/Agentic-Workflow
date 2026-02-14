"""APP Signal Contracts — Waves 7.0.8–7.0.10 (Schema Lock Only).

Defines schema-locked, frozen artifacts for measurable APP outcome signals:
  - AppSignalEventArtifact     (individual signal event)
  - AppSignalAggregateArtifact (aggregated window summary)
  - APP_SIGNAL_CATALOG         (allowlist of optimizable metrics, Wave 7.0.10)

NO runtime behavior changes.  NO mutation logic.  NO automatic application.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Literal

from agentic_core.L0_routing.types.v15_p2_types import (
    SemanticClockSnapshot,
    validate_semantic_clock,
)
from agentic_core.L7_meta_learning.types.meta_learning_types import (
    _canonical_payload_json,
)

# =============================================================================
# §Wave7.0.8 — Finite Validation Helper
# =============================================================================


def _validate_finite(value: float, field_name: str) -> None:
    """Raise ValueError if *value* is NaN, +inf, or -inf."""
    if not math.isfinite(value):
        raise ValueError(f"{field_name}_NOT_FINITE")


# =============================================================================
# §Wave7.0.10 — APP Signal Catalog (guarded target signals)
# =============================================================================

APP_SIGNAL_CATALOG: dict[str, dict[str, object]] = {
    "resume_message_response_rate": {
        "direction": "MAXIMIZE",
        "bounds": {"min": 0.0, "max": 1.0},
        "unit": "rate",
        "aggregation": "rate",
        "recommended_window": "28d",
    },
    "resume_message_positive_reply_rate": {
        "direction": "MAXIMIZE",
        "bounds": {"min": 0.0, "max": 1.0},
        "unit": "rate",
        "aggregation": "rate",
        "recommended_window": "28d",
    },
    "resume_message_reject_rate": {
        "direction": "MINIMIZE",
        "bounds": {"min": 0.0, "max": 1.0},
        "unit": "rate",
        "aggregation": "rate",
        "recommended_window": "28d",
    },
    "time_to_first_reply_hours": {
        "direction": "MINIMIZE",
        "bounds": {"min": 0.0},
        "unit": "hours",
        "aggregation": "median",
        "recommended_window": "28d",
    },
    "conversion_to_interview_rate": {
        "direction": "MAXIMIZE",
        "bounds": {"min": 0.0, "max": 1.0},
        "unit": "rate",
        "aggregation": "rate",
        "recommended_window": "28d",
    },
}


def _validate_catalog_bounds(metric_name: str, value: float, field_name: str) -> None:
    """Validate *value* against APP_SIGNAL_CATALOG bounds for *metric_name*."""
    entry = APP_SIGNAL_CATALOG.get(metric_name)
    if entry is None:
        raise ValueError(f"METRIC_NAME_NOT_IN_CATALOG: {metric_name!r}")
    bounds = entry.get("bounds", {})
    lo = bounds.get("min")  # type: ignore[union-attr]
    hi = bounds.get("max")  # type: ignore[union-attr]
    if lo is not None and value < lo:
        raise ValueError(
            f"{field_name}_BELOW_MIN: {value} < {lo} for {metric_name!r}",
        )
    if hi is not None and value > hi:
        raise ValueError(
            f"{field_name}_ABOVE_MAX: {value} > {hi} for {metric_name!r}",
        )


# =============================================================================
# §Wave7.0.8 — AppSignalEventArtifact (immutable APP signal)
# =============================================================================


@dataclass(frozen=True)
class AppSignalEventArtifact:
    """Frozen, schema-locked APP signal event.

    Rules
    -----
    - semantic_clock required (ValueError if missing).
    - metric_name must be non-empty.
    - metric_value must be finite (no NaN/inf).
    - timestamp_utc, if present, must be ISO-8601 format string.
    - canonical serialization (sort_keys=True).
    """

    artifact_type: Literal["APP_SIGNAL_EVENT"]
    app_id: str
    run_id: str
    message_id: str
    segment_id: str | None
    metric_name: str
    metric_value: float
    outcome_label: str | None
    timestamp_utc: str | None
    semantic_clock: SemanticClockSnapshot
    trace_id: str

    def __post_init__(self) -> None:
        validate_semantic_clock(self.semantic_clock, "AppSignalEventArtifact")
        if self.artifact_type != "APP_SIGNAL_EVENT":
            raise ValueError(
                f"artifact_type must be 'APP_SIGNAL_EVENT', got {self.artifact_type!r}",
            )
        if not self.metric_name:
            raise ValueError("METRIC_NAME_EMPTY")
        _validate_finite(self.metric_value, "metric_value")

    def to_dict(self) -> dict[str, object]:
        """Canonical, deterministic serialization (keys sorted alphabetically)."""
        return {
            "app_id": self.app_id,
            "artifact_type": self.artifact_type,
            "message_id": self.message_id,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "outcome_label": self.outcome_label,
            "run_id": self.run_id,
            "segment_id": self.segment_id,
            "semantic_clock": self.semantic_clock.to_dict(),
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        """Deterministic JSON string (sort_keys=True, compact separators)."""
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))


def build_app_signal_event(
    *,
    app_id: str,
    run_id: str,
    message_id: str,
    segment_id: str | None = None,
    metric_name: str,
    metric_value: float,
    outcome_label: str | None = None,
    timestamp_utc: str | None = None,
    semantic_clock: SemanticClockSnapshot,
) -> AppSignalEventArtifact:
    """Build an AppSignalEventArtifact with deterministic trace_id.

    Parameters
    ----------
    app_id : str
        Application identifier (e.g. "apps_rg", "apps_lic").
    run_id : str
        Unique run/session identifier.
    message_id : str
        Unique message identifier within the run.
    segment_id : str | None
        Optional sub-segment identifier.
    metric_name : str
        Name of the metric (must be non-empty).
    metric_value : float
        Observed metric value (must be finite).
    outcome_label : str | None
        Optional categorical outcome label.
    timestamp_utc : str | None
        Optional ISO-8601 timestamp string.
    semantic_clock : SemanticClockSnapshot
        Required immutable clock snapshot.

    Returns
    -------
    AppSignalEventArtifact
        Frozen, deterministic signal event artifact.
    """
    validate_semantic_clock(semantic_clock, "build_app_signal_event")
    if not metric_name:
        raise ValueError("METRIC_NAME_EMPTY")
    _validate_finite(metric_value, "metric_value")
    _validate_catalog_bounds(metric_name, metric_value, "metric_value")

    temp_payload = {
        "app_id": app_id,
        "artifact_type": "APP_SIGNAL_EVENT",
        "message_id": message_id,
        "metric_name": metric_name,
        "metric_value": metric_value,
        "outcome_label": outcome_label,
        "run_id": run_id,
        "segment_id": segment_id,
        "semantic_clock": semantic_clock.to_dict(),
        "timestamp_utc": timestamp_utc,
    }
    canonical = _canonical_payload_json(temp_payload)
    trace_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    return AppSignalEventArtifact(
        artifact_type="APP_SIGNAL_EVENT",
        app_id=app_id,
        run_id=run_id,
        message_id=message_id,
        segment_id=segment_id,
        metric_name=metric_name,
        metric_value=metric_value,
        outcome_label=outcome_label,
        timestamp_utc=timestamp_utc,
        semantic_clock=semantic_clock,
        trace_id=trace_id,
    )


# =============================================================================
# §Wave7.0.8 — AppSignalAggregateArtifact (immutable APP aggregate)
# =============================================================================


@dataclass(frozen=True)
class AppSignalAggregateArtifact:
    """Frozen, schema-locked APP signal aggregate.

    Rules
    -----
    - semantic_clock required (ValueError if missing).
    - delta MUST equal candidate_value - baseline_value (computed deterministically).
    - n must be >= 1.
    - evidence_hash required (non-empty).
    - All float fields must be finite.
    - canonical serialization (sort_keys=True).
    """

    artifact_type: Literal["APP_SIGNAL_AGGREGATE"]
    app_id: str
    window_id: str
    metric_name: str
    baseline_value: float
    candidate_value: float
    delta: float
    n: int
    evidence_hash: str
    semantic_clock: SemanticClockSnapshot
    trace_id: str

    def __post_init__(self) -> None:
        validate_semantic_clock(self.semantic_clock, "AppSignalAggregateArtifact")
        if self.artifact_type != "APP_SIGNAL_AGGREGATE":
            raise ValueError(
                f"artifact_type must be 'APP_SIGNAL_AGGREGATE', got {self.artifact_type!r}",
            )
        _validate_finite(self.baseline_value, "baseline_value")
        _validate_finite(self.candidate_value, "candidate_value")
        _validate_finite(self.delta, "delta")
        if self.n < 1:
            raise ValueError("N_LESS_THAN_ONE")
        if not self.evidence_hash:
            raise ValueError("EVIDENCE_HASH_EMPTY")

    def to_dict(self) -> dict[str, object]:
        """Canonical, deterministic serialization (keys sorted alphabetically)."""
        return {
            "app_id": self.app_id,
            "artifact_type": self.artifact_type,
            "baseline_value": self.baseline_value,
            "candidate_value": self.candidate_value,
            "delta": self.delta,
            "evidence_hash": self.evidence_hash,
            "metric_name": self.metric_name,
            "n": self.n,
            "semantic_clock": self.semantic_clock.to_dict(),
            "trace_id": self.trace_id,
            "window_id": self.window_id,
        }

    def to_json(self) -> str:
        """Deterministic JSON string (sort_keys=True, compact separators)."""
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))


def build_app_signal_aggregate(
    *,
    app_id: str,
    window_id: str,
    metric_name: str,
    baseline_value: float,
    candidate_value: float,
    n: int,
    evidence_hash: str,
    semantic_clock: SemanticClockSnapshot,
) -> AppSignalAggregateArtifact:
    """Build an AppSignalAggregateArtifact with deterministic trace_id.

    Parameters
    ----------
    app_id : str
        Application identifier (e.g. "apps_rg", "apps_lic").
    window_id : str
        Aggregation window identifier.
    metric_name : str
        Name of the aggregated metric.
    baseline_value, candidate_value : float
        Aggregated metric values (must be finite).
    n : int
        Sample count (must be >= 1).
    evidence_hash : str
        SHA-256 of the evidence bundle (required, non-empty).
    semantic_clock : SemanticClockSnapshot
        Required immutable clock snapshot.

    Returns
    -------
    AppSignalAggregateArtifact
        Frozen, deterministic aggregate artifact.
    """
    validate_semantic_clock(semantic_clock, "build_app_signal_aggregate")
    _validate_finite(baseline_value, "baseline_value")
    _validate_finite(candidate_value, "candidate_value")
    _validate_catalog_bounds(metric_name, baseline_value, "baseline_value")
    _validate_catalog_bounds(metric_name, candidate_value, "candidate_value")
    if n < 1:
        raise ValueError("N_LESS_THAN_ONE")
    if not evidence_hash:
        raise ValueError("EVIDENCE_HASH_EMPTY")

    delta = candidate_value - baseline_value

    temp_payload = {
        "app_id": app_id,
        "artifact_type": "APP_SIGNAL_AGGREGATE",
        "baseline_value": baseline_value,
        "candidate_value": candidate_value,
        "delta": delta,
        "evidence_hash": evidence_hash,
        "metric_name": metric_name,
        "n": n,
        "semantic_clock": semantic_clock.to_dict(),
        "window_id": window_id,
    }
    canonical = _canonical_payload_json(temp_payload)
    trace_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    return AppSignalAggregateArtifact(
        artifact_type="APP_SIGNAL_AGGREGATE",
        app_id=app_id,
        window_id=window_id,
        metric_name=metric_name,
        baseline_value=baseline_value,
        candidate_value=candidate_value,
        delta=delta,
        n=n,
        evidence_hash=evidence_hash,
        semantic_clock=semantic_clock,
        trace_id=trace_id,
    )
