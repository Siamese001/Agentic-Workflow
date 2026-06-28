"""Strip retired HEAVY/MODERATE/LIGHT_PROTECTED rewrite-intensity fields from employment bullet JSON."""

from __future__ import annotations

from typing import Any

# Top-level keys the retired intensity model used — must never appear in lane output.
RETIRED_TOP_LEVEL_KEYS: frozenset[str] = frozenset(
    {
        "rewrite_distribution",
        "rewrite_intensity_request",
        "strategic_tailor_plan",
    }
)

RETIRED_BULLET_KEYS: frozenset[str] = frozenset({"rewrite_intensity"})

RETIRED_SELF_CHECK_KEYS: frozenset[str] = frozenset(
    {
        "distribution_valid",
        "no_heavy_rewrites",
    }
)

_INTENSITY_TOKENS: frozenset[str] = frozenset({"HEAVY", "MODERATE", "LIGHT_PROTECTED"})


def strip_bullet_row(row: dict[str, Any]) -> dict[str, Any]:
    cleaned = dict(row)
    for key in RETIRED_BULLET_KEYS:
        cleaned.pop(key, None)
    return cleaned


def strip_employment_bullet_intensity_model(parsed: dict[str, Any] | None) -> dict[str, Any] | None:
    """Remove rewrite-intensity taxonomy fields from a PROVIDER_MODEL or merged employment-bullet payload."""
    if parsed is None or not isinstance(parsed, dict):
        return parsed
    out = dict(parsed)
    for key in RETIRED_TOP_LEVEL_KEYS:
        out.pop(key, None)
    sc = out.get("self_check")
    if isinstance(sc, dict):
        sc_clean = {k: v for k, v in sc.items() if k not in RETIRED_SELF_CHECK_KEYS}
        out["self_check"] = sc_clean
    bullets = out.get("bullets")
    if isinstance(bullets, list):
        out["bullets"] = [
            strip_bullet_row(b) for b in bullets if isinstance(b, dict)
        ]
    return out


def find_rewrite_intensity_model_violations(
    *,
    parsed_output: dict[str, Any] | None,
    bullets: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Return human-readable violation messages if retired intensity fields are present."""
    violations: list[str] = []
    po = parsed_output if isinstance(parsed_output, dict) else {}
    for key in RETIRED_TOP_LEVEL_KEYS:
        if key in po:
            violations.append(f"top_level.{key}")
    sc = po.get("self_check")
    if isinstance(sc, dict):
        for key in RETIRED_SELF_CHECK_KEYS:
            if key in sc:
                violations.append(f"self_check.{key}")
    rows = bullets if bullets is not None else po.get("bullets")
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            if "rewrite_intensity" in row:
                bid = str(row.get("bullet_id") or "?")
                val = str(row.get("rewrite_intensity") or "")
                violations.append(f"bullets.{bid}.rewrite_intensity={val}")
    return violations


def sanitize_l2_employment_bullet_record(l2: dict[str, Any]) -> dict[str, Any]:
    """Strip retired intensity fields from persisted l2_output (final write guard)."""
    out = dict(l2)
    for key in RETIRED_TOP_LEVEL_KEYS:
        out.pop(key, None)
    sc = out.get("self_check")
    if isinstance(sc, dict):
        out["self_check"] = {k: v for k, v in sc.items() if k not in RETIRED_SELF_CHECK_KEYS}
    bullets = out.get("bullets")
    if isinstance(bullets, list):
        out["bullets"] = [strip_bullet_row(b) for b in bullets if isinstance(b, dict)]
    return out


def serialized_contains_intensity_taxonomy(text: str) -> bool:
    """True when serialized JSON still advertises the retired taxonomy (gate helper)."""
    lower = text.lower()
    if "rewrite_distribution" in lower or "rewrite_intensity" in lower:
        return True
    for token in _INTENSITY_TOKENS:
        if f'"{token.lower()}"' in lower or f'"{token}"' in text:
            return True
    return False


__all__ = [
    "RETIRED_BULLET_KEYS",
    "RETIRED_SELF_CHECK_KEYS",
    "RETIRED_TOP_LEVEL_KEYS",
    "find_rewrite_intensity_model_violations",
    "sanitize_l2_employment_bullet_record",
    "serialized_contains_intensity_taxonomy",
    "strip_bullet_row",
    "strip_employment_bullet_intensity_model",
]
