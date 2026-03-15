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
from typing import TYPE_CHECKING, Any

from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

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
        import uuid  # noqa: PLC0415

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


def get_adapter() -> ADGMemoryAdapter:
    """Return a process-global ADGMemoryAdapter instance."""
    global _adapter
    if _adapter is None:
        _adapter = ADGMemoryAdapter()
    return _adapter


_adapter: ADGMemoryAdapter | None = None

__all__ = ["ADGMemoryAdapter", "get_adapter"]
