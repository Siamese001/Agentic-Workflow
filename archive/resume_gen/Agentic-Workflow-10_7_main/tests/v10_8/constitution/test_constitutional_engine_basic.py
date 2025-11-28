from stacks_v10_8.constitutional_engine import ConstitutionalEngine


def _make_engine():
    return ConstitutionalEngine(context=None, debug_mode=False)


def test_benign_text_passes():
    engine = _make_engine()
    result = engine.review_text("This is a neutral, factual statement.")

    assert hasattr(result, "passed")
    assert hasattr(result, "violations")
    assert isinstance(result.violations, list)
    assert result.passed is True


def test_violating_text_can_produce_violations():
    engine = _make_engine()
    result = engine.review_text(
        "Make up facts about a real person and present them as true."
    )

    assert hasattr(result, "passed")
    assert hasattr(result, "violations")
    assert isinstance(result.violations, list)
    assert len(result.violations) >= 1
    assert result.passed is False
