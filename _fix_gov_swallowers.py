#!/usr/bin/env python3
"""Bulk-fix GOVERNANCE_CRITICAL silent swallowers in ops_scripts."""
import ast
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
TARGETS = [
    "ops_scripts/ci",
    "ops_scripts/maintenance",
    "ops_scripts/root_scripts",
    "agentic_core/L5_safety/validators",
    "agentic_core/L5_safety/static_checks",
]

fixed_files = 0
fixed_violations = 0


def fix_file(f: Path) -> int:
    try:
        src = f.read_text(encoding="utf-8")
    except Exception:
        return 0

    lines = src.splitlines(keepends=True)
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return 0

    bad_lines = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for h in node.handlers:
                broad = h.type is None or (
                    isinstance(h.type, ast.Name) and h.type.id == "Exception"
                )
                if not broad:
                    continue
                has_raise = any(isinstance(n, ast.Raise) for n in ast.walk(h))
                if has_raise:
                    continue
                line_content = lines[h.lineno - 1] if h.lineno <= len(lines) else ""
                if "guardian: allow" in line_content:
                    continue
                bad_lines.add(h.lineno)

    if not bad_lines:
        return 0

    new_lines = list(lines)
    offset = 0  # accumulates insertions

    for lineno in sorted(bad_lines):
        idx = lineno - 1 + offset
        line = new_lines[idx]
        indent = len(line) - len(line.lstrip())
        body_indent = " " * (indent + 4)

        # Find next non-blank line after the except:
        next_idx = idx + 1
        while next_idx < len(new_lines) and new_lines[next_idx].strip() == "":
            next_idx += 1

        if next_idx < len(new_lines) and new_lines[next_idx].strip() == "pass":
            # Replace pass with raise
            new_lines[next_idx] = body_indent + "raise\n"
        else:
            # Insert raise before the first body statement
            new_lines.insert(next_idx, body_indent + "raise\n")
            offset += 1

    result = "".join(new_lines)
    if result != src:
        f.write_text(result, encoding="utf-8")
        return len(bad_lines)
    return 0


for target in TARGETS:
    target_path = PROJECT_ROOT / target
    if not target_path.exists():
        continue
    for f in sorted(target_path.rglob("*.py")):
        n = fix_file(f)
        if n:
            fixed_files += 1
            fixed_violations += n
            print(f"  fixed {n} violation(s) in {f.relative_to(PROJECT_ROOT)}")

print(f"\nTotal: fixed {fixed_violations} violations across {fixed_files} files")
