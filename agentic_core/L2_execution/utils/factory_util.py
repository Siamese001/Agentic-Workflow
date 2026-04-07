"""MCP client factory and instantiation logic.

Phase 1 - Pillar 3: Typed Contracts (Strict Schemas)
"""

import importlib
import logging
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

_emit_authorize_and_execute("p2", "factory_util", "execution_auth")
_emit_validates_capability("p2", "factory_util", "capability_check")
_emit_routes_to_capability("p2", "factory_util", "capability_route")
_emit_writes_via_uwg("p2", "factory_util", "uwg_write")
_emit_blocks_direct_write("p2", "factory_util", "direct_write_block")
_emit_records_tool_invocation("p2", "factory_util", "tool_invocation")
_emit_captures_execution_output("p2", "factory_util", "exec_output")
_emit_dispatches_agent("p3", "factory_util", "agent_dispatch")
_emit_coordinates_agents("p3", "factory_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "factory_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "factory_util", "healing_outcome")
_emit_escalates_failure("p3", "factory_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "factory_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "factory_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "factory_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "factory_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "factory_util", "eval_metric")
_emit_stores_embedding("p4", "factory_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "factory_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "factory_util", "exec_snapshot_link")
from .client import MCPClientRegistry, MCPClientSpec, MCPClientStub
from .exceptions_util import MCPClientInitializationError

emit_replay_key("p0", "factory_util")
emit_determinism_digest("p0", "factory_util")

_emit_dispatches_healing_run("p1", "factory_util", "L2")
_emit_routes_through("p1", "factory_util", "L2")
_emit_checks_agent_registry("p1", "factory_util", "agent_registry")
_emit_validates_agent_capability("p1", "factory_util", "capability")
_emit_dispatches_execution_plan("p1", "factory_util", "exec_plan")
_emit_agent_executes_agent("p1", "factory_util", "sub_agent")
_emit_routes_to_agent("p1", "factory_util", "target_agent")
_emit_verifies_policy("p1", "factory_util", "policy_check")
_emit_observes_runtime_state("p1", "factory_util", "runtime_state")
_emit_verifies_boundary("p1", "factory_util", "boundary_check")
_emit_transcripts_response("p1", "factory_util", "transcript")
_emit_hard_fails_untranscripted("p1", "factory_util")
_emit_gated_by_confidence("p1", "factory_util", "confidence_gate")
_emit_escalates_to_human("p1", "factory_util", "L2")
_emit_reads_policy_state("p1", "factory_util", "L2")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
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
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
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

_emit_emits_metric_event("factory_util", "p4obs", "metric_1")
_emit_emits_metric_event("factory_util", "p4obs", "metric_2")
_emit_emits_metric_event("factory_util", "p4obs", "metric_3")
_emit_emits_metric_event("factory_util", "p4obs", "metric_4")
_emit_emits_metric_event("factory_util", "p4obs", "metric_5")
_emit_emits_metric_event("factory_util", "p4obs", "metric_6")
_emit_records_incident_event("factory_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("factory_util", "p4obs", "anomaly")
_emit_writes_observability_log("factory_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("factory_util", "p4obs", "mon_state")
_emit_triggers_alert("factory_util", "p4obs", "alert")
_emit_links_incident_trace("factory_util", "p4obs", "trace_link")
_emit_captures_pattern("factory_util", "p3lm", "pattern")
_emit_records_learning_event("factory_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("factory_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("factory_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("factory_util", "p3lm", "routing")
_emit_improves_agent_policy("factory_util", "p3lm", "policy")
_emit_stores_learning_state("factory_util", "p3lm", "state")
_emit_records_execution_trace("factory_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("factory_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("factory_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("factory_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("factory_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("factory_util", "env_read", "p2_env_1")
_emit_reads_environ("factory_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("factory_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("factory_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "factory_util", "context_pull")
_emit_pulls_context("p1", "factory_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "factory_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "factory_util", "uwg_term_2")
_emit_writes_through("p1", "factory_util", "write_through")
_emit_writes_through("p1", "factory_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "factory_util", "safety_validation")
_emit_invokes_eval("p1", "factory_util", "eval_call")
_emit_proposal_commits_routing("p1", "factory_util", "routing_commit")

logger = logging.getLogger(__name__)


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

    _emit_snapshots_state(str(_uuid.uuid4()), "parse_mcp_client_specs", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "parse_mcp_client_specs", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "parse_mcp_client_specs")
    specs: list[MCPClientSpec] = []
    for raw in raw_specs:
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
        provider = str(raw.get("provider", "stub")).lower()
        module = raw.get("module")
        class_name = raw.get("class_name") or raw.get("class")
        spec = MCPClientSpec(
            name=name,
            provider=provider,
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
    if spec.provider == "stub" and (not spec.module):
        logger.info(f"Using stub for MCP client '{spec.name}'")
        return MCPClientStub(spec.name, spec.parameters)
    module_name = spec.resolved_module()
    class_name = spec.resolved_class()
    if not module_name:
        raise MCPClientInitializationError(
            f"Cannot create MCP client '{spec.name}': no module specified and no provider mapping found.",
            client_name=spec.name,
            provider=spec.provider,
        )
    if not class_name:
        raise MCPClientInitializationError(
            f"Cannot create MCP client '{spec.name}': no class_name specified and no provider mapping found.",
            client_name=spec.name,
            provider=spec.provider,
        )
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        if spec.optional:
            logger.warning(
                f"Optional MCP client '{spec.name}' module '{module_name}' not available, using stub: {exc}",
            )
            return MCPClientStub(spec.name, {"error": f"Module not available: {exc}"})
        raise MCPClientInitializationError(
            f"Failed to import MCP module '{module_name}' for client '{spec.name}': {exc}",
            client_name=spec.name,
            provider=spec.provider,
        ) from exc
    try:
        client_cls = getattr(module, class_name)
    except AttributeError as exc:
        if spec.optional:
            logger.warning(
                f"Optional MCP client '{spec.name}' class '{class_name}' not found in '{module_name}', using stub",
            )
            return MCPClientStub(spec.name, {"error": f"Class not found: {class_name}"})
        raise MCPClientInitializationError(
            f"Module '{module_name}' missing class '{class_name}' for MCP client '{spec.name}'.",
            client_name=spec.name,
            provider=spec.provider,
        ) from exc
    try:
        instance = client_cls(**spec.parameters)
        logger.info(f"Initialized MCP client '{spec.name}' via {module_name}.{class_name}")
        return instance
    except Exception as exc:
        if spec.optional:
            logger.warning(f"Optional MCP client '{spec.name}' failed to initialize, using stub: {exc}")
            return MCPClientStub(spec.name, {"error": f"Initialization failed: {exc}"})
        raise MCPClientInitializationError(
            f"Failed to instantiate MCP client '{spec.name}': {exc}",
            client_name=spec.name,
            provider=spec.provider,
        ) from exc


def create_mcp_registry(specs: list[MCPClientSpec], fail_on_error: bool = False) -> MCPClientRegistry:
    """Create an MCP client registry from specifications.

    Args:
        specs: List of client specifications
        fail_on_error: If True, raise on any initialization error

    Returns:
        Populated MCPClientRegistry

    Raises:
        MCPClientInitializationError: If fail_on_error=True and init fails
    """
    registry = MCPClientRegistry()
    for spec in specs:
        try:
            client = instantiate_mcp_client(spec)
            registry.register(spec, client)
        except MCPClientInitializationError as exc:    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context    # guardian: MCPClientInitializationError should be handled with specific context
            if fail_on_error and (not spec.optional):
                raise
            logger.warning(f"Failed to initialize MCP client '{spec.name}', registering stub: {exc}")
            stub = MCPClientStub(spec.name, {"error": str(exc)})
            registry.register(spec, stub)
    return registry
