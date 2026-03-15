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
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
_DEFAULT_DB = Path(r"C:\Git\Agentic-Workflow\artifacts\memory\knowledge_graph.sqlite")
_DB_PATH: Path = Path(os.environ.get("MEMORY_DB", str(_DEFAULT_DB)))
_ADG_REDIS_URL: str = os.environ.get("ADG_REDIS_URL", "redis://localhost:6379/0")

_PROTECTED_TYPES = ("ArchitectureLayer", "ProjectContext", "ConstitutionalRule")

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
# SQLite helpers
# ---------------------------------------------------------------------------


def _conn() -> sqlite3.Connection:
    """Open a fresh SQLite connection with WAL mode and foreign keys."""
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def _db() -> Generator[sqlite3.Connection, None, None]:
    """Context manager: open connection, commit/rollback, then CLOSE explicitly."""
    conn = _conn()
    try:
        with conn:  # commit on success, rollback on exception
            yield conn
    finally:
        conn.close()


def _ensure_schema() -> None:
    with _db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS entities (
                name        TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL DEFAULT 'general',
                created_at  REAL NOT NULL,
                updated_at  REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS observations (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_name  TEXT NOT NULL REFERENCES entities(name) ON DELETE CASCADE,
                content      TEXT NOT NULL,
                created_at   REAL NOT NULL,
                UNIQUE (entity_name, content)
            );

            CREATE TABLE IF NOT EXISTS relations (
                from_entity   TEXT NOT NULL REFERENCES entities(name) ON DELETE CASCADE,
                relation_type TEXT NOT NULL,
                to_entity     TEXT NOT NULL,
                created_at    REAL NOT NULL,
                PRIMARY KEY (from_entity, relation_type, to_entity)
            );

            CREATE INDEX IF NOT EXISTS idx_obs_entity   ON observations (entity_name);
            CREATE INDEX IF NOT EXISTS idx_rel_from     ON relations (from_entity);
            CREATE INDEX IF NOT EXISTS idx_rel_to       ON relations (to_entity);
            CREATE INDEX IF NOT EXISTS idx_ent_type     ON entities (entity_type);
            """
        )


_ensure_schema()


def _upsert_entity(conn: sqlite3.Connection, name: str, etype: str, now: float) -> None:
    """Insert entity or update its updated_at timestamp if it already exists."""
    conn.execute(
        """
        INSERT INTO entities (name, entity_type, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET updated_at = excluded.updated_at
        """,
        (name, etype, now, now),
    )


def _add_obs(conn: sqlite3.Connection, name: str, content: str, now: float) -> bool:
    """Insert observation; return True if inserted, False if duplicate."""
    try:
        conn.execute(
            "INSERT INTO observations (entity_name, content, created_at) VALUES (?, ?, ?)",
            (name, content.strip(), now),
        )
        return True
    except sqlite3.IntegrityError:
        return False


def _load_entity(name: str) -> dict[str, Any] | None:
    """Load entity + observations + all relations touching it."""
    with _db() as conn:
        row = conn.execute(
            "SELECT name, entity_type, created_at, updated_at FROM entities WHERE name = ?",
            (name,),
        ).fetchone()
        if row is None:
            return None
        obs = [
            r["content"]
            for r in conn.execute(
                "SELECT content FROM observations WHERE entity_name = ? ORDER BY created_at",
                (name,),
            ).fetchall()
        ]
        rels = [
            {
                "from": r["from_entity"],
                "relationType": r["relation_type"],
                "to": r["to_entity"],
            }
            for r in conn.execute(
                "SELECT from_entity, relation_type, to_entity FROM relations "
                "WHERE from_entity = ? OR to_entity = ?",
                (name, name),
            ).fetchall()
        ]
    return {
        "name": row["name"],
        "entityType": row["entity_type"],
        "observations": obs,
        "relations": rels,
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }


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
    now = time.time()
    created: list[str] = []
    skipped: list[str] = []

    with _db() as conn:
        for e in entities:
            name = (e.get("name") or "").strip()
            etype = e.get("entityType") or "general"
            obs_list: list[str] = e.get("observations") or []
            if not name:
                continue
            exists = conn.execute("SELECT 1 FROM entities WHERE name = ?", (name,)).fetchone()
            if exists:
                skipped.append(name)
                continue
            conn.execute(
                "INSERT INTO entities (name, entity_type, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (name, etype, now, now),
            )
            for obs in obs_list:
                if obs:
                    _add_obs(conn, name, obs, now)
            created.append(name)

    return {"created": created, "skipped_existing": skipped}


@mcp.tool()
def add_observations(observations: list[dict]) -> dict[str, Any]:
    """Add observations to existing entities (creates entity if missing).

    Each item: {entityName: str, contents: list[str]}
    Duplicate observations are silently ignored — safe to call repeatedly.
    """
    now = time.time()
    result: dict[str, int] = {}

    with _db() as conn:
        for item in observations:
            name = (item.get("entityName") or "").strip()
            contents: list[str] = item.get("contents") or []
            if not name:
                continue
            _upsert_entity(conn, name, "general", now)
            count = sum(1 for c in contents if c and _add_obs(conn, name, c, now))
            if count:
                conn.execute("UPDATE entities SET updated_at = ? WHERE name = ?", (now, name))
            result[name] = count

    return {"added_observations": result}


@mcp.tool()
def create_relations(relations: list[dict]) -> dict[str, Any]:
    """Create directional relations between entities.

    Each relation: {from: str, to: str, relationType: str}
    Auto-creates missing entities (type='general'). Duplicate relations ignored.
    """
    now = time.time()
    created: list[dict] = []

    with _db() as conn:
        for rel in relations:
            from_e = (rel.get("from") or "").strip()
            to_e = (rel.get("to") or "").strip()
            rel_type = (rel.get("relationType") or "related_to").strip()
            if not from_e or not to_e:
                continue
            for name in (from_e, to_e):
                _upsert_entity(conn, name, "general", now)
            try:
                conn.execute(
                    "INSERT INTO relations (from_entity, relation_type, to_entity, created_at) "
                    "VALUES (?, ?, ?, ?)",
                    (from_e, rel_type, to_e, now),
                )
                created.append({"from": from_e, "relationType": rel_type, "to": to_e})
            except sqlite3.IntegrityError:
                pass

    return {"created_relations": created}


@mcp.tool()
def open_nodes(names: list[str]) -> dict[str, Any]:
    """Retrieve specific entities with their observations and relations.

    Args:
        names: List of entity names to load.
    """
    entities = []
    not_found = []
    for name in names:
        e = _load_entity(name)
        if e:
            entities.append(e)
        else:
            not_found.append(name)
    return {"entities": entities, "not_found": not_found}


@mcp.tool()
def search_nodes(query: str) -> dict[str, Any]:
    """Full-text search across entity names, types, and observation content.

    Case-insensitive substring match. Returns matching entities with all context.
    """
    pat = f"%{query}%"
    with _db() as conn:
        direct = {
            row["name"]
            for row in conn.execute(
                "SELECT name FROM entities WHERE name LIKE ? OR entity_type LIKE ?",
                (pat, pat),
            ).fetchall()
        }
        via_obs = {
            row["entity_name"]
            for row in conn.execute(
                "SELECT DISTINCT entity_name FROM observations WHERE content LIKE ?",
                (pat,),
            ).fetchall()
        }
        all_names = direct | via_obs
    entities = [e for n in sorted(all_names) if (e := _load_entity(n))]

    return {"query": query, "count": len(entities), "entities": entities}


@mcp.tool()
def read_graph() -> dict[str, Any]:
    """Read the complete knowledge graph — all entities, observations, and relations.

    Warning: may be large if many entities exist. Use search_nodes for targeted queries.
    """
    with _db() as conn:
        ent_rows = conn.execute(
            "SELECT name, entity_type FROM entities ORDER BY entity_type, name"
        ).fetchall()
        entities = []
        for row in ent_rows:
            obs = [
                r["content"]
                for r in conn.execute(
                    "SELECT content FROM observations WHERE entity_name = ? ORDER BY created_at",
                    (row["name"],),
                ).fetchall()
            ]
            entities.append(
                {
                    "name": row["name"],
                    "entityType": row["entity_type"],
                    "observations": obs,
                }
            )

        rels = [
            {
                "from": r["from_entity"],
                "relationType": r["relation_type"],
                "to": r["to_entity"],
            }
            for r in conn.execute(
                "SELECT from_entity, relation_type, to_entity FROM relations ORDER BY from_entity"
            ).fetchall()
        ]

    return {"entities": entities, "relations": rels}


@mcp.tool()
def delete_entities(entityNames: list[str]) -> dict[str, Any]:
    """Delete entities and cascade-delete their observations and relations.

    Args:
        entityNames: List of entity names to remove.
    """
    with _db() as conn:
        deleted = []
        not_found = []
        for name in entityNames:
            rows = conn.execute("DELETE FROM entities WHERE name = ?", (name,)).rowcount
            (deleted if rows else not_found).append(name)

    return {"deleted": deleted, "not_found": not_found}


@mcp.tool()
def delete_observations(deletions: list[dict]) -> dict[str, Any]:
    """Delete specific observations from entities.

    Each item: {entityName: str, observations: list[str]}
    """
    with _db() as conn:
        removed: dict[str, int] = {}
        for item in deletions:
            name = item.get("entityName") or ""
            obs_list: list[str] = item.get("observations") or []
            count = sum(
                conn.execute(
                    "DELETE FROM observations WHERE entity_name = ? AND content = ?",
                    (name, obs),
                ).rowcount
                for obs in obs_list
            )
            removed[name] = count

    return {"removed_observations": removed}


@mcp.tool()
def delete_relations(relations: list[dict]) -> dict[str, Any]:
    """Delete specific relations.

    Each item: {from: str, to: str, relationType: str}
    """
    with _db() as conn:
        deleted = []
        for rel in relations:
            rows = conn.execute(
                "DELETE FROM relations WHERE from_entity = ? AND relation_type = ? AND to_entity = ?",
                (
                    rel.get("from") or "",
                    rel.get("relationType") or "",
                    rel.get("to") or "",
                ),
            ).rowcount
            if rows:
                deleted.append(rel)

    return {"deleted_relations": deleted}


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
    placeholders = ",".join("?" * len(_PROTECTED_TYPES))
    with _db() as conn:
        rows = conn.execute(
            f"SELECT name FROM entities WHERE entity_type IN ({placeholders}) ORDER BY entity_type, name",
            _PROTECTED_TYPES,
        ).fetchall()
        names_list = [row["name"] for row in rows]
    entities = [e for n in names_list if (e := _load_entity(n))]

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
        now = time.time()
        imported: list[str] = []

        with _db() as conn:
            _upsert_entity(conn, "Project:ADG", "ProjectContext", now)
            for obs in [
                f"ADG timestamp: {timestamp}",
                f"Total modules: {node_count}",
                f"Total edges: {edge_count}",
                f"SQLite path: {meta.get('sqlite_path', 'unknown')}",
                f"Digest: {meta.get('digest', 'unknown')}",
            ]:
                _add_obs(conn, "Project:ADG", obs, now)
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
            for layer, desc in layer_descriptions.items():
                count = r.scard(f"adg:nodes:by_layer:{layer}")
                ename = f"Layer:{layer}"
                _upsert_entity(conn, ename, "ArchitectureLayer", now)
                for obs in [
                    f"{layer} — {desc}",
                    f"Node count: {count} (ADG timestamp: {timestamp})",
                ]:
                    _add_obs(conn, ename, obs, now)
                try:
                    conn.execute(
                        "INSERT OR IGNORE INTO relations "
                        "(from_entity, relation_type, to_entity, created_at) VALUES (?, ?, ?, ?)",
                        (ename, "belongs_to", "Project:ADG", now),
                    )
                except sqlite3.IntegrityError:
                    pass
                imported.append(ename)

        return {
            "status": "ok",
            "imported_count": len(imported),
            "entities": imported,
            "adg_timestamp": timestamp,
        }
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": str(exc)}


@mcp.tool()
def mem_get_stats() -> dict[str, Any]:
    """Return knowledge graph statistics.

    Counts entities, observations, and relations by type.
    Shows top entities by observation count and database age.
    """
    with _db() as conn:
        total_e = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        total_o = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
        total_r = conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0]

        by_type = {
            row["entity_type"]: row["cnt"]
            for row in conn.execute(
                "SELECT entity_type, COUNT(*) AS cnt FROM entities GROUP BY entity_type ORDER BY cnt DESC"
            ).fetchall()
        }

        top = [
            {"name": row["entity_name"], "observation_count": row["cnt"]}
            for row in conn.execute(
                "SELECT entity_name, COUNT(*) AS cnt FROM observations "
                "GROUP BY entity_name ORDER BY cnt DESC LIMIT 10"
            ).fetchall()
        ]

        oldest = conn.execute("SELECT MIN(created_at) FROM entities").fetchone()[0]
        newest = conn.execute("SELECT MAX(updated_at) FROM entities").fetchone()[0]

    now = time.time()
    return {
        "total_entities": total_e,
        "total_observations": total_o,
        "total_relations": total_r,
        "by_entity_type": by_type,
        "top_entities_by_observations": top,
        "db_path": str(_DB_PATH),
        "oldest_entity_age_days": round((now - oldest) / 86400, 1) if oldest else 0,
        "last_updated_ago_seconds": round(now - newest, 1) if newest else 0,
    }


@mcp.tool()
def mem_cleanup_stale(older_than_days: float = 30.0) -> dict[str, Any]:
    """Delete entities not updated in N days (default 30).

    Protected entity types are NEVER deleted regardless of age:
      ArchitectureLayer, ProjectContext, ConstitutionalRule

    Use this to prune session-scoped observations that are no longer relevant.
    """
    cutoff = time.time() - (older_than_days * 86400)
    placeholders = ",".join("?" * len(_PROTECTED_TYPES))

    with _db() as conn:
        stale = conn.execute(
            f"SELECT name FROM entities WHERE updated_at < ? AND entity_type NOT IN ({placeholders})",
            (cutoff, *_PROTECTED_TYPES),
        ).fetchall()
        names = [r["name"] for r in stale]
        if names:
            conn.execute(
                f"DELETE FROM entities WHERE name IN ({','.join('?' * len(names))})",
                names,
            )

    return {
        "deleted_count": len(names),
        "deleted_names": names,
        "cutoff_days": older_than_days,
        "protected_types": list(_PROTECTED_TYPES),
    }


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
