"""Post-Cursor Agent dispatcher handlers.

Each handler is a callable taking a ParsedResponse + repo_root, returning None.
Handlers MUST be fail-soft — never raise; log to stderr and continue.

Wired in by `.cursor/scripts/post_cursor_agent_dispatch.py` when env
`POST_CURSOR_AGENT_DISPATCHER=1`. When unset, the existing standalone scripts
in `.cursor/scripts/post_cursor_agent_*.py` run unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ParsedResponse:
    """Single-pass parse of the Cursor Agent post-response payload.

    Each handler receives this and reads only the fields it cares about,
    so the response is parsed exactly once instead of N times.
    """

    raw: str
    """Raw stdin payload exactly as received."""

    json_payload: dict | None = None
    """Parsed JSON if Cursor provided structured payload; None otherwise."""

    response_text: str = ""
    """The Cursor Agent response body (markers, prose, code blocks)."""

    tool_calls: list[dict] = field(default_factory=list)
    """List of tool-call objects extracted from the payload, if present."""

    markers: dict[str, list[str]] = field(default_factory=dict)
    """Captured markers keyed by name (DECISION_CAPTURED, DEFERRED_SCOPE, etc.)."""
