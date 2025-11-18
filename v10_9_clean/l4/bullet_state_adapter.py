# FILE: v10_9_clean/l4/bullet_state_adapter.py
"""
L4 — Bullet State Adapter (v10_9)

Integrates bullet-generation results into orchestration state.
Pure deterministic transformation — no execution or planning logic.

Expected payload shape from L2:
    {
        "bullets": [...],
        "target_sections": [...],
        "guidelines": [...],
        "validation_checks": [...]
    }
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List


def attach_bullet_result(
    state: Dict[str, Any],
    bullet_payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Insert bullet-generation artifacts into state under:
        state["bullets"]
        state["bullet_history"]

    Behavior:
        • deep-copy state
        • append to bullet_history
        • write current bullets to state["bullets"]
    """

    new_state = copy.deepcopy(state) if isinstance(state, dict) else {}

    bullets: List[str] = bullet_payload.get("bullets") or []

    # Maintain cumulative history
    history = new_state.get("bullet_history")
    if not isinstance(history, list):
        history = []
    history.append(bullets)
    new_state["bullet_history"] = history

    # Current bullet bucket
    new_state["bullets"] = {
        "items": bullets,
        "target_sections": bullet_payload.get("target_sections", []),
        "guidelines": bullet_payload.get("guidelines", []),
        "validation_checks": bullet_payload.get("validation_checks", []),
    }

    return new_state
