#!/usr/bin/env python3
"""
Diagnose Syntax Errors - Quick syntax validation for all Python files.

Usage:
    python scripts/diagnose_syntax.py
"""
from __future__ import annotations

import ast
from pathlib import Path


def check_syntax(root: Path) -> int:
    """Check all Python files for syntax errors.

    Returns:
        Number of files with syntax errors
    """
    errors = []

    for f in root.rglob("*.py"):
        # Skip common exclusions
        if any(x in f.parts for x in ['__pycache__', '.git', 'node_modules', '.venv', 'venv', 'archives']):
            continue

        try:
            content = f.read_text(encoding='utf-8')
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
    agentic_errors = check_syntax(root / "agentic_core")

    # Check scripts
    print("\nChecking scripts...")
    scripts_errors = check_syntax(root / "scripts")

    # Check tests
    print("\nChecking tests...")
    tests_errors = check_syntax(root / "tests")

    total = agentic_errors + scripts_errors + tests_errors
    print(f"\n{'='*60}")
    print(f"Total syntax errors: {total}")

    sys.exit(0 if total == 0 else 1)
