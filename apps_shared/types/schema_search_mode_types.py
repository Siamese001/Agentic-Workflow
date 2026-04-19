"""schema Vector Searcher - Search operations for schema vectors.

This module provides vector search capabilities for schema operations,
including semantic search, similarity matching, and schema-aware retrieval.
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

_emit_applies_guardrail("p0", "schema_search_mode_types", "p0_governance")
_emit_reads_policy_state("p0", "schema_search_mode_types", "policy_binding")
_emit_snapshots_state("p0", "schema_search_mode_types", "state_snapshot")
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
from tqdm import tqdm

_emit_emits_metric_event("schema_search_mode_types", "p4obs", "metric_1")
_emit_emits_metric_event("schema_search_mode_types", "p4obs", "metric_2")
_emit_emits_metric_event("schema_search_mode_types", "p4obs", "metric_3")
_emit_emits_metric_event("schema_search_mode_types", "p4obs", "metric_4")
_emit_emits_metric_event("schema_search_mode_types", "p4obs", "metric_5")
_emit_emits_metric_event("schema_search_mode_types", "p4obs", "metric_6")
_emit_records_incident_event("schema_search_mode_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("schema_search_mode_types", "p4obs", "anomaly")
_emit_writes_observability_log("schema_search_mode_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("schema_search_mode_types", "p4obs", "mon_state")
_emit_triggers_alert("schema_search_mode_types", "p4obs", "alert")
_emit_links_incident_trace("schema_search_mode_types", "p4obs", "trace_link")
_emit_captures_pattern("schema_search_mode_types", "p3lm", "pattern")
_emit_records_learning_event("schema_search_mode_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("schema_search_mode_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("schema_search_mode_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("schema_search_mode_types", "p3lm", "routing")
_emit_improves_agent_policy("schema_search_mode_types", "p3lm", "policy")
_emit_stores_learning_state("schema_search_mode_types", "p3lm", "state")
_emit_records_execution_trace("schema_search_mode_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("schema_search_mode_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("schema_search_mode_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("schema_search_mode_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("schema_search_mode_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("schema_search_mode_types", "env_read", "p2_env_1")
_emit_reads_environ("schema_search_mode_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("schema_search_mode_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("schema_search_mode_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "schema_search_mode_types", "context_pull")
_emit_pulls_context("p1", "schema_search_mode_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "schema_search_mode_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "schema_search_mode_types", "uwg_term_2")
_emit_writes_through("p1", "schema_search_mode_types", "write_through")
_emit_writes_through("p1", "schema_search_mode_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "schema_search_mode_types", "safety_validation")
_emit_invokes_eval("p1", "schema_search_mode_types", "eval_call")
_emit_proposal_commits_routing("p1", "schema_search_mode_types", "routing_commit")
_emit_escalates_to_human("p1", "schema_search_mode_types", "human_escalation")
_emit_routes_through("p1", "schema_search_mode_types", "route_through")
_emit_checks_agent_registry("p1", "schema_search_mode_types", "agent_registry")
_emit_validates_agent_capability("p1", "schema_search_mode_types", "capability")
_emit_dispatches_execution_plan("p1", "schema_search_mode_types", "exec_plan")
_emit_agent_executes_agent("p1", "schema_search_mode_types", "sub_agent")
_emit_routes_to_agent("p1", "schema_search_mode_types", "target_agent")
_emit_verifies_policy("p1", "schema_search_mode_types", "policy_check")
_emit_observes_runtime_state("p1", "schema_search_mode_types", "runtime_state")
_emit_verifies_boundary("p1", "schema_search_mode_types", "boundary_check")
_emit_transcripts_response("p1", "schema_search_mode_types", "transcript")
_emit_hard_fails_untranscripted("p1", "schema_search_mode_types")
_emit_gated_by_confidence("p1", "schema_search_mode_types", "confidence_gate")
emit_replay_key("p0", "schema_search_mode_types")
emit_determinism_digest("p0", "schema_search_mode_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "schema_search_mode_types", "execution_auth")
_emit_validates_capability("p2", "schema_search_mode_types", "capability_check")
_emit_routes_to_capability("p2", "schema_search_mode_types", "capability_route")
_emit_writes_via_uwg("p2", "schema_search_mode_types", "uwg_write")
_emit_blocks_direct_write("p2", "schema_search_mode_types", "direct_write_block")
_emit_records_tool_invocation("p2", "schema_search_mode_types", "tool_invocation")
_emit_captures_execution_output("p2", "schema_search_mode_types", "exec_output")
_emit_dispatches_agent("p3", "schema_search_mode_types", "agent_dispatch")
_emit_coordinates_agents("p3", "schema_search_mode_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "schema_search_mode_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "schema_search_mode_types", "healing_outcome")
_emit_escalates_failure("p3", "schema_search_mode_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "schema_search_mode_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "schema_search_mode_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "schema_search_mode_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "schema_search_mode_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "schema_search_mode_types", "eval_metric")
_emit_stores_embedding("p4", "schema_search_mode_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "schema_search_mode_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "schema_search_mode_types", "exec_snapshot_link")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_1")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_2")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_3")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_4")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_5")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_6")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_7")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_8")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_9")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_10")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_11")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_12")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_13")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_14")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_15")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_16")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_17")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_18")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_19")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_20")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_21")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_22")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_23")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_24")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_25")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_26")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_27")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_28")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_29")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_30")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_31")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_32")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_33")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_34")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_35")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_36")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_37")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_38")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_39")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_40")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_41")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_42")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_43")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_44")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_45")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_46")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_47")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_48")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_49")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_50")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_51")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_52")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_53")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_54")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_55")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_56")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_57")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_58")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_59")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_60")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_61")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_62")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_63")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_64")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_65")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_66")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_67")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_68")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_69")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_70")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_71")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_72")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_73")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_74")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_75")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_76")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_77")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_78")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_79")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_80")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_81")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_82")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_83")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_84")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_85")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_86")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_87")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_88")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_89")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_90")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_91")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_92")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_93")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_94")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_95")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_96")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_97")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_98")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_99")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_100")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_101")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_102")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_103")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_104")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_105")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_106")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_107")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_108")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_109")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_110")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_111")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_112")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_113")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_114")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_115")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_116")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_117")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_118")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_119")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_120")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_121")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_122")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_123")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_124")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_125")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_126")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_127")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_128")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_129")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_130")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_131")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_132")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_133")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_134")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_135")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_136")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_137")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_138")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_139")
_emit_reads_through("l4", "schema_search_mode_types", "urg_read_140")

logger = logging.getLogger(__name__)


class SchemaSearchMode(Enum):
    """Search modes for schema vector operations."""

    SEMANTIC = "semantic"
    STRUCTURAL = "structural"
    HYBRID = "hybrid"
    FIELD_BASED = "field_based"


class SchemaSimilarityType(Enum):
    """Types of schema similarity."""

    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    FIELD_OVERLAP = "field_overlap"
    TYPE_COMPATIBILITY = "type_compatibility"


@dataclass
class SchemaVectorEntry:
    """Entry in the schema vector store."""

    schema_id: str
    schema_name: str
    vector: list[float]
    field_vectors: dict[str, list[float]] = field(default_factory=dict)
    schema_type: str = "json"
    field_count: int = 0
    complexity_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SchemaSearchQuery:
    """Search query for schema vectors."""

    query_text: str | None = None
    query_schema: dict[str, Any] | None = None
    query_vector: list[float] | None = None
    search_mode: SchemaSearchMode = SchemaSearchMode.SEMANTIC
    similarity_type: SchemaSimilarityType = SchemaSimilarityType.SEMANTIC
    top_k: int = 10
    threshold: float = 0.7
    schema_type_filter: str | None = None
    min_field_overlap: int = 0
    include_field_matches: bool = False


@dataclass
class SchemaSearchResult:
    """Result of schema vector search."""

    entries: list[SchemaVectorEntry]
    scores: list[float]
    field_matches: list[dict[str, Any]] | None = None
    search_time_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SchemaVectorConfig:
    """configuration for schema vector operations."""

    dimension: int = 1536
    enable_field_vectors: bool = True
    similarity_threshold: float = 0.7
    max_entries: int = 10000
    index_type: str = "hnsw"


class SchemaVectorSearcher:
    """Main class for schema vector search operations."""

    def __init__(self, config: SchemaVectorConfig | None = None):
        self.config = config or SchemaVectorConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._schema_vectors: dict[str, SchemaVectorEntry] = {}
        self._vector_index: dict[str, np.ndarray] = {}
        self._field_index: dict[str, dict[str, np.ndarray]] = {}

    def search_schema_vectors(self, query: SchemaSearchQuery) -> SchemaSearchResult:
        """Search schema vectors based on query.

        Args:
            query: schema search query configuration

        Returns:
            SchemaSearchResult: Search results with similarity scores
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            f"SchemaVectorSearchEngine.search_schema_vectors:{query.search_mode}",
        )
        self.logger.info(f"Searching schema vectors with mode: {query.search_mode.value}")
        start_time = datetime.utcnow()
        try:
            if query.query_vector is None:
                query.query_vector = self._generate_query_vector(query)
            filtered_entries = self._filter_entries(query)
            if query.search_mode == SchemaSearchMode.SEMANTIC:
                results, scores = self._semantic_search(query, filtered_entries)
            elif query.search_mode == SchemaSearchMode.STRUCTURAL:
                results, scores = self._structural_search(query, filtered_entries)
            elif query.search_mode == SchemaSearchMode.HYBRID:
                results, scores = self._hybrid_search(query, filtered_entries)
            else:
                results, scores, field_matches = self._field_based_search(query, filtered_entries)
            search_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            search_result = SchemaSearchResult(
                entries=results,
                scores=scores,
                field_matches=field_matches if query.search_mode == SchemaSearchMode.FIELD_BASED else None,
                search_time_ms=search_time,
                metadata={
                    "searched_at": datetime.utcnow().isoformat(),
                    "search_mode": query.search_mode.value,
                    "similarity_type": query.similarity_type.value,
                    "total_schemas": len(self._schema_vectors),
                },
            )
            self.logger.info(f"schema vector search completed: {len(results)} results in {search_time:.2f}ms")
            return search_result
        # guardian: allow-silent-swallow
        except (TypeError, ValueError, KeyError, AttributeError, RuntimeError, OSError) as e:
            self.logger.error(f"schema vector search failed: {str(e)}")
            return SchemaSearchResult(
                entries=[],
                scores=[],
                search_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                metadata={"error": str(e)},
            )

    def add_schema_vector(
        self,
        schema_id: str,
        schema_name: str,
        schema: dict[str, Any],
        vector: list[float] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Add a schema vector to the store.

        Args:
            schema_id: Unique schema identifier
            schema_name: Name of the schema
            schema: schema definition
            vector: Pre-computed vector (optional)
            metadata: Additional metadata

        Returns:
            bool: True if added successfully
        """
        try:
            if vector is None:
                vector = self._generate_schema_vector(schema)
            field_vectors = {}
            if self.config.enable_field_vectors:
                field_vectors = self._generate_field_vectors(schema)
            complexity = self._calculate_complexity(schema)
            entry = SchemaVectorEntry(
                schema_id=schema_id,
                schema_name=schema_name,
                vector=vector,
                field_vectors=field_vectors,
                schema_type=metadata.get("schema_type", "json") if metadata else "json",
                field_count=len(self._extract_fields(schema)),
                complexity_score=complexity,
                metadata=metadata or {},
            )
            self._schema_vectors[schema_id] = entry
            self._vector_index[schema_id] = np.array(vector)
            if field_vectors:
                self._field_index[schema_id] = {field: np.array(vec) for field, vec in field_vectors.items()}
            self.logger.debug(f"Added schema vector: {schema_id}")
            return True
        # guardian: allow-silent-swallow
        except (TypeError, ValueError, KeyError, AttributeError, RuntimeError, OSError) as e:
            self.logger.error(f"Failed to add schema vector: {str(e)}")
            return False

    # guardian: allow-magic-config
    def find_similar_schemas(self, schema_id: str, top_k: int = 10) -> list[tuple[str, float]]:
        """Find schemas similar to a given schema.

        Args:
            schema_id: ID of reference schema
            top_k: Number of similar schemas to return

        Returns:
            List of (schema_id, similarity_score) tuples
        """
        if schema_id not in self._schema_vectors:
            return []
        reference_entry = self._schema_vectors[schema_id]
        query = SchemaSearchQuery(
            query_vector=reference_entry.vector,
            search_mode=SchemaSearchMode.SEMANTIC,
            top_k=top_k,
        )
        results, scores = self._semantic_search(query, list(self._schema_vectors.values()))
        similar_schemas = [
            (entry.schema_id, score)
            for entry, score in zip(results, scores, strict=False)
            if entry.schema_id != schema_id
        ]
        return similar_schemas[:top_k]

    def get_schema_statistics(self) -> dict[str, Any]:
        """Get statistics about the schema vector store.

        Returns:
            Dict: Store statistics
        """
        if not self._schema_vectors:
            return {"total_schemas": 0}
        total_schemas = len(self._schema_vectors)
        schema_types = {}
        complexities = []
        field_counts = []
        for entry in self._schema_vectors.values():
            schema_type = entry.schema_type
            schema_types[schema_type] = schema_types.get(schema_type, 0) + 1
            complexities.append(entry.complexity_score)
            field_counts.append(entry.field_count)
        return {
            "total_schemas": total_schemas,
            "schema_types": schema_types,
            "average_complexity": sum(complexities) / len(complexities) if complexities else 0,
            "max_complexity": max(complexities) if complexities else 0,
            "average_field_count": sum(field_counts) / len(field_counts) if field_counts else 0,
            "max_field_count": max(field_counts) if field_counts else 0,
            "has_field_vectors": len(self._field_index),
        }

    def _generate_query_vector(self, query: SchemaSearchQuery) -> list[float]:
        """Generate query vector from search criteria."""
        if query.query_text:
            return self._text_to_vector(query.query_text)
        elif query.query_schema:
            return self._generate_schema_vector(query.query_schema)
        else:
            return [0.0] * self.config.dimension

    def _generate_schema_vector(self, schema: dict[str, Any]) -> list[float]:
        """Generate vector representation of a schema."""
        fields = self._extract_fields(schema)
        schema_text = " ".join(fields)
        return self._text_to_vector(schema_text)

    def _generate_field_vectors(self, schema: dict[str, Any]) -> dict[str, list[float]]:
        """Generate vectors for individual fields."""
        field_vectors = {}
        fields = self._extract_fields(schema)
        for field in fields:
            field_vectors[field] = self._text_to_vector(field)
        return field_vectors

    def _extract_fields(self, schema: dict[str, Any]) -> list[str]:
        """Extract field names from schema."""
        fields = []

        def extract_recursive(obj: object, prefix: str = "") -> None:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    field_name = f"{prefix}.{key}" if prefix else key
                    fields.append(field_name)
                    if key in ["properties", "fields"] and isinstance(value, dict):
                        extract_recursive(value, field_name)
                    elif isinstance(value, dict):
                        extract_recursive(value, field_name)

        extract_recursive(schema)
        return fields

    def _calculate_complexity(self, schema: dict[str, Any]) -> float:
        """Calculate complexity score for a schema."""
        fields = self._extract_fields(schema)
        field_count = len(fields)
        max_depth = max(f.count(".") for f in fields) if fields else 0
        complexity = min(1.0, (field_count / 100 + max_depth / 10) / 2)
        return complexity

    def _filter_entries(self, query: SchemaSearchQuery) -> list[SchemaVectorEntry]:
        """Filter schema entries based on query criteria."""
        filtered = list(self._schema_vectors.values())
        if query.schema_type_filter:
            filtered = [e for e in filtered if e.schema_type == query.schema_type_filter]
        if query.min_field_overlap > 0 and query.query_schema:
            query_fields = set(self._extract_fields(query.query_schema))
            filtered = [
                e
                for e in filtered
                if len(set(self._extract_fields({"fields": e.metadata})).intersection(query_fields))
                >= query.min_field_overlap
            ]
        return filtered

    def _semantic_search(
        self,
        query: SchemaSearchQuery,
        entries: list[SchemaVectorEntry],
    ) -> tuple[list[SchemaVectorEntry], list[float]]:
        """Perform semantic search."""
        if not query.query_vector:
            return ([], [])
        query_vector = np.array(query.query_vector)
        scored_entries = []
        for entry in entries:
            if entry.schema_id in self._vector_index:
                vector = self._vector_index[entry.schema_id]
                similarity = np.dot(query_vector, vector) / (
                    np.linalg.norm(query_vector) * np.linalg.norm(vector)
                )
                if similarity >= query.threshold:
                    scored_entries.append((entry, similarity))
        scored_entries.sort(key=lambda x: x[1], reverse=True)
        results = scored_entries[: query.top_k]
        entries = [e[0] for e in results]
        scores = [e[1] for e in results]
        return (entries, scores)

    def _structural_search(
        self,
        query: SchemaSearchQuery,
        entries: list[SchemaVectorEntry],
    ) -> tuple[list[SchemaVectorEntry], list[float]]:
        """Perform structural similarity search."""
        if not query.query_schema:
            return self._semantic_search(query, entries)
        query_fields = set(self._extract_fields(query.query_schema))
        scored_entries = []
        for entry in entries:
            entry_fields = set(self._extract_fields({"schema": entry.metadata}))
            intersection = len(query_fields.intersection(entry_fields))
            union = len(query_fields.union(entry_fields))
            if union > 0:
                similarity = intersection / union
                if similarity >= query.threshold:
                    scored_entries.append((entry, similarity))
        scored_entries.sort(key=lambda x: x[1], reverse=True)
        results = scored_entries[: query.top_k]
        entries = [e[0] for e in results]
        scores = [e[1] for e in results]
        return (entries, scores)

    def _hybrid_search(
        self,
        query: SchemaSearchQuery,
        entries: list[SchemaVectorEntry],
    ) -> tuple[list[SchemaVectorEntry], list[float]]:
        """Perform hybrid search combining semantic and structural."""
        semantic_entries, semantic_scores = self._semantic_search(query, entries)
        structural_entries, structural_scores = self._structural_search(query, entries)
        combined = {}
        for entry, score in zip(semantic_entries, semantic_scores, strict=False):
            combined[entry.schema_id] = (entry, score * 0.6)
        for entry, score in zip(structural_entries, structural_scores, strict=False):
            if entry.schema_id in combined:
                combined[entry.schema_id] = (entry, combined[entry.schema_id][1] + score * 0.4)
            else:
                combined[entry.schema_id] = (entry, score * 0.4)
        results = sorted(combined.values(), key=lambda x: x[1], reverse=True)[: query.top_k]
        entries = [e[0] for e in results]
        scores = [e[1] for e in results]
        return (entries, scores)

    def _field_based_search(
        self,
        query: SchemaSearchQuery,
        entries: list[SchemaVectorEntry],
    ) -> tuple[list[SchemaVectorEntry], list[float], list[dict[str, Any]]]:
        """Perform field-based search."""
        if not query.query_schema or not self.config.enable_field_vectors:
            return (self._semantic_search(query, entries), [], [])
        query_fields = self._extract_fields(query.query_schema)
        query_field_vectors = {field: self._text_to_vector(field) for field in query_fields}
        scored_entries = []
        field_matches_list = []
        for entry in tqdm(entries, desc="Processing", unit="item"):
            if entry.schema_id not in self._field_index:
                continue
            field_matches = []
            total_similarity = 0
            match_count = 0
            for query_field, query_vector in tqdm(
                query_field_vectors.items(), desc="Processing", unit="item"
            ):
                for entry_field, entry_vector in tqdm(
                    self._field_index[entry.schema_id].items(), desc="Processing", unit="item"
                ):
                    similarity = np.dot(query_vector, entry_vector) / (
                        np.linalg.norm(query_vector) * np.linalg.norm(entry_vector)
                    )
                    if similarity >= query.threshold:
                        field_matches.append(
                            {
                                "query_field": query_field,
                                "entry_field": entry_field,
                                "similarity": float(similarity),
                            },
                        )
                        total_similarity += similarity
                        match_count += 1
            if match_count > 0:
                avg_similarity = total_similarity / match_count
                scored_entries.append((entry, avg_similarity))
                field_matches_list.append(field_matches)
        scored_entries.sort(key=lambda x: x[1], reverse=True)
        results = scored_entries[: query.top_k]
        entries = [e[0] for e in results]
        scores = [e[1] for e in results]
        field_matches = field_matches_list[: query.top_k]
        return (entries, scores, field_matches)

    def _text_to_vector(self, text: str) -> list[float]:
        """Convert text to vector representation."""
        import hashlib

        hash_bytes = hashlib.md5(text.encode()).digest()
        vector = [float(b) / 255.0 for b in hash_bytes]
        if len(vector) < self.config.dimension:
            vector.extend([0.0] * (self.config.dimension - len(vector)))
        else:
            vector = vector[: self.config.dimension]
        return vector


# guardian: allow-magic-config
def create_schema_vector_searcher(
    dimension: int = 1536,
    enable_field_vectors: bool = True,
    similarity_threshold: float = 0.7,
    **kwargs: object,
) -> SchemaVectorSearcher:
    """Create a configured schema vector searcher."""
    config = SchemaVectorConfig(
        dimension=dimension,
        enable_field_vectors=enable_field_vectors,
        similarity_threshold=similarity_threshold,
        **kwargs,
    )
    return SchemaVectorSearcher(config)


# guardian: allow-magic-config
def search_schema_vectors(
    query_text: str | None = None,
    query_schema: dict[str, Any] | None = None,
    search_mode: str = "semantic",
    similarity_type: str = "semantic",
    top_k: int = 10,
    threshold: float = 0.7,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Search schema vectors.

    Args:
        query_text: Text query
        query_schema: schema query
        search_mode: Search mode to use
        similarity_type: Type of similarity to compute
        top_k: Number of results to return
        threshold: Minimum similarity threshold
        config: Optional searcher configuration

    Returns:
        Dict: Search results
    """
    searcher_config = SchemaVectorConfig(**config or {})
    searcher = SchemaVectorSearcher(searcher_config)
    query = SchemaSearchQuery(
        query_text=query_text,
        query_schema=query_schema,
        search_mode=SchemaSearchMode(search_mode),
        similarity_type=SchemaSimilarityType(similarity_type),
        top_k=top_k,
        threshold=threshold,
    )
    result = searcher.search_schema_vectors(query)
    return {
        "entries": [
            {
                "schema_id": e.schema_id,
                "schema_name": e.schema_name,
                "schema_type": e.schema_type,
                "field_count": e.field_count,
                "complexity_score": e.complexity_score,
                "timestamp": e.timestamp.isoformat(),
                "metadata": e.metadata,
            }
            for e in result.entries
        ],
        "scores": result.scores,
        "field_matches": result.field_matches,
        "search_time_ms": result.search_time_ms,
        "metadata": result.metadata,
    }
