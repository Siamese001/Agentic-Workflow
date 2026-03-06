"""
Evaluation Foundation Spine

Deterministic evaluation subsystem for measuring retrieval quality,
answer quality, safety compliance, and hallucination risk.

Integrates with L6 Observability, L4 State Registry, and Meta Learning Pipeline.
"""

from .runners.offline_eval_runner import OfflineEvaluationRunner
from .runners.replay_eval_runner import ReplayEvaluationRunner
from .schemas.evaluation_dataset_schema import EvaluationExample
from .schemas.evaluation_result_schema import EvaluationReport, EvaluationResult

__all__ = [
    "EvaluationExample",
    "EvaluationResult",
    "EvaluationReport",
    "OfflineEvaluationRunner",
    "ReplayEvaluationRunner",
]
