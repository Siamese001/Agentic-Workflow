# judge - Golden evaluation judge utilities
from typing import Dict, Any
from dataclasses import dataclass
import re
from .models import GoldenStateTestCase

@dataclass
class EvaluationVerdict:
    """Verdict from golden evaluation"""
    rating: str
    score: float
    details: Dict[str, Any]

def evaluate_output(test_case: GoldenStateTestCase, output: str) -> EvaluationVerdict:
    """Evaluate output against golden test case"""
    if not output:
        return EvaluationVerdict(
            rating="fail",
            score=0.0,
            details={"reason": "empty_output"}
        )
    
    # If no expected behavior specified, pass if output exists
    if not test_case.expected_behavior:
        return EvaluationVerdict(
            rating="pass",
            score=1.0,
            details={"reason": "no_behavior_specified"}
        )
    
    # Filter stop words and extract content words
    stop_words = {"should", "be", "is", "a", "this", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
    
    # Extract words and normalize
    expected_words = set(word.lower().strip('.,!?') for word in test_case.expected_behavior.split() 
                        if word.lower().strip('.,!?') not in stop_words)
    output_words = set(word.lower().strip('.,!?') for word in output.split() 
                      if word.lower().strip('.,!?') not in stop_words)
    
    # Check for key word overlap
    common_words = expected_words.intersection(output_words)
    
    # If significant overlap (>= 50% of expected words), consider it a pass
    if expected_words and len(common_words) >= len(expected_words) * 0.5:
        return EvaluationVerdict(
            rating="pass",
            score=1.0,
            details={"reason": "key_behavior_detected", "matched_words": list(common_words)}
        )
    elif expected_words:
        # Partial score based on word overlap
        score = len(common_words) / len(expected_words)
        return EvaluationVerdict(
            rating="partial",
            score=score,
            details={"reason": "partial_match", "matched_words": list(common_words)}
        )
    else:
        # No content words in expected behavior, pass based on output existence
        return EvaluationVerdict(
            rating="pass",
            score=1.0,
            details={"reason": "no_content_words_in_behavior"}
        )
