"""
03_runtime/shared/sdk_registry.py
Complete Agentic SDK Registry & Auto-Configuration

ZERO-LOSS MERGE — 21 SDK SET
Provides centralized registry, lazy initialization, and validation for:
- LLM Providers (10): OpenAI, Anthropic, Google, Mistral, Cohere, Groq, Together, Fireworks, LiteLLM, Instructor
- Vector Stores (3): ChromaDB, Qdrant, Pinecone
- Caching (2): Redis, Hiredis
- Orchestration (2): LangGraph, LangChain-Core
- Observability (2): OpenTelemetry API, OpenTelemetry SDK
- Document Processing (2): Unstructured, PyPDF
- MCP (2): MCP SDK, FastMCP

Usage:
    from agentic_workflow.runtime.shared.sdk_registry import (
        SDKRegistry, get_vector_store, get_redis_client, get_mcp_server
    )

    # Get configured clients
    chroma = get_vector_store("chromadb")
    redis = get_redis_client()

    # Validate all SDKs
    validate_all_sdks()
"""

from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

# =============================================================================
# SDK CATEGORIES
# =============================================================================

class SDKCategory(str, Enum):
    """SDK category classification."""
    LLM_PROVIDER = "llm_provider"
    VECTOR_STORE = "vector_store"
    CACHE = "cache"
    ORCHESTRATION = "orchestration"
    OBSERVABILITY = "observability"
    DOCUMENT = "document"
    MCP = "mcp"

# =============================================================================
# SDK REGISTRY ENTRIES
# =============================================================================

@dataclass
class SDKEntry:
    """Registry entry for an SDK."""
    name: str
    package: str
    import_path: str
    category: SDKCategory
    env_key: Optional[str] = None
    description: str = ""
    async_support: bool = True
    mcp_compatible: bool = False

