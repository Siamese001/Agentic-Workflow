"""
InstructionPacket unit tests -- Phase 1 crypto boundary contracts.

Covers:
- Canonical bytes determinism
- sign -> verify PASS
- Tamper-after-sign triggers verify failure
- Constant-time compare (structural)
- W1-DETERMINISM-DIGEST printed once per run
"""

from __future__ import annotations

import hashlib
import os

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_instruction_packet")
# REMOVED: _emit_applies_guardrail("p0", "test_instruction_packet", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_instruction_packet", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_instruction_packet", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_instruction_packet")
# REMOVED: emit_determinism_digest("p0", "test_instruction_packet")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_instruction_packet", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_instruction_packet", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_instruction_packet", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_instruction_packet", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_instruction_packet", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_instruction_packet", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_instruction_packet", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_instruction_packet", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_instruction_packet", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_instruction_packet", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_instruction_packet", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_instruction_packet", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_instruction_packet", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_instruction_packet", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_instruction_packet", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_instruction_packet", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_instruction_packet", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_instruction_packet", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_instruction_packet", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_instruction_packet", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps

#  # MOVED: from agentic_core.L2_execution.types.instruction_packet_types import (
    InstructionPacket,
    SignatureVerificationError,
)
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

# REMOVED: _emit_emits_metric_event("test_instruction_packet", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_instruction_packet", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_instruction_packet", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_instruction_packet", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_instruction_packet", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_instruction_packet", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_instruction_packet", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_instruction_packet", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_instruction_packet", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_instruction_packet", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_instruction_packet", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_instruction_packet", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_instruction_packet", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_instruction_packet", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_instruction_packet", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_instruction_packet", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_instruction_packet", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_instruction_packet", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_instruction_packet", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_instruction_packet", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_instruction_packet", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_instruction_packet", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_instruction_packet", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_instruction_packet", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_instruction_packet", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_instruction_packet", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_instruction_packet", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_instruction_packet", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_instruction_packet", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_instruction_packet", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_instruction_packet", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_instruction_packet", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_instruction_packet", "write_through")
# REMOVED: _emit_writes_through("p1", "test_instruction_packet", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_instruction_packet", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_instruction_packet", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_instruction_packet", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_instruction_packet", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_instruction_packet", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_instruction_packet", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_instruction_packet", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_instruction_packet", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_instruction_packet", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_instruction_packet", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_instruction_packet", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_instruction_packet", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_instruction_packet", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_instruction_packet", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_instruction_packet")
# REMOVED: _emit_gated_by_confidence("p1", "test_instruction_packet", "confidence_gate")

# ---------------------------------------------------------------------------
# Fixed test vectors (deterministic -- no randomness)
# ---------------------------------------------------------------------------

_SECRET = b"phase1-test-secret-key"

_PACKET_V = InstructionPacket(
    instruction_id="instr-0001",
    payload="apply patch to file.py",
    metadata={"agent": "StructureHealerAgent", "tick": 42},
)


def _make_unsigned_packet() -> InstructionPacket:
    """Construct an InstructionPacket with no signature, bypassing __post_init__."""
    p = InstructionPacket.__new__(InstructionPacket)
    object.__setattr__(p, "instruction_id", "instr-0001")
    object.__setattr__(p, "payload", "apply patch to file.py")
    object.__setattr__(p, "metadata", {"agent": "StructureHealerAgent", "tick": 42})
    object.__setattr__(p, "signature", "")
    object.__setattr__(p, "l5_signature", "")
    object.__setattr__(p, "certification_timestamp", "")
    object.__setattr__(p, "expiration_timestamp", "")
    object.__setattr__(p, "agent_registry_hash", "")
    object.__setattr__(p, "execution_profile_hash", "")
    object.__setattr__(p, "policy_hash", "")
    return p


def _tamper_field(packet: InstructionPacket, **kwargs: object) -> InstructionPacket:
    """Return a copy of packet with fields overridden, bypassing __post_init__."""
    p = InstructionPacket.__new__(InstructionPacket)
    for f in (
        "instruction_id",
        "payload",
        "metadata",
        "signature",
        "l5_signature",
        "certification_timestamp",
        "expiration_timestamp",
        "agent_registry_hash",
        "execution_profile_hash",
        "policy_hash",
    ):
        object.__setattr__(p, f, kwargs.get(f, getattr(packet, f)))
    return p


# ---------------------------------------------------------------------------
# W1-DETERMINISM-DIGEST  (printed once per run)
# ---------------------------------------------------------------------------

_W1_DIGEST_PRINTED = False


def _w1_digest() -> str:
    """SHA256 over canonical bytes of fixed InstructionPacket test vector."""
    raw = _PACKET_V.canonical_bytes()
    return hashlib.sha256(raw).hexdigest()


def _print_w1_digest_once() -> str:
    global _W1_DIGEST_PRINTED
    d = _w1_digest()
    if not _W1_DIGEST_PRINTED:
        print(f"\nW1-DETERMINISM-DIGEST: {d}", flush=True)
        _W1_DIGEST_PRINTED = True
    return d


# ===========================================================================
# Canonical bytes
# ===========================================================================


def test_canonical_bytes_stable():
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L2_execution.types.instruction_packet_types import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        b1 = _PACKET_V.canonical_bytes()
        b2 = _PACKET_V.canonical_bytes()
        assert b1 == b2

    assert b1 == b2


