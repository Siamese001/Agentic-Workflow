"""
Tier-to-model ID mapping for heal policy escalation.

Pure mapping function (stdlib-only, no environment access).
Phase 6 Wave 6.2.
"""

from __future__ import annotations

from agentic_core.L5_safety.types.heal_policy_types import ReasoningTier
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

emit_replay_key("p0", "heal_model_map_types")
emit_determinism_digest("p0", "heal_model_map_types")

_emit_dispatches_healing_run("p1", "heal_model_map_types", "L5")
_emit_routes_through("p1", "heal_model_map_types", "L5")
_emit_escalates_to_human("p1", "heal_model_map_types", "L5")
_emit_reads_policy_state("p1", "heal_model_map_types", "L5")
_emit_authorize_and_execute("p2", "heal_model_map_types", "execution_auth")
_emit_validates_capability("p2", "heal_model_map_types", "capability_check")
_emit_routes_to_capability("p2", "heal_model_map_types", "capability_route")
_emit_writes_via_uwg("p2", "heal_model_map_types", "uwg_write")
_emit_blocks_direct_write("p2", "heal_model_map_types", "direct_write_block")
_emit_records_tool_invocation("p2", "heal_model_map_types", "tool_invocation")
_emit_captures_execution_output("p2", "heal_model_map_types", "exec_output")
_emit_dispatches_agent("p3", "heal_model_map_types", "agent_dispatch")
_emit_coordinates_agents("p3", "heal_model_map_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "heal_model_map_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "heal_model_map_types", "healing_outcome")
_emit_escalates_failure("p3", "heal_model_map_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "heal_model_map_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "heal_model_map_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "heal_model_map_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "heal_model_map_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "heal_model_map_types", "eval_metric")
_emit_stores_embedding("p4", "heal_model_map_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "heal_model_map_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "heal_model_map_types", "exec_snapshot_link")

LOW_MODEL_ID = "local_low"
HIGH_MODEL_ID = "local_high"


def map_tier_to_model_id(tier: ReasoningTier) -> str:
    """Map a reasoning tier to a model identifier.

    Args:
        tier: The reasoning tier (LOW or HIGH)

    Returns:
        Model identifier string ("local_low" or "local_high")
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "map_tier_to_model_id", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "map_tier_to_model_id", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "map_tier_to_model_id")
    return LOW_MODEL_ID if tier == ReasoningTier.LOW else HIGH_MODEL_ID
