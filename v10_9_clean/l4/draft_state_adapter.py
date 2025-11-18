# FILE: v10_9_clean/l4/draft_state_adapter.py
"""
L4 — Draft State Adapter (v10_9)

Integrates L2 drafting results into orchestration state.

This layer:
    • performs NO planning
    • performs NO execution
    • ONLY transforms and inserts drafting outputs
      into the state dict for downstream L5 or UI use.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List


def attach_draft_result(
    state: Dict[str, Any],
    draft_payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Integrate a single drafting payload into orchestration state.

    Expected draft_payload:
        {
            "sections": [...],
            "tone": "...",
            "audience": "...",
            "hints": [...],
            "draft": [list of paragraphs]
        }

    Writes:
        state["draft"]
        state["draft_history"]
    """

    # Defensive deep-copy
    new_state = copy.deepcopy(state) if isinstance(state, dict) else {}

    sections: List[str] = draft_payload.get("sections") or []
    draft_content: List[str] = draft_payload.get("draft") or []
    tone: str = draft_payload.get("tone", "")
    audience: str = draft_payload.get("audience", "")
    hints: List[str] = draft_payload.get("hints") or []

    # Maintain cumulative history
    history = new_state.get("draft_history")
    if not isinstance(history, list):
        history = []
    history.append(draft_content)
    new_state["draft_history"] = history

    # Current draft bucket
    new_state["draft"] = {
        "sections": sections,
        "tone": tone,
        "audience": audience,
        "hints": hints,
        "content": draft_content,
    }

    return new_state
