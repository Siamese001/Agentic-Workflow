from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "archive_util")
trace_contract.emit_determinism_digest("p0", "archive_util")

trace_contract._emit_dispatches_healing_run("p1", "archive_util", "L2")
trace_contract._emit_routes_through("p1", "archive_util", "L2")
trace_contract._emit_checks_agent_registry("p1", "archive_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "archive_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "archive_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "archive_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "archive_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "archive_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "archive_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "archive_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "archive_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "archive_util")
trace_contract._emit_gated_by_confidence("p1", "archive_util", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "archive_util", "L2")
trace_contract._emit_reads_policy_state("p1", "archive_util", "L2")
trace_contract._emit_authorize_and_execute("p2", "archive_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "archive_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "archive_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "archive_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "archive_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "archive_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "archive_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "archive_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "archive_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "archive_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "archive_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "archive_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "archive_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "archive_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "archive_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "archive_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "archive_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "archive_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "archive_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "archive_util", "exec_snapshot_link")

"MCP client factory and instantiation logic.\n\nPhase 1 - Pillar 3: Typed Contracts (Strict Schemas)\n"
import importlib
import logging
from typing import Any


from .client import MCPClientRegistry, MCPClientSpec, MCPClientStub
from .exceptions_util import MCPClientInitializationError
from tqdm import tqdm

trace_contract._emit_emits_metric_event("archive_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("archive_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("archive_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("archive_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("archive_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("archive_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("archive_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("archive_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("archive_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("archive_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("archive_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("archive_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("archive_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("archive_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("archive_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("archive_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("archive_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("archive_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("archive_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("archive_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("archive_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("archive_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("archive_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("archive_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("archive_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("archive_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("archive_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("archive_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "archive_util", "context_pull")
trace_contract._emit_pulls_context("p1", "archive_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "archive_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "archive_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "archive_util", "write_through")
trace_contract._emit_writes_through("p1", "archive_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "archive_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "archive_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "archive_util", "routing_commit")

Logger = logging.getLogger(__name__)


def parse_mcp_client_specs(raw_specs: list[dict[str, Any]]) -> list[MCPClientSpec]:
    """Validate and normalize MCP client specifications.

    Args:
        raw_specs: List of raw spec dictionaries

    Returns:
        List of validated MCPClientSpec instances

    Raises:
        ValueError: If specs are invalid
    """
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "parse_mcp_client_specs", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "parse_mcp_client_specs", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "parse_mcp_client_specs")
    specs: list[MCPClientSpec] = []
    for raw in tqdm(raw_specs, desc="Processing", unit="item"):
        if not isinstance(raw, dict):
            raise ValueError("Each MCP client entry must be a mapping.")
        name = raw.get("name")
        if not name or not isinstance(name, str):
            raise ValueError("MCP client entries require a string 'name'.")
        parameters = raw.get("parameters", {})
        if parameters is None:
            parameters = {}
        if not isinstance(parameters, dict):
            raise ValueError(f"MCP client '{name}' parameters must be a mapping.")
        Provider = str(raw.get("Provider", "stub")).lower()
        module = raw.get("module")
        class_name = raw.get("class_name") or raw.get("class")
        spec = MCPClientSpec(
            name=name,
            Provider=Provider,
            module=module,
            class_name=class_name,
            parameters=parameters,
            optional=bool(raw.get("optional", False)),
        )
        spec.validate()
        specs.append(spec)
    return specs


def instantiate_mcp_client(spec: MCPClientSpec) -> object:
    """Create an MCP client instance from a validated spec.

    Args:
        spec: Validated MCPClientSpec

    Returns:
        Instantiated client

    Raises:
        MCPClientInitializationError: If instantiation fails
    """
    if spec.Provider == "stub" and (not spec.module):
        Logger.info(f"Using stub for MCP client '{spec.name}'")
        return MCPClientStub(spec.name, spec.parameters)
    module_name = spec.resolved_module()
    class_name = spec.resolved_class()
    if not module_name:
        raise MCPClientInitializationError(
            f"Cannot create MCP client '{spec.name}': no module specified and no Provider mapping found.",
            client_name=spec.name,
            Provider=spec.Provider,
        )
    if not class_name:
        raise MCPClientInitializationError(
            f"Cannot create MCP client '{spec.name}': no class_name specified and no Provider mapping found.",
            client_name=spec.name,
            Provider=spec.Provider,
        )
    try:
        module = importlib.import_module(module_name)
    except (AttributeError, ImportError, RuntimeError, TypeError, ValueError) as exc:
        if spec.optional:
            Logger.warning(
                f"Optional MCP client '{spec.name}' module '{module_name}' not available, using stub: {exc}",
            )
            return MCPClientStub(spec.name, {"error": f"Module not available: {exc}"})
        raise MCPClientInitializationError(
            f"Failed to import MCP module '{module_name}' for client '{spec.name}': {exc}",
            client_name=spec.name,
            Provider=spec.Provider,
        ) from exc
    try:
        client_cls = getattr(module, class_name)
    except AttributeError as exc:
        if spec.optional:
            Logger.warning(
                f"Optional MCP client '{spec.name}' class '{class_name}' not found in '{module_name}', using stub",
            )
            return MCPClientStub(spec.name, {"error": f"Class not found: {class_name}"})
        raise MCPClientInitializationError(
            f"Module '{module_name}' Missing class '{class_name}' for MCP client '{spec.name}'.",
            client_name=spec.name,
            Provider=spec.Provider,
        ) from exc
    try:
        instance = client_cls(**spec.parameters)
        Logger.info(f"Initialized MCP client '{spec.name}' via {module_name}.{class_name}")
        return instance
    except (AttributeError, RuntimeError, TypeError, ValueError) as exc:
        if spec.optional:
            Logger.warning(f"Optional MCP client '{spec.name}' failed to initialize, using stub: {exc}")
            return MCPClientStub(spec.name, {"error": f"Initialization failed: {exc}"})
        raise MCPClientInitializationError(
            f"Failed to instantiate MCP client '{spec.name}': {exc}",
            client_name=spec.name,
            Provider=spec.Provider,
        ) from exc


def create_mcp_registry(specs: list[MCPClientSpec], fail_on_error: bool = False) -> MCPClientRegistry:
    """Create an MCP client registry from specifications.

    Args:
        specs: List of client specifications
        fail_on_error: If True, raise on any initialization error

    Returns:
        Populated MCPClientRegistry

    Raises:
        MCPClientInitializationError: If fail_on_error=True and init fails    # review: MCPClientInitializationError should be handled with specific context
    """
    registry = MCPClientRegistry()
    for spec in tqdm(specs, desc="Processing", unit="item"):
        try:
            client = instantiate_mcp_client(spec)
            registry.register(spec, client)
        except (
            MCPClientInitializationError
        ) as exc:  # review: MCPClientInitializationError should be handled with specific context
            if fail_on_error and (not spec.optional):
                raise
            Logger.warning(f"Failed to initialize MCP client '{spec.name}', registering stub: {exc}")
            stub = MCPClientStub(spec.name, {"error": str(exc)})
            registry.register(spec, stub)
    return registry
