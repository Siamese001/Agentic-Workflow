"""Shared SQLite-backed memory store.

Single source of truth for knowledge_graph.sqlite schema and all CRUD operations.

Used by two consumers:
  - tools/memory/adg_memory_server.py  (MCP protocol wrapper — Windsurf IDE access)
  - agentic_core/L4_state/enforcement/graph_memory_bridge.py  (CLI fallback path)

Both paths write to the same knowledge_graph.sqlite file, ensuring that ADG
generation from the CLI persists identically to what the Memory MCP server sees.

API surface mirrors @modelcontextprotocol/server-memory tool signatures so
GraphMemoryBridge can use it as a drop-in replacement for mcp11 calls.
"""

from __future__ import annotations

import os
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

_DEFAULT_DB = Path(r"C:\Git\Agentic-Workflow\artifacts\memory\knowledge_graph.sqlite")

ALLOWED_ENTITY_TYPES: frozenset[str] = frozenset({
    "ArchitectureLayer",
    "ProjectContext",
    "ConstitutionalRule",
    "EpisodicEvent",
    "ProceduralPattern",
    "ArchitecturalDecision",
})

_SCHEMA = """
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

CREATE INDEX IF NOT EXISTS idx_obs_entity ON observations (entity_name);
CREATE INDEX IF NOT EXISTS idx_rel_from   ON relations (from_entity);
CREATE INDEX IF NOT EXISTS idx_rel_to     ON relations (to_entity);
CREATE INDEX IF NOT EXISTS idx_ent_type   ON entities (entity_type);
"""


