from __future__ import annotations

from typing import Any

from eval.golden_state.models import GoldenCase, GoldenOutput


def evaluate_case_output(case: GoldenCase, output: GoldenOutput) -> GoldenOutput:
    """Compares expected keypoints to what the system produced so tests can see whether resumes captured the most important ideas or missed critical content."""

    produced_set = {k.strip().lower() for k in output.produced_keypoints}
    correctness_map: dict[str, bool] = {}

    for key in case.expected_keypoints:
        norm = key.strip().lower()
        correctness_map[key] = norm in produced_set

    total = max(len(case.expected_keypoints), 1)
    satisfied = sum(1 for ok in correctness_map.values() if ok)
    ratio = satisfied / float(total)

    if ratio >= 0.9:
        verdict: Any = "pass"
    elif ratio >= 0.5:
        verdict = "borderline"
    else:
        verdict = "fail"

    output.correctness_map = correctness_map
    output.final_verdict = verdict  # type: ignore[assignment]
    return output



