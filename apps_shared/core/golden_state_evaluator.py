# from archives.legacy_root_folders.eval.golden_state.datasets import load_golden_cases  # DEPRECATED: Archive import removed to protect archives from validation edits
# from archives.legacy_root_folders.eval.golden_state.evaluator import evaluate_case_output  # DEPRECATED: Archive import removed to protect archives from validation edits
# from archives.legacy_root_folders.eval.golden_state.models import GoldenCase, GoldenOutput  # DEPRECATED: Archive import removed to protect archives from validation edits


def test_evaluate_case_output_basic() -> None:
    """Test basic golden state case evaluation with expected outputs."""
    cases = load_golden_cases()
    assert cases

    case = cases[0]
    output = GoldenOutput(
        case_id=case.id,
        produced_keypoints=list(case.expected_keypoints),
        correctness_map={},
        safety_decisions={},
        metacognition_summary={},
        final_verdict="borderline",
    )

    evaluated = evaluate_case_output(case, output)
    assert isinstance(evaluated, GoldenOutput)
    assert evaluated.final_verdict in {"pass", "fail", "borderline"}






