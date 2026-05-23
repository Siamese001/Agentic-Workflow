"""Parent-pack (00A) certification vocabulary bridges.

Maps internal L5 packet / binding tokens to the five parent ``cert_status``
values in ``00A_L5_Governance_Safety.md`` §5.
"""

from __future__ import annotations

from typing import Final

# Parent 00A §5 — canonical certification status vocabulary.
PARENT_CERT_STATUSES: Final[frozenset[str]] = frozenset(
    {
        "certified",
        "not_certified",
        "expired",
        "mismatched",
        "pending_reclearance",
    }
)

_INTERNAL_TO_PARENT: Final[dict[str, str]] = {
    "L5_CERTIFIED": "certified",
    "L5_NOT_CERTIFIED": "not_certified",
    "L5_REQUIRES_RECLEARANCE": "pending_reclearance",
    "L5_EXPIRED": "expired",
    "L5_MISMATCHED": "mismatched",
}

_PARENT_TO_INTERNAL: Final[dict[str, str]] = {
    v: k for k, v in _INTERNAL_TO_PARENT.items()
}


def internal_cert_status_to_parent(internal: str) -> str:
    """Map producer-internal status to parent ``cert_status`` token."""

    normalized = (internal or "").strip()
    if normalized in PARENT_CERT_STATUSES:
        return normalized
    mapped = _INTERNAL_TO_PARENT.get(normalized)
    if mapped is None:
        raise ValueError(
            f"Unknown internal L5 certification status {internal!r}; "
            f"expected one of {sorted(_INTERNAL_TO_PARENT)}"
        )
    return mapped


def parent_cert_status_to_internal(parent: str) -> str:
    """Map parent ``cert_status`` to internal producer token (best-effort)."""

    if parent not in PARENT_CERT_STATUSES:
        raise ValueError(
            f"parent cert_status {parent!r} not in {sorted(PARENT_CERT_STATUSES)}"
        )
    return _PARENT_TO_INTERNAL.get(parent, "L5_NOT_CERTIFIED")
