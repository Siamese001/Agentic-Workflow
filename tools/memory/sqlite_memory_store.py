"""Shared SQLite-backed memory store.

Single source of truth for knowledge_graph.sqlite schema and all CRUD operations.

Used by two consumers:
  - tools/memory/adg_memory_server.py  (MCP protocol wrapper — legacy editor IDE access)
  - agentic_core/L4_state/enforcement/graph_memory_bridge.py  (CLI fallback path)

Both paths write to the same knowledge_graph.sqlite file, ensuring that ADG
generation from the CLI persists identically to what the Memory MCP server sees.

API surface mirrors @modelcontextprotocol/server-memory tool signatures so
GraphMemoryBridge can use it as a drop-in replacement for mcp11 calls.
"""

from __future__ import annotations

import datetime as _dt
import logging as _logging
import math
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

from agentic_core.L4_state.adapters import sqlite3_adapter as sqlite3

_logger = _logging.getLogger(__name__)


def _safe_epoch(value: Any, fallback: float) -> float:
    """Defensively convert a stored ``last_reinforced`` value to a unix-epoch float.

    Schema declares ``last_reinforced REAL`` but SQLite manifest typing accepts
    arbitrary types. If a maintenance script or external writer ever stores an
    ISO-8601 timestamp string, ``float()`` raises ``ValueError`` and crashes
    every read path that uses ``effective_confidence``. This helper handles
    all observed-in-the-wild shapes:

    - ``None``                       → fallback
    - ``int``/``float``              → direct cast
    - numeric string ('1.7e9')       → ``float()``
    - ISO-8601 string                → ``datetime.fromisoformat().timestamp()``
    - anything else                  → fallback (with WARNING log)

    The first time a coercion fails for a row, we log a single WARNING with
    the raw value so the corruption can be traced. Returns ``fallback`` on
    any failure so the read path stays available.
    """
    if value is None:
        return fallback
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return fallback
        try:
            return float(s)
        except ValueError:
            pass
        try:
            return _dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
        except ValueError:
            pass
    _logger.warning(
        "memory_store: unparseable last_reinforced value %r (type=%s); using fallback=%s",
        value,
        type(value).__name__,
        fallback,
    )
    return fallback


try:
    from tqdm import tqdm
except ImportError:

    def tqdm(iterable, **_kwargs):
        return iterable


from tools.memory.memory_decay import (
    confidence_threshold,
    effective_confidence,
    jaccard_similarity,
    jaccard_threshold,
    reinforced_confidence,
)

_DEFAULT_DB = Path(__file__).resolve().parents[2] / "artifacts" / "memory" / "knowledge_graph.sqlite"

# Schema SSOT: canonical schema lives in .codex/schemas/
_SCHEMA_DIR = Path(__file__).resolve().parents[2] / ".codex" / "schemas"
_SCHEMA_FILE = _SCHEMA_DIR / "knowledge_graph.schema.sql"
_MIGRATIONS_FILE = _SCHEMA_DIR / "knowledge_graph_migrations.sql"

ALLOWED_ENTITY_TYPES: frozenset[str] = frozenset(
    {
        "ArchitectureLayer",
        "ProjectContext",
        "ConstitutionalRule",
        "EpisodicEvent",
        "ProceduralPattern",
        "ArchitecturalDecision",
        "general",
    }
)

def _load_schema() -> str:
    """Load canonical schema from .codex/schemas/knowledge_graph.schema.sql
    
    Falls back to embedded schema if file not found (backward compatibility).
    """
    if _SCHEMA_FILE.exists():
        return _SCHEMA_FILE.read_text(encoding="utf-8")
    # Fallback: embedded schema (for bootstrap or when file missing)
    return """
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

-- Schema version tracking (enables migration system)
CREATE TABLE IF NOT EXISTS _schema_version (
    version     TEXT PRIMARY KEY,
    applied_at  REAL NOT NULL,
    description TEXT NOT NULL
);
"""

_SCHEMA = _load_schema()

