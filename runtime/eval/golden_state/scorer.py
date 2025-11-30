# scorer - Golden evaluation scoring utilities
from typing import Dict, Any, List
from dataclasses import dataclass
from .models import JudgeVerdict

@dataclass
class AggregatedScore:
    """Aggregated score from multiple verdicts"""
    average_score: float
    pass_rate: float
    total_verdicts: int
    passed_verdicts: int
    failed_verdicts: int

def aggregate_scores(verdicts: List[JudgeVerdict]) -> Dict[str, float]:
    """Aggregate scores from multiple judge verdicts"""
    if not verdicts:
        return {
            "avg_score": 0.0,
            "pass_rate": 0.0,
            "pass_count": 0,
            "fail_count": 0,
            "total": 0
        }
    
    total_score = sum(v.score for v in verdicts)
    average_score = total_score / len(verdicts)
    
    passed_count = sum(1 for v in verdicts if v.rating in ["pass"])
    failed_count = sum(1 for v in verdicts if v.rating in ["fail"])
    pass_rate = passed_count / len(verdicts)
    
    return {
        "avg_score": average_score,
        "pass_rate": pass_rate,
        "pass_count": passed_count,
        "fail_count": failed_count,
        "total": len(verdicts)
    }
