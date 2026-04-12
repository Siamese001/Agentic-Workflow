"""Evaluation metrics package."""

from .base import ClassificationMetric, EvaluationMetric, GenerationMetric, RetrievalMetric

try:
    from .answer_correctness import AnswerCorrectness
except ModuleNotFoundError:
    AnswerCorrectness = None
try:
    from .classification import BinaryClassificationMetric, ConfusionMatrix, MultiClassF1Metric
except ModuleNotFoundError:
    BinaryClassificationMetric = None
    ConfusionMatrix = None
    MultiClassF1Metric = None
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
    ChunkStrategyReport = None
    CompletenessExperimentReport = None
    EvaluationDeltaReport = None
    EvaluationMetricResult = None
    EvaluationReport = None
    RetrievalExperimentReport = None
try:
    from .groundedness import Groundedness
except ModuleNotFoundError:
    Groundedness = None
try:
    from .mrr import MeanReciprocalRank
except ModuleNotFoundError:
    MeanReciprocalRank = None
try:
    from .f1_score import F1Score
except ModuleNotFoundError:
    F1Score = None
try:
    from .ndcg import NDCG
except ModuleNotFoundError:
    NDCG = None
try:
    from .precision_at_k import PrecisionAtK
except ModuleNotFoundError:
    PrecisionAtK = None
try:
    from .recall_at_k import RecallAtK
except ModuleNotFoundError:
    RecallAtK = None
__all__ = [
    "EvaluationMetric",
    "RetrievalMetric",
    "GenerationMetric",
    "ClassificationMetric",
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
    "ConfusionMatrix",
    "BinaryClassificationMetric",
    "MultiClassF1Metric",
    "F1Score",
]
