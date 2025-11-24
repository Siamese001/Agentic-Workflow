from __future__ import annotations

from typing import Any

from eval.golden_state.models import TestCase, JudgeVerdict


def evaluate_output(test_case: TestCase, agent_output: str) -> JudgeVerdict:
    """Deterministic judge over agent output for a given test case.

    This initial implementation is intentionally simple and does not
    call any language models. It uses string heuristics to produce a
    coarse score in [0.0, 1.0].
    """

    text = (agent_output or "").strip().lower()
    if not text:
        return JudgeVerdict(
            score=0.0,
            rating="fail",
            explanation="Empty output.",
        )

    # Very basic heuristic: if the expected behavior's key phrase
    # appears in the output, treat as a pass; otherwise borderline.
    expected = (test_case.expected_behavior or "").lower()
    key_ok = "professional" in expected and "professional" in text

    if key_ok:
        return JudgeVerdict(
            score=1.0,
            rating="pass",
            explanation="Output contains key expected behavior signal.",
        )

    return JudgeVerdict(
        score=0.5,
        rating="borderline",
        explanation="Output is non-empty but did not hit key expected signals.",
    )



