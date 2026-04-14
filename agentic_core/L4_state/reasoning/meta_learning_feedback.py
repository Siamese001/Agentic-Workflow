"""Meta-Learning Feedback Loop for Pipeline D.

Implements spec-compliant learning & growth from Agentic Retrieval Models v9:
- Pipeline D: Meta-Learning Feedback Loop (Offline Post-Runtime)
- Evaluation runners (Shadow/Replay: Prec@K, Recall@K, MRR, NDCG, F1-Groundedness)
- CompletenessRAGProposer with feedback triggers
- Feedback triggers: Depth++, Enrichment+, Hybrid Mode, Lexical Boost

Provides:
- Evaluation signal generation
- Completeness analysis
- Feedback trigger activation
- Change package proposals for L5 Board
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_evaluation_metric,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_records_execution_trace,
    _emit_records_learning_event,
    _emit_updates_routing_strategy,
)
from tqdm import tqdm

Logger = logging.getLogger(__name__)


class FeedbackTrigger(Enum):
    """Feedback triggers for N queries influencing N+1 configuration."""

    DEPTH_INCREMENT = "depth_increment"  # Increase expansion depth
    ENRICHMENT_BOOST = "enrichment_boost"  # Enhance L4D prompts
    HYBRID_MODE = "hybrid_mode"  # Enable parallel 4a+4b
    LEXICAL_BOOST = "lexical_boost"  # Increase lexical weight
    NO_ACTION = "no_action"  # Await more queries


@dataclass
class EvaluationMetrics:
    """Retrieval evaluation metrics."""

    precision_at_k: float = 0.0
    recall_at_k: float = 0.0
    mrr: float = 0.0  # Mean Reciprocal Rank
    ndcg: float = 0.0  # Normalized Discounted Cumulative Gain
    f1_groundedness: float = 0.0

    def is_acceptable(self, threshold: float = 0.5) -> bool:
        """Check if metrics meet threshold."""
        return all(
            [
                self.precision_at_k >= threshold,
                self.recall_at_k >= threshold,
                self.f1_groundedness >= threshold,
            ]
        )


@dataclass
class CompletenessAnalysis:
    """Analysis of context completeness."""

    mean_completeness: float = 0.0
    missing_condition_rate: float = 0.0
    missing_exception_rate: float = 0.0
    missing_scope_rate: float = 0.0
    missing_temporal_qualifier_rate: float = 0.0
    fragmentation_score: float = 0.0
    high_similarity_wrong_answer_rate: float = 0.0

    def is_complete(self, threshold: float = 0.5) -> bool:
        """Check if completeness meets threshold."""
        return self.mean_completeness >= threshold

    def has_fragmentation(self, threshold: float = 0.3) -> bool:
        """Check if fragmentation is high."""
        return self.fragmentation_score >= threshold


@dataclass
class FeedbackProposal:
    """Proposed configuration change from feedback analysis."""

    trigger: FeedbackTrigger
    rationale: str
    current_value: Any
    proposed_value: Any
    confidence: float
    supporting_evidence: list[str] = field(default_factory=list)

    def to_change_package(self) -> dict[str, Any]:
        """Convert to L5 ChangePackage format."""
        return {
            "type": "retrieval_config_update",
            "proposal_only": True,
            "trigger": self.trigger.value,
            "rationale": self.rationale,
            "changes": {
                "current": self.current_value,
                "proposed": self.proposed_value,
            },
            "confidence": self.confidence,
            "evidence": self.supporting_evidence,
        }


@dataclass
class CompletenessChangePackage:
    """Complete change package for L5 Board review."""

    snapshot_id: str
    proposals: list[FeedbackProposal]
    aggregate_metrics: EvaluationMetrics
    completeness_analysis: CompletenessAnalysis
    query_count: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for L5 Board submission."""
        return {
            "snapshot_id": self.snapshot_id,
            "proposal_only": True,
            "query_count": self.query_count,
            "aggregate_metrics": {
                "precision_at_k": self.aggregate_metrics.precision_at_k,
                "recall_at_k": self.aggregate_metrics.recall_at_k,
                "mrr": self.aggregate_metrics.mrr,
                "ndcg": self.aggregate_metrics.ndcg,
                "f1_groundedness": self.aggregate_metrics.f1_groundedness,
            },
            "completeness_analysis": {
                "mean_completeness": self.completeness_analysis.mean_completeness,
                "missing_condition_rate": self.completeness_analysis.missing_condition_rate,
                "missing_exception_rate": self.completeness_analysis.missing_exception_rate,
                "fragmentation_score": self.completeness_analysis.fragmentation_score,
            },
            "proposals": [p.to_change_package() for p in self.proposals],
        }


