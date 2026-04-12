"""Base metric classes for evaluation framework."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class EvaluationMetric(ABC):
    """Abstract base class for all evaluation metrics."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def compute(self, **kwargs: Any) -> float: ...


class GenerationMetric(EvaluationMetric):
    """Base class for generation quality metrics (answer correctness, groundedness)."""

    pass


class RetrievalMetric(EvaluationMetric):
    """Base class for retrieval quality metrics (precision, recall, MRR, NDCG)."""

    pass
