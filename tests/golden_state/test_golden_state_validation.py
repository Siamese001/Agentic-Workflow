"""Golden State Validation Tests.

Phase 2 - Pillar 12: Testing (Golden State)
Integration tests for golden state evaluation.
"""

import logging

import pytest

logger = logging.getLogger(__name__)

# Import the required classes
from golden_state import (
    GoldenStateEvaluator,
    GoldenCase,
    GoldenOutput,
    load_golden_cases,
)

@pytest.fixture
def evaluator():
    """Create golden state evaluator."""
    return GoldenStateEvaluator()

@pytest.fixture
def sample_case():
    """Create sample golden case."""
    return GoldenCase(
        id="TEST001",
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

    @pytest.fixture
def sample_output():
    """Create sample output."""
    return GoldenOutput(
        case_id="TEST001",
        actual_output="This is a test result with sufficient content.",
        actions_taken=[
            {"type": "tool_call", "tool": "search", "parameters": {}}
        ],
    )

def test_load_golden_cases(evaluator):
    """Test loading golden cases from dataset."""
    assert len(evaluator.golden_cases) > 0
    
    case = evaluator.golden_cases[0]
    assert case.id
    assert case.name
    assert case.mission

def test_load_golden_cases_function():
    """Test load_golden_cases function."""
    cases = load_golden_cases()
    assert isinstance(cases, list)
    assert len(cases) > 0

@pytest.mark.asyncio
async def test_evaluate_case(evaluator, sample_case, sample_output):
    """Test evaluating a single case."""
    report = await evaluator.evaluate_case(sample_case, sample_output)
    
    assert report.case_id == "TEST001"
    assert report.case_name == "Sample Test"
    assert isinstance(report.passed, bool)
    assert report.judge_result is not None
    assert 0.0 <= report.action_match_score <= 1.0

@pytest.mark.asyncio
async def test_evaluate_case_with_missing_content(evaluator, sample_case):
    """Test evaluation fails with missing required content."""
    output = GoldenOutput(
        case_id="TEST001",
        actual_output="Short output without required words.",
        actions_taken=[],
    )
    
    report = await evaluator.evaluate_case(sample_case, output)
    
    assert not report.passed
    assert len(report.errors) > 0

        @pytest.mark.asyncio
async def test_evaluate_case_with_wrong_actions(evaluator, sample_case):
    """Test evaluation with incorrect actions."""
    output = GoldenOutput(
        case_id="TEST001",
        actual_output="This is a test result with sufficient content.",
        actions_taken=[
            {"type": "tool_call", "tool": "wrong_tool"}
        ],
    )
    
    report = await evaluator.evaluate_case(sample_case, output)
    
    assert report.action_match_score < 1.0

@pytest.mark.asyncio
async def test_evaluate_all(evaluator):
    """Test evaluating all cases."""
    # Create mock outputs for first 3 cases
    outputs = {}
    for case in evaluator.golden_cases[:3]:
        outputs[case.id] = GoldenOutput(
            case_id=case.id,
            actual_output="Mock output for testing purposes with sufficient length.",
            actions_taken=[],
        )
    
    reports = await evaluator.evaluate_all(outputs)
    
    assert len(reports) == 3
    for case_id, report in reports.items():
        assert report.case_id == case_id

def test_generate_summary(evaluator, sample_case, sample_output):
    """Test generating evaluation summary."""
    
    # Create mock reports
    reports = {
        "TEST001": EvaluationReport(
            case_id="TEST001",
            case_name="Test 1",
            passed=True,
            judge_result=JudgeEvaluationResult(
                overall_score=0.9,
                verdicts=[],
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

    summary = evaluator.generate_summary(reports)
    
    assert summary["total_cases"] == 2
    assert summary["passed"] == 1
    assert summary["failed"] == 1
    assert summary["pass_rate"] == 0.5
    assert len(summary["failing_cases"]) == 1

def test_check_output_constraints(evaluator):
    """Test output constraint checking."""
    errors = []
    
    # Test minimum length
    evaluator._check_output_constraints(
        {"min_length": 100},
        "Short",
        errors,
    )
    assert len(errors) == 1
    assert "too short" in errors[0]
    
    # Test required content
    errors.clear()
    evaluator._check_output_constraints(
        {"contains": ["required", "words"]},
        "This has required content",
        errors,
    )
    assert len(errors) == 0  # Contains both "required" and "words"
    
    # Test forbidden content
    errors.clear()
    evaluator._check_output_constraints(
        {"not_contains": ["forbidden"]},
        "This has forbidden content",
        errors,
    )
    assert len(errors) == 1
    assert "forbidden" in errors[0]

def test_evaluate_actions(evaluator):
    """Test action matching evaluation."""
    expected = [
        {"tool": "search"},
        {"tool": "analyze"},
    ]
    
    # Perfect match
    actual = [
        {"tool": "search"},
        {"tool": "analyze"},
    ]
    score = evaluator._evaluate_actions(expected, actual)
    assert score == 1.0
    
    # Partial match
    actual = [
        {"tool": "search"},
    ]
    score = evaluator._evaluate_actions(expected, actual)
    assert score == 0.5
    
    # No match
    actual = [
        {"tool": "wrong_tool"},
    ]
    score = evaluator._evaluate_actions(expected, actual)
    assert score == 0.0

        # No actions
    score = evaluator._evaluate_actions(expected, [])
    assert score == 0.0

