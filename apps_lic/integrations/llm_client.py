"""LLM client adapter shim — sanctioned infra import wrapper for apps_lic.

This module provides a thin adapter layer that re-exports from the sanctioned
infrastructure.sdks_mcps location, allowing apps_lic to use LLM clients
without triggering P0 infra wiring violations.

See: infrastructure/sdks_mcps/__init__.py for canonical client creation.
"""
from __future__ import annotations

# guardian: allow-layer-violation -- sanctioned LLM client shim; apps_lic/integrations is the approved cross-layer seam for infra SDK access
from infrastructure.sdks_mcps import (
    create_openai_client,
    create_openai_sync_client,
    OpenAIClient,
    OpenAIConfig,
    create_anthropic_client,
    AnthropicClient,
    AnthropicConfig,
)

# Re-export openai module components through sanctioned path
try:
    import openai as _openai
    OpenAI = _openai.OpenAI
    AsyncOpenAI = _openai.AsyncOpenAI
except ImportError:
    OpenAI = None  # type: ignore[misc,assignment]
    AsyncOpenAI = None  # type: ignore[misc,assignment]

# Re-export anthropic module components through sanctioned path
try:
    import anthropic as _anthropic
    Anthropic = _anthropic.Anthropic
    AsyncAnthropic = _anthropic.AsyncAnthropic
except ImportError:
    Anthropic = None  # type: ignore[misc,assignment]
    AsyncAnthropic = None  # type: ignore[misc,assignment]

__all__ = [
    "create_openai_client",
    "create_openai_sync_client",
    "OpenAI",
    "AsyncOpenAI",
    "OpenAIClient",
    "OpenAIConfig",
    "create_anthropic_client",
    "Anthropic",
    "AsyncAnthropic",
    "AnthropicClient",
    "AnthropicConfig",
]
