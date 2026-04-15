"""Argument validation helpers for the ADG SQLite MCP server."""

from __future__ import annotations

import os

MAX_LIMIT = int(os.getenv("ADG_MCP_MAX_LIMIT", "1000"))


def require_non_empty_str(name: str, value: str) -> str:
    """Validate and normalize required string arguments."""
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{name} must be non-empty")
    return cleaned


def require_positive_limit(limit: int) -> int:
    """Reject invalid or pathological fanout limits before hitting the backend."""
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise TypeError("limit must be an integer")
    if limit < 1:
        raise ValueError("limit must be >= 1")
    if limit > MAX_LIMIT:
        raise ValueError(f"limit must be <= {MAX_LIMIT}")
    return limit
