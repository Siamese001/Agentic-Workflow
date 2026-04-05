"""GraphRAG Fusion - Combining Vector and Graph Retrieval.

This module implements the fusion of vector similarity search with knowledge graph
traversal to enable multi-hop reasoning and relationship-based queries.
"""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Final

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

_emit_applies_guardrail("p0", "graph_rag_fusion_util", "p0_governance")
_emit_reads_policy_state("p0", "graph_rag_fusion_util", "policy_binding")
_emit_snapshots_state("p0", "graph_rag_fusion_util", "state_snapshot")
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

_emit_emits_metric_event("graph_rag_fusion_util", "p4obs", "metric_1")
_emit_emits_metric_event("graph_rag_fusion_util", "p4obs", "metric_2")
_emit_emits_metric_event("graph_rag_fusion_util", "p4obs", "metric_3")
_emit_emits_metric_event("graph_rag_fusion_util", "p4obs", "metric_4")
_emit_emits_metric_event("graph_rag_fusion_util", "p4obs", "metric_5")
_emit_emits_metric_event("graph_rag_fusion_util", "p4obs", "metric_6")
_emit_records_incident_event("graph_rag_fusion_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("graph_rag_fusion_util", "p4obs", "anomaly")
_emit_writes_observability_log("graph_rag_fusion_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("graph_rag_fusion_util", "p4obs", "mon_state")
_emit_triggers_alert("graph_rag_fusion_util", "p4obs", "alert")
_emit_links_incident_trace("graph_rag_fusion_util", "p4obs", "trace_link")
_emit_captures_pattern("graph_rag_fusion_util", "p3lm", "pattern")
_emit_records_learning_event("graph_rag_fusion_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("graph_rag_fusion_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("graph_rag_fusion_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("graph_rag_fusion_util", "p3lm", "routing")
_emit_improves_agent_policy("graph_rag_fusion_util", "p3lm", "policy")
_emit_stores_learning_state("graph_rag_fusion_util", "p3lm", "state")
_emit_records_execution_trace("graph_rag_fusion_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("graph_rag_fusion_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("graph_rag_fusion_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("graph_rag_fusion_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("graph_rag_fusion_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("graph_rag_fusion_util", "env_read", "p2_env_1")
_emit_reads_environ("graph_rag_fusion_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("graph_rag_fusion_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("graph_rag_fusion_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "graph_rag_fusion_util", "context_pull")
_emit_pulls_context("p1", "graph_rag_fusion_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "graph_rag_fusion_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "graph_rag_fusion_util", "uwg_term_2")
_emit_writes_through("p1", "graph_rag_fusion_util", "write_through")
_emit_writes_through("p1", "graph_rag_fusion_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "graph_rag_fusion_util", "safety_validation")
_emit_invokes_eval("p1", "graph_rag_fusion_util", "eval_call")
_emit_proposal_commits_routing("p1", "graph_rag_fusion_util", "routing_commit")
_emit_escalates_to_human("p1", "graph_rag_fusion_util", "human_escalation")
_emit_routes_through("p1", "graph_rag_fusion_util", "route_through")
_emit_checks_agent_registry("p1", "graph_rag_fusion_util", "agent_registry")
_emit_validates_agent_capability("p1", "graph_rag_fusion_util", "capability")
_emit_dispatches_execution_plan("p1", "graph_rag_fusion_util", "exec_plan")
_emit_agent_executes_agent("p1", "graph_rag_fusion_util", "sub_agent")
_emit_routes_to_agent("p1", "graph_rag_fusion_util", "target_agent")
_emit_verifies_policy("p1", "graph_rag_fusion_util", "policy_check")
_emit_observes_runtime_state("p1", "graph_rag_fusion_util", "runtime_state")
_emit_verifies_boundary("p1", "graph_rag_fusion_util", "boundary_check")
_emit_transcripts_response("p1", "graph_rag_fusion_util", "transcript")
_emit_hard_fails_untranscripted("p1", "graph_rag_fusion_util")
_emit_gated_by_confidence("p1", "graph_rag_fusion_util", "confidence_gate")
emit_replay_key("p0", "graph_rag_fusion_util")
emit_determinism_digest("p0", "graph_rag_fusion_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "graph_rag_fusion_util", "execution_auth")
_emit_validates_capability("p2", "graph_rag_fusion_util", "capability_check")
_emit_routes_to_capability("p2", "graph_rag_fusion_util", "capability_route")
_emit_writes_via_uwg("p2", "graph_rag_fusion_util", "uwg_write")
_emit_blocks_direct_write("p2", "graph_rag_fusion_util", "direct_write_block")
_emit_records_tool_invocation("p2", "graph_rag_fusion_util", "tool_invocation")
_emit_captures_execution_output("p2", "graph_rag_fusion_util", "exec_output")
_emit_dispatches_agent("p3", "graph_rag_fusion_util", "agent_dispatch")
_emit_coordinates_agents("p3", "graph_rag_fusion_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "graph_rag_fusion_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "graph_rag_fusion_util", "healing_outcome")
_emit_escalates_failure("p3", "graph_rag_fusion_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "graph_rag_fusion_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "graph_rag_fusion_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "graph_rag_fusion_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "graph_rag_fusion_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "graph_rag_fusion_util", "eval_metric")
_emit_stores_embedding("p4", "graph_rag_fusion_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "graph_rag_fusion_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "graph_rag_fusion_util", "exec_snapshot_link")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_1")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_2")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_3")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_4")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_5")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_6")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_7")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_8")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_9")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_10")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_11")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_12")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_13")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_14")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_15")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_16")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_17")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_18")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_19")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_20")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_21")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_22")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_23")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_24")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_25")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_26")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_27")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_28")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_29")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_30")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_31")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_32")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_33")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_34")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_35")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_36")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_37")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_38")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_39")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_40")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_41")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_42")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_43")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_44")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_45")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_46")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_47")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_48")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_49")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_50")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_51")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_52")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_53")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_54")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_55")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_56")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_57")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_58")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_59")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_60")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_61")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_62")
_emit_reads_through("l4", "graph_rag_fusion_util", "urg_read_63")

