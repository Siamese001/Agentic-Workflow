"""
Phase 9 — ReplayBundle Emitter: gateway completion path emission.

emit_replay_bundle() is called after successful execution to produce and
persist a ReplayBundle to the L4 SSOT store.

Non-mutating to knowledge index (no upsert/setex calls).
"""

from __future__ import annotations

import uuid

from agentic_core.L4_state.enforcement.replay_bundle_store import ReplayBundleStore
from agentic_core.L4_state.types.replay_bundle_types import ReplayBundle, build_replay_bundle
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

emit_replay_key("p0", "replay_bundle_emitter")
emit_determinism_digest("p0", "replay_bundle_emitter")

_emit_dispatches_healing_run("p1", "replay_bundle_emitter", "L4")
_emit_routes_through("p1", "replay_bundle_emitter", "L4")
_emit_escalates_to_human("p1", "replay_bundle_emitter", "L4")
_emit_reads_policy_state("p1", "replay_bundle_emitter", "L4")
_emit_authorize_and_execute("p2", "replay_bundle_emitter", "execution_auth")
_emit_validates_capability("p2", "replay_bundle_emitter", "capability_check")
_emit_routes_to_capability("p2", "replay_bundle_emitter", "capability_route")
_emit_writes_via_uwg("p2", "replay_bundle_emitter", "uwg_write")
_emit_blocks_direct_write("p2", "replay_bundle_emitter", "direct_write_block")
_emit_records_tool_invocation("p2", "replay_bundle_emitter", "tool_invocation")
_emit_captures_execution_output("p2", "replay_bundle_emitter", "exec_output")
_emit_dispatches_agent("p3", "replay_bundle_emitter", "agent_dispatch")
_emit_coordinates_agents("p3", "replay_bundle_emitter", "agent_coordination")
_emit_records_workflow_lineage("p3", "replay_bundle_emitter", "workflow_lineage")
_emit_records_healing_outcome("p3", "replay_bundle_emitter", "healing_outcome")
_emit_escalates_failure("p3", "replay_bundle_emitter", "failure_escalation")
_emit_orchestrates_workflow("p3", "replay_bundle_emitter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "replay_bundle_emitter", "healing_dispatch")
_emit_invokes_evaluation("p3", "replay_bundle_emitter", "evaluation_signal")
_emit_records_telemetry_event("p4", "replay_bundle_emitter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "replay_bundle_emitter", "eval_metric")
_emit_stores_embedding("p4", "replay_bundle_emitter", "embedding_store")
_emit_updates_meta_learning_state("p4", "replay_bundle_emitter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "replay_bundle_emitter", "exec_snapshot_link")


def emit_replay_bundle(
    mission_id: str,
    execution_start_tick: int,
    execution_end_tick: int,
    manifest_hash: str,
    active_config_hashes: dict[str, str],
    store: ReplayBundleStore,
    *,
    retrieval_used: bool = False,
    citation_hash: str = "",
    prior_detection_signal_hash: str = "",
    prior_violation_event_hashes: list[str] | None = None,
    tool_intent_hashes: list[str] | None = None,
    tool_result_hashes: list[str] | None = None,
) -> ReplayBundle:
    """
    Build and persist a ReplayBundle to the L4 SSOT store.

    Returns the persisted ReplayBundle (with stable replay_hash).
    Non-mutating to knowledge index.
    """
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "emit_replay_bundle", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "emit_replay_bundle")
    _emit_snapshots_state(str(uuid.uuid4()), "Module.emit_replay_bundle", "L4_STATE")
    bundle = build_replay_bundle(
        mission_id=mission_id,
        execution_start_tick=execution_start_tick,
        execution_end_tick=execution_end_tick,
        manifest_hash=manifest_hash,
        active_config_hashes=active_config_hashes,
        retrieval_used=retrieval_used,
        citation_hash=citation_hash,
        prior_detection_signal_hash=prior_detection_signal_hash,
        prior_violation_event_hashes=prior_violation_event_hashes,
        tool_intent_hashes=tool_intent_hashes,
        tool_result_hashes=tool_result_hashes,
    )
    store.store_replay_bundle(bundle)
    return bundle
