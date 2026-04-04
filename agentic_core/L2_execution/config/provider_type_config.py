from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

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

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

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
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_default_module", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_default_module", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "get_default_module")
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
