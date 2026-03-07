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
        except PTCContractViolation:
            pass  # violation confirmed
        pytest.xfail("W1_NEGCTRL_TAMPER=1: PTC tampered envelope rejected correctly -- XFAIL")
    else:
        enforcer = PTCContractEnforcer(secret=_SECRET)
        unsigned = _make_unsigned_envelope()
        signed = unsigned.sign(_SECRET)
        enforcer.pre_execute(signed)  # must pass
        result = enforcer.post_execute("safe output")
        assert result == "safe output"
