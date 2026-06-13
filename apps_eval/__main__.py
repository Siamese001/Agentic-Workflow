"""CLI for the deterministic apps_eval harness."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from apps_eval.contracts import EvalRequest
from apps_eval.registry import OLD_SUITE_NAMES, load_apps_registry, load_suite, load_suites_registry
from apps_eval.runner.core import compare_record_to_baseline, render_record, run_eval


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="apps_eval", description="Deterministic grader harness for apps_rg and apps_lic")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list-apps")
    sub.add_parser("list-suites")
    inspect = sub.add_parser("inspect-suite")
    inspect.add_argument("suite")
    run = sub.add_parser("run")
    run.add_argument("--suite", required=True)
    run.add_argument("--mode", choices=["snapshot", "live_adapter"], default="snapshot")
    run.add_argument("--deterministic-only", action=argparse.BooleanOptionalAction, default=True)
    run.add_argument("--with-judge", action="store_true")
    run.add_argument("--baseline", default="")
    run.add_argument("--out-dir", default="artifacts/apps_eval/runs")
    run.add_argument("--emit-l6-handoff", action="store_true")
    compare = sub.add_parser("compare")
    compare.add_argument("--record", required=True)
    compare.add_argument("--baseline", required=True)
    render = sub.add_parser("render")
    render.add_argument("--record", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if getattr(args, "suite", "") in OLD_SUITE_NAMES:
        print(f"old suite name is rejected: {args.suite}", file=sys.stderr)
        return 2
    if args.command == "list-apps":
        for app_id in sorted(load_apps_registry()):
            print(app_id)
        return 0
    if args.command == "list-suites":
        for suite_id in sorted(load_suites_registry()):
            print(suite_id)
        return 0
    if args.command == "inspect-suite":
        print(json.dumps(load_suite(args.suite), indent=2, sort_keys=True))
        return 0
    if args.command == "run":
        record = run_eval(
            EvalRequest(
                suite_id=args.suite,
                mode=args.mode,
                deterministic_only=bool(args.deterministic_only),
                with_judge=bool(args.with_judge),
                compare_baseline=bool(args.baseline),
                baseline_path=args.baseline,
                out_dir=args.out_dir,
                emit_l6_handoff=bool(args.emit_l6_handoff),
            )
        )
        print(record.artifact_paths["eval_record"])
        return 0 if record.scorecard.verdict == "pass" else 1
    if args.command == "compare":
        record = json.loads(Path(args.record).read_text(encoding="utf-8"))
        baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
        summary = compare_record_to_baseline(record, baseline)
        print(json.dumps(summary.to_dict(), indent=2, sort_keys=True))
        return 0 if summary.verdict != "regression" else 1
    if args.command == "render":
        print(render_record(args.record), end="")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
