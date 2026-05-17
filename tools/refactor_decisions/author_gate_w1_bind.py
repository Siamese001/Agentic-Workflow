"""W1 outcome bind tier for Author-Gate capture (plan author-gate-feedback-loop-d4e8f1).

Pure helpers — no I/O. Advisory tiers only; never used as proceed/merge authority.
"""

from __future__ import annotations


def merge_precedent_verdict(
    marker_verdict: object | None,
    lookup_verdict: object | None,
    sidecar_verdict: object | None,
) -> str | None:
    """First non-empty among marker, FTS lookup, sidecar (canonical lower verdict)."""
    for v in (marker_verdict, lookup_verdict, sidecar_verdict):
        if v is None:
            continue
        s = str(v).strip().lower()
        if s in ("strong", "suggestive", "none"):
            return s
    return None


def outcome_bind_tier(
    *,
    precedent_verdict: str | None,
    override_vs_recommendation: int | None,
    reason_code: str | None,
    degraded_scope: bool,
    tests_passed: int,
    regression_found: int,
    rollback_required: int,
) -> str:
    """Return strong_bind | weak_bind | disputed_bind | no_bind | unknown_bind."""
    if rollback_required or regression_found:
        return "disputed_bind"
    if override_vs_recommendation == 1:
        return "disputed_bind"
    if reason_code == "override_recommendation":
        return "disputed_bind"

    pv = precedent_verdict
    if degraded_scope and pv == "strong":
        tier = "weak_bind"
    elif pv == "strong":
        tier = "strong_bind"
    elif pv == "suggestive":
        tier = "weak_bind"
    elif pv == "none":
        tier = "no_bind"
    else:
        tier = "unknown_bind"

    if tier == "strong_bind" and tests_passed == 0:
        tier = "weak_bind"
    return tier
