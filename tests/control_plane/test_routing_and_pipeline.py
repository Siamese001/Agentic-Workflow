from infra.control_plane.models import SafetyContext
from infra.control_plane.control_plane import run_safety_pipeline


def test_control_plane_allows_safe_text():
    ctx = SafetyContext(input_text="This is a benign sentence.")

    decision, trace = run_safety_pipeline(ctx, execution_profile=None)

    assert decision.action == "allow"
    assert decision.verdict == "safe"
    assert trace.rules_engine["match_count"] == 0
