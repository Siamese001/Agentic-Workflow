"""
Golden Evaluation Modules Package.

Deterministic evaluation contracts for golden datasets.
"""

from .injection_regression_suite import evaluate_injection_regression
from .resume_quality_evaluator import evaluate_resume_quality
from .tool_use_ground_truth_evaluator import evaluate_tool_use_ground_truth

__all__ = ["evaluate_resume_quality", "evaluate_injection_regression", "evaluate_tool_use_ground_truth"]