class EvaluationRunner:
    """Evaluation runner for retrieval quality metrics.

    Computes:
    - Precision@K: Relevant items in top K
    - Recall@K: Relevant items retrieved
    - MRR: Mean reciprocal rank of first relevant
    - NDCG: Normalized discounted cumulative gain
    - F1-Groundedness: Groundedness F1 score
    """

    def __init__(self):
        """Initialize evaluation runner."""
        self._eval_count = 0
        self._accumulated_metrics: list[EvaluationMetrics] = []

    def evaluate(
        self,
        query: str,
        retrieved_chunks: list[str],
        relevant_chunks: list[str],
        groundedness_scores: list[float],
        k: int = 5,
    ) -> EvaluationMetrics:
        """Evaluate retrieval quality for a single query.

        Args:
            query: The search query
            retrieved_chunks: List of retrieved chunk IDs
            relevant_chunks: Ground truth relevant chunk IDs
            groundedness_scores: Groundedness scores for retrieved chunks
            k: Cutoff for precision/recall

        Returns:
            EvaluationMetrics for this query
        """
        _trace_id = f"eval_{self._eval_count}"
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L6_OBSERVABILITY,
            "EvaluationRunner.evaluate",
        )

        metrics = EvaluationMetrics()

        # Precision@K
        retrieved_k = set(retrieved_chunks[:k])
        relevant_set = set(relevant_chunks)
        metrics.precision_at_k = len(retrieved_k & relevant_set) / max(len(retrieved_k), 1)

        # Recall@K
        metrics.recall_at_k = len(retrieved_k & relevant_set) / max(len(relevant_set), 1)

        # MRR
        for i, chunk in enumerate(retrieved_chunks):
            if chunk in relevant_chunks:
                metrics.mrr = 1.0 / (i + 1)
                break

        # NDCG (simplified)
        dcg = 0.0
        for i, chunk in enumerate(retrieved_chunks[:k]):
            rel = 1.0 if chunk in relevant_chunks else 0.0
            dcg += rel / (i + 1)  # Discounted

        # Ideal DCG
        ideal_dcg = sum(1.0 / (i + 1) for i in range(min(k, len(relevant_chunks))))
        metrics.ndcg = dcg / max(ideal_dcg, 1e-10)

        # F1-Groundedness
        if groundedness_scores:
            avg_groundedness = sum(groundedness_scores) / len(groundedness_scores)
            # F1 between groundedness and precision
            metrics.f1_groundedness = (
                2
                * (avg_groundedness * metrics.precision_at_k)
                / max(
                    avg_groundedness + metrics.precision_at_k,
                    1e-10,
                )
            )

        _emit_captures_evaluation_metric(
            _trace_id,
            "precision_at_k",
            metrics.precision_at_k,
        )
        _emit_captures_evaluation_metric(
            _trace_id,
            "recall_at_k",
            metrics.recall_at_k,
        )
        _emit_captures_evaluation_metric(
            _trace_id,
            "mrr",
            metrics.mrr,
        )

        self._eval_count += 1
        self._accumulated_metrics.append(metrics)

        return metrics

    def aggregate_metrics(self) -> EvaluationMetrics:
        """Aggregate metrics across all evaluations."""
        if not self._accumulated_metrics:
            return EvaluationMetrics()

        n = len(self._accumulated_metrics)
        return EvaluationMetrics(
            precision_at_k=sum(m.precision_at_k for m in self._accumulated_metrics) / n,
            recall_at_k=sum(m.recall_at_k for m in self._accumulated_metrics) / n,
            mrr=sum(m.mrr for m in self._accumulated_metrics) / n,
            ndcg=sum(m.ndcg for m in self._accumulated_metrics) / n,
            f1_groundedness=sum(m.f1_groundedness for m in self._accumulated_metrics) / n,
        )


