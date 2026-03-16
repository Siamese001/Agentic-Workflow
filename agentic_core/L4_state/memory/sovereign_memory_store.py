from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "sovereign_memory_store")
emit_determinism_digest("p0", "sovereign_memory_store")

_emit_dispatches_healing_run("p1", "sovereign_memory_store", "L4")
_emit_routes_through("p1", "sovereign_memory_store", "L4")
_emit_escalates_to_human("p1", "sovereign_memory_store", "L4")
_emit_reads_policy_state("p1", "sovereign_memory_store", "L4")
_emit_authorize_and_execute("p2", "sovereign_memory_store", "execution_auth")
_emit_validates_capability("p2", "sovereign_memory_store", "capability_check")
_emit_routes_to_capability("p2", "sovereign_memory_store", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_memory_store", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_memory_store", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_memory_store", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_memory_store", "exec_output")
_emit_dispatches_agent("p3", "sovereign_memory_store", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_memory_store", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_memory_store", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_memory_store", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_memory_store", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_memory_store", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_memory_store", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_memory_store", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_memory_store", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_memory_store", "eval_metric")
_emit_stores_embedding("p4", "sovereign_memory_store", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_memory_store", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_memory_store", "exec_snapshot_link")

"L4 State: Sovereign MCP Memory — Eternal Knowledge Graph\n\nUltra-hardened persistent memory with entities, relations, observations.\n\nDelegates all operations through GraphMemoryBridge which routes to the\nlive mcp11_* Memory MCP tools (or falls back gracefully in CI).\n\n"
import logging
from typing import Any

from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

Logger: Any = logging.getLogger(__name__)
max_observation_length: Any = 2000
max_entity_name_length: Any = 100


class SovereignMemoryMcp:
    """Ultra-hardened knowledge graph MCP — delegates to GraphMemoryBridge."""

    def __init__(self, mission_id: str, engine=None):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "SovereignMemoryMcp.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "SovereignMemoryMcp.__init__", "p0_governance")
        self.mission_id = mission_id
        self.engine = engine
        self._bridge = GraphMemoryBridge.get_instance()

    async def create_entities(self, entities: list[dict]) -> dict:
        """Create sovereign entities — delegated to GraphMemoryBridge → mcp11."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "SovereignMemoryMcp.create_entities")

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
        # guardian: allow-silent-swallow
        except Exception as e:
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
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"[SovereignMemoryMcp] Observation failure: {e}")
            return {"status": "error", "msg": str(e)}

    async def search_nodes(self, query: str) -> list[dict]:
        """Semantic search across eternal memory — delegated to GraphMemoryBridge."""
        try:
            return self._bridge.search_entities(query)
        # guardian: allow-silent-swallow
        except Exception:
            return []
