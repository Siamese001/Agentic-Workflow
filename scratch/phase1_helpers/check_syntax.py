#!/usr/bin/env python3
"""Check syntax of all Python files in scan roots."""

import ast
import sys
from pathlib import Path


def main():
    roots = ["agentic_core", "apps_lic", "apps_rg", "apps_shared"]
    errors = []

    for root in roots:
        root_path = Path(root)
        if not root_path.exists():
            continue
        for f in root_path.rglob("*.py"):
            if "__pycache__" in str(f):
                continue
            if f.name.startswith("test_"):
                continue
            try:
                with open(f, encoding="utf-8") as fp:
                    ast.parse(fp.read())
            except SyntaxError as e:
                errors.append(f"{f}: {e}")

    if errors:
        print(f"Found {len(errors)} syntax errors:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("All files pass syntax check")
        sys.exit(0)


if __name__ == "__main__":
    main()