# Complete SDK registry
SDK_REGISTRY: Dict[str, SDKEntry] = {
    # LLM Providers
    "openai": SDKEntry(
        name="openai",
        package="openai",
        import_path="openai",
        category=SDKCategory.LLM_PROVIDER,
        env_key="OPENAI_API_KEY",
        description="GPT-4o, o1, embeddings, function calling",
        mcp_compatible=True,
    ),
    "anthropic": SDKEntry(
        name="anthropic",
        package="anthropic",
        import_path="anthropic",
        category=SDKCategory.LLM_PROVIDER,
        env_key="ANTHROPIC_API_KEY",
        description="Claude 3.5 Sonnet, tool use, extended context",
        mcp_compatible=True,
    ),
    "google": SDKEntry(
        name="google",
        package="google-generativeai",
        import_path="google.generativeai",
        category=SDKCategory.LLM_PROVIDER,
        env_key="GOOGLE_API_KEY",
        description="Gemini 2.0, multimodal, grounding",
    ),
    "mistral": SDKEntry(
        name="mistral",
        package="mistralai",
        import_path="mistralai",
        category=SDKCategory.LLM_PROVIDER,
        env_key="MISTRAL_API_KEY",
        description="Mistral Large, code generation, EU compliance",
    ),
    "cohere": SDKEntry(
        name="cohere",
        package="cohere",
        import_path="cohere",
        category=SDKCategory.LLM_PROVIDER,
        env_key="COHERE_API_KEY",
        description="Command R+, RAG, reranking, embeddings",
    ),
    "groq": SDKEntry(
        name="groq",
        package="groq",
        import_path="groq",
        category=SDKCategory.LLM_PROVIDER,
        env_key="GROQ_API_KEY",
        description="Ultra-fast inference (Llama, Mixtral on LPU)",
    ),
    "together": SDKEntry(
        name="together",
        package="together",
        import_path="together",
        category=SDKCategory.LLM_PROVIDER,
        env_key="TOGETHER_API_KEY",
        description="Cheap diversified access (Llama, Mixtral, Mythomax)",
    ),
    "fireworks": SDKEntry(
        name="fireworks",
        package="fireworks-ai",
        import_path="fireworks",
        category=SDKCategory.LLM_PROVIDER,
        env_key="FIREWORKS_API_KEY",
        description="Strong tool-calling alternative",
    ),
    "litellm": SDKEntry(
        name="litellm",
        package="litellm",
        import_path="litellm",
        category=SDKCategory.LLM_PROVIDER,
        description="Unified router, fallbacks, 100+ provider support",
    ),
    "instructor": SDKEntry(
        name="instructor",
        package="instructor",
        import_path="instructor",
        category=SDKCategory.LLM_PROVIDER,
        description="Structured outputs, Pydantic validation",
    ),
    # Vector Stores
    "chromadb": SDKEntry(
        name="chromadb",
        package="chromadb",
        import_path="chromadb",
        category=SDKCategory.VECTOR_STORE,
        description="Local/embedded vector DB, fast prototyping",
        mcp_compatible=True,
    ),
    "qdrant": SDKEntry(
        name="qdrant",
        package="qdrant-client",
        import_path="qdrant_client",
        category=SDKCategory.VECTOR_STORE,
        env_key="QDRANT_API_KEY",
        description="Production vector DB, filtering, hybrid search",
        mcp_compatible=True,
    ),
    "pinecone": SDKEntry(
        name="pinecone",
        package="pinecone",
        import_path="pinecone",
        category=SDKCategory.VECTOR_STORE,
        env_key="PINECONE_API_KEY",
        description="Managed vector DB, serverless scaling",
    ),
    # Caching
    "redis": SDKEntry(
        name="redis",
        package="redis",
        import_path="redis",
        category=SDKCategory.CACHE,
        env_key="REDIS_URL",
        description="Session cache, rate limiting, pub/sub",
        mcp_compatible=True,
    ),
    "hiredis": SDKEntry(
        name="hiredis",
        package="hiredis",
        import_path="hiredis",
        category=SDKCategory.CACHE,
        description="C parser for Redis (10x faster)",
        async_support=False,
    ),
    # Orchestration
    "langgraph": SDKEntry(
        name="langgraph",
        package="langgraph",
        import_path="langgraph",
        category=SDKCategory.ORCHESTRATION,
        description="Stateful agent graphs, cycles, checkpointing",
    ),
    "langchain_core": SDKEntry(
        name="langchain_core",
        package="langchain-core",
        import_path="langchain_core",
        category=SDKCategory.ORCHESTRATION,
        description="Minimal abstractions (LCEL, runnables)",
    ),
    # Observability
    "opentelemetry": SDKEntry(
        name="opentelemetry",
        package="opentelemetry-api",
        import_path="opentelemetry",
        category=SDKCategory.OBSERVABILITY,
        description="Distributed tracing API",
    ),
    "opentelemetry_sdk": SDKEntry(
        name="opentelemetry_sdk",
        package="opentelemetry-sdk",
        import_path="opentelemetry.sdk",
        category=SDKCategory.OBSERVABILITY,
        description="Tracing implementation",
    ),
    # Document Processing
    "unstructured": SDKEntry(
        name="unstructured",
        package="unstructured",
        import_path="unstructured",
        category=SDKCategory.DOCUMENT,
        description="Universal document parser (PDF, DOCX, HTML)",
        async_support=False,
    ),
    "pypdf": SDKEntry(
        name="pypdf",
        package="pypdf",
        import_path="pypdf",
        category=SDKCategory.DOCUMENT,
        description="Lightweight PDF text extraction",
        async_support=False,
    ),
    # MCP
    "mcp": SDKEntry(
        name="mcp",
        package="mcp",
        import_path="mcp",
        category=SDKCategory.MCP,
        description="MCP SDK for building tool servers",
        mcp_compatible=True,
    ),
    "fastmcp": SDKEntry(
        name="fastmcp",
        package="fastmcp",
        import_path="fastmcp",
        category=SDKCategory.MCP,
        description="FastAPI-style MCP server framework",
        mcp_compatible=True,
    ),
}

# =============================================================================
# VALIDATION
# =============================================================================

def validate_sdk(name: str) -> tuple[bool, Optional[str]]:
    """
    Validate that an SDK is installed and importable.

    Returns:
        Tuple of (success, error_message)
    """
    entry = SDK_REGISTRY.get(name)
    if not entry:
        return False, f"Unknown SDK: {name}"

    try:
        __import__(entry.import_path)
        return True, None
    except ImportError as e:
        return False, str(e)

