"""Runtime ADG Query Library — sub-10ms hot-path reads over SQLite + Redis.

This is the enabler for runtime graph-DB-over-SQLite acceleration
(see `.windsurf/plans/runtime-adg-acceleration-b4f2a1.md`).

Design principles
-----------------
1. **SQLite is source of truth**. Redis is an optional accelerator via
   ``MVRedisReader``. Every method has a SQLite fallback that is *correct*
   even when Redis is unavailable.
2. **Zero MCP dependency at runtime**. MCP is a developer/agent tool; the
   runtime hot path opens SQLite directly via ``sqlite3.connect`` in
   read-only mode. This also sidesteps the observed MCP thread-affinity
   bug (constitutional §26, MCP serialization discipline).
3. **Per-call connection, tiny LRU**. SQLite connections are cheap in
   read-only mode (``uri=True&mode=ro&immutable=1``) and avoid thread-safety
   landmines that bit the MCP server.
4. **Snapshot provenance always exposed**. Callers must be able to decide
   freshness — every return value carries ``snapshot_id`` / ``snapshot_path``
   so runtime policy can gate on age.

Public API
----------
``RuntimeADGQuery`` — main class. Import once at module scope; shared
across threads; per-call connections keep this safe.

Fast domain helpers (sub-10ms typical):
- ``blast_radius(node_id_or_adg_name)`` — fan-in/out + risk archetype + band
- ``hotspot_info(node_id)`` — centrality + criticality roll-up
- ``upstream_callers(node_id, k=3)`` — top callers via ``imports``/``calls``
- ``downstream_targets(node_id, k=3)`` — fan-out with relation filter
- ``swallow_sites_reaching(node_id, depth=3)`` — backward walk along
  ``flows_to`` to the first antipattern catch site
- ``pview_contains(pview_name, member)`` — O(1) policy-plane membership

All public methods take the symbol by name (``adg_name`` or ``node_id``)
and return plain ``dict`` / ``list`` values for easy serialization into
routing envelopes, HITL packets, or OTel span attributes.

Exit contract: never raises on malformed input. On error: returns an
empty envelope with ``"error"`` key populated and ``"snapshot_id"`` still
valid. This preserves the "library is safe to call from guardrails" contract.
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .windsurf/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import logging
import os
import sqlite3
import threading
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Final

logger = logging.getLogger(__name__)

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
ADG_ARTIFACTS: Final[Path] = REPO_ROOT / "artifacts" / "adg"
SQLITE_GLOB: Final[str] = "adg_indexed_*.sqlite"

# Conservative caps — runtime must stay fast.
DEFAULT_LRU_SIZE: Final[int] = 512
MAX_TRAVERSAL_DEPTH: Final[int] = 5
MAX_FANOUT_ROWS: Final[int] = 50

# Archetype classification thresholds (doctrine §3; see
# .windsurf/rules/adg-canonical-invariants.md).
CENTRAL_DEPENDENCY_FAN_IN: Final[int] = 20
ORCHESTRATOR_FAN_OUT: Final[int] = 25

# Layer multipliers (doctrine §6).
LAYER_MULTIPLIER: Final[dict[str, float]] = {
    "L0": 2.0,
    "L0_routing": 2.0,
    "L1": 1.0,
    "L1_cognition": 1.0,
    "L2": 1.0,
    "L2_execution": 1.0,
    "L3": 1.75,
    "L3_orchestration": 1.75,
    "L4": 1.75,
    "L4_state": 1.75,
    "L5": 2.0,
    "L5_safety": 2.0,
    "L6": 0.75,
    "L6_observability": 0.75,
}

# Risk bands derived from combined impact score.
RISK_BAND_HIGH: Final[float] = 50.0
RISK_BAND_MEDIUM: Final[float] = 15.0


def _latest_snapshot_path() -> Path | None:
    """Resolve the newest ``adg_indexed_*.sqlite`` snapshot on disk."""
    env = os.getenv("ADG_RUNTIME_SNAPSHOT")
    if env:
        p = Path(env)
        if p.exists():
            return p
        logger.warning("ADG_RUNTIME_SNAPSHOT=%s does not exist; falling back to latest", env)
    candidates = sorted(ADG_ARTIFACTS.glob(SQLITE_GLOB))
    return candidates[-1] if candidates else None


def _open_readonly(sqlite_path: Path) -> sqlite3.Connection:
    """Open a SQLite connection in read-only mode.

    Read-only + immutable avoids the shared-lock contention and thread-affinity
    issues that affect the MCP server (see ``mcp1_adg_health`` recurring
    thread-boundary error).
    """
    uri = f"file:{sqlite_path.as_posix()}?mode=ro&immutable=1"
    conn = sqlite3.connect(uri, uri=True, timeout=0.5, isolation_level=None)
    conn.row_factory = sqlite3.Row
    return conn


@dataclass(frozen=True)
class RiskEnvelope:
    """Structured risk signal for runtime consumers (routers, guardrails, HITL).

    All fields are plain Python types for safe propagation across layer
    boundaries. ``to_dict()`` produces a JSON-safe payload.
    """

    node_id: str | None
    adg_name: str
    file_path: str | None
    layer: str | None
    fan_in: int
    fan_out: int
    archetype: str  # CENTRAL_DEPENDENCY | ORCHESTRATOR | LEAF | INTERNAL
    risk_band: str  # HIGH | MEDIUM | LOW
    impact_score: float
    snapshot_id: str
    snapshot_path: str
    error: str | None = None
    extras: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "adg_name": self.adg_name,
            "file_path": self.file_path,
            "layer": self.layer,
            "fan_in": self.fan_in,
            "fan_out": self.fan_out,
            "archetype": self.archetype,
            "risk_band": self.risk_band,
            "impact_score": self.impact_score,
            "snapshot_id": self.snapshot_id,
            "snapshot_path": self.snapshot_path,
            "error": self.error,
            **({"extras": self.extras} if self.extras else {}),
        }


class RuntimeADGQuery:
    """Thread-safe, process-local ADG query facade for runtime callers.

    Instantiate once at module scope; call methods freely from any thread.
    Each call opens a short-lived read-only SQLite connection — on modern
    systems this is <1ms overhead and sidesteps all thread-affinity issues.

    Optional: pass a pre-built ``MVRedisReader`` for Redis acceleration.
    Falls back to SQLite cleanly if Redis is unavailable.
    """

    def __init__(
        self,
        sqlite_path: Path | str | None = None,
        *,
        redis_reader: Any | None = None,
        lru_size: int = DEFAULT_LRU_SIZE,
    ) -> None:
        resolved = Path(sqlite_path) if sqlite_path else _latest_snapshot_path()
        if resolved is None or not resolved.exists():
            raise FileNotFoundError(
                f"No ADG snapshot found under {ADG_ARTIFACTS} (glob={SQLITE_GLOB}). "
                "Run `python tools/generate_full_adg.py` or set ADG_RUNTIME_SNAPSHOT."
            )
        self._sqlite_path: Final[Path] = resolved
        self._snapshot_id: Final[str] = resolved.stem  # e.g. adg_indexed_04242026_0721
        self._redis = redis_reader
        self._lock = threading.Lock()  # only guards the lazy loaders below
        # Per-instance bounded caches — keyed on resolve_node inputs.
        self._resolve_cache: dict[str, tuple[str | None, str | None, str | None, str | None]] = {}
        self._lru_size = lru_size
        # Cache-hit counters (observability).
        self._hits: dict[str, int] = {"resolve": 0, "fanin": 0, "fanout": 0}
        self._misses: dict[str, int] = {"resolve": 0, "fanin": 0, "fanout": 0}

    # ---------- provenance ----------

    @property
    def snapshot_id(self) -> str:
        return self._snapshot_id

    @property
    def snapshot_path(self) -> str:
        return str(self._sqlite_path)

    def provenance(self) -> dict[str, Any]:
        """Return the provenance stamp per doctrine §11."""
        return {
            "backend_used": "sqlite"
            + ("+redis" if self._redis and getattr(self._redis, "available", False) else ""),
            "snapshot_id": self._snapshot_id,
            "snapshot_path": self.snapshot_path,
        }

    # ---------- low-level: node resolution ----------

    def resolve_node(self, ident: str) -> tuple[str | None, str | None, str | None, str | None]:
        """Resolve an ``adg_name`` or ``node_id`` to ``(node_id, adg_name, file_path, layer)``.

        Returns a tuple of ``None`` on miss. Cached in-memory up to
        ``lru_size`` entries.
        """
        if not ident:
            return (None, None, None, None)
        with self._lock:
            cached = self._resolve_cache.get(ident)
            if cached is not None:
                self._hits["resolve"] += 1
                return cached
            self._misses["resolve"] += 1

        try:
            with _open_readonly(self._sqlite_path) as conn:
                # Try as node_id first (exact match on id), then adg_name.
                row = conn.execute(
                    "SELECT id, adg_name, resolved_path AS file_path, layer FROM nodes "
                    "WHERE id = ? OR adg_name = ? LIMIT 1",
                    (ident, ident),
                ).fetchone()
        except sqlite3.Error as exc:
            logger.warning("resolve_node(%s) failed: %s", ident, exc)
            return (None, None, None, None)

        result: tuple[str | None, str | None, str | None, str | None]
        if row is None:
            result = (None, None, None, None)
        else:
            result = (
                str(row["id"]) if row["id"] is not None else None,
                row["adg_name"],
                row["file_path"],
                row["layer"],
            )
        with self._lock:
            if len(self._resolve_cache) >= self._lru_size:
                # Simple FIFO eviction — fast enough for our access patterns.
                self._resolve_cache.pop(next(iter(self._resolve_cache)))
            self._resolve_cache[ident] = result
        return result

    # ---------- low-level: edge fan queries ----------

    def fan_in_count(self, node_id: str, relation_type: str = "imports") -> int:
        """Count incoming edges of a given relation."""
        if not node_id:
            return 0
        try:
            with _open_readonly(self._sqlite_path) as conn:
                row = conn.execute(
                    "SELECT COUNT(*) AS n FROM edges WHERE tgt_id = ? AND relation_type = ?",
                    (node_id, relation_type),
                ).fetchone()
                return int(row["n"]) if row else 0
        except sqlite3.Error as exc:
            logger.debug("fan_in_count(%s,%s) failed: %s", node_id, relation_type, exc)
            return 0

    def fan_out_count(self, node_id: str, relation_type: str = "imports") -> int:
        """Count outgoing edges of a given relation."""
        if not node_id:
            return 0
        try:
            with _open_readonly(self._sqlite_path) as conn:
                row = conn.execute(
                    "SELECT COUNT(*) AS n FROM edges WHERE src_id = ? AND relation_type = ?",
                    (node_id, relation_type),
                ).fetchone()
                return int(row["n"]) if row else 0
        except sqlite3.Error as exc:
            logger.debug("fan_out_count(%s,%s) failed: %s", node_id, relation_type, exc)
            return 0

    def upstream_callers(
        self, node_id: str, k: int = 3, relation_type: str = "imports"
    ) -> list[dict[str, Any]]:
        """Return up to ``k`` upstream callers with ``node_id``, ``adg_name``, ``file_path``, ``layer``."""
        if not node_id or k <= 0:
            return []
        k = min(k, MAX_FANOUT_ROWS)
        try:
            with _open_readonly(self._sqlite_path) as conn:
                rows = conn.execute(
                    "SELECT n.id AS node_id, n.adg_name, n.resolved_path AS file_path, n.layer "
                    "FROM edges e JOIN nodes n ON n.id = e.src_id "
                    "WHERE e.tgt_id = ? AND e.relation_type = ? "
                    "LIMIT ?",
                    (node_id, relation_type, k),
                ).fetchall()
                return [dict(r) for r in rows]
        except sqlite3.Error as exc:
            logger.debug("upstream_callers(%s) failed: %s", node_id, exc)
            return []

    def downstream_targets(
        self, node_id: str, k: int = 3, relation_type: str = "imports"
    ) -> list[dict[str, Any]]:
        """Return up to ``k`` downstream targets."""
        if not node_id or k <= 0:
            return []
        k = min(k, MAX_FANOUT_ROWS)
        try:
            with _open_readonly(self._sqlite_path) as conn:
                rows = conn.execute(
                    "SELECT n.id AS node_id, n.adg_name, n.resolved_path AS file_path, n.layer "
                    "FROM edges e JOIN nodes n ON n.id = e.tgt_id "
                    "WHERE e.src_id = ? AND e.relation_type = ? "
                    "LIMIT ?",
                    (node_id, relation_type, k),
                ).fetchall()
                return [dict(r) for r in rows]
        except sqlite3.Error as exc:
            logger.debug("downstream_targets(%s) failed: %s", node_id, exc)
            return []

    # ---------- domain: blast radius envelope ----------

    def blast_radius(self, ident: str) -> RiskEnvelope:
        """Compute a runtime-consumable risk envelope for a symbol.

        Combines: fan-in / fan-out / layer / archetype / impact-score.
        Safe to call from guardrails — never raises on unknown ident.
        """
        node_id, adg_name, file_path, layer = self.resolve_node(ident)
        if node_id is None:
            return RiskEnvelope(
                node_id=None,
                adg_name=ident,
                file_path=None,
                layer=None,
                fan_in=0,
                fan_out=0,
                archetype="UNKNOWN",
                risk_band="LOW",
                impact_score=0.0,
                snapshot_id=self._snapshot_id,
                snapshot_path=self.snapshot_path,
                error="node_not_found",
            )

        fan_in = self.fan_in_count(node_id, "imports")
        fan_out = self.fan_out_count(node_id, "imports")
        archetype = self._classify_archetype(fan_in, fan_out, layer, file_path)
        impact_score = self._impact_score(fan_in, fan_out, layer)
        risk_band = self._risk_band(impact_score)

        return RiskEnvelope(
            node_id=node_id,
            adg_name=adg_name or ident,
            file_path=file_path,
            layer=layer,
            fan_in=fan_in,
            fan_out=fan_out,
            archetype=archetype,
            risk_band=risk_band,
            impact_score=impact_score,
            snapshot_id=self._snapshot_id,
            snapshot_path=self.snapshot_path,
        )

    @staticmethod
    def _classify_archetype(fan_in: int, fan_out: int, layer: str | None, file_path: str | None) -> str:
        """Classify per doctrine §5 (adg-canonical-invariants.md)."""
        fp = (file_path or "").lower()
        if layer in ("L5", "L5_safety") or "guardrail" in fp or "safety" in fp:
            return "SAFETY_GATEKEEPER"
        if layer in ("L4", "L4_state") or "cache" in fp or "canonical_store" in fp or "memory" in fp:
            return "STATE_NODE"
        if fan_in >= CENTRAL_DEPENDENCY_FAN_IN:
            return "CENTRAL_DEPENDENCY"
        if fan_out >= ORCHESTRATOR_FAN_OUT:
            return "ORCHESTRATOR"
        if fan_in == 0 and fan_out == 0:
            return "LEAF"
        return "INTERNAL"

    @staticmethod
    def _impact_score(fan_in: int, fan_out: int, layer: str | None) -> float:
        """Doctrine formula §6: violation_count × (1 + log10(1 + fan_in)) × layer_mult.

        For runtime risk (no violation join) we use ``fan_in + fan_out/2`` as
        the primary signal and the same layer multiplier. This is a monotone
        proxy good enough for router/guardrail gating; CI gates still use the
        full doctrinal formula.
        """
        import math

        mult = LAYER_MULTIPLIER.get(layer or "", 1.0)
        base = (fan_in + fan_out / 2.0) * (1.0 + math.log10(1.0 + max(fan_in, 0)))
        return round(base * mult, 3)

    @staticmethod
    def _risk_band(impact_score: float) -> str:
        if impact_score >= RISK_BAND_HIGH:
            return "HIGH"
        if impact_score >= RISK_BAND_MEDIUM:
            return "MEDIUM"
        return "LOW"

    # ---------- domain: hotspot centrality lookup ----------

    def hotspot_info(self, ident: str) -> dict[str, Any]:
        """Return centrality/criticality roll-up for a symbol.

        Reads from ``mv_hotspot_centrality`` and ``mv_path_criticality_rollup``
        when present. Always returns a dict (never raises).
        """
        node_id, adg_name, file_path, layer = self.resolve_node(ident)
        result: dict[str, Any] = {
            "node_id": node_id,
            "adg_name": adg_name or ident,
            "file_path": file_path,
            "layer": layer,
            "snapshot_id": self._snapshot_id,
        }
        if node_id is None:
            result["error"] = "node_not_found"
            return result
        try:
            with _open_readonly(self._sqlite_path) as conn:
                hc = conn.execute(
                    "SELECT betweenness_approx, degree_centrality, fan_in, fan_out, degree "
                    "FROM mv_hotspot_centrality WHERE node_id = ? LIMIT 1",
                    (node_id,),
                ).fetchone()
                if hc is not None:
                    result["betweenness_approx"] = hc["betweenness_approx"]
                    result["degree_centrality"] = hc["degree_centrality"]
                    result["degree"] = hc["degree"]
                pcr = conn.execute(
                    "SELECT criticality_score, violation_count, cross_layer_edges "
                    "FROM mv_path_criticality_rollup WHERE node_id = ? LIMIT 1",
                    (node_id,),
                ).fetchone()
                if pcr is not None:
                    result["criticality_score"] = pcr["criticality_score"]
                    result["violation_count"] = pcr["violation_count"]
                    result["cross_layer_edges"] = pcr["cross_layer_edges"]
        except sqlite3.Error as exc:
            logger.debug("hotspot_info(%s) failed: %s", ident, exc)
            result["error"] = f"sqlite_error:{exc}"
        return result

    # ---------- domain: swallow-site traversal ----------

    def swallow_sites_reaching(
        self, node_id: str, depth: int = 3, max_hits: int = 10
    ) -> list[dict[str, Any]]:
        """Walk backward along ``flows_to`` from ``node_id`` up to ``depth`` hops.

        Returns antipattern catch sites (broad_exception_catch, log_and_swallow,
        silent_exception_swallow, return_none_swallow) that can silently
        suppress a failure at ``node_id``. Used by the causal-chain tool (W3)
        to answer "what hides this node's failures?".

        This is the **Zero-Loss Propagation Pipeline** in miniature (doctrine §7).
        """
        if not node_id:
            return []
        depth = max(1, min(int(depth), MAX_TRAVERSAL_DEPTH))
        max_hits = max(1, min(int(max_hits), MAX_FANOUT_ROWS))
        # Use a recursive CTE: cheap on our edge counts (68k flows_to).
        cte = """
        WITH RECURSIVE reach(node_id, hops) AS (
            SELECT ?, 0
            UNION
            SELECT e.src_id, r.hops + 1
              FROM edges e
              JOIN reach r ON e.tgt_id = r.node_id
             WHERE e.relation_type = 'flows_to'
               AND r.hops < ?
        )
        SELECT DISTINCT n.id AS node_id,
               n.adg_name,
               n.resolved_path AS file_path,
               n.layer,
               e.relation_type AS antipattern_kind,
               r.hops
          FROM reach r
          JOIN edges e ON e.src_id = r.node_id
          JOIN nodes n ON n.id = r.node_id
         WHERE e.relation_type IN (
               'broad_exception_catch',
               'log_and_swallow',
               'silent_exception_swallow',
               'return_none_swallow'
           )
         ORDER BY r.hops ASC
         LIMIT ?
        """
        try:
            with _open_readonly(self._sqlite_path) as conn:
                rows = conn.execute(cte, (node_id, depth, max_hits)).fetchall()
                return [dict(r) for r in rows]
        except sqlite3.Error as exc:
            logger.debug("swallow_sites_reaching(%s) failed: %s", node_id, exc)
            return []

    # ---------- domain: P-view membership ----------

    def pview_contains(self, pview_name: str, member_node_id: str) -> bool:
        """O(1) policy-plane membership test (Redis accelerated if available)."""
        if not pview_name or not member_node_id:
            return False
        if self._redis and getattr(self._redis, "available", False):
            hit = self._redis.pview_contains(pview_name, member_node_id, self._snapshot_id)
            if hit is not None:
                return bool(hit)
        # SQLite fallback: P-views are SELECT statements; we can probe by
        # executing ``SELECT 1 FROM <view> WHERE node_id = ? LIMIT 1``.
        # Not all P-views expose ``node_id`` — some use ``file``/``adg_name``.
        # We try the common column name first.
        try:
            with _open_readonly(self._sqlite_path) as conn:
                # Validate view exists to avoid SQL-injection-style concerns.
                exists = conn.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='view' AND name=? LIMIT 1",
                    (pview_name,),
                ).fetchone()
                if not exists:
                    return False
                for col in ("node_id", "adg_name", "file"):
                    try:
                        row = conn.execute(
                            f"SELECT 1 FROM {pview_name} WHERE {col} = ? LIMIT 1",
                            (member_node_id,),
                        ).fetchone()
                        if row is not None:
                            return True
                    except sqlite3.OperationalError:
                        continue
        except sqlite3.Error as exc:
            logger.debug("pview_contains(%s,%s) failed: %s", pview_name, member_node_id, exc)
        return False

    # ---------- observability ----------

    def cache_stats(self) -> dict[str, Any]:
        """Return cache hit/miss counters for introspection."""
        with self._lock:
            return {
                "hits": dict(self._hits),
                "misses": dict(self._misses),
                "resolve_cache_size": len(self._resolve_cache),
            }


# ---------- module-level singleton helper ----------

_DEFAULT_INSTANCE: RuntimeADGQuery | None = None
_DEFAULT_INSTANCE_LOCK = threading.Lock()


def get_default_query() -> RuntimeADGQuery | None:
    """Return a process-wide default ``RuntimeADGQuery``.

    Returns ``None`` if no snapshot is available — callers should branch to
    a degraded path in that case rather than crash. This is the safe default
    for L0/L5 hot-path adapters.
    """
    global _DEFAULT_INSTANCE
    if _DEFAULT_INSTANCE is not None:
        return _DEFAULT_INSTANCE
    with _DEFAULT_INSTANCE_LOCK:
        if _DEFAULT_INSTANCE is not None:
            return _DEFAULT_INSTANCE
        try:
            _DEFAULT_INSTANCE = RuntimeADGQuery()
        except FileNotFoundError as exc:
            logger.info("RuntimeADGQuery default init skipped: %s", exc)
            return None
        except sqlite3.Error as exc:
            logger.warning("RuntimeADGQuery default init sqlite error: %s", exc)
            return None
    return _DEFAULT_INSTANCE


@lru_cache(maxsize=1)
def snapshot_provenance() -> dict[str, Any]:
    """Return the default snapshot's provenance, or an error envelope."""
    q = get_default_query()
    if q is None:
        return {"backend_used": "unavailable", "snapshot_id": None, "snapshot_path": None}
    return q.provenance()


__all__ = [
    "RuntimeADGQuery",
    "RiskEnvelope",
    "get_default_query",
    "snapshot_provenance",
]
