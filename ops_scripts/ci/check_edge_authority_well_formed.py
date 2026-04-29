#!/usr/bin/env python3
"""Gate G-EDGE-AUTHORITY — every edge must have a well-formed authority value.

Per the 2026-04-28 graph-authority directive ("The ADG generator must stop
emitting unqualified edges. Every edge must be typed as verified, unresolved,
dynamic, external, test-only, or runtime-observed"), every row in the canonical
``edges`` table of every shipped ADG snapshot MUST have a non-NULL ``authority``
value drawn from the closed enum.

Tier: B (blocking). Any NULL or out-of-enum value is a hard failure — it means
the writer skipped backfill or someone introduced a new authority class
without updating the SSOT.

Reads the latest snapshot at ``artifacts/adg/adg_indexed_*.sqlite``. To pin a
specific snapshot, set ``ADG_SNAPSHOT=<path>`` in the environment. Bypass:
``EDGE_AUTHORITY_BYPASS=1``.

The gate also prints the authority distribution histogram so the operator can
spot trends (e.g. growing ``unresolved`` count). For a hard ratchet on
unresolved edges specifically, see ``check_unresolved_edges_ratchet.py``.
"""

from __future__ import annotations

import glob
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.adg.artifact.edge_authority import ALL_AUTHORITIES  # noqa: E402

ADG_DIR = REPO_ROOT / "artifacts" / "adg"
LOG_DIR = REPO_ROOT / "artifacts" / "windsurf"
LOG_FILE = LOG_DIR / "edge_authority_violations.jsonl"


def latest_snapshot() -> Path:
    override = os.environ.get("ADG_SNAPSHOT", "").strip()
    if override:
        p = Path(override).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"ADG_SNAPSHOT not found: {p}")
        return p
    matches = sorted(glob.glob(str(ADG_DIR / "adg_indexed_*.sqlite")), key=os.path.getmtime)
    if not matches:
        raise FileNotFoundError(
            f"no adg_indexed_*.sqlite under {ADG_DIR}; regenerate via `python tools/generate_full_adg.py`"
        )
    return Path(matches[-1])


def main() -> int:
    if os.environ.get("EDGE_AUTHORITY_BYPASS", "").strip() == "1":
        print("[G-EDGE-AUTHORITY] BYPASSED via EDGE_AUTHORITY_BYPASS=1")
        return 0

    snap = latest_snapshot()
    print(f"[G-EDGE-AUTHORITY] snapshot: {snap}")
    con = sqlite3.connect(snap)
    cur = con.cursor()

    # Schema check: column must exist.
    cur.execute("PRAGMA table_info(edges)")
    cols = {row[1] for row in cur.fetchall()}
    if "authority" not in cols:
        print("[G-EDGE-AUTHORITY] FAIL: edges.authority column missing — regenerate ADG snapshot")
        return 1

    # Distribution histogram (always print for visibility).
    cur.execute("SELECT COALESCE(authority,'<NULL>'), COUNT(*) FROM edges GROUP BY authority ORDER BY 2 DESC")
    hist = cur.fetchall()
    print("[G-EDGE-AUTHORITY] authority distribution:")
    total = 0
    for label, count in hist:
        print(f"    {label:>20}  {count}")
        total += count
    print(f"    {'TOTAL':>20}  {total}")

    # Failure conditions:
    # 1. Any NULL authority is a fail.
    # 2. Any value outside the closed enum is a fail.
    null_count = next((c for label, c in hist if label == "<NULL>"), 0)
    bad_values = [(label, c) for label, c in hist if label != "<NULL>" and label not in ALL_AUTHORITIES]

    record = {
        "gate": "G-EDGE-AUTHORITY",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "snapshot": str(snap),
        "distribution": {label: c for label, c in hist},
        "null_count": null_count,
        "out_of_enum": bad_values,
    }
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    if null_count > 0:
        print(
            f"[G-EDGE-AUTHORITY] FAIL: {null_count} edges have NULL authority. "
            f"Backfill UPDATE was not run, or new edges were inserted after backfill."
        )
        return 1
    if bad_values:
        print(f"[G-EDGE-AUTHORITY] FAIL: out-of-enum authority values present: {bad_values}")
        print(f"  Allowed enum: {sorted(ALL_AUTHORITIES)}")
        return 1

    print("[G-EDGE-AUTHORITY] PASS: every edge has a well-formed authority value")
    return 0


if __name__ == "__main__":
    sys.exit(main())