def validate_all_sdks() -> Dict[str, tuple[bool, Optional[str]]]:
    """
    Validate all registered SDKs.

    Returns:
        Dict mapping SDK name to (success, error_message)
    """
    results = {}
    success_count = 0

    for name in SDK_REGISTRY:
        success, error = validate_sdk(name)
        results[name] = (success, error)
        if success:
            success_count += 1

        else:
            error_count += 1

    return results

def get_available_sdks(category: Optional[SDKCategory] = None) -> List[str]:
    """Get list of available (installed) SDKs, optionally filtered by category."""
    available = []
    for name, entry in SDK_REGISTRY.items():
        if category and entry.category != category:
            continue
        success, _ = validate_sdk(name)
        if success:
            available.append(name)
    return available

# =============================================================================
# VECTOR STORE CLIENTS
# =============================================================================

_vector_clients: Dict[str, object] = {}
_lock = threading.Lock()

@dataclass
class ChromaConfig:
    """ChromaDB configuration."""
    persist_directory: Optional[str] = None
    collection_name: str = "default"
    embedding_function: Optional[Any] = None

@dataclass
class QdrantConfig:
    """Qdrant configuration."""
    url: Optional[str] = None
    api_key: Optional[str] = None
    host: str = "localhost"
    port: int = 6333
    prefer_grpc: bool = True

@dataclass
class PineconeConfig:
    """Pinecone configuration."""
    api_key: Optional[str] = None
    environment: Optional[str] = None
    index_name: str = "default"

def get_vector_store(
    provider: str,
    config: Optional[Union[ChromaConfig, QdrantConfig, PineconeConfig]] = None,
) -> object:
    """
    Get a configured vector store client.

    Args:
        provider: One of "chromadb", "qdrant", "pinecone"
        config: Provider-specific configuration

    Returns:
        Configured vector store client
    """
    if provider in _vector_clients:
        return _vector_clients[provider]

    with _lock:
        if provider in _vector_clients:
            return _vector_clients[provider]

        if provider == "chromadb":
            import chromadb
            cfg = config or ChromaConfig()
            if cfg.persist_directory:
                client = chromadb.PersistentClient(path=cfg.persist_directory)
            else:
                client = chromadb.Client()
            logger.info(f"Initialized ChromaDB client (persist={cfg.persist_directory})")
            _vector_clients[provider] = client
            return client

        elif provider == "qdrant":
            from qdrant_client import QdrantClient
            cfg = config or QdrantConfig()
            api_key = cfg.api_key or os.environ.get("QDRANT_API_KEY")
            url = cfg.url or os.environ.get("QDRANT_URL")

            if url:
                client = QdrantClient(url=url, api_key=api_key, prefer_grpc=cfg.prefer_grpc)
            else:
                client = QdrantClient(host=cfg.host, port=cfg.port, prefer_grpc=cfg.prefer_grpc)

            logger.info(f"Initialized Qdrant client (url={url or f'{cfg.host}:{cfg.port}'})")
            _vector_clients[provider] = client
            return client

        elif provider == "pinecone":
            from pinecone import Pinecone
            cfg = config or PineconeConfig()
            api_key = cfg.api_key or os.environ.get("PINECONE_API_KEY")

            if not api_key:
                raise ValueError("PINECONE_API_KEY environment variable is not set")

            client = Pinecone(api_key=api_key)
            logger.info("Initialized Pinecone client")
            _vector_clients[provider] = client
            return client

        else:
            raise ValueError(f"Unknown vector store provider: {provider}")

# =============================================================================
# REDIS CLIENT
# =============================================================================

_redis_client: Optional[Any] = None
_redis_async_client: Optional[Any] = None

@dataclass
class RedisConfig:
    """Redis configuration."""
    url: Optional[str] = None
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    decode_responses: bool = True
    socket_timeout: float = 5.0
    retry_on_timeout: bool = True

