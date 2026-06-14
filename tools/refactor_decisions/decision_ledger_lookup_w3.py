"""W3 lookup reason taxonomy (plan author-gate-feedback-loop-d4e8f1).

Deterministic ``reason_codes`` for ``lookup_refactor_decisions``. Advisory only.
"""

from __future__ import annotations

from typing import Iterable

# Bump when taxonomy or classification changes; keep in sync with lookup tests.
LOOKUP_W3_POLICY_VERSION = "lookup-w3-reasons-20260517"

ALLOWED_REASON_CODES: frozenset[str] = frozenset(
    {
        "SELF_MATCH_EXCLUDED",
        "DUPLICATE_SCOPE_COLLAPSED",
        "COLD_CORPUS",
        "MATCHED_STRONG_BIND",
        "MATCHED_WEAK_BIND",
        "MATCHED_DISPUTED_BIND",
        "MATCHED_NO_BIND",
        "MATCHED_UNKNOWN_BIND",
        "DEGRADED_SCOPE_NOT_STRONG",
        "RECENCY_BOOST_APPLIED",
        "OUTCOME_TIER_BOOST_APPLIED",
        "BELOW_THRESHOLD",
        "POLICY_BLOCKED_STRONG",
    }
)

# Stable ordering for replay / stability tests (smaller = earlier in output).
REASON_CODE_ORDER: tuple[str, ...] = (
    "COLD_CORPUS",
    "BELOW_THRESHOLD",
    "SELF_MATCH_EXCLUDED",
    "DUPLICATE_SCOPE_COLLAPSED",
    "DEGRADED_SCOPE_NOT_STRONG",
    "POLICY_BLOCKED_STRONG",
    "MATCHED_DISPUTED_BIND",
    "MATCHED_NO_BIND",
    "MATCHED_UNKNOWN_BIND",
    "MATCHED_WEAK_BIND",
    "MATCHED_STRONG_BIND",
    "OUTCOME_TIER_BOOST_APPLIED",
    "RECENCY_BOOST_APPLIED",
)

_priority = {c: i for i, c in enumerate(REASON_CODE_ORDER)}


def sort_reason_codes(codes: Iterable[str]) -> list[str]:
    """Dedupe and sort deterministically."""
    uniq = sorted(set(codes))
    return sorted(uniq, key=lambda c: (_priority.get(c, 1000), c))


def validate_reason_codes(codes: Iterable[str]) -> None:
    """Fail closed: raise if any code is not in the W3 allow-list."""
    bad = [c for c in codes if c not in ALLOWED_REASON_CODES]
    if bad:
        raise ValueError(f"Unknown lookup reason code(s): {bad}")


def human_reason_line(codes: list[str]) -> str:
    """Short human-readable line; codes are the SSOT."""
    if not codes:
        return "ok"
    return "; ".join(sort_reason_codes(codes))


def normalize_dedup_key(normalized_intent: str, row_type: str, row_area: str) -> tuple[str, str, str]:
    from tools.refactor_decisions.precedent_scope import normalize_repo_path

    ni = (normalized_intent or "").strip().lower()[:500]
    ra = normalize_repo_path(row_area or "")
    dt = (row_type or "").strip()
    return (ni, ra, dt)
