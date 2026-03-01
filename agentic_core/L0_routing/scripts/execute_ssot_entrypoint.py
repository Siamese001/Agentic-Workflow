#!/usr/bin/env python3
"""
V15-Native Entrypoint for execute_ssot.

Single canonical entrypoint — all flags defined here, no second parse in _legacy_main.

This file exists to make the runtime boundary unambiguous:
  - execute_ssot_entrypoint.py = the ONLY invocation path.
  - execute_ssot.py = active module for agent-based healing pipeline.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def _resolve_repo_root() -> Path:
    """Walk upward from this file until repo markers are found."""
    cur = Path(__file__).resolve()
    for p in (cur, *cur.parents):
        if (p / "agentic_core").is_dir() and (p / "ops_scripts").is_dir():
            return p
    raise RuntimeError(f"Unable to resolve repo root from: {cur}")


def main() -> int:
    """V15-native entrypoint — single parser, deterministic, fail-closed."""
    parser = argparse.ArgumentParser(
        description="Sovereign Healing Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  # Active healing (mutations applied)
  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --heal

  # Scan/report only — safe default (no --heal)
  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint

  # Single territory with healing
  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --heal --territory L5_safety

  # Dry-run validation (explicit alias for scan-only)
  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --validate

  # Human-in-the-loop mode
  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --heal --interactive
""",
    )
    # --- Mode flags ---
    parser.add_argument("--territory", type=str, help="Specific territory to scan")
    parser.add_argument(
        "--domains", action="store_true", help="Scan all major domains (explicit; now also the default)"
    )
    parser.add_argument("--agent", type=str, help="Run specific agent directly")
    parser.add_argument("--list-agents", action="store_true", help="List discoverable agents")
    parser.add_argument("--agents", type=str, default=None, help="Comma-separated agent keys to run")
    parser.add_argument("--capture-baseline", action="store_true", help="Capture new Golden Baseline")
    # --- Behaviour flags ---
    parser.add_argument(
        "--heal",
        action="store_true",
        default=False,
        help="Enable active healing (mutations applied). Absence = scan/report only.",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Scan/report only — no mutations (alias for omitting --heal)"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validation-only mode (implies scan-only, no mutations)"
    )
    parser.add_argument("--interactive", action="store_true", help="Enable human-in-the-loop prompts")
    parser.add_argument("--manual", action="store_true", help="Disable autonomous mode")
    parser.add_argument(
        "--no-cda", action="store_true", help="Disable CognitiveDispositionAgent (on by default)"
    )
    parser.add_argument(
        "--allow-protected-root-mutation",
        action="store_true",
        default=True,
        help="Allow writes to protected root directories (default: True).",
    )
    # --- Introspection flags ---
    parser.add_argument("--plan", action="store_true", help="Print execution plan and exit")
    parser.add_argument(
        "--arbitrate-plan", action="store_true", help="Multi-agent arbitration on plan (plan mode only)"
    )
    parser.add_argument("--ptc-plan", action="store_true", help="PTC plan context (plan mode only)")
    parser.add_argument("--fence-self-check", action="store_true", help="Run fence self-check (no mutations)")
    # --- Infra flags ---
    parser.add_argument(
        "--v15-enforcement", type=int, choices=(0, 1), default=None, help="Override V15_ENFORCEMENT"
    )
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase log verbosity")
    # Keep --legacy for backward compat (silently accepted, no longer required)
    parser.add_argument("--legacy", action="store_true", help=argparse.SUPPRESS)

    args = parser.parse_args()

    # [FENCE SELF-CHECK MODE]
    if args.fence_self_check:
        from agentic_core.L0_routing.scripts.execute_ssot import run_fence_self_check

        run_fence_self_check()
        return 0

    # [PLAN MODE]
    if args.plan:
        from agentic_core.L0_routing.scripts.execute_ssot import print_execution_plan

        print_execution_plan(arbitrate_plan=args.arbitrate_plan, ptc_plan=args.ptc_plan)
        return 0

    from agentic_core.L0_routing.scripts.execute_ssot import (
        REPO_ROOT,
        _apply_v15_enforcement_flag,
        _configure_logging,
        _legacy_main,
        _maybe_force_utf8_console,
    )

    _configure_logging(int(args.verbose))
    _apply_v15_enforcement_flag(args)
    _maybe_force_utf8_console()

    # Build argv list for _legacy_main's internal parser (still needed for territory/agents/etc.)
    # Only pass flags that _legacy_main's parser understands
    inner_argv = []
    if args.territory:
        inner_argv += ["--territory", args.territory]
    if args.domains:
        inner_argv += ["--domains"]
    if args.agent:
        inner_argv += ["--agent", args.agent]
    if args.list_agents:
        inner_argv += ["--list-agents"]
    if args.agents:
        inner_argv += ["--agents", args.agents]
    if args.capture_baseline:
        inner_argv += ["--capture-baseline"]
    if args.heal:
        inner_argv += ["--heal"]
    if args.dry_run:
        inner_argv += ["--dry-run"]
    if args.validate:
        inner_argv += ["--validate"]
    if args.interactive:
        inner_argv += ["--interactive"]
    if args.manual:
        inner_argv += ["--manual"]
    if args.no_cda:
        inner_argv += ["--no-cda"]
    if args.verbose:
        inner_argv += ["-v"] * args.verbose

    try:
        _legacy_main(
            inner_argv,
            repo_root=REPO_ROOT,
            allow_protected_root_mutation=args.allow_protected_root_mutation,
        )
    except SystemExit as exc:
        return int(exc.code) if exc.code is not None else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