class CompletenessAnalyzer:
    """Analyzes context completeness for feedback signals.

    Detects:
    - Missing conditions (if/unless statements)
    - Missing exceptions (error handling)
    - Missing scope (context boundaries)
    - Missing temporal qualifiers (when/after/before)
    - Fragmentation (disconnected context pieces)
    """

    def __init__(self):
        """Initialize completeness analyzer."""
        self._analysis_count = 0

    def analyze(
        self,
        query: str,
        retrieved_contexts: list[dict[str, Any]],
        answer_quality: float | None = None,
    ) -> CompletenessAnalysis:
        """Analyze completeness of retrieved context.

        Args:
            query: The search query
            retrieved_contexts: Retrieved context chunks with metadata
            answer_quality: Optional answer quality score

        Returns:
            CompletenessAnalysis with detected gaps
        """
        _trace_id = f"completeness_{self._analysis_count}"
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L6_OBSERVABILITY,
            "CompletenessAnalyzer.analyze",
        )

        analysis = CompletenessAnalysis()

        # Analyze query for missing elements
        query_lower = query.lower()

        # Check for conditional keywords
        has_condition = any(kw in query_lower for kw in ["if", "unless", "when", "condition"])
        has_exception = any(kw in query_lower for kw in ["except", "error", "exception", "handle"])
        has_scope = any(kw in query_lower for kw in ["scope", "within", "inside", "context"])
        has_temporal = any(kw in query_lower for kw in ["before", "after", "during", "while"])

        # Check retrieved contexts for coverage
        context_text = " ".join(ctx.get("content", "") for ctx in retrieved_contexts).lower()

        # Calculate missing rates
        if has_condition:
            condition_mentions = sum(1 for kw in ["if", "unless", "condition"] if kw in context_text)
            analysis.missing_condition_rate = 1.0 - min(1.0, condition_mentions / 2)

        if has_exception:
            exception_mentions = sum(1 for kw in ["except", "error", "exception"] if kw in context_text)
            analysis.missing_exception_rate = 1.0 - min(1.0, exception_mentions / 2)

        if has_scope:
            scope_mentions = sum(1 for kw in ["scope", "within", "context"] if kw in context_text)
            analysis.missing_scope_rate = 1.0 - min(1.0, scope_mentions / 2)

        if has_temporal:
            temporal_mentions = sum(1 for kw in ["before", "after", "during"] if kw in context_text)
            analysis.missing_temporal_qualifier_rate = 1.0 - min(1.0, temporal_mentions / 2)

        # Calculate fragmentation
        if len(retrieved_contexts) > 1:
            # Check for disconnected contexts (no shared concepts)
            concept_sets = []
            for ctx in retrieved_contexts:
                concepts = set(ctx.get("key_concepts", []))
                if concepts:
                    concept_sets.append(concepts)

            if concept_sets:
                # Fragmentation = 1 - average overlap
                overlaps = []
                for i, set_i in enumerate(concept_sets):
                    for j, set_j in enumerate(concept_sets):
                        if i < j:
                            overlap = len(set_i & set_j) / max(len(set_i | set_j), 1)
                            overlaps.append(overlap)

                if overlaps:
                    analysis.fragmentation_score = 1.0 - (sum(overlaps) / len(overlaps))

        # Calculate mean completeness
        missing_rates = [
            analysis.missing_condition_rate,
            analysis.missing_exception_rate,
            analysis.missing_scope_rate,
            analysis.missing_temporal_qualifier_rate,
        ]
        analysis.mean_completeness = 1.0 - (sum(missing_rates) / max(len(missing_rates), 1))

        # High similarity wrong answer detection
        if answer_quality is not None and answer_quality < 0.3:
            # Check if contexts seem relevant but answer is poor
            avg_chunk_relevance = sum(ctx.get("score", 0) for ctx in retrieved_contexts) / max(
                len(retrieved_contexts), 1
            )

            if avg_chunk_relevance > 0.7:
                analysis.high_similarity_wrong_answer_rate = 1.0

        self._analysis_count += 1
        return analysis


