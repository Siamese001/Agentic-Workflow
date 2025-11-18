# FILE: v10_9_clean/l4/qa_state_adapter.py
"""
L4 — QA State Adapter (v10_9)

Integrates QA execution results into orchestration state.

This layer:
    • performs NO planning
    • performs NO QA execution
    • ONLY inserts qa_report into state in a stable, deterministic format

Expected L2 payload (qa_execution):
    {
        "qa_report": {
            "issues": [...],
            "confidence": float,
            "passed": bool
        }
    }
"""

from __future__ import annotations

import copy
from typing import Any, Dict


def attach_qa_result(
    state: Dict[str, Any],
    qa_payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Writes QA results into state under:
        state["qa"]
        state["qa_history"]
    """

    new_state = copy.deepcopy(state) if isinstance(state, dict) else {}

    qa_report = qa_payload.get("qa_report") or {}

    # Maintain cumulative history
    history = new_state.get("qa_history")
    if not isinstance(history, list):
        history = []
    history.append(qa_report)
    new_state["qa_history"] = history

    # Current QA bucket
    new_state["qa"] = {
        "report": qa_report,
        "issues": qa_report.get("issues", []),
        "confidence": qa_report.get("confidence", 0.0),
        "passed": qa_report.get("passed", False),
    }

    return new_state