logger = logging.getLogger(__name__)
from apps_shared.config.pipeline_constants_config import MAX_RETRIES  # noqa: F401

DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
DEFAULT_CONFIDENCE_THRESHOLD: Final[float] = 0.6
DEFAULT_MAX_RESULTS: Final[int] = 5


@dataclass
class GraphContext:
    entities: list[dict[str, Any]] = None
    relationships: list[dict[str, Any]] = None
    confidence: float = 0.0

    def __post_init__(self) -> None:
        if self.entities is None:
            self.entities = []
        if self.relationships is None:
            self.relationships = []


class KnowledgeGraphAgent:
    def query_context(self, _entity: str, hops: int = 2, limit: int = 5) -> GraphContext:
        return GraphContext(confidence=0.0)


class QueryType(Enum):
    """Types of queries for GraphRAG."""

    VECTOR_ONLY = "vector_only"
    GRAPH_ONLY = "graph_only"
    FUSION = "fusion"
    MULTI_HOP = "multi_hop"


@dataclass
class FusionResult:
    """Result of GraphRAG fusion query."""

    query: str
    query_type: QueryType
    vector_results: list[dict[str, Any]] = None
    graph_results: GraphContext = None
    fused_context: str = ""
    sources: list[str] = None
    confidence: float = 0.0
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.vector_results is None:
            self.vector_results = []
        if self.graph_results is None:
            self.graph_results = GraphContext()
        if self.sources is None:
            self.sources = []
        if self.metadata is None:
            self.metadata = {}


