# guardian: allow-silent_swallower
"""
ADG Behavioral Index — read-only SQLite edge profile reader.

ZERO DEPENDENCIES on agentic_core internals. Uses only Python stdlib.
Safe to import from any layer (L0–L6, apps_*, scripts) without circular
import risk.

Purpose
-------
Provides per-file behavioral signal profiles sourced from the ADG SQLite
artifact. These profiles are consumed by:

  - execute_ssot.py  → RoutingInputs enrichment (deterministic_coverage, N)
  - SovereignDecisionEngine.calculate_healing_confidence()
  - FileClassificationAgent._load_adg_behavioral_profile()

Signal taxonomy (derived from Script vs. Agent.md and ADG edge catalogue)
--------------------------------------------------------------------------

AGENT-SIDE signals (goal-directed, adaptive, stateful):
  generates_prompt, consumes_prompt, orchestrates_healing,
  dispatches_healing_run, gated_by_confidence, escalates_to_human,
  routes_through, agent_executes_agent, snapshots_state,
  observes_runtime_state, validated_by_llm_gateway,
  scores_groundedness, retrieves_via, pulls_context

SCRIPT-SIDE signals (linear, side-effect, deterministic):
  execution_terminates_at_uwg, hard_fails_untranscripted,
  reads_env, reads_config, reads_governed_config

DETERMINISM signals (strong indicator of purely deterministic files):
  reads_policy_state, uses_wall_clock, external_http_call (absence)

ANTI-PATTERN signals (already tagged by ADG scanner):
  antipattern:for_retry  — retry loop, a defining agent-behaviour marker

Scoring
-------
behavioral_score  float [0.0 – 1.0]
  > 0.7   strong AGENT-side evidence
  0.4–0.7 mixed / uncertain
  < 0.4   strong SCRIPT-side evidence

deterministic_coverage  bool
  True when ≥1 SCRIPT-side signal and 0 AGENT-side signals are present.
  Maps directly to RoutingInputs.deterministic_coverage.
"""

from __future__ import annotations

import logging
import sqlite3
import uuid
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Signal taxonomy
# ---------------------------------------------------------------------------

AGENT_SIDE_EDGES: frozenset[str] = frozenset(
    {
        "generates_prompt",
        "consumes_prompt",
        "orchestrates_healing",
        "dispatches_healing_run",
        "gated_by_confidence",
        "escalates_to_human",
        "routes_through",
        "agent_executes_agent",
        "snapshots_state",
        "observes_runtime_state",
        "validated_by_llm_gateway",
        "scores_groundedness",
        "retrieves_via",
        "pulls_context",
        "observes_policy_state",
    }
)

SCRIPT_SIDE_EDGES: frozenset[str] = frozenset(
    {
        "execution_terminates_at_uwg",
        "hard_fails_untranscripted",
        "reads_env",
        "reads_config",
        "reads_governed_config",
    }
)

# Antipattern symbol values that indicate agent-like retry behaviour
AGENT_ANTIPATTERN_SYMBOLS: frozenset[str] = frozenset(
    {
        "for_retry",
    }
)

# All edge types we need to query in a single IN clause
_ALL_TRACKED_EDGES: frozenset[str] = AGENT_SIDE_EDGES | SCRIPT_SIDE_EDGES | frozenset({"antipattern"})


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BehavioralProfile:
    """Immutable behavioral profile for a single source file.

    Attributes
    ----------
    resolved_path:
        Repo-relative path as stored in ADG nodes (forward-slash, no leading slash).
    agent_signals:
        Frozenset of AGENT_SIDE edge types present on this file.
    script_signals:
        Frozenset of SCRIPT_SIDE edge types present on this file.
    antipattern_signals:
        Frozenset of antipattern symbol values (e.g. ``{"for_retry"}``).
    behavioral_score:
        Float [0.0–1.0]. Higher = more agent-like.
    deterministic_coverage:
        True when file has ≥1 script signal and 0 agent signals.
    """

    resolved_path: str
    agent_signals: frozenset[str] = field(default_factory=frozenset)
    script_signals: frozenset[str] = field(default_factory=frozenset)
    antipattern_signals: frozenset[str] = field(default_factory=frozenset)
    behavioral_score: float = 0.5
    deterministic_coverage: bool = False

    @property
    def is_agent_like(self) -> bool:
        return self.behavioral_score > 0.7

    @property
    def is_script_like(self) -> bool:
        return self.deterministic_coverage

    @property
    def has_retry_loop(self) -> bool:
        return bool(self.antipattern_signals & AGENT_ANTIPATTERN_SYMBOLS)

    @property
    def all_signals(self) -> frozenset[str]:
        return self.agent_signals | self.script_signals | self.antipattern_signals


