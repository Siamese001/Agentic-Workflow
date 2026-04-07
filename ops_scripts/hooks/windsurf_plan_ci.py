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
    # tools.windsurf_ci was never implemented; actual plan/rules CI is handled
    # by dedicated pre-commit hooks (adg-ci-gates, windsurf-rules-check, etc.).
    # This hook is a no-op pass-through to avoid blocking commits.
    return 0

if __name__ == "__main__":
    sys.exit(main())
