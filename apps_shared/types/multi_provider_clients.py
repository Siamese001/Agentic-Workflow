"""Stub: multi_provider_clients — minimal shim for HardenedGeminiExecutor."""
from __future__ import annotations

from enum import Enum
from typing import Any


class Provider(str, Enum):
    GOOGLE = "google"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class _StubClient:
    """Minimal stub client that satisfies the HardenedGeminiExecutor interface."""

    def __init__(self, provider: Provider) -> None:
        self._provider = provider

    def interactions(self, *args: Any, **kwargs: Any) -> Any:
        raise ImportError(
            f"No real client available for provider {self._provider!r}. "
            "Install the required SDK.",
        )


def get_client(provider: Provider) -> _StubClient:
    """Return a stub client for the given provider."""
    return _StubClient(provider)


__all__ = ["Provider", "get_client"]
