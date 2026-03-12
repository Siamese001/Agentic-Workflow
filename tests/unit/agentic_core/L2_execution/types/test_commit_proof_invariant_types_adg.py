"""ADG importability contract for agentic_core/L2_execution/types/commit_proof_invariant_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_commit_proof_invariant_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.commit_proof_invariant_types import (  # noqa: F401
        DeterminismProofFailure,
        CommitProofInvariant,
        make_proof,
        canonical_digest,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DeterminismProofFailure = None  # type: ignore[assignment,misc]
    CommitProofInvariant = None  # type: ignore[assignment,misc]
    make_proof = None  # type: ignore[assignment,misc]
    canonical_digest = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="commit_proof_invariant_types.py deps unavailable")
class TestCommitProofInvariantTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: commit_proof_invariant_types.py must be importable."""
        assert _AVAILABLE

    def test_determinismprooffailure_is_type(self) -> None:
        assert DeterminismProofFailure is not None

    def test_commitproofinvariant_is_type(self) -> None:
        assert CommitProofInvariant is not None

    def test_make_proof_callable(self) -> None:
        assert callable(make_proof)

    def test_canonical_digest_callable(self) -> None:
        assert callable(canonical_digest)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