def get_redis_client(config: Optional[RedisConfig] = None, async_client: bool = False) -> object:
    """
    Get a configured Redis client.

    Args:
        config: Redis configuration
        async_client: If True, return async Redis client

    Returns:
        Configured Redis client
    """
    global _redis_client, _redis_async_client

    if async_client:
        if _redis_async_client is not None:
            return _redis_async_client
    else:
        if _redis_client is not None:
            return _redis_client

    with _lock:
        # import archives.legacy_resume_gen.Older Microservices Models.v10.6.redis  # Commented out due to invalid syntax

        cfg = config or RedisConfig()
        url = cfg.url or os.environ.get("REDIS_URL")

        if async_client:
            if _redis_async_client is not None:
                return _redis_async_client

            if url:
                client = redis.asyncio.from_url(
                    url,
                    decode_responses=cfg.decode_responses,
                    socket_timeout=cfg.socket_timeout,
                    retry_on_timeout=cfg.retry_on_timeout,
                )
            else:
                client = redis.asyncio.Redis(
                    host=cfg.host,
                    port=cfg.port,
                    db=cfg.db,
                    password=cfg.password or os.environ.get("REDIS_PASSWORD"),
                    decode_responses=cfg.decode_responses,
                    socket_timeout=cfg.socket_timeout,
                    retry_on_timeout=cfg.retry_on_timeout,
                )
            _redis_async_client = client
            logger.info(f"Initialized async Redis client (url={url or f'{cfg.host}:{cfg.port}'})")
            return client
        else:
            if _redis_client is not None:
                return _redis_client

            if url:
                client = redis.from_url(
                    url,
                    decode_responses=cfg.decode_responses,
                    socket_timeout=cfg.socket_timeout,
                    retry_on_timeout=cfg.retry_on_timeout,
                )
            else:
                client = redis.Redis(
                    host=cfg.host,
                    port=cfg.port,
                    db=cfg.db,
                    password=cfg.password or os.environ.get("REDIS_PASSWORD"),
                    decode_responses=cfg.decode_responses,
                    socket_timeout=cfg.socket_timeout,
                    retry_on_timeout=cfg.retry_on_timeout,
                )
            _redis_client = client
            logger.info(f"Initialized Redis client (url={url or f'{cfg.host}:{cfg.port}'})")
            return client

# =============================================================================
# OPENTELEMETRY TRACING
# =============================================================================

@dataclass
class TracingConfig:
    """OpenTelemetry tracing configuration."""
    service_name: str = "agentic-workflow"
    exporter: str = "console"  # "console", "otlp", "jaeger"
    otlp_endpoint: Optional[str] = None
    sample_rate: float = 1.0

_tracer_provider: Optional[Any] = None

def setup_tracing(config: Optional[TracingConfig] = None) -> object:
    """
    Set up OpenTelemetry tracing.

    Args:
        config: Tracing configuration

    Returns:
        Configured TracerProvider
    """
    global _tracer_provider

    if _tracer_provider is not None:
        return _tracer_provider

    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.resources import Resource

    cfg = config or TracingConfig()

    resource = Resource.create({"provider.name": cfg.service_name})
    provider = TracerProvider(resource=resource)

    if cfg.exporter == "console":
        exporter = ConsoleSpanExporter()
    elif cfg.exporter == "otlp":
        from observability.logic.tracing.console_trace_exporter import OTLPSpanExporter
        endpoint = cfg.otlp_endpoint or os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
        exporter = OTLPSpanExporter(endpoint=endpoint)
    else:
        exporter = ConsoleSpanExporter()

    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    _tracer_provider = provider
    logger.info(f"Initialized OpenTelemetry tracing (provider={cfg.service_name}, exporter={cfg.exporter})")
    return provider

def get_tracer(name: str = "agentic-workflow") -> object:
    """Get a tracer instance."""
    from opentelemetry import trace
    return trace.get_tracer(name)

# =============================================================================
# MCP SERVER builder
# =============================================================================

@dataclass
class MCPServerConfig:
    """MCP server configuration."""
    name: str = "agentic-workflow-mcp"
    version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8000