class CompletenessRAGProposer:
    """Proposes retrieval configuration changes based on feedback analysis.

    Implements the feedback trigger decision tree from Agentic Retrieval Models v9:
    1. EVAL: COMPLETENESS -> Depth++
    2. EVAL: FRAGMENTATION -> Enrichment+
    3. EVAL: GROUNDEDNESS -> Hybrid Mode
    4. EVAL: LEXICAL GAP -> Lexical Boost
    5. EVAL: SIGNAL VOLUME -> No Action
    """

    def __init__(
        self,
        evaluator: EvaluationRunner | None = None,
        analyzer: CompletenessAnalyzer | None = None,
    ):
        """Initialize CompletenessRAGProposer.

        Args:
            evaluator: Evaluation runner for metrics
            analyzer: Completeness analyzer
        """
        self.evaluator = evaluator or EvaluationRunner()
        self.analyzer = analyzer or CompletenessAnalyzer()

        self._current_config = {
            "expansion_depth": 3,
            "enable_enrichment": True,
            "hybrid_mode": False,
            "lexical_weight": 0.3,
        }

    def analyze_and_propose(
        self,
        query_batch: list[dict[str, Any]],
    ) -> CompletenessChangePackage:
        """Analyze query batch and propose configuration changes.

        Args:
            query_batch: List of query results with retrieved contexts

        Returns:
            CompletenessChangePackage for L5 Board

        Note:
            Implements dampening gate: If query_count < 5, returns NO_ACTION
            to await more observations.
        """
        _trace_id = f"propose_{len(query_batch)}"
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L6_OBSERVABILITY,
            "CompletenessRAGProposer.analyze_and_propose",
        )
        _emit_feeds_meta_learning(_trace_id, "proposer", f"batch:{len(query_batch)}")

        # Dampening gate: Low signal volume check
        if len(query_batch) < 5:
            Logger.info(f"Dampening gate active: insufficient query volume ({len(query_batch)} < 5)")

            # Return NO_ACTION change package
            no_action_proposal = FeedbackProposal(
                trigger=FeedbackTrigger.NO_ACTION,
                rationale=f"Insufficient query volume ({len(query_batch)} queries). Minimum threshold is 5. Awaiting more observations.",
                current_value="active",
                proposed_value="hold",
                confidence=0.95,
                supporting_evidence=[
                    f"query_count={len(query_batch)}",
                    "minimum_threshold=5",
                    "dampening_gate_active",
                ],
            )

            return CompletenessChangePackage(
                snapshot_id=_trace_id,
                proposals=[no_action_proposal],
                aggregate_metrics=EvaluationMetrics(),
                completeness_analysis=CompletenessAnalysis(),
                query_count=len(query_batch),
            )

        proposals = []

        # Evaluate each query
        for query_data in tqdm(query_batch, desc="Processing", unit="item"):
            self.evaluator.evaluate(
                query=query_data["query"],
                retrieved_chunks=query_data.get("retrieved_chunks", []),
                relevant_chunks=query_data.get("relevant_chunks", []),
                groundedness_scores=query_data.get("groundedness_scores", []),
            )

            self.analyzer.analyze(
                query=query_data["query"],
                retrieved_contexts=query_data.get("contexts", []),
                answer_quality=query_data.get("answer_quality"),
            )

        # Aggregate metrics
        agg_metrics = self.evaluator.aggregate_metrics()

        # Generate proposals based on feedback triggers
        proposals.extend(self._check_completeness_trigger(agg_metrics))
        proposals.extend(self._check_fragmentation_trigger())
        proposals.extend(self._check_groundedness_trigger(agg_metrics))
        proposals.extend(self._check_lexical_gap_trigger(query_batch))
        proposals.extend(self._check_signal_volume_trigger(query_batch))

        # Create change package
        change_package = CompletenessChangePackage(
            snapshot_id=_trace_id,
            proposals=proposals,
            aggregate_metrics=agg_metrics,
            completeness_analysis=self.analyzer.analyze("", []),  # Get latest
            query_count=len(query_batch),
        )

        _emit_records_learning_event(
            _trace_id,
            "proposals_generated",
            f"count:{len(proposals)}",
        )

        return change_package

    def _check_completeness_trigger(
        self,
        metrics: EvaluationMetrics,
    ) -> list[FeedbackProposal]:
        """Check completeness trigger (Score < 0.5 -> Depth++).

        COND: mean_completeness < 0.5
        PROPOSAL: Depth++ (Modifies Step 4c)
        """
        proposals = []

        if metrics.precision_at_k < 0.5 or metrics.recall_at_k < 0.5:
            current_depth = self._current_config["expansion_depth"]

            if current_depth < 5:  # Max depth is 5
                proposal = FeedbackProposal(
                    trigger=FeedbackTrigger.DEPTH_INCREMENT,
                    rationale=f"Low completeness scores (P@K={metrics.precision_at_k:.2f}, R@K={metrics.recall_at_k:.2f}). Increasing expansion depth to capture more context.",
                    current_value=current_depth,
                    proposed_value=current_depth + 1,
                    confidence=0.8,
                    supporting_evidence=[
                        f"precision_at_k={metrics.precision_at_k:.3f}",
                        f"recall_at_k={metrics.recall_at_k:.3f}",
                    ],
                )
                proposals.append(proposal)
                _emit_updates_routing_strategy(
                    "completeness_proposer",
                    "depth_increment",
                    str(current_depth + 1),
                )

        return proposals

    def _check_fragmentation_trigger(self) -> list[FeedbackProposal]:
        """Check fragmentation trigger (High fragmentation -> Enrichment+).

        COND: High fragmentation
        PROPOSAL: Enrichment+ (Modifies L4D Prompts)
        """
        proposals = []

        # Use recent analysis
        recent_analysis = self.analyzer.analyze("", [])

        if recent_analysis.has_fragmentation(threshold=0.3):
            current = self._current_config["enable_enrichment"]

            proposal = FeedbackProposal(
                trigger=FeedbackTrigger.ENRICHMENT_BOOST,
                rationale=f"High fragmentation detected (score={recent_analysis.fragmentation_score:.2f}). Enhancing L4D enrichment to improve context cohesion.",
                current_value=current,
                proposed_value=True,
                confidence=0.75,
                supporting_evidence=[
                    f"fragmentation_score={recent_analysis.fragmentation_score:.3f}",
                    "disconnected_context_pieces_detected",
                ],
            )
            proposals.append(proposal)
            _emit_improves_agent_policy(
                "completeness_proposer",
                "enrichment_boost",
                "fragmentation_fix",
            )

        return proposals

    def _check_groundedness_trigger(
        self,
        metrics: EvaluationMetrics,
    ) -> list[FeedbackProposal]:
        """Check groundedness trigger (Support score < 0.5 -> Hybrid Mode).

        COND: Fully supported? (Support score < 0.5)
        PROPOSAL: Hybrid Mode (Enable Parallel 4a+4b)
        """
        proposals = []

        if metrics.f1_groundedness < 0.5:
            current = self._current_config["hybrid_mode"]

            if not current:  # Only propose if not already enabled
                proposal = FeedbackProposal(
                    trigger=FeedbackTrigger.HYBRID_MODE,
                    rationale=f"Low groundedness score ({metrics.f1_groundedness:.2f}). Enabling hybrid mode to combine vector and lexical search.",
                    current_value=current,
                    proposed_value=True,
                    confidence=0.7,
                    supporting_evidence=[
                        f"f1_groundedness={metrics.f1_groundedness:.3f}",
                        "vector_search_insufficient",
                    ],
                )
                proposals.append(proposal)
                _emit_updates_routing_strategy(
                    "completeness_proposer",
                    "hybrid_mode",
                    "enabled",
                )

        return proposals

    def _check_lexical_gap_trigger(
        self,
        query_batch: list[dict[str, Any]],
    ) -> list[FeedbackProposal]:
        """Check lexical gap trigger (High missing condition -> Lexical Boost).

        COND: High Missing Condition? (Lexical exact match issues)
        PROPOSAL: Lexical Boost (Increase 4e weight)
        """
        proposals = []

        # Check for lexical issues in batch
        lexical_issues = sum(1 for q in query_batch if q.get("lexical_match_score", 1.0) < 0.5)

        if lexical_issues > len(query_batch) * 0.3:  # >30% have issues
            current_weight = self._current_config["lexical_weight"]

            if current_weight < 0.7:  # Cap at 0.7
                new_weight = min(0.7, current_weight + 0.1)

                proposal = FeedbackProposal(
                    trigger=FeedbackTrigger.LEXICAL_BOOST,
                    rationale=f"Lexical match issues detected in {lexical_issues}/{len(query_batch)} queries. Increasing lexical weight to improve exact matching.",
                    current_value=current_weight,
                    proposed_value=new_weight,
                    confidence=0.65,
                    supporting_evidence=[
                        f"lexical_issues={lexical_issues}",
                        f"total_queries={len(query_batch)}",
                    ],
                )
                proposals.append(proposal)
                _emit_updates_routing_strategy(
                    "completeness_proposer",
                    "lexical_weight",
                    str(new_weight),
                )

        return proposals

    def _check_signal_volume_trigger(
        self,
        query_batch: list[dict[str, Any]],
    ) -> list[FeedbackProposal]:
        """Check signal volume trigger (Low observations -> No Action).

        COND: Low Observations? (Dampening gate active)
        ACTION: None (Awaiting more queries)
        """
        proposals = []

        # If batch is small, recommend waiting
        if len(query_batch) < 5:
            proposal = FeedbackProposal(
                trigger=FeedbackTrigger.NO_ACTION,
                rationale=f"Insufficient query volume ({len(query_batch)} queries). Awaiting more observations before proposing changes.",
                current_value="active",
                proposed_value="hold",
                confidence=0.9,
                supporting_evidence=[
                    f"query_count={len(query_batch)}",
                    "minimum_threshold=5",
                ],
            )
            proposals.append(proposal)

        return proposals

    def update_config(self, approved_proposals: list[FeedbackProposal]) -> None:
        """Update current config with approved proposals.

        Args:
            approved_proposals: Proposals approved by L5 Board
        """
        for proposal in approved_proposals:
            if proposal.trigger == FeedbackTrigger.DEPTH_INCREMENT:
                self._current_config["expansion_depth"] = proposal.proposed_value
            elif proposal.trigger == FeedbackTrigger.HYBRID_MODE:
                self._current_config["hybrid_mode"] = proposal.proposed_value
            elif proposal.trigger == FeedbackTrigger.LEXICAL_BOOST:
                self._current_config["lexical_weight"] = proposal.proposed_value
            elif proposal.trigger == FeedbackTrigger.ENRICHMENT_BOOST:
                self._current_config["enable_enrichment"] = proposal.proposed_value

        Logger.info(f"Updated config: {self._current_config}")

    def get_current_config(self) -> dict[str, Any]:
        """Get current configuration."""
        return dict(self._current_config)


# Global instances
_global_evaluator: EvaluationRunner | None = None
_global_analyzer: CompletenessAnalyzer | None = None
_global_proposer: CompletenessRAGProposer | None = None


def get_global_evaluator() -> EvaluationRunner:
    """Get or create global evaluation runner."""
    global _global_evaluator
    if _global_evaluator is None:
        _global_evaluator = EvaluationRunner()
    return _global_evaluator


def get_global_analyzer() -> CompletenessAnalyzer:
    """Get or create global completeness analyzer."""
    global _global_analyzer
    if _global_analyzer is None:
        _global_analyzer = CompletenessAnalyzer()
    return _global_analyzer


def get_global_proposer() -> CompletenessRAGProposer:
    """Get or create global CompletenessRAGProposer."""
    global _global_proposer
    if _global_proposer is None:
        _global_proposer = CompletenessRAGProposer()
    return _global_proposer


__all__ = [
    "CompletenessRAGProposer",
    "EvaluationRunner",
    "CompletenessAnalyzer",
    "FeedbackTrigger",
    "FeedbackProposal",
    "CompletenessChangePackage",
    "EvaluationMetrics",
    "CompletenessAnalysis",
    "get_global_evaluator",
    "get_global_analyzer",
    "get_global_proposer",
]