_EMPTY_PROFILE = BehavioralProfile(resolved_path="", behavioral_score=0.5)


def _compute_score(agent_count: int, script_count: int, antipattern_count: int) -> float:
    """Score [0.0–1.0] where 1.0 = maximally agent-like.

    Agent signals and retry antipatterns push toward 1.0.
    Script signals pull toward 0.0.
    Absence of all signals yields 0.5 (unknown).
    """
    total = agent_count + script_count
    if total == 0 and antipattern_count == 0:
        return 0.5
    # Antipatterns count as half an agent signal
    weighted_agent = agent_count + (antipattern_count * 0.5)
    weighted_total = weighted_agent + script_count
    if weighted_total == 0:
        return 0.5
    return round(min(1.0, weighted_agent / weighted_total), 4)


# ---------------------------------------------------------------------------
# ADGBehavioralIndex
# ---------------------------------------------------------------------------


class ADGBehavioralIndex:
    """Read-only view of behavioral edge data from an ADG SQLite artifact.

    Thread-safety: instances are not thread-safe. Callers should use one
    instance per thread or protect with a lock.

    Usage
    -----
    ::

        idx = ADGBehavioralIndex.from_latest(repo_root)
        profile = idx.profile_for("agentic_core/L5_safety/reasoning/FileClassificationAgent.py")
        if profile.is_agent_like:
            ...
        # Or use the module-level singleton helper:
        profile = get_behavioral_profile(path, repo_root)
    """

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._con: sqlite3.Connection | None = None
        self._cache: dict[str, BehavioralProfile] = {}

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_latest(cls, repo_root: Path) -> ADGBehavioralIndex | None:
        """Locate the most-recent ADG SQLite artifact under ``artifacts/adg/``.

        Returns None if no artifact exists (graceful degradation).
        """
        adg_dir = repo_root / "artifacts" / "adg"
        if not adg_dir.exists():
            logger.debug("[ADGBehavioralIndex] artifacts/adg/ not found — degraded mode")
            return None
        # Prefer timestamped files over LATEST symlinks for determinism
        candidates = sorted(adg_dir.glob("adg_indexed_*.sqlite"), reverse=True)
        if not candidates:
            # Fall back to any .sqlite in the directory
            candidates = sorted(adg_dir.glob("*.sqlite"), reverse=True)
        if not candidates:
            logger.debug("[ADGBehavioralIndex] No .sqlite artifact found — degraded mode")
            return None
        return cls(candidates[0])

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def _connect(self) -> bool:
        """Open a read-only connection. Returns False if unavailable."""
        if self._con is not None:
            return True
        if not self._db_path.exists():
            logger.debug("[ADGBehavioralIndex] DB not found: %s", self._db_path)
            return False
        try:
            # uri=True with mode=ro prevents any accidental writes
            uri = self._db_path.as_uri() + "?mode=ro"
            self._con = sqlite3.connect(uri, uri=True, check_same_thread=False)
            self._con.row_factory = sqlite3.Row
            return True
        except sqlite3.OperationalError as exc:
            logger.debug("[ADGBehavioralIndex] Cannot open DB: %s", exc)
            self._con = None
            return False

    def close(self) -> None:
        if self._con is not None:
            try:
                self._con.close()
            except Exception as e:
                logger.debug(f"Error closing SQLite connection: {e}")
            self._con = None

    # ------------------------------------------------------------------
    # Core query
    # ------------------------------------------------------------------

    def profile_for(self, resolved_path: str) -> BehavioralProfile:
        """Return behavioral profile for a single repo-relative path.

        Parameters
        ----------
        resolved_path:
            Forward-slash repo-relative path as stored in ADG nodes,
            e.g. ``"agentic_core/L5_safety/reasoning/FileClassificationAgent.py"``.

        Returns
        -------
        BehavioralProfile
            Always returns a valid object; falls back to neutral profile
            (score=0.5, no signals) when ADG is unavailable.
        """

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"BehavioralIndex.profile_for:{resolved_path}")
        # Normalize: forward slashes, no leading slash
        key = resolved_path.replace("\\", "/").lstrip("/")

        if key in self._cache:
            return self._cache[key]

        if not self._connect():
            return BehavioralProfile(resolved_path=key)

        try:
            profile = self._query_profile(key)
        except Exception as exc:
            logger.debug("[ADGBehavioralIndex] Query failed for %s: %s", key, exc)
            profile = BehavioralProfile(resolved_path=key)

        self._cache[key] = profile
        return profile

    def _query_profile(self, resolved_path: str) -> BehavioralProfile:
        """Execute the SQLite query and build a BehavioralProfile."""
        assert self._con is not None

        # 1. Resolve node id for this path (module-level nodes only)
        cur = self._con.execute(
            "SELECT id FROM nodes WHERE resolved_path = ? AND entity_type = 'module' LIMIT 1",
            (resolved_path,),
        )
        row = cur.fetchone()
        if row is None:
            # Try suffix match for paths stored with different roots
            cur = self._con.execute(
                "SELECT id FROM nodes WHERE resolved_path LIKE ? AND entity_type = 'module' LIMIT 1",
                (f"%{resolved_path}",),
            )
            row = cur.fetchone()
        if row is None:
            return BehavioralProfile(resolved_path=resolved_path)

        node_id = row["id"]

        # 2. Fetch all tracked edge types where this node is the source
        placeholders = ",".join("?" * len(_ALL_TRACKED_EDGES))
        cur = self._con.execute(
            f"""
            SELECT relation_type, symbol
            FROM edges
            WHERE src_id = ?
              AND relation_type IN ({placeholders})
            """,
            (node_id, *sorted(_ALL_TRACKED_EDGES)),
        )
        rows = cur.fetchall()

        agent_signals: set[str] = set()
        script_signals: set[str] = set()
        antipattern_signals: set[str] = set()

        for r in rows:
            rtype = r["relation_type"]
            symbol = (r["symbol"] or "").strip()
            if rtype == "antipattern":
                if symbol in AGENT_ANTIPATTERN_SYMBOLS:
                    antipattern_signals.add(symbol)
            elif rtype in AGENT_SIDE_EDGES:
                agent_signals.add(rtype)
            elif rtype in SCRIPT_SIDE_EDGES:
                script_signals.add(rtype)

        score = _compute_score(len(agent_signals), len(script_signals), len(antipattern_signals))
        det_cov = len(script_signals) > 0 and len(agent_signals) == 0

        return BehavioralProfile(
            resolved_path=resolved_path,
            agent_signals=frozenset(agent_signals),
            script_signals=frozenset(script_signals),
            antipattern_signals=frozenset(antipattern_signals),
            behavioral_score=score,
            deterministic_coverage=det_cov,
        )

    # ------------------------------------------------------------------
    # Bulk query
    # ------------------------------------------------------------------

    def profiles_for(self, resolved_paths: list[str]) -> dict[str, BehavioralProfile]:
        """Bulk-fetch profiles. More efficient than calling profile_for() in a loop."""
        result: dict[str, BehavioralProfile] = {}
        uncached = []
        for p in resolved_paths:
            key = p.replace("\\", "/").lstrip("/")
            if key in self._cache:
                result[key] = self._cache[key]
            else:
                uncached.append(key)

        if not uncached or not self._connect():
            for p in uncached:
                result[p] = BehavioralProfile(resolved_path=p)
            return result

        try:
            # Resolve all node IDs in one query
            placeholders = ",".join("?" * len(uncached))
            cur = self._con.execute(
                f"SELECT id, resolved_path FROM nodes WHERE resolved_path IN ({placeholders}) AND entity_type='module'",
                uncached,
            )
            id_to_path: dict[int, str] = {r["id"]: r["resolved_path"] for r in cur.fetchall()}

            if not id_to_path:
                for p in uncached:
                    result[p] = BehavioralProfile(resolved_path=p)
                return result

            # Fetch all edges for those node IDs in one query
            id_placeholders = ",".join("?" * len(id_to_path))
            edge_placeholders = ",".join("?" * len(_ALL_TRACKED_EDGES))
            cur = self._con.execute(
                f"""
                SELECT src_id, relation_type, symbol
                FROM edges
                WHERE src_id IN ({id_placeholders})
                  AND relation_type IN ({edge_placeholders})
                """,
                (*id_to_path.keys(), *sorted(_ALL_TRACKED_EDGES)),
            )
            # Accumulate per node
            per_node: dict[int, dict[str, set[str]]] = {
                nid: {"agent": set(), "script": set(), "anti": set()} for nid in id_to_path
            }
            for r in cur.fetchall():
                nid = r["src_id"]
                rtype = r["relation_type"]
                symbol = (r["symbol"] or "").strip()
                if rtype == "antipattern" and symbol in AGENT_ANTIPATTERN_SYMBOLS:
                    per_node[nid]["anti"].add(symbol)
                elif rtype in AGENT_SIDE_EDGES:
                    per_node[nid]["agent"].add(rtype)
                elif rtype in SCRIPT_SIDE_EDGES:
                    per_node[nid]["script"].add(rtype)

            for nid, path in id_to_path.items():
                buckets = per_node[nid]
                score = _compute_score(len(buckets["agent"]), len(buckets["script"]), len(buckets["anti"]))
                det_cov = len(buckets["script"]) > 0 and len(buckets["agent"]) == 0
                profile = BehavioralProfile(
                    resolved_path=path,
                    agent_signals=frozenset(buckets["agent"]),
                    script_signals=frozenset(buckets["script"]),
                    antipattern_signals=frozenset(buckets["anti"]),
                    behavioral_score=score,
                    deterministic_coverage=det_cov,
                )
                self._cache[path] = profile
                result[path] = profile

            # Fill in any paths that had no node in the DB
            for p in uncached:
                if p not in result:
                    result[p] = BehavioralProfile(resolved_path=p)

        except Exception as exc:
            logger.debug("[ADGBehavioralIndex] Bulk query failed: %s", exc)
            for p in uncached:
                result[p] = BehavioralProfile(resolved_path=p)

        return result

    def __enter__(self) -> ADGBehavioralIndex:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


