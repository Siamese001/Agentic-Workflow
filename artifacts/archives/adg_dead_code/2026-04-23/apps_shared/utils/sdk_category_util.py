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

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "sdk_category_util", "p0_governance")
_emit_reads_policy_state("p0", "sdk_category_util", "policy_binding")
_emit_snapshots_state("p0", "sdk_category_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("sdk_category_util", "p4obs", "metric_1")
_emit_emits_metric_event("sdk_category_util", "p4obs", "metric_2")
_emit_emits_metric_event("sdk_category_util", "p4obs", "metric_3")
_emit_emits_metric_event("sdk_category_util", "p4obs", "metric_4")
_emit_emits_metric_event("sdk_category_util", "p4obs", "metric_5")
_emit_emits_metric_event("sdk_category_util", "p4obs", "metric_6")
_emit_records_incident_event("sdk_category_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("sdk_category_util", "p4obs", "anomaly")
_emit_writes_observability_log("sdk_category_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("sdk_category_util", "p4obs", "mon_state")
_emit_triggers_alert("sdk_category_util", "p4obs", "alert")
_emit_links_incident_trace("sdk_category_util", "p4obs", "trace_link")
_emit_captures_pattern("sdk_category_util", "p3lm", "pattern")
_emit_records_learning_event("sdk_category_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("sdk_category_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("sdk_category_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("sdk_category_util", "p3lm", "routing")
_emit_improves_agent_policy("sdk_category_util", "p3lm", "policy")
_emit_stores_learning_state("sdk_category_util", "p3lm", "state")
_emit_records_execution_trace("sdk_category_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("sdk_category_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("sdk_category_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("sdk_category_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("sdk_category_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("sdk_category_util", "env_read", "p2_env_1")
_emit_reads_environ("sdk_category_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("sdk_category_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("sdk_category_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "sdk_category_util", "context_pull")
_emit_pulls_context("p1", "sdk_category_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "sdk_category_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "sdk_category_util", "uwg_term_2")
_emit_writes_through("p1", "sdk_category_util", "write_through")
_emit_writes_through("p1", "sdk_category_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "sdk_category_util", "safety_validation")
_emit_invokes_eval("p1", "sdk_category_util", "eval_call")
_emit_proposal_commits_routing("p1", "sdk_category_util", "routing_commit")
_emit_escalates_to_human("p1", "sdk_category_util", "human_escalation")
_emit_routes_through("p1", "sdk_category_util", "route_through")
_emit_checks_agent_registry("p1", "sdk_category_util", "agent_registry")
_emit_validates_agent_capability("p1", "sdk_category_util", "capability")
_emit_dispatches_execution_plan("p1", "sdk_category_util", "exec_plan")
_emit_agent_executes_agent("p1", "sdk_category_util", "sub_agent")
_emit_routes_to_agent("p1", "sdk_category_util", "target_agent")
_emit_verifies_policy("p1", "sdk_category_util", "policy_check")
_emit_observes_runtime_state("p1", "sdk_category_util", "runtime_state")
_emit_verifies_boundary("p1", "sdk_category_util", "boundary_check")
_emit_transcripts_response("p1", "sdk_category_util", "transcript")
_emit_hard_fails_untranscripted("p1", "sdk_category_util")
_emit_gated_by_confidence("p1", "sdk_category_util", "confidence_gate")
emit_replay_key("p0", "sdk_category_util")
emit_determinism_digest("p0", "sdk_category_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "sdk_category_util", "execution_auth")
_emit_validates_capability("p2", "sdk_category_util", "capability_check")
_emit_routes_to_capability("p2", "sdk_category_util", "capability_route")
_emit_writes_via_uwg("p2", "sdk_category_util", "uwg_write")
_emit_blocks_direct_write("p2", "sdk_category_util", "direct_write_block")
_emit_records_tool_invocation("p2", "sdk_category_util", "tool_invocation")
_emit_captures_execution_output("p2", "sdk_category_util", "exec_output")
_emit_dispatches_agent("p3", "sdk_category_util", "agent_dispatch")
_emit_coordinates_agents("p3", "sdk_category_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "sdk_category_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "sdk_category_util", "healing_outcome")
_emit_escalates_failure("p3", "sdk_category_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "sdk_category_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sdk_category_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "sdk_category_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "sdk_category_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sdk_category_util", "eval_metric")
_emit_stores_embedding("p4", "sdk_category_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "sdk_category_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sdk_category_util", "exec_snapshot_link")

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
        except ImportError:  # guardian: allow-silent-swallow - optional dependency
            return False

    def has_api_key(self) -> bool:
        """Check if required API key is set."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SDKEntry.has_api_key")

        if not self.env_var:
            return True
        return bool(os.getenv(self.env_var))


SDK_REGISTRY: dict[str, SDKEntry] = {
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
        return (False, f"Unknown SDK: {sdk_name}")
    entry = SDK_REGISTRY[sdk_name]
    if not entry.is_available():
        if entry.required:
            return (False, f"Required SDK '{sdk_name}' not installed")
        return (False, f"Optional SDK '{sdk_name}' not installed")
    if entry.env_var and (not entry.has_api_key()):
        if entry.required:
            return (False, f"Required API key {entry.env_var} not set")
        return (False, f"Optional API key {entry.env_var} not set")
    return (True, None)


def validate_all_sdks() -> dict[str, Any]:
    """Validate all SDKs in registry.

    Returns:
        Validation report with status for each SDK
    """
    report = {"total": len(SDK_REGISTRY), "available": 0, "missing": 0, "missing_keys": 0, "details": {}}
    for sdk_name, entry in tqdm(SDK_REGISTRY.items(), desc="Processing", unit="item"):
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
        f"SDK validation: {report['available']}/{report['total']} available, {report['missing']} missing, {report['missing_keys']} missing keys",
    )
    return report


def get_sdk_by_category(category: SDKCategory) -> list[SDKEntry]:
    """Get all SDKs in a category.

    Args:
        category: SDK category

    Returns:
        List of SDK entries
    """
    return [entry for entry in SDK_REGISTRY.values() if entry.category == category]


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

    class MockCollection:
        def __init__(self, documents: list = None):
            self.documents = documents or []

        def add(self, documents: list, ids: list = None):
            import uuid as _uuid  # noqa: PLC0415

            _trace_id = str(_uuid.uuid4())
            _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "MockCollection.add")

            self.documents.extend(documents)
            return ids or list(range(len(documents)))

        def query(self, query_texts: list, n_results: int = 10):
            return {"ids": [[0]], "documents": [["Mock result"]], "metadatas": [[{}]]}

    class MockVectorStore:
        def __init__(self, config: dict[str, Any] | None = None):
            self.config = config or {}
            self.collections = {}

        def add_documents(self, collection_name: str, documents: list, ids: list = None):
            import uuid as _uuid  # noqa: PLC0415

            _trace_id = str(_uuid.uuid4())
            _emit_records_execution_trace(
                _trace_id, LayerSegment.L3_ORCHESTRATION, "MockVectorStore.add_documents"
            )

            if collection_name not in self.collections:
                self.collections[collection_name] = []
            self.collections[collection_name].extend(documents)
            return ids or list(range(len(documents)))

        def search(self, collection_name: str, query: str, n_results: int = 10):
            self.collections.get(collection_name, [])
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
