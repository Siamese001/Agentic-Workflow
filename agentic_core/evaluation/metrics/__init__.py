"""Evaluation metrics package."""

from .base import EvaluationMetric, GenerationMetric, RetrievalMetric

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

try:
    from .answer_correctness import AnswerCorrectness
except ModuleNotFoundError:
    AnswerCorrectness = None  # type: ignore[assignment,misc]

try:
    from .completeness_metrics import (
        ChunkStrategyReport,
        CompletenessExperimentReport,
        EvaluationDeltaReport,
        EvaluationMetricResult,
        EvaluationReport,
        RetrievalExperimentReport,
    )
except ModuleNotFoundError:
    ChunkStrategyReport = None  # type: ignore[assignment,misc]
    CompletenessExperimentReport = None  # type: ignore[assignment,misc]
    EvaluationDeltaReport = None  # type: ignore[assignment,misc]
    EvaluationMetricResult = None  # type: ignore[assignment,misc]
    EvaluationReport = None  # type: ignore[assignment,misc]
    RetrievalExperimentReport = None  # type: ignore[assignment,misc]

try:
    from .groundedness import Groundedness
except ModuleNotFoundError:
    Groundedness = None  # type: ignore[assignment,misc]

try:
    from .mrr import MeanReciprocalRank
except ModuleNotFoundError:
    MeanReciprocalRank = None  # type: ignore[assignment,misc]

try:
    from .ndcg import NDCG
except ModuleNotFoundError:
    NDCG = None  # type: ignore[assignment,misc]

try:
    from .precision_at_k import PrecisionAtK
except ModuleNotFoundError:
    PrecisionAtK = None  # type: ignore[assignment,misc]

try:
    from .recall_at_k import RecallAtK
except ModuleNotFoundError:
    RecallAtK = None  # type: ignore[assignment,misc]

__all__ = [
    "EvaluationMetric",
    "RetrievalMetric",
    "GenerationMetric",
    "PrecisionAtK",
    "RecallAtK",
    "MeanReciprocalRank",
    "NDCG",
    "Groundedness",
    "AnswerCorrectness",
    "EvaluationMetricResult",
    "EvaluationReport",
    "EvaluationDeltaReport",
    "RetrievalExperimentReport",
    "ChunkStrategyReport",
    "CompletenessExperimentReport",
]
