"""Pure shim entrypoint for apps_eval.

Usage:
    python -m apps_eval --suites routing_enforcement,determinism_contracts

100% delegation to L1/L2/L0 — no business logic in __main__.
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Sequence

logger = logging.getLogger(__name__)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="apps_eval",
        description="Evaluation Lab — benchmarks agentic_core against deterministic scenarios",
    )
    parser.add_argument(
        "--suites",
        required=True,
        help="Comma-separated suite IDs (e.g., routing_enforcement,determinism_contracts)",
    )
    parser.add_argument(
        "--filter",
        default="",
        help="Scenario filter (optional substring match)",
    )
    parser.add_argument(
        "--baseline-mode",
        action="store_true",
        help="Enable regression detection vs stored baseline",
    )
    parser.add_argument(
        "--out-dir",
        default="artifacts/apps_eval/runs",
        help="Run artifact output directory",
    )
    parser.add_argument(
        "--deterministic-only",
        action="store_true",
        help="Skip LLM-judge dimensions (degraded mode)",
    )
    parser.add_argument(
        "--cache-strategy",
        choices=["exact", "semantic", "none"],
        default="exact",
        help="R1A exact / R1B semantic / disabled",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser


def _run_eval(args: argparse.Namespace) -> int:
    """Delegate to L1→L0→L2→Exit pipeline."""
    from apps_eval.integrations.eval_ingress import run_eval_from_cli
    return run_eval_from_cli(
        suites_str=args.suites,
        scenario_filter=args.filter,
        baseline_mode=args.baseline_mode,
        out_dir=args.out_dir,
        deterministic_only=args.deterministic_only,
        cache_strategy=args.cache_strategy,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    return _run_eval(args)


if __name__ == "__main__":
    main()
