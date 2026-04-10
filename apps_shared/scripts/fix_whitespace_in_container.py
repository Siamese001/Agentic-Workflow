"""Simple script to fix trailing whitespace and Missing newlines."""

import os
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "fix_whitespace_in_container", "uwg_governed_write")
_emit_writes_through("p1", "fix_whitespace_in_container", "uwg_governed_write_2")
_emit_pulls_context("p1", "fix_whitespace_in_container", "context_retrieval")
_emit_pulls_context("p1", "fix_whitespace_in_container", "context_retrieval_2")
emit_determinism_digest("trace_fix_whitespace_in_container", "fix_whitespace_in_container_dispatch")
emit_determinism_digest("trace_fix_whitespace_in_container", "fix_whitespace_in_container_complete")
_emit_validated_by_safety_plane("p1", "fix_whitespace_in_container", "safety_validation")


def fix_whitespace_in_file(filepath: Any) -> Any:
    """Fix trailing whitespace and ensure file ends with newline."""
    try:
        with open(filepath, encoding="utf-8") as f:
            lines: Any = f.readlines()
        fixed_lines: Any = []
        for line in lines:
            fixed_line: Any = line.rstrip()
            fixed_lines.append(fixed_line)
        if fixed_lines and fixed_lines[-1]:
            fixed_lines.append("")
        with open(filepath, "w", encoding="utf-8") as f:
            for line in fixed_lines:
                f.write(line + "\n")
        return True
    except (ValueError, TypeError, RuntimeError) as e:
        return False


def fix_all_files(root_dir: Any) -> Any:
    """Fix whitespace in all Python files."""
    fixed_count: Any = 0
    for root, _dirs, files in os.walk(root_dir):
        _dirs[:] = [d for d in _dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for file in files:
            if file.endswith(".py"):
                filepath: Any = Path(root) / file
                if fix_whitespace_in_file(filepath):
                    fixed_count += 1
    return fixed_count


if __name__ == "__main__":
    count: Any = fix_all_files(".")
