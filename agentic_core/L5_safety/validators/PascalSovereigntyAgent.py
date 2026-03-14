"""
validators/PascalSovereigntyAgent.py — backward-compat re-export shim.

Canonical implementation has moved to:
    agentic_core.L5_safety.reasoning.PascalSovereigntyAgent

This file is a pure re-export stub with NO mutation logic of its own.
All filesystem mutations (rename, delete, import rewrite) are in
reasoning/PascalSovereigntyAgent.py (L5 healer territory).

ADG fix: A-02 (healer misplaced in validators/) + A-01 (validators/ mutation boundary).
"""

from __future__ import annotations

from agentic_core.L5_safety.reasoning.PascalSovereigntyAgent import (
    FileType,
    PascalSovereigntyAgent,
    get_python_files_fast,
    main,
)

__all__ = ["FileType", "PascalSovereigntyAgent", "get_python_files_fast", "main"]
