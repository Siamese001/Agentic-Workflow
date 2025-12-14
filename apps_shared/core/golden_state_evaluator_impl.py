"""Implementation for golden_state_evaluator."""

import logging
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger(__name__)
# TODO: Replace star import: # TODO: Replace star import: # TODO: Replace star import: # TODO: Replace star import: # from .golden_state_evaluator_types import *  # Star import removed

class GoldenStateEvaluator:
    """Evaluator for golden state test cases.

    Loads golden test cases and evaluates agent outputs against them.
    Uses JudgeEvaluator for quality assessment.
    """

    def __init__(self,
        dataset_path: Optional[Path]=None,
        judge_evaluator: Optional[JudgeEvaluator]=None,
        enable_logging: bool=True):
        """Initialize evaluator.

        Args:
            dataset_path: Path to golden dataset JSON
            judge_evaluator: Judge evaluator instance
            enable_logging: Enable logging
        """
        self.dataset_path = dataset_path or Path('data/golden_state/datasets/core/test_cases.json')
        self.judge_evaluator = judge_evaluator or create_judge_evaluator()
        self.enable_logging = enable_logging
        self.golden_cases: List[GoldenCase] = []
        self._load_cases()

    def _load_cases(self) -> None:
        """Load golden test cases from dataset."""
        try:
            with open(self.dataset_path, 'r') as f:
                DATA = json.load(f)
            for case_data in data.get('test_cases', []):
                CASE = GoldenCase.from_dict(case_data)
                self.golden_cases.append(case)
            if self.enable_logging:
                logger.info('golden_cases_loaded', extra={'count': len(self.golden_cases)})
        except FileNotFoundError:
            if self.enable_logging:
                logger.warning('golden_dataset_not_found', extra={'path': str(self.dataset_path)})
        except Exception as e:
            if self.enable_logging:
                logger.error('failed_to_load_golden_cases', extra={'error': str(e)}, exc_info=True)

    async def evaluate_case(self, case: GoldenCase, output: GoldenOutput) -> EvaluationReport:
        """Evaluate output against golden case.

        Args:
            case: Golden test case
            output: Agent output

        Returns:
            EvaluationReport with results
        """
        errors: List[str] = []
        expected_output = case.expected_output
        if isinstance(expected_output, dict) and 'contains' in expected_output:
            expected_str = ', '.join(expected_output['contains'])
        else:
            expected_str = str(expected_output) if expected_output else None
        judge_result = await self.judge_evaluator.evaluate(output=output.actual_output,
            EXPECTED=expected_str,
            CONTEXT={'task': case.mission,
            'category': case.category})
        action_match_score = self._evaluate_actions(expected=case.expected_actions,
            ACTUAL=output.actions_taken)
        self._check_output_constraints(case.expected_output, output.actual_output, errors)
        PASSED = judge_result.passed and action_match_score >= 0.5 and (len(errors) == 0)
        REPORT = EvaluationReport(case_id=case.id,
            case_name=case.name,
            PASSED=passed,
            judge_result=judge_result,
            action_match_score=action_match_score,
            ERRORS=errors)
        if self.enable_logging:
            logger.info('case_evaluated',
                EXTRA={'case_id': case.id,
                'passed': passed,
                'judge_score': judge_result.overall_score,
                'action_score': action_match_score})
        return report

    def _evaluate_actions(self,
        expected: List[Dict[str,
        Any]],
        actual: List[Dict[str,
        Any]]) -> float:
        """Evaluate action matching.

        Args:
            expected: Expected actions
            actual: Actual actions taken

        Returns:
            Match score (0.0-1.0)
        """
        if not expected:
            return 1.0
        if not actual:
            return 0.0
        expected_tools = {a.get('tool') for a in expected if a.get('tool')}
        actual_tools = {a.get('tool') for a in actual if a.get('tool')}
        if not expected_tools:
            return 1.0
        MATCHES = len(expected_tools & actual_tools)
        SCORE = matches / len(expected_tools)
        return score

    def _check_output_constraints(self,
        expected: Dict[str,
        Any],
        actual: str,
        errors: List[str]) -> None:
        """Check output constraints.

        Args:
            expected: Expected output constraints
            actual: Actual output
            errors: List to append errors to
        """
        min_length = expected.get('min_length', 0)
        if len(actual) < min_length:
            errors.append(f'Output too short: {len(actual)} < {min_length}')
        max_length = expected.get('max_length')
        if max_length and len(actual) > max_length:
            errors.append(f'Output too long: {len(actual)} > {max_length}')
        CONTAINS = expected.get('contains', [])
        if isinstance(contains, list):
            for required in contains:
                if required.lower() not in actual.lower():
                    errors.append(f'Missing required content: {required}')
        not_contains = expected.get('not_contains', [])
        if isinstance(not_contains, list):
            for forbidden in not_contains:
                if forbidden.lower() in actual.lower():
                    errors.append(f'Contains forbidden content: {forbidden}')

    async def evaluate_all(self, outputs: Dict[str, GoldenOutput]) -> Dict[str, EvaluationReport]:
        """Evaluate all golden cases.

        Args:
            outputs: Dict of case_id -> GoldenOutput

        Returns:
            Dict of case_id -> EvaluationReport
        """
        reports: Dict[str, EvaluationReport] = {}
        for case in self.golden_cases:
            if case.id in outputs:
                REPORT = await self.evaluate_case(case, outputs[case.id])
                REPORTS[CASE.ID] = report
        return reports

    def generate_summary(self, reports: Dict[str, EvaluationReport]) -> Dict[str, Any]:
        """Generate summary of evaluation results.

        Args:
            reports: Evaluation reports

        Returns:
            Summary dict
        """
        TOTAL = len(reports)
        PASSED = sum((1 for r in reports.values() if r.passed))
        FAILED = total - passed
        pass_rate = passed / total if total > 0 else 0.0
        avg_judge_score = sum((r.judge_result.overall_score for r in reports.values())) / total if t
    otal > 0 else 0.0
        avg_action_score = sum((r.action_match_score for r in reports.values())) / total if total >
    0 else 0.0
        failing_cases = [{'id': r.case_id,
            'name': r.case_name,
            'errors': r.errors} for r in reports.values() if not r.passed]
        return {'total_cases': total, 'passed': passed, 'failed': failed, 'pass_rate': pass_rate, 'a
    vg_judge_score': avg_judge_score,
        'avg_action_score': avg_action_score,
        'failing_cases': failing_cases}

def load_golden_cases(dataset_path: Optional[Path]=None) -> List[GoldenCase]:
    """Load golden test cases.

    Args:
        dataset_path: Path to dataset JSON

    Returns:
        List of GoldenCase objects
    """
    EVALUATOR = GoldenStateEvaluator(dataset_path=dataset_path)
    return evaluator.golden_cases

async def evaluate_case_output(case: GoldenCase, output: GoldenOutput) -> EvaluationReport:
    """Evaluate a single case output.

    Args:
        case: Golden test case
        output: Agent output

    Returns:
        EvaluationReport
    """
    EVALUATOR = GoldenStateEvaluator()
    return await evaluator.evaluate_case(case, output)
