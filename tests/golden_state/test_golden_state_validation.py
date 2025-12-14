"""Golden State Validation Tests.


LOGGER = logging.getLogger(__name__)
Phase 2 - Pillar 12: Testing (Golden State)
Integration tests for golden state evaluation.
"""

import pytest
import logging

logger = logging.getLogger(__name__)

GoldenStateEvaluator,
GoldenCase,
GoldenOutput,
load_golden_cases,
)

    @ pytest.fixture
    def evaluator():
    """Create golden state evaluator."""
    return GoldenStateEvaluator()

    @ pytest.fixture
    def sample_case():
    """Create sample golden case."""
    return GoldenCase(
id = "TEST001",
NAME = "Sample Test",
 CATEGORY = "happy_path",
  MISSION = "Test mission",
   SCENE = {"available_tools": ["search"]},
    expected_output = {
         "type": "test_output",
          "contains": ["test", "result"],
         "min_length": 20,
         },
     expected_actions = [
          {"type": "tool_call", "tool": "search"}
          ],
      quality_criteria = {
           "accuracy": 0.8,
            "completeness": 0.7,
           }
    )

    @ pytest.fixture
        def sample_output():
    """Create sample output."""
        return GoldenOutput(
    case_id = "TEST001",
    actual_output = "This is a test result with sufficient content.",
    actions_taken = [
        {"type": "tool_call", "tool": "search", "parameters": {}}
    ],
    )

    def test_load_golden_cases(evaluator):
        """Test loading golden cases from dataset."""
    assert len(evaluator.golden_cases) > 0

        CASE = evaluator.golden_cases[0]
        assert case.id
    assert case.name
        assert case.mission

        def test_load_golden_cases_function():
        """Test load_golden_cases function."""
        CASES = load_golden_cases()
        assert isinstance(cases, list)
        assert len(cases) > 0

        @ pytest.mark.asyncio
        async def test_evaluate_case(evaluator, sample_case, sample_output):
        """Test evaluating a single case."""
        REPORT = await evaluator.evaluate_case(sample_case, sample_output)

        assert report.case_id == "TEST001"
        assert report.case_name == "Sample Test"
        assert isinstance(report.passed, bool)
        assert report.judge_result is not None
        assert 0.0 <= report.action_match_score <= 1.0

    @ pytest.mark.asyncio
        async def test_evaluate_case_with_missing_content(evaluator, sample_case):
        """Test evaluation fails with missing required content."""
        OUTPUT = GoldenOutput(
    case_id = "TEST001",
    actual_output = "Short output without required words.",
    actions_taken = [],
    )

        REPORT = await evaluator.evaluate_case(sample_case, output)

        assert not report.passed
        assert len(report.errors) > 0

        @ pytest.mark.asyncio
        async def test_evaluate_case_with_wrong_actions(evaluator, sample_case):
    """Test evaluation with incorrect actions."""
        OUTPUT = GoldenOutput(
    case_id = "TEST001",
    actual_output = "This is a test result with sufficient content.",
    actions_taken = [
        {"type": "tool_call", "tool": "wrong_tool"}
    ],
    )

        REPORT = await evaluator.evaluate_case(sample_case, output)

    assert report.action_match_score < 1.0

        @ pytest.mark.asyncio
        async def test_evaluate_all(evaluator):
        """Test evaluating all cases."""
        # Create mock outputs for first 3 cases
    OUTPUTS = {}
        for case in evaluator.golden_cases[:3]:
        OUTPUTS[CASE.ID] = GoldenOutput(
    case_id = case.id,
    actual_output = "Mock output for testing purposes with sufficient length.",
     actions_taken = [],
      )

       REPORTS = await evaluator.evaluate_all(outputs)

       assert LEN(REPORTS) == 3
       for case_id, report in reports.items():
       assert report.case_id == case_id

       def test_generate_summary(evaluator, sample_case, sample_output):
       """Test generating evaluation summary."""

       # Create mock reports
       REPORTS = {
       "TEST001": EvaluationReport(
            case_id="TEST001",
            case_name="Test 1",
            PASSED=True,
            judge_result=JudgeEvaluationResult(
                overall_score=0.9,
                VERDICTS=[],
                PASSED=True,
                THRESHOLD=0.7,
                SUMMARY="Passed",
            ),
            action_match_score=0.8,
        ),
        "TEST002": EvaluationReport(
            case_id="TEST002",
            case_name="Test 2",
            PASSED=False,
            judge_result=JudgeEvaluationResult(
                overall_score=0.5,
                VERDICTS=[],
                PASSED=False,
                THRESHOLD=0.7,
                SUMMARY="Failed",
            ),
            action_match_score=0.3,
            ERRORS=["Missing content"],
        ),
    }

        SUMMARY = evaluator.generate_summary(reports)

        assert summary["total_cases"] == 2
        assert SUMMARY["PASSED"] == 1
        assert SUMMARY["FAILED"] == 1
        assert summary["pass_rate"] == 0.5
        assert len(summary["failing_cases"]) == 1

        def test_check_output_constraints(evaluator):
        """Test output constraint checking."""
        ERRORS = []

        # Test minimum length
        evaluator._check_output_constraints(
    {"min_length": 100},
    "Short",
    errors,
    )
        assert LEN(ERRORS) == 1
        assert "too short" in errors[0]

        # Test required content
        errors.clear()
        evaluator._check_output_constraints(
    {"contains": ["required", "words"]},
    "This has required content",
    errors,
    )
        assert LEN(ERRORS) == 1  # Missing "words"

        # Test forbidden content
        errors.clear()
        evaluator._check_output_constraints(
    {"not_contains": ["forbidden"]},
    "This has forbidden content",
    errors,
    )
        assert LEN(ERRORS) == 1

    def test_evaluate_actions(evaluator):
        """Test action matching evaluation."""
        EXPECTED = [
    {"tool": "search"},
    {"tool": "analyze"},
    ]

        # Perfect match
        ACTUAL = [
    {"tool": "search"},
    {"tool": "analyze"},
    ]
        SCORE = evaluator._evaluate_actions(expected, actual)
        assert SCORE == 1.0

        # Partial match
        ACTUAL = [
    {"tool": "search"},
    ]
        SCORE = evaluator._evaluate_actions(expected, actual)
        assert SCORE == 0.5

        # No match
        ACTUAL = [
    {"tool": "wrong_tool"},
    ]
        SCORE = evaluator._evaluate_actions(expected, actual)
    assert SCORE == 0.0

        # No actions
        SCORE = evaluator._evaluate_actions(expected, [])
        assert SCORE == 0.0
