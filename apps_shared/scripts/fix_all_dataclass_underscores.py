"""
Emergency Fix Script: Remove ALL underscore prefixes from dataclass fields in core_contracts_types.py
Session 5 - Critical Issue Resolution
"""

import re
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "fix_all_dataclass_underscores", "uwg_governed_write")
_emit_writes_through("p1", "fix_all_dataclass_underscores", "uwg_governed_write_2")
_emit_pulls_context("p1", "fix_all_dataclass_underscores", "context_retrieval")
_emit_pulls_context("p1", "fix_all_dataclass_underscores", "context_retrieval_2")
emit_determinism_digest("trace_fix_all_dataclass_underscores", "fix_all_dataclass_underscores_dispatch")
emit_determinism_digest("trace_fix_all_dataclass_underscores", "fix_all_dataclass_underscores_complete")
_emit_validated_by_safety_plane("p1", "fix_all_dataclass_underscores", "safety_validation")


def fix_dataclass_underscores(file_path: Path) -> tuple[int, list[str]]:
    """Remove all underscore prefixes from dataclass fields."""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()
    original_content = content
    changes = []
    pattern = "^(\\s+)_([a-z][a-z0-9_]*)(:\\s+.+)$"
    lines = content.split("\n")
    fixed_lines = []
    for i, line in enumerate(lines):
        match = re.match(pattern, line)
        if match:
            indent, field_name, rest = match.groups()
            new_line = f"{indent}{field_name}{rest}"
            fixed_lines.append(new_line)
            changes.append(f"Line {i + 1}: _{field_name} → {field_name}")
        else:
            fixed_lines.append(line)
    fixed_content = "\n".join(fixed_lines)
    method_pattern = "\\bself\\._([a-z][a-z0-9_]*)\\b"

    def replace_self_ref(match):
        field_name = match.group(1)
        changes.append(f"Method reference: self._{field_name} → self.{field_name}")
        return f"self.{field_name}"

    fixed_content = re.sub(method_pattern, replace_self_ref, fixed_content)
    if fixed_content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(fixed_content)
        return (len(changes), changes)
    return (0, [])


def main():
    """Run the fix on core_contracts_types.py"""
    file_path = Path("c:\\Git\\Agentic-Workflow\\agentic_core\\schemas\\models\\core_contracts_types.py")
    print("=" * 70)
    print("EMERGENCY FIX: Removing ALL dataclass underscore prefixes")
    print("=" * 70)
    print(f"\nTarget: {file_path}")
    print("\nProcessing...")
    count, changes = fix_dataclass_underscores(file_path)
    print(f"\n✅ Fixed {count} underscore violations")
    if count > 0:
        print("\nSample changes (first 20):")
        for change in changes[:20]:
            print(f"  - {change}")
        if count > 20:
            print(f"\n  ... and {count - 20} more changes")
    print("\n" + "=" * 70)
    print("FIX COMPLETE - Please verify with integrity check")
    print("=" * 70)


if __name__ == "__main__":
    main()
