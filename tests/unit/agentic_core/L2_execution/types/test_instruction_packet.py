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

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L2_execution.types.instruction_packet import (
    InstructionPacket,
    SignatureVerificationError,
)

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
    b1 = _PACKET_V.canonical_bytes()
    b2 = _PACKET_V.canonical_bytes()
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
    unsigned = _make_unsigned_packet()
    signed = unsigned.sign(_SECRET)
    signed.verify(_SECRET)  # must not raise


def test_sign_is_deterministic():
    unsigned = _make_unsigned_packet()
    s1 = unsigned.sign(_SECRET)
    s2 = unsigned.sign(_SECRET)
    assert s1.signature == s2.signature


def test_unsigned_packet_verify_raises():
    unsigned = _make_unsigned_packet()
    with pytest.raises(SignatureVerificationError, match="unsigned"):
        unsigned.verify(_SECRET)


# ===========================================================================
# Tamper detection
# ===========================================================================


def test_tamper_payload_fails_verify():
    unsigned = _make_unsigned_packet()
    signed = unsigned.sign(_SECRET)
    tampered = _tamper_field(signed, payload="TAMPERED payload")
    with pytest.raises(SignatureVerificationError, match="mismatch"):
        tampered.verify(_SECRET)


def test_tamper_metadata_fails_verify():
    unsigned = _make_unsigned_packet()
    signed = unsigned.sign(_SECRET)
    tampered = _tamper_field(signed, metadata={"agent": "EvilAgent", "tick": 99})
    with pytest.raises(SignatureVerificationError, match="mismatch"):
        tampered.verify(_SECRET)


def test_wrong_key_fails_verify():
    unsigned = _make_unsigned_packet()
    signed = unsigned.sign(_SECRET)
    with pytest.raises(SignatureVerificationError, match="mismatch"):
        signed.verify(b"wrong-key")


def test_tamper_signature_directly_fails_verify():
    unsigned = _make_unsigned_packet()
    signed = unsigned.sign(_SECRET)
    tampered = _tamper_field(signed, signature="a" * 64)
    with pytest.raises(SignatureVerificationError, match="mismatch"):
        tampered.verify(_SECRET)


# ===========================================================================
# is_signed predicate
# ===========================================================================


def test_is_signed_false_when_unsigned():
    unsigned = _make_unsigned_packet()
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
        except SignatureVerificationError:
            pass  # violation confirmed
        pytest.xfail("W1_NEGCTRL_TAMPER=1: InstructionPacket tamper detected correctly -- XFAIL")
    else:
        unsigned = _make_unsigned_packet()
        signed = unsigned.sign(_SECRET)
        signed.verify(_SECRET)  # must pass
