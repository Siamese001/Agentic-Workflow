"""
Pinned context management for résumé processing workflows.

Manages essential context items that ensure consistent résumé improvement prompt generation.
"""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class PinnedItem:
    """
    Represents pinned context item for résumé processing.

    Ensures critical information is always included in résumé improvement workflows.
    """
    id: str
    text: str
    metadata: Dict[str, Any]


def filter_pinned(items: List[PinnedItem], max_items: int) -> List[PinnedItem]:
    """
    Filters pinned context items for résumé processing workflows.

    Ensures optimal selection of essential information for résumé improvement operations.
    """

    if max_items <= 0:
        return []
    return items[:max_items]



