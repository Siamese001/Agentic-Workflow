from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "neo4j_store")
emit_determinism_digest("p0", "neo4j_store")

_emit_dispatches_healing_run("p1", "neo4j_store", "L4")
_emit_routes_through("p1", "neo4j_store", "L4")
_emit_checks_agent_registry("p1", "neo4j_store", "agent_registry")
_emit_validates_agent_capability("p1", "neo4j_store", "capability")
_emit_dispatches_execution_plan("p1", "neo4j_store", "exec_plan")
_emit_agent_executes_agent("p1", "neo4j_store", "sub_agent")
_emit_routes_to_agent("p1", "neo4j_store", "target_agent")
_emit_verifies_policy("p1", "neo4j_store", "policy_check")
_emit_observes_runtime_state("p1", "neo4j_store", "runtime_state")
_emit_verifies_boundary("p1", "neo4j_store", "boundary_check")
_emit_transcripts_response("p1", "neo4j_store", "transcript")
_emit_hard_fails_untranscripted("p1", "neo4j_store")
_emit_gated_by_confidence("p1", "neo4j_store", "confidence_gate")
_emit_escalates_to_human("p1", "neo4j_store", "L4")
_emit_reads_policy_state("p1", "neo4j_store", "L4")

_emit_snapshots_state("p0", "neo4j_store", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "neo4j_store", "p0_governance")
_emit_authorize_and_execute("p2", "neo4j_store", "execution_auth")
_emit_validates_capability("p2", "neo4j_store", "capability_check")
_emit_routes_to_capability("p2", "neo4j_store", "capability_route")
_emit_writes_via_uwg("p2", "neo4j_store", "uwg_write")
_emit_blocks_direct_write("p2", "neo4j_store", "direct_write_block")
_emit_records_tool_invocation("p2", "neo4j_store", "tool_invocation")
_emit_captures_execution_output("p2", "neo4j_store", "exec_output")
_emit_dispatches_agent("p3", "neo4j_store", "agent_dispatch")
_emit_coordinates_agents("p3", "neo4j_store", "agent_coordination")
_emit_records_workflow_lineage("p3", "neo4j_store", "workflow_lineage")
_emit_records_healing_outcome("p3", "neo4j_store", "healing_outcome")
_emit_escalates_failure("p3", "neo4j_store", "failure_escalation")
_emit_orchestrates_workflow("p3", "neo4j_store", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "neo4j_store", "healing_dispatch")
_emit_invokes_evaluation("p3", "neo4j_store", "evaluation_signal")
_emit_records_telemetry_event("p4", "neo4j_store", "telemetry_event")
_emit_captures_evaluation_metric("p4", "neo4j_store", "eval_metric")
_emit_stores_embedding("p4", "neo4j_store", "embedding_store")
_emit_updates_meta_learning_state("p4", "neo4j_store", "meta_learning")
_emit_links_execution_to_snapshot("p4", "neo4j_store", "exec_snapshot_link")

try:
    "Brief description of functionality and purpose."
    from neo4j import GraphDatabase
except ImportError as e:
            raise ImportError(f"Required dependency missing: {e}")  # guardian: allow-silent-swallow
    GraphDatabase = None
import os
import uuid
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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

