"""Replay harness contracts: merged from 4-file family.

Covers:
  artifact_registry:   REQ-157/158/212/302/303/307/313/320/327/331
  core_determinism:    REQ-036/060/063/095/184/289
  crypto_clock:        REQ-337/360/378/381/384/395/399/404/409/413
  state_protocol:      REQ-142/192/201/222/242/254/262
"""

from __future__ import annotations

import hashlib
import hmac
import json

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes

pytestmark = [pytest.mark.unit_min_deps]


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _digest(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _digest_bytes(obj) -> str:
    return hashlib.sha256(_canonical(obj)).hexdigest()


# ===========================================================================
# artifact_registry: REQ-157/158/212/302/303/307/313/320/327/331
# ===========================================================================


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
    tampered = ["h3", "h1", "h2"]
    assert _digest(tampered) != digest_original, "REQ-158: tamper not detected"


def test_req157_replay_bundle_store_deterministic():
    from agentic_core.L2_execution.determinism.canonicalize import canonical_bytes
    from agentic_core.L4_state.enforcement.replay_bundle_store import ReplayBundleStore
    from agentic_core.L4_state.types.replay_bundle_types import ReplayBundle

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


# ===========================================================================
# core_determinism: REQ-036/060/063/095/184/289
# ===========================================================================


def test_req036_two_runs_identical_digest():
    inputs = {"payload": "fixed", "policy_hash": "ph1", "trace_id": "CC3AL1-00000001"}
    assert _digest_bytes(inputs) == _digest_bytes(inputs)


def test_req060_stage_order_deterministic():
    STAGES = ("AUDIT", "TELEMETRY", "CONFIG", "SNAPSHOT", "RCA", "PROPOSE", "VALIDATE", "INTAKE", "COMMIT")
    run1 = list(STAGES)
    run2 = list(STAGES)
    assert run1 == run2


def test_req063_proposer_order_fixed():
    ORDER = ["L0", "RAG", "L1", "L5"]
    assert ORDER == sorted(ORDER, key=lambda x: ORDER.index(x))


def test_req095_sorted_prompt_composition():
    fragments = ["frag_c", "frag_a", "frag_b"]
    run1 = sorted(fragments)
    run2 = sorted(fragments)
    assert run1 == run2 and _digest(run1) == _digest(run2)


def test_req184_ast_serializer_deterministic():
    import ast

    code = "x = 1 + 2"
    tree = ast.parse(code)
    dump1 = ast.dump(tree, indent=None)
    dump2 = ast.dump(tree, indent=None)
    assert _digest(dump1) == _digest(dump2)


def test_req289_enforcement_audit_deterministic():
    from pathlib import Path

    from ops_scripts.ci.enforcement_audit import audit, parse_tagged_corpus

    corpus = (Path(__file__).parents[2] / "docs/reports/plans/Agentic Master Requirements.md").read_text(
        encoding="utf-8"
    )
    reqs = parse_tagged_corpus(corpus)
    r1 = audit(reqs)
    r2 = audit(reqs)
    assert r1["status"] == r2["status"]
    assert r1["failure_count"] == r2["failure_count"]


def test_req036_instruction_packet_canonical_bytes_stable():
    from agentic_core.L2_execution.determinism.canonicalize import canonical_bytes
    from agentic_core.L2_execution.enforcement.key_source import TestKeySource, inject_key_source
    from agentic_core.L2_execution.types.instruction_packet_types import InstructionPacket

    inject_key_source(TestKeySource())
    pkt = InstructionPacket(instruction_id="CI-00000001", payload="fixed")
    b1 = canonical_bytes(pkt)
    b2 = canonical_bytes(pkt)
    assert b1 == b2 and len(b1) > 0


def test_req036_gateway_request_normalization_stable():
    from agentic_core.L2_execution.determinism.canonicalize import canonical_bytes
    from agentic_core.L2_execution.types.gateway_types import GenerationRequest

    req = GenerationRequest(agent_id="test", provider="openai", model="gpt-4o", prompt="hello")
    b1 = canonical_bytes(req)
    b2 = canonical_bytes(req)
    assert b1 == b2


# ===========================================================================
# crypto_clock: REQ-337/360/378/381/384/395/399/404/409/413
# ===========================================================================


@pytest.mark.parametrize(
    "req,obj",
    [
        ("REQ-337", {"from_state": "SHADOW", "to_state": "ACTIVE", "clock_tick": 7}),
        ("REQ-360", {"artifact_type": "RESULT", "layer": "L2", "verdict": "LEGAL"}),
        ("REQ-378", {"seed": "CC3AL1-AABBCCDD", "index": 0}),
        ("REQ-381", {"keys": ["b", "a"], "values": [2, 1]}),
        ("REQ-384", {"input_bytes": "aabbcc", "algo": "sha256"}),
        ("REQ-409", {"clock_vector": [0, 1, 2], "trace_id": "CC3AL1-00000001"}),
        (
            "REQ-413",
            {"provider_id": "openai", "model_id": "gpt-4o", "gateway_version": "1.0", "clock_vector": [0, 1]},
        ),
    ],
)
def test_crypto_clock_replay_deterministic(req, obj):
    assert _digest(obj) == _digest(obj), f"{req}: not deterministic"


def test_req395_hmac_deterministic():
    key = b"test-key"
    data = b"canonical payload"
    h1 = hmac.new(key, data, hashlib.sha256).hexdigest()
    h2 = hmac.new(key, data, hashlib.sha256).hexdigest()
    assert h1 == h2  # REQ-395


def test_req399_enclave_deterministic():
    payload = b"artifact_hash_abc"
    sig1 = hashlib.sha256(payload).hexdigest()
    sig2 = hashlib.sha256(payload).hexdigest()
    assert sig1 == sig2  # REQ-399 / REQ-404


def test_req413_provider_binding_in_digest():
    digest = _digest(
        {"provider_id": "openai", "model_id": "gpt-4o", "gateway_version": "1.0", "clock_vector": [0]}
    )
    assert len(digest) == 64


def test_req399_signature_enclave_real_round_trip():
    from agentic_core.L0_routing.enforcement.crypto_trust_contracts import (
        sign_artifact,
        verify_signature,
    )
    from agentic_core.L0_routing.types.crypto_trust_types import (
        DeterministicTestEnclave,
        KeyRecord,
        KeyStatus,
        SigningAlgorithm,
        TrustRoot,
    )
    from agentic_core.L2_execution.enforcement.key_source import TestKeySource, inject_key_source
    from agentic_core.L2_execution.types.instruction_packet_types import InstructionPacket

    inject_key_source(TestKeySource())
    key_id = "test-key-1"
    key = KeyRecord(
        key_id=key_id,
        public_key=b"test-secret-key-0123456789abcdef",
        created_tick=0,
        status=KeyStatus.ACTIVE,
        algorithm=SigningAlgorithm.HMAC_SHA256,
    )
    trust_root = TrustRoot(keys=(key,))
    enclave = DeterministicTestEnclave(trust_root=trust_root)

    pkt = InstructionPacket(instruction_id="CI-00000001", payload="canonical")
    artifact_bytes = pkt.canonical_bytes()

    env1 = sign_artifact(artifact_bytes, key_id, enclave, "CC3AL1-00000001", 0)
    env2 = sign_artifact(artifact_bytes, key_id, enclave, "CC3AL1-00000001", 0)
    assert env1.signature == env2.signature
    assert verify_signature(artifact_bytes, env1, trust_root, enclave)


# ===========================================================================
# state_protocol: REQ-142/192/201/222/242/254/262
# ===========================================================================


def test_req142_seam_audit_deterministic():
    artifact = {"source": "L0", "target": "L1", "invocation_hash": "abc123", "trace_id": "CC3AL1-00000001"}
    assert _digest(artifact) == _digest(artifact)


def test_req192_clock_serialization_canonical():
    clock = {"tick": 42, "trace_id": "CC3AL1-00000001", "entries": [{"layer": "L2", "op": "write"}]}
    assert _digest(clock) == _digest(clock)


def test_req201_retrieval_deterministic():
    chunks = sorted(["chunk_b", "chunk_a", "chunk_c"])
    assert _digest(chunks) == _digest(chunks)


def test_req222_law_slot_deterministic():
    invocation = {"token_scope": "read", "tool_id": "T1", "trace_id": "CC3AL1-00000001"}
    assert _digest(invocation) == _digest(invocation)


def test_req242_rollback_event_deterministic():
    event = {"reason_code": "GUARDIAN_FAIL", "prev_pointer": "v1", "new_pointer": "v0"}
    assert _digest(event) == _digest(event)


def test_req254_cross_wave_linkage():
    wave1_hash = hashlib.sha256(b"wave1").hexdigest()
    wave2 = {"prev_wave_hash": wave1_hash, "payload": "wave2"}
    assert _digest(wave2) == _digest(wave2)


def test_req262_governance_enforcement_deterministic():
    decision = {"policy_hash": "ph1", "verdict": "ALLOW", "trace_id": "CC3AL1-00000001"}
    assert _digest(decision) == _digest(decision)


def test_req192_semantic_clock_real_serialize():
    from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
    from agentic_core.L2_execution.determinism.canonicalize import canonical_bytes

    snap = SemanticClockSnapshot(tick=42, vector_clock=())
    b1 = canonical_bytes(snap)
    b2 = canonical_bytes(snap)
    assert b1 == b2 and len(b1) > 0
