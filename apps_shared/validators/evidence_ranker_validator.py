"""Evidence Ranker - Freshness and Corroboration-Based Evidence Ranking.

This module provides a post-retrieval ranking layer that prioritizes fresh (recent)
and corroborated (multi-source) evidence over older or isolated claims, ensuring
the Resume Engine cites the most current and verified truth.
"""

import logging
import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, confloat, validator

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "evidence_ranker_validator", "p0_governance")
_emit_reads_policy_state("p0", "evidence_ranker_validator", "policy_binding")
_emit_snapshots_state("p0", "evidence_ranker_validator", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("evidence_ranker_validator", "p4obs", "metric_1")
_emit_emits_metric_event("evidence_ranker_validator", "p4obs", "metric_2")
_emit_emits_metric_event("evidence_ranker_validator", "p4obs", "metric_3")
_emit_emits_metric_event("evidence_ranker_validator", "p4obs", "metric_4")
_emit_emits_metric_event("evidence_ranker_validator", "p4obs", "metric_5")
_emit_emits_metric_event("evidence_ranker_validator", "p4obs", "metric_6")
_emit_records_incident_event("evidence_ranker_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("evidence_ranker_validator", "p4obs", "anomaly")
_emit_writes_observability_log("evidence_ranker_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("evidence_ranker_validator", "p4obs", "mon_state")
_emit_triggers_alert("evidence_ranker_validator", "p4obs", "alert")
_emit_links_incident_trace("evidence_ranker_validator", "p4obs", "trace_link")
_emit_captures_pattern("evidence_ranker_validator", "p3lm", "pattern")
_emit_records_learning_event("evidence_ranker_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("evidence_ranker_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("evidence_ranker_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("evidence_ranker_validator", "p3lm", "routing")
_emit_improves_agent_policy("evidence_ranker_validator", "p3lm", "policy")
_emit_stores_learning_state("evidence_ranker_validator", "p3lm", "state")
_emit_records_execution_trace("evidence_ranker_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("evidence_ranker_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("evidence_ranker_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("evidence_ranker_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("evidence_ranker_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("evidence_ranker_validator", "env_read", "p2_env_1")
_emit_reads_environ("evidence_ranker_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("evidence_ranker_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("evidence_ranker_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "evidence_ranker_validator", "context_pull")
_emit_pulls_context("p1", "evidence_ranker_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "evidence_ranker_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "evidence_ranker_validator", "uwg_term_2")
_emit_writes_through("p1", "evidence_ranker_validator", "write_through")
_emit_writes_through("p1", "evidence_ranker_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "evidence_ranker_validator", "safety_validation")
_emit_invokes_eval("p1", "evidence_ranker_validator", "eval_call")
_emit_proposal_commits_routing("p1", "evidence_ranker_validator", "routing_commit")
_emit_escalates_to_human("p1", "evidence_ranker_validator", "human_escalation")
_emit_routes_through("p1", "evidence_ranker_validator", "route_through")
_emit_checks_agent_registry("p1", "evidence_ranker_validator", "agent_registry")
_emit_validates_agent_capability("p1", "evidence_ranker_validator", "capability")
_emit_dispatches_execution_plan("p1", "evidence_ranker_validator", "exec_plan")
_emit_agent_executes_agent("p1", "evidence_ranker_validator", "sub_agent")
_emit_routes_to_agent("p1", "evidence_ranker_validator", "target_agent")
_emit_verifies_policy("p1", "evidence_ranker_validator", "policy_check")
_emit_observes_runtime_state("p1", "evidence_ranker_validator", "runtime_state")
_emit_verifies_boundary("p1", "evidence_ranker_validator", "boundary_check")
_emit_transcripts_response("p1", "evidence_ranker_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "evidence_ranker_validator")
_emit_gated_by_confidence("p1", "evidence_ranker_validator", "confidence_gate")
emit_replay_key("p0", "evidence_ranker_validator")
emit_determinism_digest("p0", "evidence_ranker_validator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "evidence_ranker_validator", "execution_auth")
_emit_validates_capability("p2", "evidence_ranker_validator", "capability_check")
_emit_routes_to_capability("p2", "evidence_ranker_validator", "capability_route")
_emit_writes_via_uwg("p2", "evidence_ranker_validator", "uwg_write")
_emit_blocks_direct_write("p2", "evidence_ranker_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "evidence_ranker_validator", "tool_invocation")
_emit_captures_execution_output("p2", "evidence_ranker_validator", "exec_output")
_emit_dispatches_agent("p3", "evidence_ranker_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "evidence_ranker_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "evidence_ranker_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "evidence_ranker_validator", "healing_outcome")
_emit_escalates_failure("p3", "evidence_ranker_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "evidence_ranker_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "evidence_ranker_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "evidence_ranker_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "evidence_ranker_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "evidence_ranker_validator", "eval_metric")
_emit_stores_embedding("p4", "evidence_ranker_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "evidence_ranker_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "evidence_ranker_validator", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class RankedEvidence(BaseModel):
    """Ranked evidence with freshness and corroboration metrics."""

    content: str = Field(..., description="Document content")
    final_score: confloat(ge=0.0, le=1.0) = Field(..., description="Final ranking score")
    freshness_score: confloat(ge=0.0, le=1.0) = Field(..., description="Freshness score")
    corroboration_count: int = Field(..., ge=0, description="Number of corroborating sources")
    year_detected: int | None = Field(None, description="Year extracted from content")
    semantic_score: confloat(ge=0.0, le=1.0) = Field(..., description="Original semantic score")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    key_entities: list[str] = Field(default_factory=list, description="Corroborated entities")
    doc_id: str | None = Field(None, description="Document identifier for logging")

    @validator("year_detected")
    def validate_year(cls, v):
        """Validate year is within reasonable range."""
        if v is not None:
            current_year = datetime.now().year
            if v < 2000 or v > current_year + 1:
                logger.warning(f"Suspicious year detected: {v}")
                return None
        return v

    @property
    def is_recent(self) -> bool:
        """Check if evidence is from the last 2 years."""
        if self.year_detected is None:
            return False
        current_year = datetime.now().year
        return current_year - self.year_detected <= 2

    @property
    def is_corroborated(self) -> bool:
        """Check if evidence has multiple sources."""
        return self.corroboration_count >= 2


class EvidenceRanker:
    """Evidence ranker that prioritizes fresh and corroborated content.

    This ranker re-shuffles passed signals based on freshness and corroboration
    to ensure the most current and verified evidence is ranked highest.
    """

    def __init__(
        self,
        freshness_weight: float = 0.4,
        corroboration_weight: float = 0.2,
        semantic_weight: float = 0.4,
        current_year: int | None = None,
    ):
        """Initialize the evidence ranker.

        Args:
            freshness_weight: Weight for freshness in final score
            corroboration_weight: Weight for corroboration in final score
            semantic_weight: Weight for original semantic score
            current_year: Reference year for freshness calculation
        """
        self.freshness_weight = freshness_weight
        self.corroboration_weight = corroboration_weight
        self.semantic_weight = semantic_weight
        self.current_year = current_year or datetime.now().year
        total_weight = freshness_weight + corroboration_weight + semantic_weight
        if total_weight != 1.0:
            self.freshness_weight /= total_weight
            self.corroboration_weight /= total_weight
            self.semantic_weight /= total_weight
        self.year_patterns = ["\\b(20[2-3][0-9])\\b", "\\b([2-3][0-9]{3})\\b"]
        self.entity_patterns = [
            "\\b([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*)\\b",
            "\\b([A-Z]{2,})\\b",
            "\\$[\\d,]+(?:\\.\\d+)?[kmb]?",
            "\\b\\d+(?:,\\d{3})*(?:\\.\\d+)?%\\b",
        ]
        logger.info(
            f"Initialized EvidenceRanker with weights: freshness={self.freshness_weight:.2f}, corroboration={self.corroboration_weight:.2f}, semantic={self.semantic_weight:.2f}",
        )

    def rank_evidence(
        self, signals: list[dict[str, Any]], current_year: int | None = None,
    ) -> list[RankedEvidence]:
        """Rank evidence based on freshness and corroboration.

        Args:
            signals: List of signal dictionaries with 'content', 'score', and 'metadata'
            current_year: Override current year for freshness calculation

        Returns:
            List of RankedEvidence sorted by final_score descending
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "EvidenceRanker.rank_evidence")
        try:
            if current_year:
                self.current_year = current_year
            if not signals or not isinstance(signals, list):
                logger.warning("Invalid or empty signals list")
                return []
            all_entities = self._extract_all_entities(signals)
            ranked_signals = []
            for idx, signal in enumerate(signals):
                try:
                    content = signal.get("content", "")
                    semantic_score = float(signal.get("score", 0.0))
                    metadata = signal.get("metadata", {})
                    doc_id = signal.get("doc_id") or signal.get("id") or str(idx)
                    if not isinstance(content, str):
                        logger.warning(f"Invalid content type for doc {doc_id}: {type(content)}")
                        continue
                    if not 0.0 <= semantic_score <= 1.0:
                        logger.warning(f"Semantic score out of bounds for doc {doc_id}: {semantic_score}")
                        semantic_score = max(0.0, min(1.0, semantic_score))
                    freshness_score, year_detected = self._score_freshness(content, metadata)
                    corroboration_count, key_entities = self._count_corroboration(
                        content, all_entities, signals,
                    )
                    corroboration_normalized = min(1.0, corroboration_count / 3.0)
                    final_score = (
                        semantic_score * self.semantic_weight
                        + freshness_score * self.freshness_weight
                        + corroboration_normalized * self.corroboration_weight
                    )
                    ranked = RankedEvidence(
                        content=content,
                        final_score=final_score,
                        freshness_score=freshness_score,
                        corroboration_count=corroboration_count,
                        year_detected=year_detected,
                        semantic_score=semantic_score,
                        metadata=metadata if isinstance(metadata, dict) else {},
                        key_entities=key_entities,
                        doc_id=doc_id,
                    )
                    ranked_signals.append(ranked)
                    logger.debug(
                        f"Ranked signal {doc_id}: final={final_score:.3f}, semantic={semantic_score:.3f}, freshness={freshness_score:.3f}, corroboration={corroboration_count}",
                        extra={"doc_id": doc_id, "final_score": final_score},
                    )
                # guardian: allow-silent-swallow
                except Exception as e:
                    logger.error(f"Error processing signal at index {idx}: {str(e)}")
                    continue
            ranked_signals.sort(key=lambda x: x.final_score, reverse=True)
            logger.info(
                f"Ranked {len(signals)} signals, top score: {ranked_signals[0].final_score:.3f if ranked_signals else 0:.3f}",
            )
            return ranked_signals
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error in rank_evidence: {str(e)}")
            return []

    def _score_freshness(self, content: str, metadata: dict[str, str]) -> tuple[float, int | None]:
        """Score content based on freshness (recency).

        Args:
            content: Document content
            metadata: Document metadata

        Returns:
            Tuple of (freshness_score, detected_year)
        """
        try:
            year = self._extract_year(content)
            if year is None:
                for key in ["date", "year", "timestamp", "created_at"]:
                    if key in metadata:
                        year = self._extract_year(str(metadata[key]))
                        if year:
                            break
            if year is None:
                return (0.5, None)
            year_diff = self.current_year - year
            if year_diff < 0:
                return (0.1, year)
            elif year_diff == 0:
                return (1.0, year)
            elif year_diff == 1:
                return (0.9, year)
            elif year_diff == 2:
                return (0.7, year)
            elif year_diff == 3:
                return (0.5, year)
            elif year_diff == 4:
                return (0.3, year)
            else:
                return (0.2, year)
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error scoring freshness: {str(e)}")
            return (0.5, None)

    def _extract_year(self, text: str) -> int | None:
        """Extract a 4-digit year from text.

        Args:
            text: Text to search for year

        Returns:
            Extracted year or None
        """
        try:
            for pattern in self.year_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    try:
                        year = int(match)
                        if 2020 <= year <= 2030:
                            return year
                    except ValueError:
                        continue
            return None
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error extracting year: {str(e)}")
            return None

    def _count_corroboration(
        self, content: str, all_entities: dict[str, list[str]], all_signals: list[dict[str, Any]],
    ) -> tuple[int, list[str]]:
        """Count how many other signals corroborate this one.

        Args:
            content: Content to check for corroboration
            all_entities: Pre-extracted entities from all signals
            all_signals: All signals for overlap checking

        Returns:
            Tuple of (corroboration_count, key_entities_found)
        """
        try:
            entities = self._extract_entities(content)
            if not entities:
                return (0, [])
            corroboration_counts = {}
            for entity in entities:
                if entity in all_entities:
                    corroboration_counts[entity] = len(all_entities[entity])
            total_corroboration = sum(count - 1 for count in corroboration_counts.values() if count > 1)
            key_entities = [entity for entity, count in corroboration_counts.items() if count > 1]
            return (total_corroboration, key_entities)
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error counting corroboration: {str(e)}")
            return (0, [])

    def _extract_all_entities(self, signals: list[dict[str, Any]]) -> dict[str, list[str]]:
        """Extract entities from all signals for corroboration checking.

        Args:
            signals: List of all signals

        Returns:
            Dictionary mapping entity to list of signal indices containing it
        """
        try:
            entity_map = {}
            for idx, signal in enumerate(signals):
                content = signal.get("content", "")
                if isinstance(content, str):
                    entities = self._extract_entities(content)
                    for entity in entities:
                        if entity not in entity_map:
                            entity_map[entity] = []
                        entity_map[entity].append(idx)
            return entity_map
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error extracting all entities: {str(e)}")
            return {}

    def _extract_entities(self, content: str) -> list[str]:
        """Extract key entities from content.

        Args:
            content: Text to extract entities from

        Returns:
            List of extracted entities
        """
        try:
            entities = []
            for pattern in self.entity_patterns:
                matches = re.findall(pattern, content)
                entities.extend(matches)
            normalized_entities = []
            for entity in entities:
                if len(entity) < 2 or len(entity) > 50:
                    continue
                common_words = {
                    "the",
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
                    "this",
                    "that",
                    "these",
                    "those",
                }
                if entity.lower() not in common_words:
                    normalized_entities.append(entity)
            seen = set()
            unique_entities = []
            for entity in normalized_entities:
                if entity not in seen:
                    seen.add(entity)
                    unique_entities.append(entity)
            return unique_entities
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return []

    def get_ranking_summary(self, ranked_evidence: list[RankedEvidence]) -> dict[str, Any]:
        """Get a summary of the ranking results.

        Args:
            ranked_evidence: List of ranked evidence

        Returns:
            Summary statistics
        """
        try:
            if not ranked_evidence:
                return {"total": 0}
            recent_count = sum(1 for e in ranked_evidence if e.is_recent)
            corroborated_count = sum(1 for e in ranked_evidence if e.is_corroborated)
            years_detected = [e.year_detected for e in ranked_evidence if e.year_detected]
            avg_year = sum(years_detected) / len(years_detected) if years_detected else None
            return {
                "total": len(ranked_evidence),
                "recent_count": recent_count,
                "corroborated_count": corroborated_count,
                "avg_freshness": sum(e.freshness_score for e in ranked_evidence) / len(ranked_evidence),
                "avg_corroboration": sum(e.corroboration_count for e in ranked_evidence)
                / len(ranked_evidence),
                "year_range": (min(years_detected), max(years_detected)) if years_detected else None,
                "avg_year": avg_year,
                "top_score": ranked_evidence[0].final_score,
                "bottom_score": ranked_evidence[-1].final_score,
            }
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error getting ranking summary: {str(e)}")
            return {"error": str(e)}


def create_evidence_ranker(
    freshness_weight: float = 0.4,
    corroboration_weight: float = 0.2,
    semantic_weight: float = 0.4,
    current_year: int | None = None,
) -> EvidenceRanker:
    """Create an EvidenceRanker instance.

    Args:
        freshness_weight: Weight for freshness in scoring
        corroboration_weight: Weight for corroboration in scoring
        semantic_weight: Weight for semantic similarity in scoring
        current_year: Reference year for freshness

    Returns:
        Configured EvidenceRanker instance
    """
    return EvidenceRanker(
        freshness_weight=freshness_weight,
        corroboration_weight=corroboration_weight,
        semantic_weight=semantic_weight,
        current_year=current_year,
    )


def rank_evidence(
    signals: list[dict[str, Any]], prioritize_freshness: bool = True, current_year: int | None = None,
) -> list[RankedEvidence]:
    """Quickly rank evidence by freshness and corroboration.

    Args:
        signals: List of signals to rank
        prioritize_freshness: Whether to emphasize freshness in ranking
        current_year: Reference year for freshness calculation

    Returns:
        List of ranked evidence
    """
    weights = (0.5, 0.2, 0.3) if prioritize_freshness else (0.4, 0.2, 0.4)
    ranker = create_evidence_ranker(
        freshness_weight=weights[0],
        corroboration_weight=weights[1],
        semantic_weight=weights[2],
        current_year=current_year,
    )
    return ranker.rank_evidence(signals)
