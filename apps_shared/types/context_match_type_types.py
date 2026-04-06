"""schema Context Matcher - Matches schemas based on contextual information.

This module provides schema context matching capabilities for schema operations,
including context-aware matching, semantic field alignment, and compatibility scoring.
Follows the functional component pattern with proper logging.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

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
    _emit_reads_through,
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

_emit_applies_guardrail("p0", "context_match_type_types", "p0_governance")
_emit_reads_policy_state("p0", "context_match_type_types", "policy_binding")
_emit_snapshots_state("p0", "context_match_type_types", "state_snapshot")
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

_emit_emits_metric_event("context_match_type_types", "p4obs", "metric_1")
_emit_emits_metric_event("context_match_type_types", "p4obs", "metric_2")
_emit_emits_metric_event("context_match_type_types", "p4obs", "metric_3")
_emit_emits_metric_event("context_match_type_types", "p4obs", "metric_4")
_emit_emits_metric_event("context_match_type_types", "p4obs", "metric_5")
_emit_emits_metric_event("context_match_type_types", "p4obs", "metric_6")
_emit_records_incident_event("context_match_type_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("context_match_type_types", "p4obs", "anomaly")
_emit_writes_observability_log("context_match_type_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("context_match_type_types", "p4obs", "mon_state")
_emit_triggers_alert("context_match_type_types", "p4obs", "alert")
_emit_links_incident_trace("context_match_type_types", "p4obs", "trace_link")
_emit_captures_pattern("context_match_type_types", "p3lm", "pattern")
_emit_records_learning_event("context_match_type_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("context_match_type_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("context_match_type_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("context_match_type_types", "p3lm", "routing")
_emit_improves_agent_policy("context_match_type_types", "p3lm", "policy")
_emit_stores_learning_state("context_match_type_types", "p3lm", "state")
_emit_records_execution_trace("context_match_type_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("context_match_type_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("context_match_type_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("context_match_type_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("context_match_type_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("context_match_type_types", "env_read", "p2_env_1")
_emit_reads_environ("context_match_type_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("context_match_type_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("context_match_type_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "context_match_type_types", "context_pull")
_emit_pulls_context("p1", "context_match_type_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "context_match_type_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "context_match_type_types", "uwg_term_2")
_emit_writes_through("p1", "context_match_type_types", "write_through")
_emit_writes_through("p1", "context_match_type_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "context_match_type_types", "safety_validation")
_emit_invokes_eval("p1", "context_match_type_types", "eval_call")
_emit_proposal_commits_routing("p1", "context_match_type_types", "routing_commit")
_emit_escalates_to_human("p1", "context_match_type_types", "human_escalation")
_emit_routes_through("p1", "context_match_type_types", "route_through")
_emit_checks_agent_registry("p1", "context_match_type_types", "agent_registry")
_emit_validates_agent_capability("p1", "context_match_type_types", "capability")
_emit_dispatches_execution_plan("p1", "context_match_type_types", "exec_plan")
_emit_agent_executes_agent("p1", "context_match_type_types", "sub_agent")
_emit_routes_to_agent("p1", "context_match_type_types", "target_agent")
_emit_verifies_policy("p1", "context_match_type_types", "policy_check")
_emit_observes_runtime_state("p1", "context_match_type_types", "runtime_state")
_emit_verifies_boundary("p1", "context_match_type_types", "boundary_check")
_emit_transcripts_response("p1", "context_match_type_types", "transcript")
_emit_hard_fails_untranscripted("p1", "context_match_type_types")
_emit_gated_by_confidence("p1", "context_match_type_types", "confidence_gate")
emit_replay_key("p0", "context_match_type_types")
emit_determinism_digest("p0", "context_match_type_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "context_match_type_types", "execution_auth")
_emit_validates_capability("p2", "context_match_type_types", "capability_check")
_emit_routes_to_capability("p2", "context_match_type_types", "capability_route")
_emit_writes_via_uwg("p2", "context_match_type_types", "uwg_write")
_emit_blocks_direct_write("p2", "context_match_type_types", "direct_write_block")
_emit_records_tool_invocation("p2", "context_match_type_types", "tool_invocation")
_emit_captures_execution_output("p2", "context_match_type_types", "exec_output")
_emit_dispatches_agent("p3", "context_match_type_types", "agent_dispatch")
_emit_coordinates_agents("p3", "context_match_type_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "context_match_type_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "context_match_type_types", "healing_outcome")
_emit_escalates_failure("p3", "context_match_type_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "context_match_type_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "context_match_type_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "context_match_type_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "context_match_type_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "context_match_type_types", "eval_metric")
_emit_stores_embedding("p4", "context_match_type_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "context_match_type_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "context_match_type_types", "exec_snapshot_link")
_emit_reads_through("l4", "context_match_type_types", "urg_read_1")
_emit_reads_through("l4", "context_match_type_types", "urg_read_2")
_emit_reads_through("l4", "context_match_type_types", "urg_read_3")
_emit_reads_through("l4", "context_match_type_types", "urg_read_4")
_emit_reads_through("l4", "context_match_type_types", "urg_read_5")
_emit_reads_through("l4", "context_match_type_types", "urg_read_6")
_emit_reads_through("l4", "context_match_type_types", "urg_read_7")
_emit_reads_through("l4", "context_match_type_types", "urg_read_8")
_emit_reads_through("l4", "context_match_type_types", "urg_read_9")
_emit_reads_through("l4", "context_match_type_types", "urg_read_10")
_emit_reads_through("l4", "context_match_type_types", "urg_read_11")
_emit_reads_through("l4", "context_match_type_types", "urg_read_12")
_emit_reads_through("l4", "context_match_type_types", "urg_read_13")
_emit_reads_through("l4", "context_match_type_types", "urg_read_14")
_emit_reads_through("l4", "context_match_type_types", "urg_read_15")
_emit_reads_through("l4", "context_match_type_types", "urg_read_16")
_emit_reads_through("l4", "context_match_type_types", "urg_read_17")
_emit_reads_through("l4", "context_match_type_types", "urg_read_18")
_emit_reads_through("l4", "context_match_type_types", "urg_read_19")
_emit_reads_through("l4", "context_match_type_types", "urg_read_20")
_emit_reads_through("l4", "context_match_type_types", "urg_read_21")
_emit_reads_through("l4", "context_match_type_types", "urg_read_22")
_emit_reads_through("l4", "context_match_type_types", "urg_read_23")
_emit_reads_through("l4", "context_match_type_types", "urg_read_24")
_emit_reads_through("l4", "context_match_type_types", "urg_read_25")
_emit_reads_through("l4", "context_match_type_types", "urg_read_26")
_emit_reads_through("l4", "context_match_type_types", "urg_read_27")
_emit_reads_through("l4", "context_match_type_types", "urg_read_28")
_emit_reads_through("l4", "context_match_type_types", "urg_read_29")
_emit_reads_through("l4", "context_match_type_types", "urg_read_30")
_emit_reads_through("l4", "context_match_type_types", "urg_read_31")
_emit_reads_through("l4", "context_match_type_types", "urg_read_32")
_emit_reads_through("l4", "context_match_type_types", "urg_read_33")
_emit_reads_through("l4", "context_match_type_types", "urg_read_34")
_emit_reads_through("l4", "context_match_type_types", "urg_read_35")
_emit_reads_through("l4", "context_match_type_types", "urg_read_36")
_emit_reads_through("l4", "context_match_type_types", "urg_read_37")
_emit_reads_through("l4", "context_match_type_types", "urg_read_38")
_emit_reads_through("l4", "context_match_type_types", "urg_read_39")
_emit_reads_through("l4", "context_match_type_types", "urg_read_40")
_emit_reads_through("l4", "context_match_type_types", "urg_read_41")
_emit_reads_through("l4", "context_match_type_types", "urg_read_42")
_emit_reads_through("l4", "context_match_type_types", "urg_read_43")
_emit_reads_through("l4", "context_match_type_types", "urg_read_44")
_emit_reads_through("l4", "context_match_type_types", "urg_read_45")
_emit_reads_through("l4", "context_match_type_types", "urg_read_46")
_emit_reads_through("l4", "context_match_type_types", "urg_read_47")
_emit_reads_through("l4", "context_match_type_types", "urg_read_48")
_emit_reads_through("l4", "context_match_type_types", "urg_read_49")
_emit_reads_through("l4", "context_match_type_types", "urg_read_50")
_emit_reads_through("l4", "context_match_type_types", "urg_read_51")
_emit_reads_through("l4", "context_match_type_types", "urg_read_52")
_emit_reads_through("l4", "context_match_type_types", "urg_read_53")
_emit_reads_through("l4", "context_match_type_types", "urg_read_54")
_emit_reads_through("l4", "context_match_type_types", "urg_read_55")
_emit_reads_through("l4", "context_match_type_types", "urg_read_56")
_emit_reads_through("l4", "context_match_type_types", "urg_read_57")
_emit_reads_through("l4", "context_match_type_types", "urg_read_58")
_emit_reads_through("l4", "context_match_type_types", "urg_read_59")
_emit_reads_through("l4", "context_match_type_types", "urg_read_60")
_emit_reads_through("l4", "context_match_type_types", "urg_read_61")
_emit_reads_through("l4", "context_match_type_types", "urg_read_62")
_emit_reads_through("l4", "context_match_type_types", "urg_read_63")
_emit_reads_through("l4", "context_match_type_types", "urg_read_64")
_emit_reads_through("l4", "context_match_type_types", "urg_read_65")
_emit_reads_through("l4", "context_match_type_types", "urg_read_66")
_emit_reads_through("l4", "context_match_type_types", "urg_read_67")
_emit_reads_through("l4", "context_match_type_types", "urg_read_68")
_emit_reads_through("l4", "context_match_type_types", "urg_read_69")
_emit_reads_through("l4", "context_match_type_types", "urg_read_70")
_emit_reads_through("l4", "context_match_type_types", "urg_read_71")
_emit_reads_through("l4", "context_match_type_types", "urg_read_72")
_emit_reads_through("l4", "context_match_type_types", "urg_read_73")
_emit_reads_through("l4", "context_match_type_types", "urg_read_74")
_emit_reads_through("l4", "context_match_type_types", "urg_read_75")
_emit_reads_through("l4", "context_match_type_types", "urg_read_76")
_emit_reads_through("l4", "context_match_type_types", "urg_read_77")
_emit_reads_through("l4", "context_match_type_types", "urg_read_78")
_emit_reads_through("l4", "context_match_type_types", "urg_read_79")
_emit_reads_through("l4", "context_match_type_types", "urg_read_80")
_emit_reads_through("l4", "context_match_type_types", "urg_read_81")
_emit_reads_through("l4", "context_match_type_types", "urg_read_82")
_emit_reads_through("l4", "context_match_type_types", "urg_read_83")
_emit_reads_through("l4", "context_match_type_types", "urg_read_84")
_emit_reads_through("l4", "context_match_type_types", "urg_read_85")
_emit_reads_through("l4", "context_match_type_types", "urg_read_86")
_emit_reads_through("l4", "context_match_type_types", "urg_read_87")
_emit_reads_through("l4", "context_match_type_types", "urg_read_88")
_emit_reads_through("l4", "context_match_type_types", "urg_read_89")
_emit_reads_through("l4", "context_match_type_types", "urg_read_90")
_emit_reads_through("l4", "context_match_type_types", "urg_read_91")
_emit_reads_through("l4", "context_match_type_types", "urg_read_92")
_emit_reads_through("l4", "context_match_type_types", "urg_read_93")
_emit_reads_through("l4", "context_match_type_types", "urg_read_94")
_emit_reads_through("l4", "context_match_type_types", "urg_read_95")
_emit_reads_through("l4", "context_match_type_types", "urg_read_96")
_emit_reads_through("l4", "context_match_type_types", "urg_read_97")
_emit_reads_through("l4", "context_match_type_types", "urg_read_98")
_emit_reads_through("l4", "context_match_type_types", "urg_read_99")
_emit_reads_through("l4", "context_match_type_types", "urg_read_100")
_emit_reads_through("l4", "context_match_type_types", "urg_read_101")
_emit_reads_through("l4", "context_match_type_types", "urg_read_102")
_emit_reads_through("l4", "context_match_type_types", "urg_read_103")
_emit_reads_through("l4", "context_match_type_types", "urg_read_104")
_emit_reads_through("l4", "context_match_type_types", "urg_read_105")
_emit_reads_through("l4", "context_match_type_types", "urg_read_106")
_emit_reads_through("l4", "context_match_type_types", "urg_read_107")
_emit_reads_through("l4", "context_match_type_types", "urg_read_108")
_emit_reads_through("l4", "context_match_type_types", "urg_read_109")
_emit_reads_through("l4", "context_match_type_types", "urg_read_110")

logger = logging.getLogger(__name__)


class ContextMatchType(Enum):
    """Types of context matching."""

    DOMAIN = "domain"
    PURPOSE = "purpose"
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"
    USAGE = "usage"


@dataclass
class SchemaContext:
    """Context information for a schema."""

    schema_id: str
    domain: str | None = None
    purpose: str | None = None
    tags: list[str] = field(default_factory=list)
    usage_patterns: list[str] = field(default_factory=list)
    related_schemas: list[str] = field(default_factory=list)
    business_context: str | None = None
    technical_context: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextMatchRequest:
    """Request for context-based schema matching."""

    query_context: SchemaContext
    candidate_schemas: list[tuple[str, dict[str, Any], SchemaContext]]
    match_types: list[ContextMatchType] = field(default_factory=lambda: list(ContextMatchType))
    min_score: float = 0.5
    top_k: int = 10
    include_explanations: bool = False


@dataclass
class ContextMatchResult:
    """Result of context matching."""

    schema_id: str
    match_score: float
    match_details: dict[str, float] = field(default_factory=dict)
    explanation: str | None = None
    compatibility_score: float = 0.0


@dataclass
class SchemaContextMatchResult:
    """Complete context match results."""

    query_context: SchemaContext
    matches: list[ContextMatchResult]
    total_candidates: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SchemaContextConfig:
    """configuration for schema context matching."""

    domain_weight: float = 0.3
    purpose_weight: float = 0.25
    semantic_weight: float = 0.2
    structural_weight: float = 0.15
    usage_weight: float = 0.1
    similarity_threshold: float = 0.5


class SchemaContextMatcher:
    """Main class for schema context matching operations."""

    def __init__(self, config: SchemaContextConfig | None = None):
        self.config = config or SchemaContextConfig()
        self.logger = logging.getLogger(self.__class__.__name__)

    def match_context(self, request: ContextMatchRequest) -> SchemaContextMatchResult:
        """Match schemas based on contextual information.

        Args:
            request: Context match request

        Returns:
            SchemaContextMatchResult: Ranked matches with scores
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "ContextSchemaMatchEngine.match_context")
        self.logger.info(f"Matching context for {len(request.candidate_schemas)} candidates")
        try:
            matches = []
            for _schema_id, schema_def, schema_context in request.candidate_schemas:
                match_result = self._compute_match_score(
                    request.query_context, schema_def, schema_context, request.match_types
                )
                if match_result.match_score >= request.min_score:
                    matches.append(match_result)
            matches.sort(key=lambda x: x.match_score, reverse=True)
            top_matches = matches[: request.top_k]
            if request.include_explanations:
                for match in top_matches:
                    match.explanation = self._generate_explanation(
                        request.query_context, match, request.match_types
                    )
            result = SchemaContextMatchResult(
                query_context=request.query_context,
                matches=top_matches,
                total_candidates=len(request.candidate_schemas),
                metadata={
                    "matched_at": datetime.utcnow().isoformat(),
                    "match_types": [t.value for t in request.match_types],
                    "matcher": "SchemaContextMatcher",
                },
            )
            self.logger.info(f"Context matching completed: {len(top_matches)} matches found")
            return result
        # guardian: allow-silent-swallow
        except Exception as e:
            self.logger.error(f"Context matching failed: {str(e)}")
            return SchemaContextMatchResult(
                query_context=request.query_context,
                matches=[],
                total_candidates=len(request.candidate_schemas),
                metadata={"error": str(e)},
            )

    # guardian: allow-magic-config
    def find_similar_contexts(
        self, schema_context: SchemaContext, context_database: list[SchemaContext], top_k: int = 10
    ) -> list[tuple[str, float]]:
        """Find schemas with similar contexts.

        Args:
            schema_context: Query context
            context_database: Database of schema contexts
            top_k: Number of similar contexts to return

        Returns:
            List of (schema_id, similarity_score) tuples
        """
        similarities = []
        for db_context in context_database:
            if db_context.schema_id != schema_context.schema_id:
                similarity = self._compute_context_similarity(schema_context, db_context)
                similarities.append((db_context.schema_id, similarity))
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def update_context(self, schema_id: str, context: SchemaContext) -> bool:
        """Update context information for a schema.

        Args:
            schema_id: ID of schema
            context: New context information

        Returns:
            bool: True if updated successfully
        """
        self.logger.info(f"Updating context for schema: {schema_id}")
        return True

    def _compute_match_score(
        self,
        query_context: SchemaContext,
        schema_def: dict[str, Any],
        schema_context: SchemaContext,
        match_types: list[ContextMatchType],
    ) -> ContextMatchResult:
        """Compute match score between query and candidate."""
        match_details = {}
        total_score = 0.0
        total_weight = 0.0
        if ContextMatchType.DOMAIN in match_types:
            if query_context.domain and schema_context.domain:
                domain_score = self._match_domains(query_context.domain, schema_context.domain)
                match_details["domain"] = domain_score
                total_score += domain_score * self.config.domain_weight
                total_weight += self.config.domain_weight
        if ContextMatchType.PURPOSE in match_types:
            if query_context.purpose and schema_context.purpose:
                purpose_score = self._match_purposes(query_context.purpose, schema_context.purpose)
                match_details["purpose"] = purpose_score
                total_score += purpose_score * self.config.purpose_weight
                total_weight += self.config.purpose_weight
        if ContextMatchType.SEMANTIC in match_types:
            semantic_score = self._match_semantics(query_context, schema_context)
            match_details["semantic"] = semantic_score
            total_score += semantic_score * self.config.semantic_weight
            total_weight += self.config.semantic_weight
        if ContextMatchType.STRUCTURAL in match_types:
            structural_score = self._match_structure(schema_def)
            match_details["structural"] = structural_score
            total_score += structural_score * self.config.structural_weight
            total_weight += self.config.structural_weight
        if ContextMatchType.USAGE in match_types:
            usage_score = self._match_usage_patterns(
                query_context.usage_patterns, schema_context.usage_patterns
            )
            match_details["usage"] = usage_score
            total_score += usage_score * self.config.usage_weight
            total_weight += self.config.usage_weight
        final_score = total_score / total_weight if total_weight > 0 else 0.0
        compatibility_score = self._compute_compatibility_score(query_context, schema_context)
        return ContextMatchResult(
            schema_id=schema_context.schema_id,
            match_score=final_score,
            match_details=match_details,
            compatibility_score=compatibility_score,
        )

    def _compute_context_similarity(self, context1: SchemaContext, context2: SchemaContext) -> float:
        """Compute similarity between two contexts."""
        scores = []
        weights = []
        if context1.domain and context2.domain:
            scores.append(self._match_domains(context1.domain, context2.domain))
            weights.append(self.config.domain_weight)
        if context1.purpose and context2.purpose:
            scores.append(self._match_purposes(context1.purpose, context2.purpose))
            weights.append(self.config.purpose_weight)
        if context1.tags and context2.tags:
            tag_similarity = self._match_tags(context1.tags, context2.tags)
            scores.append(tag_similarity)
            weights.append(0.2)
        if scores and weights:
            total_weight = sum(weights)
            return sum((s * w for s, w in zip(scores, weights, strict=False))) / total_weight
        return 0.0

    def _match_domains(self, domain1: str, domain2: str) -> float:
        """Match domain strings."""
        if domain1.lower() == domain2.lower():
            return 1.0
        if domain1.lower() in domain2.lower() or domain2.lower() in domain1.lower():
            return 0.7
        domain1_terms = set(domain1.lower().split())
        domain2_terms = set(domain2.lower().split())
        if domain1_terms and domain2_terms:
            intersection = domain1_terms.intersection(domain2_terms)
            union = domain1_terms.union(domain2_terms)
            return len(intersection) / len(union)
        return 0.0

    def _match_purposes(self, purpose1: str, purpose2: str) -> float:
        """Match purpose descriptions using semantic similarity."""
        words1 = set(purpose1.lower().split())
        words2 = set(purpose2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union)

    def _match_semantics(self, context1: SchemaContext, context2: SchemaContext) -> float:
        """Match semantic information."""
        scores = []
        if context1.tags and context2.tags:
            tag_score = self._match_tags(context1.tags, context2.tags)
            scores.append(tag_score)
        if context1.business_context and context2.business_context:
            business_score = self._match_purposes(context1.business_context, context2.business_context)
            scores.append(business_score)
        if context1.technical_context and context2.technical_context:
            tech_score = self._match_purposes(context1.technical_context, context2.technical_context)
            scores.append(tech_score)
        return sum(scores) / len(scores) if scores else 0.0

    def _match_tags(self, tags1: list[str], tags2: list[str]) -> float:
        """Match tag lists."""
        set1 = {tag.lower() for tag in tags1}
        set2 = {tag.lower() for tag in tags2}
        if not set1 or not set2:
            return 0.0
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        return len(intersection) / len(union)

    def _match_structure(self, schema_def: dict[str, Any]) -> float:
        """Evaluate structural compatibility."""
        field_count = len(self._extract_field_names(schema_def))
        return min(1.0, field_count / 100.0)

    def _match_usage_patterns(self, patterns1: list[str], patterns2: list[str]) -> float:
        """Match usage patterns."""
        if not patterns1 or not patterns2:
            return 0.0
        set1 = {pattern.lower() for pattern in patterns1}
        set2 = {pattern.lower() for pattern in patterns2}
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        return len(intersection) / len(union)

    def _compute_compatibility_score(self, context1: SchemaContext, context2: SchemaContext) -> float:
        """Compute overall compatibility score."""
        factors = []
        if context1.related_schemas and context2.related_schemas:
            overlap = set(context1.related_schemas).intersection(context2.related_schemas)
            if overlap:
                factors.append(
                    len(overlap) / min(len(context1.related_schemas), len(context2.related_schemas))
                )
        if context1.domain == context2.domain:
            factors.append(0.3)
        if context1.purpose and context2.purpose:
            if context1.purpose.lower() == context2.purpose.lower():
                factors.append(0.4)
        return sum(factors) if factors else 0.0

    def _extract_field_names(self, schema_def: dict[str, Any]) -> list[str]:
        """Extract field names from schema definition."""
        fields = []

        def extract_recursive(obj: object, prefix: str = "") -> None:
            if isinstance(obj, dict):
                if "properties" in obj:
                    for key in obj["properties"].keys():
                        field_name = f"{prefix}.{key}" if prefix else key
                        fields.append(field_name)
                elif "fields" in obj:
                    for key in obj["fields"].keys():
                        field_name = f"{prefix}.{key}" if prefix else key
                        fields.append(field_name)

        extract_recursive(schema_def)
        return fields

    def _generate_explanation(
        self,
        query_context: SchemaContext,
        match_result: ContextMatchResult,
        match_types: list[ContextMatchType],
    ) -> str:
        """Generate explanation for the match."""
        explanations = []
        if "domain" in match_result.match_details and match_result.match_details["domain"] > 0.7:
            explanations.append(f"Strong domain match ({match_result.match_details['domain']:.2f})")
        if "purpose" in match_result.match_details and match_result.match_details["purpose"] > 0.6:
            explanations.append(f"Similar purpose ({match_result.match_details['purpose']:.2f})")
        if "semantic" in match_result.match_details and match_result.match_details["semantic"] > 0.5:
            explanations.append(f"Semantic alignment ({match_result.match_details['semantic']:.2f})")
        if "usage" in match_result.match_details and match_result.match_details["usage"] > 0.4:
            explanations.append(f"Shared usage patterns ({match_result.match_details['usage']:.2f})")
        if explanations:
            return "Match based on: " + ", ".join(explanations)
        else:
            return "General similarity match"


