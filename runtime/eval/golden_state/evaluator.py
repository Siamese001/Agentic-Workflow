# evaluator - Golden evaluation utilities
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .datasets import GoldenCase, load_golden_cases

@dataclass
class GoldenOutput:
    """Output structure for golden evaluation results."""
    case_id: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    final_verdict: str = "pending"
    score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.case_id and "case_id" in self.content:
            self.case_id = self.content["case_id"]

@dataclass
class EvaluationResult:
    """Result from evaluating a single case"""
    case_id: str
    actual_output: Dict[str, Any]
    expected_output: Dict[str, Any]
    passed: bool
    score: float
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}

@dataclass
class EvaluationSummary:
    """Summary of evaluation results"""
    total_cases: int
    passed_cases: int
    failed_cases: int
    average_score: float
    pass_rate: float
    results: List[EvaluationResult]
    
    @property
    def success(self) -> bool:
        """Overall evaluation success"""
        return self.pass_rate >= 0.8

class GoldenEvaluator:
    """Evaluates model outputs against golden cases"""
    
    def __init__(self, tolerance: float = 0.1):
        self.tolerance = tolerance
    
    def evaluate_case_output(self, case_id: str, actual_output: Dict[str, Any], expected_output: Dict[str, Any]) -> EvaluationResult:
        """Evaluate a single case output"""
        # Simple evaluation logic - compare expected and actual
        passed = True
        score = 1.0
        details = {}
        
        # Check if outputs match
        for key, expected_value in expected_output.items():
            if key not in actual_output:
                passed = False
                score -= 0.5
                details[f"missing_{key}"] = f"Expected {key} not found in output"
            else:
                actual_value = actual_output[key]
                if isinstance(expected_value, (int, float)) and isinstance(actual_value, (int, float)):
                    if abs(actual_value - expected_value) > self.tolerance:
                        passed = False
                        score -= 0.3
                        details[f"{key}_mismatch"] = f"Expected {expected_value}, got {actual_value}"
                elif expected_value != actual_value:
                    passed = False
                    score -= 0.3
                    details[f"{key}_mismatch"] = f"Expected {expected_value}, got {actual_value}"
        
        score = max(0.0, score)
        
        return EvaluationResult(
            case_id=case_id,
            actual_output=actual_output,
            expected_output=expected_output,
            passed=passed,
            score=score,
            details=details
        )
    
    def evaluate_dataset(self, dataset_name: str = "default", model_output_func: Optional[callable] = None) -> EvaluationSummary:
        """Evaluate a complete golden dataset"""
        cases = load_golden_cases(dataset_name)
        results = []
        
        for case in cases:
            if model_output_func:
                actual_output = model_output_func(case.input_data)
            else:
                # Mock actual output for testing
                actual_output = case.expected_output
            
            result = self.evaluate_case_output(
                case.case_id,
                actual_output,
                case.expected_output
            )
            results.append(result)
        
        # Calculate summary statistics
        total_cases = len(results)
        passed_cases = sum(1 for r in results if r.passed)
        failed_cases = total_cases - passed_cases
        average_score = sum(r.score for r in results) / total_cases if total_cases > 0 else 0.0
        pass_rate = passed_cases / total_cases if total_cases > 0 else 0.0
        
        return EvaluationSummary(
            total_cases=total_cases,
            passed_cases=passed_cases,
            failed_cases=failed_cases,
            average_score=average_score,
            pass_rate=pass_rate,
            results=results
        )

# Global evaluator instance
_global_evaluator: Optional[GoldenEvaluator] = None

def get_golden_evaluator() -> GoldenEvaluator:
    """Get the global golden evaluator"""
    global _global_evaluator
    if _global_evaluator is None:
        _global_evaluator = GoldenEvaluator()
    return _global_evaluator

def evaluate_case_output(case: GoldenCase, output: GoldenOutput) -> GoldenOutput:
    """Evaluate a case output using the global evaluator"""
    evaluator = get_golden_evaluator()
    
    # Create evaluation result
    result = evaluator.evaluate_case_output(
        case.id,
        output.__dict__,
        case.expected_output
    )
    
    # Update the output with evaluation results
    if result.passed:
        output.final_verdict = "pass"
    else:
        output.final_verdict = "fail"
    
    return output

def reset_golden_evaluator() -> None:
    """Reset the global golden evaluator (for testing)"""
    global _global_evaluator
    _global_evaluator = None
