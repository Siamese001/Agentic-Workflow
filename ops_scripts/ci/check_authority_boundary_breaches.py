#!/usr/bin/env python3
"""
check_authority_boundary_breaches.py — CI gate enforcing ADR-071 disposition.

Reads `mv_authority_boundary_breaches` from the latest ADG snapshot and asserts:

  1. Total breach count is bounded (default ≤18, the 2026-05-15 ADR-071 ratchet).
  2. ALL breaches are attributed to guardian-exempt source files (proof harness
     plus sanctioned U0/L2/profile adapter surfaces inventoried in ADR-071).

Failure modes:

  - Total exceeds ratchet ceiling: a new authority boundary breach was
    introduced. Fix at source or expand the exempt-source list in this gate
    after Author-Gate review.
  - A breach exists in a NON-exempt source: a new file is outside the
    ratcheted exempt inventory. Hard fail.

Exit codes:
  0 = pass (count ≤ ceiling, all in exempt sources)
  1 = fail (regression detected)
  2 = error (no ADG snapshot, schema mismatch)

Usage:
  python ops_scripts/ci/check_authority_boundary_breaches.py
  python ops_scripts/ci/check_authority_boundary_breaches.py --max 18
  python ops_scripts/ci/check_authority_boundary_breaches.py --json
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import argparse
import collections
import json
import sqlite3
import sys
from collections.abc import Sequence
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
# Ratchet: proof harness (scenario_base) + sanctioned app U0/profile seams that
# intentionally reach documented thin adapters or shared ingress contracts.
DEFAULT_MAX = 18
DEFAULT_EXEMPT = (
    "apps_shared/proof/scenario_base.py",
    "apps_rfp/integrations/u0_intake_adapter.py",
    "apps_lic/runtime/profile_builder_adapter.py",
    "apps_research/runtime/profile_builder_adapter.py",
    "apps_research/integrations/qwen_strict_probe.py",
    "apps_rg/runtime/bindings/u0_binding.py",
    "apps_rg/runtime/bindings/l2_binding_adapter.py",
    "apps_rg/enforcement/cli_prerequisite_gate.py",
)


def find_latest_snapshot() -> Path | None:
    """Return the latest ADG SQLite snapshot via canonical resolver."""
    from tools.adg.shared_modules.path_resolver import latest_sqlite  # noqa: PLC0415

    return latest_sqlite()


def query_authority_breach_per_src(con: sqlite3.Connection) -> dict[str, int]:
    """Return breach counts keyed by ``src_file`` from ``mv_authority_boundary_breaches``."""
    cur = con.execute(
        "SELECT src_file, COUNT(*) FROM mv_authority_boundary_breaches GROUP BY src_file"
    )
    return dict(cur.fetchall())


def authority_breaches_fail_adr071(
    con: sqlite3.Connection,
    max_allowed: int = DEFAULT_MAX,
    exempt_sources: Sequence[str] | None = None,
) -> tuple[bool, dict[str, int], list[str]]:
    """Evaluate ADR-071 disposition against an open ADG connection.

    Returns:
        (failed, per_src_counts, reasons)
    """
    if exempt_sources is None:
        exempt = frozenset(DEFAULT_EXEMPT)
    else:
        exempt = frozenset(exempt_sources)
    try:
        per_src = query_authority_breach_per_src(con)
    except sqlite3.OperationalError as exc:
        raise RuntimeError(f"mv_authority_boundary_breaches unavailable: {exc}") from exc

    total = sum(per_src.values())
    non_exempt = {src: n for src, n in per_src.items() if src not in exempt}
    reasons: list[str] = []
    failed = False
    if total > max_allowed:
        failed = True
        reasons.append(f"total_breaches={total} exceeds ceiling={max_allowed}")
    if non_exempt:
        failed = True
        for src, n in sorted(non_exempt.items()):
            reasons.append(f"non-exempt source has {n} breach(es): {src}")
    return failed, per_src, reasons


def main() -> int:
    parser = argparse.ArgumentParser(description="Enforce ADR-071 authority boundary disposition")
    parser.add_argument("--max", type=int, default=DEFAULT_MAX, help="Max allowed breach count (default: 18)")
    parser.add_argument("--exempt", action="append", default=list(DEFAULT_EXEMPT), help="Exempt source file (repeatable)")
    parser.add_argument("--json", action="store_true", help="Emit JSON status")
    args = parser.parse_args()

    snap = find_latest_snapshot()
    if snap is None:
        print("ERROR: no ADG snapshot at artifacts/adg/adg_indexed_*.sqlite", file=sys.stderr)
        return 2

    con = sqlite3.connect(snap)
    try:
        failed, per_src, reasons = authority_breaches_fail_adr071(
            con, max_allowed=args.max, exempt_sources=args.exempt
        )
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        con.close()
        return 2

    total = sum(per_src.values())
    exempt_sources = sorted(s for s in per_src if s in args.exempt)
    non_exempt = {src: n for src, n in per_src.items() if src not in args.exempt}

    status: collections.OrderedDict[str, object] = collections.OrderedDict()
    status["snapshot"] = snap.name
    status["total_breaches"] = total
    status["max_allowed"] = args.max
    status["per_source"] = per_src
    status["exempt_sources_present"] = exempt_sources
    status["non_exempt_sources"] = non_exempt
    status["adr"] = "ADR-071"

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
