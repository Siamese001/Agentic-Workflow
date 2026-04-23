"""Internal helpers shared by card emitters.

Keep this module dependency-free so emitters can run in CI without importing
the rest of the stack.
"""

from __future__ import annotations

import math
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

# Layer criticality multipliers — per constitutional §23 / adg-canonical-invariants.md §6.
LAYER_MULTIPLIER: dict[str, float] = {
    "L0": 2.00,
    "L5": 2.00,
    "L3": 1.75,
    "L4": 1.75,
    "L1": 1.00,
    "L2": 1.00,
    "L6": 0.75,
}

# The 5 ADG Surfaces — heuristic mapping from layer / relation kind.
# Layer-primary, edge-secondary.
SURFACE_BY_LAYER: dict[str, str] = {
    "L0": "Execution",
    "L1": "Execution",
    "L2": "Execution",
    "L3": "Execution",
    "L4": "State",
    "L5": "Security",
    "L6": "Observability",
}


def surface_for(layer: str | None) -> str:
    """Return the most likely ADG Surface for a node by its layer."""

    if not layer:
        return "None"
    return SURFACE_BY_LAYER.get(layer, "None")


def layer_multiplier(layer: str | None) -> float:
    """Return the constitutional layer multiplier, default 1.0."""

    if not layer:
        return 1.0
    return LAYER_MULTIPLIER.get(layer, 1.0)


def archetype_for(layer: str | None, fan_in: int, fan_out: int) -> str:
    """Classify a node into one of the 4 hotspot archetypes.

    Rules (deterministic, override-aware):
    - ``SAFETY_GATEKEEPER`` if layer == L5
    - ``STATE_NODE``        if layer == L4
    - ``ORCHESTRATOR``      if layer == L3 OR fan_out >= 2 * fan_in (and fan_out >= 10)
    - ``CENTRAL_DEPENDENCY`` otherwise (default for high-fan-in structural nodes)
    """

    if layer == "L5":
        return "SAFETY_GATEKEEPER"
    if layer == "L4":
        return "STATE_NODE"
    if layer == "L3":
        return "ORCHESTRATOR"
    if fan_out >= 10 and fan_out >= 2 * max(fan_in, 1):
        return "ORCHESTRATOR"
    return "CENTRAL_DEPENDENCY"


def impact_score(violation_count: int, fan_in: int, layer: str | None) -> float:
    """Constitutional impact formula:

    ``impact = violations * (1 + log10(1 + fan_in)) * layer_multiplier``
    """

    return float(violation_count) * (1.0 + math.log10(1 + max(fan_in, 0))) * layer_multiplier(layer)


@contextmanager
def adg_conn(db_path: str | Path) -> Iterator[sqlite3.Connection]:
    """Read-only SQLite connection context manager."""

    path = Path(db_path)
    if not path.exists():
        raise FileNotFoundError(f"ADG sqlite not found: {path}")
    uri = f"file:{path.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=10.0)
    try:
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        conn.close()


def read_snapshot_id(conn: sqlite3.Connection) -> str:
    """Best-effort snapshot id from mv_hotspot_centrality; fallback to 'unknown'."""

    try:
        cur = conn.execute("SELECT snapshot_id FROM mv_hotspot_centrality LIMIT 1")
        row = cur.fetchone()
        if row and row[0]:
            return str(row[0])
    except sqlite3.OperationalError:
        pass
    return "unknown"
