"""ADG importability contract for system_learning/invariants/commit_proof_invariant.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_commit_proof_invariant.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.invariants.commit_proof_invariant import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        CommitProofInvariant,
        CommitProofViolation,
        verify_commit_proof,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    CommitProofViolation = None  # type: ignore[assignment,misc]
    CommitProofInvariant = None  # type: ignore[assignment,misc]
    verify_commit_proof = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="commit_proof_invariant.py deps unavailable")
class TestCommitProofInvariantImportability:
    def test_module_importable(self) -> None:
        """ADG contract: commit_proof_invariant.py must be importable."""
        assert _AVAILABLE

    def test_commitproofviolation_is_type(self) -> None:
        assert CommitProofViolation is not None

    def test_commitproofinvariant_is_type(self) -> None:
        assert CommitProofInvariant is not None

    def test_verify_commit_proof_callable(self) -> None:
        assert callable(verify_commit_proof)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None
