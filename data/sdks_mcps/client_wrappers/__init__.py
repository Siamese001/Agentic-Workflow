"""Client Wrappers - Production SDK Wrappers for OpenAI, Anthropic, and Google Vertex AI

This module provides factory functions for creating production-ready client instances
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

from .openai_client import create_openai_client, OpenAIClient, OpenAIConfig
from .anthropic_client import create_anthropic_client, AnthropicClient, AnthropicConfig
from .vertex_client import create_vertex_client, VertexClient, VertexConfig
from .multi_provider_router import (
    create_multi_provider_router, 
    MultiProviderRouter, 
    RouterConfig,
    Provider,
    ProviderConfig
)

__all__ = [
    # Factory functions
    "create_openai_client",
    "create_anthropic_client", 
    "create_vertex_client",
    "create_multi_provider_router",
    
    # Client classes
    "OpenAIClient",
    "AnthropicClient",
    "VertexClient", 
    "MultiProviderRouter",
    
    # Configuration classes
    "OpenAIConfig",
    "AnthropicConfig",
    "VertexConfig",
    "RouterConfig",
    "ProviderConfig",
    
    # Enums
    "Provider"
]

# Version information
__version__ = "1.0.0"
__description__ = "Production SDK wrappers for OpenAI, Anthropic, and Google Vertex AI"
