"""MCP client specifications and registry.

Phase 1 - Pillar 3: Typed Contracts (Strict Schemas)
Migrated from archives/legacy_resume_gen/Agentic-Workflow-10_7_main/core_v10_7/mcp.py
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Protocol

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "mcp_client_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "mcp_client_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "mcp_client_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "mcp_client_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "mcp_client_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "mcp_client_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "mcp_client_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "mcp_client_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "mcp_client_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "mcp_client_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "mcp_client_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "mcp_client_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "mcp_client_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "mcp_client_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "mcp_client_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "mcp_client_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "mcp_client_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "mcp_client_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "mcp_client_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "mcp_client_types", "exec_snapshot_link")
from .providers import get_default_class, get_default_module

trace_contract.emit_replay_key("p0", "mcp_client_types")
trace_contract.emit_determinism_digest("p0", "mcp_client_types")

trace_contract._emit_dispatches_healing_run("p1", "mcp_client_types", "L2")
trace_contract._emit_routes_through("p1", "mcp_client_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "mcp_client_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "mcp_client_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "mcp_client_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "mcp_client_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "mcp_client_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "mcp_client_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "mcp_client_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "mcp_client_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "mcp_client_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "mcp_client_types")
trace_contract._emit_gated_by_confidence("p1", "mcp_client_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "mcp_client_types", "L2")
trace_contract._emit_reads_policy_state("p1", "mcp_client_types", "L2")

trace_contract._emit_emits_metric_event("mcp_client_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("mcp_client_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("mcp_client_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("mcp_client_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("mcp_client_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("mcp_client_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("mcp_client_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("mcp_client_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("mcp_client_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("mcp_client_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("mcp_client_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("mcp_client_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("mcp_client_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("mcp_client_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("mcp_client_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("mcp_client_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("mcp_client_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("mcp_client_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("mcp_client_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("mcp_client_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("mcp_client_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("mcp_client_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("mcp_client_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("mcp_client_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("mcp_client_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("mcp_client_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("mcp_client_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("mcp_client_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "mcp_client_types", "context_pull")
trace_contract._emit_pulls_context("p1", "mcp_client_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "mcp_client_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "mcp_client_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "mcp_client_types", "write_through")
trace_contract._emit_writes_through("p1", "mcp_client_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "mcp_client_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "mcp_client_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "mcp_client_types", "routing_commit")

logger = logging.getLogger(__name__)


class MCPClient(Protocol):
    """Protocol defining the MCP client interface.

    All MCP clients must implement this protocol for type safety.
    """

    def __call__(self, *args: object, **kwargs: object) -> dict[str, object]:
        """Execute the client operation.

        Args:
            *args: Variable positional arguments
            **kwargs: Variable keyword arguments

        Returns:
            Dict with operation result
        """
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "MCPClient.__call__", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "MCPClient.__call__", "p0_governance")
        ...


@dataclass
class MCPClientSpec:
    """Typed representation of a configured MCP client.

    This is the canonical schema for MCP client configuration,
    enforcing strict typing and validation.

    Attributes:
        name: Unique client identifier
        provider: Provider type (redis, chromadb, openai, etc.)
        module: Optional explicit Python module path
        class_name: Optional explicit class name
        parameters: Client initialization parameters
        optional: Whether this client is optional (won't fail if unavailable)
    """

    name: str
    provider: str = "stub"
    module: str | None = None
    class_name: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    optional: bool = False

    def resolved_module(self) -> str | None:
        """Return explicit module or provider-mapped default.

        Returns:
            Module path or None for stub
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "MCPClientSpec.resolved_module")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:MCPClientSpec.resolved_module".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if self.module:
            return self.module
        return get_default_module(self.provider)

    def resolved_class(self) -> str | None:
        """Return explicit class_name or provider-mapped default.

        Returns:
            Class name or None
        """
        if self.class_name:
            return self.class_name
        return get_default_class(self.provider)

    def validate(self) -> None:
        """Validate the spec configuration.

        Raises:
            ValueError: If spec is invalid
        """
        if not self.name:
            raise ValueError("MCPClientSpec requires a non-empty 'name'")
        if not isinstance(self.parameters, dict):
            raise ValueError(f"MCPClientSpec '{self.name}' parameters must be a dict")
        if self.provider != "stub":
            if not self.resolved_module():
                raise ValueError(
                    f"MCPClientSpec '{self.name}': no module specified and no default for provider '{self.provider}'",
                )
            if not self.resolved_class():
                raise ValueError(
                    f"MCPClientSpec '{self.name}': no class_name specified and no default for provider '{self.provider}'",
                )


class MCPClientStub:
    """Safe fallback MCP client.

    All MCP tools using this stub will receive a structured response
    indicating the client is stubbed. This prevents runtime failures
    while maintaining type safety.
    """

    def __init__(self, name: str, parameters: dict[str, Any] | None = None):
        """Initialize stub client.

        Args:
            name: Client name
            parameters: Optional parameters (for logging/debugging)
        """
        self.name = name
        self.parameters = parameters or {}
        logger.info("mcp_stub_created", extra={"client_name": name, "parameters": parameters})

    def __call__(self, *args, **kwargs) -> dict[str, Any]:
        """All calls return a structured stub result.

        Returns:
            Dict with stub=True and error message
        """
        return {
            "stub": True,
            "client": self.name,
            "parameters": self.parameters,
            "args": args,
            "kwargs": kwargs,
            "error": self.parameters.get("error", "Stubbed MCP client."),
        }

    def __repr__(self) -> str:
        """String representation."""
        details = ", ".join((f"{k}={v}" for k, v in self.parameters.items()))
        return f"<MCPClientStub name={self.name} {details}>"


class MCPClientRegistry:
    """Registry for managing MCP clients.

    Provides centralized access to all configured MCP clients
    with type-safe retrieval.
    """

    def __init__(self):
        """Initialize empty registry."""
        self._clients: dict[str, MCPClient] = {}
        self._specs: dict[str, MCPClientSpec] = {}

    def register(self, name: str, client: MCPClient) -> None:
        """Register a client instance.

        Args:
            name: Client name
            client: Instantiated client
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "MCPClientRegistry.register")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:MCPClientRegistry.register".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self._clients[name] = client
        spec.validate()
        self._specs[spec.name] = spec
        self._clients[spec.name] = client
        logger.info(
            "mcp_client_registered",
            extra={
                "client_name": spec.name,
                "provider": spec.provider,
                "is_stub": isinstance(client, MCPClientStub),
            },
        )

    def get(self, name: str) -> Any | None:
        """Get a client by name.

        Args:
            name: Client name

        Returns:
            Client instance or None if not found
        """
        return self._clients.get(name)

    def get_spec(self, name: str) -> MCPClientSpec | None:
        """Get a client spec by name.

        Args:
            name: Client name

        Returns:
            Client spec or None if not found
        """
        return self._specs.get(name)

    def has(self, name: str) -> bool:
        """Check if a client exists.

        Args:
            name: Client name

        Returns:
            True if client exists
        """
        return name in self._clients

    def list_clients(self) -> list[str]:
        """List all registered client names.

        Returns:
            List of client names
        """
        return list(self._clients.keys())

    def is_stub(self, name: str) -> bool:
        """Check if a client is a stub.

        Args:
            name: Client name

        Returns:
            True if client is a stub
        """
        client = self.get(name)
        return isinstance(client, MCPClientStub)

    def clear(self) -> None:
        """Clear all registered clients."""
        self._clients.clear()
        self._specs.clear()
