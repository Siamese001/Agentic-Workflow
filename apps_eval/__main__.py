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


def _load_cert_route_entry() -> dict | None:
    """Return the first route entry from apps_eval's cert_route_registry.yaml.

    Fail-soft: any parse or IO error returns None, which makes
    ``maybe_invoke_exit_eval`` a no-op. Never raises.
    """
    try:
        import yaml  # noqa: PLC0415
        from pathlib import Path  # noqa: PLC0415

        registry_path = Path(__file__).resolve().parent / "config" / "cert_route_registry.yaml"
        doc = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 -- cert-path adoption must be fail-soft
        # guardian: allow-broad-except -- cert-path adoption must be fail-soft;
        # any registry-load failure leaves the hook as a no-op and the cert
        # bundle continues unaffected
        return None
    routes = doc.get("routes") if isinstance(doc, dict) else None
    if not routes or not isinstance(routes, list):
        return None
    return routes[0] if routes else None


def _run_eval(args: argparse.Namespace) -> int:
    """Delegate to L1→L0→L2→Exit pipeline."""
    from apps_eval.integrations.eval_ingress import run_eval_from_cli
    from apps_shared.cert import maybe_invoke_exit_eval
    from apps_eval.cert import produce_fec  # noqa: F401 -- side-effect: FEC available

    cert_route_entry = _load_cert_route_entry()
    exit_code = run_eval_from_cli(
        suites_str=args.suites,
        scenario_filter=args.filter,
        baseline_mode=args.baseline_mode,
        out_dir=args.out_dir,
        deterministic_only=args.deterministic_only,
        cache_strategy=args.cache_strategy,
    )
    _run_ctx: dict = {
        "route_id": "apps_eval.evaluation_v1",
        "route_contract": {"route_id": "apps_eval.evaluation_v1"},
    }
    _receipts: dict = {
        "output": {},
        "route_contract": _run_ctx["route_contract"],
        "evidence_bundle": {},
        "final_evidence_contract": produce_fec(_run_ctx),
        "state_diff": {},
        "compiled_prompt_artifact": {},
    }
    maybe_invoke_exit_eval(_receipts, cert_route_entry)
    return exit_code


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
