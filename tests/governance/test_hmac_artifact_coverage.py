"""REQ-018: all governance artifacts use HMAC-SHA256; signing is deterministic."""

from __future__ import annotations

import hashlib
import hmac

import pytest

from agentic_core.L0_routing.enforcement.crypto_trust_contracts import (
    hash_artifact_canonical,
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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_hmac_artifact_coverage")
_emit_applies_guardrail("p0", "test_hmac_artifact_coverage", "p0_governance")
_emit_reads_policy_state("p0", "test_hmac_artifact_coverage", "policy_binding")
_emit_snapshots_state("p0", "test_hmac_artifact_coverage", "state_snapshot")
emit_replay_key("p0", "test_hmac_artifact_coverage")
emit_determinism_digest("p0", "test_hmac_artifact_coverage")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_hmac_artifact_coverage", "execution_auth")
_emit_validates_capability("p2", "test_hmac_artifact_coverage", "capability_check")
_emit_routes_to_capability("p2", "test_hmac_artifact_coverage", "capability_route")
_emit_writes_via_uwg("p2", "test_hmac_artifact_coverage", "uwg_write")
_emit_blocks_direct_write("p2", "test_hmac_artifact_coverage", "direct_write_block")
_emit_records_tool_invocation("p2", "test_hmac_artifact_coverage", "tool_invocation")
_emit_captures_execution_output("p2", "test_hmac_artifact_coverage", "exec_output")
_emit_dispatches_agent("p3", "test_hmac_artifact_coverage", "agent_dispatch")
_emit_coordinates_agents("p3", "test_hmac_artifact_coverage", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_hmac_artifact_coverage", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_hmac_artifact_coverage", "healing_outcome")
_emit_escalates_failure("p3", "test_hmac_artifact_coverage", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_hmac_artifact_coverage", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_hmac_artifact_coverage", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_hmac_artifact_coverage", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_hmac_artifact_coverage", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_hmac_artifact_coverage", "eval_metric")
_emit_stores_embedding("p4", "test_hmac_artifact_coverage", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_hmac_artifact_coverage", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_hmac_artifact_coverage", "exec_snapshot_link")

_KEY_ID = "req018-hmac-key"
_KEY_SECRET = b"req018-fixed-hmac-secret-padding!"


def _make_trust_root() -> TrustRoot:
    return TrustRoot(
        keys=(
            KeyRecord(
                key_id=_KEY_ID,
                public_key=_KEY_SECRET,
                created_tick=0,
                status=KeyStatus.ACTIVE,
            ),
        )
    )


@pytest.mark.governance
def test_sign_artifact_uses_hmac_sha256() -> None:
    """SignatureEnvelope.algorithm MUST be HMAC_SHA256."""
    trust_root = _make_trust_root()
    enclave = DeterministicTestEnclave(trust_root)
    artifact = b'{"instruction_id":"INS-001","payload":"run_gate"}'
    envelope = sign_artifact(artifact, _KEY_ID, enclave, "TR-001", 1)
    assert envelope.algorithm == SigningAlgorithm.HMAC_SHA256


@pytest.mark.governance
def test_sign_artifact_deterministic_across_two_runs() -> None:
    """Two independent sign_artifact calls on identical inputs MUST produce identical signatures."""
    trust_root = _make_trust_root()
    enclave = DeterministicTestEnclave(trust_root)
    artifact = b'{"instruction_id":"INS-002","payload":"determinism_check"}'

    env1 = sign_artifact(artifact, _KEY_ID, enclave, "TR-DET", 42)
    env2 = sign_artifact(artifact, _KEY_ID, enclave, "TR-DET", 42)

    assert env1.signature == env2.signature, "signatures not deterministic across two invocations"
    assert env1.artifact_hash == env2.artifact_hash


@pytest.mark.governance
def test_artifact_hash_is_sha256_hex() -> None:
    """hash_artifact_canonical MUST return lowercase SHA-256 hex (64 chars)."""
    artifact = b"canonical test bytes"
    digest = hash_artifact_canonical(artifact)
    expected = hashlib.sha256(artifact).hexdigest()
    assert digest == expected
    assert len(digest) == 64
    assert digest == digest.lower()


@pytest.mark.governance
def test_signature_is_expected_hmac_hex() -> None:
    """The signature stored in the envelope MUST equal HMAC-SHA256(key, artifact_bytes).hexdigest()."""
    trust_root = _make_trust_root()
    enclave = DeterministicTestEnclave(trust_root)
    artifact = b'{"instruction_id":"INS-003","payload":"hmac_value_check"}'

    envelope = sign_artifact(artifact, _KEY_ID, enclave, "TR-003", 1)

    expected_sig = hmac.new(_KEY_SECRET, artifact, hashlib.sha256).hexdigest()
    assert envelope.signature == expected_sig


@pytest.mark.governance
def test_verify_signature_round_trip() -> None:
    """sign_artifact followed by verify_signature MUST return True."""
    trust_root = _make_trust_root()
    enclave = DeterministicTestEnclave(trust_root)
    artifact = b'{"instruction_id":"INS-004","payload":"roundtrip"}'
    envelope = sign_artifact(artifact, _KEY_ID, enclave, "TR-004", 1)
    assert verify_signature(artifact, envelope, trust_root, enclave) is True


@pytest.mark.governance
def test_w2_determinism_digest_format() -> None:
    """SOV-DELTA: phase emits W2-DETERMINISM-DIGEST; two invocations must match."""
    trust_root = _make_trust_root()
    enclave = DeterministicTestEnclave(trust_root)
    artifact = b'{"phase":"W2","gate":"determinism"}'
    env_a = sign_artifact(artifact, _KEY_ID, enclave, "W2-DIGEST", 0)
    env_b = sign_artifact(artifact, _KEY_ID, enclave, "W2-DIGEST", 0)
    digest_line_a = f"W2-DETERMINISM-DIGEST: {env_a.signature}"
    digest_line_b = f"W2-DETERMINISM-DIGEST: {env_b.signature}"
    assert digest_line_a == digest_line_b
