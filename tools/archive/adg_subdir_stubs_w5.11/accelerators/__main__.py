"""Unified ADG Accelerators Entry Point

Orchestrates all ADG accelerator tools for testing, hardening, and incremental updates.

Usage:
    # Testing accelerators
    python -m tools.adg.accelerators testing gap [--top 20] [--layer L5]
    python -m tools.adg.accelerators testing scope --changed file.py
    python -m tools.adg.accelerators testing groups --workers 4
    python -m tools.adg.accelerators testing collection-safety [--json out.json]

    # Hardening accelerators
    python -m tools.adg.accelerators hardening p0 --layer L3 --dim evidence --apply
    python -m tools.adg.accelerators hardening p1 --apply
    python -m tools.adg.accelerators hardening p2 --apply

    # Incremental accelerators
    python -m tools.adg.accelerators incremental update --changed file1.py file2.py
    python -m tools.adg.accelerators incremental scan --cache

    # Fast test runner
    python -m tools.adg.accelerators fast [--adg] [--dry-run]

Each subcommand delegates to the appropriate accelerator module.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from tools.adg.accelerators.orchestrator import (
    run_fast_test,
    run_hardening_p0,
    run_hardening_p1,
    run_hardening_p2,
    run_incremental_update,
    run_testing,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
_logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent.parent.parent


def _build_parser() -> argparse.ArgumentParser:
    """Build the unified CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="python -m tools.adg.accelerators",
        description="Unified ADG Accelerators CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- testing ---
    testing_parser = sub.add_parser("testing", help="Run testing accelerators")
    testing_sub = testing_parser.add_subparsers(dest="testing_command", required=True)

    gap_parser = testing_sub.add_parser("gap", help="Show coverage gaps")
    gap_parser.add_argument("--top", type=int, default=20)
    gap_parser.add_argument("--layer", type=str, default=None)

    scope_parser = testing_sub.add_parser("scope", help="Scope analysis")
    scope_parser.add_argument("--changed", nargs="+", required=True)

    groups_parser = testing_sub.add_parser("groups", help="Parallel test groups")
    groups_parser.add_argument("--workers", type=int, default=4)

    cs_parser = testing_sub.add_parser("collection-safety", help="Collection safety check")
    cs_parser.add_argument("--json", type=str, default=None)

    # --- hardening ---
    hardening_parser = sub.add_parser("hardening", help="Run hardening accelerators")
    hardening_sub = hardening_parser.add_subparsers(dest="hardening_command", required=True)

    p0_parser = hardening_sub.add_parser("p0", help="P0 hardening")
    p0_parser.add_argument("--layer", type=str, default=None)
    p0_parser.add_argument("--dim", type=str, default=None)
    p0_parser.add_argument("--apply", action="store_true")

    p1_parser = hardening_sub.add_parser("p1", help="P1 hardening")
    p1_parser.add_argument("--apply", action="store_true")

    p2_parser = hardening_sub.add_parser("p2", help="P2 hardening")
    p2_parser.add_argument("--apply", action="store_true")

    # --- incremental ---
    incr_parser = sub.add_parser("incremental", help="Run incremental accelerators")
    incr_sub = incr_parser.add_subparsers(dest="incremental_command", required=True)

    update_parser = incr_sub.add_parser("update", help="Incremental update")
    update_parser.add_argument("--changed", nargs="+", required=True)

    incr_sub.add_parser("scan", help="Incremental scan").add_argument("--cache", action="store_true")

    # --- fast ---
    fast_parser = sub.add_parser("fast", help="Fast test runner")
    fast_parser.add_argument("--adg", action="store_true")
    fast_parser.add_argument("--dry-run", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "testing":
        cmd_args = []
        if args.testing_command == "gap":
            cmd_args = ["gap", "--top", str(args.top)]
            if args.layer:
                cmd_args.extend(["--layer", args.layer])
        elif args.testing_command == "scope":
            cmd_args = ["scope"] + args.changed
        elif args.testing_command == "groups":
            cmd_args = ["groups", "--workers", str(args.workers)]
        elif args.testing_command == "collection-safety":
            cmd_args = ["collection-safety"]
            if args.json:
                cmd_args.extend(["--json", args.json])
        return run_testing(cmd_args)

    elif args.command == "hardening":
        if args.hardening_command == "p0":
            return run_hardening_p0(args.layer, args.dim, args.apply)
        elif args.hardening_command == "p1":
            return run_hardening_p1(args.apply)
        elif args.hardening_command == "p2":
            return run_hardening_p2(args.apply)
        return 1

    elif args.command == "incremental":
        if args.incremental_command == "update":
            return run_incremental_update(args.changed)
        elif args.incremental_command == "scan":
            return run_incremental_update(["--scan"] + (["--cache"] if args.cache else []))
        return 1

    elif args.command == "fast":
        return run_fast_test(args.adg, args.dry_run)

    return 1


if __name__ == "__main__":
    sys.exit(main())
