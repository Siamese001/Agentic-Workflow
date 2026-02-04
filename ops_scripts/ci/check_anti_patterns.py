#!/usr/bin/env python3
"""
Anti-Pattern Pre-Commit Check

Scans staged Python files for landmine anti-patterns.
Used as a pre-commit hook to prevent introduction of new anti-patterns.

Usage:
    python ops_scripts/ci/check_anti_patterns.py [file1.py file2.py ...]

    # Pre-commit hook integration:
    - id: check-anti-patterns
      name: Check Anti-Patterns
      entry: python ops_scripts/ci/check_anti_patterns.py
      language: python
"""

import sys
from pathlib import Path

# Ensure project root is in path - guardian: allow-global-mutation
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L5_safety.validators.anti_pattern_scanner import (
    AntiPatternScanner,
)
from agentic_core.L5_safety.validators.anti_patterns.base_detector import (
    EnforcementLevel,
)


def check_files(file_paths: list[str]) -> int:
    """
    Check specified files for anti-patterns.

    Args:
        file_paths: List of file paths to check

    Returns:
        Exit code: 0 if passed, 1 if violations found
    """
    if not file_paths:
        print("No files to check.")
        return 0

    # Filter to only Python files
    python_files = [Path(f) for f in file_paths if f.endswith(".py") and Path(f).exists()]

    if not python_files:
        print("No Python files to check.")
        return 0

    # Create scanner with warning level (for pre-commit, we warn but don't block)
    scanner = AntiPatternScanner(
        project_root=PROJECT_ROOT,
        enforcement_level=EnforcementLevel.WARNING,
    )

    # Scan only the specified files
    report = scanner.scan_changed_files(python_files)

    # Print results
    print(f"\n[SCAN] Anti-Pattern Check: {len(python_files)} file(s) scanned")

    if report.passed:
        print("[PASS] No anti-patterns detected!")
        return 0

    print(f"[WARN] Found {report.total_violations} anti-pattern violation(s):\n")

    # Group by category
    for category, count in report.violations_by_category.items():
        if count > 0:
            print(f"  [INFO] {category}: {count} violation(s)")

    print()

    # Show details for each violation
    for violation in report.all_violations:
        severity_tag = "[ERROR]" if violation.severity == "error" else "[WARN]"
        print(f"{severity_tag} {violation.file_path.name}:{violation.line_number}")
        print(f"   [{violation.category.value}] {violation.message}")
        print(f"   Evidence: {violation.evidence[:80]}...")
        if violation.suggested_fix:
            fix_preview = violation.suggested_fix.split("\n")[0]
            print(f"   [FIX] {fix_preview}")
        print()

    # For pre-commit, we block commits with violations (hard enforcement)
    # Change return value to 0 for warning mode
    print("[ERROR] Anti-pattern violations detected. Fix before committing.")
    print("   Add '# guardian: allow-<pattern>' comment to whitelist legitimate uses.")

    return 1  # Return 0 for warning mode, 1 for blocking mode


def main() -> int:
    """Main entry point."""
    # Get file paths from command line arguments
    file_paths = sys.argv[1:] if len(sys.argv) > 1 else []

    return check_files(file_paths)


if __name__ == "__main__":
    sys.exit(main())
