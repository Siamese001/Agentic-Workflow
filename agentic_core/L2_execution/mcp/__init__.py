from __future__ import annotations

"""MCP Integration - Hardened Sovereign Module."""
from .client import MCPClient, MCPClientSpec
from .exceptions import MCPClientInitializationError, MCPClientNotFoundError, MCPError
from .factory import create_mcp_registry, instantiate_mcp_client, parse_mcp_client_specs
from .providers import get_default_class, get_default_module
from .SovereignLLMGateway import SovereignLLMGateway, get_llm_gateway
from .llm_provider_mixin import LLMProviderMixin
from .EmbeddingSovereignAgent import EmbeddingSovereignAgent, get_embedding_gateway
from .embedding_mixin import EmbeddingMixin

__all__ = [
    "MCPClient",
    "MCPClientSpec",
    "parse_mcp_client_specs",
    "instantiate_mcp_client",
    "create_mcp_registry",
    "MCPError",
    "MCPClientInitializationError",
    "MCPClientNotFoundError",
    "get_default_module",
    "get_default_class",
    # Phase 4 LLM Gateway
    "SovereignLLMGateway",
    "get_llm_gateway",
    "LLMProviderMixin",
    # Phase 4 Embedding Gateway
    "EmbeddingSovereignAgent",
    "get_embedding_gateway",
    "EmbeddingMixin",
]