def test_canonical_bytes_compact_separators():
    b = _PACKET_V.canonical_bytes()
    text = b.decode("utf-8")
    # Compact separators: no ", " or ": " (JSON structure has no spaces)
    assert ", " not in text
    assert ": " not in text
    assert "\n" not in text


def test_canonical_bytes_keys_sorted():
    import json

    b = _PACKET_V.canonical_bytes()
    parsed = json.loads(b.decode("utf-8"))
    keys = list(parsed.keys())
    assert keys == sorted(keys)


def test_canonical_bytes_excludes_signature():
    unsigned = _make_unsigned_packet()
    signed = unsigned.sign(_SECRET)
    # Signing must NOT affect canonical bytes (signature excluded from surface)
    assert signed.canonical_bytes() == unsigned.canonical_bytes()


# ===========================================================================
# Sign -> verify round-trip
# ===========================================================================


def test_sign_returns_new_instance():
    unsigned = _make_unsigned_packet()
    signed = unsigned.sign(_SECRET)
    assert signed is not unsigned


def test_sign_sets_signature():
    unsigned = _make_unsigned_packet()
    signed = unsigned.sign(_SECRET)
    assert signed.signature != ""
    assert len(signed.signature) == 64  # SHA256 hex


def test_sign_signature_is_lowercase_hex():
    unsigned = _make_unsigned_packet()
    signed = unsigned.sign(_SECRET)
    assert signed.signature == signed.signature.lower()
    assert all(c in "0123456789abcdef" for c in signed.signature)


def test_sign_verify_pass():
"""Test sign_verify_pass contract compliance."""
# Arrange
# TODO: Set up contract test scenario
test_scenario = {}  # Replace with actual test scenario

# Act
# TODO: Execute contract test
contract_result = None  # Replace with actual contract test

# Assert - General Contract
assert contract_result is not None, "Contract should produce a result"
assert isinstance(contract_result, object), "Result should be an object"
# TODO: Add specific contract assertions
"""Test unsigned_packet_verify_raises contract compliance."""
# Arrange
# TODO: Set up contract test scenario
test_scenario = {}  # Replace with actual test scenario

# Act
# TODO: Execute contract test
contract_result = None  # Replace with actual contract test

# Assert - General Contract
assert contract_result is not None, "Contract should produce a result"
"""Test tamper_payload_fails_verify contract compliance."""
# Arrange
# TODO: Set up contract test scenario
test_scenario = {}  # Replace with actual test scenario

# Act
# TODO: Execute contract test
contract_result = None  # Replace with actual contract test
"""Test tamper_metadata_fails_verify contract compliance."""
# Arrange
# TODO: Set up contract test scenario
test_scenario = {}  # Replace with actual test scenario

# Act
# TODO: Execute contract test
contract_result = None  # Replace with actual contract test
"""Test wrong_key_fails_verify contract compliance."""
# Arrange
# TODO: Set up contract test scenario
test_scenario = {}  # Replace with actual test scenario

# Act
# TODO: Execute contract test
"""Test tamper_signature_directly_fails_verify contract compliance."""
# Arrange
# TODO: Set up contract test scenario
test_scenario = {}  # Replace with actual test scenario

# Act
# TODO: Execute contract test
contract_result = None  # Replace with actual contract test

# Assert - General Contract
assert contract_result is not None, "Contract should produce a result"
assert isinstance(contract_result, object), "Result should be an object"
# TODO: Add specific contract assertions
# assert hasattr(contract_result, "complies"), "Result should indicate compliance"
    assert unsigned.is_signed is False


def test_is_signed_true_after_sign():
    unsigned = _make_unsigned_packet()
    signed = unsigned.sign(_SECRET)
    assert signed.is_signed is True


# ===========================================================================
# Frozen dataclass (immutability)
# ===========================================================================


def test_packet_is_immutable():
    with pytest.raises((AttributeError, TypeError)):
        _PACKET_V.payload = "mutated"  # type: ignore[misc]


# ===========================================================================
# W1-DETERMINISM-DIGEST
# ===========================================================================


def test_w1_determinism_digest_stable():
    d1 = _w1_digest()
    d2 = _w1_digest()
    assert d1 == d2
    assert len(d1) == 64


def test_w1_determinism_digest_printed():
    d = _print_w1_digest_once()
    assert len(d) == 64
    assert all(c in "0123456789abcdef" for c in d)


# ===========================================================================
# Negative Control  (W1_NEGCTRL_TAMPER=1)
# ===========================================================================


def test_negative_control_tamper_instruction_packet():
    """
    W1_NEGCTRL_TAMPER=1 -> sign then tamper payload, assert verify raises,
                           then pytest.xfail() -> XFAIL exit-0.
    No env var           -> normal path: sign+verify passes (PASS).
    """
    if os.environ.get("W1_NEGCTRL_TAMPER") == "1":
        unsigned = _make_unsigned_packet()
        signed = unsigned.sign(_SECRET)
        tampered = _tamper_field(signed, payload="W1_NEGCTRL tampered payload")
        try:
            tampered.verify(_SECRET)
            pytest.fail("Expected SignatureVerificationError was not raised")
        except SignatureVerificationError:  # guardian: allow-silent-swallower
            pass  # violation confirmed
        pytest.xfail("W1_NEGCTRL_TAMPER=1: InstructionPacket tamper detected correctly -- XFAIL")
    else:
        unsigned = _make_unsigned_packet()
        signed = unsigned.sign(_SECRET)
        signed.verify(_SECRET)  # must pass
