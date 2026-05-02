"""CLI entry-point for the apps_e2e verifier (W2.3/W2.4).

Usage:
    python -m tools.certification.apps_e2e.verifier_cli --mode <smoke|warn|strict> [--app NAME]

Reads each spec's bundle from artifacts/certification/apps_e2e/<app>/<app>_e2e_proof.json.
Emits a verifier_report.json under artifacts/certification/apps_e2e/.

Exit codes:
  0 — pass (smoke: no schema/hash violations; warn: always 0; strict: no S1-S19 violations)
  1 — fail (one or more rules fired in non-warn mode)
  2 — usage error
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tools.certification.apps_e2e.app_specs import APP_SPECS, find_spec, runnable_specs
from tools.certification.apps_e2e.certification_levels import compute_level
from tools.certification.apps_e2e.hash_utils import REPO_ROOT, utc_now_iso
from tools.certification.apps_e2e.paths import AppCertPaths
from tools.certification.apps_e2e.shared_verifier import (
    Violation,
    format_violation,
    verify_with_mode,
)
from tools.certification.apps_e2e.verifier_modes import VerifierMode, exit_code_for, parse_mode


VERIFIER_REPORT_PATH = REPO_ROOT / "artifacts" / "certification" / "apps_e2e" / "verifier_report.json"


def _load_bundle(spec) -> dict | None:
    p = AppCertPaths(spec.app_name).proof_bundle
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _violation_to_dict(v: Violation) -> dict:
    return {
        "rule_id": v.rule_id,
        "stage": v.stage,
        "expected": v.expected,
        "observed": v.observed,
        "artifact_ref": v.artifact_ref,
    }


def run_verifier(mode: VerifierMode, app_name: str | None = None) -> dict:
    """Run the verifier across one or all specs. Returns a verifier_report dict."""
    if app_name:
        spec = find_spec(app_name)
        specs = (spec,) if spec else ()
    else:
        specs = APP_SPECS

    rows = []
    for spec in specs:
        if spec is None:
            continue
        bundle = _load_bundle(spec)
        viols = verify_with_mode(bundle, spec, mode)
        level = compute_level(bundle, spec, violations=viols)
        rows.append({
            "app_name": spec.app_name,
            "mode": mode.value,
            "bundle_present": bundle is not None,
            "certification_level": level.value,
            "violation_count": len(viols),
            "violations": [_violation_to_dict(v) for v in viols],
        })

    has_violations = any(r["violation_count"] > 0 for r in rows)
    return {
        "verifier_report_schema_version": "apps_e2e_verifier_report/2026-05-02/v1",
        "generated_at_utc": utc_now_iso(),
        "mode": mode.value,
        "rows": rows,
        "summary": {
            "n_apps": len(rows),
            "n_pass": sum(1 for r in rows if r["violation_count"] == 0),
            "n_fail": sum(1 for r in rows if r["violation_count"] > 0),
        },
        "exit_code": exit_code_for(mode, has_violations),
    }


def _print_summary(report: dict) -> None:
    print(f"\nVerifier mode: {report['mode']}")
    print(f"Apps:    {report['summary']['n_apps']}")
    print(f"Pass:    {report['summary']['n_pass']}")
    print(f"Fail:    {report['summary']['n_fail']}")
    print()
    for r in report["rows"]:
        verdict = "PASS" if r["violation_count"] == 0 else "FAIL"
        print(f"  {r['app_name']:<22} {verdict:<5} level={r['certification_level']:<26} "
              f"violations={r['violation_count']}")


def _print_violations_to_stderr(report: dict) -> None:
    """Emit JSONL violations to stderr for CI log-parsers + warn-mode diff."""
    for row in report["rows"]:
        for v in row["violations"]:
            line = {"app_name": row["app_name"], **v}
            print(json.dumps(line, sort_keys=True), file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="verifier_cli")
    p.add_argument("--mode", required=True, help="smoke | warn | strict (required)")
    p.add_argument("--app", default=None, help="Verify a single app (default: all specs)")
    p.add_argument("--matrix", default=None, help="Optional alias for --app for plan compat")
    p.add_argument("--report", default=None, help="Override verifier_report.json output path")
    args = p.parse_args(argv)

    try:
        mode = parse_mode(args.mode)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    target_app = args.app or args.matrix
    report = run_verifier(mode, target_app)

    out_path = Path(args.report) if args.report else VERIFIER_REPORT_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    _print_summary(report)
    _print_violations_to_stderr(report)
    return report["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
