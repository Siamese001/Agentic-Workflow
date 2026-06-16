"""CLI for the deterministic apps_eval harness."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from apps_eval.baselines import load_baseline, promote_baseline
from apps_eval.contracts import EvalRequest
from apps_eval.matrix import run_matrix
from apps_eval.registry import OLD_SUITE_NAMES, load_apps_registry, load_suite, load_suites_registry
from apps_eval.runner.core import compare_record_to_baseline, render_record, run_eval
from apps_eval.scenarios import scaffold_apps_rg_scenario, validate_suite_fixtures


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="apps_eval", description="Deterministic grader harness for apps_rg and apps_lic")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list-apps")
    sub.add_parser("list-suites")
    inspect = sub.add_parser("inspect-suite")
    inspect.add_argument("suite")
    validate = sub.add_parser("validate-suite")
    validate.add_argument("suite")
    scaffold = sub.add_parser("scaffold-apps-rg-scenario")
    scaffold.add_argument("scenario_id")
    scaffold.add_argument("--description", required=True)
    scaffold.add_argument("--fixture-root", default="apps_eval/fixtures/dev/apps_rg")
    scaffold.add_argument("--overwrite", action="store_true")
    run = sub.add_parser("run")
    run.add_argument("--suite", required=True)
    run.add_argument("--mode", choices=["snapshot", "live_adapter"], default="snapshot")
    run.add_argument("--deterministic-only", action=argparse.BooleanOptionalAction, default=True)
    run.add_argument("--with-judge", action="store_true")
    run.add_argument("--baseline", default="")
    run.add_argument("--out-dir", default="artifacts/apps_eval/runs")
    run.add_argument("--emit-l6-handoff", action="store_true")
    matrix = sub.add_parser("run-matrix")
    matrix.add_argument("--app", default="")
    matrix.add_argument("--split", default="")
    matrix.add_argument("--mode", choices=["snapshot", "live_adapter"], default="snapshot")
    matrix.add_argument("--deterministic-only", action=argparse.BooleanOptionalAction, default=True)
    matrix.add_argument("--out-dir", default="artifacts/apps_eval/runs")
    compare = sub.add_parser("compare")
    compare.add_argument("--record", required=True)
    compare.add_argument("--baseline", required=True)
    compare_named = sub.add_parser("compare-baseline")
    compare_named.add_argument("--record", required=True)
    compare_named.add_argument("--name", required=True)
    compare_named.add_argument("--baseline-dir", default="apps_eval/baselines")
    promote = sub.add_parser("promote-baseline")
    promote.add_argument("--record", required=True)
    promote.add_argument("--name", required=True)
    promote.add_argument("--baseline-dir", default="apps_eval/baselines")
    promote.add_argument("--allow-failing", action="store_true")
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
    if args.command == "validate-suite":
        problems = validate_suite_fixtures(args.suite)
        if problems:
            print(json.dumps({"suite": args.suite, "valid": False, "problems": problems}, indent=2, sort_keys=True))
            return 1
        print(json.dumps({"suite": args.suite, "valid": True, "problems": []}, indent=2, sort_keys=True))
        return 0
    if args.command == "scaffold-apps-rg-scenario":
        result = scaffold_apps_rg_scenario(
            args.scenario_id,
            args.description,
            fixture_root=args.fixture_root,
            overwrite=bool(args.overwrite),
        )
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
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
    if args.command == "run-matrix":
        summary = run_matrix(
            app_id=args.app,
            split=args.split,
            mode=args.mode,
            deterministic_only=bool(args.deterministic_only),
            out_dir=args.out_dir,
        )
        print(summary["artifact_paths"]["matrix_summary"])
        return 0 if summary["verdict"] == "pass" else 1
    if args.command == "compare":
        record = json.loads(Path(args.record).read_text(encoding="utf-8"))
        baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
        summary = compare_record_to_baseline(record, baseline)
        print(json.dumps(summary.to_dict(), indent=2, sort_keys=True))
        return 0 if summary.verdict != "regression" else 1
    if args.command == "compare-baseline":
        record = json.loads(Path(args.record).read_text(encoding="utf-8"))
        baseline = load_baseline(args.name, args.baseline_dir)
        summary = compare_record_to_baseline(record, baseline)
        print(json.dumps(summary.to_dict(), indent=2, sort_keys=True))
        return 0 if summary.verdict != "regression" else 1
    if args.command == "promote-baseline":
        path = promote_baseline(
            args.record,
            args.name,
            baseline_dir=args.baseline_dir,
            require_pass=not bool(args.allow_failing),
        )
        print(path.as_posix())
        return 0
    if args.command == "render":
        print(render_record(args.record), end="")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
