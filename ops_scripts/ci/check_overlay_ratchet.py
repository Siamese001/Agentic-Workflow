#!/usr/bin/env python3
"""Parametric overlay ratchet — implements C1-C5 from RCA-2026-04-24.

A single gate that produces one logical ratchet per overlay violation
category. Reads the latest `artifacts/adg/adg_debt_overlay_*.sqlite` and
counts violations of a given category, comparing against a baseline.

Usage:
    python ops_scripts/ci/check_overlay_ratchet.py --category dead_import
    python ops_scripts/ci/check_overlay_ratchet.py --category dead_import --seed
    python ops_scripts/ci/check_overlay_ratchet.py --all

Categories (from the overlay): dead_import, namespace_pkg_import,
import_error_fallback_stub, module_duplicate, stale_all_export,
module_load_action_call, rename_shim_module.

Baseline files live in `ops_scripts/ci/baselines/overlay_<category>.json`.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BASELINE_DIR = REPO / "ops_scripts" / "ci" / "baselines"
BASELINE_DIR.mkdir(parents=True, exist_ok=True)

CATEGORY_SEVERITY: dict[str, str] = {
    # debt_overlay_enricher categories
    "dead_import_resolved": "HIGH",
    "namespace_pkg_import": "ADVISORY",
    "import_error_fallback_stub": "MEDIUM",
    "module_duplicate": "HIGH",
    "stale_all_export": "MEDIUM",
    "module_load_action_call": "ADVISORY",
    "rename_shim_module": "LOW",
    # truth_expansion_enricher categories (R5 wave)
    "hidden_write_outside_uwg": "HIGH",
    "config_target_missing": "HIGH",
    "false_success_stub": "MEDIUM",
    "gate_self_inconsistent": "HIGH",
    "governance_assertion_at_module_load": "ADVISORY",
    "cli_only_module": "ADVISORY",
    # r6_backlog_enricher categories (R6 wave)
    "async_fire_and_forget": "MEDIUM",
    "external_call_no_timeout": "MEDIUM",
    "boundary_string_unresolved": "LOW",
    "mcp_contract_drift": "MEDIUM",
    "rename_shim_consumer_risk": "MEDIUM",
    "snapshot_dirty": "ADVISORY",
}


def latest_canonical_snapshot() -> Path:
    """Return the canonical ADG snapshot to query overlay_violations from.

    Tries the freshest `adg_indexed_*.sqlite` first; falls back to a `.tmp`
    snapshot if no atomic-rename completion exists yet (Windows quirk).
    """
    candidates = sorted(
        glob.glob(str(REPO / "artifacts/adg/adg_indexed_*.sqlite")),
        key=os.path.getmtime,
    )
    if candidates:
        return Path(candidates[-1])
    tmps = sorted(
        glob.glob(str(REPO / "artifacts/adg/adg_indexed_*.sqlite.tmp")),
        key=os.path.getmtime,
    )
    if tmps:
        return Path(tmps[-1])
    raise FileNotFoundError("No canonical ADG snapshot found. Run `python tools/generate_full_adg.py` first.")


def count_category(con: sqlite3.Connection, category: str) -> int:
    if category == "module_duplicate":
        # Derived from body_hash via the materialized view.
        return con.execute(
            "SELECT COALESCE(SUM(cluster_size), 0) FROM mv_module_duplicate_clusters_overlay"
        ).fetchone()[0]
    return con.execute(
        "SELECT COUNT(*) FROM overlay_violations WHERE category = ?",
        (category,),
    ).fetchone()[0]


def baseline_path(category: str) -> Path:
    return BASELINE_DIR / f"overlay_{category}.json"


def load_baseline(category: str) -> int | None:
    p = baseline_path(category)
    if not p.exists():
        return None
    try:
        return int(json.loads(p.read_text(encoding="utf-8"))["count"])
    except (KeyError, ValueError, json.JSONDecodeError):
        return None


def write_baseline(category: str, count: int) -> None:
    baseline_path(category).write_text(
        json.dumps({"category": category, "count": count}, indent=2),
        encoding="utf-8",
    )


def run_one(category: str, *, seed: bool = False) -> int:
    con = sqlite3.connect(latest_canonical_snapshot())
    try:
        current = count_category(con, category)
    finally:
        con.close()

    severity = CATEGORY_SEVERITY.get(category, "LOW")

    if seed:
        write_baseline(category, current)
        print(f"[overlay:{category}] baseline seeded count={current}")
        return 0

    baseline = load_baseline(category)
    if baseline is None:
        print(f"[overlay:{category}] NO BASELINE — current={current} (seed with --seed to lock in)")
        return 0  # not failing — first time

    delta = current - baseline
    status_emoji = "✓" if delta <= 0 else "✗"
    print(
        f"[overlay:{category}] {status_emoji} severity={severity} "
        f"current={current} baseline={baseline} delta={delta:+d}"
    )

    if severity == "ADVISORY":
        return 0  # advisory — log only

    if delta > 0:
        return 1  # ratchet violation — count went up
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", help="Single category to check")
    parser.add_argument("--all", action="store_true", help="Run all categories")
    parser.add_argument("--seed", action="store_true", help="Seed/refresh baseline")
    args = parser.parse_args()

    if not args.all and not args.category:
        parser.error("specify --category <name> or --all")

    cats = list(CATEGORY_SEVERITY.keys()) if args.all else [args.category]
    rcs = [run_one(c, seed=args.seed) for c in cats]
    return max(rcs) if rcs else 0


if __name__ == "__main__":
    sys.exit(main())
