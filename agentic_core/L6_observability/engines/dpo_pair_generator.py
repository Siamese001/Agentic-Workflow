from __future__ import annotations

from dataclasses import dataclass
from typing import Any, NamedTuple

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    record_execution_trace,
)

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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

record_execution_trace("dpo_pair_generator", "dpo_pair_generator_trace")


class BoundingViolation(Exception):
    """Raised when a DPO feedback value is outside the allowed bounds."""


@dataclass(frozen=True)
class DPOPair:
    """Represents a chosen/rejected pair for Direct Preference Optimization."""

    control_hash: str
    candidate_hash: str
    control_payload: Any
    candidate_payload: Any
    raw_score: float


class BoundedDPOPair(NamedTuple):
    """A DPO pair with its score bounded and clamped."""

    pair: DPOPair
    bounded_score: float


@dataclass(frozen=True)
class DPOBoundingPolicy:
    """Defines the sovereign policy for bounding DPO feedback."""

    min_clamp: float = 0.1
    max_clamp: float = 2.0
    max_delta: float = 0.1


def create_bounded_dpo_pairs(pairs: list[DPOPair], policy: DPOBoundingPolicy) -> list[BoundedDPOPair]:
    """
    Processes a list of DPO pairs, applying sovereign bounding and sorting.

    This function enforces Guarantee #23 by:
    1. Sorting pairs deterministically to prevent reordering on replay.
    2. Clamping raw scores to a fixed range [0.1, 2.0].
    3. Limiting the maximum change (delta) from a neutral score (1.0).

    Args:
        pairs: The list of raw DPO pairs to process.
        policy: The bounding policy to apply.

    Returns:
        A list of bounded DPO pairs, ready for meta-learning.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "create_bounded_dpo_pairs", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "create_bounded_dpo_pairs", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "create_bounded_dpo_pairs")
    sorted_pairs = sorted(pairs, key=lambda p: (p.control_hash, p.candidate_hash))
    bounded_pairs: list[BoundedDPOPair] = []
    for pair in sorted_pairs:
        clamped_score = max(policy.min_clamp, min(pair.raw_score, policy.max_clamp))
        delta = clamped_score - 1.0
        if abs(delta) > policy.max_delta:
            bounded_score = 1.0 + (policy.max_delta if delta > 0 else -policy.max_delta)
        else:
            bounded_score = clamped_score
        bounded_pairs.append(BoundedDPOPair(pair=pair, bounded_score=bounded_score))
    return bounded_pairs
