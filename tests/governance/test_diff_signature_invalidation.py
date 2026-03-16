"""REQ-087: MODIFY_DIFF must invalidate all prior signatures on the plan artifact."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.enforcement.crypto_trust_contracts import (
    VerificationError,
    sign_artifact,
    verify_signature,
)
from agentic_core.L0_routing.types.crypto_trust_types import (
    DeterministicTestEnclave,
    KeyRecord,
    KeyStatus,
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

_emit_records_execution_trace("p0", "evidence", "test_diff_signature_invalidation")
_emit_applies_guardrail("p0", "test_diff_signature_invalidation", "p0_governance")
_emit_reads_policy_state("p0", "test_diff_signature_invalidation", "policy_binding")
_emit_snapshots_state("p0", "test_diff_signature_invalidation", "state_snapshot")
emit_replay_key("p0", "test_diff_signature_invalidation")
emit_determinism_digest("p0", "test_diff_signature_invalidation")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_diff_signature_invalidation", "execution_auth")
_emit_validates_capability("p2", "test_diff_signature_invalidation", "capability_check")
_emit_routes_to_capability("p2", "test_diff_signature_invalidation", "capability_route")
_emit_writes_via_uwg("p2", "test_diff_signature_invalidation", "uwg_write")
_emit_blocks_direct_write("p2", "test_diff_signature_invalidation", "direct_write_block")
_emit_records_tool_invocation("p2", "test_diff_signature_invalidation", "tool_invocation")
_emit_captures_execution_output("p2", "test_diff_signature_invalidation", "exec_output")
_emit_dispatches_agent("p3", "test_diff_signature_invalidation", "agent_dispatch")
_emit_coordinates_agents("p3", "test_diff_signature_invalidation", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_diff_signature_invalidation", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_diff_signature_invalidation", "healing_outcome")
_emit_escalates_failure("p3", "test_diff_signature_invalidation", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_diff_signature_invalidation", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_diff_signature_invalidation", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_diff_signature_invalidation", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_diff_signature_invalidation", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_diff_signature_invalidation", "eval_metric")
_emit_stores_embedding("p4", "test_diff_signature_invalidation", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_diff_signature_invalidation", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_diff_signature_invalidation", "exec_snapshot_link")

_KEY_ID = "req087-test-key"
_KEY_SECRET = b"req087-fixed-secret-32b-padding!!"


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
def test_modify_diff_invalidates_old_signature() -> None:
    """Old envelope on original bytes MUST raise VerificationError on modified bytes."""
    trust_root = _make_trust_root()
    enclave = DeterministicTestEnclave(trust_root)

    original_bytes = b'{"action":"plan","payload":"initial_plan","trace_id":"REQ087-T1"}'
    envelope = sign_artifact(original_bytes, _KEY_ID, enclave, "REQ087-T1", 1)

    modified_bytes = b'{"action":"plan","payload":"modified_plan","trace_id":"REQ087-T1"}'

    with pytest.raises(VerificationError):
        verify_signature(modified_bytes, envelope, trust_root, enclave)


@pytest.mark.governance
def test_modify_diff_new_signature_verifies() -> None:
    """After MODIFY_DIFF a freshly computed signature MUST verify against modified bytes."""
    trust_root = _make_trust_root()
    enclave = DeterministicTestEnclave(trust_root)

    original_bytes = b'{"action":"plan","payload":"initial_plan","trace_id":"REQ087-T2"}'
    sign_artifact(original_bytes, _KEY_ID, enclave, "REQ087-T2", 1)

    modified_bytes = b'{"action":"plan","payload":"modified_plan","trace_id":"REQ087-T2"}'
    new_envelope = sign_artifact(modified_bytes, _KEY_ID, enclave, "REQ087-T2", 2)

    assert verify_signature(modified_bytes, new_envelope, trust_root, enclave)


@pytest.mark.governance
def test_single_byte_diff_invalidates_signature() -> None:
    """Even a single-byte change MUST invalidate the prior signature (hash avalanche)."""
    trust_root = _make_trust_root()
    enclave = DeterministicTestEnclave(trust_root)

    base = b"plan:version1"
    envelope = sign_artifact(base, _KEY_ID, enclave, "REQ087-T3", 1)

    mutated = b"plan:version2"
    with pytest.raises(VerificationError):
        verify_signature(mutated, envelope, trust_root, enclave)
