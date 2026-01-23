# FILE: tests/golden_state/test_runner.py

# from archives.legacy_root_folders.core.models.models import ExecutionProfile, RetrievalConfig  # DEPRECATED: Archive import removed to protect archives from validation edits

# from archives.legacy_root_folders.eval.golden_state.runner import run_all_golden_tests  # DEPRECATED: Archive import removed to protect archives from validation edits


def test_run_all_golden_tests_returns_results() -> None:
    """Test that running all golden tests returns valid result objects."""
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
