from __future__ import annotations
"""
L6 Observability: Gemini Spy

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
