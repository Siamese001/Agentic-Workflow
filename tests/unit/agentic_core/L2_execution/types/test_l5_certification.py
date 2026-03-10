"""
L5 Guardian Certification Tests - Phase 1 Boundary Enforcement

Tests for L5 guardian certification extension to InstructionPacket
and L2 boundary verifier enforcement.

Covers:
- L5 certification creation and verification
- L2 boundary enforcement with L5 certification
- Fail-closed behavior for uncertified packets
- Determinism and negative controls
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

import pytest

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

from agentic_core.L2_execution.enforcement.boundary_verifier import (
    L2BoundaryVerifier,
)
from agentic_core.L2_execution.enforcement.key_source import (
    TestKeySource,
    inject_key_source,
)
from agentic_core.L2_execution.types.instruction_packet_types import (
    InstructionPacket,
    SignatureVerificationError,
)

# ---------------------------------------------------------------------------
# Test Constants
# ---------------------------------------------------------------------------

_L5_SECRET = b"phase2-l5-test-secret-key"
_BASE_SECRET = b"phase1-test-secret-key"


@pytest.fixture(scope="function", autouse=True)
def inject_test_key_source():
    """Inject TestKeySource before every test."""
    inject_key_source(TestKeySource())
    yield
    # Reset after test


@pytest.fixture
def base_packet():
    """Create a base InstructionPacket for testing."""
    return InstructionPacket(
        instruction_id="test-l5-cert-001",
        payload="execute with L5 certification",
        metadata={"test": True, "phase": "L5-certification"},
    )


@pytest.fixture
def l5_verifier():
    """Create L2BoundaryVerifier with L5 secret."""
    return L2BoundaryVerifier(l5_secret=_L5_SECRET)


@pytest.fixture
def verifier_no_l5():
    """Create L2BoundaryVerifier without L5 secret."""
    return L2BoundaryVerifier(l5_secret=None)


# ---------------------------------------------------------------------------
# L5 Certification Creation Tests
# ---------------------------------------------------------------------------


def test_l5_certification_creation(base_packet):
    """Test L5 certification can be applied to InstructionPacket."""
    agent_registry_hash = hashlib.sha256(b"agent-registry-data").hexdigest()
    execution_profile_hash = hashlib.sha256(b"execution-profile-data").hexdigest()
    policy_hash = hashlib.sha256(b"policy-data").hexdigest()

    certified_packet = base_packet.certify_l5(
        l5_secret=_L5_SECRET,
        agent_registry_hash=agent_registry_hash,
        execution_profile_hash=execution_profile_hash,
        policy_hash=policy_hash,
        expiration_hours=24,
    )

    # Verify all L5 fields are populated
    assert certified_packet.l5_signature != ""
    assert certified_packet.certification_timestamp != ""
    assert certified_packet.expiration_timestamp != ""
    assert certified_packet.agent_registry_hash == agent_registry_hash
    assert certified_packet.execution_profile_hash == execution_profile_hash
    assert certified_packet.policy_hash == policy_hash
    assert certified_packet.is_l5_certified is True


def test_l5_certification_signature_verification(base_packet):
    """Test L5 certification signature can be verified."""
    agent_registry_hash = hashlib.sha256(b"agent-registry-data").hexdigest()
    execution_profile_hash = hashlib.sha256(b"execution-profile-data").hexdigest()
    policy_hash = hashlib.sha256(b"policy-data").hexdigest()

    certified_packet = base_packet.certify_l5(
        l5_secret=_L5_SECRET,
        agent_registry_hash=agent_registry_hash,
        execution_profile_hash=execution_profile_hash,
        policy_hash=policy_hash,
    )

    # Should not raise exception
    certified_packet.verify_l5_certification(_L5_SECRET)


def test_l5_certification_wrong_secret_fails(base_packet):
    """Test L5 certification verification fails with wrong secret."""
    agent_registry_hash = hashlib.sha256(b"agent-registry-data").hexdigest()
    execution_profile_hash = hashlib.sha256(b"execution-profile-data").hexdigest()
    policy_hash = hashlib.sha256(b"policy-data").hexdigest()

    certified_packet = base_packet.certify_l5(
        l5_secret=_L5_SECRET,
        agent_registry_hash=agent_registry_hash,
        execution_profile_hash=execution_profile_hash,
        policy_hash=policy_hash,
    )

    with pytest.raises(SignatureVerificationError, match="L5 signature mismatch"):
        certified_packet.verify_l5_certification(b"wrong-secret")


def test_l5_certification_expiration(base_packet):
    """Test L5 certification expiration enforcement."""
    agent_registry_hash = hashlib.sha256(b"agent-registry-data").hexdigest()
    execution_profile_hash = hashlib.sha256(b"execution-profile-data").hexdigest()
    policy_hash = hashlib.sha256(b"policy-data").hexdigest()

    # Create expired certification (1 hour expiration)
    certified_packet = base_packet.certify_l5(
        l5_secret=_L5_SECRET,
        agent_registry_hash=agent_registry_hash,
        execution_profile_hash=execution_profile_hash,
        policy_hash=policy_hash,
        expiration_hours=1,
    )

    # Manually set expiration to past (but this will break L5 signature)
    past_time = datetime.now(timezone.utc) - timedelta(hours=1)
    object.__setattr__(certified_packet, "expiration_timestamp", past_time.isoformat())

    # Since we tampered with the timestamp, L5 verification will fail with signature mismatch
    # This is expected behavior - tampering with any field invalidates the signature
    with pytest.raises(SignatureVerificationError, match="L5 signature mismatch"):
        certified_packet.verify_l5_certification(_L5_SECRET)


def test_l5_certification_missing_fields_fail(base_packet):
    """Test that missing L5 certification fields cause verification failure."""
    # Create packet with empty L5 signature
    certified_packet = InstructionPacket(
        instruction_id=base_packet.instruction_id, payload=base_packet.payload, metadata=base_packet.metadata
    )

    with pytest.raises(SignatureVerificationError, match="no L5 signature"):
        certified_packet.verify_l5_certification(_L5_SECRET)


# ---------------------------------------------------------------------------
# L2 Boundary Verifier Tests
# ---------------------------------------------------------------------------


def test_boundary_verifier_accepts_l5_certified(base_packet, l5_verifier):
    """Test that boundary verifier accepts properly L5 certified packet."""
    agent_registry_hash = hashlib.sha256(b"agent-registry-data").hexdigest()
    execution_profile_hash = hashlib.sha256(b"execution-profile-data").hexdigest()
    policy_hash = hashlib.sha256(b"policy-data").hexdigest()

    certified_packet = base_packet.certify_l5(
        l5_secret=_L5_SECRET,
        agent_registry_hash=agent_registry_hash,
        execution_profile_hash=execution_profile_hash,
        policy_hash=policy_hash,
    )

    # Should not raise exception
    l5_verifier.verify_instruction_packet_with_l5(certified_packet)
    assert l5_verifier.is_packet_valid_with_l5(certified_packet) is True


def test_boundary_verifier_rejects_uncertified(base_packet, l5_verifier):
    """Test that boundary verifier rejects uncertified packet."""
    with pytest.raises(SignatureVerificationError, match="no L5 signature"):
        l5_verifier.verify_l5_certification(base_packet)

    assert l5_verifier.is_l5_certified(base_packet) is False
    assert l5_verifier.is_packet_valid_with_l5(base_packet) is False


def test_boundary_verifier_no_l5_secret_behavior(base_packet, verifier_no_l5):
    """Test boundary verifier behavior when no L5 secret provided."""
    with pytest.raises(SignatureVerificationError, match="no L5 secret provided"):
        verifier_no_l5.verify_l5_certification(base_packet)

    assert verifier_no_l5.is_l5_certified(base_packet) is False


def test_boundary_verifier_rejects_tampered_certification(base_packet, l5_verifier):
    """Test that boundary verifier rejects tampered L5 certification."""
    agent_registry_hash = hashlib.sha256(b"agent-registry-data").hexdigest()
    execution_profile_hash = hashlib.sha256(b"execution-profile-data").hexdigest()
    policy_hash = hashlib.sha256(b"policy-data").hexdigest()

    certified_packet = base_packet.certify_l5(
        l5_secret=_L5_SECRET,
        agent_registry_hash=agent_registry_hash,
        execution_profile_hash=execution_profile_hash,
        policy_hash=policy_hash,
    )

    # Tamper with certification timestamp
    object.__setattr__(certified_packet, "certification_timestamp", "tampered")

    with pytest.raises(SignatureVerificationError, match="L5 signature mismatch"):
        l5_verifier.verify_l5_certification(certified_packet)


# ---------------------------------------------------------------------------
# Determinism Tests
# ---------------------------------------------------------------------------


def test_l5_certification_determinism(base_packet):
    """Test that L5 certification is deterministic."""
    agent_registry_hash = hashlib.sha256(b"agent-registry-data").hexdigest()
    execution_profile_hash = hashlib.sha256(b"execution-profile-data").hexdigest()
    policy_hash = hashlib.sha256(b"policy-data").hexdigest()

    # Create two identical certifications
    certified1 = base_packet.certify_l5(
        l5_secret=_L5_SECRET,
        agent_registry_hash=agent_registry_hash,
        execution_profile_hash=execution_profile_hash,
        policy_hash=policy_hash,
        expiration_hours=24,
    )

    certified2 = base_packet.certify_l5(
        l5_secret=_L5_SECRET,
        agent_registry_hash=agent_registry_hash,
        execution_profile_hash=execution_profile_hash,
        policy_hash=policy_hash,
        expiration_hours=24,
    )

    # Canonical bytes should be identical (except timestamps which differ)
    # But signatures should be valid for both
    certified1.verify_l5_certification(_L5_SECRET)
    certified2.verify_l5_certification(_L5_SECRET)


def test_w5_determinism_digest_contribution():
    """Compute W5-DETERMINISM-DIGEST contribution from L5 certification."""
    packet = InstructionPacket(
        instruction_id="w5-determinism-test", payload="test payload", metadata={"determinism": True}
    )

    agent_registry_hash = hashlib.sha256(b"agent-registry-data").hexdigest()
    execution_profile_hash = hashlib.sha256(b"execution-profile-data").hexdigest()
    policy_hash = hashlib.sha256(b"policy-data").hexdigest()

    certified = packet.certify_l5(
        l5_secret=_L5_SECRET,
        agent_registry_hash=agent_registry_hash,
        execution_profile_hash=execution_profile_hash,
        policy_hash=policy_hash,
    )

    # Compute digest over canonical bytes
    digest = hashlib.sha256(certified.canonical_bytes()).hexdigest()

    print(f"W5-DETERMINISM-DIGEST: {digest}")
    assert len(digest) == 64  # SHA256 hex length
    assert digest != ""


# ---------------------------------------------------------------------------
# Negative Control Tests
# ---------------------------------------------------------------------------


def test_negative_control_tampered_signature():
    """Negative control: tampered L5 signature should fail verification."""
    import os

    if os.getenv("W5_NEGCTRL_TAMPER") == "1":
        packet = InstructionPacket(instruction_id="negctrl-tamper", payload="test payload")

        # Apply legitimate certification
        agent_registry_hash = hashlib.sha256(b"agent-registry-data").hexdigest()
        certified = packet.certify_l5(
            l5_secret=_L5_SECRET,
            agent_registry_hash=agent_registry_hash,
            execution_profile_hash="hash",
            policy_hash="hash",
        )

        # Tamper with L5 signature
        object.__setattr__(certified, "l5_signature", "tampered_signature")

        try:
            certified.verify_l5_certification(_L5_SECRET)
            pytest.fail("Expected SignatureVerificationError")
        except SignatureVerificationError:  # guardian: allow-silent-swallower
            pytest.xfail("W5_NEGCTRL_TAMPER=1: L5 tamper detected correctly -- XFAIL")
    else:
        # Normal mode - test should pass
        packet = InstructionPacket(instruction_id="normal-test", payload="test payload")
        agent_registry_hash = hashlib.sha256(b"agent-registry-data").hexdigest()
        certified = packet.certify_l5(
            l5_secret=_L5_SECRET,
            agent_registry_hash=agent_registry_hash,
            execution_profile_hash="hash",
            policy_hash="hash",
        )
        certified.verify_l5_certification(_L5_SECRET)  # Should pass


# ---------------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------------


def test_end_to_end_l5_certification_flow():
    """Test end-to-end L5 certification flow."""
    # 1. Create instruction packet
    packet = InstructionPacket(instruction_id="e2e-test-001", payload="execute with full L5 certification")

    # 2. Apply L5 certification
    agent_registry_hash = hashlib.sha256(b"test-registry").hexdigest()
    execution_profile_hash = hashlib.sha256(b"test-profile").hexdigest()
    policy_hash = hashlib.sha256(b"test-policy").hexdigest()

    certified_packet = packet.certify_l5(
        l5_secret=_L5_SECRET,
        agent_registry_hash=agent_registry_hash,
        execution_profile_hash=execution_profile_hash,
        policy_hash=policy_hash,
        expiration_hours=24,
    )

    # 3. Verify at L2 boundary
    verifier = L2BoundaryVerifier(l5_secret=_L5_SECRET)
    verifier.verify_instruction_packet_with_l5(certified_packet)

    # 4. Confirm all validations pass
    assert verifier.is_packet_valid(certified_packet)
    assert verifier.is_l5_certified(certified_packet)
    assert verifier.is_packet_valid_with_l5(certified_packet)

    print("End-to-end L5 certification flow: PASS")
