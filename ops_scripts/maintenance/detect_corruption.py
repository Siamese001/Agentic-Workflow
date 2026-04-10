#!/usr/bin/env python3
"""
Git Corruption Detection Script
Scans Python files for syntax errors and potential corruption patterns.
"""

import ast
import re
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)


def detect_corrupted_files(project_root: Path) -> list[tuple[Path, int, str]]:
    """
    Scan all Python files for syntax errors.

    Returns:
        List of (file_path, line_number, error_message) tuples
    """
    corrupted = []
    exclude_patterns = list(
        GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES,
    )

    for py_file in project_root.rglob("*.py"):
        # Skip excluded directories
        if any(pattern in str(py_file) for pattern in exclude_patterns):
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
            ast.parse(content)
        except SyntaxError as e:  # guardian: Syntax errors should be caught at parser level, not runtime
            corrupted.append((py_file, e.lineno or 0, str(e)))
        except UnicodeDecodeError as e:  # guardian: Encoding errors should specify fallback encoding strategy
            corrupted.append((py_file, 0, f"Encoding error: {e}"))
        except Exception as e:
            raise
            # Catch other parsing issues
            corrupted.append((py_file, 0, f"Parse error: {e}"))

    return corrupted


def detect_corruption_patterns(project_root: Path) -> list[tuple[Path, int, str]]:
    """
    Scan for common corruption patterns in Python files.

    Patterns:
    - Garbled class definitions (e.g., 'clasAtomicExecutionMixin')
    - Mangled function definitions
    - Corrupted import statements
    - Invalid characters in identifiers
    """
    suspicious = []
    exclude_patterns = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

    for py_file in project_root.rglob("*.py"):
        if any(pattern in str(py_file) for pattern in exclude_patterns):
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                for pattern_name, pattern in patterns.items():
                    if pattern.search(line):
                        suspicious.append(
                            (py_file, line_num, f"{pattern_name}: {line.strip()[:80]}"),
                        )
        except (
            OSError,
            UnicodeDecodeError,
        ):  # guardian: File operations with encoding need error-specific handling
            pass

    return suspicious


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent.parent

    print("=" * 80)
    print("GIT CORRUPTION DETECTION REPORT")
    print("=" * 80)

    # Check for syntax errors
    print("\n[PHASE 1] Scanning for syntax errors...")
    corrupted = detect_corrupted_files(project_root)

    if corrupted:
        print(f"\n❌ Found {len(corrupted)} files with syntax errors:\n")
        for path, line, error in corrupted:
            rel_path = path.relative_to(project_root)
            print(f"  {rel_path}:{line}")
            print(f"    Error: {error[:100]}")
    else:
        print("✅ No syntax errors found")

    # Check for corruption patterns
    print("\n[PHASE 2] Scanning for corruption patterns...")
    suspicious = detect_corruption_patterns(project_root)

    if suspicious:
        print(f"\n⚠️  Found {len(suspicious)} suspicious patterns:\n")
        for path, line, pattern in suspicious[:50]:  # Show first 50
            rel_path = path.relative_to(project_root)
            print(f"  {rel_path}:{line}")
            print(f"    {pattern}")
    else:
        print("✅ No corruption patterns detected")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Syntax errors: {len(corrupted)}")
    print(f"Suspicious patterns: {len(suspicious)}")

    if corrupted or suspicious:
        print("\n⚠️  CORRUPTION DETECTED - Manual review required")
        return 1
    else:
        print("\n✅ Repository integrity verified")
        return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
