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

"\nSovereign MCP Registry – Phase 13 (Dec 26, 2025)\nCanonical SSOT for all MCP server configurations across L0-L6.\n\nThis registry enforces:\n- Layer-specific MCP assignments (L0-L6)\n- Mode validation (local, remote, mocked)\n- Capability tracking for sovereignty alignment\n- Constitutional compliance for all integrations\n"
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from agentic_core.config.core.sovereign_config import get_sovereign_config
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

class McpServerMode(str, Enum):
    """Deployment mode for MCP servers."""

    LOCAL: Any = "local"
    "Local execution via npx or binary"
    REMOTE: Any = "remote"
    "Remote API endpoint"
    MOCKED: Any = "mocked"
    "Mock implementation for testing"


class McpServerConfig(BaseModel):
    """Configuration for a single MCP server integration."""

    name: str = Field(..., description="Unique MCP server identifier")
    target_layer: str = Field(..., description="Primary L0-L6 layer assignment")
    mode: McpServerMode = Field(default=McpServerMode.LOCAL, description="Deployment mode")
    capabilities: list[str] = Field(default_factory=list, description="Sovereign capabilities provided")
    command: str = Field(..., description="Execution command (npx, python, etc.)")
    args: list[str] = Field(default_factory=list, description="Command arguments")
    env: dict[str, str] = Field(default_factory=dict, description="Environment variables")
    description: str | None = Field(None, description="Human-readable purpose")
    sovereignty_impact: str | None = Field(None, description="Impact on system sovereignty")


_BASE_MCP_REGISTRY: dict[str, McpServerConfig] = {
    "pinecone": McpServerConfig(
        name="pinecone",
        target_layer="L4",
        mode=McpServerMode.LOCAL,
        capabilities=["semantic_memory", "reranking", "inference"],
        command="npx",
        args=["-y", "@pinecone-database/mcp-server"],
        description="Vector database for semantic memory and reranking",
        sovereignty_impact="HIGH - Replaces custom Pinecone wrapper, enables inference",
    ),
    "sequential_thinking": McpServerConfig(
        name="sequential_thinking",
        target_layer="L1",
        mode=McpServerMode.LOCAL,
        capabilities=["hypothesis_branching", "logic_pruning", "dynamic_reasoning"],
        command="npx",
        args=["-y", "@modelcontextprotocol/server-sequential-thinking"],
        description="Dynamic reasoning chains with hypothesis management",
        sovereignty_impact="CRITICAL - Enhances L1 cognition with structured reasoning",
    ),
    "brave_search": McpServerConfig(
        name="brave_search",
        target_layer="L2",
        mode=McpServerMode.LOCAL,
        capabilities=["web_search", "real_time_data"],
        command="npx",
        args=["-y", "@modelcontextprotocol/server-brave-search"],
        env={"BRAVE_API_KEY": ""},
        description="Real-time web search for L2 tool execution",
        sovereignty_impact="MEDIUM - Enables external knowledge retrieval",
    ),
    "playwright": McpServerConfig(
        name="playwright",
        target_layer="L2",
        mode=McpServerMode.LOCAL,
        capabilities=["browser_automation", "ui_testing", "screenshot"],
        command="npx",
        args=["-y", "@modelcontextprotocol/server-playwright"],
        description="Browser automation for UI testing and validation",
        sovereignty_impact="MEDIUM - Enables automated UI verification",
    ),
    "memory": McpServerConfig(
        name="memory",
        target_layer="L4",
        mode=McpServerMode.LOCAL,
        capabilities=["knowledge_graph", "entity_persistence", "relation_tracking"],
        command="npx",
        args=["-y", "@modelcontextprotocol/server-memory"],
        description="Knowledge graph for entity and relation persistence",
        sovereignty_impact="HIGH - Structured memory beyond vector embeddings",
    ),
    "deepwiki": McpServerConfig(
        name="deepwiki",
        target_layer="L6",
        mode=McpServerMode.LOCAL,
        capabilities=["codebase_documentation", "repo_analysis"],
        command="npx",
        args=["-y", "@modelcontextprotocol/server-deepwiki"],
        description="Codebase documentation and analysis for observability",
        sovereignty_impact="MEDIUM - Enhances L6 audit trail with repo insights",
    ),
    "fetch": McpServerConfig(
        name="fetch",
        target_layer="L2",
        mode=McpServerMode.LOCAL,
        capabilities=["content_ingestion", "url_fetch", "youtube_transcript"],
        command="npx",
        args=["-y", "@modelcontextprotocol/server-fetch"],
        description="Content ingestion from URLs and YouTube",
        sovereignty_impact="LOW - Utility for content retrieval",
    ),
    "figma": McpServerConfig(
        name="figma",
        target_layer="L2",
        mode=McpServerMode.LOCAL,
        capabilities=["design_to_code", "ui_generation"],
        command="npx",
        args=["-y", "@modelcontextprotocol/server-figma"],
        env={"FIGMA_ACCESS_TOKEN": ""},
        description="Design-to-code generation from Figma",
        sovereignty_impact="LOW - Specialized use case for UI generation",
    ),
}


def get_mcp_registry() -> dict[str, McpServerConfig]:
    """Get the full MCP registry with conditional entries."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_mcp_registry", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_mcp_registry", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "get_mcp_registry")
    config = get_sovereign_config()
    registry = _BASE_MCP_REGISTRY.copy()
    if config.REDIS_MCP_ENABLED:
        registry["redis"] = McpServerConfig(
            name="redis",
            target_layer="L4",
            mode=McpServerMode.LOCAL,
            capabilities=["caching", "state_management", "session_storage"],
            command="npx",
            args=["-y", "@modelcontextprotocol/server-redis"],
            env={"REDIS_URL": config.redis_url},
            description="Redis caching and state management via MCP",
            sovereignty_impact="HIGH - Provides sovereign caching with MCP integration",
        )
    return registry


SOVEREIGN_MCP_REGISTRY = get_mcp_registry()


def get_mcps_by_layer(layer: str) -> list[McpServerConfig]:
    """Get all MCP servers assigned to a specific layer."""
    return [mcp for mcp in get_mcp_registry().values() if mcp.target_layer == layer]


def get_mcp_by_capability(capability: str) -> list[McpServerConfig]:
    """Find MCP servers providing a specific capability."""
    return [mcp for mcp in get_mcp_registry().values() if capability in mcp.capabilities]


VALID_LAYERS: Any = {"L0", "L1", "L2", "L3", "L4", "L5", "L6"}


def validate_mcp_registry() -> list[str]:
    """Validate MCP registry for constitutional compliance."""
    violations: Any = []
    for name, config in get_mcp_registry().items():
        if config.target_layer not in VALID_LAYERS:
            violations.append(f"MCP '{name}' has invalid layer: {config.target_layer}")
        if not config.command:
            violations.append(f"MCP '{name}' Missing command")
    return violations


_violations = validate_mcp_registry()
if _violations:
    import warnings

    for Violation in _violations:
        warnings.warn(f"MCP Registry Violation: {Violation}", stacklevel=2)
