#!/usr/bin/env python3
"""
Pre-commit hook to validate Windsurf plan format.
Enforces compliance with plan structure requirements.
"""

import os
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

from tools.validate_plan_format import validate_plan_format


def main():
    """Validate all plan files being committed."""

    # Get list of files being committed
    # For now, we'll validate all .md files in plans directories
    plan_files = []

    # Check workspace plans
    workspace_plans = Path.home() / ".windsurf" / "plans"
    if workspace_plans.exists():
        plan_files.extend(list(workspace_plans.glob("*.md")))

    # Check repo plans
    repo_plans = Path(repo_root) / "docs/reports/plans"
    if repo_plans.exists():
        plan_files.extend(list(repo_plans.glob("*.md")))

    if not plan_files:
        print("No plan files found to validate")
        return 0

    print("=== Windsurf Plan Format Validation ===")
    print()

    all_valid = True

    for plan_file in plan_files:
        if plan_file.name == "README.md":
            continue  # Skip README files

        print(f"Validating: {plan_file}")
        result = validate_plan_format(str(plan_file))

        if result['valid']:
            print("✅ Valid")
        else:
            print("❌ Invalid")
            all_valid = False
            for issue in result['issues']:
                print(f"  - {issue}")

        if result['warnings']:
            for warning in result['warnings']:
                print(f"  ⚠️  {warning}")
        print()

    if all_valid:
        print("✅ All plans are valid!")
        return 0
    else:
        print("❌ Some plans failed validation!")
        print("Fix the issues above before committing.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
