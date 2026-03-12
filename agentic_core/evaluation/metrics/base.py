"""
Base Metric Interface

All evaluation metrics must implement the EvaluationMetric protocol.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class EvaluationMetric(ABC):
    """Abstract base for all evaluation metrics."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Metric name used as key in result dictionaries."""
        ...

    @abstractmethod
    def compute(self, prediction: Any, ground_truth: Any, context: Any=None) -> float:
        """Compute metric score.

        Args:
            prediction: Model prediction (retrieved docs, generated answer, etc.)
            ground_truth: Ground truth for comparison
            context: Optional additional context for the computation

        Returns:
            Float score in [0.0, 1.0] unless stated otherwise in subclass
        """
        ...

class RetrievalMetric(EvaluationMetric):
    """Base class for retrieval-oriented metrics.

    prediction = list of retrieved doc IDs (ranked)
    ground_truth = list of relevant doc IDs
    """

    @abstractmethod
    def compute(self, prediction: list[str], ground_truth: list[str], context: Any=None) -> float:
        ...

class GenerationMetric(EvaluationMetric):
    """Base class for generation-oriented metrics.

    prediction = generated answer string
    ground_truth = expected answer string
    context = retrieved documents used for generation
    """

    @abstractmethod
    def compute(self, prediction: str, ground_truth: str, context: Any=None) -> float:
        ...
__all__ = ['EvaluationMetric', 'RetrievalMetric', 'GenerationMetric']
