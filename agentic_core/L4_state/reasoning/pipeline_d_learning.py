"""Pipeline D: Meta-Learning Feedback Loop

Implements spec-compliant Pipeline D with:
- Evaluation Runners (Shadow/Replay)
- Completeness, Fragmentation, Groundedness metrics
- Lexical Gap detection
- Signal Volume analysis
- CompletenessRAGProposer for L5 Board

Offline post-runtime decision tree for N queries → N+1 config.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_evaluation_metric,
    _emit_feeds_meta_learning,
    _emit_records_execution_trace,
    _emit_updates_meta_learning_state,
)

Logger = logging.getLogger(__name__)


@dataclass
class EvaluationSignal:
    """Signal from evaluation runner."""

    signal_type: str  # 'completeness', 'fragmentation', 'groundedness', 'lexical_gap', 'signal_volume'
    score: float
    threshold: float
    trigger_action: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CompletenessRAGProposal:
    """Proposal from CompletenessRAGProposer to L5 Board."""

    proposal_type: str  # 'Depth++', 'Enrichment+', 'HybridMode', 'LexicalBoost', 'None'
    confidence: float
    rationale: str
    affected_layers: list[str] = field(default_factory=list)
    proposal_only: bool = True  # C0 RULE: proposals only, never authorizes


class CompletenessEvaluator:
    """Evaluates context completeness (Trigger 1).

    Measures: mean_completeness score < 0.5?
    """

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold

    def evaluate(
        self,
        query: str,
        retrieved_contexts: list[str],
        generated_answer: str,
    ) -> EvaluationSignal:
        """Evaluate completeness of retrieved context.

        Args:
            query: User query
            retrieved_contexts: Retrieved document chunks
            generated_answer: Generated answer

        Returns:
            EvaluationSignal with completeness score
        """
        # Calculate coverage heuristic
        query_terms = set(query.lower().split())
        context_text = " ".join(retrieved_contexts).lower()

        covered_terms = sum(1 for term in query_terms if term in context_text)
        coverage_ratio = covered_terms / len(query_terms) if query_terms else 0.0

        # Additional heuristic: answer generation quality proxy
        answer_length_score = min(len(generated_answer) / 100, 1.0)

        # Combined completeness score
        completeness = coverage_ratio * 0.7 + answer_length_score * 0.3

        triggered = completeness < self.threshold

        return EvaluationSignal(
            signal_type="completeness",
            score=completeness,
            threshold=self.threshold,
            trigger_action="Depth++" if triggered else None,
            metadata={
                "coverage_ratio": coverage_ratio,
                "answer_length_score": answer_length_score,
            },
        )


class FragmentationEvaluator:
    """Evaluates context fragmentation (Trigger 2).

    Detects high boundary errors and context gaps.
    """

    def __init__(self, threshold: float = 0.3):
        self.threshold = threshold  # Max acceptable fragmentation

    def evaluate(
        self,
        retrieved_contexts: list[str],
        chunk_metadata: list[dict[str, Any]],
    ) -> EvaluationSignal:
        """Evaluate fragmentation of retrieved context.

        Args:
            retrieved_contexts: Retrieved document chunks
            chunk_metadata: Metadata for each chunk

        Returns:
            EvaluationSignal with fragmentation score
        """
        if not retrieved_contexts:
            return EvaluationSignal(
                signal_type="fragmentation",
                score=1.0,
                threshold=self.threshold,
                trigger_action="Enrichment+",
            )

        # Calculate fragmentation heuristics
        # 1. Source diversity (more sources = more fragmented)
        sources = set()
        for meta in chunk_metadata:
            source = meta.get("source_file", meta.get("doc_id", "unknown"))
            sources.add(source)

        source_diversity = len(sources) / len(retrieved_contexts) if retrieved_contexts else 0.0

        # 2. Content overlap (low overlap = fragmented)
        overlaps = []
        for i in range(len(retrieved_contexts)):
            for j in range(i + 1, len(retrieved_contexts)):
                words_i = set(retrieved_contexts[i].lower().split())
                words_j = set(retrieved_contexts[j].lower().split())

                if words_i and words_j:
                    intersection = len(words_i & words_j)
                    union = len(words_i | words_j)
                    overlap = intersection / union
                    overlaps.append(overlap)

        avg_overlap = sum(overlaps) / len(overlaps) if overlaps else 0.0
        fragmentation = source_diversity * 0.6 + (1 - avg_overlap) * 0.4

        triggered = fragmentation > self.threshold

        return EvaluationSignal(
            signal_type="fragmentation",
            score=fragmentation,
            threshold=self.threshold,
            trigger_action="Enrichment+" if triggered else None,
            metadata={
                "source_diversity": source_diversity,
                "avg_content_overlap": avg_overlap,
                "num_sources": len(sources),
            },
        )


class GroundednessEvaluator:
    """Evaluates answer groundedness (Trigger 3).

    Measures: Support score < 0.5 (F1-Groundedness)
    """

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold

    def evaluate(
        self,
        generated_answer: str,
        retrieved_contexts: list[str],
    ) -> EvaluationSignal:
        """Evaluate groundedness of generated answer.

        Args:
            generated_answer: Generated answer text
            retrieved_contexts: Source contexts

        Returns:
            EvaluationSignal with groundedness score
        """
        if not generated_answer or not retrieved_contexts:
            return EvaluationSignal(
                signal_type="groundedness",
                score=0.0,
                threshold=self.threshold,
                trigger_action="HybridMode",
            )

        # Simple groundedness: % of answer terms in context
        answer_terms = set(generated_answer.lower().split())
        context_text = " ".join(retrieved_contexts).lower()

        grounded_terms = sum(1 for term in answer_terms if term in context_text)
        groundedness = grounded_terms / len(answer_terms) if answer_terms else 0.0

        # F1-style score (precision proxy)
        precision = groundedness
        recall = min(1.0, len(answer_terms) / 50)  # Assume ideal answer covers query
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        triggered = f1 < self.threshold

        return EvaluationSignal(
            signal_type="groundedness",
            score=f1,
            threshold=self.threshold,
            trigger_action="HybridMode" if triggered else None,
            metadata={
                "precision_proxy": precision,
                "recall_proxy": recall,
                "num_answer_terms": len(answer_terms),
            },
        )


class LexicalGapEvaluator:
    """Evaluates lexical gaps (Trigger 4).

    Detects high missing conditionality (lexical exact match needed).
    """

    def __init__(self, threshold: float = 0.3):
        self.threshold = threshold

    def evaluate(
        self,
        query: str,
        retrieved_contexts: list[str],
    ) -> EvaluationSignal:
        """Evaluate lexical coverage gaps.

        Args:
            query: User query
            retrieved_contexts: Retrieved contexts

        Returns:
            EvaluationSignal with lexical gap score
        """
        query_terms = set(query.lower().split())
        context_text = " ".join(retrieved_contexts).lower()

        # Exact term matches
        exact_matches = sum(1 for term in query_terms if term in context_text)
        exact_match_ratio = exact_matches / len(query_terms) if query_terms else 0.0

        # Missing = 1 - exact_match_ratio
        lexical_gap = 1.0 - exact_match_ratio

        triggered = lexical_gap > self.threshold

        return EvaluationSignal(
            signal_type="lexical_gap",
            score=lexical_gap,
            threshold=self.threshold,
            trigger_action="LexicalBoost" if triggered else None,
            metadata={
                "exact_match_ratio": exact_match_ratio,
                "missing_terms_count": len(query_terms) - exact_matches,
            },
        )


class SignalVolumeEvaluator:
    """Evaluates signal volume (Trigger 5).

    Detects low observations (dampening gate active).
    """

    def __init__(self, min_observations: int = 10):
        self.min_observations = min_observations

    def evaluate(
        self,
        retrieval_stats: dict[str, Any],
    ) -> EvaluationSignal:
        """Evaluate signal volume.

        Args:
            retrieval_stats: Statistics from retrieval

        Returns:
            EvaluationSignal with signal volume assessment
        """
        observations = retrieval_stats.get("total_results", 0)

        # Low volume if under minimum
        volume_score = min(observations / self.min_observations, 1.0)

        triggered = observations < self.min_observations

        return EvaluationSignal(
            signal_type="signal_volume",
            score=volume_score,
            threshold=self.min_observations,
            trigger_action=None if triggered else "AwaitNQueries",
            metadata={
                "total_observations": observations,
                "min_required": self.min_observations,
            },
        )


class CompletenessRAGProposer:
    """Generates proposals for L5 Board based on evaluation signals.

    Implements Pipeline D meta-learning feedback loop.
    """

    def __init__(self):
        self._proposal_count = 0

    def generate_proposal(
        self,
        signals: list[EvaluationSignal],
        query_history: list[str],
    ) -> CompletenessRAGProposal:
        """Generate proposal based on evaluation signals.

        Follows decision tree:
        1. Completeness < 0.5? -> Depth++
        2. Fragmentation high? -> Enrichment+
        3. Groundedness < 0.5? -> HybridMode
        4. Lexical gap high? -> LexicalBoost
        5. Low volume? -> AwaitNQueries

        Args:
            signals: List of evaluation signals
            query_history: Recent query history

        Returns:
            CompletenessRAGProposal for L5 Board
        """
        _trace_id = f"proposer_{self._proposal_count}"
        _emit_feeds_meta_learning(_trace_id, "CompletenessRAGProposer", "evaluation_signals")

        # Find triggered signals
        triggered = [s for s in signals if s.trigger_action]

        if not triggered:
            # No triggers - system healthy
            self._proposal_count += 1
            return CompletenessRAGProposal(
                proposal_type="None",
                confidence=0.9,
                rationale="All evaluation metrics within thresholds. System healthy.",
                affected_layers=[],
                proposal_only=True,
            )

        # Priority order: Depth++ > Enrichment+ > HybridMode > LexicalBoost
        priority_order = ["Depth++", "Enrichment+", "HybridMode", "LexicalBoost"]

        for action in priority_order:
            matching = [s for s in triggered if s.trigger_action == action]
            if matching:
                signal = matching[0]

                proposal = self._create_proposal(action, signal, query_history)
                self._proposal_count += 1

                _emit_updates_meta_learning_state(
                    _trace_id,
                    "CompletenessRAGProposer",
                    proposal.proposal_type,
                )

                return proposal

        # Fallback
        return CompletenessRAGProposal(
            proposal_type="None",
            confidence=0.5,
            rationale="No actionable triggers found.",
            affected_layers=[],
            proposal_only=True,
        )

    def _create_proposal(
        self,
        action: str,
        signal: EvaluationSignal,
        query_history: list[str],
    ) -> CompletenessRAGProposal:
        """Create specific proposal based on action type."""

        if action == "Depth++":
            return CompletenessRAGProposal(
                proposal_type="Depth++",
                confidence=signal.score,
                rationale=f"Completeness score {signal.score:.2f} below threshold {signal.threshold}. Recommend increasing retrieval depth (step 4c).",
                affected_layers=["L3"],
                proposal_only=True,
            )

        elif action == "Enrichment+":
            return CompletenessRAGProposal(
                proposal_type="Enrichment+",
                confidence=signal.score,
                rationale=f"High fragmentation detected ({signal.metadata.get('source_diversity', 0):.2f} source diversity). Recommend enhancing L4D enrichment prompts.",
                affected_layers=["L4D"],
                proposal_only=True,
            )

        elif action == "HybridMode":
            return CompletenessRAGProposal(
                proposal_type="HybridMode",
                confidence=1.0 - signal.score,
                rationale=f"Low groundedness (F1={signal.score:.2f}). Recommend enabling hybrid search (4a+4b parallel).",
                affected_layers=["L3"],
                proposal_only=True,
            )

        elif action == "LexicalBoost":
            return CompletenessRAGProposal(
                proposal_type="LexicalBoost",
                confidence=signal.score,
                rationale=f"Lexical gap detected ({signal.score:.2f} missing). Recommend increasing BM25 weight (4e).",
                affected_layers=["L3"],
                proposal_only=True,
            )

        return CompletenessRAGProposal(
            proposal_type="None",
            confidence=0.5,
            rationale="Unknown action type.",
            affected_layers=[],
            proposal_only=True,
        )


class PipelineDEvaluationRunner:
    """Main runner for Pipeline D evaluations.

    Orchestrates all 5 evaluation triggers and generates proposals.
    """

    def __init__(self):
        self.completeness_eval = CompletenessEvaluator()
        self.fragmentation_eval = FragmentationEvaluator()
        self.groundedness_eval = GroundednessEvaluator()
        self.lexical_gap_eval = LexicalGapEvaluator()
        self.signal_volume_eval = SignalVolumeEvaluator()
        self.proposer = CompletenessRAGProposer()

        self._run_count = 0

    async def evaluate_retrieval(
        self,
        query: str,
        retrieved_contexts: list[str],
        generated_answer: str,
        chunk_metadata: list[dict[str, Any]],
        retrieval_stats: dict[str, Any],
        query_history: list[str],
    ) -> dict[str, Any]:
        """Run full Pipeline D evaluation.

        Args:
            query: User query
            retrieved_contexts: Retrieved document chunks
            generated_answer: Generated answer
            chunk_metadata: Metadata for chunks
            retrieval_stats: Retrieval statistics
            query_history: Query history

        Returns:
            Evaluation results with proposal
        """
        _trace_id = f"pipeline_d_{self._run_count}"
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L4_STATE,
            "PipelineDEvaluationRunner.evaluate_retrieval",
        )

        # Run all 5 evaluations
        signals = []

        # 1. Completeness
        completeness_signal = self.completeness_eval.evaluate(
            query,
            retrieved_contexts,
            generated_answer,
        )
        signals.append(completeness_signal)

        # 2. Fragmentation
        fragmentation_signal = self.fragmentation_eval.evaluate(
            retrieved_contexts,
            chunk_metadata,
        )
        signals.append(fragmentation_signal)

        # 3. Groundedness
        groundedness_signal = self.groundedness_eval.evaluate(
            generated_answer,
            retrieved_contexts,
        )
        signals.append(groundedness_signal)

        # 4. Lexical Gap
        lexical_signal = self.lexical_gap_eval.evaluate(query, retrieved_contexts)
        signals.append(lexical_signal)

        # 5. Signal Volume
        volume_signal = self.signal_volume_eval.evaluate(retrieval_stats)
        signals.append(volume_signal)

        # Generate proposal
        proposal = self.proposer.generate_proposal(signals, query_history)

        # Capture metrics
        for signal in signals:
            _emit_captures_evaluation_metric(
                _trace_id,
                "pipeline_d",
                signal.signal_type,
                signal.score,
            )

        self._run_count += 1

        return {
            "signals": signals,
            "proposal": proposal,
            "triggered_actions": [s.trigger_action for s in signals if s.trigger_action],
            "evaluation_id": _trace_id,
        }

    def get_stats(self) -> dict[str, Any]:
        """Get evaluation runner statistics."""
        return {
            "run_count": self._run_count,
            "evaluators": [
                "completeness",
                "fragmentation",
                "groundedness",
                "lexical_gap",
                "signal_volume",
            ],
        }


# Global instance
_global_pipeline_d: PipelineDEvaluationRunner | None = None


def get_global_pipeline_d() -> PipelineDEvaluationRunner:
    """Get or create global Pipeline D runner."""
    global _global_pipeline_d
    if _global_pipeline_d is None:
        _global_pipeline_d = PipelineDEvaluationRunner()
    return _global_pipeline_d
