#!/usr/bin/env python3
"""
V15-Native Entrypoint for execute_ssot.

Minimal, modern entrypoint that:
  1. Configures logging and V15 enforcement deterministically.
  2. Delegates to the legacy body in execute_ssot.py.
  3. Requires --legacy flag to invoke the legacy healing pipeline.
  4. Without --legacy, prints usage and exits cleanly.

This file exists to make the runtime boundary unambiguous:
  - execute_ssot_entrypoint.py = the ONLY invocation path.
  - execute_ssot.py = frozen legacy module (never invoked directly in CI).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _resolve_repo_root() -> Path:
    """Walk upward from this file until repo markers are found."""
    cur = Path(__file__).resolve()
    for p in (cur, *cur.parents):
        if (p / "agentic_core").is_dir() and (p / "ops_scripts").is_dir():
            return p
    raise RuntimeError(f"Unable to resolve repo root from: {cur}")


def main() -> int:
    """V15-native entrypoint — deterministic, fail-closed."""
    parser = argparse.ArgumentParser(
        description="V15 Sovereign Compliance Entrypoint",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  # Run legacy healing pipeline (explicit opt-in)
  python -m agentic_core.L0_maintenance.scripts.execute_ssot_entrypoint --legacy --territory L5_safety

  # Dry-run validation
  python -m agentic_core.L0_maintenance.scripts.execute_ssot_entrypoint --legacy --validate

  # List agents (no --legacy required)
  python -m agentic_core.L0_maintenance.scripts.execute_ssot_entrypoint --legacy --list-agents
""",
    )
    parser.add_argument(
        "--legacy",
        action="store_true",
        help="Invoke the legacy healing pipeline (execute_ssot._legacy_main).",
    )
    parser.add_argument(
        "--plan",
        action="store_true",
        help="Print the deterministic execution plan and exit. Requires --legacy.",
    )
    parser.add_argument(
        "--v15-enforcement",
        type=int,
        choices=(0, 1),
        default=None,
        help="Override V15_ENFORCEMENT for this run (0=off, 1=on).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase log verbosity (repeatable).",
    )

    pre_args, remaining = parser.parse_known_args()

    if not pre_args.legacy:
        parser.print_help()
        print(
            "\nError: --legacy flag required to invoke the healing pipeline.",
            file=sys.stderr,
        )
        return 1

    # [PLAN MODE] Pure introspection shortcut — no imports beyond plan data.
    if pre_args.plan:
        from agentic_core.L0_maintenance.scripts.execute_ssot import (
            print_execution_plan,
        )

        print_execution_plan()
        return 0

    # Delegate to the legacy module
    from agentic_core.L0_maintenance.scripts.execute_ssot import (
        REPO_ROOT,
        _apply_v15_enforcement_flag,
        _configure_logging,
        _legacy_main,
        _maybe_force_utf8_console,
    )

    _configure_logging(int(pre_args.verbose))
    _apply_v15_enforcement_flag(pre_args)
    _maybe_force_utf8_console()

    try:
        _legacy_main(remaining, repo_root=REPO_ROOT)
    except SystemExit as exc:
        return int(exc.code) if exc.code is not None else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
