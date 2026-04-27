"""ADG-driven enumeration of L2-capable agent modules.

Maps to: docs/reference/04_L2_Execute/04.5a_L2_Resolution_Context_Invariant.md
Phase 6 TEST CONTRACT — "Every L2-capable agent SHALL be exercised by a
matrix test."

Discovery rule (canonical, deterministic):
  An L2-capable agent module is any Python module whose `resolved_path` in
  the ADG matches one of:
    - `agentic_core/L2_execution/**/*Agent.py`
    - `apps_*/**/*Agent.py`
  and whose ADG `entity_type='module'` and `identity_kind='repo_module'`.

Source-of-truth hierarchy (matches constitutional §28):
  1. Direct read of latest `artifacts/adg/adg_indexed_*.sqlite` snapshot.
     Returned list is sorted by `resolved_path` for determinism.
  2. If no snapshot exists OR query fails, fall back to a static
     representative list (six tier representatives — same shape used by
     the negative-test matrix).
  3. Empty discovery is a fail-closed condition; callers MUST assert
     `len(discover_l2_capable_agents()) > 0` and refuse to proceed.

This module performs zero edits and zero MCP calls. It only reads SQLite.
"""

from __future__ import annotations

import glob
import sqlite3
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_ADG_GLOB = str(_REPO_ROOT / "artifacts" / "adg" / "adg_indexed_*.sqlite")


@dataclass(frozen=True, slots=True)
class L2CapableAgentEntry:
    """One L2-capable agent module discovered via ADG.

    Fields are the minimum the resolution-consistency tests need:
      - module_name  : ADG `adg_name` (e.g. ADG::Module::apps_rg/.../X.py)
      - resolved_path: repo-relative Python file path
      - layer        : ADG layer assignment (L2 or L_APP)
      - source       : 'adg' (discovered) or 'static' (fallback)
    """

    module_name: str
    resolved_path: str
    layer: str
    source: str


# Static representative fallback. Mirrors the 6-tier matrix in
# tests/.../test_l2_pipeline_resolution_invariant.py so a fallback path
# still exercises every routing tier. The names here are illustrative
# identities — the real ADG-driven path returns actual repo modules.
_STATIC_FALLBACK: tuple[L2CapableAgentEntry, ...] = (
    L2CapableAgentEntry(
        "ADG::Module::agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py",
        "agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py",
        "L2",
        "static",
    ),
    L2CapableAgentEntry(
        "ADG::Module::agentic_core/L2_execution/reasoning/RedisSovereignAgent.py",
        "agentic_core/L2_execution/reasoning/RedisSovereignAgent.py",
        "L2",
        "static",
    ),
    L2CapableAgentEntry(
        "ADG::Module::apps_eval/reasoning/QualityGateAgent.py",
        "apps_eval/reasoning/QualityGateAgent.py",
        "L_APP",
        "static",
    ),
    L2CapableAgentEntry(
        "ADG::Module::apps_lic/reasoning/ValidatorAgent.py",
        "apps_lic/reasoning/ValidatorAgent.py",
        "L_APP",
        "static",
    ),
    L2CapableAgentEntry(
        "ADG::Module::apps_rg/reasoning/ContentQualityAgent.py",
        "apps_rg/reasoning/ContentQualityAgent.py",
        "L_APP",
        "static",
    ),
    L2CapableAgentEntry(
        "ADG::Module::apps_shared/reasoning/BaseDispatchAgent.py",
        "apps_shared/reasoning/BaseDispatchAgent.py",
        "L_APP",
        "static",
    ),
)


def _latest_adg_snapshot() -> Path | None:
    """Return the most recent adg_indexed_*.sqlite, or None if none exist."""
    matches = sorted(glob.glob(_ADG_GLOB))
    return Path(matches[-1]) if matches else None


def _query_adg(snapshot: Path) -> tuple[L2CapableAgentEntry, ...]:
    """Execute the canonical L2-capable-agent SELECT against the snapshot.

    Uses ``GLOB`` (case-sensitive) instead of ``LIKE`` (case-insensitive
    by default in SQLite) so that lower-case ``foo_agent.py`` modules are
    NOT classified as L2-capable agents — only PascalCase ``FooAgent.py``
    modules are. Without this, modules like
    ``apps_eval/reasoning/criteria_decomposition_agent.py`` were
    erroneously surfaced as agents and the
    ``test_all_entries_have_required_fields`` invariant
    (``resolved_path.endswith("Agent.py")``) failed.
    """
    con = sqlite3.connect(snapshot)
    try:
        cur = con.cursor()
        cur.execute(
            """
            SELECT DISTINCT adg_name, resolved_path, layer FROM nodes
            WHERE entity_type = 'module'
              AND identity_kind = 'repo_module'
              AND (resolved_path GLOB 'agentic_core/L2_execution/*Agent.py'
                OR resolved_path GLOB 'apps_*/*Agent.py')
            ORDER BY resolved_path
            """
        )
        rows = cur.fetchall()
    finally:
        con.close()
    return tuple(
        L2CapableAgentEntry(
            module_name=str(name),
            resolved_path=str(path),
            layer=str(layer),
            source="adg",
        )
        for name, path, layer in rows
    )


def discover_l2_capable_agents() -> tuple[L2CapableAgentEntry, ...]:
    """Return the canonical list of L2-capable agent modules.

    Order:
      1. Latest ADG snapshot — preferred, deterministic.
      2. Static fallback — only when no snapshot exists OR the SQL query
         raises a recoverable error.

    Result is always sorted by `resolved_path` and never empty when the
    static fallback path is taken. An empty result from the ADG path is
    suspicious but returned as-is — callers MUST fail closed on empty.
    """
    snapshot = _latest_adg_snapshot()
    if snapshot is None:
        return _STATIC_FALLBACK
    try:
        rows = _query_adg(snapshot)
    except (sqlite3.OperationalError, sqlite3.DatabaseError):
        return _STATIC_FALLBACK
    if not rows:
        # Snapshot exists but no rows matched. Suspicious — surface the
        # empty result to the caller rather than silently substituting
        # the static fallback.
        return ()
    return rows


__all__ = [
    "L2CapableAgentEntry",
    "discover_l2_capable_agents",
]
