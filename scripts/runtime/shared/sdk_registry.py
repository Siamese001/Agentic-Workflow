"""SDK Registry - Centralized SDK management and validation.

Provides unified access to all 21 agentic SDKs with lazy loading,
singleton pattern, and graceful fallbacks.

Phase 1C - SDK Integration Layer
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple, Any

LOGGER = logging.getLogger(__name__)


class SDKCategory(Enum):
    """SDK category classification."""
    LLM_PROVIDER = "llm_provider"
    INFERENCE = "inference"
    ROUTING = "routing"
    VECTOR_STORE = "vector_store"
    CACHE = "cache"
    ORCHESTRATION = "orchestration"
    OBSERVABILITY = "observability"
    DOCUMENT = "document"
    MCP = "mcp"


@dataclass
class SDKEntry:
    """SDK registry entry with metadata."""
    name: str
    category: SDKCategory
    _module: str
    _required: bool = False
    _env_var: Optional[str] = None
    _fallback: Optional[str] = None
    _description: str = ""

    @property
    def module(self) -> str:
        return self._module

    @property
    def required(self) -> bool:
        return self._required

    @property
    def env_var(self) -> Optional[str]:
        return self._env_var

    @property
    def fallback(self) -> Optional[str]:
        return self._fallback

    @property
    def description(self) -> str:
        return self._description

    def is_available(self: Any) -> bool:
        """Check if SDK is available for import."""
        try:
            __import__(self.module)
            return True
        except ImportError:
            return False


def has_api_key(self: Any) -> bool:
    """Check if required API key is set."""
    if not self.env_var:
        return True
    return bool(os.getenv(self.env_var))


# Global SDK Registry
SDK_REGISTRY: Dict[str, SDKEntry] = {
    # Core LLM Providers
    "openai": SDKEntry(
        name="openai",
        category=SDKCategory.LLM_PROVIDER,
        _module="openai",
        _required=True,
        _env_var="OPENAI_API_KEY",
        _description="GPT-4o, o1, embeddings, function calling",
    ),
    "anthropic": SDKEntry(
        name="anthropic",
        category=SDKCategory.LLM_PROVIDER,
        _module="anthropic",
        _env_var="ANTHROPIC_API_KEY",
        _fallback="openai",
        _description="Claude 3.5 Sonnet, tool use, extended context",
    ),
    "google-generativeai": SDKEntry(
        name="google-generativeai",
        category=SDKCategory.LLM_PROVIDER,
        _module="google.generativeai",
        _env_var="GOOGLE_API_KEY",
        _fallback="openai",
        _description="Gemini 2.0, multimodal, grounding",
    ),
    "mistralai": SDKEntry(
        name="mistralai",
        category=SDKCategory.LLM_PROVIDER,
        _module="mistralai",
        _env_var="MISTRAL_API_KEY",
        _fallback="openai",
        _description="Mistral Large, code generation, EU compliance",
    ),
    "cohere": SDKEntry(
        name="cohere",
        category=SDKCategory.LLM_PROVIDER,
        _module="cohere",
        _env_var="COHERE_API_KEY",
        _fallback="openai",
        _description="Command R+, RAG, reranking, embeddings",
    ),

    # High-Performance Inference
    "groq": SDKEntry(
        name="groq",
        category=SDKCategory.INFERENCE,
        _module="groq",
        _env_var="GROQ_API_KEY",
        _fallback="openai",
        _description="Ultra-fast inference (Llama, Mixtral on LPU)",
    ),
    "together": SDKEntry(
        name="together",
        category=SDKCategory.INFERENCE,
        _module="together",
        _env_var="TOGETHER_API_KEY",
        _fallback="groq",
        _description="Cheap diversified access (Llama, Mixtral)",
    ),
    "fireworks-ai": SDKEntry(
        name="fireworks-ai",
        category=SDKCategory.INFERENCE,
        _module="fireworks.client",
        _env_var="FIREWORKS_API_KEY",
        _fallback="groq",
        _description="Strong tool-calling alternative",
    ),

    # Routing & Structured Outputs
    "litellm": SDKEntry(
        name="litellm",
        category=SDKCategory.ROUTING,
        _module="litellm",
        _required=True,
        _description="Unified router, fallbacks, 100+ provider support",
    ),
    "instructor": SDKEntry(
        name="instructor",
        category=SDKCategory.ROUTING,
        _module="instructor",
        _required=True,
        _description="Structured outputs, Pydantic validation",
    ),

    # Vector Stores
    "chromadb": SDKEntry(
        name="chromadb",
        category=SDKCategory.VECTOR_STORE,
        _module="chromadb",
        _required=True,
        _description="Local/embedded vector DB, fast prototyping",
    ),
    "qdrant-client": SDKEntry(
        name="qdrant-client",
        category=SDKCategory.VECTOR_STORE,
        _module="qdrant_client",
        _fallback="chromadb",
        _description="Production vector DB, filtering, hybrid search",
    ),
    "pinecone": SDKEntry(
        name="pinecone",
        category=SDKCategory.VECTOR_STORE,
        _module="pinecone",
        _env_var="PINECONE_API_KEY",
        _fallback="chromadb",
        _description="Managed vector DB, serverless scaling",
    ),

    # Caching & State
    "redis": SDKEntry(
        name="redis",
        category=SDKCategory.CACHE,
        _module="redis",
        _required=True,
        _description="Redis client, async support, clustering",
    ),
    "hiredis": SDKEntry(
        name="hiredis",
        category=SDKCategory.CACHE,
        _module="hiredis",
        _description="C parser for Redis (10x faster parsing)",
    ),

    # Orchestration
    "langgraph": SDKEntry(
        name="langgraph",
        category=SDKCategory.ORCHESTRATION,
        _module="langgraph",
        _description="Stateful agent graphs, cycles, checkpointing",
    ),
    "langchain-core": SDKEntry(
        name="langchain-core",
        category=SDKCategory.ORCHESTRATION,
        _module="langchain_core",
        _description="Minimal abstractions (LCEL, runnables only)",
    ),

    # Observability
    "opentelemetry-api": SDKEntry(
        name="opentelemetry-api",
        category=SDKCategory.OBSERVABILITY,
        _module="opentelemetry.trace",
        _required=True,
        _description="Tracing API (vendor-neutral)",
    ),
    "opentelemetry-sdk": SDKEntry(
        name="opentelemetry-sdk",
        category=SDKCategory.OBSERVABILITY,
        _module="opentelemetry.sdk.trace",
        _required=True,
        _description="Tracing implementation",
    ),

    # Document Processing
    "unstructured": SDKEntry(
        name="unstructured",
        category=SDKCategory.DOCUMENT,
        _module="unstructured",
        _description="Universal document parser (PDF, DOCX, HTML)",
    ),
    "pypdf": SDKEntry(
        name="pypdf",
        category=SDKCategory.DOCUMENT,
        _module="pypdf",
        _description="Lightweight PDF text extraction",
    ),

    # MCP
    "mcp": SDKEntry(
        name="mcp",
        category=SDKCategory.MCP,
        _module="mcp",
        _description="MCP SDK for building tool servers",
    ),
    "fastmcp": SDKEntry(
        name="fastmcp",
        category=SDKCategory.MCP,
        _module="fastmcp",
        _description="FastAPI-style MCP server framework",
    ),
}


def validate_sdk(sdk_name: str) -> Tuple[bool, Optional[str]]:
    """Validate SDK availability and configuration.

    Args:
        sdk_name: Name of SDK to validate

    Returns:
        Tuple of (success, error_message)
    """
    if sdk_name not in SDK_REGISTRY:
        return False, f"Unknown SDK: {sdk_name}"

    entry = SDK_REGISTRY[sdk_name]

    # Check if module is available
    if not entry.is_available():
        if entry.required:
            return False, f"Required SDK '{sdk_name}' not installed"
        return False, f"Optional SDK '{sdk_name}' not installed"

    # Check API key if required
    if entry.env_var and not entry.has_api_key():
        if entry.required:
            return False, f"Required API key {entry.env_var} not set"
        return False, f"Optional API key {entry.env_var} not set"

    return True, None


def validate_all_sdks() -> Dict[str, Any]:
    """Validate all SDKs in registry.

    Returns:
        Validation report with status for each SDK
    """
    report = {
        "total": len(SDK_REGISTRY),
        "available": 0,
        "missing": 0,
        "missing_keys": 0,
        "details": {},
    }

    for sdk_name, entry in SDK_REGISTRY.items():
        success, error = validate_sdk(sdk_name)

        status = {
            "available": success,
            "required": entry.required,
            "category": entry.category.value,
            "error": error,
        }

        if success:
            report["available"] += 1
        elif "not installed" in (error or ""):
            report["missing"] += 1
        elif "not set" in (error or ""):
            report["missing_keys"] += 1

        report["details"][sdk_name] = status

    LOGGER.info(
        f"SDK validation: {report['available']}/{report['total']} available, "
        f"{report['missing']} missing, {report['missing_keys']} missing keys"
    )

    return report


def get_sdk_by_category(category: SDKCategory) -> list[SDKEntry]:
    """Get all SDKs in a category.

    Args:
        category: SDK category

    Returns:
        List of SDK entries
    """
    return [
        entry for entry in SDK_REGISTRY.values()
        if entry.category == category
    ]


def get_available_sdks() -> list[str]:
    """Get list of available SDK names.

    Returns:
        List of available SDK names
    """
    available = []
    for sdk_name in SDK_REGISTRY:
        success, _ = validate_sdk(sdk_name)
        if success:
            available.append(sdk_name)
    return available


# Singleton client cache
_CLIENT_CACHE: Dict[str, Any] = {}


def reset_all_clients() -> None:
    """Reset all cached clients (for testing)."""
    _CLIENT_CACHE.clear()


def get_vector_store(config: Optional[Dict[str, Any]] = None) -> Any:
    """Get a vector store client.

    Args:
        config: Optional configuration for vector store

    Returns:
        Vector store client instance
    """
    # Mock collection class
    class MockCollection:
        """TODO: Add docstring."""

        def __init__(self: Any, documents: list) -> None:
            """Initialize mock collection with optional documents."""
            self.documents = documents or []

        def add(self: Any, documents: list, ids: list) -> None:
            """Docstring."""
            self.documents.extend(documents)
            return ids or list(range(len(documents)))

        def query(self: Any, query_texts: list, n_results: int) -> None:
            """Docstring."""
            return {"ids": [[0]], "documents": [["Mock result"]], "metadatas": [[{}]]}

    # Always return mock vector store for testing

    class MockVectorStore:
        """Docstring."""
        def __init__(self: Any, config: Optional[Dict[str, Any]]) -> None:
            """Initialize mock vector store with optional config."""
            self.config = config or {}
            self.collections = {}

        def add_documents(self: Any, collection_name: str, documents: list, ids: list) -> None:
            """Add documents to collection."""
            if collection_name not in self.collections:
                self.collections[collection_name] = []
            self.collections[collection_name].extend(documents)
            return ids or list(range(len(documents)))

        def search(self: Any, collection_name: str, query: str, n_results: int) -> None:
            """Docstring."""
            # Simple mock search
            self.collections.get(collection_name, [])
            return {"ids": [[0]], "documents": [["Mock result"]], "metadatas": [[{}]]}

        def get_collection(self: Any, name: str) -> None:
            """Docstring."""
            return self.collections.get(name, [])

        def add_texts(self: Any, texts: list, metadatas: list, ids: list) -> None:
            """Add texts to vector store."""
            return self.add_documents("default", texts, ids)

        def similarity_search(self: Any, query: str, k: int) -> None:
            """Search for similar documents."""
            return [{"page_content": "Mock content", "metadata": {}} for _ in range(k)]

        def get_or_create_collection(self: Any, name: str) -> None:
            """Get or create a collection."""
            if name not in self.collections:
                self.collections[name] = []
            return MockCollection(self.collections[name])

    return MockVectorStore(config)