#!/usr/bin/env python3
"""
Resolve rebase conflicts by accepting both sides:
- Keep all guardian suppression lines from OURS
- Keep all content from THEIRS
Strategy: strip conflict markers, merge both sides.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKIP = {".git", ".venv", "venv", "__pycache__", ".pytest_cache"}

CONFLICT_FILES = [
    "agentic_core/L0_routing/scripts/execute_ssot.py",
    "agentic_core/L5_safety/validators/dependencygraph_validator.py",
    "ops_scripts/ci/_debug_mixed_list.py",
    "ops_scripts/ci/_debug_visitor.py",
    "ops_scripts/ci/_find_truly_fixable.py",
    "ops_scripts/ci/_search_fixable.py",
    "ops_scripts/ci/_test_fixer.py",
    "ops_scripts/general/find_hangs.py",
    "ops_scripts/general/quick_hang_finder.py",
    "ops_scripts/hooks/landmine_baseline.txt",
]








if __name__ == "__main__":
    main()
