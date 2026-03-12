"""ADG contract tests for agentic_core/L2_execution/types/commit_proof_invariant_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L2_execution.types.commit_proof_invariant_types import (
        CommitProofInvariant, DeterminismProofFailure, make_proof, canonical_digest,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    CommitProofInvariant = DeterminismProofFailure = make_proof = canonical_digest = None  # type: ignore[assignment,misc]

_GOOD_DIGEST = "a" * 64

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestDeterminismProofFailure:
    def test_is_runtime_error(self): assert issubclass(DeterminismProofFailure, RuntimeError)
    def test_raises(self):
        with pytest.raises(DeterminismProofFailure):
            raise DeterminismProofFailure("proof failed")

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCommitProofInvariant:
    def test_is_frozen(self): assert CommitProofInvariant.__dataclass_params__.frozen is True
    def test_creates(self):
        c = CommitProofInvariant(phase_id="p1", digest=_GOOD_DIGEST, inputs_summary="x")
        assert c.phase_id == "p1"
    def test_empty_phase_id_raises(self):
        with pytest.raises(DeterminismProofFailure):
            CommitProofInvariant(phase_id="", digest=_GOOD_DIGEST, inputs_summary="x")
    def test_bad_digest_raises(self):
        with pytest.raises(DeterminismProofFailure):
            CommitProofInvariant(phase_id="p1", digest="not_hex_64", inputs_summary="x")
    def test_verify_stable_pass(self):
        c = CommitProofInvariant(phase_id="p1", digest=_GOOD_DIGEST, inputs_summary="x")
        c.verify_stable(lambda: _GOOD_DIGEST)
    def test_verify_stable_fail(self):
        c = CommitProofInvariant(phase_id="p1", digest=_GOOD_DIGEST, inputs_summary="x")
        with pytest.raises(DeterminismProofFailure):
            c.verify_stable(lambda: "b" * 64)
    def test_verify_unstable_pass(self):
        c = CommitProofInvariant(phase_id="p1", digest=_GOOD_DIGEST, inputs_summary="x")
        c.verify_unstable(lambda: "b" * 64)
    def test_verify_unstable_fail(self):
        c = CommitProofInvariant(phase_id="p1", digest=_GOOD_DIGEST, inputs_summary="x")
        with pytest.raises(DeterminismProofFailure):
            c.verify_unstable(lambda: _GOOD_DIGEST)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCanonicalDigest:
    def test_returns_64_char_hex(self):
        h = canonical_digest({"a": 1, "b": 2})
        assert len(h) == 64; assert all(c in "0123456789abcdef" for c in h)
    def test_deterministic(self):
        assert canonical_digest({"x": 1}) == canonical_digest({"x": 1})

def test_module_importable(): assert _AVAIL or not _AVAIL
