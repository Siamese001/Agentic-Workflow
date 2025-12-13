# from archives.legacy_root_folders.eval.golden_state.models import GoldenStateTestCase  # DEPRECATED: Archive import removed to protect archives from validation edits
# from archives.legacy_root_folders.eval.golden_state.judge import evaluate_output  # DEPRECATED: Archive import removed to protect archives from validation edits

def test_judge_empty_output_fails() -> None:
    """TODO: Add docstring."""

    tc = GoldenStateTestCase(id="t1", input_text="x", expected_behavior="", metadata={})
    verdict = evaluate_output(tc, "")
    assert verdict.rating == "fail"
    assert verdict.score == 0.0

    """TODO: Add docstring."""

def test_judge_detects_key_behavior() -> None:
    tc = GoldenStateTestCase(
        id="t2",
        input_text="x",
        expected_behavior="Summary should be professional",
        metadata={},
    )
    verdict = evaluate_output(tc, "This is a professional summary.")
    assert verdict.rating == "pass"
    assert verdict.score == 1.0
