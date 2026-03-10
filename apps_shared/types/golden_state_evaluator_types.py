"""Golden State Evaluator - Phase 2 Implementation.

Phase 2 - Pillar 12: Testing (Golden State)
Evaluates agent outputs against golden test cases.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

try:
    from apps_rg.core.JudgeEvaluation import (
        JudgeEvaluationResult,
        JudgeEvaluator,
        create_judge_evaluator,
    )
except ImportError:
    # Fallback implementations
    @dataclass
    class JudgeEvaluationResult:
        score: float
        reasoning: str

    class JudgeEvaluator:
        def evaluate(self, case: Any) -> JudgeEvaluationResult:
            return JudgeEvaluationResult(0.5, "Fallback evaluator")

    def create_judge_evaluator():
        return JudgeEvaluator()


Logger = logging.getLogger(__name__)


@dataclass
class GoldenCase:
    """Golden test case."""

    id: str
    name: str
    category: str
    mission: str
    scene: dict[str, Any]
    expected_output: dict[str, Any]
    expected_actions: list[dict[str, Any]]
    quality_criteria: dict[str, float]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GoldenCase":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            category=data["category"],
            mission=data["mission"],
            scene=data["scene"],
            expected_output=data["expected_output"],
            expected_actions=data["expected_actions"],
            quality_criteria=data["quality_criteria"],
        )


@dataclass
class GoldenOutput:
    """Output from agent execution."""

    case_id: str
    actual_output: str
    actions_taken: list[dict[str, Any]] = field(default_factory=list)
    execution_trace: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationReport:
    """Evaluation report for a golden case."""

    case_id: str
    case_name: str
    passed: bool
    judge_result: JudgeEvaluationResult
    action_match_score: float
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "case_id": self.case_id,
            "case_name": self.case_name,
            "passed": self.passed,
            "judge_result": self.judge_result.to_dict(),
            "action_match_score": self.action_match_score,
            "errors": self.errors,
        }


class GoldenStateEvaluator:
    """Evaluator for golden state test cases.

    Loads golden test cases and evaluates agent outputs against them.
    Uses JudgeEvaluator for quality assessment.
    """

    def __init__(
        self,
        dataset_path: Path | None = None,
        JudgeEvaluator: JudgeEvaluator | None = None,
        enable_logging: bool = True,
    ):
        """Initialize evaluator.

        Args:
            dataset_path: Path to golden dataset JSON
            JudgeEvaluator: Judge evaluator instance
            enable_logging: Enable logging
        """
        self.dataset_path = dataset_path or Path("data/golden_state/datasets/core/test_cases.json")
        self.JudgeEvaluator = JudgeEvaluator or create_judge_evaluator()
        self.enable_logging = enable_logging

        self.golden_cases: list[GoldenCase] = []
        self._load_cases()

    def _load_cases(self) -> None:
        """Load golden test cases from dataset."""
        try:
            with open(self.dataset_path) as f:
                data = json.load(f)

            for case_data in data.get("test_cases", []):
                case = GoldenCase.from_dict(case_data)
                self.golden_cases.append(case)

            if self.enable_logging:
                Logger.info("golden_cases_loaded", extra={"count": len(self.golden_cases)})

        except FileNotFoundError:
            if self.enable_logging:
                Logger.warning("golden_dataset_not_found", extra={"path": str(self.dataset_path)})
        except Exception as e:
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            if self.enable_logging:
                Logger.error(
                    "failed_to_load_golden_cases",
                    extra={"error": str(e)},
                    exc_info=True,
                )

    async def evaluate_case(
        self,
        case: GoldenCase,
        output: GoldenOutput,
    ) -> EvaluationReport:
        """Evaluate output against golden case.

        Args:
            case: Golden test case
            output: Agent output

        Returns:
            EvaluationReport with results
        """
        errors: list[str] = []

        # Evaluate with judge
        expected_output = case.expected_output
        if isinstance(expected_output, dict) and "contains" in expected_output:
            # Convert list to string for evaluation
            expected_str = ", ".join(expected_output["contains"])
        else:
            expected_str = str(expected_output) if expected_output else None

        judge_result = await self.JudgeEvaluator.evaluate(
            output=output.actual_output,
            expected=expected_str,
            context={
                "Task": case.mission,
                "category": case.category,
            },
        )

        # Evaluate action matching
        action_match_score = self._evaluate_actions(
            expected=case.expected_actions,
            actual=output.actions_taken,
        )

        # Check output constraints
        self._check_output_constraints(
            case.expected_output,
            output.actual_output,
            errors,
        )

        # Determine pass/fail
        passed = judge_result.passed and action_match_score >= 0.5 and len(errors) == 0

        report = EvaluationReport(
            case_id=case.id,
            case_name=case.name,
            passed=passed,
            judge_result=judge_result,
            action_match_score=action_match_score,
            errors=errors,
        )

        if self.enable_logging:
            Logger.info(
                "case_evaluated",
                extra={
                    "case_id": case.id,
                    "passed": passed,
                    "judge_score": judge_result.overall_score,
                    "action_score": action_match_score,
                },
            )

        return report

    def _evaluate_actions(
        self,
        expected: list[dict[str, Any]],
        actual: list[dict[str, Any]],
    ) -> float:
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

        # Simple matching: check if expected tools were used
        expected_tools = {a.get("tool") for a in expected if a.get("tool")}
        actual_tools = {a.get("tool") for a in actual if a.get("tool")}

        if not expected_tools:
            return 1.0

        matches = len(expected_tools & actual_tools)
        score = matches / len(expected_tools)

        return score

    def _check_output_constraints(
        self,
        expected: dict[str, Any],
        actual: str,
        errors: list[str],
    ) -> None:
        """Check output constraints.

        Args:
            expected: Expected output constraints
            actual: Actual output
            errors: List to append errors to
        """
        # Check minimum length
        min_length = expected.get("min_length", 0)
        if len(actual) < min_length:
            errors.append(f"Output too short: {len(actual)} < {min_length}")

        # Check maximum length
        max_length = expected.get("max_length")
        if max_length and len(actual) > max_length:
            errors.append(f"Output too long: {len(actual)} > {max_length}")

        # Check required content
        contains = expected.get("contains", [])
        if isinstance(contains, list):
            for required in contains:
                if required.lower() not in actual.lower():
                    errors.append(f"Missing required content: {required}")

        # Check forbidden content
        not_contains = expected.get("not_contains", [])
        if isinstance(not_contains, list):
            for forbidden in not_contains:
                if forbidden.lower() in actual.lower():
                    errors.append(f"Contains forbidden content: {forbidden}")

    async def evaluate_all(
        self,
        outputs: dict[str, GoldenOutput],
    ) -> dict[str, EvaluationReport]:
        """Evaluate all golden cases.

        Args:
            outputs: Dict of case_id -> GoldenOutput

        Returns:
            Dict of case_id -> EvaluationReport
        """
        reports: dict[str, EvaluationReport] = {}

        for case in self.golden_cases:
            if case.id in outputs:
                report = await self.evaluate_case(case, outputs[case.id])
                reports[case.id] = report

        return reports

    def generate_summary(
        self,
        reports: dict[str, EvaluationReport],
    ) -> dict[str, Any]:
        """Generate summary of evaluation results.

        Args:
            reports: Evaluation reports

        Returns:
            Summary dict
        """
        total = len(reports)
        passed = sum(1 for r in reports.values() if r.passed)
        failed = total - passed

        pass_rate = passed / total if total > 0 else 0.0

        avg_judge_score = (
            sum(r.judge_result.overall_score for r in reports.values()) / total if total > 0 else 0.0
        )

        avg_action_score = sum(r.action_match_score for r in reports.values()) / total if total > 0 else 0.0

        failing_cases = [
            {"id": r.case_id, "name": r.case_name, "errors": r.errors}
            for r in reports.values()
            if not r.passed
        ]

        return {
            "total_cases": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate,
            "avg_judge_score": avg_judge_score,
            "avg_action_score": avg_action_score,
            "failing_cases": failing_cases,
        }


def load_golden_cases(dataset_path: Path | None = None) -> list[GoldenCase]:
    """Load golden test cases.

    Args:
        dataset_path: Path to dataset JSON

    Returns:
        List of GoldenCase objects
    """
    evaluator = GoldenStateEvaluator(dataset_path=dataset_path)
    return evaluator.golden_cases


async def evaluate_case_output(
    case: GoldenCase,
    output: GoldenOutput,
) -> EvaluationReport:
    """Evaluate a single case output.

    Args:
        case: Golden test case
        output: Agent output

    Returns:
        EvaluationReport
    """
    evaluator = GoldenStateEvaluator()
    return await evaluator.evaluate_case(case, output)
