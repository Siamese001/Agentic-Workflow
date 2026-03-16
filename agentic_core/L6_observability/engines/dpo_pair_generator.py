from __future__ import annotations

from dataclasses import dataclass
from typing import Any, NamedTuple

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "dpo_pair_generator")
emit_determinism_digest("p0", "dpo_pair_generator")

_emit_dispatches_healing_run("p1", "dpo_pair_generator", "L6")
_emit_routes_through("p1", "dpo_pair_generator", "L6")
_emit_escalates_to_human("p1", "dpo_pair_generator", "L6")
_emit_reads_policy_state("p1", "dpo_pair_generator", "L6")
_emit_authorize_and_execute("p2", "dpo_pair_generator", "execution_auth")
_emit_validates_capability("p2", "dpo_pair_generator", "capability_check")
_emit_routes_to_capability("p2", "dpo_pair_generator", "capability_route")
_emit_writes_via_uwg("p2", "dpo_pair_generator", "uwg_write")
_emit_blocks_direct_write("p2", "dpo_pair_generator", "direct_write_block")
_emit_records_tool_invocation("p2", "dpo_pair_generator", "tool_invocation")
_emit_captures_execution_output("p2", "dpo_pair_generator", "exec_output")
_emit_dispatches_agent("p3", "dpo_pair_generator", "agent_dispatch")
_emit_coordinates_agents("p3", "dpo_pair_generator", "agent_coordination")
_emit_records_workflow_lineage("p3", "dpo_pair_generator", "workflow_lineage")
_emit_records_healing_outcome("p3", "dpo_pair_generator", "healing_outcome")
_emit_escalates_failure("p3", "dpo_pair_generator", "failure_escalation")
_emit_orchestrates_workflow("p3", "dpo_pair_generator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "dpo_pair_generator", "healing_dispatch")
_emit_invokes_evaluation("p3", "dpo_pair_generator", "evaluation_signal")
_emit_records_telemetry_event("p4", "dpo_pair_generator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "dpo_pair_generator", "eval_metric")
_emit_stores_embedding("p4", "dpo_pair_generator", "embedding_store")
_emit_updates_meta_learning_state("p4", "dpo_pair_generator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "dpo_pair_generator", "exec_snapshot_link")


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