# ---------------------------------------------------------------------------
# Module-level convenience helper (cached per repo_root)
# ---------------------------------------------------------------------------


@lru_cache(maxsize=4)
def _get_index(db_path: str) -> ADGBehavioralIndex:
    """Return a cached ADGBehavioralIndex for a given DB path."""
    return ADGBehavioralIndex(Path(db_path))


def get_behavioral_profile(
    file_path: Path | str,
    repo_root: Path | str | None = None,
) -> BehavioralProfile:
    """Convenience function: return a behavioral profile for a single file.

    Parameters
    ----------
    file_path:
        Absolute or repo-relative path to the Python file.
    repo_root:
        Repo root directory. If None, derived from file_path by walking up
        to a directory containing ``.git`` or ``pyproject.toml``.

    Returns
    -------
    BehavioralProfile
        Neutral profile (score=0.5) when ADG is unavailable.
    """
    file_path = Path(file_path)

    if repo_root is None:
        # Walk up to find repo root
        candidate = file_path if file_path.is_dir() else file_path.parent
        for parent in [candidate, *candidate.parents]:
            if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
                repo_root = parent
                break
        else:
            return BehavioralProfile(resolved_path=str(file_path))

    repo_root = Path(repo_root)
    adg_dir = repo_root / "artifacts" / "adg"
    candidates = sorted(adg_dir.glob("adg_indexed_*.sqlite"), reverse=True) if adg_dir.exists() else []
    if not candidates:
        return BehavioralProfile(resolved_path=str(file_path))

    db_path_str = str(candidates[0])
    index = _get_index(db_path_str)

    # Compute repo-relative path
    try:
        rel = file_path.resolve().relative_to(repo_root.resolve())
        resolved = rel.as_posix()
    except ValueError:
        resolved = file_path.as_posix()

    return index.profile_for(resolved)


__all__ = [
    "ADGBehavioralIndex",
    "BehavioralProfile",
    "AGENT_SIDE_EDGES",
    "SCRIPT_SIDE_EDGES",
    "AGENT_ANTIPATTERN_SYMBOLS",
    "get_behavioral_profile",
]
