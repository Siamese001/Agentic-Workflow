#!/usr/bin/env python3
"""
Hollow File Gate — T25 Pre-Commit Hook

Enforces the hollow file anti-pattern ratchet:
- Blocks new hollow files from being committed
- Warns on existing files that become hollow
- Generates baseline inventory and reports

Exit codes:
  0  — Gate passed (no violations)
  1  — Gate failed (violations found)
  2  — Error condition
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

# Add project root to Python path
project_root = Path(__file__).parents[2]
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.validators.anti_pattern_scanner_validator import (
    AntiPatternScanner,
    EnforcementLevel,
)
from agentic_core.L5_safety.validators.base_detector_validator import AntiPatternCategory


def load_baseline(baseline_path: Path) -> dict[str, Any]:
    """Load the hollow file baseline."""
    if not baseline_path.exists():
        return {}

    try:
        with open(baseline_path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"[hollow-file-gate] Warning: Failed to load baseline: {e}", file=sys.stderr)
        return {}


def save_baseline(baseline_path: Path, baseline: dict[str, Any]) -> None:
    """Save the hollow file baseline."""
    try:
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        with open(baseline_path, 'w') as f:
            json.dump(baseline, f, indent=2, sort_keys=True)
    except OSError as e:
        print(f"[hollow-file-gate] Error: Failed to save baseline: {e}", file=sys.stderr)


def get_changed_files(base_ref: str = "HEAD~1") -> list[Path]:
    """Get list of changed Python files."""
    try:
        # Get changed files vs base
        result = os.popen(f"git diff --name-only {base_ref} HEAD -- '*.py' 2>/dev/null || true").read()
        if not result.strip():
            # If base doesn't exist, check staged files
            result = os.popen("git diff --cached --name-only -- '*.py' 2>/dev/null || true").read()

        if not result.strip():
            return []

        changed_files = []
        for line in result.strip().split('\n'):
            if line.strip():
                file_path = project_root / line.strip()
                if file_path.exists() and file_path.suffix == ".py":
                    changed_files.append(file_path)

        return changed_files

    except Exception as e:
        print(f"[hollow-file-gate] Error getting changed files: {e}", file=sys.stderr)
        return []


def is_new_file(file_path: Path, base_ref: str = "HEAD~1") -> bool:
    """Check if file is new (not in base ref)."""
    try:
        # Try to show file in base ref
        result = os.popen(f"git show {base_ref}:{file_path.relative_to(project_root)} 2>/dev/null || true").read()
        return result.strip() == ""
    except Exception:
        return True


def scan_file(file_path: Path) -> dict[str, Any]:
    """Scan a single file for hollow violations."""
    scanner = AntiPatternScanner(project_root, enforcement_level=EnforcementLevel.HARD_BLOCK)
    violations = scanner.scan_file(file_path)

    # Filter for hollow file violations only
    hollow_violations = [v for v in violations if v.category == AntiPatternCategory.HOLLOW_FILE]

    if not hollow_violations:
        return {"status": "healthy", "violations": []}

    # Return the most severe violation
    violation = hollow_violations[0]  # Take first (most severe)

    return {
        "status": violation.metadata.get("classification", "unknown"),
        "violations": [v.to_dict() for v in hollow_violations],
    }


def initialize_baseline(scanner: AntiPatternScanner, baseline_path: Path) -> None:
    """Initialize baseline from current repository state."""
    print("[hollow-file-gate] Initializing baseline from current state...")

    baseline = {
        "version": "1.0",
        "generated_at": str(os.popen("git rev-parse HEAD").read().strip()),
        "files": {},
    }

    # Scan all Python files in default directories
    report = scanner.scan_repository()

    for violation in report.all_violations:
        if violation.category == AntiPatternCategory.HOLLOW_FILE:
            file_path = str(violation.file_path.relative_to(project_root))
            baseline["files"][file_path] = {
                "classification": violation.metadata.get("classification", "unknown"),
                "max_allowed_count": 1,  # Allow current count
                "first_seen": str(os.popen("git rev-parse HEAD").read().strip()),
            }

    save_baseline(baseline_path, baseline)
    print(f"[hollow-file-gate] Baseline initialized with {len(baseline['files'])} hollow files")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Hollow File Gate — T25 Pre-Commit Hook")
    parser.add_argument("--init", action="store_true", help="Initialize baseline from current state")
    parser.add_argument("--report", action="store_true", help="Generate full repository report")
    parser.add_argument("--changed-only", action="store_true", help="Check only changed files")
    parser.add_argument("--base", default="HEAD~1", help="Base ref for determining changed files")
    parser.add_argument("--baseline-path", default="ops_scripts/ci/hollow_file_baseline.json",
                       help="Path to baseline file")
    parser.add_argument(
        "--json-output",
        metavar="PATH",
        help="Write structured issues to JSON lines file",
    )

    args = parser.parse_args()

    baseline_path = project_root / args.baseline_path
    baseline = load_baseline(baseline_path)

    # Add project root for schema imports (for JSON output)
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from ops_scripts.ci.pre_commit_issue_schema import PreCommitIssue, SeverityLevel

    # Initialize scanner
    scanner = AntiPatternScanner(project_root, enforcement_level=EnforcementLevel.HARD_BLOCK)

    # Handle initialization
    if args.init:
        initialize_baseline(scanner, baseline_path)
        return 0

    # Handle full report
    if args.report:
        print("[hollow-file-gate] Generating full repository report...")
        report = scanner.scan_repository()

        hollow_violations = [v for v in report.all_violations if v.category == AntiPatternCategory.HOLLOW_FILE]

        print("\nHollow File Report")
        print("==================")
        print(f"Total hollow files: {len(hollow_violations)}")

        for violation in hollow_violations:
            classification = violation.metadata.get("classification", "unknown")
            print(f"  {violation.file_path.relative_to(project_root)} [{classification}]")

        # Save report
        report_path = project_root / "artifacts" / "adg" / "hollow_file_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w') as f:
            json.dump([v.to_dict() for v in hollow_violations], f, indent=2)

        print(f"\nReport saved to: {report_path}")
        return 0

    # Determine files to check
    if args.changed_only:
        files_to_check = get_changed_files(args.base)
        print(f"[hollow-file-gate] Checking {len(files_to_check)} changed Python files...")
    else:
        # Check all files
        files_to_check = []
        for scan_dir in scanner.get_default_scan_dirs():
            scan_path = project_root / scan_dir
            if scan_path.exists():
                files_to_check.extend(scan_path.rglob("*.py"))

        print(f"[hollow-file-gate] Checking {len(files_to_check)} Python files...")

    # Track violations
    violations = []
    new_hollow_files = []
    became_hollow_files = []

    for file_path in files_to_check:
        if not file_path.exists():
            continue

        # Skip certain file patterns
        if any(pattern in str(file_path) for pattern in [
            "__pycache__",
            ".git",
            "test_",
            "_test.py",
            "conftest.py",
        ]):
            continue

        result = scan_file(file_path)

        if result["violations"]:
            violation = result["violations"][0]
            rel_path = str(file_path.relative_to(project_root))

            # Check if file is new
            is_new = is_new_file(file_path, args.base)

            if is_new:
                new_hollow_files.append((file_path, violation))
            else:
                # Check if file was previously healthy
                prev_status = baseline.get("files", {}).get(rel_path, {}).get("classification", "healthy")
                if prev_status == "healthy":
                    became_hollow_files.append((file_path, violation))

            violations.append((file_path, violation))

    # Build structured issues for JSON output
    json_issues = []
    for file_path, violation in violations:
        rel_path = str(file_path.relative_to(project_root))
        is_new = (file_path, violation) in new_hollow_files
        is_became_hollow = (file_path, violation) in became_hollow_files

        # Determine severity based on status
        if is_new or is_became_hollow:
            sev = SeverityLevel.HIGH
        else:
            sev = SeverityLevel.MEDIUM

        issue = PreCommitIssue(
            hook_id="hollow-file-gate",
            hook_name="Hollow File Detection",
            severity=sev,
            file_path=rel_path,
            message=f"Hollow file: {violation.get('metadata', {}).get('classification', 'unknown')}",
            explanation="Files should contain meaningful behavioral logic. Empty or placeholder files increase maintenance burden.",
            issue_type="hollow_file",
        )
        json_issues.append(issue)

    # Write JSON output if requested
    if args.json_output and json_issues:
        output_path = Path(args.json_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for issue in json_issues:
                f.write(issue.to_json() + "\n")

    # Report results
    if violations:
        print(f"\n[hollow-file-gate] FAIL: Found {len(violations)} hollow file violations:")

        for file_path, violation in violations:
            rel_path = str(file_path.relative_to(project_root))
            classification = violation.get("metadata", {}).get("classification", "unknown")
            severity = violation.get("severity", "warning")

            if (file_path, violation) in new_hollow_files:
                status = "NEW"
                icon = "[BLOCK]"
            elif (file_path, violation) in became_hollow_files:
                status = "BECAME_HOLLOW"
                icon = "[WARN]"
            else:
                status = "EXISTING"
                icon = "[INFO]"

            print(f"  {icon} {rel_path} [{classification}] {severity} ({status})")
            print(f"     {violation.get('message', 'No message')}")

        # Block new hollow files and files that became hollow
        blocking_files = new_hollow_files + became_hollow_files

        if blocking_files:
            print(f"\n[hollow-file-gate] BLOCKING {len(blocking_files)} files:")
            for file_path, _ in blocking_files:
                rel_path = str(file_path.relative_to(project_root))
                print(f"  - {rel_path}")

            print("\n[hollow-file-gate] SUGGESTIONS:")
            print("  - For NEW files: Add behavioral logic or delete the file")
            print("  - For BECAME_HOLLOW files: Restore behavioral content or delete")
            print("  - Run with --report to see full repository state")

            return 1
        else:
            print("\n[hollow-file-gate] WARNING: Existing hollow files detected (not blocking)")
            print("  Run with --init to set baseline, or --report for full inventory")
            return 0
    else:
        print("[hollow-file-gate] OK: No hollow file violations found")
        return 0


if __name__ == "__main__":
    sys.exit(main())
