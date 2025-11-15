"""Unit tests for the ArbitrationEngine resilience signals."""
from core_v10_7_services import (
    ArbitrationEngine,
    RobustnessStack,
    SelfCorrectionManager,
)


def _make_engine(bullet_limit: int = 1, qa_limit: int = 1) -> ArbitrationEngine:
    stack = RobustnessStack(retry_limits={"bullets_quality": bullet_limit, "qa_validation": qa_limit})
    manager = SelfCorrectionManager()
    return ArbitrationEngine(robustness_stack=stack, self_correction_manager=manager)


def test_bullet_stage_accepts_when_scores_clear_threshold() -> None:
    engine = _make_engine()
    report = engine.run_check("bullets_post_selection", {"scores": [8.5, 7.2], "avg_score": 7.85})
    assert report.suggested_route == "ACCEPT"
    assert report.decision == "ACCEPT"


def test_bullet_stage_retries_then_replans() -> None:
    engine = _make_engine(bullet_limit=1)
    payload = {"scores": [5.0, 6.0], "avg_score": 5.5}
    first = engine.run_check("bullets_post_selection", payload)
    assert first.suggested_route == "RETRY_BULLETS"
    second = engine.run_check("bullets_post_selection", payload)
    assert second.suggested_route == "GLOBAL_REPLAN"


def test_qa_stage_handles_pass_and_retry() -> None:
    engine = _make_engine(qa_limit=1)
    passed = engine.run_check("qa_post_validation", {"qa_passed": True})
    assert passed.suggested_route == "ACCEPT"
    failed = engine.run_check("qa_post_validation", {"qa_passed": False, "issues": ["missing metrics"]})
    assert failed.suggested_route == "RETRY_QA"
    exhausted = engine.run_check("qa_post_validation", {"qa_passed": False, "issues": ["missing metrics"]})
    assert exhausted.suggested_route == "GLOBAL_REPLAN"


def test_qa_stage_requests_drafting_retry_for_blockers() -> None:
    engine = _make_engine(qa_limit=2)
    report = engine.run_check(
        "qa_post_validation",
        {"qa_passed": False, "severity": "critical", "issues": ["blocked"]},
    )
    assert report.suggested_route == "RETRY_DRAFTING"
