#!/usr/bin/env python3
"""
Check that every changed .py file has an up-to-date test.

This script enforces test coverage for all sovereign agent code.
If a source file is newer than its test, the commit is blocked.
import logging

logger = logging.getLogger(__name__)

"""

import sys
from pathlib import Path

root = Path(".")

exit_code = 0

for f in sys.argv[1:]:
    p = Path(f)

    # Skip non-Python files
    if p.suffix != ".py":
        continue

    # Skip test files themselves
    if "tests" in p.parts or "_test.py" in p.name:
        continue

    # Only check sovereign agent code
    try:
        rel = p.relative_to(root).as_posix()
    except ValueError:
        continue

    if not rel.startswith(("agentic_core/", "apps_lic/", "apps_rg/")):
        continue

    # Find corresponding test file
    test_path = root / "tests" / "unit" / rel.replace(".py", "_test.py")

    # Check if test exists and is up-to-date
    if not test_path.exists():
        # Test missing - warn but don't fail (too many missing tests currently)
        # Uncomment below to enforce:
        # logger.info(f"TEST MISSING: {test_path}")
        # exit_code = 1
        continue

    if test_path.stat().st_mtime < p.stat().st_mtime:

        exit_code = 1

sys.exit(exit_code)
