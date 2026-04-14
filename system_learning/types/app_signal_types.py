"""APP Signal Contracts — Waves 7.0.8–7.0.11 (Schema Lock Only).

Defines schema-locked, frozen artifacts for measurable APP outcome signals:
  - AppSignalEventArtifact     (individual signal event)
  - AppSignalAggregateArtifact (aggregated window summary)
  - APP_SIGNAL_CATALOG         (allowlist of optimizable metrics, Wave 7.0.10)
  - aggregate_app_signals      (deterministic offline aggregator, Wave 7.0.11)

NO runtime behavior changes.  NO mutation logic.  NO automatic application.
"""

from __future__ import annotations

import json
import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Literal

from agentic_core.interfaces.determinism_types import (
    SemanticClockSnapshot,
    validate_semantic_clock,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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

_emit_authorize_and_execute("p2", "app_signal_types", "execution_auth")
_emit_validates_capability("p2", "app_signal_types", "capability_check")
_emit_routes_to_capability("p2", "app_signal_types", "capability_route")
_emit_writes_via_uwg("p2", "app_signal_types", "uwg_write")
_emit_blocks_direct_write("p2", "app_signal_types", "direct_write_block")
_emit_records_tool_invocation("p2", "app_signal_types", "tool_invocation")
_emit_captures_execution_output("p2", "app_signal_types", "exec_output")
_emit_dispatches_agent("p3", "app_signal_types", "agent_dispatch")
_emit_coordinates_agents("p3", "app_signal_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "app_signal_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "app_signal_types", "healing_outcome")
_emit_escalates_failure("p3", "app_signal_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "app_signal_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "app_signal_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "app_signal_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "app_signal_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "app_signal_types", "eval_metric")
_emit_stores_embedding("p4", "app_signal_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "app_signal_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "app_signal_types", "exec_snapshot_link")
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
from system_learning.enforcement.determinism import (
    deterministic_json,
    stable_sha256_json,
)
from system_learning.types.meta_learning_types import (
    _canonical_payload_json,
)

_emit_emits_metric_event("app_signal_types", "p4obs", "metric_1")
_emit_emits_metric_event("app_signal_types", "p4obs", "metric_2")
_emit_emits_metric_event("app_signal_types", "p4obs", "metric_3")
_emit_emits_metric_event("app_signal_types", "p4obs", "metric_4")
_emit_emits_metric_event("app_signal_types", "p4obs", "metric_5")
_emit_emits_metric_event("app_signal_types", "p4obs", "metric_6")
_emit_records_incident_event("app_signal_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("app_signal_types", "p4obs", "anomaly")
_emit_writes_observability_log("app_signal_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("app_signal_types", "p4obs", "mon_state")
_emit_triggers_alert("app_signal_types", "p4obs", "alert")
_emit_links_incident_trace("app_signal_types", "p4obs", "trace_link")
_emit_captures_pattern("app_signal_types", "p3lm", "pattern")
_emit_records_learning_event("app_signal_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("app_signal_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("app_signal_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("app_signal_types", "p3lm", "routing")
_emit_improves_agent_policy("app_signal_types", "p3lm", "policy")
_emit_stores_learning_state("app_signal_types", "p3lm", "state")
_emit_records_execution_trace("app_signal_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("app_signal_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("app_signal_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("app_signal_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("app_signal_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("app_signal_types", "env_read", "p2_env_1")
_emit_reads_environ("app_signal_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("app_signal_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("app_signal_types", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "app_signal_types")
_emit_applies_guardrail("p0", "app_signal_types", "p0_governance")
_emit_reads_policy_state("p0", "app_signal_types", "policy_binding")
_emit_snapshots_state("p0", "app_signal_types", "state_snapshot")
_emit_pulls_context("p1", "app_signal_types", "context_pull")
_emit_pulls_context("p1", "app_signal_types", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "app_signal_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "app_signal_types", "uwg_term_secondary")
_emit_writes_through("p1", "app_signal_types", "write_through")
_emit_writes_through("p1", "app_signal_types", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "app_signal_types", "safety_validation")
_emit_invokes_eval("p1", "app_signal_types", "eval_call")
_emit_proposal_commits_routing("p1", "app_signal_types", "routing_commit")
_emit_escalates_to_human("p1", "app_signal_types", "human_escalation")
_emit_routes_through("p1", "app_signal_types", "route_through")
_emit_checks_agent_registry("p1", "app_signal_types", "agent_registry")
_emit_validates_agent_capability("p1", "app_signal_types", "capability")
_emit_dispatches_execution_plan("p1", "app_signal_types", "exec_plan")
_emit_agent_executes_agent("p1", "app_signal_types", "sub_agent")
_emit_routes_to_agent("p1", "app_signal_types", "target_agent")
_emit_verifies_policy("p1", "app_signal_types", "policy_check")
_emit_observes_runtime_state("p1", "app_signal_types", "runtime_state")
_emit_verifies_boundary("p1", "app_signal_types", "boundary_check")
_emit_transcripts_response("p1", "app_signal_types", "transcript")
_emit_hard_fails_untranscripted("p1", "app_signal_types")
_emit_gated_by_confidence("p1", "app_signal_types", "confidence_gate")
emit_replay_key("p0", "app_signal_types")
emit_determinism_digest("p0", "app_signal_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
        return deterministic_json(self.to_dict())


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
    trace_id = stable_sha256_json(json.loads(canonical))

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
        return deterministic_json(self.to_dict())


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
    trace_id = stable_sha256_json(json.loads(canonical))

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


# =============================================================================
# §Wave7.0.11 — Deterministic Offline Aggregator
# =============================================================================


def _deterministic_mean(values: list[float]) -> float:
    """Deterministic mean: sum / len. Fail-closed on empty."""
    if not values:
        raise ValueError("EMPTY_VALUES_FOR_MEAN")
    return sum(sorted(values)) / len(values)


def _deterministic_median(values: list[float]) -> float:
    """Deterministic median: sorted list, middle element(s). Fail-closed on empty."""
    if not values:
        raise ValueError("EMPTY_VALUES_FOR_MEDIAN")
    s = sorted(values)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2.0


def aggregate_app_signals(
    *,
    app_id: str,
    window_id: str,
    metric_name: str,
    events: Sequence[AppSignalEventArtifact],
    baseline_selector: Callable[[AppSignalEventArtifact], bool],
    candidate_selector: Callable[[AppSignalEventArtifact], bool],
    evidence_hash: str,
    semantic_clock: SemanticClockSnapshot,
) -> AppSignalAggregateArtifact:
    """Deterministic offline aggregator: events -> AppSignalAggregateArtifact.

    Parameters
    ----------
    app_id : str
        Application identifier.
    window_id : str
        Aggregation window identifier.
    metric_name : str
        Must be in APP_SIGNAL_CATALOG.
    events : Sequence[AppSignalEventArtifact]
        Raw signal events to aggregate.
    baseline_selector : Callable
        Predicate selecting baseline events.
    candidate_selector : Callable
        Predicate selecting candidate events.
    evidence_hash : str
        SHA-256 of the evidence bundle.
    semantic_clock : SemanticClockSnapshot
        Required immutable clock snapshot.

    Returns
    -------
    AppSignalAggregateArtifact

    Raises
    ------
    ValueError
        If metric_name not in catalog, empty baseline/candidate, or non-finite values.
    """
    entry = APP_SIGNAL_CATALOG.get(metric_name)
    if entry is None:
        raise ValueError(f"METRIC_NAME_NOT_IN_CATALOG: {metric_name!r}")

    filtered = [e for e in events if e.metric_name == metric_name and e.app_id == app_id]

    baseline_vals: list[float] = []
    candidate_vals: list[float] = []
    for evt in filtered:
        _validate_finite(evt.metric_value, "event_metric_value")
        if baseline_selector(evt):
            baseline_vals.append(evt.metric_value)
        if candidate_selector(evt):
            candidate_vals.append(evt.metric_value)

    if not baseline_vals:
        raise ValueError("EMPTY_BASELINE")
    if not candidate_vals:
        raise ValueError("EMPTY_CANDIDATE")

    agg_method = str(entry.get("aggregation", "mean"))
    if agg_method in ("rate", "mean"):
        agg_fn = _deterministic_mean
    elif agg_method == "median":
        agg_fn = _deterministic_median
    else:
        raise ValueError(f"UNKNOWN_AGGREGATION: {agg_method!r}")

    baseline_value = agg_fn(baseline_vals)
    candidate_value = agg_fn(candidate_vals)
    n = len(baseline_vals) + len(candidate_vals)

    return build_app_signal_aggregate(
        app_id=app_id,
        window_id=window_id,
        metric_name=metric_name,
        baseline_value=baseline_value,
        candidate_value=candidate_value,
        n=n,
        evidence_hash=evidence_hash,
        semantic_clock=semantic_clock,
    )
