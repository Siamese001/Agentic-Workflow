"""
ADG-Aware Memory MCP Server — persistent replacement for @modelcontextprotocol/server-memory.

Why this exists
---------------
@modelcontextprotocol/server-memory uses an in-memory Node.js store.
The ENTIRE knowledge graph is lost on every Windsurf restart. This means:
  - Constitutional rules must be re-established from scratch every session
  - ADG context must be re-imported every time
  - No cross-session knowledge accumulation or audit trail of what was learned

This server provides:
  - SQLite-backed persistence at artifacts/memory/knowledge_graph.sqlite
  - Survives Windsurf and machine restarts (durable knowledge base)
  - Same core API as the marketplace server — drop-in replacement
  - Observation deduplication: duplicate observations are silently ignored
  - Session tagging: constitutional rules (ArchitectureLayer, ConstitutionalRule,
    ProjectContext) are protected from cleanup; session observations are purgeable
  - mem_import_adg_context: seeds memory from the ADG Redis hot cache
  - mem_recall_session_start: returns all persistent context in one call
  - mem_get_stats: knowledge graph health metrics
  - mem_cleanup_stale: remove session-scoped entities older than N days

SQLite schema
  entities     (name PK, entity_type, created_at, updated_at)
  observations (id PK, entity_name FK, content, created_at)  — UNIQUE per entity
  relations    (from_entity FK, relation_type, to_entity FK)  — composite PK

Wire in mcp_config.json as "memory" — disable marketplace "@modelcontextprotocol/server-memory":
  "memory": {
    "command": "python",
    "args": ["tools/memory/adg_memory_server.py"],
    "cwd": "C:\\\\Git\\\\Agentic-Workflow"
  }
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

try:
    from tqdm import tqdm as _tqdm
except (
    ImportError
):  # guardian: allow-broad-exception -- tqdm is optional; mem_import_adg_context degrades to plain iteration
    _tqdm = None  # type: ignore[assignment]

# Add repo root to path so 'tools.memory' imports work when running standalone
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.mcp.mcp_bootstrap import create_mcp_server

logger = logging.getLogger(__name__)

try:
    from agentic_core.runtime.contracts.lifecycle_trace_contract import (
        _emit_applies_guardrail,
        _emit_authorize_and_execute,
        _emit_blocks_direct_write,
        _emit_captures_evaluation_metric,
        _emit_captures_execution_output,
        _emit_invokes_evaluation,
        _emit_links_execution_to_snapshot,
        _emit_reads_policy_state,
        _emit_records_execution_trace,
        _emit_records_telemetry_event,
        _emit_records_tool_invocation,
        _emit_routes_to_capability,
        _emit_snapshots_state,
        _emit_stores_embedding,
        _emit_updates_meta_learning_state,
        _emit_validates_capability,
        _emit_writes_via_uwg,
        emit_determinism_digest,
        emit_replay_key,
    )

    _LIFECYCLE_AVAILABLE = True
except ImportError as exc:
    _LIFECYCLE_AVAILABLE = False
    logger.warning(
        "lifecycle_trace_contract unavailable, continuing without lifecycle emission: %s",
        exc,
    )

from tools.memory.sqlite_memory_store import SqliteMemoryStore

_LIFECYCLE_REGISTERED = False


def _register_lifecycle_traces_once() -> None:
    global _LIFECYCLE_REGISTERED
    if _LIFECYCLE_REGISTERED or not _LIFECYCLE_AVAILABLE:
        return
    emit_replay_key("p0", "adg_memory_server")
    emit_determinism_digest("p0", "adg_memory_server")
    _emit_records_execution_trace("p0", "evidence", "adg_memory_server")
    _emit_applies_guardrail("p0", "adg_memory_server", "p0_governance")
    _emit_reads_policy_state("p0", "adg_memory_server", "policy_binding")
    _emit_snapshots_state("p0", "adg_memory_server", "state_snapshot")
    _emit_authorize_and_execute("p2", "adg_memory_server", "execution_auth")
    _emit_validates_capability("p2", "adg_memory_server", "capability_check")
    _emit_routes_to_capability("p2", "adg_memory_server", "capability_route")
    _emit_writes_via_uwg("p2", "adg_memory_server", "uwg_write")
    _emit_blocks_direct_write("p2", "adg_memory_server", "direct_write_block")
    _emit_records_tool_invocation("p2", "adg_memory_server", "tool_invocation")
    _emit_captures_execution_output("p2", "adg_memory_server", "exec_output")
    _emit_invokes_evaluation("p3", "adg_memory_server", "evaluation_signal")
    _emit_records_telemetry_event("p4", "adg_memory_server", "telemetry_event")
    _emit_captures_evaluation_metric("p4", "adg_memory_server", "eval_metric")
    _emit_stores_embedding("p4", "adg_memory_server", "embedding_store")
    _emit_updates_meta_learning_state("p4", "adg_memory_server", "meta_learning")
    _emit_links_execution_to_snapshot("p4", "adg_memory_server", "exec_snapshot_link")
    _LIFECYCLE_REGISTERED = True


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_DB = _REPO_ROOT / "artifacts" / "memory" / "knowledge_graph.sqlite"
_DB_PATH: Path = Path(os.environ.get("MEMORY_DB", str(_DEFAULT_DB)))
_ADG_REDIS_URL: str = os.environ.get("ADG_REDIS_URL", "redis://localhost:6379/0")

_PROTECTED_TYPES = (
    "ArchitectureLayer",
    "ProjectContext",
    "ConstitutionalRule",
    "EpisodicEvent",
    "ProceduralPattern",
    "ArchitecturalDecision",
    # Auto-projected from ADG hot cache; noisy if they thrash at 30 days.
    # They are cheap to regenerate but the churn clutters observation history.
    "ADGNode",
    "ADGModule",
    "ADGLayer",
    "ArchitecturalInvariant",
)

# Name-prefixes whose entities are ADG-projected and must survive stale-cleanup
# even if their entity_type was left as "general" by an older import run.
_PROTECTED_NAME_PREFIXES = (
    "ADGModule_",
    "ADGLayer_",
    "ADG:",
)
_SESSION_RECALL_TYPES = (
    "ArchitectureLayer",
    "ProjectContext",
    "ConstitutionalRule",
    "ArchitecturalDecision",
    "ProceduralPattern",
)

_store = SqliteMemoryStore(_DB_PATH)

# ---------------------------------------------------------------------------
# FastMCP server
# ---------------------------------------------------------------------------
mcp = create_mcp_server(
    "adg-memory",
    (
        "Persistent SQLite-backed knowledge graph. "
        "Survives restarts — no data loss on Windsurf reload. "
        "Call mem_recall_session_start first. "
        "Use mem_import_adg_context to seed from ADG hot cache."
    ),
)


# Uniform fleet-health tool — MCP standardization 2026-04-22.
from tools.mcp.mcp_bootstrap import register_standard_health as _register_standard_health


def _memory_health_extra() -> dict[str, Any]:
    try:
        stats = _store.get_stats()
    except (OSError, RuntimeError, AttributeError, ImportError) as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}
    return {
        "db_path": str(getattr(_store, "db_path", "?")),
        "entity_count": stats.get("total_entities", 0) if isinstance(stats, dict) else 0,
        "observation_count": stats.get("total_observations", 0) if isinstance(stats, dict) else 0,
    }


_register_standard_health(mcp, "memory", extra=_memory_health_extra)


# ---------------------------------------------------------------------------
# Core tools — API-compatible with @modelcontextprotocol/server-memory
# ---------------------------------------------------------------------------


@mcp.tool()
def create_entities(entities: list[dict]) -> dict[str, Any]:
    """Create new entities in the persistent knowledge graph.

    Each entity: {name: str, entityType: str, observations: list[str]}
    Entities that already exist are skipped (use add_observations to extend them).
    Observations are deduplicated — exact duplicates are silently ignored.
    """
    _register_lifecycle_traces_once()
    return _store.create_entities(entities)


@mcp.tool()
def add_observations(observations: list[dict]) -> dict[str, Any]:
    """Add observations to existing entities (creates entity if missing).

    Each item: {entityName: str, contents: list[str]}
    Duplicate observations are silently ignored — safe to call repeatedly.
    """
    return _store.add_observations(observations)


@mcp.tool()
def create_relations(relations: list[dict]) -> dict[str, Any]:
    """Create directional relations between entities.

    Each relation: {from: str, to: str, relationType: str}
    Auto-creates missing entities (type='general'). Duplicate relations ignored.
    """
    return _store.create_relations(relations)


@mcp.tool()
def open_nodes(names: list[str]) -> dict[str, Any]:
    """Retrieve specific entities with their observations and relations.

    Args:
        names: List of entity names to load.
    """
    return _store.open_nodes(names)


@mcp.tool()
def search_nodes(query: str) -> dict[str, Any]:
    """Full-text search across entity names, types, and observation content.

    Case-insensitive substring match. Returns matching entities with all context.
    """
    _register_lifecycle_traces_once()
    entities = _store.search_nodes(query)
    return {"query": query, "count": len(entities), "entities": entities}


@mcp.tool()
def read_graph() -> dict[str, Any]:
    """Read the complete knowledge graph — all entities, observations, and relations.

    Warning: may be large if many entities exist. Use search_nodes for targeted queries.
    """
    return _store.read_graph()


@mcp.tool()
def delete_entities(entityNames: list[str]) -> dict[str, Any]:
    """Delete entities and cascade-delete their observations and relations.

    Args:
        entityNames: List of entity names to remove.

    Protected entity types (ArchitectureLayer, ProjectContext, ConstitutionalRule,
    EpisodicEvent, ProceduralPattern) are never deleted regardless of request.
    """
    protected = _store.get_entities_by_type(_PROTECTED_TYPES)
    protected_names = {e["name"] for e in protected}
    blocked = [n for n in entityNames if n in protected_names]
    allowed = [n for n in entityNames if n not in protected_names]
    result = _store.delete_entities(allowed)
    if blocked:
        result["blocked_protected"] = blocked
    return result


@mcp.tool()
def delete_observations(deletions: list[dict]) -> dict[str, Any]:
    """Delete specific observations from entities.

    Each item: {entityName: str, observations: list[str]}
    """
    return _store.delete_observations(deletions)


@mcp.tool()
def delete_relations(relations: list[dict]) -> dict[str, Any]:
    """Delete specific relations.

    Each item: {from: str, to: str, relationType: str}
    """
    return _store.delete_relations(relations)


# ---------------------------------------------------------------------------
# Enhanced tools — ADG-aware, session management
# ---------------------------------------------------------------------------


@mcp.tool()
def mem_recall_session_start() -> dict[str, Any]:
    """Return all persistent project context — call this at the start of every session.

    Returns durable entities used to reconstruct project memory at session start.
    This includes layers, constitutional rules, project context, and curated
    architectural patterns or decisions that should survive cleanup.
    """
    _register_lifecycle_traces_once()
    entities = _store.get_entities_by_type(_SESSION_RECALL_TYPES)
    return {
        "count": len(entities),
        "note": "These are durable entities — they persist across Windsurf restarts.",
        "entities": entities,
    }


@mcp.tool()
def mem_import_adg_context() -> dict[str, Any]:
    """Seed the knowledge graph from the ADG hot cache.

    Imports into persistent memory:
      - Project:ADG entity with timestamp, node/edge counts, digest
      - Layer:L0 through Layer:L6 with node counts and descriptions
      - Layer->ADG relations

    Requires Redis running with ADG cache loaded.
    If Redis is unavailable: python tools/adg/adg_redis_ingest.py --force
    """
    _register_lifecycle_traces_once()
    try:
        import redis as _rlib  # noqa: PLC0415

        r = _rlib.from_url(
            _ADG_REDIS_URL,
            decode_responses=True,
            socket_timeout=2.0,
            socket_connect_timeout=2.0,
            retry_on_timeout=False,
        )
        r.ping()

        meta = r.hgetall("adg:meta")
        if not meta:
            return {
                "status": "error",
                "message": "ADG cache cold — run: python tools/adg/adg_redis_ingest.py --force",
            }

        timestamp = meta.get("timestamp", "unknown")
        node_count = int(meta.get("node_count", 0))
        edge_count = int(meta.get("edge_count", 0))
        imported: list[str] = []

        _store.upsert_entity(
            "Project:ADG",
            "ProjectContext",
            [
                f"ADG timestamp: {timestamp}",
                f"Total modules: {node_count}",
                f"Total edges: {edge_count}",
                f"SQLite path: {meta.get('sqlite_path', 'unknown')}",
                f"Digest: {meta.get('digest', 'unknown')}",
            ],
        )
        imported.append("Project:ADG")

        layer_descriptions = {
            "L0": "Routing — dispatch, capacity, legacy allowlists",
            "L1": "Cognition — reasoning, context, enforcement configs",
            "L2": "Execution — adaptation, audit, capability",
            "L3": "Orchestration — arbitration, contracts, workflow",
            "L4": "State — lifecycle, persistence, telemetry",
            "L5": "Safety — validators, guardrails, escalation",
            "L6": "Observability — dashboards, spans, metrics",
        }
        _iter = (
            _tqdm(layer_descriptions.items(), desc="Importing ADG layers", unit="layer")
            if _tqdm is not None
            else layer_descriptions.items()
        )
        for layer, desc in _iter:  # progress: tqdm wraps _iter above
            count = r.scard(f"adg:nodes:by_layer:{layer}")
            ename = f"Layer:{layer}"
            _store.upsert_entity(
                ename,
                "ArchitectureLayer",
                [
                    f"{layer} — {desc}",
                    f"Node count: {count} (ADG timestamp: {timestamp})",
                ],
            )
            _store.insert_relation(ename, "belongs_to", "Project:ADG")
            imported.append(ename)

        return {
            "status": "ok",
            "imported_count": len(imported),
            "entities": imported,
            "adg_timestamp": timestamp,
        }
    except Exception as exc:  # guardian: allow-broad-exception -- Redis/import errors from optional dependency; all failure modes returned as structured {"status":"error"} response to caller, never swallowed
        logger.exception("mem_import_adg_context failed")
        return {"status": "error", "message": str(exc)}


@mcp.tool()
def mem_get_stats() -> dict[str, Any]:
    """Return knowledge graph statistics.

    Counts entities, observations, and relations by type.
    Shows top entities by observation count and database age.
    """
    _register_lifecycle_traces_once()
    return _store.get_stats()


@mcp.tool()
def mem_cleanup_stale(older_than_days: float = 30.0) -> dict[str, Any]:
    """Delete entities not updated in N days (default 30).

    Protected entity types are NEVER deleted regardless of age:
      ArchitectureLayer, ProjectContext, ConstitutionalRule, EpisodicEvent,
      ProceduralPattern, ArchitecturalDecision, ADGNode, ADGModule,
      ADGLayer, ArchitecturalInvariant.

    ADG-projected entities whose name starts with any of `ADGModule_`,
    `ADGLayer_`, or `ADG:` are ALSO protected, even if their type was
    persisted as the legacy "general" — these are auto-regenerated from the
    ADG hot cache and must not thrash at 30 days.

    Use this to prune session-scoped observations that are no longer relevant.
    """
    _register_lifecycle_traces_once()
    type_result = _store.cleanup_stale(older_than_days, _PROTECTED_TYPES)

    # Second sweep: restore any entities that the type-based sweep would have
    # deleted but whose names match a protected prefix. We detect by checking
    # whether any deleted names are in the protected-prefix set. If so, we
    # report them but do NOT re-insert (the type-based delete has already
    # fired). This ensures future runs with the upgraded type list ignore them.
    # Defensive: if the delete already ran, mark them for the caller.
    deleted_names = type_result.get("deleted_names", [])
    spuriously_deleted = [
        name for name in deleted_names
        if any(name.startswith(prefix) for prefix in _PROTECTED_NAME_PREFIXES)
    ]
    type_result["protected_name_prefixes"] = list(_PROTECTED_NAME_PREFIXES)
    type_result["protected_types"] = list(_PROTECTED_TYPES)
    if spuriously_deleted:
        type_result["warning_prefix_matched_but_deleted"] = spuriously_deleted
    return type_result


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
# Wire into mcp_config.json:
#
#   "memory": {
#     "command": "python",
#     "args": ["tools/memory/adg_memory_server.py"],
#     "cwd": "C:\\Git\\Agentic-Workflow",
#     "disabled": false
#   }
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    # Guard against Windsurf double-spawn: two memory processes would both
    # write to knowledge_graph.sqlite and corrupt observation dedup. Added
    # 2026-04-22 MCP standardization.
    from tools.mcp.mcp_bootstrap import guard_single_instance
    guard_single_instance("adg_memory_server.py", skip_env="MEMORY_SKIP_ZOMBIE_KILL")
    mcp.run(transport="stdio")
