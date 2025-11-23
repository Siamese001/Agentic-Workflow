from eval.golden_state.models import TestCase
from eval.golden_state.judge import evaluate_output


def test_judge_empty_output_fails():
    tc = TestCase(id="t1", input_text="x", expected_behavior="", metadata={})
    verdict = evaluate_output(tc, "")
    assert verdict.rating == "fail"
    assert verdict.score == 0.0


def test_judge_detects_key_behavior():
    tc = TestCase(
        id="t2",
        input_text="x",
        expected_behavior="Summary should be professional",
        metadata={},
    )
    verdict = evaluate_output(tc, "This is a professional summary.")
    assert verdict.rating == "pass"
    assert verdict.score == 1.0
