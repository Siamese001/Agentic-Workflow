"""Proof-boundary defaults for competencies (jd_alignment flags).

Centralizes safe defaults so parsed fallbacks, l2_output, aggregation, and L6 counters agree.
"""

from __future__ import annotations

from typing import Any

JD_ALIGNMENT_PROOF_BOUNDARY_DEFAULT: dict[str, Any] = {
    "targeting_only": True,
    "jd_used_as_proof": False,
    "briefing_used_as_proof": False,
    "companion_context_used_as_proof": False,
}


def merge_jd_alignment(raw: Any) -> dict[str, Any]:
    """Merge parsed jd_alignment with safe defaults for all four proof-boundary booleans."""
    out: dict[str, Any] = {}
    if isinstance(raw, dict):
        out.update(raw)
    for k, v in JD_ALIGNMENT_PROOF_BOUNDARY_DEFAULT.items():
        out.setdefault(k, v)
    return out


__all__ = [
    "JD_ALIGNMENT_PROOF_BOUNDARY_DEFAULT",
    "merge_jd_alignment",
]