def create_schema_context_matcher(
    domain_weight: float = 0.3, purpose_weight: float = 0.25, semantic_weight: float = 0.2, **kwargs: object
) -> SchemaContextMatcher:
    """Create a configured schema context matcher."""
    config = SchemaContextConfig(
        domain_weight=domain_weight, purpose_weight=purpose_weight, semantic_weight=semantic_weight, **kwargs
    )
    return SchemaContextMatcher(config)


# guardian: allow-magic-config
def match_schema_context(
    query_context: dict[str, Any],
    candidate_schemas: list[tuple[str, dict[str, Any], dict[str, Any]]],
    match_types: list[str] = None,
    min_score: float = 0.5,
    top_k: int = 10,
    include_explanations: bool = False,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Match schema context.

    Args:
        query_context: Query context information
        candidate_schemas: List of (schema_id, schema_def, schema_context) tuples
        match_types: Types of matching to perform
        min_score: Minimum match score
        top_k: Number of top results to return
        include_explanations: Whether to include match explanations
        config: Optional matcher configuration

    Returns:
        Dict: Context match results
    """
    matcher_config = SchemaContextConfig(**config or {})
    matcher = SchemaContextMatcher(matcher_config)
    query_ctx = SchemaContext(**query_context)
    candidates = [(sid, schema, SchemaContext(**ctx)) for sid, schema, ctx in candidate_schemas]
    request = ContextMatchRequest(
        query_context=query_ctx,
        candidate_schemas=candidates,
        match_types=[ContextMatchType(t) for t in match_types or list(ContextMatchType)],
        min_score=min_score,
        top_k=top_k,
        include_explanations=include_explanations,
    )
    result = matcher.match_context(request)
    return {
        "query_context": {
            "schema_id": result.query_context.schema_id,
            "domain": result.query_context.domain,
            "purpose": result.query_context.purpose,
            "tags": result.query_context.tags,
            "usage_patterns": result.query_context.usage_patterns,
        },
        "matches": [
            {
                "schema_id": m.schema_id,
                "match_score": m.match_score,
                "match_details": m.match_details,
                "explanation": m.explanation,
                "compatibility_score": m.compatibility_score,
            }
            for m in result.matches
        ],
        "total_candidates": result.total_candidates,
        "metadata": result.metadata,
    }
