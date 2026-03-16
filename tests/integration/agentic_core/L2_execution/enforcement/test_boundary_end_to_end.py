"""
End-to-End Boundary Enforcement Tests
Phase 2: Signed Boundary Adoption & Key Discipline

Tests real L2 ingress paths with mandatory signing/verification.
"""

import hashlib
import os

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_boundary_end_to_end")
_emit_applies_guardrail("p0", "test_boundary_end_to_end", "p0_governance")
_emit_reads_policy_state("p0", "test_boundary_end_to_end", "policy_binding")
_emit_snapshots_state("p0", "test_boundary_end_to_end", "state_snapshot")
emit_replay_key("p0", "test_boundary_end_to_end")
emit_determinism_digest("p0", "test_boundary_end_to_end")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
from agentic_core.L2_execution.enforcement.key_source import (
    TestKeySource,
    get_key_source,
    inject_key_source,
)
from agentic_core.L2_execution.types.instruction_packet_types import (
    InstructionPacket,
    SignatureVerificationError,
)
from agentic_core.L2_execution.types.sandbox_envelope_types import SandboxEnvelope

# ---------------------------------------------------------------------------
# Test Infrastructure
# ---------------------------------------------------------------------------


def compute_w2_determinism_digest() -> str:
    """Compute deterministic digest over end-to-end test vectors."""
    # Use fixed test vectors for determinism
    packet = InstructionPacket(
        instruction_id="test-instruction-001", payload="test-payload", metadata={"test": True}
    )

    envelope = SandboxEnvelope(
        envelope_id="test-envelope-001",
        tool_name="test_tool",
        tool_args={"arg": "value"},
        instruction_packet_id=packet.instruction_id,
        invocation_metadata={"agent": "test"},
    )

    # Hash both canonical byte representations
    combined = packet.canonical_bytes() + envelope.canonical_bytes()
    return hashlib.sha256(combined).hexdigest()


# ---------------------------------------------------------------------------
# Happy Path Tests
# ---------------------------------------------------------------------------


def test_end_to_end_construct_verify_execute():
    """Test complete construct→verify→execute flow."""
    # Inject test key source
    inject_key_source(TestKeySource())

    # Construct instruction (auto-signed)
    packet = InstructionPacket(
        instruction_id="test-instruction-001", payload="test-payload", metadata={"test": True}
    )

    # Verify instruction is signed
    assert packet.is_signed
    packet.verify(get_key_source().get_secret())

    # Construct envelope (auto-signed)
    envelope = SandboxEnvelope(
        envelope_id="test-envelope-001",
        tool_name="test_tool",
        tool_args={"arg": "value"},
        instruction_packet_id=packet.instruction_id,
        invocation_metadata={"agent": "test"},
    )

    # Verify envelope is signed
    assert envelope.is_signed
    envelope.verify(get_key_source().get_secret())

    # Boundary verifier accepts both
    verifier = L2BoundaryVerifier()
    verifier.verify_instruction_packet(packet)
    verifier.verify_sandbox_envelope(envelope)


def test_mandatory_signing_at_construction():
    """Test that construction always produces signed artifacts."""
    inject_key_source(TestKeySource())

    # InstructionPacket must be signed after construction
    packet = InstructionPacket(instruction_id="mandatory-test", payload="test")
    assert packet.signature != ""
    assert packet.is_signed

    # SandboxEnvelope must be signed after construction
    envelope = SandboxEnvelope(envelope_id="mandatory-envelope", tool_name="test")
    assert envelope.signature != ""
    assert envelope.is_signed


def test_key_source_injection_required():
    """Test that key source must be injected before construction."""
    # Clear any injected key source
    inject_key_source(None)  # type: ignore

    # Construction must fail without injected key source
    with pytest.raises(RuntimeError, match="KeySource not injected"):
        InstructionPacket(instruction_id="fail", payload="test")

    with pytest.raises(RuntimeError, match="KeySource not injected"):
        SandboxEnvelope(envelope_id="fail", tool_name="test")


# ---------------------------------------------------------------------------
# Bypass Attempt Tests (Must Fail)
# ---------------------------------------------------------------------------


def test_bypass_unsigned_packet_rejected():
    """Test that boundary verifier rejects unsigned packets."""
    inject_key_source(TestKeySource())

    # Try to construct with empty signature (bypass attempt)
    # This should not be possible due to __post_init__, but test verifier anyway
    packet = InstructionPacket(instruction_id="bypass-test", payload="test")

    # Tamper with signature to simulate bypass
    object.__setattr__(packet, "signature", "")

    verifier = L2BoundaryVerifier()
    with pytest.raises(SignatureVerificationError):  # Should raise verification error
        verifier.verify_instruction_packet(packet)


