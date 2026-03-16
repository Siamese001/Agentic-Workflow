from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import NamedTuple, Sequence

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

emit_replay_key("p0", "deterministic_context_optimizer")
emit_determinism_digest("p0", "deterministic_context_optimizer")

_emit_dispatches_healing_run("p1", "deterministic_context_optimizer", "L1")
_emit_routes_through("p1", "deterministic_context_optimizer", "L1")
_emit_escalates_to_human("p1", "deterministic_context_optimizer", "L1")
_emit_reads_policy_state("p1", "deterministic_context_optimizer", "L1")
_emit_authorize_and_execute("p2", "deterministic_context_optimizer", "execution_auth")
_emit_validates_capability("p2", "deterministic_context_optimizer", "capability_check")
_emit_routes_to_capability("p2", "deterministic_context_optimizer", "capability_route")
_emit_writes_via_uwg("p2", "deterministic_context_optimizer", "uwg_write")
_emit_blocks_direct_write("p2", "deterministic_context_optimizer", "direct_write_block")
_emit_records_tool_invocation("p2", "deterministic_context_optimizer", "tool_invocation")
_emit_captures_execution_output("p2", "deterministic_context_optimizer", "exec_output")
_emit_dispatches_agent("p3", "deterministic_context_optimizer", "agent_dispatch")
_emit_coordinates_agents("p3", "deterministic_context_optimizer", "agent_coordination")
_emit_records_workflow_lineage("p3", "deterministic_context_optimizer", "workflow_lineage")
_emit_records_healing_outcome("p3", "deterministic_context_optimizer", "healing_outcome")
_emit_escalates_failure("p3", "deterministic_context_optimizer", "failure_escalation")
_emit_orchestrates_workflow("p3", "deterministic_context_optimizer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "deterministic_context_optimizer", "healing_dispatch")
_emit_invokes_evaluation("p3", "deterministic_context_optimizer", "evaluation_signal")
_emit_records_telemetry_event("p4", "deterministic_context_optimizer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "deterministic_context_optimizer", "eval_metric")
_emit_stores_embedding("p4", "deterministic_context_optimizer", "embedding_store")
_emit_updates_meta_learning_state("p4", "deterministic_context_optimizer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "deterministic_context_optimizer", "exec_snapshot_link")


@dataclass(frozen=True)
class ContextItem:
    """Represents a single item to be included in the context window."""

    content: str
    score: float
    content_hash: str


class OptimizationResult(NamedTuple):
    """The result of a context optimization operation."""

    optimized_context: Sequence[ContextItem]
    context_hash_before: str
    context_hash_after: str
    top_k_cap: int


def _compute_context_hash(items: Sequence[ContextItem]) -> str:
    """Computes a deterministic hash of the context items' identifiers."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_compute_context_hash", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_compute_context_hash", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L1_COGNITION, "_compute_context_hash")
    sorted_hashes = sorted([item.content_hash for item in items])
    hasher = hashlib.sha256()
    for h in sorted_hashes:
        hasher.update(h.encode("utf-8"))
    return hasher.hexdigest()


def optimize_context_window(
    items: Sequence[ContextItem], top_k_cap: int, seed_pack_hash: str
) -> OptimizationResult:
    """
    Optimizes the context window with deterministic ordering and capping.

    This function enforces Guarantee #3 by ensuring that the context slicing
    is stable, replayable, and does not suffer from non-determinism due to
    unstable sorting of items with equal scores.

    Args:
        items: The full list of candidate items for the context window.
        top_k_cap: The maximum number of items to include in the final context.
        seed_pack_hash: The hash of the embedding pack, used for replay binding.

    Returns:
        An OptimizationResult containing the sliced context and determinism hashes.
    """
    if not items:
        empty_hash = hashlib.sha256(b"").hexdigest()
        return OptimizationResult(
            optimized_context=[],
            context_hash_before=empty_hash,
            context_hash_after=empty_hash,
            top_k_cap=top_k_cap,
        )
    context_hash_before = _compute_context_hash(items)
    sorted_items = sorted(items, key=lambda x: (-x.score, x.content_hash))
    optimized_context = sorted_items[:top_k_cap]
    context_hash_after = _compute_context_hash(optimized_context)
    return OptimizationResult(
        optimized_context=optimized_context,
        context_hash_before=context_hash_before,
        context_hash_after=context_hash_after,
        top_k_cap=top_k_cap,
    )
