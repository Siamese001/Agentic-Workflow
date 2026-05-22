"""Single source of truth for the default targeting briefing (JD/briefing lane context).

Role-specific briefings use ``apps_rg/config/targeting/*_briefing.md`` (GFM tables). Operators edit
``apps_rg/config/default_targeting_briefing.txt``; dispatch entrypoints load it via
``default_targeting_briefing_text()`` instead of in-code string literals.
"""

from __future__ import annotations

import functools
from pathlib import Path

_DEFAULT_FILE = Path(__file__).resolve().parents[1] / "config" / "default_targeting_briefing.txt"

# Exposed for runbooks, tests, and tooling that need the filesystem path.
DEFAULT_TARGETING_BRIEFING_PATH: Path = _DEFAULT_FILE


@functools.lru_cache(maxsize=1)
def default_targeting_briefing_text() -> str:
    """Return UTF-8 text from the canonical default briefing file (stripped)."""
    return _DEFAULT_FILE.read_text(encoding="utf-8").strip()


__all__ = [
    "DEFAULT_TARGETING_BRIEFING_PATH",
    "default_targeting_briefing_text",
]
