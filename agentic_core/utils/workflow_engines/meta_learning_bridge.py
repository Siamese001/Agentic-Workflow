"""
Phase E: Meta-Learning Bridge — Completeness-Aware EvaluationSignals.

Adds completeness-aware evaluation signals to the Meta-Learning input surface
and extends RAGProposer to emit completeness-driven proposals.

HARD REQUIREMENTS:
- All proposals remain proposal_only=True
- Replay validated, shadow validated, approval gated
- No proposal may directly activate without existing meta-learning commit controls

C0 RULE: Informational only. Proposals must flow through existing governance.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EvaluationSignals:
    """Completeness-aware evaluation signals for Meta-Learning input.

    Aggregates retrieval relevance, completeness, answer correctness,
    support validation, and drift metrics into a single immutable payload
    for RAGProposer consumption.

    All fields are read-only — signals flow into proposals only.
    C0 RULE: Informational only.
    """

    snapshot_id: str
    retrieval_relevance_mean: float
    retrieval_precision: float
    retrieval_recall: float
    mean_completeness_score: float
    missing_condition_rate: float
    missing_exception_rate: float
    missing_scope_rate: float
    missing_temporal_qualifier_rate: float
    answer_correctness_rate: float
    fully_supported_rate: float
    mean_support_score: float
    high_similarity_wrong_answer_rate: float
    parent_reconstruction_applied_rate: float
    chunk_fragmentation_error_rate: float
    observation_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "retrieval_relevance_mean": round(self.retrieval_relevance_mean, 6),
            "retrieval_precision": round(self.retrieval_precision, 6),
            "retrieval_recall": round(self.retrieval_recall, 6),
            "mean_completeness_score": round(self.mean_completeness_score, 6),
            "missing_condition_rate": round(self.missing_condition_rate, 6),
            "missing_exception_rate": round(self.missing_exception_rate, 6),
            "missing_scope_rate": round(self.missing_scope_rate, 6),
            "missing_temporal_qualifier_rate": round(self.missing_temporal_qualifier_rate, 6),
            "answer_correctness_rate": round(self.answer_correctness_rate, 6),
            "fully_supported_rate": round(self.fully_supported_rate, 6),
            "mean_support_score": round(self.mean_support_score, 6),
            "high_similarity_wrong_answer_rate": round(self.high_similarity_wrong_answer_rate, 6),
            "parent_reconstruction_applied_rate": round(self.parent_reconstruction_applied_rate, 6),
            "chunk_fragmentation_error_rate": round(self.chunk_fragmentation_error_rate, 6),
            "observation_count": self.observation_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvaluationSignals:
        return cls(
            snapshot_id=data["snapshot_id"],
            retrieval_relevance_mean=float(data["retrieval_relevance_mean"]),
            retrieval_precision=float(data["retrieval_precision"]),
            retrieval_recall=float(data["retrieval_recall"]),
            mean_completeness_score=float(data["mean_completeness_score"]),
            missing_condition_rate=float(data["missing_condition_rate"]),
            missing_exception_rate=float(data["missing_exception_rate"]),
            missing_scope_rate=float(data["missing_scope_rate"]),
            missing_temporal_qualifier_rate=float(data["missing_temporal_qualifier_rate"]),
            answer_correctness_rate=float(data["answer_correctness_rate"]),
            fully_supported_rate=float(data["fully_supported_rate"]),
            mean_support_score=float(data["mean_support_score"]),
            high_similarity_wrong_answer_rate=float(data["high_similarity_wrong_answer_rate"]),
            parent_reconstruction_applied_rate=float(data["parent_reconstruction_applied_rate"]),
            chunk_fragmentation_error_rate=float(data["chunk_fragmentation_error_rate"]),
            observation_count=int(data["observation_count"]),
        )

    def canonical_bytes(self) -> bytes:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class CompletenessChangePackage:
    """Immutable proposal for a completeness-driven RAG parameter change.

    proposal_only=True always — never activates without approval gate.
    """

    proposal_id: str
    surface_name: str
    parameter: str
    old_value: Any
    new_value: Any
    justification: str
    snapshot_id: str
    proposal_only: bool = True

    def __post_init__(self) -> None:
        if not self.proposal_only:
            raise ValueError("proposal_only must be True — proposals never auto-activate")

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "surface_name": self.surface_name,
            "parameter": self.parameter,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "justification": self.justification,
            "snapshot_id": self.snapshot_id,
            "proposal_only": self.proposal_only,
        }

    def canonical_bytes(self) -> bytes:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


_MIN_OBSERVATIONS = 5
_LOW_COMPLETENESS_THRESHOLD = 0.6
_HIGH_FRAGMENTATION_THRESHOLD = 0.3
_LOW_SUPPORT_THRESHOLD = 0.6
_HIGH_SIM_WRONG_ANSWER_THRESHOLD = 0.2
_LOW_PARENT_EXPANSION_RATE = 0.3


class CompletenessRAGProposer:
    """Extends RAGProposer to emit completeness-aware proposals.

    Evaluates EvaluationSignals and proposes:
    - Increase parent expansion depth (low completeness + low expansion)
    - Switch to section-aware chunking (high fragmentation)
    - Enable hybrid retrieval (low support + high sim wrong answers)
    - Raise lexical exact-match boost (missing condition/scope rate high)
    - Change reranker weight toward completeness (low completeness)
    - Increase neighbor window size (low parent expansion)

    All proposals: proposal_only=True, replay-validated, approval-gated.
    C0 RULE: Never activates without existing meta-learning commit controls.
    """

    def propose(self, signals: EvaluationSignals) -> list[CompletenessChangePackage]:
        """Generate completeness-driven proposals from EvaluationSignals.

        Returns an empty list if observations are insufficient or no
        proposal is warranted.
        """
        if signals.observation_count < _MIN_OBSERVATIONS:
            return []
        proposals: list[CompletenessChangePackage] = []
        if (
            signals.mean_completeness_score < _LOW_COMPLETENESS_THRESHOLD
            and signals.parent_reconstruction_applied_rate < _LOW_PARENT_EXPANSION_RATE
        ):
            proposals.append(
                CompletenessChangePackage(
                    proposal_id=f"inc-parent-depth-{signals.snapshot_id}",
                    surface_name="parent_expansion_depth",
                    parameter="expansion_depth",
                    old_value=1,
                    new_value=2,
                    justification=f"mean_completeness={signals.mean_completeness_score:.3f} < {_LOW_COMPLETENESS_THRESHOLD}; parent_expansion_rate={signals.parent_reconstruction_applied_rate:.3f} < {_LOW_PARENT_EXPANSION_RATE}; increase expansion depth",
                    snapshot_id=signals.snapshot_id,
                    proposal_only=True,
                )
            )
        if signals.chunk_fragmentation_error_rate > _HIGH_FRAGMENTATION_THRESHOLD:
            proposals.append(
                CompletenessChangePackage(
                    proposal_id=f"section-aware-chunking-{signals.snapshot_id}",
                    surface_name="chunking_strategy",
                    parameter="chunking_mode",
                    old_value="fixed_token",
                    new_value="section_aware",
                    justification=f"chunk_fragmentation_error_rate={signals.chunk_fragmentation_error_rate:.3f} > {_HIGH_FRAGMENTATION_THRESHOLD}; switch to section-aware chunking",
                    snapshot_id=signals.snapshot_id,
                    proposal_only=True,
                )
            )
        if (
            signals.fully_supported_rate < _LOW_SUPPORT_THRESHOLD
            and signals.high_similarity_wrong_answer_rate > _HIGH_SIM_WRONG_ANSWER_THRESHOLD
        ):
            proposals.append(
                CompletenessChangePackage(
                    proposal_id=f"enable-hybrid-retrieval-{signals.snapshot_id}",
                    surface_name="retrieval_mode",
                    parameter="retrieval_mode",
                    old_value="vector_only",
                    new_value="hybrid",
                    justification=f"fully_supported_rate={signals.fully_supported_rate:.3f} < {_LOW_SUPPORT_THRESHOLD}; high_similarity_wrong_answer_rate={signals.high_similarity_wrong_answer_rate:.3f} > {_HIGH_SIM_WRONG_ANSWER_THRESHOLD}; enable hybrid retrieval",
                    snapshot_id=signals.snapshot_id,
                    proposal_only=True,
                )
            )
        if signals.missing_condition_rate > 0.3 or signals.missing_scope_rate > 0.3:
            proposals.append(
                CompletenessChangePackage(
                    proposal_id=f"raise-lexical-boost-{signals.snapshot_id}",
                    surface_name="lexical_exact_match_boost",
                    parameter="exact_match_boost",
                    old_value=1.0,
                    new_value=1.5,
                    justification=f"missing_condition_rate={signals.missing_condition_rate:.3f}, missing_scope_rate={signals.missing_scope_rate:.3f}; raise lexical exact-match boost for codes/conditions/versions",
                    snapshot_id=signals.snapshot_id,
                    proposal_only=True,
                )
            )
        if signals.mean_completeness_score < _LOW_COMPLETENESS_THRESHOLD:
            proposals.append(
                CompletenessChangePackage(
                    proposal_id=f"reranker-completeness-weight-{signals.snapshot_id}",
                    surface_name="reranker_completeness_weight",
                    parameter="completeness_weight",
                    old_value=0.4,
                    new_value=0.6,
                    justification=f"mean_completeness={signals.mean_completeness_score:.3f} < {_LOW_COMPLETENESS_THRESHOLD}; increase reranker completeness weight over similarity",
                    snapshot_id=signals.snapshot_id,
                    proposal_only=True,
                )
            )
        if signals.parent_reconstruction_applied_rate < _LOW_PARENT_EXPANSION_RATE:
            proposals.append(
                CompletenessChangePackage(
                    proposal_id=f"increase-neighbor-window-{signals.snapshot_id}",
                    surface_name="neighbor_window_size",
                    parameter="neighbor_window",
                    old_value=1,
                    new_value=2,
                    justification=f"parent_expansion_rate={signals.parent_reconstruction_applied_rate:.3f} < {_LOW_PARENT_EXPANSION_RATE}; increase neighbor window size",
                    snapshot_id=signals.snapshot_id,
                    proposal_only=True,
                )
            )
        return proposals


__all__ = ["EvaluationSignals", "CompletenessChangePackage", "CompletenessRAGProposer"]
