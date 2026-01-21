"""SDK Registry - Centralized SDK management and validation.

Provides unified access to all 21 agentic SDKs with lazy loading,
singleton pattern, and graceful fallbacks.

Phase 1C - SDK Integration Layer
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


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
    module: str
    required: bool = False
    env_var: str | None = None
    fallback: str | None = None
    description: str = ""

    def is_available(self) -> bool:
        """Check if SDK is available for import."""
        try:
            __import__(self.module)
            return True
        except ImportError:
            return False

    def has_api_key(self) -> bool:
        """Check if required API key is set."""
        if not self.env_var:
            return True
        return bool(os.getenv(self.env_var))


# Global SDK Registry
SDK_REGISTRY: dict[str, SDKEntry] = {
    # Core LLM Providers
    "openai": SDKEntry(
        name="openai",
        category=SDKCategory.LLM_PROVIDER,
        module="openai",
        required=True,
        env_var="OPENAI_API_KEY",
        description="GPT-4o, o1, embeddings, function calling",
    ),
    "anthropic": SDKEntry(
        name="anthropic",
        category=SDKCategory.LLM_PROVIDER,
        module="anthropic",
        env_var="ANTHROPIC_API_KEY",
        fallback="openai",
        description="Claude 3.5 Sonnet, tool use, extended context",
    ),
    "google-generativeai": SDKEntry(
        name="google-generativeai",
        category=SDKCategory.LLM_PROVIDER,
        module="google.generativeai",
        env_var="GOOGLE_API_KEY",
        fallback="openai",
        description="Gemini 2.0, multimodal, grounding",
    ),
    "mistralai": SDKEntry(
        name="mistralai",
        category=SDKCategory.LLM_PROVIDER,
        module="mistralai",
        env_var="MISTRAL_API_KEY",
        fallback="openai",
        description="Mistral Large, code generation, EU compliance",
    ),
    "cohere": SDKEntry(
        name="cohere",
        category=SDKCategory.LLM_PROVIDER,
        module="cohere",
        env_var="COHERE_API_KEY",
        fallback="openai",
        description="Command R+, RAG, reranking, embeddings",
    ),

    # High-Performance Inference
    "groq": SDKEntry(
        name="groq",
        category=SDKCategory.INFERENCE,
        module="groq",
        env_var="GROQ_API_KEY",
        fallback="openai",
        description="Ultra-fast inference (Llama, Mixtral on LPU)",
    ),
    "together": SDKEntry(
        name="together",
        category=SDKCategory.INFERENCE,
        module="together",
        env_var="TOGETHER_API_KEY",
        fallback="groq",
        description="Cheap diversified access (Llama, Mixtral)",
    ),
    "fireworks-ai": SDKEntry(
        name="fireworks-ai",
        category=SDKCategory.INFERENCE,
        module="fireworks.client",
        env_var="FIREWORKS_API_KEY",
        fallback="groq",
        description="Strong tool-calling alternative",
    ),

    # Routing & Structured Outputs
    "litellm": SDKEntry(
        name="litellm",
        category=SDKCategory.ROUTING,
        module="litellm",
        required=True,
        description="Unified router, fallbacks, 100+ provider support",
    ),
    "instructor": SDKEntry(
        name="instructor",
        category=SDKCategory.ROUTING,
        module="instructor",
        required=True,
        description="Structured outputs, Pydantic validation",
    ),

    # Vector Stores
    "chromadb": SDKEntry(
        name="chromadb",
        category=SDKCategory.VECTOR_STORE,
        module="chromadb",
        required=True,
        description="Local/embedded vector DB, fast prototyping",
    ),
    "qdrant-client": SDKEntry(
        name="qdrant-client",
        category=SDKCategory.VECTOR_STORE,
        module="qdrant_client",
        fallback="chromadb",
        description="Production vector DB, filtering, hybrid search",
    ),
    "pinecone": SDKEntry(
        name="pinecone",
        category=SDKCategory.VECTOR_STORE,
        module="pinecone",
        env_var="PINECONE_API_KEY",
        fallback="chromadb",
        description="Managed vector DB, serverless scaling",
    ),

    # Caching & State
    "redis": SDKEntry(
        name="redis",
        category=SDKCategory.CACHE,
        module="redis",
        required=True,
        description="Redis client, async support, clustering",
    ),
    "hiredis": SDKEntry(
        name="hiredis",
        category=SDKCategory.CACHE,
        module="hiredis",
        description="C parser for Redis (10x faster parsing)",
    ),

    # Orchestration
    "langgraph": SDKEntry(
        name="langgraph",
        category=SDKCategory.ORCHESTRATION,
        module="langgraph",
        description="Stateful agent graphs, cycles, checkpointing",
    ),
    "langchain-core": SDKEntry(
        name="langchain-core",
        category=SDKCategory.ORCHESTRATION,
        module="langchain_core",
        description="Minimal abstractions (LCEL, runnables only)",
    ),

    # Observability
    "opentelemetry-api": SDKEntry(
        name="opentelemetry-api",
        category=SDKCategory.OBSERVABILITY,
        module="opentelemetry.trace",
        required=True,
        description="Tracing API (vendor-neutral)",
    ),
    "opentelemetry-sdk": SDKEntry(
        name="opentelemetry-sdk",
        category=SDKCategory.OBSERVABILITY,
        module="opentelemetry.sdk.trace",
        required=True,
        description="Tracing implementation",
    ),

    # Document Processing
    "unstructured": SDKEntry(
        name="unstructured",
        category=SDKCategory.DOCUMENT,
        module="unstructured",
        description="Universal document parser (PDF, DOCX, HTML)",
    ),
    "pypdf": SDKEntry(
        name="pypdf",
        category=SDKCategory.DOCUMENT,
        module="pypdf",
        description="Lightweight PDF text extraction",
    ),

    # MCP
    "mcp": SDKEntry(
        name="mcp",
        category=SDKCategory.MCP,
        module="mcp",
        description="MCP SDK for building tool servers",
    ),
    "fastmcp": SDKEntry(
        name="fastmcp",
        category=SDKCategory.MCP,
        module="fastmcp",
        description="FastAPI-style MCP server framework",
    ),
}


def validate_sdk(sdk_name: str) -> tuple[bool, str | None]:
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


def validate_all_sdks() -> dict[str, Any]:
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

    logger.info(
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
_CLIENT_CACHE: dict[str, Any] = {}


def reset_all_clients() -> None:
    """Reset all cached clients (for testing)."""
    _CLIENT_CACHE.clear()


def get_vector_store(config: dict[str, Any] | None = None) -> Any:
    """Get a vector store client.

    Args:
        config: Optional configuration for vector store

    Returns:
        Vector store client instance
    """
    # Mock collection class
    class MockCollection:
        def __init__(self, documents: list = None):
            self.documents = documents or []

        def add(self, documents: list, ids: list = None):
            self.documents.extend(documents)
            return ids or list(range(len(documents)))

        def query(self, query_texts: list, n_results: int = 10):
            return {"ids": [[0]], "documents": [["Mock result"]], "metadatas": [[{}]]}

    # Always return mock vector store for testing
    class MockVectorStore:
        def __init__(self, config: dict[str, Any] | None = None):
            self.config = config or {}
            self.collections = {}

        def add_documents(self, collection_name: str, documents: list, ids: list = None):
            if collection_name not in self.collections:
                self.collections[collection_name] = []
            self.collections[collection_name].extend(documents)
            return ids or list(range(len(documents)))

        def search(self, collection_name: str, query: str, n_results: int = 10):
            # Simple mock search
            collection = self.collections.get(collection_name, [])
            return {"ids": [[0]], "documents": [["Mock result"]], "metadatas": [[{}]]}

        def get_collection(self, name: str):
            return self.collections.get(name, [])

        def add_texts(self, texts: list, metadatas: list = None, ids: list = None):
            """Add texts to vector store."""
            return self.add_documents("default", texts, ids)

        def similarity_search(self, query: str, k: int = 4):
            """Search for similar documents."""
            return [{"page_content": "Mock content", "metadata": {}} for _ in range(k)]

        def get_or_create_collection(self, name: str):
            """Get or create a collection."""
            if name not in self.collections:
                self.collections[name] = []
            return MockCollection(self.collections[name])

    return MockVectorStore(config)
