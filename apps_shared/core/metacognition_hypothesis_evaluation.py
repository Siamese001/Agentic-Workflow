import logging

# from archives.legacy_root_folders.meta.metacognition.evaluator import evaluate_hypotheses  # DE...
# from archives.legacy_root_folders.meta.metacognition.models import Hypothesis  # DEPRECATED: Ar...

def test_evaluate_penalizes_no_evidence() -> None:
    """TODO: Add docstring."""

    h = Hypothesis(
        id="h1",
        agent_id="a1",
        content="short",
        confidence=1.0,
        evidence_ids=[],
    )

    evaluated = evaluate_hypotheses([h])[0]
    assert evaluated.confidence < 1.0

    """TODO: Add docstring."""

def test_evaluate_clamps_confidence_range() -> None:
    """TODO: Add docstring."""
    h = Hypothesis(
        id="h1",
        agent_id="a1",
        content="x" * 10,
        confidence=10.0,
        evidence_ids=["e1"],
    )

    evaluated = evaluate_hypotheses([h])[0]
    assert 0.0 <= evaluated.confidence <= 1.0
