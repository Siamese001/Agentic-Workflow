#!/usr/bin/env python3
"""
check_l5_hotspot_fanin_ratchet.py — CI gate enforcing G01/G16 fan-in ceiling.

The L5 hotspots `runtime_gates/types.py` (fan_in=198) and `v5/__init__.py`
(fan_in=115) are too entangled to refactor in one session. This gate
prevents regression by ratcheting the fan-in ceiling. Any commit that
*increases* the fan-in for these hotspots fails CI; any commit that
decreases it tightens the ratchet.

Source: ADR-070 §Hotspot Concentration (2026-04-29 baseline).

Baselines stored in `.cursor/config/l5_fanin_ratchet.json`. To tighten
after a successful refactor:

    python ops_scripts/ci/check_l5_hotspot_fanin_ratchet.py --update

Exit codes:
    0 = pass (current ≤ baseline for every tracked hotspot)
    1 = fail (regression — fan-in increased)
    2 = error (no ADG snapshot or schema mismatch)
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import argparse
import json
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RATCHET_FILE = REPO_ROOT / ".cursor" / "config" / "l5_fanin_ratchet.json"

# Initial baselines — captured 2026-04-29 from adg_indexed_04282026_2152.sqlite
DEFAULT_RATCHET: dict[str, int] = {
    "agentic_core/L5_safety/runtime_gates/types.py": 198,
    "agentic_core/L5_safety/v5/__init__.py": 115,
    "agentic_core/L5_safety/types/cst_transformers_types.py": 107,
    "agentic_core/L5_safety/config/structure_blueprint/__init__.py": 106,
    "agentic_core/L5_safety/v5/types.py": 103,
    "agentic_core/L5_safety/config/structure_blueprint/ssot.py": 80,
    "agentic_core/L5_safety/runtime_gates/__init__.py": 61,
    "agentic_core/L5_safety/adapters/human_approval_adapter.py": 50,
    "agentic_core/L5_safety/enforcement/ingress_envelope_check.py": 49,
    "agentic_core/L5_safety/runtime_gates/base.py": 48,
}


def find_latest_snapshot() -> Path | None:
    """Return the latest ADG SQLite snapshot via canonical resolver."""
    from tools.adg.shared_modules.path_resolver import latest_sqlite  # noqa: PLC0415

    return latest_sqlite()


def load_ratchet() -> dict[str, int]:
    if RATCHET_FILE.exists():
        return json.loads(RATCHET_FILE.read_text(encoding="utf-8"))
    return DEFAULT_RATCHET


def save_ratchet(ratchet: dict[str, int]) -> None:
    RATCHET_FILE.parent.mkdir(parents=True, exist_ok=True)
    RATCHET_FILE.write_text(
        json.dumps(ratchet, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def query_current(snap: Path, paths: list[str]) -> dict[str, int]:
    """Query mv_hotspot_centrality for each tracked path."""
    con = sqlite3.connect(snap)
    cur = con.cursor()
    out: dict[str, int] = {}
    for p in paths:
        cur.execute(
            "SELECT fan_in FROM mv_hotspot_centrality WHERE resolved_path = ? AND layer = 'L5'",
            (p,),
        )
        row = cur.fetchone()
        out[p] = int(row[0]) if row else 0
    con.close()
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="L5 hotspot fan-in ratchet gate")
    parser.add_argument("--update", action="store_true",
                        help="Tighten the ratchet to current values (only if all paths regressed downward)")
    parser.add_argument("--json", action="store_true", help="Emit JSON status")
    args = parser.parse_args()

    snap = find_latest_snapshot()
    if snap is None:
        print("ERROR: no ADG snapshot at artifacts/adg/adg_indexed_*.sqlite", file=sys.stderr)
        return 2

    ratchet = load_ratchet()
    current = query_current(snap, list(ratchet.keys()))

    regressions: list[tuple[str, int, int]] = []
    improvements: list[tuple[str, int, int]] = []
    for path, baseline in ratchet.items():
        cur = current.get(path, 0)
        if cur > baseline:
            regressions.append((path, baseline, cur))
        elif cur < baseline:
            improvements.append((path, baseline, cur))

    status = {
        "snapshot": snap.name,
        "ratchet_file": str(RATCHET_FILE.relative_to(REPO_ROOT)),
        "tracked_paths": len(ratchet),
        "regressions": [
            {"path": p, "baseline": b, "current": c} for p, b, c in regressions
        ],
        "improvements": [
            {"path": p, "baseline": b, "current": c} for p, b, c in improvements
        ],
        "pass": not regressions,
    }

    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print(f"  Snapshot:        {snap.name}")
        print(f"  Tracked paths:   {len(ratchet)}")
        if regressions:
            print(f"  REGRESSIONS:")
            for path, b, c in regressions:
                print(f"     ✗ {path}: baseline={b} current={c} (+{c - b})")
        if improvements:
            print(f"  Improvements:")
            for path, b, c in improvements:
                print(f"     ✔ {path}: baseline={b} current={c} (-{b - c})")
        print(f"  Result:          {'PASS' if not regressions else 'FAIL'}")

    if args.update:
        if regressions:
            print("\n  Cannot --update with active regressions; refactor first.", file=sys.stderr)
            return 1
        if not improvements:
            print("\n  No improvements to tighten — ratchet unchanged.")
            return 0
        new_ratchet = {**ratchet, **{p: c for p, _, c in improvements}}
        save_ratchet(new_ratchet)
        print(f"\n  Ratchet tightened: {len(improvements)} path(s) improved.")
        return 0

    return 1 if regressions else 0


if __name__ == "__main__":
    sys.exit(main())
