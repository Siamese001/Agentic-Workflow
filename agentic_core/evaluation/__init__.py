"""
Evaluation Foundation Spine

Deterministic evaluation subsystem for measuring retrieval quality,
answer quality, safety compliance, and hallucination risk.

Integrates with L6 Observability, L4 State Registry, and Meta Learning Pipeline.
"""

try:
    from .runners.offline_eval_runner import OfflineEvaluationRunner
    from .runners.replay_eval_runner import ReplayEvaluationRunner
except ModuleNotFoundError:
    OfflineEvaluationRunner = None  # type: ignore[assignment,misc]
    ReplayEvaluationRunner = None  # type: ignore[assignment,misc]

try:
    from .schemas.evaluation_dataset_schema import EvaluationExample
except ModuleNotFoundError:
    EvaluationExample = None  # type: ignore[assignment,misc]

try:
    from .schemas.evaluation_result_schema import EvaluationReport, EvaluationResult
except ModuleNotFoundError:
    EvaluationReport = None  # type: ignore[assignment,misc]
    EvaluationResult = None  # type: ignore[assignment,misc]

__all__ = [
    "EvaluationExample",
    "EvaluationResult",
    "EvaluationReport",
    "OfflineEvaluationRunner",
    "ReplayEvaluationRunner",
]
