"""
SandboxEnvelope unit tests -- Phase 1 crypto boundary contracts.

Covers:
- Canonical bytes determinism
- sign -> verify PASS
- Tamper-after-sign triggers verify failure
- L2BoundaryVerifier fail-closed wiring
- W1-DETERMINISM-DIGEST contribution (combined with InstructionPacket vector)
"""

from __future__ import annotations

import hashlib
import os

import pytest

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

_emit_records_execution_trace("p0", "evidence", "test_sandbox_envelope")
_emit_applies_guardrail("p0", "test_sandbox_envelope", "p0_governance")
_emit_reads_policy_state("p0", "test_sandbox_envelope", "policy_binding")
_emit_snapshots_state("p0", "test_sandbox_envelope", "state_snapshot")
emit_replay_key("p0", "test_sandbox_envelope")
emit_determinism_digest("p0", "test_sandbox_envelope")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_sandbox_envelope", "execution_auth")
_emit_validates_capability("p2", "test_sandbox_envelope", "capability_check")
_emit_routes_to_capability("p2", "test_sandbox_envelope", "capability_route")
_emit_writes_via_uwg("p2", "test_sandbox_envelope", "uwg_write")
_emit_blocks_direct_write("p2", "test_sandbox_envelope", "direct_write_block")
_emit_records_tool_invocation("p2", "test_sandbox_envelope", "tool_invocation")
_emit_captures_execution_output("p2", "test_sandbox_envelope", "exec_output")
_emit_dispatches_agent("p3", "test_sandbox_envelope", "agent_dispatch")
_emit_coordinates_agents("p3", "test_sandbox_envelope", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_sandbox_envelope", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_sandbox_envelope", "healing_outcome")
_emit_escalates_failure("p3", "test_sandbox_envelope", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_sandbox_envelope", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_sandbox_envelope", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_sandbox_envelope", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_sandbox_envelope", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_sandbox_envelope", "eval_metric")
_emit_stores_embedding("p4", "test_sandbox_envelope", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_sandbox_envelope", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_sandbox_envelope", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L2_execution.enforcement.boundary_verifier import L2BoundaryVerifier
from agentic_core.L2_execution.types.instruction_packet_types import (
    SignatureVerificationError,
)
from agentic_core.L2_execution.types.sandbox_envelope_types import SandboxEnvelope
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_sandbox_envelope", "p4obs", "metric_1")
_emit_emits_metric_event("test_sandbox_envelope", "p4obs", "metric_2")
_emit_emits_metric_event("test_sandbox_envelope", "p4obs", "metric_3")
_emit_emits_metric_event("test_sandbox_envelope", "p4obs", "metric_4")
_emit_emits_metric_event("test_sandbox_envelope", "p4obs", "metric_5")
_emit_emits_metric_event("test_sandbox_envelope", "p4obs", "metric_6")
_emit_records_incident_event("test_sandbox_envelope", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_sandbox_envelope", "p4obs", "anomaly")
_emit_writes_observability_log("test_sandbox_envelope", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_sandbox_envelope", "p4obs", "mon_state")
_emit_triggers_alert("test_sandbox_envelope", "p4obs", "alert")
_emit_links_incident_trace("test_sandbox_envelope", "p4obs", "trace_link")
_emit_captures_pattern("test_sandbox_envelope", "p3lm", "pattern")
_emit_records_learning_event("test_sandbox_envelope", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_sandbox_envelope", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_sandbox_envelope", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_sandbox_envelope", "p3lm", "routing")
_emit_improves_agent_policy("test_sandbox_envelope", "p3lm", "policy")
_emit_stores_learning_state("test_sandbox_envelope", "p3lm", "state")
_emit_records_execution_trace("test_sandbox_envelope", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_sandbox_envelope", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_sandbox_envelope", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_sandbox_envelope", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_sandbox_envelope", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_sandbox_envelope", "env_read", "p2_env_1")
_emit_reads_environ("test_sandbox_envelope", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_sandbox_envelope", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_sandbox_envelope", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_sandbox_envelope", "context_pull")
_emit_pulls_context("p1", "test_sandbox_envelope", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_sandbox_envelope", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_sandbox_envelope", "uwg_term_2")
_emit_writes_through("p1", "test_sandbox_envelope", "write_through")
_emit_writes_through("p1", "test_sandbox_envelope", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_sandbox_envelope", "safety_validation")
_emit_invokes_eval("p1", "test_sandbox_envelope", "eval_call")
_emit_proposal_commits_routing("p1", "test_sandbox_envelope", "routing_commit")

# ---------------------------------------------------------------------------
# Fixed test vectors
# ---------------------------------------------------------------------------

_SECRET = b"phase1-test-secret-key"

_ENVELOPE_V = SandboxEnvelope(
    envelope_id="env-0001",
    tool_name="write_gateway",
    tool_args={"path": "src/module.py", "content": "# patched"},
    instruction_packet_id="instr-0001",
    invocation_metadata={"agent": "StructureHealerAgent", "tick": 42},
)


def _make_unsigned_envelope(**overrides) -> SandboxEnvelope:
    """Construct a SandboxEnvelope with no signature, bypassing __post_init__."""
    from agentic_core.L2_execution.types.sandbox_envelope_types import ToolBudget

    e = SandboxEnvelope.__new__(SandboxEnvelope)
    object.__setattr__(e, "envelope_id", overrides.get("envelope_id", "env-0001"))
    object.__setattr__(e, "tool_name", overrides.get("tool_name", "write_gateway"))
    object.__setattr__(
        e, "tool_args", overrides.get("tool_args", {"path": "src/module.py", "content": "# patched"})
    )
    object.__setattr__(e, "instruction_packet_id", overrides.get("instruction_packet_id", "instr-0001"))
    object.__setattr__(
        e,
        "invocation_metadata",
        overrides.get("invocation_metadata", {"agent": "StructureHealerAgent", "tick": 42}),
    )
    object.__setattr__(e, "budget", overrides.get("budget", ToolBudget()))
    object.__setattr__(e, "signature", "")
    return e


def _tamper_envelope(env: SandboxEnvelope, **kwargs) -> SandboxEnvelope:
    """Return a copy of env with fields overridden, bypassing __post_init__."""
    e = SandboxEnvelope.__new__(SandboxEnvelope)
    for f in (
        "envelope_id",
        "tool_name",
        "tool_args",
        "instruction_packet_id",
        "invocation_metadata",
        "budget",
        "signature",
    ):
        object.__setattr__(e, f, kwargs.get(f, getattr(env, f)))
    return e


# ---------------------------------------------------------------------------
# W1-DETERMINISM-DIGEST contribution from SandboxEnvelope
# ---------------------------------------------------------------------------

_W1_ENV_DIGEST_PRINTED = False


def _w1_env_digest() -> str:
    return hashlib.sha256(_ENVELOPE_V.canonical_bytes()).hexdigest()


def _print_w1_env_digest_once() -> str:
    global _W1_ENV_DIGEST_PRINTED
    d = _w1_env_digest()
    if not _W1_ENV_DIGEST_PRINTED:
        print(f"\nW1-DETERMINISM-DIGEST: {d}", flush=True)
        _W1_ENV_DIGEST_PRINTED = True
    return d


# ===========================================================================
# Canonical bytes
# ===========================================================================


def test_envelope_canonical_bytes_stable():
    b1 = _ENVELOPE_V.canonical_bytes()
    b2 = _ENVELOPE_V.canonical_bytes()
    assert b1 == b2


def test_envelope_canonical_bytes_compact_separators():
    text = _ENVELOPE_V.canonical_bytes().decode("utf-8")
    assert ", " not in text
    assert ": " not in text
    assert "\n" not in text


def test_envelope_canonical_bytes_keys_sorted():
    import json

    parsed = json.loads(_ENVELOPE_V.canonical_bytes().decode("utf-8"))
    keys = list(parsed.keys())
    assert keys == sorted(keys)


def test_envelope_canonical_bytes_excludes_signature():
    unsigned = _make_unsigned_envelope()
    signed = unsigned.sign(_SECRET)
    assert signed.canonical_bytes() == unsigned.canonical_bytes()


# ===========================================================================
# Sign -> verify round-trip
# ===========================================================================


def test_envelope_sign_returns_new_instance():
    unsigned = _make_unsigned_envelope()
    signed = unsigned.sign(_SECRET)
    assert signed is not unsigned


def test_envelope_sign_sets_lowercase_hex_signature():
    unsigned = _make_unsigned_envelope()
    signed = unsigned.sign(_SECRET)
    assert len(signed.signature) == 64
    assert signed.signature == signed.signature.lower()
    assert all(c in "0123456789abcdef" for c in signed.signature)


def test_envelope_sign_verify_pass():
    unsigned = _make_unsigned_envelope()
    signed = unsigned.sign(_SECRET)
    signed.verify(_SECRET)


def test_envelope_sign_is_deterministic():
    unsigned = _make_unsigned_envelope()
    s1 = unsigned.sign(_SECRET)
    s2 = unsigned.sign(_SECRET)
    assert s1.signature == s2.signature


def test_envelope_unsigned_verify_raises():
    unsigned = _make_unsigned_envelope()
    with pytest.raises(SignatureVerificationError, match="unsigned"):
        unsigned.verify(_SECRET)


# ===========================================================================
# Tamper detection
# ===========================================================================


def test_envelope_tamper_tool_name_fails_verify():
    unsigned = _make_unsigned_envelope()
    signed = unsigned.sign(_SECRET)
    tampered = _tamper_envelope(signed, tool_name="evil_tool")
    with pytest.raises(SignatureVerificationError, match="mismatch"):
        tampered.verify(_SECRET)


def test_envelope_tamper_tool_args_fails_verify():
    unsigned = _make_unsigned_envelope()
    signed = unsigned.sign(_SECRET)
    tampered = _tamper_envelope(signed, tool_args={"path": "/etc/passwd", "content": "evil"})
    with pytest.raises(SignatureVerificationError, match="mismatch"):
        tampered.verify(_SECRET)


def test_envelope_wrong_key_fails_verify():
    unsigned = _make_unsigned_envelope()
    signed = unsigned.sign(_SECRET)
    with pytest.raises(SignatureVerificationError, match="mismatch"):
        signed.verify(b"wrong-key")


def test_envelope_tamper_signature_directly_fails():
    unsigned = _make_unsigned_envelope()
    signed = unsigned.sign(_SECRET)
    tampered = _tamper_envelope(signed, signature="b" * 64)
    with pytest.raises(SignatureVerificationError, match="mismatch"):
        tampered.verify(_SECRET)


# ===========================================================================
# is_signed predicate
# ===========================================================================


def test_envelope_is_signed_false_when_unsigned():
    unsigned = _make_unsigned_envelope()
    assert unsigned.is_signed is False


def test_envelope_is_signed_true_after_sign():
    unsigned = _make_unsigned_envelope()
    assert unsigned.sign(_SECRET).is_signed is True


# ===========================================================================
# Frozen dataclass
# ===========================================================================


def test_envelope_is_immutable():
    with pytest.raises((AttributeError, TypeError)):
        _ENVELOPE_V.tool_name = "mutated"  # type: ignore[misc]


# ===========================================================================
# L2BoundaryVerifier wiring
# ===========================================================================


def test_boundary_verifier_rejects_unsigned_packet():
    verifier = L2BoundaryVerifier(secret=_SECRET)
    from agentic_core.L2_execution.types.instruction_packet_types import InstructionPacket as _IP

    p = _IP.__new__(_IP)
    object.__setattr__(p, "instruction_id", "x")
    object.__setattr__(p, "payload", "y")
    object.__setattr__(p, "metadata", {})
    object.__setattr__(p, "signature", "")
    object.__setattr__(p, "l5_signature", "")
    object.__setattr__(p, "certification_timestamp", "")
    object.__setattr__(p, "expiration_timestamp", "")
    object.__setattr__(p, "agent_registry_hash", "")
    object.__setattr__(p, "execution_profile_hash", "")
    object.__setattr__(p, "policy_hash", "")
    with pytest.raises(SignatureVerificationError):
        verifier.verify_packet(p)


def test_boundary_verifier_rejects_unsigned_envelope():
    verifier = L2BoundaryVerifier(secret=_SECRET)
    unsigned = _make_unsigned_envelope()
    with pytest.raises(SignatureVerificationError):
        verifier.verify_envelope(unsigned)


def test_boundary_verifier_accepts_signed_envelope():
    verifier = L2BoundaryVerifier(secret=_SECRET)
    unsigned = _make_unsigned_envelope()
    signed = unsigned.sign(_SECRET)
    verifier.verify_envelope(signed)  # must not raise


def test_boundary_verifier_accepts_signed_packet():
    verifier = L2BoundaryVerifier(secret=_SECRET)
    from agentic_core.L2_execution.types.instruction_packet_types import InstructionPacket as _IP

    p = _IP.__new__(_IP)
    object.__setattr__(p, "instruction_id", "instr-0001")
    object.__setattr__(p, "payload", "apply patch")
    object.__setattr__(p, "metadata", {"tick": 1})
    object.__setattr__(p, "signature", "")
    object.__setattr__(p, "l5_signature", "")
    object.__setattr__(p, "certification_timestamp", "")
    object.__setattr__(p, "expiration_timestamp", "")
    object.__setattr__(p, "agent_registry_hash", "")
    object.__setattr__(p, "execution_profile_hash", "")
    object.__setattr__(p, "policy_hash", "")
    signed = p.sign(_SECRET)
    verifier.verify_packet(signed)  # must not raise


def test_boundary_verifier_is_valid_helpers():
    verifier = L2BoundaryVerifier(secret=_SECRET)
    unsigned = _make_unsigned_envelope()
    signed_env = unsigned.sign(_SECRET)
    assert verifier.is_envelope_valid(signed_env) is True
    assert verifier.is_envelope_valid(unsigned) is False


def test_boundary_verifier_rejects_empty_secret():
    with pytest.raises(ValueError, match="non-empty"):
        L2BoundaryVerifier(secret=b"")


# ===========================================================================
# W1-DETERMINISM-DIGEST (SandboxEnvelope vector)
# ===========================================================================


def test_w1_env_determinism_digest_stable():
    d1 = _w1_env_digest()
    d2 = _w1_env_digest()
    assert d1 == d2
    assert len(d1) == 64


def test_w1_env_determinism_digest_printed():
    d = _print_w1_env_digest_once()
    assert len(d) == 64


# ===========================================================================
# Negative Control  (W1_NEGCTRL_TAMPER=1)
# ===========================================================================


def test_negative_control_tamper_sandbox_envelope():
    """
    W1_NEGCTRL_TAMPER=1 -> sign then tamper tool_name, assert verify raises,
                           then pytest.xfail() -> XFAIL exit-0.
    No env var           -> normal path: sign+verify passes (PASS).
    """
    if os.environ.get("W1_NEGCTRL_TAMPER") == "1":
        unsigned = _make_unsigned_envelope()
        signed = unsigned.sign(_SECRET)
        tampered = _tamper_envelope(signed, tool_name="W1_NEGCTRL_tampered_tool")
        try:
            tampered.verify(_SECRET)
            pytest.fail("Expected SignatureVerificationError was not raised")
        except SignatureVerificationError:  # guardian: allow-silent-swallower
            pass  # violation confirmed
        pytest.xfail("W1_NEGCTRL_TAMPER=1: SandboxEnvelope tamper detected correctly -- XFAIL")
    else:
        unsigned = _make_unsigned_envelope()
        signed = unsigned.sign(_SECRET)
        signed.verify(_SECRET)  # must pass
