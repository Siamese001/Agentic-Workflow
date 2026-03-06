"""
Phase 5: Human Feedback Schemas

Defines ReviewRubric, FeedbackExample, and DPO pair structures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReviewRubric:
    """Human review rubric for a single model response."""
    grounded: bool
    useful: bool
    correct: bool
    safe: bool
    missing_context: bool
    reviewer_id: str = ""
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "grounded": self.grounded,
            "useful": self.useful,
            "correct": self.correct,
            "safe": self.safe,
            "missing_context": self.missing_context,
            "reviewer_id": self.reviewer_id,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReviewRubric:
        return cls(
            grounded=data["grounded"],
            useful=data["useful"],
            correct=data["correct"],
            safe=data["safe"],
            missing_context=data["missing_context"],
            reviewer_id=data.get("reviewer_id", ""),
            notes=data.get("notes", ""),
        )

    @property
    def is_positive(self) -> bool:
        """True if the review is overall positive (all critical dimensions pass)."""
        return self.grounded and self.useful and self.correct and self.safe

    @property
    def quality_score(self) -> float:
        """Numeric quality score [0.0, 1.0] computed from rubric dimensions."""
        dimensions = [self.grounded, self.useful, self.correct, self.safe]
        penalty = 0.1 if self.missing_context else 0.0
        raw = sum(1 for d in dimensions if d) / len(dimensions)
        return max(0.0, raw - penalty)


@dataclass
class FeedbackExample:
    """A single human-annotated feedback example for training or evaluation."""
    example_id: str
    query: str
    model_answer: str
    human_annotation: ReviewRubric
    context_documents: list[str]
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "example_id": self.example_id,
            "query": self.query,
            "model_answer": self.model_answer,
            "human_annotation": self.human_annotation.to_dict(),
            "context_documents": self.context_documents,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FeedbackExample:
        return cls(
            example_id=data["example_id"],
            query=data["query"],
            model_answer=data["model_answer"],
            human_annotation=ReviewRubric.from_dict(data["human_annotation"]),
            context_documents=data["context_documents"],
            timestamp=data["timestamp"],
            metadata=data.get("metadata", {}),
        )


@dataclass(frozen=True)
class DPOPair:
    """A Direct Preference Optimization training pair (chosen vs rejected)."""
    pair_id: str
    query: str
    chosen_response: str
    rejected_response: str
    context_documents: list[str]
    chosen_score: float
    rejected_score: float
    source_example_ids: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pair_id": self.pair_id,
            "query": self.query,
            "chosen_response": self.chosen_response,
            "rejected_response": self.rejected_response,
            "context_documents": list(self.context_documents),
            "chosen_score": self.chosen_score,
            "rejected_score": self.rejected_score,
            "source_example_ids": list(self.source_example_ids),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DPOPair:
        return cls(
            pair_id=data["pair_id"],
            query=data["query"],
            chosen_response=data["chosen_response"],
            rejected_response=data["rejected_response"],
            context_documents=data["context_documents"],
            chosen_score=data["chosen_score"],
            rejected_score=data["rejected_score"],
            source_example_ids=data["source_example_ids"],
            metadata=data.get("metadata", {}),
        )


@dataclass(frozen=True)
class DPOBatch:
    """A batch of DPO training pairs ready for fine-tuning."""
    batch_id: str
    timestamp: str
    pair_count: int
    pairs: list[DPOPair]
    source_feedback_count: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "timestamp": self.timestamp,
            "pair_count": self.pair_count,
            "pairs": [p.to_dict() for p in self.pairs],
            "source_feedback_count": self.source_feedback_count,
            "metadata": dict(self.metadata),
        }


__all__ = [
    "ReviewRubric",
    "FeedbackExample",
    "DPOPair",
    "DPOBatch",
]
