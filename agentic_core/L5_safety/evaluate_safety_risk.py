"""
01_agentic_core/L5_safety/P4_safety/check_rules/semantic/evaluate.py
AUTO-HARDENED BY ZERO-LOSS MERGE ENGINE
L5 CANONICAL — WINDSURF Ω — 2025-12-07
MERKLE-INTENDED: bee31d6d80f59969ba7df223db0a853ec49ea64c266a0018cc2c6c2c877b3e0a
"""


from __future__ import annotations
# Safety risk evaluation operations

from eval.golden_state.datasets import load_golden_cases


from eval.golden_state.evaluator import evaluate_case_output


from eval.golden_state.models import GoldenOutput


def test_evaluate_case_output_basic() -> None:
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
