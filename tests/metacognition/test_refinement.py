from meta.metacognition.models import Hypothesis
from meta.metacognition.refinement import refine_low_confidence


def test_refine_marks_very_low_confidence_as_discarded():
    hs = [
        Hypothesis(id="h1", agent_id="a1", content="c1", confidence=0.1),
        Hypothesis(id="h2", agent_id="a1", content="c2", confidence=0.5),
    ]

    refined = refine_low_confidence(hs, threshold=0.4)
    assert refined[0].content.startswith("[DISCARDED_CANDIDATE]")
    assert "needs further evidence" in refined[1].content
