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

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def create_openai_client():
    """Create OpenAI client - minimal wrapper for migration."""
    import openai

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY missing")
    return openai.AsyncOpenAI(api_key=api_key)


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
