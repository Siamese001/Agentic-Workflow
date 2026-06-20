#!/usr/bin/env python3
"""Gate G-UNRESOLVED-RATCHET — count of unresolved edges must not grow.

Reads the latest ADG snapshot, queries ``mv_edges_unresolved``, compares the
count to a stored baseline, fails if current > baseline. Seed via ``--seed``.

Tier: R (ratchet). Companion to ``check_edge_authority_well_formed.py``.

Origin: 2026-04-28 graph-authority directive — "Any downstream hotspot,
coverage, or governance analysis must exclude or downgrade unresolved edges."
This gate enforces the "do not grow unresolved" half of that contract; the
verified-only materialized view enforces the "downstream must filter" half.

Bypass: ``UNRESOLVED_RATCHET_BYPASS=1``.
"""

from __future__ import annotations

# W4 ADG consumer mode declaration (per .codex/rules/adg-canonical-invariants.md
# §6 + agentic_core/adg/artifact/consumer_mode.py).
# Ratchet over RISK_SIGNAL_ONLY edges — this is a hygiene signal, not a verdict.
__adg_consumer_mode__ = "risk"

import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

ADG_DIR = REPO_ROOT / "artifacts" / "adg"
LOG_DIR = REPO_ROOT / "artifacts" / "governance"
LOG_FILE = LOG_DIR / "unresolved_edges_ratchet.jsonl"
BASELINE_DIR = REPO_ROOT / "ops_scripts" / "ci" / "baselines"
BASELINE_FILE = BASELINE_DIR / "unresolved_edges_ratchet.json"


def latest_snapshot() -> Path:
    """Return the latest ADG SQLite snapshot via canonical resolver."""
    override = os.environ.get("ADG_SNAPSHOT", "").strip()
    if override:
        p = Path(override).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"ADG_SNAPSHOT not found: {p}")
        return p
    from tools.adg.shared_modules.path_resolver import latest_sqlite  # noqa: PLC0415

    snap = latest_sqlite()
    if snap is None:
        raise FileNotFoundError(
            f"no adg_indexed_*.sqlite under {ADG_DIR}; regenerate via `python tools/generate_full_adg.py`"
        )
    return snap


def _count_unresolved(snap: Path) -> int:
    con = sqlite3.connect(snap)
    cur = con.cursor()
    # Try the materialized view first; fall back to direct edges query if
    # the view wasn't built (older snapshot pre-authority-axis).
    try:
        cur.execute("SELECT COUNT(*) FROM mv_edges_unresolved")
        return int(cur.fetchone()[0])
    except sqlite3.OperationalError:
        try:
            cur.execute("SELECT COUNT(*) FROM edges WHERE authority = 'unresolved'")
            return int(cur.fetchone()[0])
        except sqlite3.OperationalError:
            # Authority column does not exist — pre-axis snapshot.
            return -1
    finally:
        con.close()


def _load_baseline() -> int | None:
    if not BASELINE_FILE.exists():
        return None
    try:
        return int(json.loads(BASELINE_FILE.read_text(encoding="utf-8")).get("count", 0))
    except (json.JSONDecodeError, OSError, ValueError):
        return None


def _seed_baseline(count: int, snap: Path) -> None:
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    BASELINE_FILE.write_text(
        json.dumps(
            {
                "count": count,
                "seeded_at": datetime.now(timezone.utc).isoformat(),
                "snapshot": str(snap.name),
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> int:
    if os.environ.get("UNRESOLVED_RATCHET_BYPASS", "").strip() == "1":
        print("[G-UNRESOLVED-RATCHET] BYPASSED via UNRESOLVED_RATCHET_BYPASS=1")
        return 0

    snap = latest_snapshot()
    current = _count_unresolved(snap)

    if current < 0:
        print(
            f"[G-UNRESOLVED-RATCHET] snapshot {snap.name} predates the authority axis; "
            f"regenerate ADG to populate edges.authority"
        )
        return 0  # informational; do not block first regeneration

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    if "--seed" in sys.argv:
        _seed_baseline(current, snap)
        print(f"[G-UNRESOLVED-RATCHET] baseline seeded at {current} (snapshot={snap.name})")
        return 0

    baseline = _load_baseline()
    record = {
        "gate": "G-UNRESOLVED-RATCHET",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "snapshot": str(snap),
        "current": current,
        "baseline": baseline,
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    if baseline is None:
        print(
            f"[G-UNRESOLVED-RATCHET] current={current}; baseline unset. Run with --seed to lock the ratchet."
        )
        return 0

    print(f"[G-UNRESOLVED-RATCHET] current={current} baseline={baseline} (snapshot={snap.name})")
    if current > baseline:
        print(
            f"[G-UNRESOLVED-RATCHET] FAIL: unresolved edges grew by {current - baseline}. "
            f"Either fix the new dangling-import targets or seed a new baseline only after "
            f"a deliberate, audited reduction."
        )
        return 1
    if current < baseline:
        print(
            f"[G-UNRESOLVED-RATCHET] IMPROVEMENT: count dropped {baseline} -> {current}. "
            f"Run --seed to lower the ratchet."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
