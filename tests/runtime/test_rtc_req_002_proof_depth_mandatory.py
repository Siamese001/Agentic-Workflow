"""RTC-REQ-002 — Proof Depth Fields Mandatory.

Validates that every requirement row has proof depth fields populated
and that the proof depth ladder is correctly ordered.

W0 implementation per runtime-cert-hardened-w0-7e3c9a.md
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.prove_requirements.matrix_loader import load_matrix
from agentic_core.runtime.prove_requirements.proof_depth_ladder import (
    PROOF_DEPTH_ORDER,
    rank_proof_depth,
    is_valid_proof_depth,
)


class TestRTC002ProofDepthMandatory:
    """RTC-REQ-002: Proof depth fields mandatory."""

    def test_all_rows_have_proof_depth(self) -> None:
        """Every requirement has proof_depth field."""
        rows = load_matrix()
        for row in rows:
            assert "proof_depth" in row, f"Row {row.get('req_id', '?')} missing proof_depth"

    def test_proof_depth_not_empty(self) -> None:
        """proof_depth field is non-empty for all rows."""
        rows = load_matrix()
        for row in rows:
            depth = row.get("proof_depth", "").strip()
            assert depth, f"Row {row.get('req_id', '?')} has empty proof_depth"

    def test_proof_depth_valid_values(self) -> None:
        """proof_depth is one of the valid ladder values."""
        rows = load_matrix()
        for row in rows:
            depth = row.get("proof_depth", "")
            assert is_valid_proof_depth(depth), f"Invalid proof_depth '{depth}' for {row.get('req_id', '?')}"


class TestRTC002ProofDepthLadder:
    """Proof depth ladder ordering tests."""

    def test_proof_depth_order_defined(self) -> None:
        """PROOF_DEPTH_ORDER has at least 4 levels."""
        assert len(PROOF_DEPTH_ORDER) >= 4

    def test_rank_proof_depth_returns_int(self) -> None:
        """rank_proof_depth() returns integer rank."""
        for depth in PROOF_DEPTH_ORDER:
            rank = rank_proof_depth(depth)
            assert isinstance(rank, int)

    def test_rank_increases_with_depth(self) -> None:
        """Higher proof depths have higher ranks."""
        ranks = [rank_proof_depth(d) for d in PROOF_DEPTH_ORDER]
        assert ranks == sorted(ranks)

    def test_invalid_depth_returns_none(self) -> None:
        """Invalid proof depth returns None rank."""
        assert rank_proof_depth("invalid_depth") is None


class TestRTC002FailClosedPaths:
    """Fail-closed tests for proof depth validation."""

    def test_empty_proof_depth_invalid(self) -> None:
        """Empty proof_depth is invalid."""
        assert not is_valid_proof_depth("")

    def test_null_proof_depth_invalid(self) -> None:
        """None proof_depth is invalid."""
        assert not is_valid_proof_depth(None)  # type: ignore[arg-type]

    def test_whitespace_only_proof_depth_invalid(self) -> None:
        """Whitespace-only proof_depth is invalid."""
        assert not is_valid_proof_depth("   ")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
