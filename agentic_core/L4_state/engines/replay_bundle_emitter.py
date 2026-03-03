"""
Phase 9 — ReplayBundle Emitter: gateway completion path emission.

emit_replay_bundle() is called after successful execution to produce and
persist a ReplayBundle to the L4 SSOT store.

Non-mutating to knowledge index (no upsert/setex calls).
"""

from __future__ import annotations

from agentic_core.L4_state.enforcement.replay_bundle_store import ReplayBundleStore
from agentic_core.L4_state.types.replay_bundle_types import ReplayBundle, build_replay_bundle


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
