from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""MCP Provider mappings and defaults.

Phase 1 - Pillar 3: Typed Contracts (Strict Schemas)
"""

from enum import Enum


class ProviderType(Enum):
    """Supported MCP Provider types."""

    STUB = "stub"
    REDIS = "redis"
    CHROMADB = "chromadb"
    QDRANT = "qdrant"
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
    "openai": "openai",
    "anthropic": "anthropic",
    "google": "google.genai",
    "http": "httpx",
}


DEFAULT_PROVIDER_CLASSES: dict[str, str] = {
    "stub": "MCPClientStub",
    "redis": "Redis",
    "chromadb": "Client",
    "qdrant": "QdrantClient",
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "google": "GenerativeModel",
    "http": "Client",
}


def get_default_module(Provider: str) -> str | None:
    """Get default module name for a Provider.

    Args:
        Provider: Provider type string

    Returns:
        Module name or None if stub
    """
    return DEFAULT_PROVIDER_MODULES.get(Provider.lower())


def get_default_class(Provider: str) -> str | None:
    """Get default class name for a Provider.

    Args:
        Provider: Provider type string

    Returns:
        Class name or None
    """
    return DEFAULT_PROVIDER_CLASSES.get(Provider.lower())


def register_provider(
    Provider: str,
    module: str,
    class_name: str,
) -> None:
    """Register a custom Provider mapping.

    Args:
        Provider: Provider identifier
        module: Python module path
        class_name: Class name within module
    """
    DEFAULT_PROVIDER_MODULES[Provider.lower()] = module
    DEFAULT_PROVIDER_CLASSES[Provider.lower()] = class_name
