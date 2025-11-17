# validation.py
"""
L4 — State Validation (v10_9)

Performs lightweight structural checks on orchestrator state.
"""

from __future__ import annotations

from typing import Dict, Any, List


_EXPECTED_TYPES = {
    "messages": list,
    "rag_history": list,
    "summary": str,
    "world": list,
    "session": dict,
    "metadata": dict,
    "phase": str,
    "phase_metadata": dict,
}


def validate_state(state: Dict[str, Any]) -> Dict[str, List[str]]:
    missing = []
    mismatch = []
    warnings = []

    for k, typ in _EXPECTED_TYPES.items():
        if k not in state:
            missing.append(k)
        elif not isinstance(state[k], typ):
            mismatch.append(k)

    # Example cross-field warning
    if state.get("draft") and not state.get("messages"):
        warnings.append("draft present but messages empty")

    return {
        "missing": missing,
        "type_mismatch": mismatch,
        "warnings": warnings,
    }
