#!/usr/bin/env python3
"""
Diagnose why suppression tokens are not being respected.
Reads exact whitelist check logic from each validator.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "archives"}


def show_whitelist_logic(validator_filename: str) -> None:
    hits = [
        p for p in REPO.rglob(validator_filename)
        if not any(s in p.parts for s in SKIP_DIRS)
    ]
    if not hits:
        print(f"  {validator_filename}: NOT FOUND")
        return
    content = hits[0].read_text(encoding="utf-8")
    # Find WHITELIST_COMMENT assignment
    m_token = re.search(r'WHITELIST_COMMENT\s*=\s*["\']([^"\']+)["\']', content)
    token = m_token.group(1) if m_token else "NOT FOUND"
    # Find how it is checked (surrounding lines)
    lines = content.splitlines()
    check_lines = []
    for i, line in enumerate(lines):
        if "WHITELIST_COMMENT" in line or "whitelist" in line.lower() or "guardian" in line.lower():
            check_lines.append(f"    {i+1}: {line.rstrip()}")
    print(f"\n  {validator_filename}")
    print(f"    token = {token!r}")
    print("    usage lines:")
    for cl in check_lines[:15]:
        print(cl)


def show_current_line(filepath: str, lineno: int) -> None:
    """Show the actual line content after suppression was applied."""
    hits = [
        p for p in REPO.rglob(filepath)
        if not any(s in p.parts for s in SKIP_DIRS)
    ]
    if not hits:
        print(f"  {filepath}: NOT FOUND")
        return
    lines = hits[0].read_text(encoding="utf-8").splitlines()
    idx = lineno - 1
    if 0 <= idx < len(lines):
        print(f"  {filepath}:{lineno}  →  {lines[idx]!r}")





if __name__ == "__main__":
    print("=== Whitelist logic per validator ===")
    for v in [
        "global_mutation_validator.py",
        "magic_validator.py",
        "path_fragility_validator.py",
        "type_erasure_validator.py",
        "config_with_logic_validator.py",
    ]:
        show_whitelist_logic(v)

    print("\n=== Sample suppressed lines (checking token was written) ===")
    samples = [
        ("_debug_mixed_list.py", 5),
        ("_search_fixable.py", 7),
        ("find_hangs.py", 28),
        ("SovereignLLMGateway.py", 83),
        ("ast_gap_report.py", 104),
    ]
    for fname, lineno in samples:
        show_current_line(fname, lineno)
