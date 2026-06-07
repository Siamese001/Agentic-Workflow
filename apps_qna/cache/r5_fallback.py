"""R5 Fallback Cache — degraded fallback, always marked.

W4.3: Degraded fallback cache used only when R1A and R1B are unavailable.
Always marked as degraded with reason codes.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-qna-spine-integration-e9c5b3.md W4.3
"""

from __future__ import annotations

from typing import Any


def r5_lookup(
    *,
    interview_slug: str,
    reason: str = "degraded_fallback",
) -> dict[str, Any]:
    """Degraded fallback cache lookup.

    Args:
        interview_slug: The interview slug.
        reason: Reason for degraded fallback.

    Returns:
        Degraded result dict, always marked as degraded.
    """
    return {
        "degraded": True,
        "interview_slug": interview_slug,
        "reason": reason,
        "result": None,
        "warning": "R5 is degraded fallback; results may be stale or incomplete.",
    }


__all__ = ["r5_lookup"]
