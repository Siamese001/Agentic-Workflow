from __future__ import annotations

"""Context slot definitions.

Slots represent logical sections in a prompt (e.g. job, resume, policy)
that can be filled with curated context.
"""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ContextSlot:
    id: str
    max_items: int
    metadata: Dict[str, Any]


def assign_to_slot(slot: ContextSlot, texts: List[str]) -> List[str]:
    """Assign up to slot.max_items texts to a slot, preserving order."""

    if slot.max_items <= 0:
        return []
    return texts[: slot.max_items]



