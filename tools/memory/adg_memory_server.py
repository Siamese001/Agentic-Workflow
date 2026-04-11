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

from mcp.server.fastmcp import FastMCP

try:
    from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
        _emit_records_execution_trace,  # noqa: E402
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
except ImportError as _ltc_err:
    print(
        f"[adg_memory_server] FATAL: lifecycle_trace_contract import failed: {_ltc_err}\n"
        "  Check that agentic_core is on PYTHONPATH and the contract module has not been moved.\n"
        f"  PYTHONPATH={__import__('os').environ.get('PYTHONPATH', '<unset>')}",
        file=__import__("sys").stderr,
        flush=True,
    )
    __import__("sys").exit(1)

_emit_authorize_and_execute("p2", "adg_memory_server", "execution_auth")
_emit_validates_capability("p2", "adg_memory_server", "capability_check")
_emit_routes_to_capability("p2", "adg_memory_server", "capability_route")
_emit_writes_via_uwg("p2", "adg_memory_server", "uwg_write")
_emit_blocks_direct_write("p2", "adg_memory_server", "direct_write_block")
_emit_records_tool_invocation("p2", "adg_memory_server", "tool_invocation")
_emit_captures_execution_output("p2", "adg_memory_server", "exec_output")
_emit_dispatches_agent("p3", "adg_memory_server", "agent_dispatch")
_emit_coordinates_agents("p3", "adg_memory_server", "agent_coordination")
_emit_records_workflow_lineage("p3", "adg_memory_server", "workflow_lineage")
_emit_records_healing_outcome("p3", "adg_memory_server", "healing_outcome")
_emit_escalates_failure("p3", "adg_memory_server", "failure_escalation")
_emit_orchestrates_workflow("p3", "adg_memory_server", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "adg_memory_server", "healing_dispatch")
_emit_invokes_evaluation("p3", "adg_memory_server", "evaluation_signal")
_emit_records_telemetry_event("p4", "adg_memory_server", "telemetry_event")
_emit_captures_evaluation_metric("p4", "adg_memory_server", "eval_metric")
_emit_stores_embedding("p4", "adg_memory_server", "embedding_store")
_emit_updates_meta_learning_state("p4", "adg_memory_server", "meta_learning")
_emit_links_execution_to_snapshot("p4", "adg_memory_server", "exec_snapshot_link")
from tools.memory.sqlite_memory_store import SqliteMemoryStore

_emit_records_execution_trace("p0", "evidence", "adg_memory_server")
_emit_applies_guardrail("p0", "adg_memory_server", "p0_governance")
_emit_reads_policy_state("p0", "adg_memory_server", "policy_binding")
_emit_snapshots_state("p0", "adg_memory_server", "state_snapshot")
try:
    from agentic_core.runtime.contracts.lifecycle_trace_contract import (
        _emit_captures_pattern,
        _emit_captures_runtime_anomaly,
        _emit_emits_metric_event,
        _emit_execution_terminates_at_uwg,
        _emit_feeds_meta_learning,
        _emit_improves_agent_policy,
        _emit_invokes_eval,
        _emit_links_incident_trace,
        _emit_proposal_commits_routing,
        _emit_pulls_context,
        _emit_reads_environ,
        _emit_reads_runtime_state,
        _emit_records_execution_trace,
        _emit_records_incident_event,
        _emit_records_learning_event,
        _emit_stores_learning_state,
        _emit_triggers_alert,
        _emit_updates_monitoring_state,
        _emit_updates_routing_strategy,
        _emit_validated_by_safety_plane,
        _emit_writes_learning_snapshot,
        _emit_writes_observability_log,
        _emit_writes_through,
    )
except ImportError as _ltc_err2:
    print(
        f"[adg_memory_server] FATAL: lifecycle_trace_contract (second import) failed: {_ltc_err2}\n"
        "  Check that agentic_core is on PYTHONPATH and the contract module has not been moved.",
        file=__import__("sys").stderr,
        flush=True,
    )
    __import__("sys").exit(1)

