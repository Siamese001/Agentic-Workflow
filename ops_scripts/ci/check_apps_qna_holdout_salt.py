"""CI gate: Detect holdout_salt changes in apps_qna eval rubrics.

The holdout_salt determines how interview slugs are assigned to
holdout vs dev partitions. Changing it reassigns ALL slugs,
invalidating prior calibration data.

Checks:
1. holdout_salt exists in eval_rubrics.yaml
2. holdout_salt has not changed in recent commits (default: last 30 days)

Exit codes:
    0: Salt is frozen (no recent changes)
    1: Salt changed recently OR salt is missing

Usage:
    python ops_scripts/ci/check_apps_qna_holdout_salt.py [--days N] [--json]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
RUBRICS_PATH = REPO_ROOT / "apps_qna" / "config" / "domain_contract" / "eval_rubrics.yaml"

# Canonical salt value (frozen)
EXPECTED_SALT = "a3f7e9d2c8b1a6f5d4e3c2b1a9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1"


def _extract_salt_from_yaml() -> str | None:
    """Extract holdout_salt from eval_rubrics.yaml."""
    if not RUBRICS_PATH.exists():
        return None

    try:
        import yaml  # noqa: PLC0415
        with open(RUBRICS_PATH, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f)

        if not isinstance(doc, dict):
            return None

        return doc.get("holdout_salt")
    except Exception:  # noqa: BLE001
        # Fallback: regex extraction
        content = RUBRICS_PATH.read_text(encoding="utf-8")
        match = re.search(r'holdout_salt:\s*"([^"]+)"', content)
        return match.group(1) if match else None


def _get_salt_changes(days: int = 30) -> list[dict[str, Any]]:
    """Get commits that modified holdout_salt in recent history."""
    changes: list[dict[str, Any]] = []

    try:
        # Get commits touching the file in last N days
        result = subprocess.run(
            [
                "git", "log",
                f"--since={days} days ago",
                "--format=%H|%ai|%s",
                "--",
                str(RUBRICS_PATH.relative_to(REPO_ROOT)),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return changes

        for line in result.stdout.strip().split("\n"):
            if "|" not in line:
                continue
            parts = line.split("|", 2)
            if len(parts) >= 3:
                changes.append({
                    "sha": parts[0],
                    "date": parts[1],
                    "message": parts[2],
                })

    except Exception:  # noqa: BLE001
        pass

    return changes


def _check_salt_line_changes(commits: list[str]) -> bool:
    """Check if any commit actually changed the holdout_salt line."""
    if not commits:
        return False

    try:
        for commit_sha in commits:
            # Get diff for this commit
            result = subprocess.run(
                ["git", "show", commit_sha, "--", str(RUBRICS_PATH.relative_to(REPO_ROOT))],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if "holdout_salt" in result.stdout:
                return True

    except Exception:  # noqa: BLE001
        pass

    return False


def run_checks(days: int = 30) -> tuple[bool, list[dict[str, Any]]]:
    """Run all holdout salt checks.

    Returns:
        Tuple of (passed, findings)
    """
    findings: list[dict[str, Any]] = []

    # Check 1: Salt exists
    current_salt = _extract_salt_from_yaml()
    if current_salt is None:
        findings.append({
            "check_id": "HOLDOUT_SALT_MISSING",
            "severity": "ERROR",
            "message": f"holdout_salt not found in {RUBRICS_PATH.relative_to(REPO_ROOT)}",
        })
        return False, findings

    # Check 2: Salt matches expected value
    if current_salt != EXPECTED_SALT:
        findings.append({
            "check_id": "HOLDOUT_SALT_CHANGED",
            "severity": "ERROR",
            "message": f"holdout_salt changed from canonical value! Expected: {EXPECTED_SALT[:16]}..., Found: {current_salt[:16]}...",
            "expected": EXPECTED_SALT,
            "found": current_salt,
        })

    # Check 3: Recent commits touching the file
    recent_commits = _get_salt_changes(days)
    if recent_commits:
        # Check if any actually modified the salt line
        commit_shas = [c["sha"] for c in recent_commits]
        salt_changed = _check_salt_line_changes(commit_shas)

        if salt_changed:
            findings.append({
                "check_id": "HOLDOUT_SALT_RECENTLY_MODIFIED",
                "severity": "WARN",
                "message": f"holdout_salt line modified in last {days} days — corpus reassignment risk!",
                "commits": recent_commits[:3],  # Show last 3
            })

    passed = not any(f.get("severity") == "ERROR" for f in findings)
    return passed, findings


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check apps_qna holdout_salt frozen status"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Lookback window for recent changes (default: 30)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON report",
    )
    parser.add_argument(
        "--fail-closed",
        action="store_true",
        help="Fail on any finding including WARN",
    )
    args = parser.parse_args(argv)

    # Environment override
    fail_closed = args.fail_closed or os.environ.get("HOLDOUT_SALT_FAIL_CLOSED") == "1"

    passed, findings = run_checks(args.days)

    result = {
        "passed": passed,
        "advisory": not fail_closed,
        "days_window": args.days,
        "expected_salt_prefix": EXPECTED_SALT[:16] + "...",
        "findings": findings,
        "summary": {
            "total": len(findings),
            "error": sum(1 for f in findings if f.get("severity") == "ERROR"),
            "warn": sum(1 for f in findings if f.get("severity") == "WARN"),
        },
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = "PASS" if passed else "FAIL"
        mode = "fail-closed" if fail_closed else "advisory"
        print(f"apps_qna holdout_salt check: {status} ({mode})")
        print(f"  Expected: {EXPECTED_SALT[:32]}...")
        print(f"  Findings: {result['summary']['total']} "
              f"({result['summary']['error']} error, "
              f"{result['summary']['warn']} warn)")

        if findings:
            print()
            for f in findings:
                icon = "✗" if f.get("severity") == "ERROR" else "⚠"
                print(f"  [{icon}] {f['check_id']}: {f.get('message', '')}")

    # Exit code
    if fail_closed:
        return 0 if passed and result["summary"]["warn"] == 0 else 1
    else:
        return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