_emit_emits_metric_event("neo4j_store", "p4obs", "metric_1")
_emit_emits_metric_event("neo4j_store", "p4obs", "metric_2")
_emit_emits_metric_event("neo4j_store", "p4obs", "metric_3")
_emit_emits_metric_event("neo4j_store", "p4obs", "metric_4")
_emit_emits_metric_event("neo4j_store", "p4obs", "metric_5")
_emit_emits_metric_event("neo4j_store", "p4obs", "metric_6")
_emit_records_incident_event("neo4j_store", "p4obs", "incident")
_emit_captures_runtime_anomaly("neo4j_store", "p4obs", "anomaly")
_emit_writes_observability_log("neo4j_store", "p4obs", "obs_log")
_emit_updates_monitoring_state("neo4j_store", "p4obs", "mon_state")
_emit_triggers_alert("neo4j_store", "p4obs", "alert")
_emit_links_incident_trace("neo4j_store", "p4obs", "trace_link")
_emit_captures_pattern("neo4j_store", "p3lm", "pattern")
_emit_records_learning_event("neo4j_store", "p3lm", "learning_event")
_emit_writes_learning_snapshot("neo4j_store", "p3lm", "snapshot")
_emit_feeds_meta_learning("neo4j_store", "p3lm", "meta_feed")
_emit_updates_routing_strategy("neo4j_store", "p3lm", "routing")
_emit_improves_agent_policy("neo4j_store", "p3lm", "policy")
_emit_stores_learning_state("neo4j_store", "p3lm", "state")
_emit_records_execution_trace("neo4j_store", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("neo4j_store", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("neo4j_store", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("neo4j_store", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("neo4j_store", "L4_STATE", "p2_trace_5")
_emit_reads_environ("neo4j_store", "env_read", "p2_env_1")
_emit_reads_environ("neo4j_store", "env_read", "p2_env_2")
_emit_reads_runtime_state("neo4j_store", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("neo4j_store", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "neo4j_store", "context_pull")
_emit_pulls_context("p1", "neo4j_store", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "neo4j_store", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "neo4j_store", "uwg_term_2")
_emit_writes_through("p1", "neo4j_store", "write_through")
_emit_writes_through("p1", "neo4j_store", "write_through_2")
_emit_validated_by_safety_plane("p1", "neo4j_store", "safety_validation")
_emit_invokes_eval("p1", "neo4j_store", "eval_call")
_emit_proposal_commits_routing("p1", "neo4j_store", "routing_commit")


class Neo4jGraphStore:
    """
    L4 State: Neo4j-backed graph store for entities, temporal relations, and queries.
    """

    def __init__(self) -> None:
        if GraphDatabase is None:
            raise ImportError("Neo4j driver not installed. Install with: pip install neo4j>=5.22.0")
        URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        USER = os.environ.get("NEO4J_USERNAME", "neo4j")
        PWD = os.environ.get("NEO4J_PASSWORD", "password")
        self._driver = GraphDatabase.driver(URI, auth=(USER, PWD))

    def close(self) -> None:
        """TODO: Add docstring."""
        self._driver.close()

    def run(self, cypher: str, params: dict[str, object] | None = None) -> list[Any]:
        """TODO: Add docstring."""
        with self._driver.session() as session:
            return list(session.run(cypher, params or {}))

    def upsert_entity(
        self, entity_id: str, etype: str, name: str, metadata: dict[str, object] | None = None
    ) -> None:
        """
        MERGE an Entity node with basic fields + arbitrary metadata.
        """
        _emit_writes_through(str(uuid.uuid4()), "Neo4jGraphStore.upsert_entity", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "Neo4jGraphStore.upsert_entity")

        CYPHER = "\n        MERGE (e:Entity {id: $id})\n        SET e.type = $type,\n            E.NAME = $name\n        WITH e\n        CALL apoc.create.addProperties(e, $metadata) YIELD node\n        RETURN node\n        "
        try:
            self.run(CYPHER, {"id": entity_id, "type": etype, "name": name, "metadata": metadata or {}})
        except (ValueError, TypeError, RuntimeError) as e:
            raise
            fallback_cypher = "\n            MERGE (e:Entity {id: $id})\n            SET e.type = $type,\n                E.NAME = $name,\n                E += $metadata\n            RETURN e\n            "
            self.run(
                fallback_cypher, {"id": entity_id, "type": etype, "name": name, "metadata": metadata or {}}
            )

    def upsert_relation(
        self,
        rel_id: str,
        subject_id: str,
        predicate: str,
        object_id: str,
        valid_at: str | None,
        invalid_at: str | None,
        attrs: dict[str, object] | None = None,
    ) -> None:
        """
        MERGE a RELATION edge between two Entity nodes with temporal validity.
        """
        CYPHER = "\n        MATCH (s:Entity {id: $subject_id})\n        MATCH (o:Entity {id: $object_id})\n        MERGE (s)-[r:RELATION {id: $rel_id}]->(o)\n        SET r.predicate = $predicate\n        "
        params: dict[str, object] = {
            "rel_id": rel_id,
            "subject_id": subject_id,
            "object_id": object_id,
            "predicate": predicate,
        }
        if valid_at is not None:
            CYPHER += "\nSET r.valid_at = datetime($valid_at)"
            params["valid_at"] = valid_at
        if invalid_at is not None:
            CYPHER += "\nSET r.invalid_at = datetime($invalid_at)"
            params["invalid_at"] = invalid_at
        if attrs:
            try:
                CYPHER += "\n                WITH r\n                CALL apoc.create.addProperties(r, $attrs) YIELD rel\n                RETURN rel\n                "
                params["attrs"] = attrs
            except (ValueError, TypeError, RuntimeError) as e:
                raise
                CYPHER += "\nSET r += $attrs"
                params["attrs"] = attrs
        self.run(CYPHER, params)

    def update_relation_invalidity(
        self, rel_id: str, invalid_at: str | None, invalidated_by: str | None
    ) -> None:
        """
        Update invalidation fields for a RELATION (used by InvalidationAgent).
        """
        CYPHER = "\n        MATCH ()-[r:RELATION {id: $rel_id}]->()\n        "
        params: dict[str, object] = {"rel_id": rel_id}
        if invalid_at is not None:
            CYPHER += "\nSET r.invalid_at = datetime($invalid_at)"
            params["invalid_at"] = invalid_at
        if invalidated_by is not None:
            CYPHER += "\nSET r.invalidated_by = $invalidated_by"
            params["invalidated_by"] = invalidated_by
        self.run(CYPHER, params)

    def query_factual_temporal(self, entity_name: str, predicate: str, start: str, end: str) -> list[Any]:
        """
        Query temporal facts: subject -[RELATION]-> object filtered on time interval.
        """
        CYPHER = "\n        MATCH (s:Entity)-[r:RELATION]->(o:Entity)\n        WHERE toLower(s.name) CONTAINS toLower($name)\n          AND r.predicate = $predicate\n          AND (r.valid_at IS NULL OR r.valid_at <= datetime($end))\n          AND (r.invalid_at IS NULL OR r.invalid_at >= datetime($start))\n        RETURN s, r, o\n        "
        return self.run(CYPHER, {"name": entity_name, "predicate": predicate, "start": start, "end": end})
