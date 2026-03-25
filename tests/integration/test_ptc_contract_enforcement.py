"""
PTC Runtime Contract Enforcement tests -- Phase 1 (Item 41).

Covers:
- pre_execute: unsigned envelope rejected
- pre_execute: signed envelope accepted
- pre_execute: tampered envelope rejected
- post_execute: output within cap passes
- post_execute: output exceeding cap raises PTCBytesCapExceeded
- redact_output: deterministic redaction patterns
- violation_count tracking
"""

from __future__ import annotations

import os

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_ptc_contract_enforcement")
# REMOVED: _emit_applies_guardrail("p0", "test_ptc_contract_enforcement", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_ptc_contract_enforcement", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_ptc_contract_enforcement", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_ptc_contract_enforcement")
# REMOVED: emit_determinism_digest("p0", "test_ptc_contract_enforcement")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_ptc_contract_enforcement", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_ptc_contract_enforcement", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_ptc_contract_enforcement", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_ptc_contract_enforcement", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_ptc_contract_enforcement", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_ptc_contract_enforcement", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_ptc_contract_enforcement", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_ptc_contract_enforcement", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_ptc_contract_enforcement", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_ptc_contract_enforcement", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_ptc_contract_enforcement", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_ptc_contract_enforcement", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_ptc_contract_enforcement", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_ptc_contract_enforcement", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_ptc_contract_enforcement", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_ptc_contract_enforcement", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_ptc_contract_enforcement", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_ptc_contract_enforcement", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_ptc_contract_enforcement", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_ptc_contract_enforcement", "exec_snapshot_link")

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

from agentic_core.L2_execution.tools.ptc_contract import (
    PTC_STDOUT_BYTE_CAP,
    PTCBytesCapExceeded,
    PTCContractEnforcer,
    PTCContractViolation,
    PTCUnsignedEnvelopeError,
    redact_output,
)
from agentic_core.L2_execution.types.sandbox_envelope_types import SandboxEnvelope
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_ptc_contract_enforcement", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_ptc_contract_enforcement", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_ptc_contract_enforcement", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_ptc_contract_enforcement", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_ptc_contract_enforcement", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_ptc_contract_enforcement", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_ptc_contract_enforcement", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_ptc_contract_enforcement", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_ptc_contract_enforcement", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_ptc_contract_enforcement", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_ptc_contract_enforcement", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_ptc_contract_enforcement", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_ptc_contract_enforcement", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_ptc_contract_enforcement", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_ptc_contract_enforcement", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_ptc_contract_enforcement", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_ptc_contract_enforcement", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_ptc_contract_enforcement", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_ptc_contract_enforcement", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_ptc_contract_enforcement", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_ptc_contract_enforcement", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_ptc_contract_enforcement", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_ptc_contract_enforcement", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_ptc_contract_enforcement", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_ptc_contract_enforcement", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_ptc_contract_enforcement", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_ptc_contract_enforcement", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_ptc_contract_enforcement", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_ptc_contract_enforcement", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_ptc_contract_enforcement", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_ptc_contract_enforcement", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_ptc_contract_enforcement", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_ptc_contract_enforcement", "write_through")
# REMOVED: _emit_writes_through("p1", "test_ptc_contract_enforcement", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_ptc_contract_enforcement", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_ptc_contract_enforcement", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_ptc_contract_enforcement", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_ptc_contract_enforcement", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_ptc_contract_enforcement", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_ptc_contract_enforcement", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_ptc_contract_enforcement", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_ptc_contract_enforcement", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_ptc_contract_enforcement", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_ptc_contract_enforcement", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_ptc_contract_enforcement", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_ptc_contract_enforcement", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_ptc_contract_enforcement", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_ptc_contract_enforcement", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_ptc_contract_enforcement")
# REMOVED: _emit_gated_by_confidence("p1", "test_ptc_contract_enforcement", "confidence_gate")

# ---------------------------------------------------------------------------
# Fixed test vectors
# ---------------------------------------------------------------------------

_SECRET = b"phase1-test-secret-key"

_ENVELOPE_V = SandboxEnvelope(
    envelope_id="ptc-env-0001",
    tool_name="ptc_tool",
    tool_args={"prompt": "write hello world"},
    instruction_packet_id="instr-0001",
    invocation_metadata={"agent": "PTCAgent", "tick": 7},
)


