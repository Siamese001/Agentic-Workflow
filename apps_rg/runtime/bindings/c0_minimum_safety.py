"""apps_rg C0 minimum safety enforcement.

W3: Defines the minimum passing support statuses for apps_rg C0 retrieval.
PARTIAL is explicitly excluded — it must be coerced to UNKNOWN before reaching
this gate.

Plan: apps-rg-retrieval-metrics-ownership-and-c0-evidence-plan W3
"""
from __future__ import annotations

# Canonical passing support statuses for apps_rg C0 gate.
# PARTIAL must NOT appear here — it is not a canonical output status.
_PASSING_SUPPORT_STATUSES: frozenset[str] = frozenset({
    "PASS",
    "WEAK_WITH_CAVEATS",
})


def is_c0_minimum_safe(support_status: str) -> bool:
    """Return True if support_status meets the C0 minimum safety bar.

    PARTIAL is never considered safe — callers must coerce it to UNKNOWN
    before invoking this function.

    Parameters
    ----------
    support_status:
        The (already-coerced) support status string from the c0_metrics artifact.

    Returns
    -------
    bool
    """
    return support_status in _PASSING_SUPPORT_STATUSES


__all__ = [
    "_PASSING_SUPPORT_STATUSES",
    "is_c0_minimum_safe",
]
