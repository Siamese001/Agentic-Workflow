"""
run_eval.py — CLI entrypoint for apps_eval Evaluation Lab.

Usage:
    python -m apps_eval --suites routing_enforcement,determinism_contracts
    python -m apps_eval.scripts.run_eval --all --out eval/ --json-output
"""

from __future__ import annotations

import argparse
import json
import logging
import sys

_log = logging.getLogger("apps_eval.run_eval")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="apps_eval", description="Evaluation Lab — agentic_core platform")
    parser.add_argument(
        "--suites",
        default="",
        help="Comma-separated suite IDs to run. Leave empty to run all.",
    )
    parser.add_argument("--all", action="store_true", help="Run all configured suites")
    parser.add_argument("--out", default="eval", help="Output directory for artifacts")
    parser.add_argument("--baseline-dir", default="eval_baselines", help="Baseline directory")
    parser.add_argument("--no-regression", action="store_true", help="Skip regression detection")
    parser.add_argument("--update-baseline", action="store_true", help="Update baseline after run")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--trace-id", default="")
    parser.add_argument("--json-output", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    from apps_eval.reasoning.EvalOrchestrator import EvalOrchestrator
    from apps_eval.types.eval_types import EvalRequest

    suite_ids: list[str] = []
    if args.suites:
        suite_ids = [s.strip() for s in args.suites.split(",") if s.strip()]

    request = EvalRequest(
        suite_ids=suite_ids,
        dry_run=args.dry_run,
        trace_id=args.trace_id,
        compare_baseline=not args.no_regression,
        emit_scorecard_csv=True,
    )

    orchestrator = EvalOrchestrator(
        dry_run=args.dry_run,
        output_dir=args.out,
        baseline_dir=args.baseline_dir,
    )
    result = orchestrator.run(request)

    if args.json_output:
        print(
            json.dumps(
                {
                    "trace_id": result.trace_id,
                    "status": str(result.status),
                    "overall_score": result.overall_score,
                    "suites_run": len(result.suite_results),
                    "gate_violations": result.gate_violations,
                    "regressions": sum(
                        1 for r in result.regression_records if str(r.verdict) == "REGRESSION"
                    ),
                    "artifacts": result.artifact_paths,
                },
                indent=2,
            ),
        )

    status_val = result.status.value if hasattr(result.status, "value") else str(result.status)
    if status_val in ("complete", "dry_run"):
        _log.info("[apps_eval] SUCCESS trace=%s score=%.1f%%", result.trace_id, result.overall_score * 100)
        return 0
    elif status_val == "regression":
        _log.error("[apps_eval] REGRESSION DETECTED trace=%s", result.trace_id)
        return 2
    else:
        _log.error("[apps_eval] FAILED trace=%s violations=%s", result.trace_id, result.gate_violations)
        return 1


if __name__ == "__main__":
    sys.exit(main())
