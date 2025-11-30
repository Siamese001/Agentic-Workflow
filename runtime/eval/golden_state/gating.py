# gating - Golden experiment gating utilities
from typing import Dict, Any

def gate_experiment(candidate: Dict[str, Any], baseline: Dict[str, Any]) -> bool:
    """Gate experiment based on baseline scores and candidate parameters."""
    # If no baseline provided, allow the experiment
    if not baseline:
        return True
    
    # Extract baseline metrics (thresholds)
    baseline_avg_score = baseline.get("avg_score", 0.0)
    baseline_pass_count = baseline.get("pass_count", 0)
    
    # Extract candidate metrics
    candidate_avg_score = candidate.get("avg_score", 0.0)
    candidate_pass_count = candidate.get("pass_count", 0)
    
    # Gating logic: allow if candidate meets or exceeds baseline thresholds
    if baseline_avg_score > 0 and candidate_avg_score < baseline_avg_score:
        return False
    
    if baseline_pass_count > 0 and candidate_pass_count < baseline_pass_count:
        return False
    
    return True
