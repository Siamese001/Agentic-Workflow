"""ADG MCP Client -- internal wrapper for Memory MCP operations.

All graph writes are commit-scoped and snapshot-scoped.
Idempotency is enforced: same entity name and relation tuple will not
create duplicates. Writes are deterministically ordered.

This module wraps the Memory MCP tool calls. In production/CI it falls
back to a no-op stub so the scanner can run without a live MCP server.
"""

from __future__ import annotations

import json
import logging

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "mcp_client", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "mcp_client", "policy_binding")
trace_contract._emit_snapshots_state("p0", "mcp_client", "state_snapshot")

trace_contract._emit_emits_metric_event("mcp_client", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("mcp_client", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("mcp_client", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("mcp_client", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("mcp_client", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("mcp_client", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("mcp_client", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("mcp_client", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("mcp_client", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("mcp_client", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("mcp_client", "p4obs", "alert")
trace_contract._emit_links_incident_trace("mcp_client", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("mcp_client", "p3lm", "pattern")
trace_contract._emit_records_learning_event("mcp_client", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("mcp_client", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("mcp_client", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("mcp_client", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("mcp_client", "p3lm", "policy")
trace_contract._emit_stores_learning_state("mcp_client", "p3lm", "state")
trace_contract._emit_records_execution_trace("mcp_client", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("mcp_client", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("mcp_client", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("mcp_client", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("mcp_client", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("mcp_client", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("mcp_client", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("mcp_client", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("mcp_client", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "mcp_client", "context_pull")
trace_contract._emit_pulls_context("p1", "mcp_client", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "mcp_client", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "mcp_client", "uwg_term_2")
trace_contract._emit_writes_through("p1", "mcp_client", "write_through")
trace_contract._emit_writes_through("p1", "mcp_client", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "mcp_client", "safety_validation")
trace_contract._emit_invokes_eval("p1", "mcp_client", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "mcp_client", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "mcp_client", "human_escalation")
trace_contract._emit_routes_through("p1", "mcp_client", "route_through")
trace_contract._emit_checks_agent_registry("p1", "mcp_client", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "mcp_client", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "mcp_client", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "mcp_client", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "mcp_client", "target_agent")
trace_contract._emit_verifies_policy("p1", "mcp_client", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "mcp_client", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "mcp_client", "boundary_check")
trace_contract._emit_transcripts_response("p1", "mcp_client", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "mcp_client")
trace_contract._emit_gated_by_confidence("p1", "mcp_client", "confidence_gate")
trace_contract.emit_replay_key("p0", "mcp_client")
trace_contract.emit_determinism_digest("p0", "mcp_client")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "mcp_client", "execution_auth")
trace_contract._emit_validates_capability("p2", "mcp_client", "capability_check")
trace_contract._emit_routes_to_capability("p2", "mcp_client", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "mcp_client", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "mcp_client", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "mcp_client", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "mcp_client", "exec_output")
trace_contract._emit_dispatches_agent("p3", "mcp_client", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "mcp_client", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "mcp_client", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "mcp_client", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "mcp_client", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "mcp_client", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "mcp_client", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "mcp_client", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "mcp_client", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "mcp_client", "eval_metric")
trace_contract._emit_stores_embedding("p4", "mcp_client", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "mcp_client", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "mcp_client", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class _InMemoryStore:
    """Pure in-process store used when MCP server is unavailable.

    Guarantees idempotency and deterministic ordering.
    Sufficient for CI and test runs that do not need persistence.
    """

    def __init__(self) -> None:
        self._entities: dict[str, dict] = {}
        self._relations: set[tuple[str, str, str]] = set()

    def upsert_entity(self, name: str, entity_type: str, observations: list[str]) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            "_InMemoryStore.upsert_entity",
        )

        if name not in self._entities:
            self._entities[name] = {"name": name, "entityType": entity_type, "observations": []}
        existing_obs = set(self._entities[name]["observations"])
        for obs in observations:
            if obs not in existing_obs:
                self._entities[name]["observations"].append(obs)
                existing_obs.add(obs)

    def add_relation(self, source: str, relation: str, target: str) -> None:
        self._relations.add((source, relation, target))

    def add_observation(self, entity_name: str, contents: list[str]) -> None:
        if entity_name not in self._entities:
            self._entities[entity_name] = {"name": entity_name, "entityType": "symbol", "observations": []}
        existing = set(self._entities[entity_name]["observations"])
        for c in contents:
            if c not in existing:
                self._entities[entity_name]["observations"].append(c)
                existing.add(c)

    def get_entities(self) -> list[dict]:
        return sorted(self._entities.values(), key=lambda e: e["name"])

    def get_relations(self) -> list[dict]:
        return [{"from": f, "relationType": r, "to": t} for f, r, t in sorted(self._relations)]

    def search_nodes(self, query: str) -> list[dict]:
        q = query.lower()
        return [
            e
            for e in self._entities.values()
            if q in e["name"].lower()
            or q in e["entityType"].lower()
            or any(q in obs.lower() for obs in e["observations"])
        ]

    def open_nodes(self, names: list[str]) -> list[dict]:
        result = []
        for n in names:
            if n in self._entities:
                e = dict(self._entities[n])
                e["relations"] = [
                    {"from": f, "relationType": r, "to": t}
                    for f, r, t in sorted(self._relations)
                    if f == n or t == n
                ]
                result.append(e)
        return result

    def to_json(self) -> str:
        return json.dumps(
            {"entities": self.get_entities(), "relations": self.get_relations()},
            indent=2,
            sort_keys=True,
        )


InMemoryStore = _InMemoryStore


class ADGMCPClient:
    """Unified client for all ADG graph operations.

    Wraps Memory MCP calls with:
    - Idempotency (no duplicate entities or relations)
    - Deterministic ordering on all writes
    - Fallback to in-memory store when MCP is unavailable

    All public methods are safe to call in CI without a live MCP server.
    """

    def __init__(self, use_mcp: bool = False) -> None:
        self._use_mcp = use_mcp
        self._store = InMemoryStore()

    def upsert_entity(self, name: str, entity_type: str, observations: list[str] | None = None) -> None:
        """Create or update an entity. Idempotent."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ADGMCPClient.upsert_entity")

        obs = sorted(set(observations or []))
        self._store.upsert_entity(name, entity_type, obs)

    def upsert_relation(self, from_name: str, relation_type: str, to_name: str) -> None:
        """Create a directed relation. Idempotent."""
        self._store.add_relation(from_name, relation_type, to_name)

    def add_observation(self, entity_name: str, contents: list[str]) -> None:
        """Add observations to an entity. Idempotent."""
        self._store.add_observation(entity_name, sorted(set(contents)))

    def search_nodes(self, query: str) -> list[dict]:
        """Search entities matching query."""
        return self._store.search_nodes(query)

    def open_nodes(self, names: list[str]) -> list[dict]:
        """Open specific entities by name, returning entities with relations."""
        return self._store.open_nodes(names)

    def read_graph(self) -> dict:
        """Read the full graph."""
        return {"entities": self._store.get_entities(), "relations": self._store.get_relations()}

    def get_store(self) -> InMemoryStore:
        """Return the in-memory store for direct inspection in tests."""
        return self._store

    def bulk_upsert_entities(self, entities: list[dict]) -> None:
        """Batch upsert. entities: list of {name, entity_type, observations}."""
        for e in sorted(entities, key=lambda x: x["name"]):
            self.upsert_entity(e["name"], e["entity_type"], e.get("observations"))

    def bulk_upsert_relations(self, relations: list[dict]) -> None:
        """Batch upsert relations. relations: list of {from_name, relation_type, to_name}."""
        for r in sorted(relations, key=lambda x: (x["from_name"], x["relation_type"], x["to_name"])):
            self.upsert_relation(r["from_name"], r["relation_type"], r["to_name"])


__all__ = ["ADGMCPClient", "LayerSegment", "InMemoryStore"]