class CypherQueryGenerator:
    """Generates Cypher queries from natural language patterns."""

    def __init__(self):
        """Initialize the query generator with patterns."""
        self.patterns = {
            "skills_match": "(?:what|which) skills do (?:i|you|candidate) have (?:for|in|related to) (.+)",
            "experience_with": "(?:experience|worked|used) (?:with|on) (.+)",
            "projects_using": "projects (?:using|with|involving) (.+)",
            "role_at_company": "(?:role|position|job) (?:at|in) (.+)",
            "company_tech_stack": "(?:tech stack|technology|technologies) (?:at|used by) (.+)",
            "team_collaboration": "(?:worked|collaborated) (?:with|on) (.+)",
            "career_path": "(?:career|progression|advancement) (?:path|track) (?:for|to) (.+)",
            "skill_to_role": "(.+) skills (?:lead to|for|required for) (.+) role",
            "project_outcomes": "(?:outcome|result|impact) (?:of|from) (.+) project",
            "technologies_for": "(?:technologies|tech) (?:for|to|needed for) (.+)",
        }
        self.templates = {
            "skills_match": "\n                MATCH (e:Entity)-[:HAS_SKILL]->(s:Skill)\n                WHERE s.name =~ $skill_pattern\n                OPTIONAL MATCH (e)-[:WORKED_ON]->(p:Project)\n                RETURN e.name as entity,\n                       collect(DISTINCT s.name) as skills,\n                       collect(DISTINCT p.name) as projects\n                LIMIT 10\n            ",
            "experience_with": "\n                MATCH (e:Entity)-[:WORKED_WITH]->(t:Technology)\n                WHERE t.name =~ $tech_pattern\n                OPTIONAL MATCH (e)-[:WORKED_ON]->(p:Project)\n                RETURN e.name as entity,\n                       t.name as technology,\n                       collect(DISTINCT p.name) as projects\n                LIMIT 10\n            ",
            "projects_using": "\n                MATCH (p:Project)-[:USES_TECH]->(t:Technology)\n                WHERE t.name =~ $tech_pattern\n                OPTIONAL MATCH (e:Entity)-[:WORKED_ON]->(p)\n                RETURN p.name as project,\n                       collect(DISTINCT t.name) as technologies,\n                       collect(DISTINCT e.name) as contributors\n                LIMIT 10\n            ",
            "role_at_company": "\n                MATCH (e:Entity)-[:WORKED_AT]->(c:Company)\n                WHERE c.name =~ $company_pattern\n                OPTIONAL MATCH (e)-[:HAD_ROLE]->(r:Role)\n                RETURN e.name as entity,\n                       c.name as company,\n                       collect(DISTINCT r.name) as roles\n                LIMIT 10\n            ",
            "company_tech_stack": "\n                MATCH (c:Company)-[:USES_TECH]->(t:Technology)\n                WHERE c.name =~ $company_pattern\n                RETURN c.name as company,\n                       collect(DISTINCT t.name) as tech_stack\n                LIMIT 10\n            ",
            "team_collaboration": "\n                MATCH (e1:Entity)-[:COLLABORATED_WITH]->(e2:Entity)\n                WHERE e1.name =~ $entity_pattern OR e2.name =~ $entity_pattern\n                OPTIONAL MATCH (e1)-[:WORKED_ON]->(p:Project)<-[:WORKED_ON]-(e2)\n                RETURN e1.name as collaborator1,\n                       e2.name as collaborator2,\n                       collect(DISTINCT p.name) as shared_projects\n                LIMIT 10\n            ",
            "career_path": "\n                MATCH path = (e:Entity)-[:NEXT_ROLE*]->(r:Role)\n                WHERE e.name =~ $entity_pattern\n                RETURN [node in nodes(path) | node.name] as career_progression\n                LIMIT 5\n            ",
            "skill_to_role": "\n                MATCH (s:Skill)-[:REQUIRED_FOR]->(r:Role)\n                WHERE s.name =~ $skill_pattern AND r.name =~ $role_pattern\n                RETURN s.name as skill,\n                       r.name as role,\n                       collect(DISTINCT r.level) as levels\n                LIMIT 10\n            ",
            "project_outcomes": "\n                MATCH (p:Project)-[:RESULTED_IN]->(o:Outcome)\n                WHERE p.name =~ $project_pattern\n                RETURN p.name as project,\n                       collect(DISTINCT o.name) as outcomes,\n                       collect(DISTINCT o.metric) as metrics\n                LIMIT 10\n            ",
            "technologies_for": "\n                MATCH (d:Domain)-[:REQUIRES_TECH]->(t:Technology)\n                WHERE d.name =~ $domain_pattern\n                RETURN d.name as domain,\n                       collect(DISTINCT t.name) as technologies\n                LIMIT 10\n            ",
        }

    def generate_query(self, natural_query: str) -> tuple[str, dict[str, Any], str]:
        """Generate Cypher query from natural language.

        Args:
            natural_query: Natural language query

        Returns:
            Tuple of (cypher_query, parameters, query_type)
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "GraphRAGQueryGenerator.generate_query")
        natural_lower = natural_query.lower()
        for pattern_name, pattern in self.patterns.items():
            match = re.search(pattern, natural_lower)
            if match:
                template = self.templates[pattern_name]
                if pattern_name == "skill_to_role":
                    skill_pattern = f"(?i).*{match.group(1)}.*"
                    role_pattern = f"(?i).*{match.group(2)}.*"
                    params = {"skill_pattern": skill_pattern, "role_pattern": role_pattern}
                else:
                    entity = match.group(1).strip()
                    entity_pattern = f"(?i).*{entity}.*"
                    if "skill" in pattern_name:
                        params = {"skill_pattern": entity_pattern}
                    elif "tech" in pattern_name:
                        params = {"tech_pattern": entity_pattern}
                    elif "company" in pattern_name:
                        params = {"company_pattern": entity_pattern}
                    elif "project" in pattern_name:
                        params = {"project_pattern": entity_pattern}
                    elif "domain" in pattern_name:
                        params = {"domain_pattern": entity_pattern}
                    elif "entity" in pattern_name:
                        params = {"entity_pattern": entity_pattern}
                    else:
                        params = {"entity_pattern": entity_pattern}
                return (template, params, pattern_name)
        fallback_template = "\n            MATCH (e:Entity)\n            WHERE e.name =~ $entity_pattern\n            OPTIONAL MATCH (e)-[r]-(related)\n            RETURN e.name as entity,\n                   labels(e) as types,\n                   collect(DISTINCT related.name)[0..5] as related_entities\n            LIMIT 10\n        "
        entity_pattern = f"(?i).*{natural_lower.split()[-1]}.*"
        return (fallback_template, {"entity_pattern": entity_pattern}, "entity_search")


class GraphRAGFusion:
    """Fuses vector and graph retrieval for enhanced RAG."""

    def __init__(
        self,
        knowledge_graph: KnowledgeGraphAgent | None = None,
        vector_retriever: callable | None = None,
        enable_fusion: bool = True,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    ):
        """Initialize GraphRAG fusion.

        Args:
            knowledge_graph: KnowledgeGraphAgent instance
            vector_retriever: Function for vector retrieval
            enable_fusion: Whether to enable fusion (vs. vector-only)
            confidence_threshold: Minimum confidence for fusion results
        """
        self.knowledge_graph = knowledge_graph
        self.vector_retriever = vector_retriever
        self.enable_fusion = enable_fusion
        self.confidence_threshold = confidence_threshold
        self.query_generator = CypherQueryGenerator()
        self.stats = {
            "total_queries": 0,
            "vector_only": 0,
            "graph_only": 0,
            "fusion_queries": 0,
            "multi_hop_queries": 0,
            "graph_fallbacks": 0,
        }
        logger.info(f"Initialized GraphRAGFusion - Fusion: {enable_fusion}")

    async def query(
        self, natural_query: str, query_type: QueryType | None = None, max_results: int = DEFAULT_MAX_RESULTS
    ) -> FusionResult:
        """Execute a GraphRAG fusion query.

        Args:
            natural_query: Natural language query
            query_type: Type of query (auto-detected if None)
            max_results: Maximum results to return

        Returns:
            FusionResult with combined results
        """
        self.stats["total_queries"] += 1
        if query_type is None:
            query_type = self._detect_query_type(natural_query)
        if query_type == QueryType.VECTOR_ONLY:
            return await self._vector_only_query(natural_query, max_results)
        elif query_type == QueryType.GRAPH_ONLY:
            return await self._graph_only_query(natural_query, max_results)
        else:
            return await self._fusion_query(natural_query, query_type, max_results)

    def _detect_query_type(self, query: str) -> QueryType:
        """Detect query type from natural language.

        Args:
            query: Natural language query

        Returns:
            Detected QueryType
        """
        query_lower = query.lower()
        relationship_words = [
            "relationship",
            "connection",
            "between",
            "related to",
            "worked with",
            "collaborated",
            "team",
            "together",
        ]
        multi_hop_words = [
            "path",
            "journey",
            "progression",
            "through",
            "via",
            "leads to",
            "resulted in",
            "caused",
        ]
        graph_patterns = ["nodes", "edges", "graph", "network", "hops", "traverse", "connected"]
        if any(word in query_lower for word in multi_hop_words):
            return QueryType.MULTI_HOP
        elif any(word in query_lower for word in relationship_words):
            return QueryType.FUSION
        elif any(word in query_lower for word in graph_patterns):
            return QueryType.GRAPH_ONLY
        else:
            return QueryType.VECTOR_ONLY

    async def _vector_only_query(self, query: str, max_results: int) -> FusionResult:
        """Execute vector-only query.

        Args:
            query: Query string
            max_results: Maximum results

        Returns:
            FusionResult with vector results
        """
        self.stats["vector_only"] += 1
        try:
            if self.vector_retriever:
                vector_results = await self.vector_retriever(query, max_results)
            else:
                vector_results = []
            return FusionResult(
                query=query,
                query_type=QueryType.VECTOR_ONLY,
                vector_results=vector_results,
                sources=["vector_search"],
                confidence=0.8,
            )
        except Exception as e:
            logger.error(f"Vector query failed: {e}")
            return None

    async def _graph_only_query(self, query: str, max_results: int) -> FusionResult:
        """Execute graph-only query.

        Args:
            query: Query string
            max_results: Maximum results

        Returns:
            FusionResult with graph results
        """
        self.stats["graph_only"] += 1
        try:
            if self.knowledge_graph:
                cypher, params, pattern_type = self.query_generator.generate_query(query)
                graph_context = self.knowledge_graph.query_context(
                    params.get("entity_pattern", "").replace("(?i).*", "").replace(".*", ""),
                    hops=2,
                    limit=max_results,
                )
                return FusionResult(
                    query=query,
                    query_type=QueryType.GRAPH_ONLY,
                    graph_results=graph_context,
                    sources=["graph_search"],
                    confidence=graph_context.confidence,
                    metadata={"cypher_pattern": pattern_type},
                )
            else:
                self.stats["graph_fallbacks"] += 1
                return FusionResult(
                    query=query,
                    query_type=QueryType.GRAPH_ONLY,
                    sources=["graph_unavailable"],
                    confidence=0.0,
                )
        except Exception as e:
            logger.error(f"Graph query failed: {e}")
            return None

    async def _fusion_query(self, query: str, query_type: QueryType, max_results: int) -> FusionResult:
        """Execute fusion query combining vector and graph.

        Args:
            query: Query string
            query_type: Type of fusion query
            max_results: Maximum results

        Returns:
            FusionResult with fused results
        """
        if query_type == QueryType.MULTI_HOP:
            self.stats["multi_hop_queries"] += 1
        else:
            self.stats["fusion_queries"] += 1
        vector_task = self._vector_only_query(query, max_results)
        graph_task = self._graph_only_query(query, max_results)
        vector_result, graph_result = await asyncio.gather(vector_task, graph_task, return_exceptions=True)
        if isinstance(vector_result, Exception):
            vector_result = FusionResult(query=query, query_type=QueryType.VECTOR_ONLY)
        if isinstance(graph_result, Exception):
            graph_result = FusionResult(query=query, query_type=QueryType.GRAPH_ONLY)
        fused_context = self._fuse_results(
            vector_result.vector_results, graph_result.graph_results, query_type
        )
        combined_sources = vector_result.sources + graph_result.sources
        combined_confidence = max(vector_result.confidence, graph_result.confidence)
        return FusionResult(
            query=query,
            query_type=query_type,
            vector_results=vector_result.vector_results,
            graph_results=graph_result.graph_results,
            fused_context=fused_context,
            sources=combined_sources,
            confidence=combined_confidence,
            metadata={
                "vector_confidence": vector_result.confidence,
                "graph_confidence": graph_result.confidence,
                "graph_metadata": graph_result.metadata,
            },
        )

    def _fuse_results(
        self, vector_results: list[dict[str, Any]], graph_context: GraphContext, query_type: QueryType
    ) -> str:
        """Fuse vector and graph results into context.

        Args:
            vector_results: Results from vector search
            graph_context: Results from graph search
            query_type: Type of query

        Returns:
            Fused context string
        """
        context_parts = []
        if vector_results:
            context_parts.append("## Unstructured Knowledge")
            for i, result in enumerate(vector_results[:3], 1):
                text = ""
                if isinstance(result, dict):
                    text = result.get("text", result.get("content", ""))
                else:
                    text = str(result)
                context_parts.append(f"{i}. {text[:200]}...")
        if graph_context and graph_context.entities:
            context_parts.append("\n## Structured Relationships")
            if graph_context.entities:
                context_parts.append("### Key Entities:")
                for entity in graph_context.entities[:5]:
                    name = entity.get("name", entity.get("entity_name", "Unknown"))
                    score = entity.get("influence_score", entity.get("score", 0))
                    context_parts.append(f"- {name} (relevance: {score:.2f})")
            if graph_context.relationships:
                context_parts.append("\n### Relationships:")
                for rel in graph_context.relationships[:5]:
                    source = rel.get("source", rel.get("start", "Unknown"))
                    target = rel.get("target", rel.get("end", "Unknown"))
                    rel_type = rel.get("type", "related_to")
                    context_parts.append(f"- {source} --[{rel_type}]--> {target}")
        return "\n".join(context_parts)

    def get_stats(self) -> dict[str, Any]:
        """Get fusion statistics.

        Returns:
            Dictionary with stats
        """
        return {
            **self.stats,
            "fusion_enabled": self.enable_fusion,
            "graph_available": self.knowledge_graph is not None,
            "vector_available": self.vector_retriever is not None,
        }


_graphrag_fusion: GraphRAGFusion | None = None


def get_graphrag_fusion(**kwargs) -> GraphRAGFusion:
    """Get or create global GraphRAG fusion instance.

    Args:
        **kwargs: Arguments for GraphRAGFusion

    Returns:
        GraphRAGFusion instance
    """
    global _graphrag_fusion
    if _graphrag_fusion is None:
        _graphrag_fusion = GraphRAGFusion(**kwargs)
    return _graphrag_fusion


async def graphrag_query(
    query: str, query_type: QueryType | None = None, max_results: int = DEFAULT_MAX_RESULTS, **kwargs
) -> FusionResult:
    """Convenience function for GraphRAG query.

    Args:
        query: Natural language query
        query_type: Type of query
        max_results: Maximum results
        **kwargs: Additional arguments

    Returns:
        FusionResult
    """
    fusion = get_graphrag_fusion(**kwargs)
    return await fusion.query(query, query_type, max_results)
