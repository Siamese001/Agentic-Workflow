"""Runtime Shared Module - SDK Integration Layer.

Provides unified access to all agentic SDKs with lazy loading,
singleton pattern, and graceful fallbacks.

Phase 1C - SDK Integration Layer
"""

# SDK Registry
from .sdk_registry import (
    SDK_REGISTRY,
    SDKCategory,
    SDKEntry,
    get_available_sdks,
    get_sdk_by_category,
    reset_all_clients,
    validate_all_sdks,
    validate_sdk,
)

# Multi-Provider LLM Clients
from .multi_provider_clients import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_MODELS,
    Provider,
    ProviderConfig,
    get_api_key,
    get_client,
    get_default_model,
    get_instructor_client,
    get_litellm_completion,
    reset_all_clients as reset_llm_clients,
)

# Vector Store Clients
from .vector_store_clients import (
    ChromaConfig,
    PineconeConfig,
    QdrantConfig,
    VectorStoreProvider,
    create_chroma_collection,
    create_qdrant_collection,
    get_vector_store,
    reset_all_vector_stores,
    search_vectors_chroma,
    search_vectors_qdrant,
    upsert_vectors_chroma,
    upsert_vectors_qdrant,
)

# Cache Clients
from .cache_clients import (
    RedisConfig,
    cache_clear_pattern,
    cache_delete,
    cache_exists,
    cache_get,
    cache_get_many,
    cache_set,
    cache_set_many,
    get_redis_client,
    reset_redis_client,
)

# Observability Clients
from .observability_clients import (
    TracingConfig,
    add_span_event,
    create_span,
    get_structured_logger,
    get_tracer,
    record_exception,
    set_span_attribute,
    setup_structured_logging,
    setup_tracing,
    shutdown_tracing,
)

# Agent Executor
from .agent_executor import (
    AgentConfig,
    AgentExecutor,
    AgentMessage,
    AgentResponse,
    create_agent_executor,
)

# Workflow Integration
from .workflow_integration import (
    HopExecutionContext,
    WorkflowContext,
    WorkflowOrchestrator,
    create_workflow_context,
    create_workflow_orchestrator,
    execute_hop_with_agent,
)

# K.X Nodes (Knowledge Extraction)
from .kx_nodes import (
    DecodingParams,
    KNodeConfig,
    KNodeType,
    KXNodeRegistry,
    RAGConfig,
    ReasoningStrategy,
    OUTREACH_CONNECTION_REQ_NODES,
    OUTREACH_KX_NODES,
    RESUME_KX_NODES,
    get_kx_registry,
    get_outreach_kx_node,
    get_resume_kx_node,
)

# K.X Node Executor
from .kx_executor import (
    KXExecutionContext,
    KXExecutionResult,
    KXNodeExecutor,
    execute_kx_node,
)

# Uber High Signal Agents
from .architecture_visualizer_agent import (
    ArchitectureVisualizerAgent,
    DiagramType,
    DiagramNode,
    DiagramArtifact,
)
from .cultural_decoder_agent import (
    CulturalDecoderAgent,
    CompanyDNA,
    CulturallyAlignedContent,
)
from .pre_mortem_agent import (
    PreMortemAgent,
    RiskCategory,
    ImpactLevel,
    FailureMode,
    PreMortemReport,
)

# Phase 1 Precision Layer Components
from .contextual_compressor import (
    ContextualCompressor,
    CompressionResult,
    compress_chunks,
)
from .adaptive_retrieval_gate import (
    AdaptiveRetrievalGate,
    RetrievalDecision,
    should_retrieve,
)

# Phase 2 Reasoning Layer Components
from .query_decomposer import (
    QueryDecomposer,
    DecomposedQuery,
    decompose_query,
)

__all__ = [
    # SDK Registry
    "SDK_REGISTRY",
    "SDKCategory",
    "SDKEntry",
    "validate_sdk",
    "validate_all_sdks",
    "get_sdk_by_category",
    "get_available_sdks",
    "reset_all_clients",
    # LLM Clients
    "Provider",
    "ProviderConfig",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_MODELS",
    "get_api_key",
    "get_client",
    "get_default_model",
    "get_litellm_completion",
    "get_instructor_client",
    "reset_llm_clients",
    # Vector Stores
    "VectorStoreProvider",
    "ChromaConfig",
    "QdrantConfig",
    "PineconeConfig",
    "get_vector_store",
    "create_chroma_collection",
    "create_qdrant_collection",
    "upsert_vectors_chroma",
    "upsert_vectors_qdrant",
    "search_vectors_chroma",
    "search_vectors_qdrant",
    "reset_all_vector_stores",
    # Cache
    "RedisConfig",
    "get_redis_client",
    "cache_get",
    "cache_set",
    "cache_delete",
    "cache_exists",
    "cache_get_many",
    "cache_set_many",
    "cache_clear_pattern",
    "reset_redis_client",
    # Observability
    "TracingConfig",
    "setup_tracing",
    "get_tracer",
    "create_span",
    "add_span_event",
    "set_span_attribute",
    "record_exception",
    "setup_structured_logging",
    "get_structured_logger",
    "shutdown_tracing",
    # Agent Executor
    "AgentConfig",
    "AgentExecutor",
    "AgentMessage",
    "AgentResponse",
    "create_agent_executor",
    # Workflow Integration
    "WorkflowContext",
    "HopExecutionContext",
    "WorkflowOrchestrator",
    "create_workflow_context",
    "create_workflow_orchestrator",
    "execute_hop_with_agent",
    # K.X Nodes
    "KNodeType",
    "ReasoningStrategy",
    "RAGConfig",
    "DecodingParams",
    "KNodeConfig",
    "KXNodeRegistry",
    "RESUME_KX_NODES",
    "OUTREACH_KX_NODES",
    "OUTREACH_CONNECTION_REQ_NODES",
    "get_kx_registry",
    "get_resume_kx_node",
    "get_outreach_kx_node",
    # K.X Executor
    "KXExecutionContext",
    "KXExecutionResult",
    "KXNodeExecutor",
    "execute_kx_node",
    # Uber High Signal Agents
    "ArchitectureVisualizerAgent",
    "CulturalDecoderAgent",
    "PreMortemAgent",
    "DiagramType",
    "DiagramNode",
    "DiagramArtifact",
    "CompanyDNA",
    "CulturallyAlignedContent",
    "RiskCategory",
    "ImpactLevel",
    "FailureMode",
    "PreMortemReport",
    # Phase 1 Precision Layer
    "ContextualCompressor",
    "CompressionResult",
    "compress_chunks",
    "AdaptiveRetrievalGate",
    "RetrievalDecision",
    "should_retrieve",
    # Phase 2 Reasoning Layer
    "QueryDecomposer",
    "DecomposedQuery",
    "decompose_query",
]
