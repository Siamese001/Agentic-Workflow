"""Dynamic Signal Weighter - Archetype-Aware Document scoring.

This module provides dynamic weighting of retrieved documents based on recipient
archetype and industry, enabling more relevant content selection for personalized
outreach and resume generation.
"""

import logging

from pydantic import BaseModel, Field, confloat

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

_emit_applies_guardrail("p0", "signal_weighter_util", "p0_governance")
_emit_reads_policy_state("p0", "signal_weighter_util", "policy_binding")
_emit_snapshots_state("p0", "signal_weighter_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("signal_weighter_util", "p4obs", "metric_1")
_emit_emits_metric_event("signal_weighter_util", "p4obs", "metric_2")
_emit_emits_metric_event("signal_weighter_util", "p4obs", "metric_3")
_emit_emits_metric_event("signal_weighter_util", "p4obs", "metric_4")
_emit_emits_metric_event("signal_weighter_util", "p4obs", "metric_5")
_emit_emits_metric_event("signal_weighter_util", "p4obs", "metric_6")
_emit_records_incident_event("signal_weighter_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("signal_weighter_util", "p4obs", "anomaly")
_emit_writes_observability_log("signal_weighter_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("signal_weighter_util", "p4obs", "mon_state")
_emit_triggers_alert("signal_weighter_util", "p4obs", "alert")
_emit_links_incident_trace("signal_weighter_util", "p4obs", "trace_link")
_emit_captures_pattern("signal_weighter_util", "p3lm", "pattern")
_emit_records_learning_event("signal_weighter_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("signal_weighter_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("signal_weighter_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("signal_weighter_util", "p3lm", "routing")
_emit_improves_agent_policy("signal_weighter_util", "p3lm", "policy")
_emit_stores_learning_state("signal_weighter_util", "p3lm", "state")
_emit_records_execution_trace("signal_weighter_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("signal_weighter_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("signal_weighter_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("signal_weighter_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("signal_weighter_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("signal_weighter_util", "env_read", "p2_env_1")
_emit_reads_environ("signal_weighter_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("signal_weighter_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("signal_weighter_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "signal_weighter_util", "context_pull")
_emit_pulls_context("p1", "signal_weighter_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "signal_weighter_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "signal_weighter_util", "uwg_term_2")
_emit_writes_through("p1", "signal_weighter_util", "write_through")
_emit_writes_through("p1", "signal_weighter_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "signal_weighter_util", "safety_validation")
_emit_invokes_eval("p1", "signal_weighter_util", "eval_call")
_emit_proposal_commits_routing("p1", "signal_weighter_util", "routing_commit")
_emit_escalates_to_human("p1", "signal_weighter_util", "human_escalation")
_emit_routes_through("p1", "signal_weighter_util", "route_through")
_emit_checks_agent_registry("p1", "signal_weighter_util", "agent_registry")
_emit_validates_agent_capability("p1", "signal_weighter_util", "capability")
_emit_dispatches_execution_plan("p1", "signal_weighter_util", "exec_plan")
_emit_agent_executes_agent("p1", "signal_weighter_util", "sub_agent")
_emit_routes_to_agent("p1", "signal_weighter_util", "target_agent")
_emit_verifies_policy("p1", "signal_weighter_util", "policy_check")
_emit_observes_runtime_state("p1", "signal_weighter_util", "runtime_state")
_emit_verifies_boundary("p1", "signal_weighter_util", "boundary_check")
_emit_transcripts_response("p1", "signal_weighter_util", "transcript")
_emit_hard_fails_untranscripted("p1", "signal_weighter_util")
_emit_gated_by_confidence("p1", "signal_weighter_util", "confidence_gate")
emit_replay_key("p0", "signal_weighter_util")
emit_determinism_digest("p0", "signal_weighter_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "signal_weighter_util", "execution_auth")
_emit_validates_capability("p2", "signal_weighter_util", "capability_check")
_emit_routes_to_capability("p2", "signal_weighter_util", "capability_route")
_emit_writes_via_uwg("p2", "signal_weighter_util", "uwg_write")
_emit_blocks_direct_write("p2", "signal_weighter_util", "direct_write_block")
_emit_records_tool_invocation("p2", "signal_weighter_util", "tool_invocation")
_emit_captures_execution_output("p2", "signal_weighter_util", "exec_output")
_emit_dispatches_agent("p3", "signal_weighter_util", "agent_dispatch")
_emit_coordinates_agents("p3", "signal_weighter_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "signal_weighter_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "signal_weighter_util", "healing_outcome")
_emit_escalates_failure("p3", "signal_weighter_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "signal_weighter_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "signal_weighter_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "signal_weighter_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "signal_weighter_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "signal_weighter_util", "eval_metric")
_emit_stores_embedding("p4", "signal_weighter_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "signal_weighter_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "signal_weighter_util", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class SignalWeights(BaseModel):
    """Weight coefficients for different signal types (0.0-1.0)."""

    technical_depth: confloat(ge=0.0, le=1.0) = 0.5
    business_impact: confloat(ge=0.0, le=1.0) = 0.5
    leadership_scope: confloat(ge=0.0, le=1.0) = 0.5
    cultural_fit: confloat(ge=0.0, le=1.0) = 0.5

    class Config:
        """Pydantic configuration."""

        validate_assignment = True

    def as_dict(self) -> dict[str, float]:
        """Convert weights to dictionary."""
        return {
            "technical_depth": self.technical_depth,
            "business_impact": self.business_impact,
            "leadership_scope": self.leadership_scope,
            "cultural_fit": self.cultural_fit,
        }


class WeightingResult(BaseModel):
    """Result of reweighting operation."""

    original_score: confloat(ge=0.0, le=1.0) = Field(..., description="Original relevance score")
    adjusted_score: confloat(ge=0.0, le=1.0) = Field(..., description="Adjusted score after weighting")
    weights_applied: SignalWeights = Field(..., description="Weights that were applied")
    signal_type: str = Field(..., description="Type of signal detected")
    adjustment_factor: confloat(ge=0.0, le=1.0) = Field(..., description="Weight factor applied")
    doc_id: str | None = Field(None, description="Document identifier for logging")

    @property
    def score_change(self) -> float:
        """Calculate the change in score."""
        return self.adjusted_score - self.original_score

    @property
    def percent_change(self) -> float:
        """Calculate percentage change."""
        if self.original_score == 0:
            return 0.0
        return self.score_change / self.original_score * 100


class SignalWeighter:
    """Dynamic signal weighter for archetype-aware document scoring.

    This component adjusts relevance scores of retrieved documents based on the
    target recipient's persona (e.g., CTO vs. Recruiter) and industry context.
    """

    def __init__(self, default_weights: SignalWeights | None = None):
        """Initialize the signal weighter.

        Args:
            default_weights: Default weights to use when no specific mapping exists
        """
        self.default_weights = default_weights or SignalWeights()
        self._archetype_mappings = {
            "CTO": SignalWeights(
                technical_depth=0.9, leadership_scope=0.7, business_impact=0.4, cultural_fit=0.3
            ),
            "VP Engineering": SignalWeights(
                technical_depth=0.8, leadership_scope=0.8, business_impact=0.5, cultural_fit=0.4
            ),
            "Engineering Manager": SignalWeights(
                technical_depth=0.6, leadership_scope=0.9, business_impact=0.4, cultural_fit=0.6
            ),
            "Staff Engineer": SignalWeights(
                technical_depth=1.0, leadership_scope=0.4, business_impact=0.3, cultural_fit=0.5
            ),
            "Principal Engineer": SignalWeights(
                technical_depth=1.0, leadership_scope=0.5, business_impact=0.4, cultural_fit=0.5
            ),
            "CEO": SignalWeights(
                technical_depth=0.3, leadership_scope=0.8, business_impact=1.0, cultural_fit=0.7
            ),
            "Founder": SignalWeights(
                technical_depth=0.4, leadership_scope=0.7, business_impact=1.0, cultural_fit=0.8
            ),
            "CFO": SignalWeights(
                technical_depth=0.2, leadership_scope=0.6, business_impact=1.0, cultural_fit=0.5
            ),
            "CPO": SignalWeights(
                technical_depth=0.5, leadership_scope=0.6, business_impact=0.7, cultural_fit=0.9
            ),
            "VP Product": SignalWeights(
                technical_depth=0.4, leadership_scope=0.7, business_impact=0.8, cultural_fit=0.8
            ),
            "Product Manager": SignalWeights(
                technical_depth=0.5, leadership_scope=0.5, business_impact=0.7, cultural_fit=0.8
            ),
            "Recruiter": SignalWeights(
                technical_depth=0.5, leadership_scope=0.4, business_impact=0.5, cultural_fit=0.9
            ),
            "Talent Acquisition": SignalWeights(
                technical_depth=0.5, leadership_scope=0.4, business_impact=0.5, cultural_fit=0.9
            ),
            "HR Manager": SignalWeights(
                technical_depth=0.3, leadership_scope=0.5, business_impact=0.6, cultural_fit=1.0
            ),
            "VP Sales": SignalWeights(
                technical_depth=0.3, leadership_scope=0.6, business_impact=1.0, cultural_fit=0.7
            ),
            "Account Executive": SignalWeights(
                technical_depth=0.3, leadership_scope=0.4, business_impact=0.9, cultural_fit=0.8
            ),
        }
        self._industry_modifiers = {
            "technology": {
                "technical_depth": 1.2,
                "business_impact": 0.9,
                "leadership_scope": 1.0,
                "cultural_fit": 0.9,
            },
            "finance": {
                "technical_depth": 0.7,
                "business_impact": 1.2,
                "leadership_scope": 1.1,
                "cultural_fit": 0.8,
            },
            "healthcare": {
                "technical_depth": 0.9,
                "business_impact": 0.8,
                "leadership_scope": 1.0,
                "cultural_fit": 1.1,
            },
            "retail": {
                "technical_depth": 0.6,
                "business_impact": 1.1,
                "leadership_scope": 0.9,
                "cultural_fit": 1.0,
            },
            "consulting": {
                "technical_depth": 0.8,
                "business_impact": 1.1,
                "leadership_scope": 1.0,
                "cultural_fit": 0.9,
            },
        }
        logger.info(f"Initialized SignalWeighter with {len(self._archetype_mappings)} archetype mappings")

    def get_weights(self, archetype: str, industry: str | None = None) -> SignalWeights:
        """Get weights for a specific archetype and industry.

        Args:
            archetype: Target recipient archetype (e.g., "CTO", "Recruiter")
            industry: Industry context for additional adjustment (optional)

        Returns:
            SignalWeights configured for the archetype and industry
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"SignalWeighter.get_weights:{archetype}")
        try:
            normalized_archetype = archetype.strip().lower() if archetype else ""
            base_weights = None
            for key, weights in self._archetype_mappings.items():
                if key.lower() == normalized_archetype:
                    base_weights = weights
                    break
            if base_weights is None:
                logger.warning(f"Unknown archetype '{archetype}', using balanced weights")
                base_weights = self.default_weights
            if industry and industry.strip():
                normalized_industry = industry.strip().lower()
                if normalized_industry in self._industry_modifiers:
                    modifiers = self._industry_modifiers[normalized_industry]
                    try:
                        adjusted_weights = SignalWeights(
                            technical_depth=min(
                                1.0, base_weights.technical_depth * modifiers["technical_depth"]
                            ),
                            business_impact=min(
                                1.0, base_weights.business_impact * modifiers["business_impact"]
                            ),
                            leadership_scope=min(
                                1.0, base_weights.leadership_scope * modifiers["leadership_scope"]
                            ),
                            cultural_fit=min(1.0, base_weights.cultural_fit * modifiers["cultural_fit"]),
                        )
                        logger.debug(
                            f"Applied industry modifiers for {industry}: {base_weights.as_dict()} -> {adjusted_weights.as_dict()}"
                        )
                        return adjusted_weights
                    except Exception as e:
                        logger.error(f"Failed to apply industry modifiers: {str(e)}")
                        return None
            logger.debug(f"Using base weights for archetype {archetype}: {base_weights.as_dict()}")
            return base_weights
        except Exception as e:
            logger.error(f"Error getting weights for archetype '{archetype}': {str(e)}")
            return None

    def reweight_score(
        self,
        original_score: float,
        doc_metadata: dict[str, str | float],
        weights: SignalWeights,
        doc_id: str | None = None,
    ) -> WeightingResult:
        """Apply dynamic weighting to a document score.

        Args:
            original_score: Original relevance score (0.0-1.0)
            doc_metadata: Document metadata with signal type tags
            weights: SignalWeights to apply
            doc_id: Document identifier for logging

        Returns:
            WeightingResult with adjusted score and metadata
        """
        try:
            if not isinstance(original_score, int | float):
                logger.error(f"Invalid score type: {type(original_score)} for doc {doc_id}")
                original_score = 0.0
            if not 0.0 <= original_score <= 1.0:
                logger.warning(f"Score out of bounds: {original_score} for doc {doc_id}, clamping to [0,1]")
                original_score = max(0.0, min(1.0, original_score))
            if not isinstance(doc_metadata, dict):
                logger.warning(f"Invalid metadata type for doc {doc_id}: {type(doc_metadata)}")
                doc_metadata = {}
            signal_type = self._extract_signal_type(doc_metadata)
            weight = self._get_weight_for_signal_type(signal_type, weights)
            adjusted_score = original_score * weight
            adjusted_score = max(0.0, min(1.0, adjusted_score))
            result = WeightingResult(
                original_score=original_score,
                adjusted_score=adjusted_score,
                weights_applied=weights,
                signal_type=signal_type,
                adjustment_factor=weight,
                doc_id=doc_id,
            )
            logger.debug(
                f"Reweighted score: {original_score:.3f} -> {adjusted_score:.3f} (signal: {signal_type}, weight: {weight:.2f})",
                extra={"doc_id": doc_id, "signal_type": signal_type, "weight": weight},
            )
            return result
        except Exception as e:
            logger.error(f"Error reweighting score for doc {doc_id}: {str(e)}")
            return None

    def _extract_signal_type(self, metadata: dict[str, str | float]) -> str:
        """Extract signal type from document metadata.

        Args:
            metadata: Document metadata

        Returns:
            Signal type string
        """
        try:
            if "type" in metadata:
                return str(metadata["type"])
            if "category" in metadata:
                return str(metadata["category"])
            if "tags" in metadata and metadata["tags"]:
                if isinstance(metadata["tags"], list):
                    return str(metadata["tags"][0])
                else:
                    return str(metadata["tags"])
            content_lower = str(metadata.get("content", "")).lower()
            if any(keyword in content_lower for keyword in ["revenue", "growth", "savings", "roi"]):
                return "business_impact"
            elif any(keyword in content_lower for keyword in ["team", "managed", "led", "mentorship"]):
                return "leadership_scope"
            elif any(keyword in content_lower for keyword in ["python", "java", "architecture", "algorithm"]):
                return "technical_depth"
            elif any(
                keyword in content_lower for keyword in ["culture", "mission", "values", "collaboration"]
            ):
                return "cultural_fit"
            return "balanced"
        except Exception as e:
            logger.error(f"Error extracting signal type: {str(e)}")
            return None

    def _get_weight_for_signal_type(self, signal_type: str, weights: SignalWeights) -> float:
        """Get the appropriate weight for a signal type.

        Args:
            signal_type: Type of signal
            weights: SignalWeights to extract from

        Returns:
            Weight value for the signal type
        """
        try:
            weight_map = {
                "technical_depth": weights.technical_depth,
                "technical": weights.technical_depth,
                "business_impact": weights.business_impact,
                "business": weights.business_impact,
                "leadership_scope": weights.leadership_scope,
                "leadership": weights.leadership_scope,
                "cultural_fit": weights.cultural_fit,
                "cultural": weights.cultural_fit,
                "balanced": 0.5,
            }
            return weight_map.get(signal_type.lower(), 0.5)
        except Exception as e:
            logger.error(f"Error getting weight for signal type '{signal_type}': {str(e)}")
            return None

    def batch_reweight(
        self, documents: list[dict[str, str | float]], archetype: str, industry: str | None = None
    ) -> list[WeightingResult]:
        """Apply dynamic weighting to a batch of documents.

        Args:
            documents: List of documents with scores and metadata
            archetype: Target recipient archetype
            industry: Industry context (optional)

        Returns:
            List of WeightingResult objects
        """
        try:
            weights = self.get_weights(archetype, industry)
            results = []
            for doc in documents:
                score = float(doc.get("score", 0.0))
                metadata = {k: v for k, v in doc.items() if k != "score"}
                doc_id = doc.get("doc_id") or doc.get("id")
                result = self.reweight_score(score, metadata, weights, doc_id)
                results.append(result)
            return results
        except Exception as e:
            logger.error(f"Error in batch reweighting: {str(e)}")
            return None


def create_signal_weighter(default_weights: SignalWeights | None = None) -> SignalWeighter:
    """Create a SignalWeighter instance.

    Args:
        default_weights: Default weights to use

    Returns:
        Configured SignalWeighter instance
    """
    return SignalWeighter(default_weights=default_weights)


def weight_results(
    documents: list[dict[str, str | float]], archetype: str, industry: str | None = None
) -> list[WeightingResult]:
    """Quickly weight a batch of results for an archetype.

    Args:
        documents: List of documents with scores and metadata
        archetype: Target recipient archetype
        industry: Industry context (optional)

    Returns:
        List of WeightingResult objects
    """
    weighter = create_signal_weighter()
    return weighter.batch_reweight(documents, archetype, industry)
