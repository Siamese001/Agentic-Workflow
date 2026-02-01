#!/usr/bin/env python3
"""
Pre-commit Hook: Validate Report Location

Validates that report files are stored in the SSOT location (docs/reports/).
Runs in dry-run mode by default - reports violations without blocking commits.

Usage:
    python scripts/hooks/validate_report_location.py [--strict] [--fix]

Options:
    --strict    Block commit if violations are found
    --fix       Auto-move misplaced reports to SSOT location (requires --strict)
    --quiet     Suppress non-error output
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.utils.report_location_validator import (
    ReportLocationValidator,
    SSOT_REPORTS_DIR,
)


def main() -> int:
    """Main entry point for the pre-commit hook."""
    parser = argparse.ArgumentParser(
        description="Validate report file locations against SSOT requirements."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Block commit if violations are found",
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
    args = parser.parse_args()

    validator = ReportLocationValidator(PROJECT_ROOT, dry_run=not args.fix)
    misplaced = validator.get_misplaced_reports()

    if not misplaced:
        if not args.quiet:
            print("✅ All reports are in SSOT-compliant locations.")
        return 0

    # Report violations
    print(f"\n⚠️  Found {len(misplaced)} misplaced report(s):")
    print(f"   SSOT Location: {SSOT_REPORTS_DIR}/\n")

    for result in misplaced[:20]:  # Limit output to first 20
        print(f"   ❌ {result.current_location}")
        print(f"      → Move to: {result.expected_location}")

    if len(misplaced) > 20:
        print(f"\n   ... and {len(misplaced) - 20} more violations")

    if args.fix:
        print("\n🔧 Auto-fix mode enabled - moving files...")
        moved_count = 0
        for result in misplaced:
            try:
                source = PROJECT_ROOT / result.current_location
                dest = PROJECT_ROOT / result.expected_location
                dest.parent.mkdir(parents=True, exist_ok=True)
                source.rename(dest)
                moved_count += 1
                print(f"   ✅ Moved: {result.current_location}")
            except Exception as e:
                print(f"   ❌ Failed to move {result.current_location}: {e}")
        print(f"\n📦 Moved {moved_count}/{len(misplaced)} files to SSOT location.")
        return 0

    if args.strict:
        print("\n❌ Commit blocked: Report location violations detected.")
        print("   Run with --fix to auto-move files, or manually relocate them.")
        return 1

    # Dry-run mode (default) - warn but don't block
    print("\n⚠️  [DRY-RUN] Violations detected but commit not blocked.")
    print("   Run with --strict to enforce SSOT compliance.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
