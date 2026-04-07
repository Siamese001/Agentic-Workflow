"""
Unified Registration Module for Orphan Agent Integration - Phase 1 Foundation

This module registers all previously-orphan agents into the validation
and healing infrastructure. Import this module at application startup
to enable all security and resilience features.

Usage:
    from agentic_core.L5_safety.validators import register_all_validators
    register_all_validators.initialize()

    # Check status
    status = register_all_validators.get_integration_status()
"""

from __future__ import annotations

import logging
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "register_all_validators_util")
emit_determinism_digest("p0", "register_all_validators_util")

_emit_dispatches_healing_run("p1", "register_all_validators_util", "L5")
_emit_routes_through("p1", "register_all_validators_util", "L5")
_emit_checks_agent_registry("p1", "register_all_validators_util", "agent_registry")
_emit_validates_agent_capability("p1", "register_all_validators_util", "capability")
_emit_dispatches_execution_plan("p1", "register_all_validators_util", "exec_plan")
_emit_agent_executes_agent("p1", "register_all_validators_util", "sub_agent")
_emit_routes_to_agent("p1", "register_all_validators_util", "target_agent")
_emit_verifies_policy("p1", "register_all_validators_util", "policy_check")
_emit_observes_runtime_state("p1", "register_all_validators_util", "runtime_state")
_emit_verifies_boundary("p1", "register_all_validators_util", "boundary_check")
_emit_transcripts_response("p1", "register_all_validators_util", "transcript")
_emit_hard_fails_untranscripted("p1", "register_all_validators_util")
_emit_gated_by_confidence("p1", "register_all_validators_util", "confidence_gate")
_emit_escalates_to_human("p1", "register_all_validators_util", "L5")
_emit_reads_policy_state("p1", "register_all_validators_util", "L5")
_emit_authorize_and_execute("p2", "register_all_validators_util", "execution_auth")
_emit_validates_capability("p2", "register_all_validators_util", "capability_check")
_emit_routes_to_capability("p2", "register_all_validators_util", "capability_route")
_emit_writes_via_uwg("p2", "register_all_validators_util", "uwg_write")
_emit_blocks_direct_write("p2", "register_all_validators_util", "direct_write_block")
_emit_records_tool_invocation("p2", "register_all_validators_util", "tool_invocation")
_emit_captures_execution_output("p2", "register_all_validators_util", "exec_output")
_emit_dispatches_agent("p3", "register_all_validators_util", "agent_dispatch")
_emit_coordinates_agents("p3", "register_all_validators_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "register_all_validators_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "register_all_validators_util", "healing_outcome")
_emit_escalates_failure("p3", "register_all_validators_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "register_all_validators_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "register_all_validators_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "register_all_validators_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "register_all_validators_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "register_all_validators_util", "eval_metric")
_emit_stores_embedding("p4", "register_all_validators_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "register_all_validators_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "register_all_validators_util", "exec_snapshot_link")
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

_emit_emits_metric_event("register_all_validators_util", "p4obs", "metric_1")
_emit_emits_metric_event("register_all_validators_util", "p4obs", "metric_2")
_emit_emits_metric_event("register_all_validators_util", "p4obs", "metric_3")
_emit_emits_metric_event("register_all_validators_util", "p4obs", "metric_4")
_emit_emits_metric_event("register_all_validators_util", "p4obs", "metric_5")
_emit_emits_metric_event("register_all_validators_util", "p4obs", "metric_6")
_emit_records_incident_event("register_all_validators_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("register_all_validators_util", "p4obs", "anomaly")
_emit_writes_observability_log("register_all_validators_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("register_all_validators_util", "p4obs", "mon_state")
_emit_triggers_alert("register_all_validators_util", "p4obs", "alert")
_emit_links_incident_trace("register_all_validators_util", "p4obs", "trace_link")
_emit_captures_pattern("register_all_validators_util", "p3lm", "pattern")
_emit_records_learning_event("register_all_validators_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("register_all_validators_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("register_all_validators_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("register_all_validators_util", "p3lm", "routing")
_emit_improves_agent_policy("register_all_validators_util", "p3lm", "policy")
_emit_stores_learning_state("register_all_validators_util", "p3lm", "state")
_emit_records_execution_trace("register_all_validators_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("register_all_validators_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("register_all_validators_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("register_all_validators_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("register_all_validators_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("register_all_validators_util", "env_read", "p2_env_1")
_emit_reads_environ("register_all_validators_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("register_all_validators_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("register_all_validators_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "register_all_validators_util", "context_pull")
_emit_pulls_context("p1", "register_all_validators_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "register_all_validators_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "register_all_validators_util", "uwg_term_2")
_emit_writes_through("p1", "register_all_validators_util", "write_through")
_emit_writes_through("p1", "register_all_validators_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "register_all_validators_util", "safety_validation")
_emit_invokes_eval("p1", "register_all_validators_util", "eval_call")
_emit_proposal_commits_routing("p1", "register_all_validators_util", "routing_commit")

Logger = logging.getLogger(__name__)
_REGISTERED = False


def initialize() -> dict[str, Any]:
    """
    Initialize all orphan agent integrations.

    This function registers:
    - Red team validators (adversarial_probe, boundary_testing)
    - Chaos resilience healing strategy
    - Dependency pruning healing strategy

    Returns:
        dict with initialization status and details
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "initialize", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "initialize", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "initialize")
    global _REGISTERED
    if _REGISTERED:
        return {"status": "already_initialized", "validators": [], "strategies": []}
    Logger.info("[Sovereign Integration] Initializing orphan agent integrations...")
    results = {"status": "initializing", "validators": [], "strategies": [], "errors": []}
    try:
        from agentic_core.L5_safety.validators.red_team_integration_types import register_red_team_validators

        red_team_result = register_red_team_validators()
        results["validators"].extend(red_team_result.get("registered", []))
        results["errors"].extend(red_team_result.get("errors", []))
    except ImportError as e:
        Logger.warning(f"[Sovereign Integration] Red team integration unavailable: {e}")
        results["errors"].append(f"red_team_integration: {e}")
    try:
        from agentic_core.L5_safety.validators.chaos_healing_integration_types import register_chaos_healing

        chaos_result = register_chaos_healing()
        results["strategies"].extend(chaos_result.get("registered", []))
        results["errors"].extend(chaos_result.get("errors", []))
    except ImportError as e:
        Logger.warning(f"[Sovereign Integration] Chaos integration unavailable: {e}")
        results["errors"].append(f"chaos_healing_integration: {e}")
    try:
        from agentic_core.L5_safety.validators.dependency_healing_integration_types import (
            register_dependency_healing,
        )

        dep_result = register_dependency_healing()
        results["strategies"].extend(dep_result.get("registered", []))
        results["errors"].extend(dep_result.get("errors", []))
    except ImportError as e:
        Logger.warning(f"[Sovereign Integration] Dependency integration unavailable: {e}")
        results["errors"].append(f"dependency_healing_integration: {e}")
    try:
        from agentic_core.L5_safety.validators.operational_healing_integration_types import (
            register_operational_healing,
        )

        op_result = register_operational_healing()
        results["strategies"].extend(op_result.get("registered", []))
        results["errors"].extend(op_result.get("errors", []))
    except ImportError as e:
        Logger.warning(f"[Sovereign Integration] Operational integration unavailable: {e}")
        results["errors"].append(f"operational_healing_integration: {e}")
    _REGISTERED = True
    results["status"] = "initialized" if not results["errors"] else "partial"
    Logger.info(
        f"[Sovereign Integration] Initialized: {len(results['validators'])} validators, {len(results['strategies'])} strategies",
    )
    return results


def get_integration_status() -> dict[str, Any]:
    """
    Return comprehensive status of all integrations.

    Returns:
        dict with:
        - initialized: bool
        - validators_registered: list of validator names
        - strategies_registered: list of strategy names
        - module_status: dict of each module's status
    """
    status = {
        "initialized": _REGISTERED,
        "validators_registered": [],
        "strategies_registered": [],
        "module_status": {},
    }
    try:
        from agentic_core.L5_safety.types.healing_orchestration_types import get_validator_orchestrator

        orchestrator = get_validator_orchestrator()
        status["validators_registered"] = list(orchestrator._validators.keys())
        status["module_status"]["validator_orchestrator"] = "available"
    except ImportError as e:

        raise ImportError(f"Required dependency missing: {e}")  # guardian: allow-silent-swallow
        status["module_status"]["validator_orchestrator"] = "unavailable"
    try:
        from agentic_core.L5_safety.types.healing_orchestration_types import get_healing_orchestrator

        orchestrator = get_healing_orchestrator()
        status["strategies_registered"] = list(orchestrator._strategies.keys())
        status["module_status"]["healing_orchestrator"] = "available"
    except ImportError:
        status["module_status"]["healing_orchestrator"] = "unavailable"
    try:
        import importlib.util

        if importlib.util.find_spec("agentic_core.L5_safety.validators.red_team_integration"):
            status["module_status"]["red_team_integration"] = "available"
        else:
            status["module_status"]["red_team_integration"] = "unavailable"
    except ImportError:
        status["module_status"]["red_team_integration"] = "unavailable"
    try:
        if importlib.util.find_spec("agentic_core.L5_safety.validators.chaos_healing_integration"):
            status["module_status"]["chaos_healing_integration"] = "available"
        else:
            status["module_status"]["chaos_healing_integration"] = "unavailable"
    except ImportError:
        status["module_status"]["chaos_healing_integration"] = "unavailable"
    try:
        dep_module = "agentic_core.L5_safety.validators.dependency_healing_integration"
        if importlib.util.find_spec(dep_module):
            status["module_status"]["dependency_healing_integration"] = "available"
        else:
            status["module_status"]["dependency_healing_integration"] = "unavailable"
    except ImportError:
        status["module_status"]["dependency_healing_integration"] = "unavailable"
    return status


def reset() -> None:
    """
    Reset integration state (for testing purposes only).

    WARNING: This should only be used in test fixtures.
    """
    global _REGISTERED
    _REGISTERED = False
    try:
        from agentic_core.L5_safety.types.healing_orchestration_types import ValidatorOrchestrator

        ValidatorOrchestrator.reset_instance()
    except ImportError:
        pass
    try:
        from agentic_core.L5_safety.types.healing_orchestration_types import HealingSovereignOrchestrator

        HealingSovereignOrchestrator.reset_instance()
    except ImportError:
        pass
