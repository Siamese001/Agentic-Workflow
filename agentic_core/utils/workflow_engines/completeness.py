"""
Phase A: Context Completeness Scorer and Parent-Child Expander Interfaces.

Extends the L1 RAG C0 pipeline with:
- IParentChildExpander: reconstructs parent section from child chunk
- IContextCompletenessScorer: scores whether retrieved evidence preserves
  condition, action, exception, scope, and temporal qualifier
- IAnswerSupportValidator: validates that the answer is grounded in the
  reconstructed evidence span, not just the highest-similarity chunk

SOVEREIGNTY RULE: All outputs remain informational only (C0).
No retrieval output may alter route mode, safety thresholds, or execution
tiering.  These interfaces only add observability signals and richer context.
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from agentic_core.L0_routing.config.pipeline_constants import BATCH_SIZE, MAX_RETRIES

# Configuration constants
BUFFER_SIZE = 4096
DEFAULT_SLEEP = 0.1
THRESHOLD = 0.8


@dataclass(frozen=True)
class ContextCompletenessScore:
    """Scores whether a retrieved chunk preserves all required context elements.

    C0 RULE: Informational only — must not mutate routing, safety, or tiers.
    """

    query_id: str
    chunk_id: str
    parent_section_id: str
    relevance_score: float
    completeness_score: float
    missing_condition: bool
    missing_exception: bool
    missing_scope: bool
    missing_temporal_qualifier: bool
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_id": self.query_id,
            "chunk_id": self.chunk_id,
            "parent_section_id": self.parent_section_id,
            "relevance_score": round(self.relevance_score, 6),
            "completeness_score": round(self.completeness_score, 6),
            "missing_condition": self.missing_condition,
            "missing_exception": self.missing_exception,
            "missing_scope": self.missing_scope,
            "missing_temporal_qualifier": self.missing_temporal_qualifier,
            "confidence": round(self.confidence, 6),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ContextCompletenessScore:
        return cls(
            query_id=data["query_id"],
            chunk_id=data["chunk_id"],
            parent_section_id=data["parent_section_id"],
            relevance_score=float(data["relevance_score"]),
            completeness_score=float(data["completeness_score"]),
            missing_condition=bool(data["missing_condition"]),
            missing_exception=bool(data["missing_exception"]),
            missing_scope=bool(data["missing_scope"]),
            missing_temporal_qualifier=bool(data["missing_temporal_qualifier"]),
            confidence=float(data["confidence"]),
        )

    def canonical_bytes(self) -> bytes:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    @property
    def is_complete(self) -> bool:
        """True only when no required context element is missing."""
        return not (
            self.missing_condition
            or self.missing_exception
            or self.missing_scope
            or self.missing_temporal_qualifier
        )

    @property
    def missing_count(self) -> int:
        return sum(
            [
                self.missing_condition,
                self.missing_exception,
                self.missing_scope,
                self.missing_temporal_qualifier,
            ],
        )


@dataclass
class GroundedDocument:
    """A Document augmented with parent-section reconstruction and completeness score.

    Extends Document to carry parent context and completeness metadata.
    C0 RULE: Informational only.
    """

    # Document interface fields
    doc_id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    parent_section_id: str = ""
    parent_content: str = ""
    sibling_ids: list[str] = field(default_factory=list)
    heading_path: list[str] = field(default_factory=list)
    completeness_score: ContextCompletenessScore | None = None
    expanded: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "content": self.content,
            "metadata": self.metadata,
            "parent_section_id": self.parent_section_id,
            "parent_content": self.parent_content,
            "sibling_ids": list(self.sibling_ids),
            "heading_path": list(self.heading_path),
            "completeness": self.completeness_score.to_dict() if self.completeness_score else None,
            "expanded": self.expanded,
        }


class IParentChildExpander(ABC):
    """Reconstructs parent section context from a child chunk match.

    C0 RULE: Provides richer context only. Does not authorize execution.
    """

    @abstractmethod
    def expand(self, child: Document, neighbor_window: int = 1) -> GroundedDocument:
        """Expand a child chunk to include its parent section and neighbors.

        Args:
            child: The child chunk from retrieval.
            neighbor_window: Number of sibling chunks to include on each side.

        Returns:
            GroundedDocument with parent section content populated.
        """
        ...

    @abstractmethod
    def get_parent_section_id(self, chunk_id: str) -> str | None:
        """Return the parent section ID for a given chunk ID, or None."""
        ...

    @abstractmethod
    def get_heading_path(self, chunk_id: str) -> list[str]:
        """Return the heading hierarchy path for a given chunk ID."""
        ...


class IContextCompletenessScorer(ABC):
    """Scores retrieved evidence for contextual completeness.

    Determines whether the retrieved fragment preserves:
    - condition (if/when/unless clauses)
    - action (the main operation or result)
    - exception (edge-case or error handling)
    - scope (which entities, versions, or domains apply)
    - temporal qualifier (effective dates, deprecation, version ranges)

    C0 RULE: Scores are informational telemetry only.
    """

    @abstractmethod
    def score(
        self,
        query_id: str,
        query: str,
        chunk: Document | GroundedDocument,
    ) -> ContextCompletenessScore:
        """Score the completeness of a chunk relative to the query.

        Args:
            query_id: Stable identifier for this query.
            query: The original user query text.
            chunk: The retrieved (and optionally expanded) document.

        Returns:
            ContextCompletenessScore with per-dimension flags.
        """
        ...

    @abstractmethod
    def score_batch(
        self,
        query_id: str,
        query: str,
        chunks: list[Document | GroundedDocument],
    ) -> list[ContextCompletenessScore]:
        """Score a batch of chunks for a single query.

        Returns scores in the same order as input chunks.
        """
        ...


class IAnswerSupportValidator(ABC):
    """Validates that the final answer is supported by the reconstructed evidence.

    Checks the answer against cited chunks AND cited parent sections.
    Detects unsupported claims and emits a SupportedAnswerCheck artifact.

    C0 RULE: Emits observability telemetry only. Never becomes a hidden
    authority bypass. Must not gate execution without explicit governance routing.
    """

    @abstractmethod
    def validate(
        self,
        answer_id: str,
        answer: str,
        cited_chunks: list[Document | GroundedDocument],
        cited_parent_sections: list[str],
    ) -> SupportedAnswerCheck:
        """Validate that an answer is grounded in the provided evidence.

        Args:
            answer_id: Stable identifier for this answer.
            answer: The generated answer text.
            cited_chunks: Retrieved chunks used to generate the answer.
            cited_parent_sections: Parent section content strings.

        Returns:
            SupportedAnswerCheck artifact.
        """
        ...


@dataclass(frozen=True)
class SupportedAnswerCheck:
    """Artifact recording whether an answer is supported by full evidence span.

    C0 RULE: Written to RetrievalEvaluationRegistry as observability telemetry.
    Must not be used as a hidden authority gate without explicit governance routing.
    """

    answer_id: str
    cited_chunk_ids: tuple[str, ...]
    cited_parent_section_ids: tuple[str, ...]
    fully_supported: bool
    unsupported_claim_spans: tuple[str, ...]
    support_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "answer_id": self.answer_id,
            "cited_chunk_ids": list(self.cited_chunk_ids),
            "cited_parent_section_ids": list(self.cited_parent_section_ids),
            "fully_supported": self.fully_supported,
            "unsupported_claim_spans": list(self.unsupported_claim_spans),
            "support_score": round(self.support_score, 6),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SupportedAnswerCheck:
        return cls(
            answer_id=data["answer_id"],
            cited_chunk_ids=tuple(data["cited_chunk_ids"]),
            cited_parent_section_ids=tuple(data["cited_parent_section_ids"]),
            fully_supported=bool(data["fully_supported"]),
            unsupported_claim_spans=tuple(data["unsupported_claim_spans"]),
            support_score=float(data["support_score"]),
        )

    def canonical_bytes(self) -> bytes:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


__all__ = [
    "ContextCompletenessScore",
    "GroundedDocument",
    "IParentChildExpander",
    "IContextCompletenessScorer",
    "IAnswerSupportValidator",
    "SupportedAnswerCheck",
    # Configuration constants
    "BATCH_SIZE",
    "BUFFER_SIZE",
    "DEFAULT_SLEEP",
    "MAX_RETRIES",
    "THRESHOLD",
]
