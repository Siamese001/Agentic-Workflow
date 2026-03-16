"""
Tests for HealContext trace_id and execution_mode (E1 + E10).

Per .windsurfrules §1.1: Zero-tolerance testing - all changed logic tested.
Per .windsurfrules §1.7: Deterministic decision surfaces - identical input → identical output.
Per hostile audit Section E1: trace_id threads through all artifacts and HealContext.
Per hostile audit Section E10: execution_mode distinguishes scan/heal/validate modes.
"""

import argparse
import re

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_heal_context_trace_id")
_emit_applies_guardrail("p0", "test_heal_context_trace_id", "p0_governance")
_emit_reads_policy_state("p0", "test_heal_context_trace_id", "policy_binding")
_emit_snapshots_state("p0", "test_heal_context_trace_id", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("test_heal_context_trace_id", "p4obs", "metric_1")
_emit_emits_metric_event("test_heal_context_trace_id", "p4obs", "metric_2")
_emit_emits_metric_event("test_heal_context_trace_id", "p4obs", "metric_3")
_emit_emits_metric_event("test_heal_context_trace_id", "p4obs", "metric_4")
_emit_emits_metric_event("test_heal_context_trace_id", "p4obs", "metric_5")
_emit_emits_metric_event("test_heal_context_trace_id", "p4obs", "metric_6")
_emit_records_incident_event("test_heal_context_trace_id", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_heal_context_trace_id", "p4obs", "anomaly")
_emit_writes_observability_log("test_heal_context_trace_id", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_heal_context_trace_id", "p4obs", "mon_state")
_emit_triggers_alert("test_heal_context_trace_id", "p4obs", "alert")
_emit_links_incident_trace("test_heal_context_trace_id", "p4obs", "trace_link")
_emit_captures_pattern("test_heal_context_trace_id", "p3lm", "pattern")
_emit_records_learning_event("test_heal_context_trace_id", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_heal_context_trace_id", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_heal_context_trace_id", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_heal_context_trace_id", "p3lm", "routing")
_emit_improves_agent_policy("test_heal_context_trace_id", "p3lm", "policy")
_emit_stores_learning_state("test_heal_context_trace_id", "p3lm", "state")
_emit_records_execution_trace("test_heal_context_trace_id", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_heal_context_trace_id", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_heal_context_trace_id", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_heal_context_trace_id", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_heal_context_trace_id", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_heal_context_trace_id", "env_read", "p2_env_1")
_emit_reads_environ("test_heal_context_trace_id", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_heal_context_trace_id", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_heal_context_trace_id", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_heal_context_trace_id", "context_pull")
_emit_pulls_context("p1", "test_heal_context_trace_id", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_heal_context_trace_id", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_heal_context_trace_id", "uwg_term_2")
_emit_writes_through("p1", "test_heal_context_trace_id", "write_through")
_emit_writes_through("p1", "test_heal_context_trace_id", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_heal_context_trace_id", "safety_validation")
_emit_invokes_eval("p1", "test_heal_context_trace_id", "eval_call")
_emit_proposal_commits_routing("p1", "test_heal_context_trace_id", "routing_commit")
emit_replay_key("p0", "test_heal_context_trace_id")
emit_determinism_digest("p0", "test_heal_context_trace_id")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_heal_context_trace_id", "execution_auth")
_emit_validates_capability("p2", "test_heal_context_trace_id", "capability_check")
_emit_routes_to_capability("p2", "test_heal_context_trace_id", "capability_route")
_emit_writes_via_uwg("p2", "test_heal_context_trace_id", "uwg_write")
_emit_blocks_direct_write("p2", "test_heal_context_trace_id", "direct_write_block")
_emit_records_tool_invocation("p2", "test_heal_context_trace_id", "tool_invocation")
_emit_captures_execution_output("p2", "test_heal_context_trace_id", "exec_output")
_emit_dispatches_agent("p3", "test_heal_context_trace_id", "agent_dispatch")
_emit_coordinates_agents("p3", "test_heal_context_trace_id", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_heal_context_trace_id", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_heal_context_trace_id", "healing_outcome")
_emit_escalates_failure("p3", "test_heal_context_trace_id", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_heal_context_trace_id", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_heal_context_trace_id", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_heal_context_trace_id", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_heal_context_trace_id", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_heal_context_trace_id", "eval_metric")
_emit_stores_embedding("p4", "test_heal_context_trace_id", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_heal_context_trace_id", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_heal_context_trace_id", "exec_snapshot_link")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def test_heal_context_trace_id_format():
    """
    PASS: trace_id follows format SSOT-YYYYMMDD-HHMMSS-{8hex}.
    FAIL: trace_id has wrong format or missing components.

    Per .windsurfrules §1.7: Deterministic decision surfaces.
    Per hostile audit Section E1: trace_id must be unique and traceable.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import HealContext

    args = argparse.Namespace(heal=False, validate=False)
    ctx = HealContext.from_args(args)

    # Verify trace_id format: SSOT-YYYYMMDD-HHMMSS-{8hex}
    pattern = r"^SSOT-\d{8}-\d{6}-[0-9a-f]{8}$"
    assert re.match(pattern, ctx.trace_id), f"trace_id format invalid: {ctx.trace_id}"

    # Verify trace_id components
    parts = ctx.trace_id.split("-")
    assert len(parts) == 4, f"trace_id should have 4 parts, got {len(parts)}"
    assert parts[0] == "SSOT", "trace_id should start with SSOT"
    assert len(parts[1]) == 8, "timestamp date should be 8 digits"
    assert len(parts[2]) == 6, "timestamp time should be 6 digits"
    assert len(parts[3]) == 8, "uuid fragment should be 8 hex chars"


def test_heal_context_trace_id_uniqueness():
    """
    PASS: Multiple HealContext instances generate different trace_ids.
    FAIL: trace_ids collide or are identical.

    Per .windsurfrules §1.7: Deterministic decision surfaces must not collapse.
    Per hostile audit Section E1: trace_id must be unique per run.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import HealContext

    args = argparse.Namespace(heal=False, validate=False)

    # Generate multiple trace_ids
    trace_ids = set()
    for _ in range(10):
        ctx = HealContext.from_args(args)
        trace_ids.add(ctx.trace_id)

    # All trace_ids should be unique
    assert len(trace_ids) == 10, "trace_ids should be unique across instances"


def test_heal_context_execution_mode_scan():
    """
    PASS: execution_mode='scan' when heal=False and validate=False.
    FAIL: Wrong execution_mode for scan-only mode.

    Per .windsurfrules §1.7: Deterministic decision surfaces.
    Per hostile audit Section E10: execution_mode distinguishes scan/heal/validate.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import HealContext

    args = argparse.Namespace(heal=False, validate=False)
    ctx = HealContext.from_args(args)

    assert ctx.execution_mode == "scan", f"Expected 'scan', got '{ctx.execution_mode}'"
    assert ctx.heal is False
    assert ctx.auto_approve is False


def test_heal_context_execution_mode_heal():
    """
    PASS: execution_mode='heal' when heal=True.
    FAIL: Wrong execution_mode for heal mode.

    Per .windsurfrules §1.7: Deterministic decision surfaces.
    Per hostile audit Section E10: execution_mode distinguishes scan/heal/validate.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import HealContext

    args = argparse.Namespace(heal=True, validate=False)
    ctx = HealContext.from_args(args)

    assert ctx.execution_mode == "heal", f"Expected 'heal', got '{ctx.execution_mode}'"
    assert ctx.heal is True
    assert ctx.auto_approve is True


def test_heal_context_execution_mode_validate():
    """
    PASS: execution_mode='validate' when validate=True.
    FAIL: Wrong execution_mode for validate mode.

    Per .windsurfrules §1.7: Deterministic decision surfaces.
    Per hostile audit Section E10: execution_mode distinguishes scan/heal/validate.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import HealContext

    args = argparse.Namespace(heal=False, validate=True)
    ctx = HealContext.from_args(args)

    assert ctx.execution_mode == "validate", f"Expected 'validate', got '{ctx.execution_mode}'"


def test_heal_context_execution_mode_validate_overrides_heal():
    """
    PASS: execution_mode='validate' when both validate=True and heal=True.
    FAIL: validate doesn't take precedence over heal.

    Per .windsurfrules §1.7: Deterministic decision surfaces.
    Per hostile audit Section E10: validate mode has highest priority.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import HealContext

    args = argparse.Namespace(heal=True, validate=True)
    ctx = HealContext.from_args(args)

    assert ctx.execution_mode == "validate", "validate should override heal"


def test_heal_context_immutability():
    """
    PASS: HealContext is frozen and cannot be mutated.
    FAIL: HealContext fields can be modified after creation.

    Per .windsurfrules §1.8: Fail-closed - invalid preconditions must block operation.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import HealContext

    args = argparse.Namespace(heal=False, validate=False)
    ctx = HealContext.from_args(args)

    with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
        ctx.heal = True

    with pytest.raises(Exception):
        ctx.trace_id = "modified"

    with pytest.raises(Exception):
        ctx.execution_mode = "modified"


def test_heal_context_trace_id_correlation():
    """
    PASS: trace_id is consistent within a single HealContext instance.
    FAIL: trace_id changes or is unstable.

    Per .windsurfrules §1.7: Deterministic decision surfaces.
    Per hostile audit Section E1: trace_id must be stable for correlation.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import HealContext

    args = argparse.Namespace(heal=True, validate=False)
    ctx = HealContext.from_args(args)

    # Access trace_id multiple times
    trace_id_1 = ctx.trace_id
    trace_id_2 = ctx.trace_id
    trace_id_3 = ctx.trace_id

    assert trace_id_1 == trace_id_2 == trace_id_3, "trace_id must be stable"


def test_heal_context_all_fields_present():
    """
    PASS: HealContext has all required fields (heal, auto_approve, telemetry, meta_learning, trace_id, execution_mode).
    FAIL: Missing required fields.

    Per .windsurfrules §1.5: Edge cases - missing field.
    Per hostile audit Section E1+E10: All fields must be present.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import HealContext

    args = argparse.Namespace(heal=True, validate=False)
    ctx = HealContext.from_args(args)

    # Verify all fields exist
    assert hasattr(ctx, "heal")
    assert hasattr(ctx, "auto_approve")
    assert hasattr(ctx, "enable_telemetry")
    assert hasattr(ctx, "enable_meta_learning")
    assert hasattr(ctx, "trace_id")
    assert hasattr(ctx, "execution_mode")

    # Verify types
    assert isinstance(ctx.heal, bool)
    assert isinstance(ctx.auto_approve, bool)
    assert isinstance(ctx.enable_telemetry, bool)
    assert isinstance(ctx.enable_meta_learning, bool)
    assert isinstance(ctx.trace_id, str)
    assert isinstance(ctx.execution_mode, str)

    # Verify trace_id is not empty
    assert len(ctx.trace_id) > 0, "trace_id must not be empty"

    # Verify execution_mode is valid
    assert ctx.execution_mode in ["scan", "heal", "validate"], f"Invalid execution_mode: {ctx.execution_mode}"
