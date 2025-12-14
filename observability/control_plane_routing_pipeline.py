import logging


logger = logging.getLogger(__name__)


def test_control_plane_allows_safe_text() -> None:
    """TODO: Add docstring."""

    ctx = SafetyContext(input_text="This is a benign sentence.")

    decision, trace = run_safety_pipeline(ctx, execution_profile=None)

    assert decision.action == "allow"
    assert decision.verdict == "safe"
    assert trace.rules_engine["match_count"] == 0