def create_mcp_server(config: Optional[MCPServerConfig] = None) -> object:
    """
    Create a FastMCP server instance.

    Args:
        config: MCP server configuration

    Returns:
        Configured FastMCP server

    Example:
        from agentic_workflow.runtime.shared.sdk_registry import create_mcp_server

        mcp = create_mcp_server()

        @mcp.tool()
        def search_documents(query: str) -> list[str]:
            '''Search documents by query.'''
            return ["doc1", "doc2"]

        @mcp.resource("config://settings")
        def get_settings() -> dict:
            return {"theme": "dark"}
    """
    from fastmcp import FastMCP

    cfg = config or MCPServerConfig()
    server = FastMCP(name=cfg.name, version=cfg.version)

    logger.info(f"Created MCP server (name={cfg.name}, version={cfg.version})")
    return server

def create_mcp_tool_from_function(
    func: Callable,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Dict[str, object]:
    """
    Create an MCP tool definition from a Python function.

    Args:
        func: The function to wrap as an MCP tool
        name: Optional tool name (defaults to function name)
        description: Optional description (defaults to docstring)

    Returns:
        MCP tool definition dict
    """
    import agentic_core.L1_cognition.P2_inspect.detect_anomalies_update.inspect
    from typing import get_type_hints

    tool_name = name or func.__name__
    tool_desc = description or (func.__doc__ or "").strip().split("\n")[0]

    hints = get_type_hints(func)
    sig = inspect.signature(func)

    properties = {}
    required = []

    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue

        param_type = hints.get(param_name, str)
        json_type = "string"
        if param_type is int:
            json_type = "integer"
        elif param_type is float:
            json_type = "number"
        elif param_type is bool:
            json_type = "boolean"
        elif param_type is list:
            json_type = "array"
        elif param_type is dict:
            json_type = "object"

        properties[param_name] = {"type": json_type}

        if param.default == inspect.Parameter.empty:
            required.append(param_name)

    return {
        "name": tool_name,
        "description": tool_desc,
        "inputSchema": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }

# =============================================================================
# DOCUMENT PROCESSING
# =============================================================================

def parse_document(file_path: str, strategy: str = "auto") -> List[Dict[str, object]]:
    """
    Parse a document using unstructured.

    Args:
        file_path: Path to the document
        strategy: Parsing strategy ("auto", "fast", "hi_res", "ocr_only")

    Returns:
        List of parsed elements with text and metadata
    """
    from unstructured.partition.auto import partition

    elements = partition(filename=file_path, strategy=strategy)

    return [
        {
            "text": str(el),
            "type": type(el).__name__,
            "metadata": el.metadata.to_dict() if hasattr(el, "metadata") else {},
        }
        for el in elements
    ]

def extract_pdf_text(file_path: str) -> str:
    """
    Extract text from a PDF using pypdf.

    Args:
        file_path: Path to the PDF file

    Returns:
        Extracted text content
    """
    from pypdf import PdfReader

    reader = PdfReader(file_path)
    text_parts = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)

    return "\n\n".join(text_parts)

# =============================================================================
# RESET UTILITIES
# =============================================================================

def reset_all_clients() -> None:
    """Reset all singleton clients. Useful for testing."""
    global _vector_clients, _redis_client, _redis_async_client, _tracer_provider

    with _lock:
        _vector_clients.clear()
        _redis_client = None
        _redis_async_client = None
        _tracer_provider = None
        logger.debug("Reset all SDK clients")

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "SDKCategory",
    # Registry
    "SDKEntry",
    "SDK_REGISTRY",
    # Validation
    "validate_sdk",
    "validate_all_sdks",
    "get_available_sdks",
    # Vector Stores
    "ChromaConfig",
    "QdrantConfig",
    "PineconeConfig",
    "get_vector_store",
    # Redis
    "RedisConfig",
    "get_redis_client",
    # Tracing
    "TracingConfig",
    "setup_tracing",
    "get_tracer",
    # MCP
    "MCPServerConfig",
    "create_mcp_server",
    "create_mcp_tool_from_function",
    # Document Processing
    "parse_document",
    "extract_pdf_text",
    # Utilities
    "reset_all_clients",
]
