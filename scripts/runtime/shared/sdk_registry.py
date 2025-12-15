"""SDK Registry - Centralized SDK management and validation.

Provides unified access to all 21 agentic SDKs with lazy loading,
singleton pattern, and graceful fallbacks.

Phase 1C - SDK Integration Layer
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple

LOGGER = logging.getLogger(__name__)


class SDKCategory(Enum):
    """SDK category classification."""


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


def is_available(self: Any) -> bool:
        """Check if SDK is available for import."""
        try:
            __import__(self.module)
            return True
        except ImportError:
    pass
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
        NAME="openai",
        CATEGORY=SDKCategory.LLM_PROVIDER,
        MODULE="openai",
        REQUIRED=True,
        env_var="OPENAI_API_KEY",
        DESCRIPTION="GPT-4o, o1, embeddings, function calling",
    ),
    "anthropic": SDKEntry(
        NAME="anthropic",
        CATEGORY=SDKCategory.LLM_PROVIDER,
        MODULE="anthropic",
        env_var="ANTHROPIC_API_KEY",
        FALLBACK="openai",
        DESCRIPTION="Claude 3.5 Sonnet, tool use, extended context",
    ),
    "google-generativeai": SDKEntry(
        NAME="google-generativeai",
        CATEGORY=SDKCategory.LLM_PROVIDER,
        MODULE="google.generativeai",
        env_var="GOOGLE_API_KEY",
        FALLBACK="openai",
        DESCRIPTION="Gemini 2.0, multimodal, grounding",
    ),
    "mistralai": SDKEntry(
        NAME="mistralai",
        CATEGORY=SDKCategory.LLM_PROVIDER,
        MODULE="mistralai",
        env_var="MISTRAL_API_KEY",
        FALLBACK="openai",
        DESCRIPTION="Mistral Large, code generation, EU compliance",
    ),
    "cohere": SDKEntry(
        NAME="cohere",
        CATEGORY=SDKCategory.LLM_PROVIDER,
        MODULE="cohere",
        env_var="COHERE_API_KEY",
        FALLBACK="openai",
        DESCRIPTION="Command R+, RAG, reranking, embeddings",
    ),

    # High-Performance Inference
    "groq": SDKEntry(
        NAME="groq",
        CATEGORY=SDKCategory.INFERENCE,
        MODULE="groq",
        env_var="GROQ_API_KEY",
        FALLBACK="openai",
        DESCRIPTION="Ultra-fast inference (Llama, Mixtral on LPU)",
    ),
    "together": SDKEntry(
        NAME="together",
        CATEGORY=SDKCategory.INFERENCE,
        MODULE="together",
        env_var="TOGETHER_API_KEY",
        FALLBACK="groq",
        DESCRIPTION="Cheap diversified access (Llama, Mixtral)",
    ),
    "fireworks-ai": SDKEntry(
        NAME="fireworks-ai",
        CATEGORY=SDKCategory.INFERENCE,
        MODULE="fireworks.client",
        env_var="FIREWORKS_API_KEY",
        FALLBACK="groq",
        DESCRIPTION="Strong tool-calling alternative",
    ),

    # Routing & Structured Outputs
    "litellm": SDKEntry(
        NAME="litellm",
        CATEGORY=SDKCategory.ROUTING,
        MODULE="litellm",
        REQUIRED=True,
        DESCRIPTION="Unified router, fallbacks, 100+ provider support",
    ),
    "instructor": SDKEntry(
        NAME="instructor",
        CATEGORY=SDKCategory.ROUTING,
        MODULE="instructor",
        REQUIRED=True,
        DESCRIPTION="Structured outputs, Pydantic validation",
    ),

    # Vector Stores
    "chromadb": SDKEntry(
        NAME="chromadb",
        CATEGORY=SDKCategory.VECTOR_STORE,
        MODULE="chromadb",
        REQUIRED=True,
        DESCRIPTION="Local/embedded vector DB, fast prototyping",
    ),
    "qdrant-client": SDKEntry(
        NAME="qdrant-client",
        CATEGORY=SDKCategory.VECTOR_STORE,
        MODULE="qdrant_client",
        FALLBACK="chromadb",
        DESCRIPTION="Production vector DB, filtering, hybrid search",
    ),
    "pinecone": SDKEntry(
        NAME="pinecone",
        CATEGORY=SDKCategory.VECTOR_STORE,
        MODULE="pinecone",
        env_var="PINECONE_API_KEY",
        FALLBACK="chromadb",
        DESCRIPTION="Managed vector DB, serverless scaling",
    ),

    # Caching & State
    "redis": SDKEntry(
        NAME="redis",
        CATEGORY=SDKCategory.CACHE,
        MODULE="redis",
        REQUIRED=True,
        DESCRIPTION="Redis client, async support, clustering",
    ),
    "hiredis": SDKEntry(
        NAME="hiredis",
        CATEGORY=SDKCategory.CACHE,
        MODULE="hiredis",
        DESCRIPTION="C parser for Redis (10x faster parsing)",
    ),

    # Orchestration
    "langgraph": SDKEntry(
        NAME="langgraph",
        CATEGORY=SDKCategory.ORCHESTRATION,
        MODULE="langgraph",
        DESCRIPTION="Stateful agent graphs, cycles, checkpointing",
    ),
    "langchain-core": SDKEntry(
        NAME="langchain-core",
        CATEGORY=SDKCategory.ORCHESTRATION,
        MODULE="langchain_core",
        DESCRIPTION="Minimal abstractions (LCEL, runnables only)",
    ),

    # Observability
    "opentelemetry-api": SDKEntry(
        NAME="opentelemetry-api",
        CATEGORY=SDKCategory.OBSERVABILITY,
        MODULE="opentelemetry.trace",
        REQUIRED=True,
        DESCRIPTION="Tracing API (vendor-neutral)",
    ),
    "opentelemetry-sdk": SDKEntry(
        NAME="opentelemetry-sdk",
        CATEGORY=SDKCategory.OBSERVABILITY,
        MODULE="opentelemetry.sdk.trace",
        REQUIRED=True,
        DESCRIPTION="Tracing implementation",
    ),

    # Document Processing
    "unstructured": SDKEntry(
        NAME="unstructured",
        CATEGORY=SDKCategory.DOCUMENT,
        MODULE="unstructured",
        DESCRIPTION="Universal document parser (PDF, DOCX, HTML)",
    ),
    "pypdf": SDKEntry(
        NAME="pypdf",
        CATEGORY=SDKCategory.DOCUMENT,
        MODULE="pypdf",
        DESCRIPTION="Lightweight PDF text extraction",
    ),

    # MCP
    "mcp": SDKEntry(
        NAME="mcp",
        CATEGORY=SDKCategory.MCP,
        MODULE="mcp",
        DESCRIPTION="MCP SDK for building tool servers",
    ),
    "fastmcp": SDKEntry(
        NAME="fastmcp",
        CATEGORY=SDKCategory.MCP,
        MODULE="fastmcp",
        DESCRIPTION="FastAPI-style MCP server framework",
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

    ENTRY = SDK_REGISTRY[sdk_name]

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
    REPORT = {
        "total": len(SDK_REGISTRY),
        "available": 0,
        "missing": 0,
        "missing_keys": 0,
        "details": {},
    }

    for sdk_name, entry in SDK_REGISTRY.items():
        SUCCESS, ERROR = validate_sdk(sdk_name)

        STATUS = {
            "available": success,
            "required": entry.required,
            "category": entry.category.value,
            "error": error,
        }

        if success:
            REPORT["AVAILABLE"] += 1
        elif "not installed" in (error or ""):
            REPORT["MISSING"] += 1
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
    AVAILABLE = []
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
            SELF.DOCUMENTS = documents or []


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
            SELF.CONFIG = config or {}
            SELF.COLLECTIONS = {}

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
                SELF.COLLECTIONS[NAME] = []
            return MockCollection(self.collections[name])

    return MockVectorStore(config)

