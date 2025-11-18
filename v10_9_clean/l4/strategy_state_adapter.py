# FILE: v10_9_clean/l4/strategy_state_adapter.py
"""
L4 — Strategy State Adapter (v10_9)

Integrates L2 strategy reasoning results into orchestration state.

This adapter:
    • performs NO planning
    • performs NO execution
    • simply inserts structured strategy results into the L4 state tree

Expected L2 payload from execute_strategy():
    {
        "objective": ...,
        "constraints": [...],
        "dependencies": [...],
        "deliverables": [...],
        "outline": [...],
        "next_actions": [...]
    }
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List


def attach_strategy_result(
    state: Dict[str, Any],
    strategy_payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Writes strategy_results into:
        state["strategy"]
        state["strategy_history"]
    """

    new_state = copy.deepcopy(state) if isinstance(state, dict) else {}

    outline = strategy_payload.get("outline") or []
    next_actions = strategy_payload.get("next_actions") or []

    # Maintain cumulative strategy history
    history = new_state.get("strategy_history")
    if not isinstance(history, list):
        history = []
    history.append(strategy_payload)
    new_state["strategy_history"] = history

    # Current strategy bucket
    new_state["strategy"] = {
        "objective": strategy_payload.get("objective"),
        "constraints": strategy_payload.get("constraints", []),
        "dependencies": strategy_payload.get("dependencies", []),
        "deliverables": strategy_payload.get("deliverables", []),
        "outline": outline,
        "next_actions": next_actions,
    }

    return new_state
