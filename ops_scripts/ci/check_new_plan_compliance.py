#!/usr/bin/env python3
"""
Check New Plan Compliance
Validates that new plans (created after 2026-01-01) follow current standards.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

from tools.validate_plan_format import validate_plan_format


def check_new_plan_compliance(plan_path: Path) -> bool:
    """Check if a new plan follows current standards."""

    # Skip if not a markdown file
    if plan_path.suffix != ".md":
        return True

    # Skip if not in plans directories
    try:
        rel_path = str(plan_path.relative_to(repo_root))
    except ValueError:
        # File is not in repo, skip
        return True

    if "plans" not in rel_path:
        return True

    # Skip README files
    if plan_path.name == "README.md":
        return True

    # Validate the plan
    result = validate_plan_format(str(plan_path))

    # Print results
    print(f"Checking: {rel_path}")

    if result.get("is_legacy", False):
        print("  ✅ Legacy plan - exempt")
        return True

    if result["valid"]:
        print("  ✅ Valid")
        if result["warnings"]:
            for warning in result["warnings"]:
                print(f"    ⚠️  {warning}")
        return True
    else:
        print("  ❌ Invalid")
        for issue in result["issues"]:
            print(f"    - {issue}")
        for warning in result["warnings"]:
            print(f"    ⚠️  {warning}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python check_new_plan_compliance.py <file1.md> [file2.md ...]")
        sys.exit(1)

    all_valid = True

    for file_arg in sys.argv[1:]:
        file_path = Path(file_arg)
        if not file_path.exists():
            print(f"File not found: {file_arg}")
            all_valid = False
            continue

        if not check_new_plan_compliance(file_path):
            all_valid = False

    if all_valid:
        print("\n✅ All plans compliant")
        sys.exit(0)
    else:
        print("\n❌ Some plans are not compliant")
        print("Use template: .windsurf/templates/execution-plan-template.md")
        sys.exit(1)


if __name__ == "__main__":
    main()
