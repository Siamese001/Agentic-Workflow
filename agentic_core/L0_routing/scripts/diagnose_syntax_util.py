#!/usr/bin/env python3
"""
Diagnose Syntax Errors - Quick syntax validation for all Python files.

Usage:
    python scripts/diagnose_syntax_util.py
"""

import ast
from pathlib import Path

from agentic_core.L0_routing.config import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    AGENTIC_CORE_DIR,
)
from agentic_core.L0_routing.config.path_constants import TESTS_DIR


def check_syntax(root: Path) -> int:
    """Check all Python files for syntax errors.

    Returns:
        Number of files with syntax errors
    """
    errors = []

    for f in root.rglob("*.py"):
        # Skip common exclusions
        if any(x in f.parts for x in ["__pycache__", ".git", "node_modules", ".venv", "venv", ARCHIVES_DIR]):
            continue

        try:
            content = f.read_text(encoding="utf-8")
            ast.parse(content)
        except SyntaxError as e:
            errors.append((str(f), e.lineno, e.msg))

    if errors:
        print(f"❌ Found {len(errors)} files with syntax errors:")
        for f, line, msg in errors:
            print(f"  {f}:{line} - {msg}")
        return len(errors)
    else:
        print("✅ All Python files have valid syntax!")
        return 0


if __name__ == "__main__":
    import sys

    root = Path(__file__).parent.parent

    # Check agentic_core
    print("Checking agentic_core...")
    agentic_errors = check_syntax(root / AGENTIC_CORE_DIR)

    # Check scripts
    print("\nChecking scripts...")
    scripts_errors = check_syntax(root / "scripts")

    # Check tests
    print("\nChecking tests...")
    tests_errors = check_syntax(root / TESTS_DIR)

    total = agentic_errors + scripts_errors + tests_errors
    print(f"\n{'=' * 60}")
    print(f"Total syntax errors: {total}")

    sys.exit(0 if total == 0 else 1)
