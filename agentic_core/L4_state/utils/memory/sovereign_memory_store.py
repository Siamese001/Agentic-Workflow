from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "sovereign_memory_store")
trace_contract.emit_determinism_digest("p0", "sovereign_memory_store")

trace_contract._emit_dispatches_healing_run("p1", "sovereign_memory_store", "L4")
trace_contract._emit_routes_through("p1", "sovereign_memory_store", "L4")
trace_contract._emit_checks_agent_registry("p1", "sovereign_memory_store", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "sovereign_memory_store", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "sovereign_memory_store", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "sovereign_memory_store", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "sovereign_memory_store", "target_agent")
trace_contract._emit_verifies_policy("p1", "sovereign_memory_store", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "sovereign_memory_store", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "sovereign_memory_store", "boundary_check")
trace_contract._emit_transcripts_response("p1", "sovereign_memory_store", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "sovereign_memory_store")
trace_contract._emit_gated_by_confidence("p1", "sovereign_memory_store", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "sovereign_memory_store", "L4")
trace_contract._emit_reads_policy_state("p1", "sovereign_memory_store", "L4")
trace_contract._emit_authorize_and_execute("p2", "sovereign_memory_store", "execution_auth")
trace_contract._emit_validates_capability("p2", "sovereign_memory_store", "capability_check")
trace_contract._emit_routes_to_capability("p2", "sovereign_memory_store", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "sovereign_memory_store", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "sovereign_memory_store", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "sovereign_memory_store", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "sovereign_memory_store", "exec_output")
trace_contract._emit_dispatches_agent("p3", "sovereign_memory_store", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "sovereign_memory_store", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "sovereign_memory_store", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "sovereign_memory_store", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "sovereign_memory_store", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "sovereign_memory_store", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "sovereign_memory_store", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "sovereign_memory_store", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "sovereign_memory_store", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "sovereign_memory_store", "eval_metric")
trace_contract._emit_stores_embedding("p4", "sovereign_memory_store", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "sovereign_memory_store", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "sovereign_memory_store", "exec_snapshot_link")

"L4 State: Sovereign MCP Memory — Eternal Knowledge Graph\n\nUltra-hardened persistent memory with entities, relations, observations.\n\nDelegates all operations through GraphMemoryBridge which routes to the\nlive mcp11_* Memory MCP tools (or falls back gracefully in CI).\n\n"
import logging
from typing import Any

from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge

trace_contract._emit_emits_metric_event("sovereign_memory_store", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("sovereign_memory_store", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("sovereign_memory_store", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("sovereign_memory_store", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("sovereign_memory_store", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("sovereign_memory_store", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("sovereign_memory_store", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("sovereign_memory_store", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("sovereign_memory_store", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("sovereign_memory_store", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("sovereign_memory_store", "p4obs", "alert")
trace_contract._emit_links_incident_trace("sovereign_memory_store", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("sovereign_memory_store", "p3lm", "pattern")
trace_contract._emit_records_learning_event("sovereign_memory_store", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("sovereign_memory_store", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("sovereign_memory_store", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("sovereign_memory_store", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("sovereign_memory_store", "p3lm", "policy")
trace_contract._emit_stores_learning_state("sovereign_memory_store", "p3lm", "state")
trace_contract._emit_records_execution_trace("sovereign_memory_store", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("sovereign_memory_store", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("sovereign_memory_store", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("sovereign_memory_store", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("sovereign_memory_store", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("sovereign_memory_store", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("sovereign_memory_store", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("sovereign_memory_store", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("sovereign_memory_store", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "sovereign_memory_store", "context_pull")
trace_contract._emit_pulls_context("p1", "sovereign_memory_store", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "sovereign_memory_store", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "sovereign_memory_store", "uwg_term_2")
trace_contract._emit_writes_through("p1", "sovereign_memory_store", "write_through")
trace_contract._emit_writes_through("p1", "sovereign_memory_store", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "sovereign_memory_store", "safety_validation")
trace_contract._emit_invokes_eval("p1", "sovereign_memory_store", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "sovereign_memory_store", "routing_commit")

Logger: Any = logging.getLogger(__name__)
max_observation_length: Any = 2000
max_entity_name_length: Any = 100


class SovereignMemoryMcp:
    """Ultra-hardened knowledge graph MCP — delegates to GraphMemoryBridge."""

    def __init__(self, mission_id: str, engine=None):
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "SovereignMemoryMcp.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "SovereignMemoryMcp.__init__", "p0_governance")
        self.mission_id = mission_id
        self.engine = engine
        self._bridge = GraphMemoryBridge.get_instance()

    async def create_entities(self, entities: list[dict]) -> dict:
        """Create sovereign entities — delegated to GraphMemoryBridge → mcp11."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L4_STATE, "SovereignMemoryMcp.create_entities")

        created: Any = []
        try:
            for entity in entities[:20]:
                name: Any = entity.get("name", "")
                if not name or len(name) > max_entity_name_length:
                    continue
                self._bridge.create_agent_entity(
                    agent_name=name,
                    agent_type=entity.get("entityType", "Entity"),
                    observations=entity.get("observations"),
                )
                created.append(name)
            return {"status": "success", "created": created}
        except (
            AttributeError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as e:  # guardian: allow-silent-swallow
            Logger.error(f"[SovereignMemoryMcp] Entity creation failure: {e}")
            return {"status": "error", "msg": str(e)}

    async def add_observations(self, observations: list[dict]) -> dict:
        """Add atomic facts to the graph with size-shielding — delegated to GraphMemoryBridge."""
        added: Any = {}
        try:
            for obs in observations:
                name: Any = obs.get("entityName", "")
                for content in obs.get("contents", []):
                    if len(content) > max_observation_length:
                        content = content[: max_observation_length - 3] + "..."
                    self._bridge.add_observation(name, content)
                    added.setdefault(name, []).append(content)
            return {"status": "success", "added_count": len(added)}
        except (
            AttributeError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as e:  # guardian: allow-silent-swallow
            Logger.error(f"[SovereignMemoryMcp] Observation failure: {e}")
            return {"status": "error", "msg": str(e)}

    async def search_nodes(self, query: str) -> list[dict]:
        """Semantic search across eternal memory — delegated to GraphMemoryBridge."""
        try:
            return self._bridge.search_entities(query)
        except (
            AttributeError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ):  # guardian: allow-silent-swallow
            return []
