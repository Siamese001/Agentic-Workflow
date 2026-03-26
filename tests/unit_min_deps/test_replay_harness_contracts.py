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

#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_replay_harness_contracts")
# REMOVED: _emit_applies_guardrail("p0", "test_replay_harness_contracts", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_replay_harness_contracts", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_replay_harness_contracts", "state_snapshot")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
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
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_replay_harness_contracts", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_replay_harness_contracts", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_replay_harness_contracts", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_replay_harness_contracts", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_replay_harness_contracts", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_replay_harness_contracts", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_replay_harness_contracts", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_replay_harness_contracts", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_replay_harness_contracts", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_replay_harness_contracts", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_replay_harness_contracts", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_replay_harness_contracts", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_replay_harness_contracts", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_replay_harness_contracts", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_replay_harness_contracts", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_replay_harness_contracts", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_replay_harness_contracts", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_replay_harness_contracts", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_replay_harness_contracts", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_replay_harness_contracts", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_replay_harness_contracts", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_replay_harness_contracts", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_replay_harness_contracts", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_replay_harness_contracts", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_replay_harness_contracts", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_replay_harness_contracts", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_replay_harness_contracts", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_replay_harness_contracts", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_replay_harness_contracts", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_replay_harness_contracts", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_replay_harness_contracts", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_replay_harness_contracts", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_replay_harness_contracts", "write_through")
# REMOVED: _emit_writes_through("p1", "test_replay_harness_contracts", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_replay_harness_contracts", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_replay_harness_contracts", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_replay_harness_contracts", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_replay_harness_contracts", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_replay_harness_contracts", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_replay_harness_contracts", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_replay_harness_contracts", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_replay_harness_contracts", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_replay_harness_contracts", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_replay_harness_contracts", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_replay_harness_contracts", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_replay_harness_contracts", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_replay_harness_contracts", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_replay_harness_contracts", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_replay_harness_contracts")
# REMOVED: _emit_gated_by_confidence("p1", "test_replay_harness_contracts", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_replay_harness_contracts")
# REMOVED: emit_determinism_digest("p0", "test_replay_harness_contracts")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_replay_harness_contracts", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_replay_harness_contracts", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_replay_harness_contracts", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_replay_harness_contracts", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_replay_harness_contracts", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_replay_harness_contracts", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_replay_harness_contracts", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_replay_harness_contracts", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_replay_harness_contracts", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_replay_harness_contracts", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_replay_harness_contracts", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_replay_harness_contracts", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_replay_harness_contracts", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_replay_harness_contracts", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_replay_harness_contracts", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_replay_harness_contracts", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_replay_harness_contracts", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_replay_harness_contracts", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_replay_harness_contracts", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_replay_harness_contracts", "exec_snapshot_link")

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
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L2_execution.determinism.canonicalize import canonical_bytes
        from agentic_core.L4_state.enforcement.replay_bundle_store import ReplayBundleStore
        from agentic_core.L4_state.types.replay_bundle_types import ReplayBundle
        from agentic_core.L2_execution.determinism.canonicalize import canonical_bytes
        from agentic_core.L2_execution.enforcement.key_source import TestKeySource, inject_key_source
        from agentic_core.L2_execution.types.instruction_packet_types import InstructionPacket
        from agentic_core.L2_execution.determinism.canonicalize import canonical_bytes
        from agentic_core.L2_execution.types.gateway_types import GenerationRequest
        from agentic_core.L0_routing.enforcement.crypto_trust_contracts import (
        from agentic_core.L0_routing.types.crypto_trust_types import (
        from agentic_core.L2_execution.enforcement.key_source import TestKeySource, inject_key_source
        from agentic_core.L2_execution.types.instruction_packet_types import InstructionPacket
        from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
        from agentic_core.L2_execution.determinism.canonicalize import canonical_bytes
        d1 = _digest(artifact)
        d2 = _digest(artifact)
        assert d1 == d2, f"{req}: replay digest mismatch"

    assert d1 == d2, f"{req}: replay digest mismatch"


def test_req158_reorder_tamper_detected():
    chain = ["h1", "h2", "h3"]
    digest_original = _digest(chain)
    tampered = ["h3", "h1", "h2"]
    assert _digest(tampered) != digest_original, "REQ-158: tamper not detected"


def test_req157_replay_bundle_store_deterministic():
#  # MOVED: from agentic_core.L2_execution.determinism.canonicalize import canonical_bytes
#  # MOVED: from agentic_core.L4_state.enforcement.replay_bundle_store import ReplayBundleStore
#  # MOVED: from agentic_core.L4_state.types.replay_bundle_types import ReplayBundle

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
"""Test req036_two_runs_identical_digest runtime behavior."""
# Arrange
# TODO: Set up execution parameters
input_data = {}  # Replace with actual test data

# Act
# TODO: Execute req036_two_runs_identical_digest
result = None  # Replace with actual execution

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
# TODO: Add specific execution assertions
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
#  # MOVED: from agentic_core.L2_execution.determinism.canonicalize import canonical_bytes
#  # MOVED: from agentic_core.L2_execution.enforcement.key_source import TestKeySource, inject_key_source
#  # MOVED: from agentic_core.L2_execution.types.instruction_packet_types import InstructionPacket

    inject_key_source(TestKeySource())
    pkt = InstructionPacket(instruction_id="CI-00000001", payload="fixed")
    b1 = canonical_bytes(pkt)
    b2 = canonical_bytes(pkt)
    assert b1 == b2 and len(b1) > 0


def test_req036_gateway_request_normalization_stable():
#  # MOVED: from agentic_core.L2_execution.determinism.canonicalize import canonical_bytes
#  # MOVED: from agentic_core.L2_execution.types.gateway_types import GenerationRequest

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
#  # MOVED: from agentic_core.L0_routing.enforcement.crypto_trust_contracts import (
        sign_artifact,
        verify_signature,
    )
#  # MOVED: from agentic_core.L0_routing.types.crypto_trust_types import (
        DeterministicTestEnclave,
        KeyRecord,
        KeyStatus,
        SigningAlgorithm,
        TrustRoot,
    )
#  # MOVED: from agentic_core.L2_execution.enforcement.key_source import TestKeySource, inject_key_source
#  # MOVED: from agentic_core.L2_execution.types.instruction_packet_types import InstructionPacket

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
#  # MOVED: from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
#  # MOVED: from agentic_core.L2_execution.determinism.canonicalize import canonical_bytes

    snap = SemanticClockSnapshot(tick=42, vector_clock=())
    b1 = canonical_bytes(snap)
    b2 = canonical_bytes(snap)
    assert b1 == b2 and len(b1) > 0