# Additive columns added by _migrate_decay_columns() — old DBs upgrade in place,
# new DBs get them via the same path. Existing rows default to confidence=1.0
# and last_reinforced=updated_at, preserving behavior for anyone reading without
# applying decay.
_DECAY_MIGRATION_COLUMNS: tuple[tuple[str, str, str], ...] = (
    ("entities", "confidence", "REAL NOT NULL DEFAULT 1.0"),
    ("entities", "last_reinforced", "REAL"),
    ("entities", "access_count", "INTEGER NOT NULL DEFAULT 0"),
    ("observations", "confidence", "REAL NOT NULL DEFAULT 1.0"),
    ("observations", "last_reinforced", "REAL"),
    ("observations", "access_count", "INTEGER NOT NULL DEFAULT 0"),
)


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
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA synchronous=NORMAL")
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def _ensure_schema(self) -> None:
        with self.connection() as conn:
            conn.executescript(_SCHEMA)
            self._migrate_decay_columns(conn)
            self._ensure_schema_version(conn)

    def _ensure_schema_version(self, conn) -> None:
        """Ensure schema version is recorded. Idempotent."""
        # Ensure _schema_version table exists (may not be in older files)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS _schema_version (
                version     TEXT PRIMARY KEY,
                applied_at  REAL NOT NULL,
                description TEXT NOT NULL
            )
        """)
        # Record base schema version if not present
        conn.execute("""
            INSERT OR IGNORE INTO _schema_version (version, applied_at, description)
            VALUES ('1.0.0', ?, 'Initial schema with entities, observations, relations')
        """, (time.time(),))

    def get_schema_version(self) -> dict[str, Any]:
        """Return current schema version info from database."""
        with self.connection() as conn:
            # Check if _schema_version table exists
            row = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='_schema_version'"
            ).fetchone()
            if row is None:
                return {"version": "unknown", "applied_at": None, "description": "pre-versioning schema"}
            
            versions = conn.execute(
                "SELECT version, applied_at, description FROM _schema_version ORDER BY applied_at"
            ).fetchall()
            if not versions:
                return {"version": "unknown", "applied_at": None, "description": "no version recorded"}
            
            latest = versions[-1]
            return {
                "version": latest["version"],
                "applied_at": latest["applied_at"],
                "description": latest["description"],
                "all_versions": [{"version": v["version"], "applied_at": v["applied_at"]} for v in versions]
            }

    @staticmethod
    def _migrate_decay_columns(conn: sqlite3.Connection) -> None:
        """Idempotent additive migration for confidence + last_reinforced columns.

        SQLite ADD COLUMN is cheap: O(1), no table rewrite. Safe to run every
        open. Existing rows get the column default (1.0 for confidence) and
        NULL for last_reinforced which is back-filled to updated_at.
        """
        for table, col, decl in _DECAY_MIGRATION_COLUMNS:
            existing = {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}
            if col in existing:
                continue
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {decl}")
        # Back-fill last_reinforced once, using updated_at/created_at as a proxy.
        conn.execute("UPDATE entities SET last_reinforced = updated_at WHERE last_reinforced IS NULL")
        conn.execute("UPDATE observations SET last_reinforced = created_at WHERE last_reinforced IS NULL")
        # Index used by threshold-filtered reads.
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ent_confidence ON entities (confidence, last_reinforced)"
        )

    def _upsert_entity(self, conn: sqlite3.Connection, name: str, etype: str, now: float) -> None:
        """Insert or reinforce. On conflict: bump confidence (reinforcement) and
        touch last_reinforced. Stored confidence is decayed-then-bumped so it
        cannot grow without bound.
        """
        row = conn.execute(
            "SELECT confidence, last_reinforced, entity_type FROM entities WHERE name = ?",
            (name,),
        ).fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO entities (name, entity_type, created_at, updated_at, "
                "confidence, last_reinforced) VALUES (?, ?, ?, ?, 1.0, ?)",
                (name, etype, now, now, now),
            )
            return
        new_conf = reinforced_confidence(
            float(row["confidence"]),
            _safe_epoch(row["last_reinforced"], now),
            str(row["entity_type"]),
            now=now,
        )
        conn.execute(
            "UPDATE entities SET updated_at = ?, confidence = ?, last_reinforced = ? WHERE name = ?",
            (now, new_conf, now, name),
        )

    def _add_obs(self, conn: sqlite3.Connection, name: str, content: str, now: float) -> bool:
        """Insert observation OR reinforce near-duplicate.

        Two-stage dedup:
          1. Exact UNIQUE constraint on (entity_name, content) — fast SQL check.
          2. Jaccard similarity against existing observations on the same entity.
             If any existing row has Jaccard overlap >= jaccard_threshold()
             (default 0.60), REINFORCE that row instead of inserting.

        Returns True if a new row was inserted; False if an existing duplicate
        or near-duplicate was reinforced. Either path is a useful write —
        the caller should NOT treat False as a no-op.
        """
        content = content.strip()
        if not content:
            return False

        etype_row = conn.execute(
            "SELECT entity_type FROM entities WHERE name = ?",
            (name,),
        ).fetchone()
        etype = str(etype_row["entity_type"]) if etype_row else "general"

        # Stage 1: exact-match fast path (UNIQUE constraint).
        existing_exact = conn.execute(
            "SELECT id, confidence, last_reinforced FROM observations WHERE entity_name = ? AND content = ?",
            (name, content),
        ).fetchone()
        if existing_exact is not None:
            self._reinforce_observation(conn, existing_exact, etype, now)
            return False

        # Stage 2: Jaccard near-duplicate check against siblings.
        threshold = jaccard_threshold()
        sibling_rows = conn.execute(
            "SELECT id, content, confidence, last_reinforced FROM observations WHERE entity_name = ?",
            (name,),
        ).fetchall()
        best_sim = 0.0
        best_row = None
        for sib in sibling_rows:
            sim = jaccard_similarity(content, str(sib["content"]))
            if sim > best_sim:
                best_sim = sim
                best_row = sib
        if best_row is not None and best_sim >= threshold:
            self._reinforce_observation(conn, best_row, etype, now)
            return False

        # Stage 3: genuinely new observation — insert.
        try:
            conn.execute(
                "INSERT INTO observations (entity_name, content, created_at, "
                "confidence, last_reinforced) VALUES (?, ?, ?, 1.0, ?)",
                (name, content, now, now),
            )
            return True
        except sqlite3.IntegrityError:
            # Race: a concurrent writer inserted the same content between stages.
            return False

    @staticmethod
    def _reinforce_observation(conn: sqlite3.Connection, row: sqlite3.Row, etype: str, now: float) -> None:
        """Apply reinforcement to an observation row — bumps confidence and
        touches last_reinforced. Shared by exact-match and Jaccard paths."""
        new_conf = reinforced_confidence(
            float(row["confidence"]),
            _safe_epoch(row["last_reinforced"], now),
            etype,
            now=now,
        )
        conn.execute(
            "UPDATE observations SET confidence = ?, last_reinforced = ? WHERE id = ?",
            (new_conf, now, row["id"]),
        )

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
            for e in tqdm(entities, desc="Creating entities", unit="entity", leave=False):
                name = (e.get("name") or "").strip()
                if not name:
                    continue
                etype = (e.get("entityType") or "general").strip()
                if etype not in ALLOWED_ENTITY_TYPES:
                    rejected.append(
                        {
                            "name": name,
                            "entity_type": etype,
                            "reason": f"entity_type '{etype}' not in ALLOWED_ENTITY_TYPES",
                        }
                    )
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
            for rel in tqdm(relations, desc="Creating relations", unit="rel", leave=False):
                from_e = (rel.get("from") or "").strip()
                to_e = (rel.get("to") or "").strip()
                rel_type = (rel.get("relationType") or "related_to").strip()
                if not from_e or not to_e:
                    continue
                if not rel_type:
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

    def search_nodes(self, query: str, include_low_confidence: bool = False) -> list[dict[str, Any]]:
        """Full-text search across entity names, types, and observations.

        By default, entities whose effective confidence is below the read-time
        threshold are hidden. Pass include_low_confidence=True for admin views
        or the consolidation pass.
        """
        query = (query or "").strip()
        if not query:
            return []
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
        loaded = [
            e
            for n in sorted(all_names)
            if (e := self.load_entity(n, include_low_confidence=include_low_confidence))
        ]
        return loaded

    def read_graph(self, include_low_confidence: bool = False) -> dict[str, Any]:
        """Read the complete graph — all entities, observations, and relations.

        Entities below the effective-confidence threshold are hidden unless
        include_low_confidence=True.
        """
        threshold = 0.0 if include_low_confidence else confidence_threshold()
        now = time.time()
        with self.connection() as conn:
            ent_rows = conn.execute(
                "SELECT name, entity_type, confidence, last_reinforced "
                "FROM entities ORDER BY entity_type, name",
            ).fetchall()
            entities = []
            hidden_names: set[str] = set()
            for row in ent_rows:
                eff = effective_confidence(
                    float(row["confidence"]),
                    _safe_epoch(row["last_reinforced"], now),
                    str(row["entity_type"]),
                    now=now,
                )
                if eff < threshold:
                    hidden_names.add(row["name"])
                    continue
                obs_rows = conn.execute(
                    "SELECT content, confidence, last_reinforced FROM observations "
                    "WHERE entity_name = ? ORDER BY created_at",
                    (row["name"],),
                ).fetchall()
                obs = [
                    r["content"]
                    for r in obs_rows
                    if effective_confidence(
                        float(r["confidence"]),
                        float(r["last_reinforced"] or now),
                        str(row["entity_type"]),
                        now=now,
                    )
                    >= threshold
                ]
                entities.append(
                    {
                        "name": row["name"],
                        "entityType": row["entity_type"],
                        "observations": obs,
                        "effectiveConfidence": round(eff, 4),
                    }
                )
            rels = [
                {"from": r["from_entity"], "relationType": r["relation_type"], "to": r["to_entity"]}
                for r in conn.execute(
                    "SELECT from_entity, relation_type, to_entity FROM relations ORDER BY from_entity",
                ).fetchall()
                if r["from_entity"] not in hidden_names and r["to_entity"] not in hidden_names
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
            for item in tqdm(deletions, desc="Deleting observations", unit="item", leave=False):
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

    def load_entity(self, name: str, include_low_confidence: bool = False) -> dict[str, Any] | None:
        """Load a single entity with observations and relations.

        Applies read-time decay. Returns None if the entity is below threshold
        (and include_low_confidence=False). Observations below threshold are
        filtered out but the entity is still returned as long as IT is above.
        """
        threshold = 0.0 if include_low_confidence else confidence_threshold()
        now = time.time()
        with self.connection() as conn:
            row = conn.execute(
                "SELECT name, entity_type, created_at, updated_at, "
                "confidence, last_reinforced FROM entities WHERE name = ?",
                (name,),
            ).fetchone()
            if row is None:
                return None
            etype = str(row["entity_type"])
            eff = effective_confidence(
                float(row["confidence"]),
                _safe_epoch(row["last_reinforced"], now),
                etype,
                now=now,
            )
            if eff < threshold:
                return None
            # Advisory: bump access counter on a successful above-threshold read.
            self._bump_access(conn, name)
            obs_rows = conn.execute(
                "SELECT content, confidence, last_reinforced FROM observations "
                "WHERE entity_name = ? ORDER BY created_at",
                (name,),
            ).fetchall()
            obs = [
                r["content"]
                for r in obs_rows
                if effective_confidence(
                    float(r["confidence"]),
                    float(r["last_reinforced"] or now),
                    etype,
                    now=now,
                )
                >= threshold
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
            "entityType": etype,
            "observations": obs,
            "relations": rels,
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
            "effectiveConfidence": round(eff, 4),
        }

    def get_entities_by_type(
        self, types: tuple[str, ...], include_low_confidence: bool = False
    ) -> list[dict[str, Any]]:
        """Return all entities whose type is in the given tuple, fully loaded.

        Applies read-time decay. Pass include_low_confidence=True to bypass.
        """
        if not types:
            return []
        placeholders = ",".join("?" * len(types))
        with self.connection() as conn:
            rows = conn.execute(
                f"SELECT name FROM entities WHERE entity_type IN ({placeholders}) ORDER BY entity_type, name",
                types,
            ).fetchall()
            names = [row["name"] for row in rows]
        return [e for n in names if (e := self.load_entity(n, include_low_confidence=include_low_confidence))]

    def upsert_entity(self, name: str, etype: str, observations: list[str] | None = None) -> None:
        """Single-entity upsert with optional observation list. Idempotent."""
        now = time.time()
        with self.connection() as conn:
            self._upsert_entity(conn, name, etype, now)
            for obs in observations or []:
                if obs:
                    self._add_obs(conn, name, obs, now)

    def add_observation(self, entity_name: str, content: str) -> bool:
        """Add a single observation to an entity. Returns True if inserted,
        False if the observation already existed (and was reinforced)."""
        if not entity_name or not entity_name.strip():
            return False
        now = time.time()
        with self.connection() as conn:
            self._upsert_entity(conn, entity_name, "general", now)
            return self._add_obs(conn, entity_name, content, now)

    def _bump_access(self, conn: sqlite3.Connection, name: str) -> None:
        """Increment access_count on a successful read. Best-effort — never
        raises. Used to power Ebbinghaus-style frequency reinforcement:
        frequently-accessed memories rank higher in top_entities()."""
        try:
            conn.execute(
                "UPDATE entities SET access_count = access_count + 1 WHERE name = ?",
                (name,),
            )
        except sqlite3.Error:
            # guardian: allow-broad-exception -- access tracking is advisory; never block reads
            pass

    def top_entities(
        self,
        limit: int = 25,
        entity_types: tuple[str, ...] | None = None,
    ) -> list[dict[str, Any]]:
        """Return Tier-1 ranking: entities ranked by effective_confidence *
        log(1 + access_count). This is the "AGENTS.md briefing" list from
        yuvalsuede/memory-mcp — most-useful memories first.
        """
        now = time.time()
        where = ""
        params: tuple[Any, ...] = ()
        if entity_types:
            placeholders = ",".join("?" * len(entity_types))
            where = f"WHERE entity_type IN ({placeholders})"
            params = entity_types
        with self.connection() as conn:
            rows = conn.execute(
                f"SELECT name, entity_type, confidence, last_reinforced, access_count FROM entities {where}",
                params,
            ).fetchall()
        threshold = confidence_threshold()
        scored: list[tuple[float, dict[str, Any]]] = []
        for r in rows:
            eff = effective_confidence(
                float(r["confidence"]),
                float(r["last_reinforced"] or now),
                str(r["entity_type"]),
                now=now,
            )
            if eff < threshold:
                continue
            ac = int(r["access_count"] or 0)
            score = eff * math.log1p(ac)
            # Give all visible entities a floor score so fresh-but-unused
            # memories aren't completely suppressed by never-accessed rank.
            score = max(score, eff * 0.1)
            scored.append(
                (
                    score,
                    {
                        "name": r["name"],
                        "entityType": r["entity_type"],
                        "effectiveConfidence": round(eff, 4),
                        "accessCount": ac,
                        "score": round(score, 4),
                    },
                )
            )
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in scored[:limit]]

    def reinforce(self, name: str) -> bool:
        """Explicitly reinforce an entity without changing its observations.

        Use this when a read-site (e.g., search_nodes hit, open_nodes lookup)
        wants to register use of a memory — future work: call this from the
        MCP server on successful reads to emulate Ebbinghaus frequency effects.
        """
        now = time.time()
        with self.connection() as conn:
            row = conn.execute(
                "SELECT confidence, last_reinforced, entity_type FROM entities WHERE name = ?",
                (name,),
            ).fetchone()
            if row is None:
                return False
            new_conf = reinforced_confidence(
                float(row["confidence"]),
                _safe_epoch(row["last_reinforced"], now),
                str(row["entity_type"]),
                now=now,
            )
            conn.execute(
                "UPDATE entities SET confidence = ?, last_reinforced = ? WHERE name = ?",
                (new_conf, now, name),
            )
        return True

    def insert_relation(self, from_e: str, rel_type: str, to_e: str) -> bool:
        """Insert a single relation. Returns True if inserted, False if duplicate."""
        if not from_e or not to_e or not rel_type or not rel_type.strip():
            return False
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
        if older_than_days < 0:
            raise ValueError("older_than_days must be >= 0")
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
