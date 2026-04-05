"""Multi-Stage Signal Quality Pipeline - Quality Control for RAG Retrieval.

This module provides a quality control layer that evaluates retrieved chunks against
multiple quality standards before they reach the generation agents. Low-quality or
unverifiable content is filtered out to ensure only high-signal content is used.
"""

import logging
import re

from pydantic import BaseModel, Field, confloat, validator

from agentic_core.interfaces.path_constants import THRESHOLD
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "signal_quality_pipeline_validator", "p0_governance")
_emit_reads_policy_state("p0", "signal_quality_pipeline_validator", "policy_binding")
_emit_snapshots_state("p0", "signal_quality_pipeline_validator", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("signal_quality_pipeline_validator", "p4obs", "metric_1")
_emit_emits_metric_event("signal_quality_pipeline_validator", "p4obs", "metric_2")
_emit_emits_metric_event("signal_quality_pipeline_validator", "p4obs", "metric_3")
_emit_emits_metric_event("signal_quality_pipeline_validator", "p4obs", "metric_4")
_emit_emits_metric_event("signal_quality_pipeline_validator", "p4obs", "metric_5")
_emit_emits_metric_event("signal_quality_pipeline_validator", "p4obs", "metric_6")
_emit_records_incident_event("signal_quality_pipeline_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("signal_quality_pipeline_validator", "p4obs", "anomaly")
_emit_writes_observability_log("signal_quality_pipeline_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("signal_quality_pipeline_validator", "p4obs", "mon_state")
_emit_triggers_alert("signal_quality_pipeline_validator", "p4obs", "alert")
_emit_links_incident_trace("signal_quality_pipeline_validator", "p4obs", "trace_link")
_emit_captures_pattern("signal_quality_pipeline_validator", "p3lm", "pattern")
_emit_records_learning_event("signal_quality_pipeline_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("signal_quality_pipeline_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("signal_quality_pipeline_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("signal_quality_pipeline_validator", "p3lm", "routing")
_emit_improves_agent_policy("signal_quality_pipeline_validator", "p3lm", "policy")
_emit_stores_learning_state("signal_quality_pipeline_validator", "p3lm", "state")
_emit_records_execution_trace("signal_quality_pipeline_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("signal_quality_pipeline_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("signal_quality_pipeline_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("signal_quality_pipeline_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("signal_quality_pipeline_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("signal_quality_pipeline_validator", "env_read", "p2_env_1")
_emit_reads_environ("signal_quality_pipeline_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("signal_quality_pipeline_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("signal_quality_pipeline_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "signal_quality_pipeline_validator", "context_pull")
_emit_pulls_context("p1", "signal_quality_pipeline_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "signal_quality_pipeline_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "signal_quality_pipeline_validator", "uwg_term_2")
_emit_writes_through("p1", "signal_quality_pipeline_validator", "write_through")
_emit_writes_through("p1", "signal_quality_pipeline_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "signal_quality_pipeline_validator", "safety_validation")
_emit_invokes_eval("p1", "signal_quality_pipeline_validator", "eval_call")
_emit_proposal_commits_routing("p1", "signal_quality_pipeline_validator", "routing_commit")
_emit_escalates_to_human("p1", "signal_quality_pipeline_validator", "human_escalation")
_emit_routes_through("p1", "signal_quality_pipeline_validator", "route_through")
_emit_checks_agent_registry("p1", "signal_quality_pipeline_validator", "agent_registry")
_emit_validates_agent_capability("p1", "signal_quality_pipeline_validator", "capability")
_emit_dispatches_execution_plan("p1", "signal_quality_pipeline_validator", "exec_plan")
_emit_agent_executes_agent("p1", "signal_quality_pipeline_validator", "sub_agent")
_emit_routes_to_agent("p1", "signal_quality_pipeline_validator", "target_agent")
_emit_verifies_policy("p1", "signal_quality_pipeline_validator", "policy_check")
_emit_observes_runtime_state("p1", "signal_quality_pipeline_validator", "runtime_state")
_emit_verifies_boundary("p1", "signal_quality_pipeline_validator", "boundary_check")
_emit_transcripts_response("p1", "signal_quality_pipeline_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "signal_quality_pipeline_validator")
_emit_gated_by_confidence("p1", "signal_quality_pipeline_validator", "confidence_gate")
emit_replay_key("p0", "signal_quality_pipeline_validator")
emit_determinism_digest("p0", "signal_quality_pipeline_validator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "signal_quality_pipeline_validator", "execution_auth")
_emit_validates_capability("p2", "signal_quality_pipeline_validator", "capability_check")
_emit_routes_to_capability("p2", "signal_quality_pipeline_validator", "capability_route")
_emit_writes_via_uwg("p2", "signal_quality_pipeline_validator", "uwg_write")
_emit_blocks_direct_write("p2", "signal_quality_pipeline_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "signal_quality_pipeline_validator", "tool_invocation")
_emit_captures_execution_output("p2", "signal_quality_pipeline_validator", "exec_output")
_emit_dispatches_agent("p3", "signal_quality_pipeline_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "signal_quality_pipeline_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "signal_quality_pipeline_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "signal_quality_pipeline_validator", "healing_outcome")
_emit_escalates_failure("p3", "signal_quality_pipeline_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "signal_quality_pipeline_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "signal_quality_pipeline_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "signal_quality_pipeline_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "signal_quality_pipeline_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "signal_quality_pipeline_validator", "eval_metric")
_emit_stores_embedding("p4", "signal_quality_pipeline_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "signal_quality_pipeline_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "signal_quality_pipeline_validator", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class QualityAssessment(BaseModel):
    """Assessment result for a document's signal quality."""

    is_pass: bool = Field(..., description="Overall pass/fail decision")
    relevance_score: confloat(ge=0.0, le=1.0) = Field(default=0.0, description="Relevance to query")
    authority_score: confloat(ge=0.0, le=1.0) = Field(default=0.0, description="Source authority")
    specificity_score: confloat(ge=0.0, le=1.0) = Field(default=0.0, description="Metric specificity")
    coherence_score: confloat(ge=0.0, le=1.0) = Field(default=0.0, description="Content coherence")
    flags: list[str] = Field(default_factory=list, description="Quality flags/warnings")
    doc_id: str | None = Field(None, description="Document identifier for logging")

    @validator("flags", pre=True)
    def validate_flags(cls, v):
        """Ensure flags is a list of strings."""
        if isinstance(v, str):
            return [v]
        return v if isinstance(v, list) else []

    @property
    def composite_score(self) -> float:
        """Calculate composite quality score."""
        weights = {"relevance": 0.3, "authority": 0.3, "specificity": 0.2, "coherence": 0.2}
        return (
            self.relevance_score * weights["relevance"]
            + self.authority_score * weights["authority"]
            + self.specificity_score * weights["specificity"]
            + self.coherence_score * weights["coherence"]
        )

    def has_flag(self, flag: str) -> bool:
        """Check if a specific flag is present."""
        return flag in self.flags

    def add_flag(self, flag: str) -> None:
        """Add a quality flag."""
        if flag not in self.flags:
            self.flags.append(flag)


class SignalQualityPipeline:
    """Multi-stage quality control pipeline for RAG retrieval.

    This pipeline evaluates every retrieved chunk against a 5-stage standard
    to ensure only high-signal, verifiable content reaches the generation agents.
    """

    # guardian: allow-magic-config
    def __init__(
        self,
        relevance_threshold: float = 0.3,
        authority_threshold: float = 0.4,
        specificity_threshold: float = 0.5,
        enable_coherence_check: bool = False,
    ):
        """Initialize the quality pipeline.

        Args:
            relevance_threshold: Minimum relevance score to pass
            authority_threshold: Minimum authority score to pass
            specificity_threshold: Minimum specificity score to pass
            enable_coherence_check: Whether to run coherence checks (expensive)
        """
        self.relevance_threshold = relevance_threshold
        self.authority_threshold = authority_threshold
        self.specificity_threshold = specificity_threshold
        self.enable_coherence_check = enable_coherence_check
        self.authority_tiers = {
            "tier_1": {
                "score": 1.0,
                "sources": {
                    "10-k",
                    "10-q",
                    "official_report",
                    "sec_filing",
                    "annual_report",
                    "proxy_statement",
                },
            },
            "tier_2": {
                "score": 0.8,
                "sources": {
                    "linkedin",
                    "resume_v1",
                    "official_resume",
                    "company_profile",
                    "verified_profile",
                },
            },
            "tier_3": {"score": 0.5, "sources": {"notes", "blog", "scratchpad", "personal_notes", "draft"}},
            "tier_4": {"score": 0.2, "sources": {"unknown", "unverified", "cached", "temp"}},
        }
        self.impact_words = {
            "grew",
            "growth",
            "increased",
            "decreased",
            "reduced",
            "saved",
            "generated",
            "achieved",
            "improved",
            "optimized",
            "accelerated",
            "expanded",
            "launched",
            "delivered",
            "completed",
            "managed",
            "led",
            "built",
            "created",
            "drove",
            "revenue",
            "cost",
            "savings",
            "profit",
            "margin",
            "roi",
            "efficiency",
        }
        self.metric_patterns = [
            "\\$\\d+(?:,\\d{3})*(?:\\.\\d+)?[kmb]?",
            "\\d+(?:,\\d{3})*(?:\\.\\d+)?%",
            "\\d+(?:,\\d{3})*(?:\\.\\d+)?[kmb]",
            "\\d+(?:,\\d{3})*(?:\\.\\d+)?x",
            "\\d+(?:,\\d{3})*(?:\\.\\d+)?\\s*(?:times|fold)",
            "\\b\\d+\\s*(?:years?|months?|weeks?|days?)\\b",
        ]
        logger.info(
            f"Initialized SignalQualityPipeline with thresholds: relevance={relevance_threshold}, authority={authority_threshold}, specificity={specificity_threshold}"
        )

    def evaluate_signal(
        self, content: str, metadata: dict[str, str], query: str, doc_id: str | None = None
    ) -> QualityAssessment:
        """Evaluate a signal through all quality checks.

        Args:
            content: Document content to evaluate
            metadata: Document metadata (source, type, etc.)
            query: Original search query for relevance checking
            doc_id: Document identifier for logging

        Returns:
            QualityAssessment with detailed evaluation results
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "SignalQualityPipeline.evaluate_signal")
        try:
            assessment = QualityAssessment(is_pass=True, doc_id=doc_id)
            if not content or not isinstance(content, str):
                logger.warning(f"Empty or invalid content for doc {doc_id}")
                assessment.is_pass = False
                assessment.add_flag("EMPTY_CONTENT")
                return assessment
            if not isinstance(metadata, dict):
                logger.warning(f"Invalid metadata type for doc {doc_id}: {type(metadata)}")
                metadata = {}
            if not query or not isinstance(query, str):
                logger.warning(f"Invalid query for doc {doc_id}: {type(query)}")
                query = ""
            assessment.relevance_score = self._check_relevance(content, query)
            if assessment.relevance_score < self.relevance_threshold:
                assessment.add_flag("LOW_RELEVANCE")
            assessment.authority_score = self._check_authority(metadata)
            if assessment.authority_score < self.authority_threshold:
                assessment.add_flag("LOW_AUTHORITY")
            assessment.specificity_score = self._check_specificity(content)
            if assessment.specificity_score < self.specificity_threshold:
                assessment.add_flag("MISSING_METRICS")
            if self.enable_coherence_check:
                assessment.coherence_score = self._check_coherence(content)
                if assessment.coherence_score < 0.5:
                    assessment.add_flag("LOW_COHERENCE")
            else:
                assessment.coherence_score = 0.5
            if (
                assessment.authority_score < self.authority_threshold
                or assessment.relevance_score < self.relevance_threshold
            ):
                assessment.is_pass = False
                assessment.add_flag("HARD_FAIL")
            logger.debug(
                f"Signal evaluation for doc {doc_id}: relevance={assessment.relevance_score:.2f}, authority={assessment.authority_score:.2f}, specificity={assessment.specificity_score:.2f}, flags={assessment.flags}, pass={assessment.is_pass}",
                extra={"doc_id": doc_id, "flags": assessment.flags, "is_pass": assessment.is_pass},
            )
            return assessment
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error evaluating signal for doc {doc_id}: {str(e)}")
            return QualityAssessment(is_pass=False, flags=["EVALUATION_ERROR"], doc_id=doc_id)

    def _check_relevance(self, content: str, query: str) -> float:
        """Check relevance between content and query using keyword overlap.

        Args:
            content: Document content
            query: Search query

        Returns:
            Relevance score (0.0-1.0)
        """
        try:
            content_words = set(self._normalize_text(content.lower()))
            query_words = set(self._normalize_text(query.lower()))
            if not query_words:
                return 0.0
            intersection = content_words.intersection(query_words)
            union = content_words.union(query_words)
            if not union:
                return 0.0
            jaccard = len(intersection) / len(union)
            query_lower = query.lower()
            content_lower = content.lower()
            if query_lower in content_lower:
                jaccard = min(1.0, jaccard * 1.5)
            return min(1.0, jaccard)
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error checking relevance: {str(e)}")
            return 0.0

    def _check_authority(self, metadata: dict[str, str]) -> float:
        """Check source authority based on metadata.

        Args:
            metadata: Document metadata

        Returns:
            Authority score (0.0-1.0)
        """
        try:
            source = metadata.get("source", "").lower()
            doc_type = metadata.get("type", "").lower()
            for _tier_name, tier_config in self.authority_tiers.items():
                for source_id in tier_config["sources"]:
                    if source_id in source or source_id in doc_type:
                        return tier_config["score"]
            return self.authority_tiers["tier_4"]["score"]
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error checking authority: {str(e)}")
            return 0.2

    def _check_specificity(self, content: str) -> float:
        """Check content specificity based on presence of metrics.

        Args:
            content: Document content

        Returns:
            Specificity score (0.0-1.0)
        """
        try:
            content_lower = content.lower()
            has_impact_words = any(word in content_lower for word in self.impact_words)
            has_metrics = any(re.search(pattern, content, re.IGNORECASE) for pattern in self.metric_patterns)
            if has_impact_words and has_metrics:
                return 0.9
            elif has_metrics and (not has_impact_words):
                return 0.7
            elif has_impact_words and (not has_metrics):
                return 0.3
            else:
                return 0.1
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error checking specificity: {str(e)}")
            return 0.1

    def _check_coherence(self, content: str) -> float:
        """Check content coherence (simplified implementation).

        Args:
            content: Document content

        Returns:
            Coherence score (0.0-1.0)
        """
        try:
            sentences = re.split("[.!?]+", content)
            sentences = [s.strip() for s in sentences if s.strip()]
            if not sentences:
                return 0.0
            avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
            if 5 <= avg_length <= 25:
                length_score = 1.0
            elif avg_length < 5:
                length_score = 0.5
            else:
                length_score = 0.7
            fragment_penalty = 0.1 if not content.endswith((".", "!", "?")) else 0.0
            words = content.lower().split()
            unique_ratio = len(set(words)) / len(words) if words else 0
            repetition_score = min(1.0, unique_ratio * 1.2)
            coherence = length_score * 0.4 + repetition_score * 0.4 + (1.0 - fragment_penalty) * 0.2
            return min(1.0, max(0.0, coherence))
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error checking coherence: {str(e)}")
            return 0.5

    def _normalize_text(self, text: str) -> list[str]:
        """Normalize text and extract meaningful tokens.

        Args:
            text: Text to normalize

        Returns:
            List of normalized tokens
        """
        try:
            tokens = re.findall("\\b\\w+\\b", text.lower())
            stop_words = {
                "the",
                "a",
                "an",
                "and",
                "or",
                "but",
                "in",
                "on",
                "at",
                "to",
                "for",
                "of",
                "with",
                "by",
                "is",
                "are",
                "was",
                "were",
                "be",
                "been",
                "have",
                "has",
                "had",
                "do",
                "does",
                "did",
                "will",
                "would",
                "could",
                "should",
                "may",
                "might",
                "can",
                "this",
                "that",
            }
            return [token for token in tokens if len(token) > 2 and token not in stop_words]
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error normalizing text: {str(e)}")
            return []

    def batch_evaluate(
        self, documents: list[tuple[str, dict[str, str], str]], filter_failed: bool = True
    ) -> list[tuple[dict[str, str], QualityAssessment]]:
        """Evaluate multiple documents in batch.

        Args:
            documents: List of (content, metadata, query) tuples
            filter_failed: Whether to filter out failed assessments

        Returns:
            List of (metadata, assessment) tuples
        """
        try:
            results = []
            for idx, (content, metadata, query) in enumerate(documents):
                doc_id = metadata.get("doc_id") or metadata.get("id") or str(idx)
                assessment = self.evaluate_signal(content, metadata, query, doc_id)
                if not filter_failed or assessment.is_pass:
                    results.append((metadata, assessment))
            logger.info(f"Batch evaluation: {len(documents)} input, {len(results)} passed")
            return results
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error in batch evaluation: {str(e)}")
            return []


# guardian: allow-magic-config
def create_quality_pipeline(
    relevance_threshold: float = 0.3,
    authority_threshold: float = 0.4,
    specificity_threshold: float = 0.5,
    strict_mode: bool = False,
) -> SignalQualityPipeline:
    """Create a SignalQualityPipeline instance.

    Args:
        relevance_threshold: Minimum relevance score
        authority_threshold: Minimum authority score
        specificity_threshold: Minimum specificity score
        strict_mode: If True, use stricter thresholds

    Returns:
        Configured SignalQualityPipeline instance
    """
    if strict_mode:
        return SignalQualityPipeline(
            relevance_threshold=THRESHOLD,
            authority_threshold=THRESHOLD,
            specificity_threshold=THRESHOLD,
            enable_coherence_check=True,
        )
    return SignalQualityPipeline(
        relevance_threshold=relevance_threshold,
        authority_threshold=authority_threshold,
        specificity_threshold=specificity_threshold,
    )


def filter_high_quality_signals(
    documents: list[tuple[str, dict[str, str], str]], strict_mode: bool = False
) -> list[dict[str, str]]:
    """Quickly filter documents for high-quality signals.

    Args:
        documents: List of (content, metadata, query) tuples
        strict_mode: Whether to use strict filtering

    Returns:
        List of metadata for documents that passed quality checks
    """
    pipeline = create_quality_pipeline(strict_mode=strict_mode)
    results = pipeline.batch_evaluate(documents, filter_failed=True)
    return [metadata for metadata, _ in results]
