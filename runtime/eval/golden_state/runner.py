# runner - Golden test runner utilities
from typing import Dict, Any, List
from dataclasses import dataclass
from .datasets import load_golden_cases
from .judge import evaluate_output, EvaluationVerdict
from .models import GoldenStateTestCase

@dataclass
class GoldenTestResult:
    """Result from running a golden test"""
    test_id: str
    passed: bool
    verdict: EvaluationVerdict
    execution_time: float = 0.0

@dataclass
class GoldenTestSummary:
    """Summary of golden test execution"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    results: List[GoldenTestResult]
    overall_score: float = 0.0

def convert_golden_case_to_state_test_case(golden_case) -> GoldenStateTestCase:
    """Convert GoldenCase to GoldenStateTestCase for evaluation"""
    # Extract input text from input_data
    input_text = str(golden_case.input_data.get("text", golden_case.input_data.get("input", "")))
    
    # Extract expected behavior from expected_output
    expected_behavior = str(golden_case.expected_output.get("behavior", 
                           golden_case.expected_output.get("expected_behavior", 
                           str(golden_case.expected_output))))
    
    return GoldenStateTestCase(
        id=golden_case.id,
        input_text=input_text,
        expected_behavior=expected_behavior,
        metadata=golden_case.metadata
    )

def run_all_golden_tests(profile) -> List[GoldenTestResult]:
    """Run all golden tests for a dataset using the provided profile"""
    # Extract dataset name from profile or use default
    dataset_name = profile.metadata.get("dataset_name", "default")
    
    # Load test cases
    test_cases = load_golden_cases(dataset_name)
    
    results = []
    passed_count = 0
    
    for test_case in test_cases:
        # Convert GoldenCase to GoldenStateTestCase for evaluation
        state_test_case = convert_golden_case_to_state_test_case(test_case)
        
        # Mock execution - in real implementation would use profile for execution
        mock_output = f"Mock output for {test_case.id} using profile {profile.name}"
        
        # Evaluate the output
        verdict = evaluate_output(state_test_case, mock_output)
        
        # Create result
        result = GoldenTestResult(
            test_id=test_case.id,
            passed=verdict.rating in ["pass"],
            verdict=verdict,
            execution_time=0.1  # Mock execution time
        )
        
        results.append(result)
        if result.passed:
            passed_count += 1
    
    return results
