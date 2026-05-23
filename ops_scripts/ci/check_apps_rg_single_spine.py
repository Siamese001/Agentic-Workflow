"""APPS-RG-SINGLE-SPINE — W1 CI ratchet (plan apps-rg-spine-only-unification-d8f4a2).

Blocks second-pipeline imports and patterns in product paths:
  apps_rg/__main__.py
  apps_rg/runtime/orchestration/canonical_dispatch.py
  apps_rg/runtime/spine/**
  apps_rg/runtime/sections/**

Fail-closed by default (exit 1 on ERROR findings).
Bypass: APPS_RG_SINGLE_SPINE_GATE_BYPASS=1
Advisory override: APPS_RG_SINGLE_SPINE_GATE_ADVISORY=1
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci.apps_rg_single_spine_scan import (  # noqa: E402
    PRODUCT_SCAN_REL_PATHS,
    SPINE_SECTION_CONTRACT_FILENAMES,
    findings_with_errors,
    scan_product_paths,
    summarize_findings,
)

VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "ci" / "apps_rg_single_spine_violations.jsonl"
REPORT_JSON = REPO_ROOT / "artifacts" / "ci" / "apps_rg_single_spine_gate.json"


def _emit_jsonl(findings: list) -> None:
    VIOLATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()
    with VIOLATIONS_LOG.open("w", encoding="utf-8") as fh:
        for f in findings:
            row = {
                "ts": ts,
                "code": f.code,
                "severity": f.severity,
                "file": f.file,
                "line": f.line,
                "message": f.message,
                "extra": f.extra,
            }
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _emit_report(findings: list, exit_code: int) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    errors = findings_with_errors(findings)
    REPORT_JSON.write_text(
        json.dumps(
            {
                "gate": "APPS-RG-SINGLE-SPINE",
                "plan_id": "apps-rg-spine-only-unification-d8f4a2",
                "wave": "W1",
                "status": "PASS" if exit_code == 0 else "FAIL",
                "product_scan_paths": list(PRODUCT_SCAN_REL_PATHS),
                "spine_section_contract_filenames": list(SPINE_SECTION_CONTRACT_FILENAMES),
                "error_count": len(errors),
                "summary_by_code": summarize_findings(errors),
                "proof_classification": "CI_STATIC_CONTRACT_SCAN",
                "explicit_non_claims": [
                    "not LIVE_RUNTIME_PROOF",
                    "not RELEASE_ELIGIBLE_PROOF",
                    "baseline violations expected until W2 spine_run lands",
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="apps_rg single-spine W1 ratchet")
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Print findings and always exit 0 (for inventory)",
    )
    _ = parser.parse_args(argv)

    if os.environ.get("APPS_RG_SINGLE_SPINE_GATE_BYPASS", "").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        print("[APPS-RG-SINGLE-SPINE] BYPASS — APPS_RG_SINGLE_SPINE_GATE_BYPASS=1")
        _emit_report([], 0)
        return 0

    findings = scan_product_paths(REPO_ROOT)
    errors = findings_with_errors(findings)
    _emit_jsonl(findings)

    advisory = os.environ.get("APPS_RG_SINGLE_SPINE_GATE_ADVISORY", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    report_only = "--report-only" in (argv or sys.argv[1:])

    for f in errors[:50]:
        print(f"[{f.code}] {f.file}:{f.line} — {f.message}")
    if len(errors) > 50:
        print(f"... and {len(errors) - 50} more ERROR findings")

    print(
        f"[APPS-RG-SINGLE-SPINE] ERROR findings={len(errors)} "
        f"total={len(findings)} log={VIOLATIONS_LOG.relative_to(REPO_ROOT)}"
    )

    if report_only or advisory:
        _emit_report(findings, 0)
        return 0

    exit_code = 0 if not errors else 1
    _emit_report(findings, exit_code)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
