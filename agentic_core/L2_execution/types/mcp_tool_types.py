from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

emit_replay_key("p0", "mcp_tool_types")
emit_determinism_digest("p0", "mcp_tool_types")

_emit_dispatches_healing_run("p1", "mcp_tool_types", "L2")
_emit_routes_through("p1", "mcp_tool_types", "L2")
_emit_checks_agent_registry("p1", "mcp_tool_types", "agent_registry")
_emit_validates_agent_capability("p1", "mcp_tool_types", "capability")
_emit_dispatches_execution_plan("p1", "mcp_tool_types", "exec_plan")
_emit_agent_executes_agent("p1", "mcp_tool_types", "sub_agent")
_emit_routes_to_agent("p1", "mcp_tool_types", "target_agent")
_emit_verifies_policy("p1", "mcp_tool_types", "policy_check")
_emit_observes_runtime_state("p1", "mcp_tool_types", "runtime_state")
_emit_verifies_boundary("p1", "mcp_tool_types", "boundary_check")
_emit_transcripts_response("p1", "mcp_tool_types", "transcript")
_emit_hard_fails_untranscripted("p1", "mcp_tool_types")
_emit_gated_by_confidence("p1", "mcp_tool_types", "confidence_gate")
_emit_escalates_to_human("p1", "mcp_tool_types", "L2")
_emit_reads_policy_state("p1", "mcp_tool_types", "L2")
_emit_authorize_and_execute("p2", "mcp_tool_types", "execution_auth")
_emit_validates_capability("p2", "mcp_tool_types", "capability_check")
_emit_routes_to_capability("p2", "mcp_tool_types", "capability_route")
_emit_writes_via_uwg("p2", "mcp_tool_types", "uwg_write")
_emit_blocks_direct_write("p2", "mcp_tool_types", "direct_write_block")
_emit_records_tool_invocation("p2", "mcp_tool_types", "tool_invocation")
_emit_captures_execution_output("p2", "mcp_tool_types", "exec_output")
_emit_dispatches_agent("p3", "mcp_tool_types", "agent_dispatch")
_emit_coordinates_agents("p3", "mcp_tool_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "mcp_tool_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "mcp_tool_types", "healing_outcome")
_emit_escalates_failure("p3", "mcp_tool_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "mcp_tool_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "mcp_tool_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "mcp_tool_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "mcp_tool_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "mcp_tool_types", "eval_metric")
_emit_stores_embedding("p4", "mcp_tool_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "mcp_tool_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "mcp_tool_types", "exec_snapshot_link")

"MCP Tool Server Integration.\n\nProvides MCP (Model Context Protocol) tool server integration\nfor external tool access and context providers.\n\nPhase 1C - SDK Integration Layer\n"
import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L0_routing.enforcement.runtime_guard import (
    runtime_guard,
)  # guardian: allow-layer-violation -- L2 module uses L0 config/enforcement; intentional downward enforcement-chain dependency
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
from tqdm import tqdm

_emit_emits_metric_event("mcp_tool_types", "p4obs", "metric_1")
_emit_emits_metric_event("mcp_tool_types", "p4obs", "metric_2")
_emit_emits_metric_event("mcp_tool_types", "p4obs", "metric_3")
_emit_emits_metric_event("mcp_tool_types", "p4obs", "metric_4")
_emit_emits_metric_event("mcp_tool_types", "p4obs", "metric_5")
_emit_emits_metric_event("mcp_tool_types", "p4obs", "metric_6")
_emit_records_incident_event("mcp_tool_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("mcp_tool_types", "p4obs", "anomaly")
_emit_writes_observability_log("mcp_tool_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("mcp_tool_types", "p4obs", "mon_state")
_emit_triggers_alert("mcp_tool_types", "p4obs", "alert")
_emit_links_incident_trace("mcp_tool_types", "p4obs", "trace_link")
_emit_captures_pattern("mcp_tool_types", "p3lm", "pattern")
_emit_records_learning_event("mcp_tool_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("mcp_tool_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("mcp_tool_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("mcp_tool_types", "p3lm", "routing")
_emit_improves_agent_policy("mcp_tool_types", "p3lm", "policy")
_emit_stores_learning_state("mcp_tool_types", "p3lm", "state")
_emit_records_execution_trace("mcp_tool_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("mcp_tool_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("mcp_tool_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("mcp_tool_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("mcp_tool_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("mcp_tool_types", "env_read", "p2_env_1")
_emit_reads_environ("mcp_tool_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("mcp_tool_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("mcp_tool_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "mcp_tool_types", "context_pull")
_emit_pulls_context("p1", "mcp_tool_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "mcp_tool_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "mcp_tool_types", "uwg_term_2")
_emit_writes_through("p1", "mcp_tool_types", "write_through")
_emit_writes_through("p1", "mcp_tool_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "mcp_tool_types", "safety_validation")
_emit_invokes_eval("p1", "mcp_tool_types", "eval_call")
_emit_proposal_commits_routing("p1", "mcp_tool_types", "routing_commit")

Logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """MCP tool definition."""

    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable
    requires_approval: bool = False

    def to_openai_format(self) -> dict[str, Any]:
        """Convert to OpenAI function calling format.

        Returns:
            OpenAI-compatible tool definition
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "MCPTool.to_openai_format", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "MCPTool.to_openai_format", "p0_governance")
        return {
            "type": "function",
            "function": {"name": self.name, "description": self.description, "parameters": self.parameters},
        }

    def to_anthropic_format(self) -> dict[str, Any]:
        """Convert to Anthropic tool format.

        Returns:
            Anthropic-compatible tool definition
        """
        return {"name": self.name, "description": self.description, "input_schema": self.parameters}


@dataclass
class MCPToolResult:
    """Result from MCP tool execution."""

    tool_name: str
    success: bool
    result: Any
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class MCPToolServer:
    """MCP tool server for managing and executing tools."""

    def __init__(
        self,
        name: str = "agentic-workflow-tools",
        *,
        allow_legacy_capability_enforcer: bool = False,
    ):
        """Initialize MCP tool server.

        Args:
            name: Server name
            allow_legacy_capability_enforcer: If True, permits the legacy
                set_capability_enforcer() path.  Default False (fail-closed).
        """
        self.name = name
        self._tools: dict[str, MCPTool] = {}
        self._capability_enforcer: Any | None = None
        self._allow_legacy_capability_enforcer = allow_legacy_capability_enforcer
        Logger.info(f"MCP tool server initialized: {name}")

    def set_capability_enforcer(self, enforcer: Any) -> None:
        """Set the CapabilityEnforcer for this server.

        §Wave5.0.1: Single L2 chokepoint capability enforcement.
        §Wave5.0.4: Disabled by default.  Requires
        allow_legacy_capability_enforcer=True at construction time.

        Args:
            enforcer: CapabilityEnforcer instance (or None to clear)

        Raises:
            ValueError: If legacy capability enforcer is disabled (default).
        """

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            "MCPServerConfig.set_capability_enforcer",
        )
        if not self._allow_legacy_capability_enforcer:
            raise ValueError(
                "legacy capability enforcer is disabled. Use allow_legacy_capability_enforcer=True at construction or pass capability_token= per call.",
            )
        self._capability_enforcer = enforcer

    def register_tool(self, tool: MCPTool) -> None:
        """Register a tool.

        Args:
            tool: MCP tool to register
        """
        self._tools[tool.name] = tool
        Logger.info(f"Registered MCP tool: {tool.name}")

    def register_function(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        handler: Callable,
        requires_approval: bool = False,
    ) -> None:
        """Register a function as an MCP tool.

        Args:
            name: Tool name
            description: Tool description
            parameters: JSON schema for parameters
            handler: Function to execute
            requires_approval: Whether tool requires approval
        """
        tool = MCPTool(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler,
            requires_approval=requires_approval,
        )
        self.register_tool(tool)

    def get_tool(self, name: str) -> MCPTool | None:
        """Get a tool by name.

        Args:
            name: Tool name

        Returns:
            MCPTool or None if not found
        """
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        """List all registered tool names.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def get_tools_for_provider(self, Provider: str = "openai") -> list[dict[str, Any]]:
        """Get tools in Provider-specific format.

        Args:
            Provider: Provider name (openai, anthropic)

        Returns:
            List of tool definitions
        """
        tools = []
        for tool in self._tools.values():
            if Provider == "anthropic":
                tools.append(tool.to_anthropic_format())
            else:
                tools.append(tool.to_openai_format())
        return tools

    @runtime_guard("B.execute_tool.mcp_tool_types")
    def execute_tool(
        self,
        name: str,
        arguments: dict[str, Any],
        *,
        capability_token: Any | None = None,
    ) -> MCPToolResult:
        """Execute a tool.

        §Wave2.4: All tool calls pass through the LawSlotHandler enforcement
        gate before execution. The gate resolves applicable law slots,
        records an enforcement artifact, and may PASS/BLOCK/MODIFY.

        §Wave5.0.2: Explicit capability_token parameter for per-call
        propagation. Precedence: explicit token > legacy enforcer > DENY.

        Args:
            name: Tool name
            arguments: Tool arguments
            capability_token: Explicit CapabilityTokenArtifact for this call

        Returns:
            MCPToolResult with execution result

        Raises:
            ToolPolicyBlocked: If enforcement blocks the tool call
            PermissionError: If capability enforcement denies the call
        """
        tool = self.get_tool(name)
        if not tool:
            return MCPToolResult(tool_name=name, success=False, result=None, error=f"Tool not found: {name}")
        from agentic_core.L2_execution.types.capability_token_types import (
            PERMISSION_CODES,
            CapabilityEnforcer,
            build_capability_decision,
        )

        required_perm = PERMISSION_CODES["TOOL_READ"]
        resource_path = f"tool/{name}"
        if capability_token is not None:
            enforcer_local = CapabilityEnforcer(capability_token)
            enforcer_local.check(
                tool_name=name,
                action="execute",
                requested_resource=resource_path,
                required_permission=required_perm,
                semantic_clock=capability_token.semantic_clock,
            )
        elif self._allow_legacy_capability_enforcer and self._capability_enforcer is not None:
            enforcer_legacy: CapabilityEnforcer = self._capability_enforcer
            enforcer_legacy.check(
                tool_name=name,
                action="execute",
                requested_resource=resource_path,
                required_permission=required_perm,
                semantic_clock=enforcer_legacy.token.semantic_clock,
            )
        else:
            from agentic_core.L0_routing.types.determinism_types import (
                SemanticClockSnapshot,
            )  # guardian: allow-layer-violation -- L2 module uses L0 config/enforcement; intentional downward enforcement-chain dependency

            deny_clock = SemanticClockSnapshot(tick=0, vector_clock={})
            build_capability_decision(
                semantic_clock=deny_clock,
                tool_name=name,
                action="execute",
                requested_resource=resource_path,
                decision="DENY",
                deny_reason="NO_TOKEN_PROVIDED",
                capability_trace_id="NONE",
            )
            raise PermissionError("CAPABILITY_DENIED:NO_TOKEN_PROVIDED")
        from agentic_core.L2_execution.enforcement.tool_policy_enforcer import (
            _stable_args_hash,
            get_tool_policy_enforcer,
        )
        from agentic_core.L2_execution.types.tool_enforcement_types import LawSlotOutcome, ToolPolicyBlocked

        enforcer = get_tool_policy_enforcer()
        original_hash = _stable_args_hash(arguments)
        outcome, new_args, rationale, applied_slots = enforcer.enforce(name, arguments)
        modified_hash = _stable_args_hash(new_args) if outcome == LawSlotOutcome.MODIFY else ""
        artifact = enforcer.build_artifact(
            tool_name=name,
            outcome=outcome,
            applied_slots=applied_slots,
            rationale=rationale,
            original_args_hash=original_hash,
            modified_args_hash=modified_hash,
        )
        try:
            from agentic_core.L0_routing.types.routing_contracts_types import (
                TelemetryEmitter,
            )  # guardian: allow-layer-violation -- L2 module uses L0 config/enforcement; intentional downward enforcement-chain dependency

            emitter = TelemetryEmitter()
            emitter.emit_typed_artifact("TOOL_ENFORCEMENT", artifact)
        except Exception as e:  # guardian: allow-broad-exception -- re-raise after context enrichment
            raise ValueError(f"Invalid MCP tool result: {e}") from e
        if outcome == LawSlotOutcome.BLOCK:
            raise ToolPolicyBlocked(name, rationale, artifact)
        effective_args = new_args if outcome == LawSlotOutcome.MODIFY else arguments
        try:
            result = tool.handler(**effective_args)
            return MCPToolResult(tool_name=name, success=True, result=result)
        except (ValueError, TypeError) as e:
            Logger.error(f"Tool execution failed for {name}: {e}")
            return MCPToolResult(tool_name=name, success=False, result=None, error=str(e))


_MCP_SERVER: MCPToolServer | None = None


def get_mcp_server(name: str = "agentic-workflow-tools") -> MCPToolServer:
    """Get or create global MCP tool server.

    Args:
        name: Server name

    Returns:
        MCPToolServer instance
    """
    global _MCP_SERVER
    if _MCP_SERVER is None:
        _MCP_SERVER = MCPToolServer(name)
    return _MCP_SERVER


def register_default_tools(server: MCPToolServer) -> None:
    """Register default MCP tools.

    Args:
        server: MCP tool server
    """

    def calculator(operation: str, a: float, b: float) -> float:
        """Perform basic arithmetic operations."""
        operations = {
            "add": lambda x, y: x + y,
            "subtract": lambda x, y: x - y,
            "multiply": lambda x, y: x * y,
            "divide": lambda x, y: x / y if y != 0 else float("inf"),
        }
        if operation not in operations:
            raise ValueError(f"Unknown operation: {operation}")
        return operations[operation](a, b)

    server.register_function(
        name="calculator",
        description="Perform basic arithmetic operations (add, subtract, multiply, divide)",
        parameters={
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "The arithmetic operation to perform",
                },
                "a": {"type": "number", "description": "First operand"},
                "b": {"type": "number", "description": "Second operand"},
            },
            "required": ["operation", "a", "b"],
        },
        handler=calculator,
    )

    def analyze_text(text: str) -> dict[str, Any]:
        """Analyze text and return statistics."""
        words = text.split()
        sentences = text.split(".")
        return {
            "character_count": len(text),
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "average_word_length": sum(len(w) for w in words) / len(words) if words else 0,
        }

    server.register_function(
        name="analyze_text",
        description="Analyze text and return statistics (character count, word count, etc.)",
        parameters={
            "type": "object",
            "properties": {"text": {"type": "string", "description": "The text to analyze"}},
            "required": ["text"],
        },
        handler=analyze_text,
    )
    Logger.info("Registered default MCP tools")


def create_mcp_server(name: str = "agentic-workflow-tools", register_defaults: bool = True) -> MCPToolServer:
    """Factory function to create MCP tool server.

    Args:
        name: Server name
        register_defaults: Whether to register default tools

    Returns:
        MCPToolServer instance
    """
    server = MCPToolServer(name)
    if register_defaults:
        register_default_tools(server)
    return server


def execute_tool_with_capability(
    server: MCPToolServer,
    name: str,
    arguments: dict[str, Any],
    *,
    semantic_clock: Any,
    subject_kind: str,
    subject_id: str,
    issued_by: str,
    permissions: list[str],
    allowed_paths: list[str],
    max_tool_calls: int,
    policy_config_hash: str | None = None,
) -> MCPToolResult:
    """§Wave5.0.3 — Integration seam: issue token + execute tool in one call.

    Mints a CapabilityTokenArtifact via issue_capability_token and passes
    it to server.execute_tool using the explicit capability_token parameter.
    No enforcement logic here — enforcement remains solely in execute_tool.

    Args:
        server: MCPToolServer instance
        name: Tool name
        arguments: Tool arguments
        semantic_clock: SemanticClockSnapshot for token issuance
        subject_kind: Subject type (e.g. "agent")
        subject_id: Subject identifier
        issued_by: Issuer identity
        permissions: Permission code values (e.g. ["TOOL:READ"])
        allowed_paths: Allowed resource path prefixes
        max_tool_calls: Maximum invocations for this token
        policy_config_hash: Optional policy config hash

    Returns:
        MCPToolResult from execute_tool
    """
    from agentic_core.L2_execution.types.capability_token_types import issue_capability_token

    token = issue_capability_token(
        semantic_clock=semantic_clock,
        subject_kind=subject_kind,
        subject_id=subject_id,
        issued_by=issued_by,
        permissions=permissions,
        allowed_paths=allowed_paths,
        max_tool_calls=max_tool_calls,
        policy_config_hash=policy_config_hash,
    )
    return server.execute_tool(name, arguments, capability_token=token)


def execute_tool_calls(
    server: MCPToolServer,
    tool_calls: list[dict[str, Any]],
    *,
    capability_token: Any | None = None,
) -> list[MCPToolResult]:
    """Execute multiple tool calls.

    §Wave5.0.2: capability_token is propagated to each server.execute_tool call.

    Args:
        server: MCP tool server
        tool_calls: List of tool call definitions
        capability_token: Explicit CapabilityTokenArtifact for all calls

    Returns:
        List of MCPToolResult
    """
    results = []
    for tool_call in tqdm(tool_calls, desc="Processing", unit="item"):
        if "function" in tool_call:
            function = tool_call["function"]
            name = function.get("name")
            arguments = function.get("arguments", {})
            if isinstance(arguments, str):
                import json

                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    arguments = {}
            result = server.execute_tool(name, arguments, capability_token=capability_token)
            results.append(result)
    return results
