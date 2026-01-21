"""MCP provider mappings and defaults.

Phase 1 - Pillar 3: Typed Contracts (Strict Schemas)
"""

from enum import Enum


class ProviderType(Enum):
    """Supported MCP provider types."""
    STUB = "stub"
    REDIS = "redis"
    CHROMADB = "chromadb"
    QDRANT = "qdrant"
    PINECONE = "pinecone"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    HTTP = "http"
    CUSTOM = "custom"


DEFAULT_PROVIDER_MODULES: dict[str, str] = {
    "stub": None,
    "redis": "redis",
    "chromadb": "chromadb",
    "qdrant": "qdrant_client",
    "pinecone": "pinecone",
    "openai": "openai",
    "anthropic": "anthropic",
    "google": "google.generativeai",
    "http": "httpx",
}


DEFAULT_PROVIDER_CLASSES: dict[str, str] = {
    "stub": "MCPClientStub",
    "redis": "Redis",
    "chromadb": "Client",
    "qdrant": "QdrantClient",
    "pinecone": "Pinecone",
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "google": "GenerativeModel",
    "http": "Client",
}


def get_default_module(provider: str) -> str | None:
    """Get default module name for a provider.

    Args:
        provider: Provider type string

    Returns:
        Module name or None if stub
    """
    return DEFAULT_PROVIDER_MODULES.get(provider.lower())


def get_default_class(provider: str) -> str | None:
    """Get default class name for a provider.

    Args:
        provider: Provider type string

    Returns:
        Class name or None
    """
    return DEFAULT_PROVIDER_CLASSES.get(provider.lower())


def register_provider(
    provider: str,
    module: str,
    class_name: str,
) -> None:
    """Register a custom provider mapping.

    Args:
        provider: Provider identifier
        module: Python module path
        class_name: Class name within module
    """
    DEFAULT_PROVIDER_MODULES[provider.lower()] = module
    DEFAULT_PROVIDER_CLASSES[provider.lower()] = class_name
