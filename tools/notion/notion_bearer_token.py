"""Single SSOT for reading the Notion API bearer token from the process environment.

Canonical variable: ``NOTION_TOKEN`` (matches Notion MCP / integration docs).

Compatibility: ``NOTION_API_KEY`` is still read if ``NOTION_TOKEN`` is unset so
older ``.env`` files and one-off scripts keep working. Prefer migrating to
``NOTION_TOKEN`` only.
"""

from __future__ import annotations

import os


def get_notion_bearer_token() -> str:
    """Return stripped bearer token, or empty string if neither env var is set."""
    raw = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY") or ""
    return raw.strip()


def get_notion_bearer_token_or_none() -> str | None:
    """Same as :func:`get_notion_bearer_token` but returns ``None`` when absent."""
    tok = get_notion_bearer_token()
    return tok or None
