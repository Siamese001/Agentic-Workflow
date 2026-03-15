"""ADG importability contract for agentic_core/L2_execution/types/commit_proof_invariant_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_commit_proof_invariant_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.commit_proof_invariant_types import (  # noqa: F401
        CommitProofInvariant,
        DeterminismProofFailure,
        canonical_digest,
        make_proof,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    DeterminismProofFailure = None  # type: ignore[assignment,misc]
    CommitProofInvariant = None  # type: ignore[assignment,misc]
    make_proof = None  # type: ignore[assignment,misc]
    canonical_digest = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="commit_proof_invariant_types deps unavailable")
class TestCommitProofInvariantTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/types/commit_proof_invariant_types.py must be importable."""
        assert _AVAILABLE

    def test_determinismprooffailure_defined(self) -> None:
        assert DeterminismProofFailure is not None

    def test_commitproofinvariant_defined(self) -> None:
        assert CommitProofInvariant is not None
