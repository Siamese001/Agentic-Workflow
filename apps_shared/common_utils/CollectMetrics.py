"""
base_collector.py - Collector Module

Domain: metrics
Generated: 2025-12-07T12:07:59.846192
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class CollectedItem:
    """A collected item."""
    source: str
    data: Any
    timestamp: float = field(default_factory=lambda: __import__("time").time())


class BaseCollector:
    """Collector for metrics domain."""

    def __init__(self, config: Optional[Dict[str, object]] = None):
        self.config = config or {}
        self.items: Dict[str, List[CollectedItem]] = defaultdict(list)
        self.max_items = self.config.get("max_items", 1000)
        logger.info(f"Initialized {self.__class__.__name__}")

    def collect(self, source: str, data: object) -> None:
        """Collect data from source."""
        item = CollectedItem(source=source, data=data)
        self.items[source].append(item)

        # Trim if over limit
        if len(self.items[source]) > self.max_items:
            self.items[source] = self.items[source][-self.max_items:]

        logger.debug(f"Collected item from {source}")

    def get_items(self, source: Optional[str] = None) -> List[CollectedItem]:
        """Get collected items."""
        if source:
            return self.items.get(source, [])
        return [item for items in self.items.values() for item in items]

    def flush(self, source: Optional[str] = None) -> List[CollectedItem]:
        """Flush and return items."""
        if source:
            items = self.items.pop(source, [])
        else:
            items = self.get_items()
            self.items.clear()
        return items


# Global collector
_collector = BaseCollector()


def collect(source: str, data: object) -> None:
    """Collect data to global collector."""
    _collector.collect(source, data)


def get_collected(source: Optional[str] = None) -> List[CollectedItem]:
    """Get items from global collector."""
    return _collector.get_items(source)