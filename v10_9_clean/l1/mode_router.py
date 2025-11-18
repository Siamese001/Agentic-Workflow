# FILE: v10_9_clean/l1/mode_router.py
"""
L1 — Mode Router (v10_9)

Determines which high-level mode the system should run in
(strategy, rag, bullets, drafting, qa, safety)
based on orchestrator state and user intent.

This is the L1-level router that existed implicitly in 10_7 and 10_8
and is required in a clean 10_9 L1–L5 architecture.
"""

from __future__ import annotations
from typing import Any, Dict


def route_mode(state: Dict[str, Any]) -> str:
    """
    Determine which plan mode should be invoked.

    Priority order:
        1. explicit state['mode']
        2. explicit state['task_mode']
        3. recognized patterns in 'objective'
        4. fallback = 'strategy'
    """

    if "mode" in state and state["mode"]:
        return str(state["mode"]).lower()

    if "task_mode" in state and state["task_mode"]:
        return str(state["task_mode"]).lower()

    objective = str(state.get("objective") or "").lower()

    if any(k in objective for k in ("retrieve", "search", "evidence", "cite")):
        return "rag"

    if any(k in objective for k in ("bullet", "bullets")):
        return "bullets"

    if any(k in objective for k in ("draft", "narrative", "rewrite", "writing")):
        return "drafting"

    if any(k in objective for k in ("qa", "validate", "quality", "check")):
        return "qa"

    if any(k in objective for k in ("safety", "sanitize", "redact")):
        return "safety"

    return "strategy"
