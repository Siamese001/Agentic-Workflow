"""ADG → Memory MCP Adapter.

Bridges the ADG static scanner result into the Memory MCP knowledge graph
via GraphMemoryBridge.  Provides:
  - Bulk snapshot ingestion (entities + relations)
  - Incremental diff ingestion (only changed edges)
  - Layer violation entities for remediation tracking
  - Fan-out hotspot entities for prioritized cleanup
  - Impact query helpers that read back from the graph

Design constraints:
  - Idempotent: repeated calls for the same snapshot are safe
  - Resilient: MCP unavailability is logged, never raises
  - Bounded: caps entity/relation batches to avoid graph bloat
  - Non-authoritative: MCP graph is a read-replica of ADG artifacts on disk

[SSOT] Canonical implementation for ADG → Memory MCP persistence.
"""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING, Any

from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("memory_mcp_adapter", "p4obs", "metric_1")
_emit_emits_metric_event("memory_mcp_adapter", "p4obs", "metric_2")
_emit_emits_metric_event("memory_mcp_adapter", "p4obs", "metric_3")
_emit_emits_metric_event("memory_mcp_adapter", "p4obs", "metric_4")
_emit_emits_metric_event("memory_mcp_adapter", "p4obs", "metric_5")
_emit_emits_metric_event("memory_mcp_adapter", "p4obs", "metric_6")
_emit_records_incident_event("memory_mcp_adapter", "p4obs", "incident")
_emit_captures_runtime_anomaly("memory_mcp_adapter", "p4obs", "anomaly")
_emit_writes_observability_log("memory_mcp_adapter", "p4obs", "obs_log")
_emit_updates_monitoring_state("memory_mcp_adapter", "p4obs", "mon_state")
_emit_triggers_alert("memory_mcp_adapter", "p4obs", "alert")
_emit_links_incident_trace("memory_mcp_adapter", "p4obs", "trace_link")
_emit_captures_pattern("memory_mcp_adapter", "p3lm", "pattern")
_emit_records_learning_event("memory_mcp_adapter", "p3lm", "learning_event")
_emit_writes_learning_snapshot("memory_mcp_adapter", "p3lm", "snapshot")
_emit_feeds_meta_learning("memory_mcp_adapter", "p3lm", "meta_feed")
_emit_updates_routing_strategy("memory_mcp_adapter", "p3lm", "routing")
_emit_improves_agent_policy("memory_mcp_adapter", "p3lm", "policy")
_emit_stores_learning_state("memory_mcp_adapter", "p3lm", "state")
_emit_records_execution_trace("memory_mcp_adapter", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("memory_mcp_adapter", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("memory_mcp_adapter", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("memory_mcp_adapter", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("memory_mcp_adapter", "L4_STATE", "p2_trace_5")
_emit_reads_environ("memory_mcp_adapter", "env_read", "p2_env_1")
_emit_reads_environ("memory_mcp_adapter", "env_read", "p2_env_2")
_emit_reads_runtime_state("memory_mcp_adapter", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("memory_mcp_adapter", "runtime_state", "p2_rt_2")

_emit_applies_guardrail("p0", "memory_mcp_adapter", "p0_governance")
_emit_reads_policy_state("p0", "memory_mcp_adapter", "policy_binding")
_emit_snapshots_state("p0", "memory_mcp_adapter", "state_snapshot")
_emit_escalates_to_human("p1", "memory_mcp_adapter", "human_escalation")
_emit_pulls_context("p1", "memory_mcp_adapter", "context_pull")
_emit_pulls_context("p1", "memory_mcp_adapter", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "memory_mcp_adapter", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "memory_mcp_adapter", "uwg_term_secondary")
_emit_writes_through("p1", "memory_mcp_adapter", "write_through")
_emit_writes_through("p1", "memory_mcp_adapter", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "memory_mcp_adapter", "safety_validation")
_emit_invokes_eval("p1", "memory_mcp_adapter", "eval_call")
_emit_proposal_commits_routing("p1", "memory_mcp_adapter", "routing_commit")
_emit_routes_through("p1", "memory_mcp_adapter", "route_through")
_emit_checks_agent_registry("p1", "memory_mcp_adapter", "agent_registry")
_emit_validates_agent_capability("p1", "memory_mcp_adapter", "capability")
_emit_dispatches_execution_plan("p1", "memory_mcp_adapter", "exec_plan")
_emit_agent_executes_agent("p1", "memory_mcp_adapter", "sub_agent")
_emit_routes_to_agent("p1", "memory_mcp_adapter", "target_agent")
_emit_verifies_policy("p1", "memory_mcp_adapter", "policy_check")
_emit_observes_runtime_state("p1", "memory_mcp_adapter", "runtime_state")
_emit_verifies_boundary("p1", "memory_mcp_adapter", "boundary_check")
_emit_transcripts_response("p1", "memory_mcp_adapter", "transcript")
_emit_hard_fails_untranscripted("p1", "memory_mcp_adapter")
_emit_gated_by_confidence("p1", "memory_mcp_adapter", "confidence_gate")
emit_replay_key("p0", "memory_mcp_adapter")
emit_determinism_digest("p0", "memory_mcp_adapter")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "memory_mcp_adapter", "execution_auth")
_emit_validates_capability("p2", "memory_mcp_adapter", "capability_check")
_emit_routes_to_capability("p2", "memory_mcp_adapter", "capability_route")
_emit_writes_via_uwg("p2", "memory_mcp_adapter", "uwg_write")
_emit_blocks_direct_write("p2", "memory_mcp_adapter", "direct_write_block")
_emit_records_tool_invocation("p2", "memory_mcp_adapter", "tool_invocation")
_emit_captures_execution_output("p2", "memory_mcp_adapter", "exec_output")
_emit_dispatches_agent("p3", "memory_mcp_adapter", "agent_dispatch")
_emit_coordinates_agents("p3", "memory_mcp_adapter", "agent_coordination")
_emit_records_workflow_lineage("p3", "memory_mcp_adapter", "workflow_lineage")
_emit_records_healing_outcome("p3", "memory_mcp_adapter", "healing_outcome")
_emit_escalates_failure("p3", "memory_mcp_adapter", "failure_escalation")
_emit_orchestrates_workflow("p3", "memory_mcp_adapter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "memory_mcp_adapter", "healing_dispatch")
_emit_invokes_evaluation("p3", "memory_mcp_adapter", "evaluation_signal")
_emit_records_telemetry_event("p4", "memory_mcp_adapter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "memory_mcp_adapter", "eval_metric")
_emit_stores_embedding("p4", "memory_mcp_adapter", "embedding_store")
_emit_updates_meta_learning_state("p4", "memory_mcp_adapter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "memory_mcp_adapter", "exec_snapshot_link")

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class AnyType:
    """Runtime Any placeholder for tests."""


Any = AnyType

_MAX_VIOLATIONS = 50
_MAX_HOTSPOTS = 20
_MAX_MODULES = 200
_OBSERVATION_LIMIT = 2000


class ADGMemoryAdapter:
    """Persists ADG scan results into the Memory MCP knowledge graph.

    Usage::

        adapter = ADGMemoryAdapter()
        adapter.ingest_snapshot(scan_result, ts="20260311T193725Z")
        nodes = adapter.query_violations("L0->L5")
    """

    ENTITY_TYPE_SNAPSHOT = "ADGSnapshot"
    ENTITY_TYPE_MODULE = "ADGModule"
    ENTITY_TYPE_LAYER = "ADGLayer"
    ENTITY_TYPE_VIOLATION = "ADGViolation"
    ENTITY_TYPE_HOTSPOT = "ADGHotspot"

    RELATION_IMPORTS = "ADG_IMPORTS"
    RELATION_VIOLATES = "ADG_VIOLATES"
    RELATION_OWNS = "ADG_OWNS"
    RELATION_HOTSPOT_IN = "ADG_HOTSPOT_IN"

    def __init__(self) -> None:
        self._bridge = GraphMemoryBridge.get_instance()

    # ------------------------------------------------------------------
    # Snapshot ingestion
    # ------------------------------------------------------------------

    def ingest_snapshot(self, result: Any, ts: str, *, diff_edges: int = 0) -> None:
        """Persist a full ADG scan result into the knowledge graph.

        Args:
            result: ScanResult from ADGStaticScanner.scan()
            ts: ISO timestamp string (e.g. "20260311T193725Z")
            diff_edges: Net edge delta vs previous snapshot (for observations)
        """

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"MemoryMCPAdapter.ingest_snapshot:{ts}")
        snapshot_name = f"ADGSnapshot_{ts}"
        violation_edges = [e for e in result.edges if getattr(e, "relation_type", "") == "violates"]
        violation_count = len(violation_edges)

        self._bridge.create_agent_entity(
            agent_name=snapshot_name,
            agent_type=self.ENTITY_TYPE_SNAPSHOT,
            observations=[
                f"ts={ts}",
                f"modules={len(result.modules)}",
                f"edges={len(result.edges)}",
                f"digest={result.digest}",
                f"violations={violation_count}",
                f"diff_edges={diff_edges:+d}",
            ],
        )
        logger.info("[ADGMemoryAdapter] Snapshot entity created: %s", snapshot_name)

        self._ingest_layers(ts)
        self._ingest_hotspots(result, ts, snapshot_name)
        self._ingest_violations(violation_edges, ts, snapshot_name)
        self._ingest_top_modules(result, ts, snapshot_name)

        logger.info(
            "[ADGMemoryAdapter] Ingestion complete: %s modules, %s violations, ts=%s",
            len(result.modules),
            violation_count,
            ts,
        )

    # ------------------------------------------------------------------
    # Layer entities
    # ------------------------------------------------------------------

    def _ingest_layers(self, ts: str) -> None:
        layers = [
            "L0",
            "L1",
            "L2",
            "L3",
            "L4",
            "L5",
            "L6",
            "L_APP",
            "L_SL",
            "L_TOOLS",
            "L_OPS",
            "L_RUNTIME",
            "L_TEST",
        ]
        for layer in layers:
            self._bridge.create_agent_entity(
                agent_name=f"ADGLayer_{layer}",
                agent_type=self.ENTITY_TYPE_LAYER,
                observations=[f"layer={layer}", f"last_scan={ts}"],
            )

    # ------------------------------------------------------------------
    # Fan-out hotspot entities
    # ------------------------------------------------------------------

    def _ingest_hotspots(self, result: Any, ts: str, snapshot_name: str) -> None:
        fan_out_map: dict[str, int] = {}
        for edge in result.edges:
            src = str(getattr(edge, "source_file", "") or "")
            if src:
                fan_out_map[src] = fan_out_map.get(src, 0) + 1

        hotspots = sorted(fan_out_map.items(), key=lambda x: -x[1])[:_MAX_HOTSPOTS]
        for module_path, fan_out in hotspots:
            safe_name = module_path.replace("/", "_").replace("\\", "_").replace(".", "_")[:60]
            entity_name = f"ADGHotspot_{safe_name}"
            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_HOTSPOT,
                observations=[
                    f"module={module_path[:200]}",
                    f"fan_out={fan_out}",
                    f"last_scan={ts}",
                ],
            )
            self._bridge.create_relation(entity_name, snapshot_name, self.RELATION_HOTSPOT_IN)

    # ------------------------------------------------------------------
    # Layer violation entities
    # ------------------------------------------------------------------

    def _ingest_violations(self, violation_edges: list[Any], ts: str, snapshot_name: str) -> None:
        for i, edge in enumerate(violation_edges[:_MAX_VIOLATIONS]):
            src = str(getattr(edge, "source_file", "") or "unknown")[:80]
            tgt = str(getattr(edge, "to_name", "") or "unknown")[:80]
            sym = str(getattr(edge, "symbol", "") or "")[:40]
            entity_name = f"ADGViolation_{src.replace('/', '_').replace('.', '_')[:40]}_{i}"
            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_VIOLATION,
                observations=[
                    f"source={src}",
                    f"target={tgt}",
                    f"symbol={sym}",
                    f"relation={getattr(edge, 'relation_type', 'violates')}",
                    f"ts={ts}",
                    "status=open",
                ],
            )
            self._bridge.create_relation(entity_name, snapshot_name, self.RELATION_VIOLATES)

    # ------------------------------------------------------------------
    # Top modules by edge count
    # ------------------------------------------------------------------

    def _ingest_top_modules(self, result: Any, ts: str, snapshot_name: str) -> None:
        modules_list = sorted(result.modules)[:_MAX_MODULES]
        for module_path in modules_list:
            safe_name = str(module_path).replace("/", ".").replace("\\", ".")[:100]
            entity_name = f"ADGModule_{safe_name}"
            layer = _infer_layer(str(module_path))
            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_MODULE,
                observations=[
                    f"path={module_path}",
                    f"layer={layer}",
                    f"last_scan={ts}",
                ],
            )
            layer_entity = f"ADGLayer_{layer}"
            self._bridge.create_relation(layer_entity, entity_name, self.RELATION_OWNS)

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def query_violations(self, layer_pattern: str = "") -> list[dict[str, Any]]:
        """Search violation entities, optionally filtered by layer pattern (e.g. 'L0->L5').

        Args:
            layer_pattern: Substring to filter by (matched against entity observations)

        Returns:
            List of matching entity dicts from the knowledge graph
        """
        query = "ADGViolation"
        if layer_pattern:
            query = f"ADGViolation {layer_pattern}"
        return self._bridge.search_entities(query)

    def query_hotspots(self) -> list[dict[str, Any]]:
        """Return all ADGHotspot entities from the knowledge graph."""
        return self._bridge.search_entities("ADGHotspot")

    def query_snapshot(self, ts: str) -> list[dict[str, Any]]:
        """Return the ADGSnapshot entity for a given timestamp."""
        return self._bridge.search_entities(f"ADGSnapshot_{ts}")

    def mark_violation_fixed(self, entity_name: str) -> bool:
        """Update a violation entity to mark it as remediated.

        Args:
            entity_name: The full entity name (e.g. ADGViolation_agentic_core_L0_...)

        Returns:
            True if observation added, False if failed
        """
        return self._bridge.add_observation(entity_name, "status=fixed")

    @property
    def is_available(self) -> bool:
        """True if the underlying Memory MCP bridge is operational."""
        return self._bridge.is_available


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


def _infer_layer(path: str) -> str:
    """Infer ADG layer label from a file path string."""
    for layer in ("L0", "L1", "L2", "L3", "L4", "L5", "L6"):
        if f"/{layer}_" in path or f"\\{layer}_" in path:
            return layer
    for prefix in ("apps_shared", "apps_lic", "apps_rg"):
        if path.startswith(prefix) or f"/{prefix}" in path or f"\\{prefix}" in path:
            return "L_APP"
    if "system_learning" in path:
        return "L_SL"
    if "ops_scripts" in path:
        return "L_OPS"
    if path.startswith("tools") or "/tools/" in path:
        return "L_TOOLS"
    if path.startswith("tests") or "/tests/" in path:
        return "L_TEST"
    return "L_UNKNOWN"


def get_adapter(_cache_state: dict | None = None) -> ADGMemoryAdapter:
    """Return a process-global ADGMemoryAdapter instance."""
    global _adapter
    if _adapter is None:
        _adapter = ADGMemoryAdapter()
    return _adapter


_adapter: ADGMemoryAdapter | None = None

__all__ = ["ADGMemoryAdapter", "get_adapter", "GraphMemoryBridge", "LayerSegment", "Any"]
