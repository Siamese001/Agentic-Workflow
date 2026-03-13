"""
Evaluation Result and Report Schemas

Defines immutable structures for evaluation results, reports, and L4 snapshots.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EvaluationResult:
    """Result for a single evaluation example across one or more metrics."""

    example_id: str
    query: str
    retrieved_doc_ids: list[str]
    generated_answer: str
    metric_scores: dict[str, float]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "example_id": self.example_id,
            "query": self.query,
            "retrieved_doc_ids": list(self.retrieved_doc_ids),
            "generated_answer": self.generated_answer,
            "metric_scores": dict(self.metric_scores),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvaluationResult:
        return cls(
            example_id=data["example_id"],
            query=data["query"],
            retrieved_doc_ids=data["retrieved_doc_ids"],
            generated_answer=data["generated_answer"],
            metric_scores=data["metric_scores"],
            metadata=data.get("metadata", {}),
        )


@dataclass(frozen=True)
class EvaluationReport:
    """Aggregate report across all examples in an evaluation run."""

    run_id: str
    dataset_name: str
    dataset_version: str
    system_version: str
    timestamp: str
    aggregate_scores: dict[str, float]
    per_example_results: list[EvaluationResult]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "dataset_name": self.dataset_name,
            "dataset_version": self.dataset_version,
            "system_version": self.system_version,
            "timestamp": self.timestamp,
            "aggregate_scores": dict(self.aggregate_scores),
            "per_example_results": [r.to_dict() for r in self.per_example_results],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvaluationReport:
        return cls(
            run_id=data["run_id"],
            dataset_name=data["dataset_name"],
            dataset_version=data["dataset_version"],
            system_version=data["system_version"],
            timestamp=data["timestamp"],
            aggregate_scores=data["aggregate_scores"],
            per_example_results=[EvaluationResult.from_dict(r) for r in data.get("per_example_results", [])],
            metadata=data.get("metadata", {}),
        )


@dataclass(frozen=True)
class EvaluationSnapshot:
    """L4 state registry artifact: snapshot of an evaluation run for persistence."""

    timestamp: str
    system_version: str
    dataset_version: str
    metric_results: dict[str, float]
    run_id: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "system_version": self.system_version,
            "dataset_version": self.dataset_version,
            "metric_results": dict(self.metric_results),
            "run_id": self.run_id,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvaluationSnapshot:
        return cls(
            timestamp=data["timestamp"],
            system_version=data["system_version"],
            dataset_version=data["dataset_version"],
            metric_results=data["metric_results"],
            run_id=data["run_id"],
            metadata=data.get("metadata", {}),
        )


@dataclass(frozen=True)
class DeltaReport:
    """Comparison report between two system configurations."""

    run_id_a: str
    run_id_b: str
    config_a_name: str
    config_b_name: str
    timestamp: str
    metric_deltas: dict[str, float]
    scores_a: dict[str, float]
    scores_b: dict[str, float]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id_a": self.run_id_a,
            "run_id_b": self.run_id_b,
            "config_a_name": self.config_a_name,
            "config_b_name": self.config_b_name,
            "timestamp": self.timestamp,
            "metric_deltas": dict(self.metric_deltas),
            "scores_a": dict(self.scores_a),
            "scores_b": dict(self.scores_b),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DeltaReport:
        return cls(
            run_id_a=data["run_id_a"],
            run_id_b=data["run_id_b"],
            config_a_name=data["config_a_name"],
            config_b_name=data["config_b_name"],
            timestamp=data["timestamp"],
            metric_deltas=data["metric_deltas"],
            scores_a=data["scores_a"],
            scores_b=data["scores_b"],
            metadata=data.get("metadata", {}),
        )


__all__ = ["EvaluationResult", "EvaluationReport", "EvaluationSnapshot", "DeltaReport"]
