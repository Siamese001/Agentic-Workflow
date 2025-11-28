from meta.metacognition.evaluator import evaluate_hypotheses
from meta.metacognition.models import Hypothesis


def test_evaluate_penalizes_no_evidence():
    h = Hypothesis(
        id="h1",
        agent_id="a1",
        content="short",
        confidence=1.0,
        evidence_ids=[],
    )

    evaluated = evaluate_hypotheses([h])[0]
    assert evaluated.confidence < 1.0


def test_evaluate_clamps_confidence_range():
    h = Hypothesis(
        id="h1",
        agent_id="a1",
        content="x" * 10,
        confidence=10.0,
        evidence_ids=["e1"],
    )

    evaluated = evaluate_hypotheses([h])[0]
    assert 0.0 <= evaluated.confidence <= 1.0






