#!/usr/bin/env python3
"""
Anti-Pattern Pre-Commit Check

Scans staged Python files for landmine anti-patterns.
Used as a pre-commit hook to prevent introduction of new anti-patterns.

Usage:
    python ops_scripts/ci/check_anti_patterns.py [file1.py file2.py ...]

    # Generate baseline:
    python ops_scripts/ci/check_anti_patterns.py --write-baseline

    # Pre-commit hook integration:
    - id: check-anti-patterns
      name: Check Anti-Patterns
      entry: python ops_scripts/ci/check_anti_patterns.py
      language: python
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Force UTF-8 encoding for Windows compatibility
import io
import locale
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Ensure project root is in path - guardian: allow-global-mutation
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L5_safety.validators.anti_pattern_scanner_validator import (
    AntiPatternScanner,
)
from agentic_core.L5_safety.validators.base_detector_validator import (
    EnforcementLevel,
)

# Baseline file path
BASELINE_FILE = PROJECT_ROOT / "ops_scripts" / "hooks" / "landmine_baseline.txt"


def load_baseline() -> set[str]:
    """Load baseline violations from file."""
    if not BASELINE_FILE.exists():
        return set()

    try:
        content = BASELINE_FILE.read_text(encoding="utf-8")
        # Each line is a violation signature: file:line:category:message
        return set(line.strip() for line in content.splitlines() if line.strip())
    except (OSError, UnicodeDecodeError):
        return set()


def write_baseline(violations: list) -> None:
    """Write current violations to baseline file."""
    # Create deterministic violation signatures
    signatures = []
    for v in violations:
        # Normalize path to repo-relative POSIX path
        if isinstance(v.file_path, Path):
            if v.file_path.is_absolute():
                rel_path = v.file_path.relative_to(PROJECT_ROOT).as_posix()
            else:
                rel_path = v.file_path.as_posix()
        else:
            path_obj = Path(v.file_path)
            if path_obj.is_absolute():
                rel_path = path_obj.relative_to(PROJECT_ROOT).as_posix()
            else:
                rel_path = path_obj.as_posix()
        signature = f"{rel_path}:{v.line_number}:{v.category.value}:{v.message}"
        signatures.append(signature)

    # Sort for determinism
    signatures.sort()

    # Write baseline
    BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_FILE.write_text("\n".join(signatures) + "\n", encoding="utf-8")
    print(f"Wrote {len(signatures)} violations to {BASELINE_FILE.relative_to(PROJECT_ROOT)}")


def check_files(file_paths: list[str]) -> int:
    """
    Check specified files for anti-patterns.

    Args:
        file_paths: List of file paths to check

    Returns:
        Exit code: 0 if passed, 1 if violations found
    """
    # If no files specified (pre-commit --all-files), scan all Python files
    if not file_paths:
        all_python_files = list(PROJECT_ROOT.rglob("*.py"))
        # Skip tests, __pycache__, .nox, and other non-source directories
        exclude_dirs = ["tests", "__pycache__", ".nox", ".git", "archives", ".backup", "ops_scripts"]
        python_files = [
            f for f in all_python_files
            if not any(exclude_dir in str(f) for exclude_dir in exclude_dirs)
        ]
    else:
        # Filter to only Python files
        python_files = []
        for f in file_paths:
            if f.endswith(".py"):
                path_obj = Path(f)
                # Try relative to current directory first, then project root
                if not path_obj.exists():
                    path_obj = PROJECT_ROOT / path_obj
                if path_obj.exists():
                    python_files.append(path_obj)

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

    # Load baseline and compute new violations
    baseline = load_baseline()
    current_violations = report.all_violations

    # Create signatures for current violations
    current_signatures = set()
    for v in current_violations:
        # Normalize path to repo-relative POSIX path
        if isinstance(v.file_path, Path):
            if v.file_path.is_absolute():
                rel_path = v.file_path.relative_to(PROJECT_ROOT).as_posix()
            else:
                rel_path = v.file_path.as_posix()
        else:
            # If it's already a string, make sure it's repo-relative
            path_obj = Path(v.file_path)
            if path_obj.is_absolute():
                rel_path = path_obj.relative_to(PROJECT_ROOT).as_posix()
            else:
                rel_path = path_obj.as_posix()
        signature = f"{rel_path}:{v.line_number}:{v.category.value}:{v.message}"
        current_signatures.add(signature)

    # New violations = current - baseline
    new_signatures = current_signatures - baseline
    new_violations = []
    for v in current_violations:
        # Normalize path for signature comparison
        if isinstance(v.file_path, Path):
            if v.file_path.is_absolute():
                rel_path = v.file_path.relative_to(PROJECT_ROOT).as_posix()
            else:
                rel_path = v.file_path.as_posix()
        else:
            path_obj = Path(v.file_path)
            if path_obj.is_absolute():
                rel_path = path_obj.relative_to(PROJECT_ROOT).as_posix()
            else:
                rel_path = path_obj.as_posix()
        signature = f"{rel_path}:{v.line_number}:{v.category.value}:{v.message}"
        if signature in new_signatures:
            new_violations.append(v)

    if not new_violations:
        # No new violations, check passed
        if current_violations:
            print(f"[OK] {len(current_violations)} existing violations, 0 new violations")
        return 0

    # Only print on failure (Signal vs Noise)
    print(f"\n[BLOCK] Found {len(new_violations)} NEW anti-pattern landmine(s) "
          f"(out of {len(current_violations)} total):")

    # Group by category
    new_by_category = {}
    for violation in new_violations:
        cat = violation.category.value
        new_by_category[cat] = new_by_category.get(cat, 0) + 1

    for category, count in sorted(new_by_category.items()):
        print(f"  • {category}: {count}")

    # Show details for each NEW violation
    for violation in new_violations:
        print(f"\n[FAIL] {violation.file_path.name}:{violation.line_number}")
        print(f"   [{violation.category.value}] {violation.message}")
        # Handle unicode characters in evidence
        evidence = violation.evidence[:80]
        if isinstance(evidence, str):
            evidence = evidence.encode('ascii', errors='replace').decode('ascii')
        print(f"   Evidence: {evidence}...")
        if violation.suggested_fix:
            fix_preview = violation.suggested_fix.split("\n")[0]
            if isinstance(fix_preview, str):
                fix_preview = fix_preview.encode('ascii', errors='replace').decode('ascii')
            print(f"   [FIX] {fix_preview}")

    print("\n[ACTION] Fix NEW violations or add '# guardian: allow-<pattern>' to whitelist.")
    print("         To update baseline with current violations: python ops_scripts/ci/check_anti_patterns.py --write-baseline")

    return 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check anti-pattern violations")
    parser.add_argument(
        "--write-baseline",
        action="store_true",
        help="Generate baseline file from current violations"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Files to check (default: all staged files if run from pre-commit)"
    )

    args = parser.parse_args()

    # If writing baseline, require explicit authorization
    if args.write_baseline:
        if os.environ.get("ALLOW_LANDMINE_BASELINE_WRITE") != "1":
            print("[ERROR] --write-baseline requires ALLOW_LANDMINE_BASELINE_WRITE=1 environment variable")
            print("        This prevents accidental baseline dilution in CI/automation")
            print("        To authorize: ALLOW_LANDMINE_BASELINE_WRITE=1 python ops_scripts/ci/check_anti_patterns.py --write-baseline")
            return 1

        all_python_files = list(PROJECT_ROOT.rglob("*.py"))
        # Skip tests, __pycache__, .nox, and other non-source directories
        exclude_dirs = ["tests", "__pycache__", ".nox", ".git", "archives", ".backup", "ops_scripts"]
        all_python_files = [
            f for f in all_python_files
            if not any(exclude_dir in str(f) for exclude_dir in exclude_dirs)
        ]

        scanner = AntiPatternScanner(
            project_root=PROJECT_ROOT,
            enforcement_level=EnforcementLevel.WARNING,
        )

        report = scanner.scan_changed_files(all_python_files)
        write_baseline(report.all_violations)
        return 0

    # Normal check mode
    return check_files(args.files)


if __name__ == "__main__":
    sys.exit(main())
