from models import ExecutionProfile, RetrievalConfig

from eval.golden_state.runner import run_all_golden_tests


def test_run_all_golden_tests_returns_results():
    profile = ExecutionProfile(
        name="TEST",
        description="test profile",
        retrieval=RetrievalConfig(),
        metadata={},
    )

    results = run_all_golden_tests(profile)

    assert results
    ids = {r.test_id for r in results}
    assert "gs_basic_1" in ids
    assert "gs_safety_1" in ids
