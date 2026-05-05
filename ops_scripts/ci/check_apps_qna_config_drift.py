"""CI gate: Detect config drift in apps_qna domain-contract YAMLs.

Checks:
1. No drift violations (policy_hash/version mismatches within same task_class)
2. All policy_hash-bearing configs have version and status fields

Exit codes:
    0: All checks passed (or advisory mode with zero ERRORs)
    1: Drift or missing fields detected (fail-closed mode)

Usage:
    python ops_scripts/ci/check_apps_qna_config_drift.py [--json] [--fail-closed]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

# Add repo root to path for imports
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

# Delay import until path is set
def _get_inventory_module():
    """Lazy import to ensure path is set."""
    from apps_qna.config.config_inventory import (
        ConfigInventoryReport,
        scan_config_inventory,
    )
    return ConfigInventoryReport, scan_config_inventory


def _policy_hash_missing_version_status(report: Any) -> list[dict[str, Any]]:
    """Find entries with policy_hash but missing version or status."""
    violations: list[dict[str, Any]] = []

    for entry in report.entries:
        if not entry.policy_hash:
            continue  # No policy_hash, skip

        missing: list[str] = []
        if not entry.version:
            missing.append("version")
        if not entry.status:
            missing.append("status")

        if missing:
            violations.append({
                "check_id": "POLICY_HASH_MISSING_FIELDS",
                "filename": entry.filename,
                "record_id": entry.record_id,
                "policy_hash": entry.policy_hash,
                "missing_fields": missing,
                "severity": "ERROR",
            })

    return violations


def _drift_to_findings(report: ConfigInventoryReport) -> list[dict[str, Any]]:
    """Convert drift violations to finding format."""
    findings: list[dict[str, Any]] = []

    for drift in report.drift_violations:
        findings.append({
            "check_id": f"DRIFT_{drift.field.upper()}",
            "severity": "ERROR",
            "field": drift.field,
            "file_a": drift.file_a,
            "file_b": drift.file_b,
            "value_a": drift.value_a,
            "value_b": drift.value_b,
            "message": (
                f"{drift.field} drift: '{drift.value_a}' in {drift.file_a} "
                f"vs '{drift.value_b}' in {drift.file_b}"
            ),
        })

    return findings


def _missing_canonical_to_findings(report: ConfigInventoryReport) -> list[dict[str, Any]]:
    """Convert missing canonical fields to finding format."""
    findings: list[dict[str, Any]] = []
    critical_fields = ("app_id", "version", "policy_hash")

    for filename, missing in report.missing_fields.items():
        critical_missing = [f for f in missing if f in critical_fields]
        if critical_missing:
            findings.append({
                "check_id": "MISSING_CANONICAL_FIELDS",
                "severity": "ERROR",
                "filename": filename,
                "missing_fields": critical_missing,
                "message": f"Missing critical fields in {filename}: {', '.join(critical_missing)}",
            })

    return findings


def run_checks() -> tuple[bool, list[dict[str, Any]], Any]:
    """Run all drift checks.

    Returns:
        Tuple of (all_passed, findings, report)
    """
    _, scan_config_inventory = _get_inventory_module()
    report = scan_config_inventory()

    findings: list[dict[str, Any]] = []

    # Check 1: Drift violations
    findings.extend(_drift_to_findings(report))

    # Check 2: Missing canonical fields (app_id, version, policy_hash)
    findings.extend(_missing_canonical_to_findings(report))

    # Check 3: policy_hash entries must have version + status
    findings.extend(_policy_hash_missing_version_status(report))

    # Pass if no ERROR findings
    errors = [f for f in findings if f.get("severity") == "ERROR"]
    all_passed = len(errors) == 0

    return all_passed, findings, report


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check apps_qna domain-contract config drift"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON report",
    )
    parser.add_argument(
        "--fail-closed",
        action="store_true",
        help="Fail on any finding (default: advisory, zero errors = pass)",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Write JSON report to file",
    )
    args = parser.parse_args(argv)

    # Environment override for fail-closed
    fail_closed = args.fail_closed or os.environ.get("APPS_QNA_CONFIG_DRIFT_FAIL_CLOSED") == "1"

    all_passed, findings, report = run_checks()

    result = {
        "passed": all_passed,
        "advisory": not fail_closed,
        "files_scanned": report.files_scanned,
        "records_parsed": report.records_parsed,
        "aligned": report.aligned,
        "findings": findings,
        "summary": {
            "total": len(findings),
            "error": sum(1 for f in findings if f.get("severity") == "ERROR"),
            "warn": sum(1 for f in findings if f.get("severity") == "WARN"),
            "info": sum(1 for f in findings if f.get("severity") == "INFO"),
        },
    }

    # Write report file if requested
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

    # Output
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = "PASS" if all_passed else "FAIL"
        mode = "fail-closed" if fail_closed else "advisory"
        print(f"apps_qna config drift check: {status} ({mode})")
        print(f"  Files scanned: {report.files_scanned}")
        print(f"  Records parsed: {report.records_parsed}")
        print(f"  Findings: {result['summary']['total']} "
              f"({result['summary']['error']} error, "
              f"{result['summary']['warn']} warn, "
              f"{result['summary']['info']} info)")

        if findings:
            print()
            for f in findings:
                icon = "✗" if f.get("severity") == "ERROR" else "⚠" if f.get("severity") == "WARN" else "ℹ"
                print(f"  [{icon}] {f['check_id']}: {f.get('message', '')}")

    # Exit code
    if fail_closed:
        return 0 if all_passed else 1
    else:
        # Advisory: pass if zero errors (warnings ok)
        return 0 if result["summary"]["error"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
