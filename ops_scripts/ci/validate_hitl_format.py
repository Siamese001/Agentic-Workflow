#!/usr/bin/env python3
"""
HITL Format Compliance Validator

Validates that HITL (Human-In-The-Loop) decision points in plan files
include the required ⭐ star marker for recommendations and Pros/Cons
for options, as specified in .windsurf/rules/hitl-enforcement.md.

Usage:
    python ops_scripts/ci/validate_hitl_format.py --path .windsurf/plans
    python ops_scripts/ci/validate_hitl_format.py --path docs/reports/plans
    python ops_scripts/ci/validate_hitl_format.py --all
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple


def validate_file(file_path: Path) -> List[Tuple[int, str, str]]:
    """
    Validate a single markdown file for HITL format compliance.

    Returns:
        List of (line_number, issue_type, message) tuples for violations
    """
    violations = []
    content = file_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    # Patterns to detect
    option_pattern = re.compile(r"^\*\*Option [A-D]:.*\(Recommended\)")
    option_with_star_pattern = re.compile(r"^\*\*Option [A-D]:.*\(⭐ RECOMMENDED\)")
    recommended_text_pattern = re.compile(r"Recommendation:(?!.*⭐)")
    pros_pattern = re.compile(r"^\*\*Pros\*\*:")
    cons_pattern = re.compile(r"^\*\*Cons\*\*:")

    has_options = False
    has_pros = False
    has_cons = False

    for i, line in enumerate(lines, start=1):
        # Check for option declarations
        if option_pattern.match(line):
            has_options = True
            if not option_with_star_pattern.match(line):
                violations.append(
                    (
                        i,
                        "MISSING_STAR",
                        f'Option declaration has "(Recommended)" but missing ⭐ marker: {line.strip()}',
                    )
                )

        # Check for "Recommendation:" text without ⭐
        if recommended_text_pattern.search(line) and "⭐" not in line:
            violations.append(
                (
                    i,
                    "MISSING_STAR",
                    f'"Recommendation:" text found without ⭐ marker: {line.strip()}',
                )
            )

        # Check for Pros/Cons
        if pros_pattern.match(line):
            has_pros = True
        if cons_pattern.match(line):
            has_cons = True

    # If options exist but no Pros/Cons, flag it
    if has_options and not (has_pros and has_cons):
        violations.append(
            (
                0,
                "MISSING_PROS_CONS",
                "File has option declarations but missing **Pros** or **Cons** sections",
            )
        )

    return violations


def main():
    parser = argparse.ArgumentParser(description="Validate HITL format compliance")
    parser.add_argument("--path", type=str, help="Path to scan (file or directory)")
    parser.add_argument("--all", action="store_true", help="Scan both .windsurf/plans and docs/reports/plans")
    args = parser.parse_args()

    paths_to_scan = []
    if args.all:
        paths_to_scan.extend(
            [
                Path(".windsurf/plans"),
                Path("docs/reports/plans"),
            ]
        )
    elif args.path:
        paths_to_scan.append(Path(args.path))
    else:
        parser.error("Must specify --path or --all")

    all_violations = []
    files_scanned = 0

    for path in paths_to_scan:
        if path.is_file() and path.suffix == ".md":
            files = [path]
        elif path.is_dir():
            files = list(path.glob("*.md"))
        else:
            print(f"Warning: {path} is not a valid file or directory", file=sys.stderr)
            continue

        for file_path in files:
            files_scanned += 1
            violations = validate_file(file_path)
            if violations:
                all_violations.append((file_path, violations))

    # Report results
    print("\nHITL Format Validation Report")
    print("=" * 50)
    print(f"Files scanned: {files_scanned}")
    print(f"Files with violations: {len(all_violations)}")
    print(f"Total violations: {sum(len(v) for _, v in all_violations)}")

    if all_violations:
        print("\n" + "=" * 50)
        print("VIOLATIONS:")
        print("=" * 50)
        for file_path, violations in all_violations:
            print(f"\n{file_path}:")
            for line_num, issue_type, message in violations:
                if line_num > 0:
                    print(f"  Line {line_num} [{issue_type}]: {message}")
                else:
                    print(f"  [{issue_type}]: {message}")
        print("\n" + "=" * 50)
        print("FAILED: HITL format violations found")
        print("=" * 50)
        sys.exit(1)
    else:
        print("\n" + "=" * 50)
        print("PASSED: All HITL decisions comply with format requirements")
        print("=" * 50)
        sys.exit(0)


if __name__ == "__main__":
    main()