def test_bypass_tampered_packet_rejected():
    """Test that boundary verifier rejects tampered packets."""
    inject_key_source(TestKeySource())

    packet = InstructionPacket(instruction_id="tamper-test", payload="original")

    # Tamper with payload after signing
    object.__setattr__(packet, "payload", "tampered")

    verifier = L2BoundaryVerifier()
    with pytest.raises(SignatureVerificationError):  # Should raise verification error
        verifier.verify_instruction_packet(packet)


def test_bypass_unsigned_envelope_rejected():
    """Test that boundary verifier rejects unsigned envelopes."""
    inject_key_source(TestKeySource())

    envelope = SandboxEnvelope(envelope_id="bypass-envelope", tool_name="test")

    # Tamper with signature to simulate bypass
    object.__setattr__(envelope, "signature", "")

    verifier = L2BoundaryVerifier()
    with pytest.raises(SignatureVerificationError):  # Should raise verification error
        verifier.verify_sandbox_envelope(envelope)


def test_bypass_tampered_envelope_rejected():
    """Test that boundary verifier rejects tampered envelopes."""
    inject_key_source(TestKeySource())

    envelope = SandboxEnvelope(envelope_id="tamper-envelope", tool_name="test")

    # Tamper with tool name after signing
    object.__setattr__(envelope, "tool_name", "malicious_tool")

    verifier = L2BoundaryVerifier()
    with pytest.raises(SignatureVerificationError):  # Should raise verification error
        verifier.verify_sandbox_envelope(envelope)


def test_bypass_wrong_key_rejected():
    """Test that wrong secret key is rejected."""
    inject_key_source(TestKeySource())

    packet = InstructionPacket(instruction_id="wrong-key-test", payload="test")

    # Try to verify with wrong key
    wrong_secret = b"wrong-secret-key"
    with pytest.raises(SignatureVerificationError):  # Should raise verification error
        packet.verify(wrong_secret)


# ---------------------------------------------------------------------------
# Determinism Marker
# ---------------------------------------------------------------------------


def test_w2_determinism_digest_printed():
    """Print the W2-DETERMINISM-DIGEST marker exactly once per run."""
    digest = compute_w2_determinism_digest()
    print(f"W2-DETERMINISM-DIGEST: {digest}")

    # Verify digest is stable - compute expected value
    # Using TestKeySource with "phase1-test-secret-key"
    from agentic_core.L2_execution.types.instruction_packet_types import _canonical_bytes

    # Recreate the exact vectors
    packet_dict = {
        "instruction_id": "test-instruction-001",
        "metadata": {"test": True},
        "payload": "test-payload",
    }
    envelope_dict = {
        "budget": {"compute_ms": 5000, "memory_mb": 256, "stdout_bytes": 65536},
        "envelope_id": "test-envelope-001",
        "instruction_packet_id": "test-instruction-001",
        "invocation_metadata": {"agent": "test"},
        "tool_args": {"arg": "value"},
        "tool_name": "test_tool",
    }

    combined = _canonical_bytes(packet_dict) + _canonical_bytes(envelope_dict)
    expected = hashlib.sha256(combined).hexdigest()

    assert digest == expected, f"Determinism digest unstable: {digest} != {expected}"


# ---------------------------------------------------------------------------
# Negative Control Test
# ---------------------------------------------------------------------------


def test_negative_control_bypass_attempt():
    """Negative control: attempt bypass when W2_NEGCTRL_BYPASS=1."""
    if os.environ.get("W2_NEGCTRL_BYPASS") == "1":
        # This should XFAIL - simulate bypass attempt
        inject_key_source(TestKeySource())

        # Create legitimate packet
        packet = InstructionPacket(instruction_id="negctrl-test", payload="test")

        # Simulate bypass by clearing signature
        object.__setattr__(packet, "signature", "")

        # This should fail in bypass mode
        verifier = L2BoundaryVerifier()
        try:
            verifier.verify_instruction_packet(packet)  # Should raise
        except (ValueError, TypeError, AttributeError):
            pytest.xfail("Negative control: bypass attempt correctly failed")
    else:
        # Normal mode - this test should pass
        inject_key_source(TestKeySource())
        packet = InstructionPacket(instruction_id="normal-test", payload="test")
        assert packet.is_signed
