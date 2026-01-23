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

# Version information
__version__ = "1.0.0"
__description__ = "Production SDK wrappers for OpenAI, Anthropic, and Google Vertex AI"
