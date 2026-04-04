#!/usr/bin/env python3
"""
Windsurf CI Hook - Runs CI validation on relevant changes
Integrates with Windsurf's native hook system.
"""

import os
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

def main():
    """Run Windsurf CI for plan changes."""

    # Check if any plan files changed
    # For now, run CI always (can be optimized later)

    print("Running Windsurf CI for Plans...")

    # Import and run CI
    from tools.windsurf_ci import check_windsurfrules_compliance, run_windsurf_ci

    # Run CI validation
    ci_passed = run_windsurf_ci()

    # Check rules compliance
    rules_compliant = check_windsurfrules_compliance()

    if ci_passed and rules_compliant:
        print("Windsurf CI passed")
        return 0
    else:
        print("Windsurf CI failed")
        print("Fix issues before committing")
        return 1

if __name__ == "__main__":
    sys.exit(main())
