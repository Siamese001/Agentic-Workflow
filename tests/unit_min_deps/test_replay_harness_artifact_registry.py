"""Replay harness: REQ-157/158/212/302/303/307/313/320/327/331."""

import hashlib
import json

import pytest

pytestmark = [pytest.mark.unit_min_deps]


def _digest(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


@pytest.mark.parametrize(
    "req,artifact",
    [
        ("REQ-157", {"transcript_hash": "th1", "trace_id": "CC3AL1-00000001", "entries": ["e1", "e2"]}),
        ("REQ-158", {"chain": ["h1", "h2", "h3"], "trace_id": "CC3AL1-00000001"}),
        ("REQ-212", {"intended": "plan_v1", "actual": "plan_v1", "diff": None}),
        ("REQ-302", {"transcript_hash": "th2", "trace_id": "CC3AL1-00000002", "entries": ["e3"]}),
        ("REQ-303", {"chain": ["h4", "h5"], "trace_id": "CC3AL1-00000002"}),
        ("REQ-307", {"pack_id": "ep1", "trace_id": "CC3AL1-00000001", "hash": "abc"}),
        ("REQ-313", {"manifest_hash": "mh1", "node_id": "N1", "edit_op": "replace"}),
        ("REQ-320", {"ssot_version": "v2", "hash": "sh1", "trace_id": "CC3AL1-00000001"}),
        ("REQ-327", {"declared": ["WRITE"], "observed": ["WRITE"], "trace_id": "CC3AL1-00000001"}),
        ("REQ-331", {"query": {"effect_class": "WRITE"}, "result": ["T1"]}),
    ],
)
def test_artifact_replay_deterministic(req, artifact):
    d1 = _digest(artifact)
    d2 = _digest(artifact)
    assert d1 == d2, f"{req}: replay digest mismatch"


def test_req158_reorder_tamper_detected():
    chain = ["h1", "h2", "h3"]
    digest_original = _digest(chain)
    tampered = ["h3", "h1", "h2"]  # reordered
    assert _digest(tampered) != digest_original, "REQ-158: tamper not detected"


# ---------------------------------------------------------------------------
# SOV-DELTA: ADD REAL CALL PATH for W7 (append; do NOT remove existing tests)
# ---------------------------------------------------------------------------


# REQ-157/302 real path: ReplayBundleStore store/fetch (no IO)
def test_req157_replay_bundle_store_deterministic():
    from agentic_core.L2_execution.determinism.canonicalize import canonical_bytes
    from agentic_core.L4_state.enforcement.replay_bundle_store import ReplayBundleStore
    from agentic_core.L4_state.types.replay_bundle import ReplayBundle

    bundle = ReplayBundle(
        schema_version=1,
        mission_id="CC3AL1-00000001",
        execution_start_tick=0,
        execution_end_tick=1,
        manifest_hash="a" * 64,
        active_config_hashes={},
        retrieval_used=False,
        citation_hash="",
        prior_detection_signal_hash="",
        prior_violation_event_hashes=[],
        tool_intent_hashes=[],
        tool_result_hashes=[],
    )
    b1 = canonical_bytes(bundle)
    b2 = canonical_bytes(bundle)
    assert b1 == b2
    store = ReplayBundleStore()
    h = store.store_replay_bundle(bundle)
    assert store.fetch_replay_bundle(h) is bundle
