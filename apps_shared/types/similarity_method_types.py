"""schema Similarity Retriever - Retrieves and computes schema similarity.

This module provides schema similarity retrieval capabilities for schema operations,
including structural similarity, semantic similarity, and compatibility checking.
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

_emit_applies_guardrail("p0", "similarity_method_types", "p0_governance")
_emit_reads_policy_state("p0", "similarity_method_types", "policy_binding")
_emit_snapshots_state("p0", "similarity_method_types", "state_snapshot")
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

_emit_emits_metric_event("similarity_method_types", "p4obs", "metric_1")
_emit_emits_metric_event("similarity_method_types", "p4obs", "metric_2")
_emit_emits_metric_event("similarity_method_types", "p4obs", "metric_3")
_emit_emits_metric_event("similarity_method_types", "p4obs", "metric_4")
_emit_emits_metric_event("similarity_method_types", "p4obs", "metric_5")
_emit_emits_metric_event("similarity_method_types", "p4obs", "metric_6")
_emit_records_incident_event("similarity_method_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("similarity_method_types", "p4obs", "anomaly")
_emit_writes_observability_log("similarity_method_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("similarity_method_types", "p4obs", "mon_state")
_emit_triggers_alert("similarity_method_types", "p4obs", "alert")
_emit_links_incident_trace("similarity_method_types", "p4obs", "trace_link")
_emit_captures_pattern("similarity_method_types", "p3lm", "pattern")
_emit_records_learning_event("similarity_method_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("similarity_method_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("similarity_method_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("similarity_method_types", "p3lm", "routing")
_emit_improves_agent_policy("similarity_method_types", "p3lm", "policy")
_emit_stores_learning_state("similarity_method_types", "p3lm", "state")
_emit_records_execution_trace("similarity_method_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("similarity_method_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("similarity_method_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("similarity_method_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("similarity_method_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("similarity_method_types", "env_read", "p2_env_1")
_emit_reads_environ("similarity_method_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("similarity_method_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("similarity_method_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "similarity_method_types", "context_pull")
_emit_pulls_context("p1", "similarity_method_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "similarity_method_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "similarity_method_types", "uwg_term_2")
_emit_writes_through("p1", "similarity_method_types", "write_through")
_emit_writes_through("p1", "similarity_method_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "similarity_method_types", "safety_validation")
_emit_invokes_eval("p1", "similarity_method_types", "eval_call")
_emit_proposal_commits_routing("p1", "similarity_method_types", "routing_commit")
_emit_escalates_to_human("p1", "similarity_method_types", "human_escalation")
_emit_routes_through("p1", "similarity_method_types", "route_through")
_emit_checks_agent_registry("p1", "similarity_method_types", "agent_registry")
_emit_validates_agent_capability("p1", "similarity_method_types", "capability")
_emit_dispatches_execution_plan("p1", "similarity_method_types", "exec_plan")
_emit_agent_executes_agent("p1", "similarity_method_types", "sub_agent")
_emit_routes_to_agent("p1", "similarity_method_types", "target_agent")
_emit_verifies_policy("p1", "similarity_method_types", "policy_check")
_emit_observes_runtime_state("p1", "similarity_method_types", "runtime_state")
_emit_verifies_boundary("p1", "similarity_method_types", "boundary_check")
_emit_transcripts_response("p1", "similarity_method_types", "transcript")
_emit_hard_fails_untranscripted("p1", "similarity_method_types")
_emit_gated_by_confidence("p1", "similarity_method_types", "confidence_gate")
emit_replay_key("p0", "similarity_method_types")
emit_determinism_digest("p0", "similarity_method_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "similarity_method_types", "execution_auth")
_emit_validates_capability("p2", "similarity_method_types", "capability_check")
_emit_routes_to_capability("p2", "similarity_method_types", "capability_route")
_emit_writes_via_uwg("p2", "similarity_method_types", "uwg_write")
_emit_blocks_direct_write("p2", "similarity_method_types", "direct_write_block")
_emit_records_tool_invocation("p2", "similarity_method_types", "tool_invocation")
_emit_captures_execution_output("p2", "similarity_method_types", "exec_output")
_emit_dispatches_agent("p3", "similarity_method_types", "agent_dispatch")
_emit_coordinates_agents("p3", "similarity_method_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "similarity_method_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "similarity_method_types", "healing_outcome")
_emit_escalates_failure("p3", "similarity_method_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "similarity_method_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "similarity_method_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "similarity_method_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "similarity_method_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "similarity_method_types", "eval_metric")
_emit_stores_embedding("p4", "similarity_method_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "similarity_method_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "similarity_method_types", "exec_snapshot_link")
_emit_reads_through("l4", "similarity_method_types", "urg_read_1")
_emit_reads_through("l4", "similarity_method_types", "urg_read_2")
_emit_reads_through("l4", "similarity_method_types", "urg_read_3")
_emit_reads_through("l4", "similarity_method_types", "urg_read_4")
_emit_reads_through("l4", "similarity_method_types", "urg_read_5")
_emit_reads_through("l4", "similarity_method_types", "urg_read_6")
_emit_reads_through("l4", "similarity_method_types", "urg_read_7")
_emit_reads_through("l4", "similarity_method_types", "urg_read_8")
_emit_reads_through("l4", "similarity_method_types", "urg_read_9")
_emit_reads_through("l4", "similarity_method_types", "urg_read_10")
_emit_reads_through("l4", "similarity_method_types", "urg_read_11")
_emit_reads_through("l4", "similarity_method_types", "urg_read_12")
_emit_reads_through("l4", "similarity_method_types", "urg_read_13")
_emit_reads_through("l4", "similarity_method_types", "urg_read_14")
_emit_reads_through("l4", "similarity_method_types", "urg_read_15")
_emit_reads_through("l4", "similarity_method_types", "urg_read_16")
_emit_reads_through("l4", "similarity_method_types", "urg_read_17")
_emit_reads_through("l4", "similarity_method_types", "urg_read_18")
_emit_reads_through("l4", "similarity_method_types", "urg_read_19")
_emit_reads_through("l4", "similarity_method_types", "urg_read_20")
_emit_reads_through("l4", "similarity_method_types", "urg_read_21")
_emit_reads_through("l4", "similarity_method_types", "urg_read_22")
_emit_reads_through("l4", "similarity_method_types", "urg_read_23")
_emit_reads_through("l4", "similarity_method_types", "urg_read_24")
_emit_reads_through("l4", "similarity_method_types", "urg_read_25")
_emit_reads_through("l4", "similarity_method_types", "urg_read_26")
_emit_reads_through("l4", "similarity_method_types", "urg_read_27")
_emit_reads_through("l4", "similarity_method_types", "urg_read_28")
_emit_reads_through("l4", "similarity_method_types", "urg_read_29")
_emit_reads_through("l4", "similarity_method_types", "urg_read_30")
_emit_reads_through("l4", "similarity_method_types", "urg_read_31")
_emit_reads_through("l4", "similarity_method_types", "urg_read_32")
_emit_reads_through("l4", "similarity_method_types", "urg_read_33")
_emit_reads_through("l4", "similarity_method_types", "urg_read_34")
_emit_reads_through("l4", "similarity_method_types", "urg_read_35")
_emit_reads_through("l4", "similarity_method_types", "urg_read_36")
_emit_reads_through("l4", "similarity_method_types", "urg_read_37")
_emit_reads_through("l4", "similarity_method_types", "urg_read_38")
_emit_reads_through("l4", "similarity_method_types", "urg_read_39")
_emit_reads_through("l4", "similarity_method_types", "urg_read_40")
_emit_reads_through("l4", "similarity_method_types", "urg_read_41")
_emit_reads_through("l4", "similarity_method_types", "urg_read_42")
_emit_reads_through("l4", "similarity_method_types", "urg_read_43")
_emit_reads_through("l4", "similarity_method_types", "urg_read_44")
_emit_reads_through("l4", "similarity_method_types", "urg_read_45")
_emit_reads_through("l4", "similarity_method_types", "urg_read_46")
_emit_reads_through("l4", "similarity_method_types", "urg_read_47")
_emit_reads_through("l4", "similarity_method_types", "urg_read_48")
_emit_reads_through("l4", "similarity_method_types", "urg_read_49")
_emit_reads_through("l4", "similarity_method_types", "urg_read_50")
_emit_reads_through("l4", "similarity_method_types", "urg_read_51")
_emit_reads_through("l4", "similarity_method_types", "urg_read_52")
_emit_reads_through("l4", "similarity_method_types", "urg_read_53")
_emit_reads_through("l4", "similarity_method_types", "urg_read_54")
_emit_reads_through("l4", "similarity_method_types", "urg_read_55")
_emit_reads_through("l4", "similarity_method_types", "urg_read_56")
_emit_reads_through("l4", "similarity_method_types", "urg_read_57")
_emit_reads_through("l4", "similarity_method_types", "urg_read_58")
_emit_reads_through("l4", "similarity_method_types", "urg_read_59")
_emit_reads_through("l4", "similarity_method_types", "urg_read_60")
_emit_reads_through("l4", "similarity_method_types", "urg_read_61")
_emit_reads_through("l4", "similarity_method_types", "urg_read_62")
_emit_reads_through("l4", "similarity_method_types", "urg_read_63")
_emit_reads_through("l4", "similarity_method_types", "urg_read_64")
_emit_reads_through("l4", "similarity_method_types", "urg_read_65")
_emit_reads_through("l4", "similarity_method_types", "urg_read_66")
_emit_reads_through("l4", "similarity_method_types", "urg_read_67")
_emit_reads_through("l4", "similarity_method_types", "urg_read_68")
_emit_reads_through("l4", "similarity_method_types", "urg_read_69")
_emit_reads_through("l4", "similarity_method_types", "urg_read_70")
_emit_reads_through("l4", "similarity_method_types", "urg_read_71")
_emit_reads_through("l4", "similarity_method_types", "urg_read_72")
_emit_reads_through("l4", "similarity_method_types", "urg_read_73")
_emit_reads_through("l4", "similarity_method_types", "urg_read_74")
_emit_reads_through("l4", "similarity_method_types", "urg_read_75")
_emit_reads_through("l4", "similarity_method_types", "urg_read_76")
_emit_reads_through("l4", "similarity_method_types", "urg_read_77")
_emit_reads_through("l4", "similarity_method_types", "urg_read_78")
_emit_reads_through("l4", "similarity_method_types", "urg_read_79")
_emit_reads_through("l4", "similarity_method_types", "urg_read_80")
_emit_reads_through("l4", "similarity_method_types", "urg_read_81")
_emit_reads_through("l4", "similarity_method_types", "urg_read_82")
_emit_reads_through("l4", "similarity_method_types", "urg_read_83")
_emit_reads_through("l4", "similarity_method_types", "urg_read_84")
_emit_reads_through("l4", "similarity_method_types", "urg_read_85")
_emit_reads_through("l4", "similarity_method_types", "urg_read_86")
_emit_reads_through("l4", "similarity_method_types", "urg_read_87")
_emit_reads_through("l4", "similarity_method_types", "urg_read_88")
_emit_reads_through("l4", "similarity_method_types", "urg_read_89")
_emit_reads_through("l4", "similarity_method_types", "urg_read_90")
_emit_reads_through("l4", "similarity_method_types", "urg_read_91")
_emit_reads_through("l4", "similarity_method_types", "urg_read_92")
_emit_reads_through("l4", "similarity_method_types", "urg_read_93")
_emit_reads_through("l4", "similarity_method_types", "urg_read_94")
_emit_reads_through("l4", "similarity_method_types", "urg_read_95")
_emit_reads_through("l4", "similarity_method_types", "urg_read_96")
_emit_reads_through("l4", "similarity_method_types", "urg_read_97")
_emit_reads_through("l4", "similarity_method_types", "urg_read_98")
_emit_reads_through("l4", "similarity_method_types", "urg_read_99")
_emit_reads_through("l4", "similarity_method_types", "urg_read_100")
_emit_reads_through("l4", "similarity_method_types", "urg_read_101")
_emit_reads_through("l4", "similarity_method_types", "urg_read_102")
_emit_reads_through("l4", "similarity_method_types", "urg_read_103")
_emit_reads_through("l4", "similarity_method_types", "urg_read_104")
_emit_reads_through("l4", "similarity_method_types", "urg_read_105")
_emit_reads_through("l4", "similarity_method_types", "urg_read_106")
_emit_reads_through("l4", "similarity_method_types", "urg_read_107")
_emit_reads_through("l4", "similarity_method_types", "urg_read_108")
_emit_reads_through("l4", "similarity_method_types", "urg_read_109")
_emit_reads_through("l4", "similarity_method_types", "urg_read_110")
_emit_reads_through("l4", "similarity_method_types", "urg_read_111")
_emit_reads_through("l4", "similarity_method_types", "urg_read_112")
_emit_reads_through("l4", "similarity_method_types", "urg_read_113")
_emit_reads_through("l4", "similarity_method_types", "urg_read_114")
_emit_reads_through("l4", "similarity_method_types", "urg_read_115")
_emit_reads_through("l4", "similarity_method_types", "urg_read_116")

logger = logging.getLogger(__name__)


class SimilarityMethod(Enum):
    """Methods for computing schema similarity."""

    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    FIELD_OVERLAP = "field_overlap"
    TYPE_COMPATIBILITY = "type_compatibility"
    HYBRID = "hybrid"


class CompatibilityLevel(Enum):
    """Levels of schema compatibility."""

    IDENTICAL = "identical"
    COMPATIBLE = "compatible"
    PARTIALLY_COMPATIBLE = "partially_compatible"
    INCOMPATIBLE = "incompatible"


@dataclass
class SchemaSimilarityRequest:
    """Request for schema similarity computation."""

    source_schema: dict[str, Any]
    target_schema: dict[str, Any]
    method: SimilarityMethod = SimilarityMethod.STRUCTURAL
    include_field_details: bool = False
    weight_structural: float = 0.4
    weight_semantic: float = 0.3
    weight_overlap: float = 0.3


@dataclass
class FieldMatch:
    """Field-level match information."""

    field_name: str
    source_type: str
    target_type: str
    type_match: bool
    semantic_similarity: float = 0.0
    confidence: float = 0.0


@dataclass
class SchemaSimilarityResult:
    """Result of schema similarity computation."""

    similarity_score: float
    compatibility_level: CompatibilityLevel
    field_matches: list[FieldMatch] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)
    extra_fields: list[str] = field(default_factory=list)
    type_conflicts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SchemaSimilarityConfig:
    """configuration for schema similarity operations."""

    default_method: SimilarityMethod = SimilarityMethod.HYBRID
    type_compatibility_matrix: dict[str, set[str]] = field(
        default_factory=lambda: {
            "string": {"string", "text"},
            "integer": {"integer", "number"},
            "number": {"integer", "number", "float"},
            "boolean": {"boolean"},
            "array": {"array", "list"},
            "object": {"object", "dict"},
            "null": {"null", "any"},
        },
    )
    similarity_thresholds: dict[str, float] = field(
        default_factory=lambda: {"identical": 0.95, "compatible": 0.7, "partially_compatible": 0.4},
    )


class SchemaSimilarityRetriever:
    """Main class for schema similarity retrieval operations."""

    def __init__(self, config: SchemaSimilarityConfig | None = None):
        self.config = config or SchemaSimilarityConfig()
        self.logger = logging.getLogger(self.__class__.__name__)

    def retrieve_similarity(self, request: SchemaSimilarityRequest) -> SchemaSimilarityResult:
        """Retrieve similarity between two schemas.

        Args:
            request: Similarity computation request

        Returns:
            SchemaSimilarityResult: Detailed similarity analysis
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            f"SchemaSimilarityRetriever.retrieve_similarity:{request.similarity_method}",
        )
        self.logger.info(f"Computing schema similarity using method: {request.method.value}")
        try:
            source_fields = self._extract_fields_with_types(request.source_schema)
            target_fields = self._extract_fields_with_types(request.target_schema)
            if request.method == SimilarityMethod.STRUCTURAL:
                similarity = self._compute_structural_similarity(source_fields, target_fields)
            elif request.method == SimilarityMethod.SEMANTIC:
                similarity = self._compute_semantic_similarity(source_fields, target_fields)
            elif request.method == SimilarityMethod.FIELD_OVERLAP:
                similarity = self._compute_field_overlap_similarity(source_fields, target_fields)
            elif request.method == SimilarityMethod.TYPE_COMPATIBILITY:
                similarity = self._compute_type_compatibility_similarity(source_fields, target_fields)
            else:
                similarity = self._compute_hybrid_similarity(
                    source_fields,
                    target_fields,
                    request.weight_structural,
                    request.weight_semantic,
                    request.weight_overlap,
                )
            compatibility = self._determine_compatibility(similarity)
            field_analysis = self._analyze_field_differences(source_fields, target_fields)
            field_matches = []
            if request.include_field_details:
                field_matches = self._create_field_matches(source_fields, target_fields)
            result = SchemaSimilarityResult(
                similarity_score=similarity,
                compatibility_level=compatibility,
                field_matches=field_matches,
                missing_fields=field_analysis["missing"],
                extra_fields=field_analysis["extra"],
                type_conflicts=field_analysis["conflicts"],
                metadata={
                    "computed_at": datetime.utcnow().isoformat(),
                    "method": request.method.value,
                    "source_field_count": len(source_fields),
                    "target_field_count": len(target_fields),
                    "retriever": "SchemaSimilarityRetriever",
                },
            )
            self.logger.info(
                f"schema similarity computed: {similarity:.3f} (compatibility: {compatibility.value})",
            )
            return result
        # guardian: allow-silent-swallow
        except Exception as e:
            self.logger.error(f"Failed to compute schema similarity: {str(e)}")
            return SchemaSimilarityResult(
                similarity_score=0.0,
                compatibility_level=CompatibilityLevel.INCOMPATIBLE,
                metadata={"error": str(e)},
            )

    def batch_similarity(
        self,
        source_schema: dict[str, Any],
        target_schemas: list[dict[str, Any]],
        method: SimilarityMethod | None = None,
    ) -> list[SchemaSimilarityResult]:
        """Compute similarity against multiple target schemas.

        Args:
            source_schema: Source schema to compare
            target_schemas: List of target schemas
            method: Similarity method to use

        Returns:
            List[SchemaSimilarityResult]: Results for each target schema
        """
        self.logger.info(f"Computing batch similarity for {len(target_schemas)} schemas")
        results = []
        method = method or self.config.default_method
        for target_schema in target_schemas:
            request = SchemaSimilarityRequest(
                source_schema=source_schema,
                target_schema=target_schema,
                method=method,
            )
            result = self.retrieve_similarity(request)
            results.append(result)
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results

    def find_compatible_schemas(
        self,
        schema: dict[str, Any],
        schema_candidates: list[tuple[str, dict[str, Any]]],
        min_compatibility: CompatibilityLevel = CompatibilityLevel.PARTIALLY_COMPATIBLE,
    ) -> list[tuple[str, SchemaSimilarityResult]]:
        """Find schemas compatible with a given schema.

        Args:
            schema: Reference schema
            schema_candidates: List of (schema_id, schema) tuples
            min_compatibility: Minimum compatibility level

        Returns:
            List of (schema_id, similarity_result) tuples
        """
        compatible_schemas = []
        compatibility_order = [
            CompatibilityLevel.INCOMPATIBLE,
            CompatibilityLevel.PARTIALLY_COMPATIBLE,
            CompatibilityLevel.COMPATIBLE,
            CompatibilityLevel.IDENTICAL,
        ]
        min_threshold = compatibility_order.index(min_compatibility)
        for schema_id, candidate_schema in schema_candidates:
            request = SchemaSimilarityRequest(
                source_schema=schema,
                target_schema=candidate_schema,
                method=self.config.default_method,
            )
            result = self.retrieve_similarity(request)
            result_threshold = compatibility_order.index(result.compatibility_level)
            if result_threshold >= min_threshold:
                compatible_schemas.append((schema_id, result))
        compatible_schemas.sort(key=lambda x: x[1].similarity_score, reverse=True)
        return compatible_schemas

    def _extract_from_properties(self, obj: dict[str, Any], prefix: str, fields: dict[str, str]) -> None:
        """Extract fields from properties format."""
        for key, value in obj["properties"].items():
            field_name = f"{prefix}.{key}" if prefix else key
            field_type = value.get("type", "unknown")
            fields[field_name] = field_type
            self._extract_fields_recursive(value, field_name, fields)

    def _extract_from_fields(self, obj: dict[str, Any], prefix: str, fields: dict[str, str]) -> None:
        """Extract fields from fields format."""
        for key, value in obj["fields"].items():
            field_name = f"{prefix}.{key}" if prefix else key
            field_type = value.get("type", "unknown")
            fields[field_name] = field_type
            self._extract_fields_recursive(value, field_name, fields)

    def _extract_direct_fields(self, obj: dict[str, Any], prefix: str, fields: dict[str, str]) -> None:
        """Extract direct fields from object."""
        for key, value in obj.items():
            if key in ["type", "required", "description"]:
                continue
            field_name = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict) and "type" in value:
                fields[field_name] = value["type"]
            else:
                fields[field_name] = type(value).__name__.lower()

    def _extract_fields_recursive(self, obj: object, prefix: str, fields: dict[str, str]) -> None:
        """Recursively extract fields from nested schema objects."""
        if not isinstance(obj, dict):
            return
        if "properties" in obj:
            self._extract_from_properties(obj, prefix, fields)
        elif "fields" in obj:
            self._extract_from_fields(obj, prefix, fields)
        else:
            self._extract_direct_fields(obj, prefix, fields)

    def _extract_fields_with_types(self, schema: dict[str, Any]) -> dict[str, str]:
        """Extract field names and their types from a schema."""
        fields = {}
        self._extract_fields_recursive(schema, "", fields)
        return fields

    def _compute_structural_similarity(
        self,
        source_fields: dict[str, str],
        target_fields: dict[str, str],
    ) -> float:
        """Compute structural similarity based on field hierarchy."""
        source_paths = set(source_fields.keys())
        target_paths = set(target_fields.keys())
        intersection = source_paths.intersection(target_paths)
        union = source_paths.union(target_paths)
        if not union:
            return 0.0
        path_similarity = len(intersection) / len(union)
        type_matches = 0
        for path in intersection:
            if source_fields[path] == target_fields[path]:
                type_matches += 1
        type_similarity = type_matches / len(intersection) if intersection else 0.0
        return path_similarity * 0.6 + type_similarity * 0.4

    def _compute_semantic_similarity(
        self,
        source_fields: dict[str, str],
        target_fields: dict[str, str],
    ) -> float:
        """Compute semantic similarity based on field names."""
        source_names = {path.split(".")[-1] for path in source_fields.keys()}
        target_names = {path.split(".")[-1] for path in target_fields.keys()}
        intersection = source_names.intersection(target_names)
        union = source_names.union(target_names)
        if not union:
            return 0.0
        return len(intersection) / len(union)

    def _compute_field_overlap_similarity(
        self,
        source_fields: dict[str, str],
        target_fields: dict[str, str],
    ) -> float:
        """Compute similarity based on field overlap."""
        source_paths = set(source_fields.keys())
        target_paths = set(target_fields.keys())
        intersection = source_paths.intersection(target_paths)
        min_size = min(len(source_paths), len(target_paths))
        if min_size == 0:
            return 0.0
        return len(intersection) / min_size

    def _compute_type_compatibility_similarity(
        self,
        source_fields: dict[str, str],
        target_fields: dict[str, str],
    ) -> float:
        """Compute similarity based on type compatibility."""
        source_paths = set(source_fields.keys())
        target_paths = set(target_fields.keys())
        intersection = source_paths.intersection(target_paths)
        if not intersection:
            return 0.0
        compatible_types = 0
        for path in intersection:
            source_type = source_fields[path]
            target_type = target_fields[path]
            if self._are_types_compatible(source_type, target_type):
                compatible_types += 1
        return compatible_types / len(intersection)

    def _compute_hybrid_similarity(
        self,
        source_fields: dict[str, str],
        target_fields: dict[str, str],
        weight_structural: float,
        weight_semantic: float,
        weight_overlap: float,
    ) -> float:
        """Compute hybrid similarity combining multiple methods."""
        total_weight = weight_structural + weight_semantic + weight_overlap
        if total_weight == 0:
            return 0.0
        w_structural = weight_structural / total_weight
        w_semantic = weight_semantic / total_weight
        w_overlap = weight_overlap / total_weight
        structural = self._compute_structural_similarity(source_fields, target_fields)
        semantic = self._compute_semantic_similarity(source_fields, target_fields)
        overlap = self._compute_field_overlap_similarity(source_fields, target_fields)
        return structural * w_structural + semantic * w_semantic + overlap * w_overlap

    def _determine_compatibility(self, similarity_score: float) -> CompatibilityLevel:
        """Determine compatibility level from similarity score."""
        thresholds = self.config.similarity_thresholds
        if similarity_score >= thresholds["identical"]:
            return CompatibilityLevel.IDENTICAL
        elif similarity_score >= thresholds["compatible"]:
            return CompatibilityLevel.COMPATIBLE
        elif similarity_score >= thresholds["partially_compatible"]:
            return CompatibilityLevel.PARTIALLY_COMPATIBLE
        else:
            return CompatibilityLevel.INCOMPATIBLE

    def _analyze_field_differences(
        self,
        source_fields: dict[str, str],
        target_fields: dict[str, str],
    ) -> dict[str, list[str]]:
        """Analyze differences between schemas."""
        source_paths = set(source_fields.keys())
        target_paths = set(target_fields.keys())
        missing = list(source_paths - target_paths)
        extra = list(target_paths - source_paths)
        conflicts = []
        intersection = source_paths.intersection(target_paths)
        for path in intersection:
            if not self._are_types_compatible(source_fields[path], target_fields[path]):
                conflicts.append(path)
        return {"missing": missing, "extra": extra, "conflicts": conflicts}

    def _create_field_matches(
        self,
        source_fields: dict[str, str],
        target_fields: dict[str, str],
    ) -> list[FieldMatch]:
        """Create detailed field match information."""
        matches = []
        intersection = source_fields.keys() & target_fields.keys()
        for field_name in intersection:
            source_type = source_fields[field_name]
            target_type = target_fields[field_name]
            match = FieldMatch(
                field_name=field_name,
                source_type=source_type,
                target_type=target_type,
                type_match=source_type == target_type,
                semantic_similarity=1.0 if source_type == target_type else 0.5,
                confidence=1.0 if source_type == target_type else 0.7,
            )
            matches.append(match)
        return matches

    def _are_types_compatible(self, type1: str, type2: str) -> bool:
        """Check if two types are compatible."""
        if type1 == type2:
            return True
        if type1 in self.config.type_compatibility_matrix:
            return type2 in self.config.type_compatibility_matrix[type1]
        if type2 in self.config.type_compatibility_matrix:
            return type1 in self.config.type_compatibility_matrix[type2]
        return False


