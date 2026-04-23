"""Shared helpers for W6 temporal / snapshot-diff gates.

Resolves the 2nd most-recent ``adg_indexed_*.sqlite`` as the prior
snapshot for delta computations. Returns ``None`` when only one
snapshot exists (fresh repo / first run); gates treat that as a
compliance pass.
"""

from __future__ import annotations

import glob
import os
import sqlite3
from pathlib import Path

from ops_scripts.ci._adg_wiring_gate_base import ADG_DIR, connect_snapshot, latest_snapshot


def prior_snapshot() -> Path | None:
    """Return the 2nd most-recent adg_indexed_*.sqlite, or None."""
    pattern = str(ADG_DIR / "adg_indexed_*.sqlite")
    matches = sorted(glob.glob(pattern), key=os.path.getmtime)
    if len(matches) < 2:
        return None
    current = latest_snapshot()
    for p in reversed(matches[:-1]):
        cand = Path(p)
        if cand.samefile(current):
            continue
        return cand
    return None


def connect_prior() -> sqlite3.Connection | None:
    """Open a read-only connection to the prior snapshot, or None."""
    p = prior_snapshot()
    if p is None:
        return None
    return connect_snapshot(p)
