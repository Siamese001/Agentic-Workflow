from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
L6 observability: Gemini Spy

Monitors and logs Gemini API interactions for observability.
"""


import logging
from typing import Any

Logger = logging.getLogger(__name__)


class GeminiSpy:
    """Monitors Gemini API calls for observability."""

    def __init__(self):
        self.calls: list[dict[str, Any]] = []
        self.enabled = True

    def record_call(self, endpoint: str, request: Any, response: Any) -> None:
        """Record a Gemini API call."""
        if self.enabled:
            self.calls.append({"endpoint": endpoint, "request": request, "response": response})

    def get_call_count(self) -> int:
        """Get total number of recorded calls."""
        return len(self.calls)

    def clear(self) -> None:
        """Clear recorded calls."""
        self.calls = []
