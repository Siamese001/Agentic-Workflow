"""
Golden Evaluation Modules Package.

Deterministic evaluation contracts for golden datasets.
"""

from .injection_regression_suite import evaluate_injection_regression
from .resume_quality_evaluator import evaluate_resume_quality
from .tool_use_ground_truth_evaluator import evaluate_tool_use_ground_truth

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

__all__ = ["evaluate_resume_quality", "evaluate_injection_regression", "evaluate_tool_use_ground_truth"]
