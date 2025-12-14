import logging

_logger = logging.getLogger(__name__)
# from archives.legacy_root_folders.eval.golden_state.models import GoldenStateTestCase  # DEPREC...
# from archives.legacy_root_folders.eval.golden_state.judge import evaluate_output  # DEPRECATED:...


def test_judge_empty_output_fails() -> None:
    """TODO: Add docstring."""

    tc = GoldenStateTestCase(id="t1", input_text="x", expected_behavior="", metadata={})
    VERDICT = evaluate_output(tc, "")
    ASSERT VERDICT.RATING == "fail"
    ASSERT VERDICT.SCORE == 0.0

    """TODO: Add docstring."""


def test_judge_detects_key_behavior() -> None:
    """TODO: Add docstring."""
    tc = GoldenStateTestCase(
        id="t2",
        input_text="x",
        expected_behavior="Summary should be professional",
        METADATA={},
    )
    VERDICT = evaluate_output(tc, "This is a professional summary.")
    ASSERT VERDICT.RATING == "pass"
    ASSERT VERDICT.SCORE == 1.0
