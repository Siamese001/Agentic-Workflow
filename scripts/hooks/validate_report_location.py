#!/usr/bin/env python3
"""
Pre-commit Hook: Validate Report Location

Validates that report files are stored in the SSOT location (docs/reports/).
Supports multiple enforcement modes for gradual rollout.

Usage:
    python scripts/hooks/validate_report_location.py [options]

Options:
    --mode MODE     Enforcement mode: dry-run, warn, strict (default: warn)
    --fix           Auto-move misplaced reports to SSOT location
    --quiet         Suppress non-error output
    --log           Log violations to compliance report
    --staged-only   Only check staged files (for pre-commit)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Use ASCII-safe symbols for Windows compatibility
SYMBOL_OK = "[OK]"
SYMBOL_WARN = "[WARN]"
SYMBOL_ERROR = "[ERROR]"
SYMBOL_INFO = "[INFO]"
SYMBOL_MOVE = "->"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.utils.report_location_validator_types import (  # noqa: E402
    SSOT_REPORTS_DIR,
    ReportLocationValidator,
)

COMPLIANCE_LOG_DIR = PROJECT_ROOT / "logs" / "compliance_reports"


def get_staged_files() -> list[Path]:
    """Get list of staged files from git."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return [PROJECT_ROOT / f for f in result.stdout.strip().split("\n") if f]
    except Exception:
        pass
    return []


def log_violations(misplaced: list, mode: str, action_taken: str) -> Path:
    """Log violations to compliance report."""
    COMPLIANCE_LOG_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = COMPLIANCE_LOG_DIR / f"report_location_violations_{timestamp}.json"

    report = {
        "timestamp": datetime.now().isoformat(),
        "mode": mode,
        "action_taken": action_taken,
        "total_violations": len(misplaced),
        "violations": [
            {
                "file": r.current_location,
                "expected": r.expected_location,
                "violation_type": r.violation_type,
            }
            for r in misplaced
        ],
    }

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return log_path


def main() -> int:
    """Main entry point for the pre-commit hook."""
    parser = argparse.ArgumentParser(
        description="Validate report file locations against SSOT requirements."
    )
    parser.add_argument(
        "--mode",
        choices=["dry-run", "warn", "strict"],
        default="warn",
        help="Enforcement mode (default: warn)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-move misplaced reports to SSOT location",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress non-error output",
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="Log violations to compliance report",
    )
    parser.add_argument(
        "--staged-only",
        action="store_true",
        help="Only check staged files",
    )
    args = parser.parse_args()

    validator = ReportLocationValidator(PROJECT_ROOT, dry_run=not args.fix)

    # Get files to check
    if args.staged_only:
        staged = get_staged_files()
        misplaced = [
            validator.validate_file(f)
            for f in staged
            if validator.is_report_file(f) and not validator.is_approved_location(f)
        ]
        misplaced = [r for r in misplaced if not r.is_compliant]
    else:
        misplaced = validator.get_misplaced_reports()

    if not misplaced:
        if not args.quiet:
            print(f"{SYMBOL_OK} All reports are in SSOT-compliant locations.")
        return 0

    # Report violations
    print(f"\n{SYMBOL_WARN} Found {len(misplaced)} misplaced report(s):")
    print(f"   SSOT Location: {SSOT_REPORTS_DIR}/\n")

    for result in misplaced[:20]:
        print(f"   {SYMBOL_ERROR} {result.current_location}")
        print(f"      {SYMBOL_MOVE} Move to: {result.expected_location}")

    if len(misplaced) > 20:
        print(f"\n   ... and {len(misplaced) - 20} more violations")

    # Log violations if requested
    if args.log:
        action = "fix" if args.fix else args.mode
        log_path = log_violations(misplaced, args.mode, action)
        print(f"\n{SYMBOL_INFO} Violations logged to: {log_path.relative_to(PROJECT_ROOT)}")

    # Handle fix mode
    if args.fix:
        print("\n[FIX] Auto-fix mode enabled - moving files...")
        moved_count = 0
        for result in misplaced:
            try:
                source = PROJECT_ROOT / result.current_location
                dest = PROJECT_ROOT / result.expected_location
                dest.parent.mkdir(parents=True, exist_ok=True)
                source.rename(dest)
                moved_count += 1
                print(f"   {SYMBOL_OK} Moved: {result.current_location}")
            except Exception as e:
                print(f"   {SYMBOL_ERROR} Failed to move {result.current_location}: {e}")
        print(f"\n{SYMBOL_INFO} Moved {moved_count}/{len(misplaced)} files to SSOT location.")
        return 0

    # Handle enforcement modes
    if args.mode == "strict":
        print(f"\n{SYMBOL_ERROR} Commit blocked: Report location violations detected.")
        print("   Run with --fix to auto-move files, or manually relocate them.")
        return 1
    elif args.mode == "warn":
        print(f"\n{SYMBOL_WARN} Violations detected - commit allowed but please fix.")
        print("   Run: python scripts/hooks/validate_report_location.py --fix")
        return 0
    else:  # dry-run
        print(f"\n{SYMBOL_INFO} [DRY-RUN] Violations detected but no action taken.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
