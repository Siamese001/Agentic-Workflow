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
