#!/usr/bin/env python3
"""
check_authority_boundary_breaches.py — CI gate enforcing ADR-071 disposition.

Reads `mv_authority_boundary_breaches` from the latest ADG snapshot and asserts:

  1. Total breach count is bounded (default ≤17, the post-ADR-071 baseline).
  2. ALL breaches are attributed to the guardian-exempt source files
     (default: apps_shared/proof/scenario_base.py).

Failure modes:

  - Total exceeds ratchet ceiling: a new authority boundary breach was
    introduced. Fix at source or expand the exempt-source list in this gate
    after Author-Gate review.
  - A breach exists in a NON-exempt source: a new file is doing what only
    proof harnesses are allowed to do. Hard fail.

Exit codes:
  0 = pass (count ≤ ceiling, all in exempt sources)
  1 = fail (regression detected)
  2 = error (no ADG snapshot, schema mismatch)

Usage:
  python ops_scripts/ci/check_authority_boundary_breaches.py
  python ops_scripts/ci/check_authority_boundary_breaches.py --max 17
  python ops_scripts/ci/check_authority_boundary_breaches.py --json
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .windsurf/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import argparse
import collections
import json
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MAX = 17
DEFAULT_EXEMPT = (
    "apps_shared/proof/scenario_base.py",
)


def find_latest_snapshot() -> Path | None:
    """Return the latest ADG SQLite snapshot via canonical resolver."""
    from tools.adg.shared_modules.path_resolver import latest_sqlite  # noqa: PLC0415

    return latest_sqlite()


def main() -> int:
    parser = argparse.ArgumentParser(description="Enforce ADR-071 authority boundary disposition")
    parser.add_argument("--max", type=int, default=DEFAULT_MAX, help="Max allowed breach count (default: 17)")
    parser.add_argument("--exempt", action="append", default=list(DEFAULT_EXEMPT), help="Exempt source file (repeatable)")
    parser.add_argument("--json", action="store_true", help="Emit JSON status")
    args = parser.parse_args()

    snap = find_latest_snapshot()
    if snap is None:
        print("ERROR: no ADG snapshot at artifacts/adg/adg_indexed_*.sqlite", file=sys.stderr)
        return 2

    con = sqlite3.connect(snap)
    cur = con.cursor()

    try:
        cur.execute("SELECT src_file, COUNT(*) FROM mv_authority_boundary_breaches GROUP BY src_file")
        per_src = dict(cur.fetchall())
    except sqlite3.OperationalError as exc:
        print(f"ERROR: mv_authority_boundary_breaches not found in snapshot — {exc}", file=sys.stderr)
        con.close()
        return 2

    total = sum(per_src.values())
    non_exempt = {src: n for src, n in per_src.items() if src not in args.exempt}
    exempt_sources = sorted(s for s in per_src if s in args.exempt)

    status: collections.OrderedDict[str, object] = collections.OrderedDict()
    status["snapshot"] = snap.name
    status["total_breaches"] = total
    status["max_allowed"] = args.max
    status["per_source"] = per_src
    status["exempt_sources_present"] = exempt_sources
    status["non_exempt_sources"] = non_exempt
    status["adr"] = "ADR-071"

    failed = False
    reasons: list[str] = []

    if total > args.max:
        failed = True
        reasons.append(f"total_breaches={total} exceeds ceiling={args.max}")

    if non_exempt:
        failed = True
        for src, n in non_exempt.items():
            reasons.append(f"non-exempt source has {n} breach(es): {src}")

    status["pass"] = not failed
    status["reasons"] = reasons

    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print(f"  Snapshot:        {snap.name}")
        print(f"  Total breaches:  {total} (ceiling: {args.max})")
        print(f"  Exempt sources:  {len(exempt_sources)}")
        for src in exempt_sources:
            print(f"     ✔ {src}: {per_src[src]} breach(es) — exempt")
        if non_exempt:
            print(f"  Non-exempt sources: {len(non_exempt)}")
            for src, n in non_exempt.items():
                print(f"     ✗ {src}: {n} breach(es) — NOT EXEMPT")
        print(f"  Result:          {'PASS' if not failed else 'FAIL'}")
        for r in reasons:
            print(f"     - {r}")

    con.close()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
