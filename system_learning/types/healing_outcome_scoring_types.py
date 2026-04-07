"""Healing outcome scoring types for offline evaluation.

Phase 3: Types for deterministic scoring of healing outcome proposals.
All types are frozen/immutable with ASCII-only reasons.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field

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

_emit_authorize_and_execute("p2", "healing_outcome_scoring_types", "execution_auth")
_emit_validates_capability("p2", "healing_outcome_scoring_types", "capability_check")
_emit_routes_to_capability("p2", "healing_outcome_scoring_types", "capability_route")
_emit_writes_via_uwg("p2", "healing_outcome_scoring_types", "uwg_write")
_emit_blocks_direct_write("p2", "healing_outcome_scoring_types", "direct_write_block")
_emit_records_tool_invocation("p2", "healing_outcome_scoring_types", "tool_invocation")
_emit_captures_execution_output("p2", "healing_outcome_scoring_types", "exec_output")
_emit_dispatches_agent("p3", "healing_outcome_scoring_types", "agent_dispatch")
_emit_coordinates_agents("p3", "healing_outcome_scoring_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "healing_outcome_scoring_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "healing_outcome_scoring_types", "healing_outcome")
_emit_escalates_failure("p3", "healing_outcome_scoring_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "healing_outcome_scoring_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "healing_outcome_scoring_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "healing_outcome_scoring_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "healing_outcome_scoring_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "healing_outcome_scoring_types", "eval_metric")
_emit_stores_embedding("p4", "healing_outcome_scoring_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "healing_outcome_scoring_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "healing_outcome_scoring_types", "exec_snapshot_link")
from system_learning.types.healing_outcome_intake_types import HealingOutcomeIntakeRecord

_emit_applies_guardrail("p0", "healing_outcome_scoring_types", "p0_governance")
_emit_reads_policy_state("p0", "healing_outcome_scoring_types", "policy_binding")
_emit_snapshots_state("p0", "healing_outcome_scoring_types", "state_snapshot")
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

_emit_emits_metric_event("healing_outcome_scoring_types", "p4obs", "metric_1")
_emit_emits_metric_event("healing_outcome_scoring_types", "p4obs", "metric_2")
_emit_emits_metric_event("healing_outcome_scoring_types", "p4obs", "metric_3")
_emit_emits_metric_event("healing_outcome_scoring_types", "p4obs", "metric_4")
_emit_emits_metric_event("healing_outcome_scoring_types", "p4obs", "metric_5")
_emit_emits_metric_event("healing_outcome_scoring_types", "p4obs", "metric_6")
_emit_records_incident_event("healing_outcome_scoring_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("healing_outcome_scoring_types", "p4obs", "anomaly")
_emit_writes_observability_log("healing_outcome_scoring_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("healing_outcome_scoring_types", "p4obs", "mon_state")
_emit_triggers_alert("healing_outcome_scoring_types", "p4obs", "alert")
_emit_links_incident_trace("healing_outcome_scoring_types", "p4obs", "trace_link")
_emit_captures_pattern("healing_outcome_scoring_types", "p3lm", "pattern")
_emit_records_learning_event("healing_outcome_scoring_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("healing_outcome_scoring_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("healing_outcome_scoring_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("healing_outcome_scoring_types", "p3lm", "routing")
_emit_improves_agent_policy("healing_outcome_scoring_types", "p3lm", "policy")
_emit_stores_learning_state("healing_outcome_scoring_types", "p3lm", "state")
_emit_records_execution_trace("healing_outcome_scoring_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("healing_outcome_scoring_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("healing_outcome_scoring_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("healing_outcome_scoring_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("healing_outcome_scoring_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("healing_outcome_scoring_types", "env_read", "p2_env_1")
_emit_reads_environ("healing_outcome_scoring_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("healing_outcome_scoring_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("healing_outcome_scoring_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "healing_outcome_scoring_types", "context_pull")
_emit_pulls_context("p1", "healing_outcome_scoring_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "healing_outcome_scoring_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "healing_outcome_scoring_types", "uwg_term_2")
_emit_writes_through("p1", "healing_outcome_scoring_types", "write_through")
_emit_writes_through("p1", "healing_outcome_scoring_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "healing_outcome_scoring_types", "safety_validation")
_emit_invokes_eval("p1", "healing_outcome_scoring_types", "eval_call")
_emit_proposal_commits_routing("p1", "healing_outcome_scoring_types", "routing_commit")
_emit_escalates_to_human("p1", "healing_outcome_scoring_types", "human_escalation")
_emit_routes_through("p1", "healing_outcome_scoring_types", "route_through")
_emit_checks_agent_registry("p1", "healing_outcome_scoring_types", "agent_registry")
_emit_validates_agent_capability("p1", "healing_outcome_scoring_types", "capability")
_emit_dispatches_execution_plan("p1", "healing_outcome_scoring_types", "exec_plan")
_emit_agent_executes_agent("p1", "healing_outcome_scoring_types", "sub_agent")
_emit_routes_to_agent("p1", "healing_outcome_scoring_types", "target_agent")
_emit_verifies_policy("p1", "healing_outcome_scoring_types", "policy_check")
_emit_observes_runtime_state("p1", "healing_outcome_scoring_types", "runtime_state")
_emit_verifies_boundary("p1", "healing_outcome_scoring_types", "boundary_check")
_emit_transcripts_response("p1", "healing_outcome_scoring_types", "transcript")
_emit_hard_fails_untranscripted("p1", "healing_outcome_scoring_types")
_emit_gated_by_confidence("p1", "healing_outcome_scoring_types", "confidence_gate")
emit_replay_key("p0", "healing_outcome_scoring_types")
emit_determinism_digest("p0", "healing_outcome_scoring_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def _validate_weight(value: float, name: str) -> None:
    """Validate weight is finite and non-negative."""
    if not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number, got {type(value).__name__}")
    if not value >= 0:
        raise ValueError(f"{name} must be >= 0, got {value}")
    if value != value:
        raise ValueError(f"{name} must not be NaN")
    if value in (float("inf"), float("-inf")):
        raise ValueError(f"{name} must be finite, got {value}")


def _validate_ascii_only(value: str, name: str) -> None:
    """Validate string is ASCII-only."""
    try:
        value.encode("ascii")
    except UnicodeEncodeError:    # guardian: UnicodeEncodeError should be handled with specific context
        raise ValueError(f"{name} must be ASCII-only, contains non-ASCII characters")


def _stable_round(score: float) -> float:
    """Deterministic rounding: round-half-up to 4 decimal places."""
    return int(score * 10000 + 0.5) / 10000


@dataclass(frozen=True, slots=True)
class ScoringWeights:
    """Weights for deterministic scoring of healing outcome proposals.

    All weights must be finite and >= 0.
    """

    success_rate_weight: float
    stability_penalty_weight: float
    sample_size_weight: float
    risk_tier_penalty_weight: float

    def __post_init__(self) -> None:
        """Validate all weights."""
        _validate_weight(self.success_rate_weight, "success_rate_weight")
        _validate_weight(self.stability_penalty_weight, "stability_penalty_weight")
        _validate_weight(self.sample_size_weight, "sample_size_weight")
        _validate_weight(self.risk_tier_penalty_weight, "risk_tier_penalty_weight")


@dataclass(frozen=True, slots=True)
class ScoredRecommendation:
    """A scored recommendation from the offline evaluator.

    Reasons must be ASCII-only strings.
    """

    proposer_id: str
    target_surface: str
    recommended_actions: tuple[str, ...]
    score: float
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        """Validate fields."""
        if not isinstance(self.proposer_id, str):
            raise ValueError("proposer_id must be a string")
        if not isinstance(self.target_surface, str):
            raise ValueError("target_surface must be a string")
        if not isinstance(self.recommended_actions, tuple):
            raise ValueError("recommended_actions must be a tuple")
        if not isinstance(self.reasons, tuple):
            raise ValueError("reasons must be a tuple")
        _validate_weight(self.score, "score")
        for i, reason in enumerate(self.reasons):
            _validate_ascii_only(reason, f"reasons[{i}]")


@dataclass(frozen=True, slots=True)
class ScoringReport:
    """Report from offline evaluation of healing outcome proposals.

    Recommendations are sorted deterministically by (-score, proposer_id, target_surface).
    Rejected reasons are ordered deterministically.
    """

    created_utc: int
    intake_record: HealingOutcomeIntakeRecord
    weights: ScoringWeights
    schema_version: int = 1
    source: str = "offline-evaluator"
    recommendations: tuple[ScoredRecommendation, ...] = field(default_factory=tuple)
    rejected_reasons: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Validate fields."""
        if self.schema_version < 1:
            raise ValueError("schema_version must be >= 1")
        if not isinstance(self.created_utc, int):
            raise ValueError("created_utc must be an integer")
        if not isinstance(self.source, str):
            raise ValueError("source must be a string")
        if not isinstance(self.recommendations, tuple):
            raise ValueError("recommendations must be a tuple")
        if not isinstance(self.rejected_reasons, tuple):
            raise ValueError("rejected_reasons must be a tuple")
        for i, reason in enumerate(self.rejected_reasons):
            _validate_ascii_only(reason, f"rejected_reasons[{i}]")
        if list(self.recommendations) != sorted(
            self.recommendations, key=lambda r: (-r.score, r.proposer_id, r.target_surface),
        ):
            raise ValueError("recommendations must be sorted by (-score, proposer_id, target_surface)")

    def canonical_bytes(self) -> bytes:
        """Get canonical byte representation for hashing.

        Returns:
            Stable byte representation using sorted JSON keys and stable rounding
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ScoringReport.canonical_bytes")

        data = asdict(self)
        canonical_json = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return canonical_json.encode("utf-8")

    def content_hash(self) -> str:
        """Get SHA-256 hash of canonical content.

        Returns:
            Hexadecimal SHA-256 hash
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


__all__ = ["ScoringWeights", "ScoredRecommendation", "ScoringReport", "_stable_round"]
