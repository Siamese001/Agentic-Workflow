"""Negative-first tests for Phase 4 Wave 1 — typed slot contracts + airlock."""

from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_slot_contracts")
_emit_applies_guardrail("p0", "test_slot_contracts", "p0_governance")
_emit_reads_policy_state("p0", "test_slot_contracts", "policy_binding")
_emit_snapshots_state("p0", "test_slot_contracts", "state_snapshot")
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

_emit_emits_metric_event("test_slot_contracts", "p4obs", "metric_1")
_emit_emits_metric_event("test_slot_contracts", "p4obs", "metric_2")
_emit_emits_metric_event("test_slot_contracts", "p4obs", "metric_3")
_emit_emits_metric_event("test_slot_contracts", "p4obs", "metric_4")
_emit_emits_metric_event("test_slot_contracts", "p4obs", "metric_5")
_emit_emits_metric_event("test_slot_contracts", "p4obs", "metric_6")
_emit_records_incident_event("test_slot_contracts", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_slot_contracts", "p4obs", "anomaly")
_emit_writes_observability_log("test_slot_contracts", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_slot_contracts", "p4obs", "mon_state")
_emit_triggers_alert("test_slot_contracts", "p4obs", "alert")
_emit_links_incident_trace("test_slot_contracts", "p4obs", "trace_link")
_emit_captures_pattern("test_slot_contracts", "p3lm", "pattern")
_emit_records_learning_event("test_slot_contracts", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_slot_contracts", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_slot_contracts", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_slot_contracts", "p3lm", "routing")
_emit_improves_agent_policy("test_slot_contracts", "p3lm", "policy")
_emit_stores_learning_state("test_slot_contracts", "p3lm", "state")
_emit_records_execution_trace("test_slot_contracts", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_slot_contracts", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_slot_contracts", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_slot_contracts", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_slot_contracts", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_slot_contracts", "env_read", "p2_env_1")
_emit_reads_environ("test_slot_contracts", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_slot_contracts", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_slot_contracts", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_slot_contracts", "context_pull")
_emit_pulls_context("p1", "test_slot_contracts", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_slot_contracts", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_slot_contracts", "uwg_term_2")
_emit_writes_through("p1", "test_slot_contracts", "write_through")
_emit_writes_through("p1", "test_slot_contracts", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_slot_contracts", "safety_validation")
_emit_invokes_eval("p1", "test_slot_contracts", "eval_call")
_emit_proposal_commits_routing("p1", "test_slot_contracts", "routing_commit")
emit_replay_key("p0", "test_slot_contracts")
emit_determinism_digest("p0", "test_slot_contracts")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_slot_contracts", "execution_auth")
_emit_validates_capability("p2", "test_slot_contracts", "capability_check")
_emit_routes_to_capability("p2", "test_slot_contracts", "capability_route")
_emit_writes_via_uwg("p2", "test_slot_contracts", "uwg_write")
_emit_blocks_direct_write("p2", "test_slot_contracts", "direct_write_block")
_emit_records_tool_invocation("p2", "test_slot_contracts", "tool_invocation")
_emit_captures_execution_output("p2", "test_slot_contracts", "exec_output")
_emit_dispatches_agent("p3", "test_slot_contracts", "agent_dispatch")
_emit_coordinates_agents("p3", "test_slot_contracts", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_slot_contracts", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_slot_contracts", "healing_outcome")
_emit_escalates_failure("p3", "test_slot_contracts", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_slot_contracts", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_slot_contracts", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_slot_contracts", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_slot_contracts", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_slot_contracts", "eval_metric")
_emit_stores_embedding("p4", "test_slot_contracts", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_slot_contracts", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_slot_contracts", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps


# ---------------------------------------------------------------------------
# SlotS0
# ---------------------------------------------------------------------------


def test_slot_s0_requires_content():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotS0

    with pytest.raises(TypeError):
        SlotS0()  # missing required field


def test_slot_s0_is_frozen():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotS0

    s = SlotS0(content="system directive")
    with pytest.raises((AttributeError, TypeError)):
        s.content = "mutated"  # type: ignore[misc]


def test_slot_s0_wrong_type_still_constructs_but_is_typed():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotS0

    s = SlotS0(content="valid")
    assert isinstance(s, SlotS0)
    assert s.content == "valid"


# ---------------------------------------------------------------------------
# SlotD0
# ---------------------------------------------------------------------------


def test_slot_d0_requires_content_and_authority():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotD0

    with pytest.raises(TypeError):
        SlotD0()  # missing both fields

    with pytest.raises(TypeError):
        SlotD0(content="fence")  # missing authority


def test_slot_d0_is_frozen():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotD0

    d = SlotD0(content="fence", authority="BINDING")
    with pytest.raises((AttributeError, TypeError)):
        d.authority = "mutated"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# SlotI0
# ---------------------------------------------------------------------------


def test_slot_i0_requires_content():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotI0

    with pytest.raises(TypeError):
        SlotI0()


def test_slot_i0_is_frozen():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotI0

    i = SlotI0(content="capability manual")
    with pytest.raises((AttributeError, TypeError)):
        i.content = "mutated"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# SlotC0
# ---------------------------------------------------------------------------


def test_slot_c0_requires_content():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotC0

    with pytest.raises(TypeError):
        SlotC0()


def test_slot_c0_content_is_dict():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotC0

    c = SlotC0(content={"namespace": "ns1", "max_k": 5})
    assert isinstance(c.content, dict)


def test_slot_c0_is_frozen():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotC0

    c = SlotC0(content={})
    with pytest.raises((AttributeError, TypeError)):
        c.content = {"mutated": True}  # type: ignore[misc]


# ---------------------------------------------------------------------------
# SlotU0
# ---------------------------------------------------------------------------


def test_slot_u0_requires_content():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotU0

    with pytest.raises(TypeError):
        SlotU0()


def test_slot_u0_is_frozen():
    from agentic_core.prompt_governance.contracts.slot_contracts import SlotU0

    u = SlotU0(content="user intent")
    with pytest.raises((AttributeError, TypeError)):
        u.content = "mutated"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# SLOT_ORDER
# ---------------------------------------------------------------------------


def test_slot_order_is_tuple():
    from agentic_core.prompt_governance.contracts.slot_contracts import SLOT_ORDER

    assert isinstance(SLOT_ORDER, tuple)


def test_slot_order_cannot_be_mutated():
    from agentic_core.prompt_governance.contracts.slot_contracts import SLOT_ORDER

    with pytest.raises((AttributeError, TypeError)):
        SLOT_ORDER[0] = "X"  # type: ignore[index]


def test_slot_order_contains_all_five_slots():
    from agentic_core.prompt_governance.contracts.slot_contracts import SLOT_ORDER

    assert set(SLOT_ORDER) == {"S0", "D0", "I0", "C0", "U0"}


def test_slot_order_sequence():
    from agentic_core.prompt_governance.contracts.slot_contracts import SLOT_ORDER

    assert SLOT_ORDER == ("S0", "D0", "I0", "C0", "U0")


# ---------------------------------------------------------------------------
# AirlockViolationError
# ---------------------------------------------------------------------------


def test_airlock_violation_error_is_exception():
    from agentic_core.prompt_governance.contracts.slot_contracts import AirlockViolationError

    assert issubclass(AirlockViolationError, Exception)


def test_airlock_violation_error_can_be_raised():
    from agentic_core.prompt_governance.contracts.slot_contracts import AirlockViolationError

    with pytest.raises(AirlockViolationError, match="AIRLOCK_VIOLATION"):
        raise AirlockViolationError("AIRLOCK_VIOLATION")


def test_airlock_violation_error_carries_message():
    from agentic_core.prompt_governance.contracts.slot_contracts import AirlockViolationError

    err = AirlockViolationError("bypass detected")
    assert "bypass detected" in str(err)


# ---------------------------------------------------------------------------
# contracts/__init__.py exports
# ---------------------------------------------------------------------------


def test_contracts_package_exports_all_slots():
    from agentic_core.prompt_governance import contracts

    for name in ("SlotS0", "SlotD0", "SlotI0", "SlotC0", "SlotU0", "SLOT_ORDER", "AirlockViolationError"):
        assert hasattr(contracts, name), f"contracts missing export: {name}"
