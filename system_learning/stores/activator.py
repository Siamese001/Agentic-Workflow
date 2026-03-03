"""Concrete Activator — swaps active config version pointer via L4StateWriter.

Provides in-memory and file-backed implementations of the ``Activator``
protocol defined in ``meta_learning_pipeline.py``.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# In-memory implementation
# ---------------------------------------------------------------------------


@dataclass
class InMemoryActivator:
    """In-memory activator for testing."""

    _active: dict[str, str] = field(default_factory=dict)

    def activate(self, component: str, version_id: str) -> None:
        """Activate a specific version for a component."""
        logger.info("Activating component=%s version=%s", component, version_id)
        self._active[component] = version_id

    def get_active(self, component: str) -> str | None:
        return self._active.get(component)


# ---------------------------------------------------------------------------
# File-backed implementation
# ---------------------------------------------------------------------------


class FileBackedActivator:
    """File-backed activator that persists active version pointers.

    Writes ``<base_dir>/_active.json`` mapping component names to version IDs.
    """

    def __init__(self, base_dir: Path) -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._active_path = self._base_dir / "_active.json"
        self._active: dict[str, str] = self._load()

    def _load(self) -> dict[str, str]:
        if self._active_path.exists():
            try:
                return json.loads(self._active_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save(self) -> None:
        self._active_path.write_text(
            json.dumps(self._active, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def activate(self, component: str, version_id: str) -> None:
        """Activate a specific version for a component."""
        logger.info("Activating component=%s version=%s", component, version_id)
        self._active[component] = version_id
        self._save()

    def get_active(self, component: str) -> str | None:
        return self._active.get(component)


__all__ = [
    "InMemoryActivator",
    "FileBackedActivator",
]
