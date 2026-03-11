"""FreezeStateReader -- reads L2 freeze state and gates meta-learning pipeline.

GAP-014: When L2 freeze is active (FREEZ), the meta-learning pipeline must not
run.  This module provides the FreezeStateReader protocol and a concrete
JsonFileBackedFreezeReader that reads from runtime_state.json.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class FreezeStateReader(Protocol):
    """Protocol: report whether the system is currently frozen."""

    def is_frozen(self) -> bool:
        """Return True if meta-learning should be suppressed due to freeze."""
        ...


class JsonFileBackedFreezeReader:
    """Read freeze state from runtime_state.json.

    The file is read once per is_frozen() call so that state changes on disk
    are reflected without restarting the process.  This is consistent with
    the existing FileBackedConfigProvider behaviour.

    Freeze is declared active when any of the following is true in the JSON:
      - Top-level "freeze" key is truthy.
      - Top-level "status" == "FREEZ".
      - Nested "l2_freeze" key under "flags" is truthy.
    """

    def __init__(self, runtime_state_path: Path) -> None:
        self._path = runtime_state_path

    def is_frozen(self) -> bool:
        """Return True if the runtime state file declares a freeze."""
        try:
            text = self._path.read_text(encoding="utf-8", errors="replace")
            data: dict = json.loads(text)
        except (OSError, json.JSONDecodeError):
            # File unreadable / malformed -- fail open (do not block pipeline)
            return False

        # Direct freeze key
        if data.get("freeze"):
            return True

        # status == FREEZ
        if str(data.get("status", "")).upper() == "FREEZ":
            return True

        # Nested flags.l2_freeze
        flags = data.get("flags", {})
        if isinstance(flags, dict) and flags.get("l2_freeze"):
            return True

        return False


class StaticFreezeReader:
    """Deterministic in-memory freeze reader for tests."""

    def __init__(self, frozen: bool = False) -> None:
        self._frozen = frozen

    def is_frozen(self) -> bool:
        return self._frozen


__all__ = [
    "FreezeStateReader",
    "JsonFileBackedFreezeReader",
    "StaticFreezeReader",
]
