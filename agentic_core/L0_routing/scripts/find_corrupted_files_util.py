#!/usr/bin/env python3
"""
Find and Fix Corrupted Python Files - Detects and repairs literal \\n corruption.

This script scans for files where literal backslash-n sequences appear at the
end of files (typically caused by bad copy-paste or repr() output being written
to source files), and optionally fixes them.

Usage:
    python scripts/find_corrupted_files_util.py          # Scan only
    python scripts/find_corrupted_files_util.py --fix    # Scan and fix
"""

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
)
from agentic_core.L0_routing.enforcement.mutation_prohibition import (
    safe_write_text,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "find_corrupted_files_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "find_corrupted_files_util", "p0_governance")
_emit_snapshots_state("p0", "find_corrupted_files_util", "state_snapshot")


def find_corruption(content: str) -> int:
    """Find position of literal backslash-n corruption. Returns -1 if none."""
    # Look for literal backslash followed by 'n' (two chars)
    return content.find(chr(92) + "n")


def is_valid_python(content: str) -> bool:
    """Check if content is valid Python syntax."""
    try:
        ast.parse(content)
        return True
    except SyntaxError:
        return False


def main():
    fix_mode = "--fix" in sys.argv

    # Scan multiple directories
    scan_dirs = [
        AGENTIC_CORE_DIR,
        APPS_RG_DIR,
        APPS_LIC_DIR,
        APPS_SHARED_DIR,
        SCRIPTS_DIR,
        TESTS_DIR,
    ]

    corrupted_files = []
    fixed_files = []

    for root_dir in scan_dirs:
        root_path = Path(root_dir)
        if not root_path.exists():
            continue

        # Phase 6.9: Use ssot_discovery instead of rglob
        from agentic_core.utils.ssot_discovery_validator import get_python_files

        py_files = list(get_python_files(root_path))

        for py_file in py_files:
            if "__pycache__" in str(py_file) or ARCHIVES_DIR in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")

                # Check for literal backslash-n
                idx = find_corruption(content)
                if idx != -1:
                    # Verify it's actually corruption (file doesn't parse)
                    if not is_valid_python(content):
                        corrupted_files.append((py_file, idx))

                        if fix_mode:
                            # Truncate at corruption point
                            clean = content[:idx].rstrip() + "\n"
                            if is_valid_python(clean):
                                safe_write_text(py_file, clean, layer="L0", encoding="utf-8")
                                fixed_files.append(py_file)
                                print(f"FIXED: {py_file}")
                            else:
                                print(f"UNFIXABLE: {py_file} (truncation doesn't fix syntax)")
                        else:
                            print(f"CORRUPTED: {py_file}")
            # guardian: allow-silent-swallow
            except Exception as e:
                print(f"ERROR: {py_file} - {e}")

    print("\n" + "=" * 60)
    print(f"SUMMARY: {len(corrupted_files)} corrupted file(s) found")

    if fix_mode:
        print(f"         {len(fixed_files)} file(s) fixed")
        unfixed = len(corrupted_files) - len(fixed_files)
        if unfixed > 0:
            print(f"         {unfixed} file(s) could not be auto-fixed")
    else:
        if corrupted_files:
            print("\nRun with --fix to automatically repair these files:")
            print("  python scripts/find_corrupted_files_util.py --fix")

    return 0 if not corrupted_files or (fix_mode and len(fixed_files) == len(corrupted_files)) else 1


if __name__ == "__main__":
    sys.exit(main())