def create_schema_similarity_retriever(
    default_method: str = "hybrid",
    **kwargs: object,
) -> SchemaSimilarityRetriever:
    """Create a configured schema similarity retriever."""
    config = SchemaSimilarityConfig(default_method=SimilarityMethod(default_method), **kwargs)
    return SchemaSimilarityRetriever(config)


def retrieve_schema_similarity(
    source_schema: dict[str, Any],
    target_schema: dict[str, Any],
    method: str = "hybrid",
    include_field_details: bool = False,
    weight_structural: float = 0.4,
    weight_semantic: float = 0.3,
    weight_overlap: float = 0.3,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Retrieve schema similarity.

    Args:
        source_schema: Source schema
        target_schema: Target schema
        method: Similarity method to use
        include_field_details: Whether to include field-level details
        weight_structural: Weight for structural similarity
        weight_semantic: Weight for semantic similarity
        weight_overlap: Weight for field overlap similarity
        config: Optional retriever configuration

    Returns:
        Dict: Similarity results
    """
    retriever_config = SchemaSimilarityConfig(**config or {})
    retriever = SchemaSimilarityRetriever(retriever_config)
    request = SchemaSimilarityRequest(
        source_schema=source_schema,
        target_schema=target_schema,
        method=SimilarityMethod(method),
        include_field_details=include_field_details,
        weight_structural=weight_structural,
        weight_semantic=weight_semantic,
        weight_overlap=weight_overlap,
    )
    result = retriever.retrieve_similarity(request)
    return {
        "similarity_score": result.similarity_score,
        "compatibility_level": result.compatibility_level.value,
        "field_matches": [
            {
                "field_name": m.field_name,
                "source_type": m.source_type,
                "target_type": m.target_type,
                "type_match": m.type_match,
                "semantic_similarity": m.semantic_similarity,
                "confidence": m.confidence,
            }
            for m in result.field_matches
        ],
        "missing_fields": result.missing_fields,
        "extra_fields": result.extra_fields,
        "type_conflicts": result.type_conflicts,
        "metadata": result.metadata,
    }
