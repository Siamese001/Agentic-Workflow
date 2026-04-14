"""Memory MCP persistence integration for ADG generation."""

from __future__ import annotations

import re as _re


def _persist_adg_to_memory(result, artifact, snapshot, graph_diff, routing_summary, ts: str) -> None:
    """Persist key ADG signals to Memory MCP knowledge graph via ADGMemoryAdapter."""
    try:
        from agentic_core.adg.adapters.ADGMemoryAdapter import get_adapter

        adapter = get_adapter()
    except (ImportError, AttributeError, RuntimeError) as e:
        print(f"[ADG] Memory MCP unavailable — skipping persistence: {e}")
        return

    diff_edges = 0
    if graph_diff and hasattr(graph_diff, "summary"):
        summary = graph_diff.summary or ""
        m = _re.search(r"([+-]\d+)\s*edges", summary)
        if m:
            diff_edges = int(m.group(1))

    try:
        adapter.ingest_snapshot(result, ts, diff_edges=diff_edges)
    except (ValueError, TypeError, AttributeError, RuntimeError, OSError) as e:
        print(f"[ADG] Memory MCP: ingest_snapshot failed: {e}")
        return

    result_edges = getattr(result, "edges", []) or []
    violation_edges = [e for e in result_edges if getattr(e, "relation_type", None) == "violates"]
    total_violations = len(violation_edges)
    by_severity = routing_summary.get("by_severity", {}) if isinstance(routing_summary, dict) else {}
    critical_count = by_severity.get("critical", 0) if isinstance(by_severity, dict) else 0
    print(
        f"[ADG] Memory MCP: persisted snapshot + layers + hotspots + {min(total_violations, 50)}/{total_violations} violations (critical={critical_count})",
    )