class SqliteMemoryStore:
    """SQLite-backed memory store — shared between MCP server and CLI fallback.

    Idempotent: repeated calls for the same entity/relation/observation are safe.
    Thread-safe: WAL mode allows concurrent readers with a single writer.
    Schema-stable: schema is created on first instantiation and never modified here.
    """

    def __init__(self, db_path: Path | str | None = None) -> None:
        if db_path is None:
            db_path = Path(os.environ.get("MEMORY_DB", str(_DEFAULT_DB)))
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Open a WAL-mode SQLite connection, commit on success, close on exit."""
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def _ensure_schema(self) -> None:
        with self.connection() as conn:
            conn.executescript(_SCHEMA)

    def _upsert_entity(self, conn: sqlite3.Connection, name: str, etype: str, now: float) -> None:
        conn.execute(
            """
            INSERT INTO entities (name, entity_type, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET updated_at = excluded.updated_at
            """,
            (name, etype, now, now),
        )

    def _add_obs(self, conn: sqlite3.Connection, name: str, content: str, now: float) -> bool:
        """Insert observation; return True if inserted, False if duplicate."""
        try:
            conn.execute(
                "INSERT INTO observations (entity_name, content, created_at) VALUES (?, ?, ?)",
                (name, content.strip(), now),
            )
            return True
        except sqlite3.IntegrityError:
            return False

    # ------------------------------------------------------------------
    # Core API — mirrors mcp11 / @modelcontextprotocol/server-memory signatures
    # ------------------------------------------------------------------

    def create_entities(self, entities: list[dict]) -> dict[str, Any]:
        """Create entities; skip existing. Returns {created, skipped_existing, rejected_type}.

        entity_type must be one of ALLOWED_ENTITY_TYPES. Unknown types are rejected
        with an entry in the 'rejected_type' list so callers get an explicit error.
        """
        now = time.time()
        created: list[str] = []
        skipped: list[str] = []
        rejected: list[dict] = []
        with self.connection() as conn:
            for e in entities:
                name = (e.get("name") or "").strip()
                if not name:
                    continue
                etype = e.get("entityType") or "general"
                if etype not in ALLOWED_ENTITY_TYPES:
                    rejected.append({"name": name, "entity_type": etype,
                                     "reason": f"entity_type '{etype}' not in ALLOWED_ENTITY_TYPES"})
                    continue
                obs_list: list[str] = e.get("observations") or []
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
                        self._add_obs(conn, name, obs, now)
                created.append(name)
        result: dict[str, Any] = {"created": created, "skipped_existing": skipped}
        if rejected:
            result["rejected_type"] = rejected
        return result

    def add_observations(self, observations: list[dict]) -> dict[str, Any]:
        """Add observations to entities; create entity if missing. Idempotent.

        Each item: {entityName: str, contents: list[str]}
        """
        now = time.time()
        result: dict[str, int] = {}
        with self.connection() as conn:
            for item in observations:
                name = (item.get("entityName") or "").strip()
                contents: list[str] = item.get("contents") or []
                if not name:
                    continue
                self._upsert_entity(conn, name, "general", now)
                count = sum(1 for c in contents if c and self._add_obs(conn, name, c, now))
                if count:
                    conn.execute("UPDATE entities SET updated_at = ? WHERE name = ?", (now, name))
                result[name] = count
        return {"added_observations": result}

    def create_relations(self, relations: list[dict]) -> dict[str, Any]:
        """Create directed relations; auto-create missing entities. Idempotent.

        Each item: {from: str, to: str, relationType: str}
        """
        now = time.time()
        created: list[dict] = []
        with self.connection() as conn:
            for rel in relations:
                from_e = (rel.get("from") or "").strip()
                to_e = (rel.get("to") or "").strip()
                rel_type = (rel.get("relationType") or "related_to").strip()
                if not from_e or not to_e:
                    continue
                for name in (from_e, to_e):
                    self._upsert_entity(conn, name, "general", now)
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

    def open_nodes(self, names: list[str]) -> dict[str, Any]:
        """Retrieve specific entities with observations and relations."""
        entities = []
        not_found = []
        for name in names:
            e = self.load_entity(name)
            if e:
                entities.append(e)
            else:
                not_found.append(name)
        return {"entities": entities, "not_found": not_found}

    def search_nodes(self, query: str) -> list[dict[str, Any]]:
        """Full-text search across entity names, types, and observations."""
        pat = f"%{query}%"
        with self.connection() as conn:
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
        return [e for n in sorted(all_names) if (e := self.load_entity(n))]

    def read_graph(self) -> dict[str, Any]:
        """Read the complete graph — all entities, observations, and relations."""
        with self.connection() as conn:
            ent_rows = conn.execute(
                "SELECT name, entity_type FROM entities ORDER BY entity_type, name",
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
                entities.append({"name": row["name"], "entityType": row["entity_type"], "observations": obs})
            rels = [
                {"from": r["from_entity"], "relationType": r["relation_type"], "to": r["to_entity"]}
                for r in conn.execute(
                    "SELECT from_entity, relation_type, to_entity FROM relations ORDER BY from_entity",
                ).fetchall()
            ]
        return {"entities": entities, "relations": rels}

    def delete_entities(self, entity_names: list[str]) -> dict[str, Any]:
        """Delete entities and cascade-delete their observations and relations."""
        with self.connection() as conn:
            deleted, not_found = [], []
            for name in entity_names:
                rows = conn.execute("DELETE FROM entities WHERE name = ?", (name,)).rowcount
                (deleted if rows else not_found).append(name)
        return {"deleted": deleted, "not_found": not_found}

    def delete_observations(self, deletions: list[dict]) -> dict[str, Any]:
        """Delete specific observations. Each item: {entityName, observations: list[str]}."""
        with self.connection() as conn:
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

    def delete_relations(self, relations: list[dict]) -> dict[str, Any]:
        """Delete specific relations. Each item: {from, to, relationType}."""
        with self.connection() as conn:
            deleted = []
            for rel in relations:
                rows = conn.execute(
                    "DELETE FROM relations WHERE from_entity = ? AND relation_type = ? AND to_entity = ?",
                    (rel.get("from") or "", rel.get("relationType") or "", rel.get("to") or ""),
                ).rowcount
                if rows:
                    deleted.append(rel)
        return {"deleted_relations": deleted}

    # ------------------------------------------------------------------
    # Enhanced API — used by adg_memory_server.py and ADGMemoryAdapter
    # ------------------------------------------------------------------

    def load_entity(self, name: str) -> dict[str, Any] | None:
        """Load a single entity with all observations and relations."""
        with self.connection() as conn:
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
                {"from": r["from_entity"], "relationType": r["relation_type"], "to": r["to_entity"]}
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

    def get_entities_by_type(self, types: tuple[str, ...]) -> list[dict[str, Any]]:
        """Return all entities whose type is in the given tuple, fully loaded."""
        if not types:
            return []
        placeholders = ",".join("?" * len(types))
        with self.connection() as conn:
            rows = conn.execute(
                f"SELECT name FROM entities WHERE entity_type IN ({placeholders}) ORDER BY entity_type, name",
                types,
            ).fetchall()
            names = [row["name"] for row in rows]
        return [e for n in names if (e := self.load_entity(n))]

    def upsert_entity(self, name: str, etype: str, observations: list[str] | None = None) -> None:
        """Single-entity upsert with optional observation list. Idempotent."""
        now = time.time()
        with self.connection() as conn:
            self._upsert_entity(conn, name, etype, now)
            for obs in (observations or []):
                if obs:
                    self._add_obs(conn, name, obs, now)

    def add_observation(self, entity_name: str, content: str) -> bool:
        """Add a single observation to an entity. Returns True if inserted."""
        now = time.time()
        with self.connection() as conn:
            self._upsert_entity(conn, entity_name, "general", now)
            return self._add_obs(conn, entity_name, content, now)

    def insert_relation(self, from_e: str, rel_type: str, to_e: str) -> bool:
        """Insert a single relation. Returns True if inserted, False if duplicate."""
        now = time.time()
        with self.connection() as conn:
            for name in (from_e, to_e):
                self._upsert_entity(conn, name, "general", now)
            try:
                conn.execute(
                    "INSERT INTO relations (from_entity, relation_type, to_entity, created_at) "
                    "VALUES (?, ?, ?, ?)",
                    (from_e, rel_type, to_e, now),
                )
                return True
            except sqlite3.IntegrityError:
                return False

    def get_stats(self) -> dict[str, Any]:
        """Return entity/observation/relation counts and top entities."""
        with self.connection() as conn:
            total_e = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
            total_o = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
            total_r = conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0]
            by_type = {
                row["entity_type"]: row["cnt"]
                for row in conn.execute(
                    "SELECT entity_type, COUNT(*) AS cnt FROM entities GROUP BY entity_type ORDER BY cnt DESC",
                ).fetchall()
            }
            top = [
                {"name": row["entity_name"], "observation_count": row["cnt"]}
                for row in conn.execute(
                    "SELECT entity_name, COUNT(*) AS cnt FROM observations "
                    "GROUP BY entity_name ORDER BY cnt DESC LIMIT 10",
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
            "db_path": str(self.db_path),
            "oldest_entity_age_days": round((now - oldest) / 86400, 1) if oldest else 0,
            "last_updated_ago_seconds": round(now - newest, 1) if newest else 0,
        }

    def cleanup_stale(
        self,
        older_than_days: float = 30.0,
        protected_types: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        """Delete entities not updated in N days, excluding protected types."""
        cutoff = time.time() - (older_than_days * 86400)
        with self.connection() as conn:
            if protected_types:
                placeholders = ",".join("?" * len(protected_types))
                stale = conn.execute(
                    f"SELECT name FROM entities WHERE updated_at < ? AND entity_type NOT IN ({placeholders})",
                    (cutoff, *protected_types),
                ).fetchall()
            else:
                stale = conn.execute(
                    "SELECT name FROM entities WHERE updated_at < ?",
                    (cutoff,),
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
            "protected_types": list(protected_types),
        }


__all__ = ["SqliteMemoryStore"]
