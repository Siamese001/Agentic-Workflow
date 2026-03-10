"""
Phase 4: Monitoring Snapshot Schemas

Immutable snapshot types for retrieval drift, embedding health, and
answer quality drift.  All snapshots are persisted in the L4 telemetry registry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@dataclass(frozen=True)
class RetrievalDriftSnapshot:
    """Snapshot of retrieval health metrics at a point in time."""
    timestamp: str
    system_version: str
    retrieval_hit_rate: float
    score_distribution_mean: float
    score_distribution_std: float
    top_k_stability: float
    sample_size: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_type": "retrieval_drift",
            "timestamp": self.timestamp,
            "system_version": self.system_version,
            "retrieval_hit_rate": self.retrieval_hit_rate,
            "score_distribution_mean": self.score_distribution_mean,
            "score_distribution_std": self.score_distribution_std,
            "top_k_stability": self.top_k_stability,
            "sample_size": self.sample_size,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RetrievalDriftSnapshot:
        return cls(
            timestamp=data["timestamp"],
            system_version=data["system_version"],
            retrieval_hit_rate=data["retrieval_hit_rate"],
            score_distribution_mean=data["score_distribution_mean"],
            score_distribution_std=data["score_distribution_std"],
            top_k_stability=data["top_k_stability"],
            sample_size=data["sample_size"],
            metadata=data.get("metadata", {}),
        )


@dataclass(frozen=True)
class EmbeddingHealthSnapshot:
    """Snapshot of embedding model health metrics."""
    timestamp: str
    embedding_model_version: str
    vector_norm_mean: float
    vector_norm_std: float
    similarity_distribution_mean: float
    similarity_distribution_std: float
    version_mismatch_detected: bool
    sample_size: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_type": "embedding_health",
            "timestamp": self.timestamp,
            "embedding_model_version": self.embedding_model_version,
            "vector_norm_mean": self.vector_norm_mean,
            "vector_norm_std": self.vector_norm_std,
            "similarity_distribution_mean": self.similarity_distribution_mean,
            "similarity_distribution_std": self.similarity_distribution_std,
            "version_mismatch_detected": self.version_mismatch_detected,
            "sample_size": self.sample_size,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EmbeddingHealthSnapshot:
        return cls(
            timestamp=data["timestamp"],
            embedding_model_version=data["embedding_model_version"],
            vector_norm_mean=data["vector_norm_mean"],
            vector_norm_std=data["vector_norm_std"],
            similarity_distribution_mean=data["similarity_distribution_mean"],
            similarity_distribution_std=data["similarity_distribution_std"],
            version_mismatch_detected=data["version_mismatch_detected"],
            sample_size=data["sample_size"],
            metadata=data.get("metadata", {}),
        )


@dataclass(frozen=True)
class AnswerQualitySnapshot:
    """Snapshot of answer quality drift metrics."""
    timestamp: str
    system_version: str
    groundedness_rate: float
    hallucination_rate: float
    human_override_rate: float
    answer_correctness_mean: float
    sample_size: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_type": "answer_quality",
            "timestamp": self.timestamp,
            "system_version": self.system_version,
            "groundedness_rate": self.groundedness_rate,
            "hallucination_rate": self.hallucination_rate,
            "human_override_rate": self.human_override_rate,
            "answer_correctness_mean": self.answer_correctness_mean,
            "sample_size": self.sample_size,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AnswerQualitySnapshot:
        return cls(
            timestamp=data["timestamp"],
            system_version=data["system_version"],
            groundedness_rate=data["groundedness_rate"],
            hallucination_rate=data["hallucination_rate"],
            human_override_rate=data["human_override_rate"],
            answer_correctness_mean=data["answer_correctness_mean"],
            sample_size=data["sample_size"],
            metadata=data.get("metadata", {}),
        )


@dataclass(frozen=True)
class DriftAlert:
    """Triggered when a monitored metric crosses a degradation threshold."""
    alert_id: str
    timestamp: str
    alert_type: str
    metric_name: str
    current_value: float
    threshold_value: float
    delta: float
    severity: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "timestamp": self.timestamp,
            "alert_type": self.alert_type,
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "threshold_value": self.threshold_value,
            "delta": self.delta,
            "severity": self.severity,
            "message": self.message,
        }


__all__ = [
    "RetrievalDriftSnapshot",
    "EmbeddingHealthSnapshot",
    "AnswerQualitySnapshot",
    "DriftAlert",
]
