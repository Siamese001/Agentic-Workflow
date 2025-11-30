# Uncertainty computation module
from typing import List
from .models import Hypothesis

def compute_uncertainty(hypotheses: List[Hypothesis], qa_signals: int = 0, safety_signals: int = 0) -> float:
    """Compute uncertainty score based on hypotheses and signals"""
    if not hypotheses:
        return 1.0
    
    # Base uncertainty from confidence variance
    confidences = [h.confidence for h in hypotheses]
    avg_confidence = sum(confidences) / len(confidences)
    variance = sum((c - avg_confidence) ** 2 for c in confidences) / len(confidences)
    
    # Increase uncertainty with conflicting signals
    signal_factor = (qa_signals + safety_signals) * 0.1
    
    # Combine factors (0.0 to 1.0)
    uncertainty = min(1.0, variance + signal_factor)
    
    return max(0.0, uncertainty)
