# FILE: v10_9_clean/l4/safety_state_adapter.py
"""
L4 — Safety State Adapter (v10_9)

Integrates L2 safety results into the orchestration state.

Expected L2 payload:
    {
        "safety_report": {
            "issues": [...],
            "passed": bool,
            "sensitivity": str,
            "audience": str
        },
        "sanitized_content": str
    }

Writes into state:
    • state["safety"]
    • state["safety_history"]
"""

from __future__ import annotations

import copy
from typing import Any, Dict


def attach_safety_result(
    state: Dict[str, Any],
    safety_payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Insert safety results into state in a canonical, deterministic structure.
    """

    new_state = copy.deepcopy(state) if isinstance(state, dict) else {}

    report = safety_payload.get("safety_report") or {}
    sanitized = safety_payload.get("sanitized_content", "")

    # History bucket
    history = new_state.get("safety_history")
    if not isinstance(history, list):
        history = []
    history.append(report)
    new_state["safety_history"] = history

    # Current safety bucket
    new_state["safety"] = {
        "report": report,
        "issues": report.get("issues", []),
        "passed": report.get("passed", False),
        "audience": report.get("audience", ""),
        "sensitivity": report.get("sensitivity", ""),
        "sanitized_content": sanitized,
    }

    return new_state
