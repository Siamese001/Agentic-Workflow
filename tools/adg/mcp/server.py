"""ADG MCP Server - SQLite-first with optional Redis cache.

This server keeps SQLite as the mandatory canonical source and Redis as an
optional read-through cache. The transport layer stays intentionally thin, with
runtime lifecycle and tool behavior split into dedicated helper modules.
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


from typing import Any

from tools.mcp.mcp_bootstrap import create_mcp_server, mcp_process_identity
from tools.adg.mcp.runtime import LOG
from tools.adg.mcp import tool_handlers as handlers

LOG.info("Creating FastMCP instance...")
# MCP-4 (2026-04-22): unified through create_mcp_server() which applies
# standardized logging, TOKENIZERS_PARALLELISM, PYTHONUNBUFFERED, and any
# future worker-cap config. Equivalent to raw FastMCP(...) for current
# FastMCP versions.
mcp = create_mcp_server(
    "adg-sqlite",
    (
        "ADG SQLite-first MCP server. SQLite is canonical source, "
        "Redis is optional cache. Use adg_health first to check status."
    ),
)
LOG.info("FastMCP instance created")
_log = LOG


def _init_service() -> None:
    """Eagerly initialize the singleton runtime service for legacy launchers."""
    runtime = handlers.runtime
    _ = runtime.service


@mcp.tool()
def adg_health() -> dict[str, Any]:
    """PRIMARY health check - always call this first.

    Returns mode, sqlite status, redis status, cache capability,
    schema version, and ADG snapshot ID.
    """
    return handlers.adg_health()


@mcp.tool()
def adg_status() -> dict[str, Any]:
    """Get ADG snapshot status.

    Returns timestamp, node_count, edge_count, and sqlite_path.
    """
    return handlers.adg_status()


@mcp.tool()
def adg_node(node_id: str) -> dict[str, Any]:
    """Get node by ID.

    Tries Redis cache first with a short timeout, then falls back to SQLite.
    """
    return handlers.adg_node(node_id)


@mcp.tool()
def adg_nodes_by_layer(layer: str, limit: int = 100) -> dict[str, Any]:
    """Get nodes by layer.

    This is a SQLite-only query because list results are not cached in Redis.
    """
    return handlers.adg_nodes_by_layer(layer, limit)


@mcp.tool()
def adg_nodes_by_file(file_path: str, limit: int = 100) -> dict[str, Any]:
    """Get nodes by file path.

    Tries Redis cache first with lazy warm on miss, then falls back to SQLite.
    """
    return handlers.adg_nodes_by_file(file_path, limit)


@mcp.tool()
def adg_find_node(name: str, limit: int = 10) -> dict[str, Any]:
    """Find nodes by adg_name.

    Resolves a human-readable ADG name to a node id without needing the opaque
    integer id up front.
    """
    return handlers.adg_find_node(name, limit)


@mcp.tool()
def adg_edge_fanout(src_id: str, relation_type: str, limit: int = 30) -> dict[str, Any]:
    """Get outgoing edges from src_id via relation_type."""
    return handlers.adg_edge_fanout(src_id, relation_type, limit)


@mcp.tool()
def adg_edge_fanin(tgt_id: str, relation_type: str, limit: int = 30) -> dict[str, Any]:
    """Get incoming edges to tgt_id via relation_type."""
    return handlers.adg_edge_fanin(tgt_id, relation_type, limit)


@mcp.tool()
def adg_violations(limit: int = 100) -> dict[str, Any]:
    """Get anti-pattern violations.

    This is a SQLite-only query.
    """
    return handlers.adg_violations(limit)


@mcp.tool()
def adg_p0_wave_plan(limit: int = 100) -> dict[str, Any]:
    """Build a wave-based remediation plan for current P0 defects."""
    return handlers.adg_p0_wave_plan(limit)


@mcp.tool()
def adg_close_connections() -> dict[str, Any]:
    """Close ADG backend connections to release SQLite file locks.

    Use this before running full ADG generation when lock checks report files
    in use.
    """
    return handlers.adg_close_connections()


@mcp.tool()
def adg_reopen_connections() -> dict[str, Any]:
    """Reopen ADG backend connections after adg_close_connections()."""
    return handlers.adg_reopen_connections()


@mcp.tool()
def adg_runtime_info() -> dict[str, Any]:
    """Return process-level runtime identity for verifying restarts.

    A changed pid or nonce after a Windsurf MCP restart proves a fresh process
    is serving. Use adg_reload for SQLite snapshot refresh only.
    """
    return handlers.adg_runtime_info()


@mcp.tool()
def adg_process_identity() -> dict[str, Any]:
    """Return process identity for Codex MCP attached-PID cleanup proof."""
    return {"status": "ok", "process": mcp_process_identity("adg_sqlite")}


@mcp.tool()
def adg_reload() -> dict[str, Any]:
    """Auto-reload ADG SQLite snapshot if a newer file exists on disk.

    This repoints the connection to the latest snapshot file. It does not
    restart the server process or reload edited source code.
    """
    return handlers.adg_reload()


# ---------------------------------------------------------------------------
# W3 P3.3 — graph-layer primitives (MV / semantic edges / P-views)
# Plan: docs/archive/windsurf/legacy-tree/plans/adg-three-bucket-unified-c4f8e2.md
# ---------------------------------------------------------------------------


@mcp.tool()
def adg_mv_hotspot_centrality(limit: int = 50) -> dict[str, Any]:
    """Top-N structurally central nodes from `mv_hotspot_centrality`.

    Returns rows ordered DESC by degree_centrality, then fan_in. Each row
    carries node_id, adg_name, layer, resolved_path, fan_in, fan_out,
    degree, betweenness_approx, degree_centrality. Use this to drive
    refactor target ranking per constitutional §22.
    """
    return handlers.adg_mv_hotspot_centrality(limit)


@mcp.tool()
def adg_blast_radius(node_id: str, hops: int = 2) -> dict[str, Any]:
    """Blast-radius (downstream impact) for a node, up to `hops` hops out.

    Sources from the graph projection (Cypher-style overlay) when available;
    falls back to direct SQL when projection is missing. Use this for
    refactor-impact estimation and wave ordering.
    """
    return handlers.adg_blast_radius(node_id, hops)


@mcp.tool()
def adg_semantic_fanout(
    src_id: str, relation_type: str, limit: int = 30
) -> dict[str, Any]:
    """Outgoing edges via a canonical semantic relation type.

    Valid relation_type values: flows_to, writes_to, reads_from,
    emits_side_effect, controls_flow, resolves_callsite. Use
    `adg_edge_fanout` for `imports` and other non-semantic edges.
    """
    return handlers.adg_semantic_fanout(src_id, relation_type, limit)


@mcp.tool()
def adg_p_view_query(view_name: str, limit: int = 100) -> dict[str, Any]:
    """Return up to `limit` rows from a canonical P-view (`v_p[0-3]_<name>`).

    P-views are pre-classified architectural concerns: P0=critical layer
    breaks, P1=mis-layered/zero-caller infra, P2=duplicated/dormant,
    P3=isolated experimental. Names are validated against the
    `v_p[0-3]_<word>` whitelist + sqlite_master existence check before
    SELECT — invalid view_name returns an error response with the list
    of available P-views.
    """
    return handlers.adg_p_view_query(view_name, limit)


if __name__ == "__main__":
    # Guard against Windsurf double-spawn: two adg_sqlite processes would
    # both hold SQLite read locks on the ADG snapshot and can deadlock when
    # one tries to rotate snapshots. Added 2026-04-22 MCP standardization.
    # Bugfix 2026-04-23: pass BOTH dot-separated and slash-separated markers.
    # This server is invoked via `python -u -m tools.adg.mcp.server` (dots)
    # so the original slash-only marker never matched any cmdline and the
    # guard silently no-oped, letting stale siblings survive window reloads.
    from tools.mcp.mcp_bootstrap import guard_single_instance

    guard_single_instance(
        ("tools.adg.mcp.server", "tools/adg/mcp/server"),
        skip_env="ADG_SKIP_ZOMBIE_KILL",
    )
    mcp.run(transport="stdio")