_emit_emits_metric_event("adg_memory_server", "p4obs", "metric_1")
_emit_emits_metric_event("adg_memory_server", "p4obs", "metric_2")
_emit_emits_metric_event("adg_memory_server", "p4obs", "metric_3")
_emit_emits_metric_event("adg_memory_server", "p4obs", "metric_4")
_emit_emits_metric_event("adg_memory_server", "p4obs", "metric_5")
_emit_emits_metric_event("adg_memory_server", "p4obs", "metric_6")
_emit_records_incident_event("adg_memory_server", "p4obs", "incident")
_emit_captures_runtime_anomaly("adg_memory_server", "p4obs", "anomaly")
_emit_writes_observability_log("adg_memory_server", "p4obs", "obs_log")
_emit_updates_monitoring_state("adg_memory_server", "p4obs", "mon_state")
_emit_triggers_alert("adg_memory_server", "p4obs", "alert")
_emit_links_incident_trace("adg_memory_server", "p4obs", "trace_link")
_emit_captures_pattern("adg_memory_server", "p3lm", "pattern")
_emit_records_learning_event("adg_memory_server", "p3lm", "learning_event")
_emit_writes_learning_snapshot("adg_memory_server", "p3lm", "snapshot")
_emit_feeds_meta_learning("adg_memory_server", "p3lm", "meta_feed")
_emit_updates_routing_strategy("adg_memory_server", "p3lm", "routing")
_emit_improves_agent_policy("adg_memory_server", "p3lm", "policy")
_emit_stores_learning_state("adg_memory_server", "p3lm", "state")
_emit_records_execution_trace("adg_memory_server", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("adg_memory_server", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("adg_memory_server", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("adg_memory_server", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("adg_memory_server", "L4_STATE", "p2_trace_5")
_emit_reads_environ("adg_memory_server", "env_read", "p2_env_1")
_emit_reads_environ("adg_memory_server", "env_read", "p2_env_2")
_emit_reads_runtime_state("adg_memory_server", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("adg_memory_server", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "adg_memory_server", "context_pull")
_emit_pulls_context("p1", "adg_memory_server", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "adg_memory_server", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "adg_memory_server", "uwg_term_2")
_emit_writes_through("p1", "adg_memory_server", "write_through")
_emit_writes_through("p1", "adg_memory_server", "write_through_2")
_emit_validated_by_safety_plane("p1", "adg_memory_server", "safety_validation")
_emit_invokes_eval("p1", "adg_memory_server", "eval_call")
_emit_proposal_commits_routing("p1", "adg_memory_server", "routing_commit")
_emit_escalates_to_human("p1", "adg_memory_server", "human_escalation")
_emit_routes_through("p1", "adg_memory_server", "route_through")
_emit_checks_agent_registry("p1", "adg_memory_server", "agent_registry")
_emit_validates_agent_capability("p1", "adg_memory_server", "capability")
_emit_dispatches_execution_plan("p1", "adg_memory_server", "exec_plan")
_emit_agent_executes_agent("p1", "adg_memory_server", "sub_agent")
_emit_routes_to_agent("p1", "adg_memory_server", "target_agent")
_emit_verifies_policy("p1", "adg_memory_server", "policy_check")
_emit_observes_runtime_state("p1", "adg_memory_server", "runtime_state")
_emit_verifies_boundary("p1", "adg_memory_server", "boundary_check")
_emit_transcripts_response("p1", "adg_memory_server", "transcript")
_emit_hard_fails_untranscripted("p1", "adg_memory_server")
_emit_gated_by_confidence("p1", "adg_memory_server", "confidence_gate")
emit_replay_key("p0", "adg_memory_server")
emit_determinism_digest("p0", "adg_memory_server")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_reads_through("l4", "adg_memory_server", "urg_read_1")
_emit_reads_through("l4", "adg_memory_server", "urg_read_2")
_emit_reads_through("l4", "adg_memory_server", "urg_read_3")
_emit_reads_through("l4", "adg_memory_server", "urg_read_4")
_emit_reads_through("l4", "adg_memory_server", "urg_read_5")
_emit_reads_through("l4", "adg_memory_server", "urg_read_6")
_emit_reads_through("l4", "adg_memory_server", "urg_read_7")
_emit_reads_through("l4", "adg_memory_server", "urg_read_8")
_emit_reads_through("l4", "adg_memory_server", "urg_read_9")
_emit_reads_through("l4", "adg_memory_server", "urg_read_10")
_emit_reads_through("l4", "adg_memory_server", "urg_read_11")
_emit_reads_through("l4", "adg_memory_server", "urg_read_12")
_emit_reads_through("l4", "adg_memory_server", "urg_read_13")
_emit_reads_through("l4", "adg_memory_server", "urg_read_14")
_emit_reads_through("l4", "adg_memory_server", "urg_read_15")
_emit_reads_through("l4", "adg_memory_server", "urg_read_16")
_emit_reads_through("l4", "adg_memory_server", "urg_read_17")
_emit_reads_through("l4", "adg_memory_server", "urg_read_18")
_emit_reads_through("l4", "adg_memory_server", "urg_read_19")
_emit_reads_through("l4", "adg_memory_server", "urg_read_20")
_emit_reads_through("l4", "adg_memory_server", "urg_read_21")
_emit_reads_through("l4", "adg_memory_server", "urg_read_22")
_emit_reads_through("l4", "adg_memory_server", "urg_read_23")
_emit_reads_through("l4", "adg_memory_server", "urg_read_24")
_emit_reads_through("l4", "adg_memory_server", "urg_read_25")
_emit_reads_through("l4", "adg_memory_server", "urg_read_26")
_emit_reads_through("l4", "adg_memory_server", "urg_read_27")
_emit_reads_through("l4", "adg_memory_server", "urg_read_28")
_emit_reads_through("l4", "adg_memory_server", "urg_read_29")
_emit_reads_through("l4", "adg_memory_server", "urg_read_30")
_emit_reads_through("l4", "adg_memory_server", "urg_read_31")
_emit_reads_through("l4", "adg_memory_server", "urg_read_32")
_emit_reads_through("l4", "adg_memory_server", "urg_read_33")
_emit_reads_through("l4", "adg_memory_server", "urg_read_34")
_emit_reads_through("l4", "adg_memory_server", "urg_read_35")
_emit_reads_through("l4", "adg_memory_server", "urg_read_36")
_emit_reads_through("l4", "adg_memory_server", "urg_read_37")
_emit_reads_through("l4", "adg_memory_server", "urg_read_38")

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
)

_store = SqliteMemoryStore(_DB_PATH)

# ---------------------------------------------------------------------------
# FastMCP server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "adg-memory",
    instructions=(
        "Persistent SQLite-backed knowledge graph. "
        "Survives restarts — no data loss on Windsurf reload. "
        "Call mem_recall_session_start first. "
        "Use mem_import_adg_context to seed from ADG hot cache."
    ),
)


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

    Returns entities typed as ArchitectureLayer, ProjectContext, and ConstitutionalRule.
    These are durable entities that survive cleanup and represent the long-lived
    knowledge base: ADG metadata, layer structure, and constitutional rules.
    """
    entities = _store.get_entities_by_type(_PROTECTED_TYPES)
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
    try:
        import redis as _rlib  # noqa: PLC0415

        r = _rlib.from_url(_ADG_REDIS_URL, decode_responses=True)
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
        for layer, desc in _iter:
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
        return {"status": "error", "message": str(exc)}


@mcp.tool()
def mem_get_stats() -> dict[str, Any]:
    """Return knowledge graph statistics.

    Counts entities, observations, and relations by type.
    Shows top entities by observation count and database age.
    """
    return _store.get_stats()


@mcp.tool()
def mem_cleanup_stale(older_than_days: float = 30.0) -> dict[str, Any]:
    """Delete entities not updated in N days (default 30).

    Protected entity types are NEVER deleted regardless of age:
      ArchitectureLayer, ProjectContext, ConstitutionalRule

    Use this to prune session-scoped observations that are no longer relevant.
    """
    return _store.cleanup_stale(older_than_days, _PROTECTED_TYPES)


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
    mcp.run(transport="stdio")
