"""W15: CognitiveDiff compares cryptographically sealed execution trace; advisory diff without trusted trace rejected.

REQ-211/236: CognitiveDiff must compare against a cryptographically sealed
(signed) execution trace. Advisory diff without a trusted trace baseline is rejected.
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

_GUARDIAN_SECRET = b"guardian-cognitive-diff-secret!!"


def _sign_trace(trace_bytes: bytes) -> bytes:
    return hmac.new(_GUARDIAN_SECRET, trace_bytes, hashlib.sha256).digest()


def _verify_trace(trace_bytes: bytes, sig: bytes) -> bool:
    expected = hmac.new(_GUARDIAN_SECRET, trace_bytes, hashlib.sha256).digest()
    return hmac.compare_digest(expected, sig)


# ---------------------------------------------------------------------------
# Sealed execution trace
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SealedExecutionTrace:
    trace_id: str
    canonical_bytes: bytes
    guardian_signature: bytes

    @classmethod
    def seal(cls, trace_id: str, canonical_bytes: bytes) -> SealedExecutionTrace:
        sig = _sign_trace(canonical_bytes)
        return cls(trace_id=trace_id, canonical_bytes=canonical_bytes, guardian_signature=sig)

    def verify(self) -> bool:
        return _verify_trace(self.canonical_bytes, self.guardian_signature)

    @property
    def trace_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes).hexdigest()


# ---------------------------------------------------------------------------
# CognitiveDiff comparator
# ---------------------------------------------------------------------------


class CognitiveDiffError(ValueError):
    pass


@dataclass(frozen=True)
class CognitiveDiffResult:
    diff_id: str
    trusted_trace_hash: str
    current_trace_hash: str
    is_match: bool
    mismatch_reason: str | None


class CognitiveDiffComparator:
    """Compare current execution trace against cryptographically sealed trusted trace."""

    def compare(
        self,
        trusted: SealedExecutionTrace,
        current_bytes: bytes,
    ) -> CognitiveDiffResult:
        """Compare current trace against trusted sealed trace.

        Raises CognitiveDiffError if trusted trace signature invalid.
        """
        if not trusted.verify():
            raise CognitiveDiffError(
                f"Trusted trace '{trusted.trace_id}' has invalid guardian signature — "
                "cannot perform cognitive diff"
            )

        current_hash = hashlib.sha256(current_bytes).hexdigest()
        is_match = current_hash == trusted.trace_hash
        reason = (
            None if is_match else f"Hash mismatch: {current_hash[:16]}... != {trusted.trace_hash[:16]}..."
        )

        return CognitiveDiffResult(
            diff_id=f"diff_{trusted.trace_id}",
            trusted_trace_hash=trusted.trace_hash,
            current_trace_hash=current_hash,
            is_match=is_match,
            mismatch_reason=reason,
        )

    def compare_advisory(
        self,
        trusted: SealedExecutionTrace | None,
        current_bytes: bytes,
    ) -> CognitiveDiffResult:
        """Advisory diff — rejected if no trusted trace provided."""
        if trusted is None:
            raise CognitiveDiffError(
                "Advisory cognitive diff rejected: no trusted sealed trace baseline provided"
            )
        return self.compare(trusted, current_bytes)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def comparator() -> CognitiveDiffComparator:
    return CognitiveDiffComparator()


@pytest.fixture()
def trusted_trace() -> SealedExecutionTrace:
    return SealedExecutionTrace.seal("trace_001", b"canonical execution trace bytes run1")


@pytest.mark.governance
def test_cognitive_diff_match_identical_traces(comparator, trusted_trace):
    """Identical current trace matches trusted sealed trace."""
    result = comparator.compare(trusted_trace, b"canonical execution trace bytes run1")
    assert result.is_match is True
    assert result.mismatch_reason is None


@pytest.mark.governance
def test_cognitive_diff_mismatch_detected(comparator, trusted_trace):
    """Different current trace produces mismatch in CognitiveDiff."""
    result = comparator.compare(trusted_trace, b"DIFFERENT execution trace bytes")
    assert result.is_match is False
    assert result.mismatch_reason is not None


@pytest.mark.governance
def test_cognitive_diff_invalid_guardian_sig_rejected(comparator):
    """CognitiveDiff rejects trusted trace with invalid guardian signature."""
    tampered = SealedExecutionTrace(
        trace_id="trace_tampered",
        canonical_bytes=b"original bytes",
        guardian_signature=b"\x00" * 32,  # invalid
    )
    with pytest.raises(CognitiveDiffError, match="invalid guardian signature"):
        comparator.compare(tampered, b"original bytes")


@pytest.mark.governance
def test_cognitive_diff_advisory_without_trusted_rejected(comparator):
    """REQ-211: Advisory diff without trusted trace is rejected."""
    with pytest.raises(CognitiveDiffError, match="no trusted sealed trace"):
        comparator.compare_advisory(None, b"some trace bytes")


@pytest.mark.governance
def test_cognitive_diff_advisory_with_trusted_passes(comparator, trusted_trace):
    """Advisory diff with valid trusted trace succeeds."""
    result = comparator.compare_advisory(trusted_trace, b"canonical execution trace bytes run1")
    assert result.is_match is True


@pytest.mark.governance
def test_sealed_trace_verify_deterministic(trusted_trace):
    """Sealed trace verify() is deterministic across calls."""
    assert trusted_trace.verify() is True
    assert trusted_trace.verify() is True


@pytest.mark.governance
def test_cognitive_diff_result_is_frozen():
    """CognitiveDiffResult is immutable after creation."""
    r = CognitiveDiffResult(
        diff_id="d1",
        trusted_trace_hash="a" * 64,
        current_trace_hash="b" * 64,
        is_match=False,
        mismatch_reason="test",
    )
    with pytest.raises((AttributeError, TypeError)):
        r.is_match = True  # type: ignore[misc]
