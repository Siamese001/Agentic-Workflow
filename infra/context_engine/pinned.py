from __future__ import annotations

"""Pinned context utilities.

These helpers manage pinned context items that should always be present in
prompts (e.g. key instructions, safety reminders). Implementations are
simple and deterministic.
"""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class PinnedItem:
    id: str
    text: str
    metadata: Dict[str, Any]


def filter_pinned(items: List[PinnedItem], max_items: int) -> List[PinnedItem]:
    """Return up to max_items pinned items in a deterministic order."""

    if max_items <= 0:
        return []
    return items[:max_items]
