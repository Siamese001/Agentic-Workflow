"""
State Validation Utilities

Provides lightweight validation of orchestration state with warnings for
cross-field inconsistencies.
"""
from __future__ import annotations

from typing import Any, Dict, List


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


def validate(state: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate the orchestration state for required keys and consistency."""

    missing: List[str] = []
    type_mismatch: List[str] = []
    cross_field_warnings: List[str] = []

    for field, expected_type in _EXPECTED_TYPES.items():
        if field not in state:
            missing.append(field)
            continue
        if not isinstance(state[field], expected_type):
            type_mismatch.append(field)

    if state.get("draft") is not None and len(state.get("messages", [])) == 0:
        cross_field_warnings.append("draft present but messages are empty")

    if state.get("qa_report") is not None and "plan" not in state:
        cross_field_warnings.append("qa_report present without plan")

    return {
        "missing": missing,
        "type_mismatch": type_mismatch,
        "cross_field_warnings": cross_field_warnings,
    }
