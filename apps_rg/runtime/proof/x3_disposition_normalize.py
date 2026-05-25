"""Normalize apps_rg lane x3_code values for quality-plan closeout (W0+)."""
from __future__ import annotations

from typing import Any

ALLOW_RAW = frozenset({"X3_ALLOW", "ALLOW"})
BLOCK_RAW_PREFIXES = ("X3_BLOCK", "X3_DENY", "BLOCK", "DENY")
REVIEW_MARKERS = ("REVIEW", "SOFT_FAIL")


def normalize_x3_code(x3_code: str | None) -> str:
    """Map raw x3_disposition.json x3_code to closeout bucket."""
    raw = str(x3_code or "").strip()
    if not raw:
        return "UNKNOWN"
    upper = raw.upper()
    if upper in ALLOW_RAW or (upper.startswith("X3_ALLOW") and "REVIEW" not in upper):
        return "ALLOW_FINISH"
    if any(marker in upper for marker in REVIEW_MARKERS):
        return "REVIEW"
    if any(upper.startswith(prefix) for prefix in BLOCK_RAW_PREFIXES) or upper == "BLOCK":
        return "BLOCK"
    if "ALLOW" in upper and "REVIEW" not in upper and "SOFT_FAIL" not in upper:
        return "ALLOW_FINISH"
    return "UNKNOWN"


def normalize_x3_disposition(payload: dict[str, Any]) -> dict[str, Any]:
    """Return normalization view for a lane x3_disposition.json payload."""
    raw = str(payload.get("x3_code") or "").strip()
    normalized = normalize_x3_code(raw)
    x3_pass = bool(payload.get("pass"))
    live_x3_allow_claimed = (
        normalized == "ALLOW_FINISH"
        and x3_pass
    )
    return {
        "x3_code_raw": raw or None,
        "x3_normalized": normalized,
        "x3_pass": x3_pass,
        "live_x3_allow_claimed": live_x3_allow_claimed,
    }
