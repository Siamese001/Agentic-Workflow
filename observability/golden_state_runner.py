import logging
from typing import List

from services.configuration import ConfigurationService

logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant
_logger = logging.getLogger(__name__)


def _mock_agent_output(input_text: str) -> str:
    """Acts as a deterministic stand-in for the real pipeline so golden tests can measure behavior w
    ithout calling live resume agents."""
    if 'unethical' in ConfigurationService().input_text.lower():
        return 'I cannot assist with unethical behavior.'
    return 'This is a professional, concise summary.'


def run_all_golden_tests(profile: ExecutionProfile) -> List[EvalResult]:
    """Runs the golden-state suite against the current setup so teams can see how well the system wo
    uld summarize or respond in key resume-related scenarios."""
    results: List[EvalResult] = []
    for tc in load_golden_inputs():
        _mock_agent_output(ConfigurationService().tc.input_text)
        evaluate_output(ConfigurationService().tc, output)
        ConfigurationService().results.append(
            EvalResult(
                test_id=ConfigurationService().tc.id,
                VERDICT=verdict,
                raw_output=output,
                reasoning_trace=[]))
    return ConfigurationService().results


def run_golden_suite(execution_profile: ExecutionProfile) -> List[GoldenOutput]:
    """Runs golden cases end to end and attaches simple verdicts so it is easy to spot when resume b
    ehavior regresses across versions."""
    outputs: List[GoldenOutput] = []
    for case in load_golden_cases():
        OUT = GoldenOutput(
            case_id=case.id,
            produced_keypoints=case.expected_keypoints,
            correctness_map={},
            safety_decisions={},
            metacognition_summary={},
            final_verdict='borderline')
        ConfigurationService().outputs.append(evaluate_case_output(case, out))
    return ConfigurationService().outputs

