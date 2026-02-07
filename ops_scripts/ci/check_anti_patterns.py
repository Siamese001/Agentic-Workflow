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

from agentic_core.L5_safety.validators.base_detector import (
    EnforcementLevel,
)
from agentic_core.L5_safety.validators.anti_pattern_scanner import (
    AntiPatternScanner,
)


def check_files(file_paths: list[str]) -> int:
    """
    Check specified files for anti-patterns.

    Args:
        file_paths: List of file paths to check

    Returns:
        Exit code: 0 if passed, 1 if violations found
    """
    # Filter to only Python files
    python_files = [Path(f) for f in file_paths if f.endswith(".py") and Path(f).exists()]

    if not python_files:
        return 0

    # Create scanner with WARNING level to catch all potential issues
    # We enforce BLOCKING on these warnings to prevent debt accumulation
    scanner = AntiPatternScanner(
        project_root=PROJECT_ROOT,
        enforcement_level=EnforcementLevel.WARNING,
    )

    # Scan only the specified files
    report = scanner.scan_changed_files(python_files)

    if report.passed:
        return 0

    # Only print on failure (Signal vs Noise)
    print(f"\n[BLOCK] Found {report.total_violations} anti-pattern landmine(s):")

    # Group by category
    for category, count in report.violations_by_category.items():
        if count > 0:
            print(f"  • {category}: {count}")

    # Show details for each violation
    for violation in report.all_violations:
        print(f"\n[FAIL] {violation.file_path.name}:{violation.line_number}")
        print(f"   [{violation.category.value}] {violation.message}")
        print(f"   Evidence: {violation.evidence[:80]}...")
        if violation.suggested_fix:
            fix_preview = violation.suggested_fix.split("\n")[0]
            print(f"   [FIX] {fix_preview}")

    print("\n[ACTION] Fix violations or add '# guardian: allow-<pattern>' to whitelist.")

    return 1


def main() -> int:
    """Main entry point."""
    # Get file paths from command line arguments
    file_paths = sys.argv[1:] if len(sys.argv) > 1 else []

    return check_files(file_paths)


if __name__ == "__main__":
    sys.exit(main())
