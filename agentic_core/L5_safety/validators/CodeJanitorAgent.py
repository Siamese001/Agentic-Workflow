"""
validators/CodeJanitorAgent.py — backward-compat re-export shim.

Canonical implementation has moved to:
    agentic_core.L5_safety.reasoning.CodeJanitorAgent

This file is a pure re-export stub with NO mutation logic of its own.
All filesystem writes (_write_file_content, _smart_fix, heal_repository) are in
reasoning/CodeJanitorAgent.py (L5 healer territory).

ADG fix: A-04 (CodeJanitorAgent split — healer logic moved to reasoning/).
"""

from __future__ import annotations

from agentic_core.L5_safety.reasoning.CodeJanitorAgent import (
    CodeJanitorAgent,
    JanitorViolation,
)

__all__ = ["CodeJanitorAgent", "JanitorViolation"]
