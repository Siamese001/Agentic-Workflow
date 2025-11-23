from __future__ import annotations

from typing import List

from models import ExecutionProfile

from eval.golden_state.datasets import load_golden_inputs
from eval.golden_state.judge import evaluate_output
from eval.golden_state.models import EvalResult


def _mock_agent_output(input_text: str) -> str:
    """Deterministic stand-in for the real agent pipeline.

    Phase 4 integrates the golden harness without depending on actual
    L1–L4 execution here. Tests rely on this being stable.
    """

    if "unethical" in input_text.lower():
        return "I cannot assist with unethical behavior."
    return "This is a professional, concise summary placeholder."


def run_all_golden_tests(profile: ExecutionProfile) -> List[EvalResult]:
    """Run the golden-state suite against the current agent stack.

    For now this uses a deterministic mock agent output, but the
    interface matches what a real integration would use.
    """

    results: List[EvalResult] = []
    for tc in load_golden_inputs():
        output = _mock_agent_output(tc.input_text)
        verdict = evaluate_output(tc, output)
        results.append(
            EvalResult(
                test_id=tc.id,
                verdict=verdict,
                raw_output=output,
                reasoning_trace=[],
            )
        )
    return results