def _make_unsigned_envelope(**overrides) -> SandboxEnvelope:
    """Construct a SandboxEnvelope with empty signature, bypassing __post_init__."""
    from agentic_core.L2_execution.types.sandbox_envelope_types import ToolBudget

    e = SandboxEnvelope.__new__(SandboxEnvelope)
    object.__setattr__(e, "envelope_id", overrides.get("envelope_id", "ptc-env-0001"))
    object.__setattr__(e, "tool_name", overrides.get("tool_name", "ptc_tool"))
    object.__setattr__(e, "tool_args", overrides.get("tool_args", {"prompt": "write hello world"}))
    object.__setattr__(e, "instruction_packet_id", overrides.get("instruction_packet_id", "instr-0001"))
    object.__setattr__(
        e, "invocation_metadata", overrides.get("invocation_metadata", {"agent": "PTCAgent", "tick": 7})
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


# ===========================================================================
# Constants
# ===========================================================================


def test_ptc_stdout_byte_cap_positive():
    assert PTC_STDOUT_BYTE_CAP > 0


def test_ptc_stdout_byte_cap_value():
    assert PTC_STDOUT_BYTE_CAP == 65_536


# ===========================================================================
# PTCContractEnforcer construction
# ===========================================================================


def test_enforcer_rejects_empty_secret():
    with pytest.raises(ValueError, match="non-empty"):
        PTCContractEnforcer(secret=b"")


def test_enforcer_rejects_zero_byte_cap():
    with pytest.raises(ValueError, match="positive"):
        PTCContractEnforcer(secret=_SECRET, byte_cap=0)


def test_enforcer_rejects_negative_byte_cap():
    with pytest.raises(ValueError, match="positive"):
        PTCContractEnforcer(secret=_SECRET, byte_cap=-1)


# ===========================================================================
# pre_execute -- unsigned rejected
# ===========================================================================


def test_pre_execute_rejects_unsigned_envelope():
    enforcer = PTCContractEnforcer(secret=_SECRET)
    unsigned = _make_unsigned_envelope()
    with pytest.raises(PTCUnsignedEnvelopeError, match="unsigned"):
        enforcer.pre_execute(unsigned)


def test_pre_execute_increments_violation_count_on_unsigned():
    enforcer = PTCContractEnforcer(secret=_SECRET)
    assert enforcer.violation_count == 0
    unsigned = _make_unsigned_envelope()
    with pytest.raises(PTCUnsignedEnvelopeError):
        enforcer.pre_execute(unsigned)
    assert enforcer.violation_count == 1


# ===========================================================================
# pre_execute -- signed accepted
# ===========================================================================


def test_pre_execute_accepts_signed_envelope():
    enforcer = PTCContractEnforcer(secret=_SECRET)
    unsigned = _make_unsigned_envelope()
    signed = unsigned.sign(_SECRET)
    enforcer.pre_execute(signed)  # must not raise
    assert enforcer.violation_count == 0


# ===========================================================================
# pre_execute -- tampered rejected
# ===========================================================================


def test_pre_execute_rejects_tampered_envelope():
    enforcer = PTCContractEnforcer(secret=_SECRET)
    unsigned = _make_unsigned_envelope()
    signed = unsigned.sign(_SECRET)
    tampered = _tamper_envelope(signed, tool_name="evil_tool")
    with pytest.raises(PTCContractViolation):
        enforcer.pre_execute(tampered)
    assert enforcer.violation_count == 1


def test_pre_execute_rejects_wrong_key():
    enforcer = PTCContractEnforcer(secret=b"wrong-key")
    unsigned = _make_unsigned_envelope()
    signed = unsigned.sign(_SECRET)
    with pytest.raises(PTCContractViolation):
        enforcer.pre_execute(signed)


def test_pre_execute_rejects_non_envelope():
    enforcer = PTCContractEnforcer(secret=_SECRET)
    with pytest.raises(TypeError):
        enforcer.pre_execute("not-an-envelope")  # type: ignore[arg-type]


# ===========================================================================
# post_execute -- within cap
# ===========================================================================


def test_post_execute_passes_short_output():
    enforcer = PTCContractEnforcer(secret=_SECRET)
    result = enforcer.post_execute("hello world")
    assert result == "hello world"
    assert enforcer.violation_count == 0


def test_post_execute_passes_output_at_cap():
    enforcer = PTCContractEnforcer(secret=_SECRET, byte_cap=10)
    result = enforcer.post_execute("0123456789")  # exactly 10 bytes
    assert result == "0123456789"


# ===========================================================================
# post_execute -- exceeds cap
# ===========================================================================


def test_post_execute_rejects_output_over_cap():
    enforcer = PTCContractEnforcer(secret=_SECRET, byte_cap=5)
    with pytest.raises(PTCBytesCapExceeded, match="exceeds"):
        enforcer.post_execute("123456")  # 6 bytes > cap 5


def test_post_execute_increments_violation_count_on_cap_exceeded():
    enforcer = PTCContractEnforcer(secret=_SECRET, byte_cap=5)
    with pytest.raises(PTCBytesCapExceeded):
        enforcer.post_execute("123456")
    assert enforcer.violation_count == 1


def test_post_execute_rejects_non_string():
    enforcer = PTCContractEnforcer(secret=_SECRET)
    with pytest.raises(TypeError):
        enforcer.post_execute(12345)  # type: ignore[arg-type]


# ===========================================================================
# Deterministic redaction
# ===========================================================================


def test_redact_api_key():
    raw = "config: api_key=sk-abc123xyz"
    result = redact_output(raw)
    assert "[REDACTED]" in result
    assert "sk-abc123xyz" not in result


def test_redact_secret():
    raw = "secret=mysecret123"
    result = redact_output(raw)
    assert "[REDACTED]" in result
    assert "mysecret123" not in result


def test_redact_password():
    raw = "password: hunter2"
    result = redact_output(raw)
    assert "[REDACTED]" in result
    assert "hunter2" not in result


def test_redact_bearer_token():
    raw = "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.abc"
    result = redact_output(raw)
    assert "[REDACTED]" in result
    assert "eyJhbGciOiJIUzI1NiJ9" not in result


def test_redact_is_deterministic():
    raw = "api_key=my-secret-key token=abc123"
    r1 = redact_output(raw)
    r2 = redact_output(raw)
    assert r1 == r2


def test_redact_clean_text_unchanged():
    raw = "def hello_world():\n    print('hello')"
    result = redact_output(raw)
    assert result == raw


def test_post_execute_redacts_before_cap_check():
    # Output that would contain a secret -- should be redacted
    enforcer = PTCContractEnforcer(secret=_SECRET)
    raw = "api_key=sk-supersecret output=done"
    result = enforcer.post_execute(raw)
    assert "sk-supersecret" not in result
    assert "[REDACTED]" in result


# ===========================================================================
# violation_count
# ===========================================================================


def test_violation_count_starts_at_zero():
    enforcer = PTCContractEnforcer(secret=_SECRET)
    assert enforcer.violation_count == 0


def test_violation_count_accumulates():
    enforcer = PTCContractEnforcer(secret=_SECRET, byte_cap=3)
    unsigned = _make_unsigned_envelope()
    with pytest.raises(PTCUnsignedEnvelopeError):
        enforcer.pre_execute(unsigned)
    with pytest.raises(PTCBytesCapExceeded):
        enforcer.post_execute("1234")
    assert enforcer.violation_count == 2


# ===========================================================================
# Negative Control  (W1_NEGCTRL_TAMPER=1)
# ===========================================================================


def test_negative_control_ptc_tamper():
    """
    W1_NEGCTRL_TAMPER=1 -> sign envelope, tamper it, assert pre_execute raises,
                           then pytest.xfail() -> XFAIL exit-0.
    No env var           -> normal path: signed envelope passes pre_execute (PASS).
    """
    if os.environ.get("W1_NEGCTRL_TAMPER") == "1":
        enforcer = PTCContractEnforcer(secret=_SECRET)
        unsigned = _make_unsigned_envelope()
        signed = unsigned.sign(_SECRET)
        tampered = _tamper_envelope(signed, tool_args={"prompt": "W1_NEGCTRL injected"})
        try:
            enforcer.pre_execute(tampered)
            pytest.fail("Expected PTCContractViolation was not raised")
        except PTCContractViolation:  # guardian: allow-silent-swallower
            pass  # violation confirmed
        pytest.xfail("W1_NEGCTRL_TAMPER=1: PTC tampered envelope rejected correctly -- XFAIL")
    else:
        enforcer = PTCContractEnforcer(secret=_SECRET)
        unsigned = _make_unsigned_envelope()
        signed = unsigned.sign(_SECRET)
        enforcer.pre_execute(signed)  # must pass
        result = enforcer.post_execute("safe output")
        assert result == "safe output"
