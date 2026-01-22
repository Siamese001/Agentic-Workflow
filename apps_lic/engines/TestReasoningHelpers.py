

def test_cot_expand_guarantees_minimum_step():
    steps = cot.expand("Consider options", steps=0)
    assert steps == ["Step 1: Consider options"]


def test_cot_expand_respects_requested_steps():
    steps = cot.expand("Consider options", steps=2)
    assert len(steps) == 2


def test_reflexion_apply_feedback_appends_insight():
    updated = reflexion.apply_feedback("Draft body", "Focus on product value")
    assert "Reflexion:" in updated
    assert updated.startswith("Draft body")


def test_reflexion_no_insight_returns_original():
    updated = reflexion.apply_feedback("Draft body", "")
    assert updated == "Draft body"