"""
Phase F: Path D HITL Extension — Completeness-Specific Reviewer Rubric.

Extends ReviewRubric with completeness-specific fields so humans can label
incompleteness failure modes.

New artifacts:
  CompletenessReviewRubric — extends ReviewRubric with 6 new dimensions
  CompletenessFeedbackExample — carries retrieved_chunks and expanded_parent_context

INTENT: Create labeled examples for 'relevant chunk, incomplete context, wrong answer'.
Integrates with existing deterministic HITL and DPO flows without breaking
existing routing or evidence contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.evaluation.feedback.schemas import ReviewRubric


@dataclass
class CompletenessReviewRubric(ReviewRubric):
    """Extends ReviewRubric with completeness-specific failure mode labels.

    New dimensions map directly to the ContextCompletenessScore dimensions:
      missing_condition          — answer required a condition not in retrieved context
      missing_exception          — answer required an exception clause not retrieved
      missing_scope              — answer required scope constraints not in context
      missing_temporal_qualifier — answer required temporal/version info not retrieved
      incomplete_parent_context  — parent section was available but not used
      answer_not_fully_supported — answer makes claims beyond the evidence span
    """

    missing_condition: bool = False
    missing_exception: bool = False
    missing_scope: bool = False
    missing_temporal_qualifier: bool = False
    incomplete_parent_context: bool = False
    answer_not_fully_supported: bool = False

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base.update(
            {
                "missing_condition": self.missing_condition,
                "missing_exception": self.missing_exception,
                "missing_scope": self.missing_scope,
                "missing_temporal_qualifier": self.missing_temporal_qualifier,
                "incomplete_parent_context": self.incomplete_parent_context,
                "answer_not_fully_supported": self.answer_not_fully_supported,
            }
        )
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CompletenessReviewRubric:
        return cls(
            grounded=data["grounded"],
            useful=data["useful"],
            correct=data["correct"],
            safe=data["safe"],
            missing_context=data["missing_context"],
            reviewer_id=data.get("reviewer_id", ""),
            notes=data.get("notes", ""),
            missing_condition=bool(data.get("missing_condition", False)),
            missing_exception=bool(data.get("missing_exception", False)),
            missing_scope=bool(data.get("missing_scope", False)),
            missing_temporal_qualifier=bool(data.get("missing_temporal_qualifier", False)),
            incomplete_parent_context=bool(data.get("incomplete_parent_context", False)),
            answer_not_fully_supported=bool(data.get("answer_not_fully_supported", False)),
        )

    @property
    def completeness_failure_count(self) -> int:
        """Count of completeness-specific failures labeled."""
        return sum(
            [
                self.missing_condition,
                self.missing_exception,
                self.missing_scope,
                self.missing_temporal_qualifier,
                self.incomplete_parent_context,
                self.answer_not_fully_supported,
            ]
        )

    @property
    def has_completeness_failure(self) -> bool:
        """True if any completeness dimension was labeled as failing."""
        return self.completeness_failure_count > 0

    @property
    def quality_score(self) -> float:
        """Extended quality score including completeness penalty."""
        base_dimensions = [self.grounded, self.useful, self.correct, self.safe]
        base_raw = sum(1 for d in base_dimensions if d) / len(base_dimensions)
        context_penalty = 0.1 if self.missing_context else 0.0
        completeness_penalty = 0.05 * self.completeness_failure_count
        return max(0.0, base_raw - context_penalty - completeness_penalty)


@dataclass
class CompletenessFeedbackExample:
    """Human-annotated feedback example for completeness-specific failures.

    Captures the 'relevant chunk, incomplete context, wrong answer' pattern.
    Integrates with existing DPO flows via support_failure_reason.
    """

    example_id: str
    query: str
    model_answer: str
    retrieved_chunks: list[str]
    expanded_parent_context: list[str]
    human_annotation: CompletenessReviewRubric
    support_failure_reason: str
    context_documents: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "example_id": self.example_id,
            "query": self.query,
            "model_answer": self.model_answer,
            "retrieved_chunks": list(self.retrieved_chunks),
            "expanded_parent_context": list(self.expanded_parent_context),
            "human_annotation": self.human_annotation.to_dict(),
            "support_failure_reason": self.support_failure_reason,
            "context_documents": list(self.context_documents),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CompletenessFeedbackExample:
        return cls(
            example_id=data["example_id"],
            query=data["query"],
            model_answer=data["model_answer"],
            retrieved_chunks=list(data["retrieved_chunks"]),
            expanded_parent_context=list(data["expanded_parent_context"]),
            human_annotation=CompletenessReviewRubric.from_dict(data["human_annotation"]),
            support_failure_reason=data["support_failure_reason"],
            context_documents=list(data["context_documents"]),
            metadata=dict(data.get("metadata", {})),
        )

    @property
    def is_right_chunk_wrong_context(self) -> bool:
        """True when the retrieved chunk was relevant but context was incomplete."""
        return self.human_annotation.grounded and self.human_annotation.has_completeness_failure


__all__ = ["CompletenessReviewRubric", "CompletenessFeedbackExample"]
