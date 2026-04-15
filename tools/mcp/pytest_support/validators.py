from __future__ import annotations

import sys
from pathlib import Path

from .config import ALLOWED_COVERAGE_REPORTS, MAX_EXECUTION_TIME, SAFE_EXPR_RE


def resolve_confined_path(user_path: str, base: Path) -> Path:
    """Resolve user_path relative to base and reject traversal outside base."""
    try:
        resolved = (base / user_path).resolve()
    except (ValueError, OSError) as exc:
        raise ValueError(f"Invalid path {user_path!r}: {exc}") from exc
    try:
        resolved.relative_to(base.resolve())
    except ValueError as exc:
        raise ValueError(f"Path {user_path!r} escapes the allowed directory {base}") from exc
    return resolved


def validate_expr(value: str, param_name: str) -> str:
    """Reject marker/keyword expressions containing shell-dangerous characters."""
    if not SAFE_EXPR_RE.match(value):
        raise ValueError(
            f"{param_name!r} contains unsafe characters. "
            "Only word chars, spaces, and common punctuation are allowed."
        )
    return value


def python_cmd(*args: str) -> list[str]:
    """Run subprocesses with the same interpreter as the MCP server."""
    return [sys.executable, *args]


def validate_timeout(value: int) -> int:
    """Reject nonsensical timeouts and enforce the server-side max."""
    if value <= 0:
        raise ValueError("timeout must be a positive integer")
    return min(value, MAX_EXECUTION_TIME)


def validate_coverage_report(value: str) -> str:
    """Restrict coverage reports to known pytest-cov values."""
    if value not in ALLOWED_COVERAGE_REPORTS:
        allowed = ", ".join(sorted(ALLOWED_COVERAGE_REPORTS))
        raise ValueError(f"Unsupported coverage format {value!r}. Allowed: {allowed}")
    return value


__all__ = [
    "python_cmd",
    "resolve_confined_path",
    "validate_coverage_report",
    "validate_expr",
    "validate_timeout",
]
