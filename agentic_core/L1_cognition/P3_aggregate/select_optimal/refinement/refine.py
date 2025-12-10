"""
01_agentic_core/L1_cognition/P3_aggregate/select_optimal/refinement/refine.py
AUTO-HARDENED BY ZERO-LOSS MERGE ENGINE
L5 CANONICAL — WINDSURF Ω — 2025-12-07
MERKLE-INTENDED: 692af9b07045aba57eb8f1a97fae327746951bfca2a858bf51dbd14c69b66c2e
"""


# Refinement operations for aggregation phase

from meta.metacognition.models import Hypothesis


from meta.metacognition.refinement import refine_low_confidence


def test_refine_marks_very_low_confidence_as_discarded() -> None:
    """Test that hypotheses below confidence threshold are marked as discarded."""
    hs = [
        Hypothesis(id="h1", agent_id="a1", content="c1", confidence=0.1),
        Hypothesis(id="h2", agent_id="a1", content="c2", confidence=0.5),
    ]

    refined = refine_low_confidence(hs, threshold=0.4)
    assert refined[0].content.startswith("[DISCARDED_CANDIDATE]")
    assert "needs further evidence" in refined[1].content
