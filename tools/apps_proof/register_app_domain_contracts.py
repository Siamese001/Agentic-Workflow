"""CLI entry point: register app-domain contracts through UWG into L4.

Usage:
    python -m tools.apps_proof.register_app_domain_contracts --app all
    python -m tools.apps_proof.register_app_domain_contracts --app apps_rg
    python -m tools.apps_proof.register_app_domain_contracts --app apps_rg --dry-run

A dry-run validates schemas without submitting to UWG.

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-domain-contract-fortknox-c4d8e2.md`` §W3.3.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from agentic_core.L4_state.uwg import (
    discover_app_contract_dirs,
    load_bundle_from_dir,
    register_bundle,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="register_app_domain_contracts",
        description="Register apps_*/config/domain_contract/*.yaml bundles through UWG into L4.",
    )
    parser.add_argument(
        "--app",
        default="all",
        help="Which app to register (e.g. 'apps_rg') or 'all'. Default: all.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate bundles without submitting to UWG.",
    )
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="Repo root (default: inferred from this script's path).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-app output; show only the summary.",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    repo_root = Path(args.repo_root).resolve()
    all_dirs = discover_app_contract_dirs(repo_root)

    if args.app == "all":
        targets = sorted(all_dirs.items())
    else:
        if args.app not in all_dirs:
            print(f"ERROR: no domain_contract found for app {args.app!r}", file=sys.stderr)
            print(f"Available: {sorted(all_dirs.keys())}", file=sys.stderr)
            return 2
        targets = [(args.app, all_dirs[args.app])]

    if not args.quiet:
        mode = "dry-run (no UWG submission)" if args.dry_run else "UWG submission"
        print(f"Mode: {mode}. Targets: {len(targets)}")

    accepted = 0
    blocked = 0
    total_records = 0
    for app_id, dir_path in targets:
        try:
            bundle = load_bundle_from_dir(dir_path)
        except Exception as exc:
            print(f"  [LOAD-FAIL] {app_id}: {type(exc).__name__}: {exc}", file=sys.stderr)
            blocked += 1
            continue

        n_records = len(bundle.all_records())
        if args.dry_run:
            if not args.quiet:
                print(f"  [DRY-OK]  {app_id}: validated {n_records} records")
            accepted += 1
            total_records += n_records
            continue

        try:
            receipt = register_bundle(bundle)
        except Exception as exc:
            print(f"  [REG-FAIL] {app_id}: {type(exc).__name__}: {exc}", file=sys.stderr)
            blocked += 1
            continue

        if receipt.accepted:
            if not args.quiet:
                print(
                    f"  [OK]      {app_id}: records={receipt.state_diff_count} "
                    f"digest={receipt.bundle_digest[:16]}",
                )
            accepted += 1
            total_records += receipt.state_diff_count
        else:
            blocked += 1
            reasons = ()
            if receipt.blocked_receipt is not None:
                reasons = receipt.blocked_receipt.blocked_reason_codes
            print(
                f"  [BLOCKED] {app_id}: reasons={list(reasons)}",
                file=sys.stderr,
            )

    print(
        f"Summary: accepted={accepted} blocked={blocked} total_state_diffs={total_records}",
    )
    return 0 if blocked == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
