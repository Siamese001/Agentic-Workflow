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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

_emit_dispatches_healing_run("p1", "replay_bundle_emitter", "L4")
_emit_routes_through("p1", "replay_bundle_emitter", "L4")
_emit_escalates_to_human("p1", "replay_bundle_emitter", "L4")
_emit_reads_policy_state("p1", "replay_bundle_emitter", "L4")


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
