"""Client Wrappers - Production SDK Wrappers for OpenAI, Anthropic, and Google Vertex AI

This module provides builder functions for creating production-ready client instances
with comprehensive error handling, retry logic, and optimization features.

Usage:
    from data.sdks_mcps.client_wrappers import (
        create_openai_client,
        create_anthropic_client,
        create_vertex_client,
        create_multi_provider_router
    )

    # Single provider
    client = create_openai_client()
    response = client.chat_completion([{"role": "user", "content": "Hi"}])

    # Multi-provider with failover
    router = create_multi_provider_router()
    result = router.chat_completion([{"role": "user", "content": "Hi"}])
"""

__all__ = [
    # builder functions
    "create_openai_client",
    "create_openai_sync_client",
    "create_anthropic_client",
    "create_vertex_client",
    # Client classes
    "OpenAIClient",
    "AnthropicClient",
    "VertexClient",
    # configuration classes
    "OpenAIConfig",
    "AnthropicConfig",
    "VertexConfig",
]

# MultiProviderRouterAgent moved to agentic_core.L5_safety.guardrails.multi_provider_router_agent

# Temporary minimal wrapper functions for migration
import os

def create_openai_client():
    """Create OpenAI client - minimal wrapper for migration."""
    import openai

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY missing")
    return openai.AsyncOpenAI(api_key=api_key)


def create_openai_sync_client():
    """Create synchronous OpenAI client for sync call sites."""
    import openai

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY missing")
    return openai.OpenAI(api_key=api_key)


def create_anthropic_client():
    """Create Anthropic client - minimal wrapper for migration."""
    import anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY missing")
    return anthropic.AsyncAnthropic(api_key=api_key)


def create_vertex_client():
    """Create Vertex client - minimal wrapper for migration."""
    import google.generativeai as genai

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY missing")
    genai.configure(api_key=api_key)
    return genai


def create_gemini_model(model_name: str):
    """Create a configured Gemini ``GenerativeModel`` instance.

    Canonical chokepoint for all Gemini SDK usage outside this package.
    Replaces scattered ``import google.generativeai as genai`` +
    ``genai.configure`` + ``genai.GenerativeModel(name)`` triples in
    production code. See ``ops_scripts/ci/infra_wiring_scan.py`` for the
    governance policy that forces callers through this adapter.

    Args:
        model_name: Gemini model identifier (e.g. ``"gemini-2.5-flash"``).

    Returns:
        A ``google.generativeai.GenerativeModel`` configured with the
        ``GEMINI_API_KEY`` or ``GOOGLE_API_KEY`` environment variable.

    Raises:
        ValueError: if neither env var is set.
        ImportError: if the ``google-generativeai`` SDK is not installed.
    """
    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY must be set")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)


# Import minimal classes
class OpenAIClient:
    pass


class AnthropicClient:
    pass


class VertexClient:
    pass


class OpenAIConfig:
    pass


class AnthropicConfig:
    pass


class VertexConfig:
    pass


# Version information
__version__ = "1.0.0"
__description__ = "Production SDK wrappers for OpenAI, Anthropic, and Google Vertex AI"
