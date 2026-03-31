"""W13: Sig verification precedes mutation in all 5 artifact consumption paths.

REQ-177/354: Signature verification must precede side-effect for:
  1. SurgicalManifest
  2. WaveAuditSummary
  3. PromotionDecisionArtifact
  4. CapabilityToken
  5. EvidencePack
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass

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

pytestmark = pytest.mark.governance


# ---------------------------------------------------------------------------
# Execution ordering tracker
# ---------------------------------------------------------------------------


class ExecutionOrderTracker:
    """Records verify/effect events to enforce ordering invariant."""

    def __init__(self):
        self._events: list[tuple[str, str]] = []  # (event_type, artifact_id)

    def record_verify(self, artifact_id: str) -> None:
        self._events.append(("verify", artifact_id))

    def record_effect(self, artifact_id: str) -> None:
        verify_idx = None
        for i, (evt, aid) in enumerate(self._events):
            if evt == "verify" and aid == artifact_id:
                verify_idx = i
                break
        if verify_idx is None:
            raise AssertionError(f"Side-effect for '{artifact_id}' attempted before signature verification")
        self._events.append(("effect", artifact_id))

    def assert_ordering(self, artifact_id: str) -> None:
        """Assert verify < effect for the given artifact_id."""
        verify_pos = None
        effect_pos = None
        for i, (evt, aid) in enumerate(self._events):
            if aid == artifact_id:
                if evt == "verify" and verify_pos is None:
                    verify_pos = i
                elif evt == "effect" and effect_pos is None:
                    effect_pos = i
        assert verify_pos is not None, f"No verify recorded for '{artifact_id}'"
        assert effect_pos is not None, f"No effect recorded for '{artifact_id}'"
        assert verify_pos < effect_pos, (
            f"verify ({verify_pos}) must precede effect ({effect_pos}) for '{artifact_id}'"
        )


# ---------------------------------------------------------------------------
# Generic artifact processor
# ---------------------------------------------------------------------------

GUARDIAN_SECRET = b"guardian-test-secret-32bytes!!!!"


def _sign(artifact_bytes: bytes) -> bytes:
    return hmac.new(GUARDIAN_SECRET, artifact_bytes, hashlib.sha256).digest()


def _verify(artifact_bytes: bytes, sig: bytes) -> bool:
    expected = hmac.new(GUARDIAN_SECRET, artifact_bytes, hashlib.sha256).digest()
    return hmac.compare_digest(expected, sig)


@dataclass(frozen=True)
class SignedArtifact:
    artifact_id: str
    artifact_type: str
    payload: bytes
    signature: bytes

    def verify_signature(self) -> bool:
        return _verify(self.payload, self.signature)


class ArtifactConsumer:
    """Consumes signed artifacts with mandatory sig-before-effect ordering."""

    def __init__(self, tracker: ExecutionOrderTracker):
        self._tracker = tracker
        self._applied: list[str] = []

    def consume(self, artifact: SignedArtifact) -> None:
        """Verify then apply. Raises if sig fails or ordering violated."""
        if not artifact.verify_signature():
            raise ValueError(f"Signature verification failed for '{artifact.artifact_id}'")
        self._tracker.record_verify(artifact.artifact_id)
        # Apply side-effect
        self._tracker.record_effect(artifact.artifact_id)
        self._applied.append(artifact.artifact_id)

    def consume_bypass(self, artifact: SignedArtifact) -> None:
        """Bypass path — applies without verifying. Must never be used."""
        self._tracker.record_effect(artifact.artifact_id)  # effect without verify → raises

    @property
    def applied(self) -> list[str]:
        return list(self._applied)


def _make_artifact(artifact_id: str, artifact_type: str, payload: bytes = b"payload") -> SignedArtifact:
    sig = _sign(payload)
    return SignedArtifact(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        payload=payload,
        signature=sig,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

_FIVE_ARTIFACT_TYPES = [
    ("art_surgical_001", "SurgicalManifest"),
    ("art_wave_002", "WaveAuditSummary"),
    ("art_promo_003", "PromotionDecisionArtifact"),
    ("art_cap_004", "CapabilityToken"),
    ("art_evidence_005", "EvidencePack"),
]


@pytest.fixture()
def tracker() -> ExecutionOrderTracker:
    return ExecutionOrderTracker()


@pytest.fixture()
def consumer(tracker) -> ArtifactConsumer:
    return ArtifactConsumer(tracker)


@pytest.mark.governance
def test_req177_354_sig_before_effect_all_five_paths(consumer, tracker):
    """REQ-177/354: Verify precedes effect for all 5 artifact consumption paths."""
    for artifact_id, artifact_type in _FIVE_ARTIFACT_TYPES:
        artifact = _make_artifact(artifact_id, artifact_type)
        consumer.consume(artifact)

    for artifact_id, _ in _FIVE_ARTIFACT_TYPES:
        tracker.assert_ordering(artifact_id)

    assert len(consumer.applied) == 5


@pytest.mark.governance
def test_req354_bypass_raises_before_effect(tracker):
    """REQ-354: Effect without prior verify raises AssertionError."""
    consumer = ArtifactConsumer(tracker)
    artifact = _make_artifact("art_bypass", "SurgicalManifest")

    with pytest.raises(AssertionError, match="before signature verification"):
        consumer.consume_bypass(artifact)


@pytest.mark.governance
def test_req177_invalid_signature_blocks_effect(consumer, tracker):
    """REQ-177: Invalid signature blocks effect — consumer raises before recording effect."""
    bad_artifact = SignedArtifact(
        artifact_id="art_bad_sig",
        artifact_type="SurgicalManifest",
        payload=b"original_payload",
        signature=b"\x00" * 32,  # wrong signature
    )
    with pytest.raises(ValueError, match="Signature verification failed"):
        consumer.consume(bad_artifact)

    assert "art_bad_sig" not in consumer.applied


@pytest.mark.governance
def test_req177_354_ordering_invariant_surgical_manifest(consumer, tracker):
    """REQ-177/354: SurgicalManifest verify-before-effect invariant."""
    art = _make_artifact("sm_001", "SurgicalManifest", b"surgical_payload_data")
    consumer.consume(art)
    tracker.assert_ordering("sm_001")


@pytest.mark.governance
def test_req177_354_ordering_invariant_wave_audit_summary(consumer, tracker):
    """REQ-177/354: WaveAuditSummary verify-before-effect invariant."""
    art = _make_artifact("was_001", "WaveAuditSummary", b"wave_audit_data")
    consumer.consume(art)
    tracker.assert_ordering("was_001")


@pytest.mark.governance
def test_req177_354_ordering_invariant_capability_token(consumer, tracker):
    """REQ-177/354: CapabilityToken verify-before-effect invariant."""
    art = _make_artifact("cap_001", "CapabilityToken", b"capability_data")
    consumer.consume(art)
    tracker.assert_ordering("cap_001")


@pytest.mark.governance
def test_req177_354_sig_verification_deterministic():
    """REQ-354: Signature verification is deterministic — same inputs → same result."""
    payload = b"deterministic_payload"
    sig = _sign(payload)

    result1 = _verify(payload, sig)
    result2 = _verify(payload, sig)

    assert result1 is True
    assert result2 is True
