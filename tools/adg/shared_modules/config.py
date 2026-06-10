"""Shared ADG configuration helpers."""

from __future__ import annotations

import os


def normalize_optional_env_url(value: str | None) -> str | None:
    """Return a usable URL string, or None for empty/unexpanded MCP placeholders."""
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if "$" in normalized or normalized.startswith("{") or normalized.endswith("}"):
        return None
    return normalized


def resolve_adg_redis_url(explicit_url: str | None = None) -> str | None:
    """Resolve the optional ADG Redis URL from an explicit value or environment."""
    return normalize_optional_env_url(explicit_url) or normalize_optional_env_url(
        os.getenv("ADG_REDIS_URL")
    )
