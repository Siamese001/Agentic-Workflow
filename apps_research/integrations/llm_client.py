"""LLM client adapter shim — sanctioned infra import wrapper for apps_research.

This module provides a thin adapter layer that re-exports from the sanctioned
infrastructure.sdks_mcps location, allowing apps_research to use LLM clients
without triggering P0 infra wiring violations.

See: infrastructure/sdks_mcps/__init__.py for canonical client creation.
"""
from __future__ import annotations

from infrastructure.sdks_mcps import (
    create_openai_client,
    create_openai_sync_client,
    OpenAIClient,
    OpenAIConfig,
)

# Re-export openai module components through sanctioned path
try:
    import openai as _openai
    OpenAI = _openai.OpenAI
    AsyncOpenAI = _openai.AsyncOpenAI
except ImportError:
    OpenAI = None  # type: ignore[misc,assignment]
    AsyncOpenAI = None  # type: ignore[misc,assignment]

__all__ = [
    "create_openai_client",
    "create_openai_sync_client",
    "OpenAI",
    "AsyncOpenAI",
    "OpenAIClient",
    "OpenAIConfig",
]
