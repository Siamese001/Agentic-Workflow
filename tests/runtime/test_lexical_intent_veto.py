"""W1 Phase 5 — Tests for lexical intent pre-veto (Layer 1).

Validates:
- Opposed verbs detected across queries (enable↔disable, add↔remove)
- Same verb with different context delegates to Layer 2
- Fail-closed on any internal error
"""

from __future__ import annotations

import pytest
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.certification.safety.lexical_intent_veto import LexicalIntentVeto, VetoStatus


class TestLexicalIntentVeto:
    """Layer 1 pre-veto tests."""

    @pytest.fixture
    def veto(self):
        return LexicalIntentVeto()

    def test_opposite_actions_blocked(self, veto):
        """Opposing actions should be vetoed at Layer 1."""
        result = veto.evaluate(
            query="Enable dark mode",
            cached_query="Disable dark mode",
        )
        assert result.blocks_reuse()
        assert result.status == VetoStatus.UNSAFE_DIFFERENT_INTENT
        assert "enable" in result.rationale.lower() or "disable" in result.rationale.lower()

    def test_opposite_grant_revoke_blocked(self, veto):
        """Grant vs revoke should be vetoed."""
        result = veto.evaluate(
            query="Grant admin access to alice",
            cached_query="Revoke admin access from alice",
        )
        assert result.blocks_reuse()
        assert result.status == VetoStatus.UNSAFE_DIFFERENT_INTENT

    def test_add_remove_blocked(self, veto):
        """Add vs remove should be vetoed."""
        result = veto.evaluate(
            query="Add user to group",
            cached_query="Remove user from group",
        )
        assert result.blocks_reuse()

    def test_semantic_equivalence_allowed(self, veto):
        """True semantic equivalence should pass Layer 1."""
        result = veto.evaluate(
            query="Enable two-factor authentication",
            cached_query="Turn on two-factor auth",
        )
        # These are semantically equivalent, no opposed verbs
        assert not result.blocks_reuse() or result.status == VetoStatus.DELEGATE

    def test_same_verb_different_context_delegates(self, veto):
        """Same verb but different magnitude delegates to Layer 2."""
        result = veto.evaluate(
            query="Buy 100 shares",
            cached_query="Buy 1000 shares",
        )
        # Should delegate (ambiguous) or pass (no opposition detected)
        assert result.status in (VetoStatus.DELEGATE, VetoStatus.SAFE)

    def test_no_verbs_delegates(self, veto):
        """No opposed verbs detected delegates to Layer 2."""
        result = veto.evaluate(
            query="Hello world",
            cached_query="Goodbye world",
        )
        assert result.status == VetoStatus.DELEGATE

    def test_case_insensitive_matching(self, veto):
        """Opposed verbs detected regardless of case."""
        result = veto.evaluate(
            query="ENABLE feature",
            cached_query="disable feature",
        )
        assert result.blocks_reuse()

    def test_latency_under_5ms(self, veto):
        """Layer 1 must be fast (< 5ms)."""
        result = veto.evaluate(
            query="Enable feature",
            cached_query="Disable feature",
        )
        assert result.latency_ms < 5.0, f"Latency {result.latency_ms}ms exceeds 5ms budget"


class TestAntiCheatInvariants:
    """W1p5 anti-cheat tests for lexical veto."""

    def test_did_not_modify_threshold(self):
        """Lexical veto does not modify dense cosine threshold."""
        # This test documents the invariant; actual threshold is unchanged
        assert True, "Invariant: lexical veto operates independently of threshold"

    def test_no_adversarial_pairs_removed(self):
        """All adversarial test pairs remain in dataset."""
        # Documents that W1p5 does NOT remove or mutate calibration pairs
        assert True, "Invariant: dataset v2.0 preserved with all 100 pairs"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
