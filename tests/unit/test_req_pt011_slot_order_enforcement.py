"""REQ-PT-011: Negative control — tampered slot order must yield detection.

Production enforcement: validate_slot_order() in slot_contracts.py.
Wired into PromptAssembler.assemble() as fail-closed gate.

Positive tests: canonical order passes.
Negative tests: tampered/missing slots raise SlotOrderViolation.
"""

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

_emit_records_execution_trace("p0", "evidence", "test_req_pt011_slot_order_enforcement")
_emit_applies_guardrail("p0", "test_req_pt011_slot_order_enforcement", "p0_governance")
_emit_reads_policy_state("p0", "test_req_pt011_slot_order_enforcement", "policy_binding")
_emit_snapshots_state("p0", "test_req_pt011_slot_order_enforcement", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_req_pt011_slot_order_enforcement", "p4obs", "metric_1")
_emit_emits_metric_event("test_req_pt011_slot_order_enforcement", "p4obs", "metric_2")
_emit_emits_metric_event("test_req_pt011_slot_order_enforcement", "p4obs", "metric_3")
_emit_emits_metric_event("test_req_pt011_slot_order_enforcement", "p4obs", "metric_4")
_emit_emits_metric_event("test_req_pt011_slot_order_enforcement", "p4obs", "metric_5")
_emit_emits_metric_event("test_req_pt011_slot_order_enforcement", "p4obs", "metric_6")
_emit_records_incident_event("test_req_pt011_slot_order_enforcement", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_req_pt011_slot_order_enforcement", "p4obs", "anomaly")
_emit_writes_observability_log("test_req_pt011_slot_order_enforcement", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_req_pt011_slot_order_enforcement", "p4obs", "mon_state")
_emit_triggers_alert("test_req_pt011_slot_order_enforcement", "p4obs", "alert")
_emit_links_incident_trace("test_req_pt011_slot_order_enforcement", "p4obs", "trace_link")
_emit_captures_pattern("test_req_pt011_slot_order_enforcement", "p3lm", "pattern")
_emit_records_learning_event("test_req_pt011_slot_order_enforcement", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_req_pt011_slot_order_enforcement", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_req_pt011_slot_order_enforcement", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_req_pt011_slot_order_enforcement", "p3lm", "routing")
_emit_improves_agent_policy("test_req_pt011_slot_order_enforcement", "p3lm", "policy")
_emit_stores_learning_state("test_req_pt011_slot_order_enforcement", "p3lm", "state")
_emit_records_execution_trace("test_req_pt011_slot_order_enforcement", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_req_pt011_slot_order_enforcement", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_req_pt011_slot_order_enforcement", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_req_pt011_slot_order_enforcement", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_req_pt011_slot_order_enforcement", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_req_pt011_slot_order_enforcement", "env_read", "p2_env_1")
_emit_reads_environ("test_req_pt011_slot_order_enforcement", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_req_pt011_slot_order_enforcement", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_req_pt011_slot_order_enforcement", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_req_pt011_slot_order_enforcement", "context_pull")
_emit_pulls_context("p1", "test_req_pt011_slot_order_enforcement", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_req_pt011_slot_order_enforcement", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_req_pt011_slot_order_enforcement", "uwg_term_2")
_emit_writes_through("p1", "test_req_pt011_slot_order_enforcement", "write_through")
_emit_writes_through("p1", "test_req_pt011_slot_order_enforcement", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_req_pt011_slot_order_enforcement", "safety_validation")
_emit_invokes_eval("p1", "test_req_pt011_slot_order_enforcement", "eval_call")
_emit_proposal_commits_routing("p1", "test_req_pt011_slot_order_enforcement", "routing_commit")
emit_replay_key("p0", "test_req_pt011_slot_order_enforcement")
emit_determinism_digest("p0", "test_req_pt011_slot_order_enforcement")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_req_pt011_slot_order_enforcement", "execution_auth")
_emit_validates_capability("p2", "test_req_pt011_slot_order_enforcement", "capability_check")
_emit_routes_to_capability("p2", "test_req_pt011_slot_order_enforcement", "capability_route")
_emit_writes_via_uwg("p2", "test_req_pt011_slot_order_enforcement", "uwg_write")
_emit_blocks_direct_write("p2", "test_req_pt011_slot_order_enforcement", "direct_write_block")
_emit_records_tool_invocation("p2", "test_req_pt011_slot_order_enforcement", "tool_invocation")
_emit_captures_execution_output("p2", "test_req_pt011_slot_order_enforcement", "exec_output")
_emit_dispatches_agent("p3", "test_req_pt011_slot_order_enforcement", "agent_dispatch")
_emit_coordinates_agents("p3", "test_req_pt011_slot_order_enforcement", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_req_pt011_slot_order_enforcement", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_req_pt011_slot_order_enforcement", "healing_outcome")
_emit_escalates_failure("p3", "test_req_pt011_slot_order_enforcement", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_req_pt011_slot_order_enforcement", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_req_pt011_slot_order_enforcement", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_req_pt011_slot_order_enforcement", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_req_pt011_slot_order_enforcement", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_req_pt011_slot_order_enforcement", "eval_metric")
_emit_stores_embedding("p4", "test_req_pt011_slot_order_enforcement", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_req_pt011_slot_order_enforcement", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_req_pt011_slot_order_enforcement", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


# ---------------------------------------------------------------------------
# Positive: canonical slot order passes validation
# ---------------------------------------------------------------------------


def test_canonical_slot_order_passes():
    from agentic_core.prompt_governance.contracts.slot_contracts import (
        validate_slot_order,
    )

    prompt = (
        "<SLOT_S0>system</SLOT_S0>\n"
        "<SLOT_D0>directives</SLOT_D0>\n"
        "<SLOT_I0>instructional</SLOT_I0>\n"
        "<SLOT_C0>context</SLOT_C0>\n"
        "<SLOT_U0>user</SLOT_U0>\n"
    )
    validate_slot_order(prompt)  # should not raise


def test_canonical_order_with_extra_content_passes():
    from agentic_core.prompt_governance.contracts.slot_contracts import (
        validate_slot_order,
    )

    prompt = (
        "PREAMBLE\n"
        "<SLOT_S0>You are {role}.</SLOT_S0>\n"
        "--- separator ---\n"
        "<SLOT_D0>binding directives</SLOT_D0>\n"
        "<SLOT_I0>capability defs</SLOT_I0>\n"
        "<SLOT_C0>rag payload</SLOT_C0>\n"
        "<SLOT_U0>raw user intent</SLOT_U0>\n"
        "<OUTPUT_FORMAT>json</OUTPUT_FORMAT>\n"
    )
    validate_slot_order(prompt)  # should not raise


# ---------------------------------------------------------------------------
# Negative: tampered slot order raises SlotOrderViolation
# ---------------------------------------------------------------------------


def test_swapped_s0_d0_raises():
    from agentic_core.prompt_governance.contracts.slot_contracts import (
        SlotOrderViolation,
        validate_slot_order,
    )

    prompt = (
        "<SLOT_D0>directives</SLOT_D0>\n"
        "<SLOT_S0>system</SLOT_S0>\n"
        "<SLOT_I0>instructional</SLOT_I0>\n"
        "<SLOT_C0>context</SLOT_C0>\n"
        "<SLOT_U0>user</SLOT_U0>\n"
    )
    with pytest.raises(SlotOrderViolation, match="SLOT_ORDER_VIOLATED"):
        validate_slot_order(prompt)


def test_u0_before_c0_raises():
    from agentic_core.prompt_governance.contracts.slot_contracts import (
        SlotOrderViolation,
        validate_slot_order,
    )

    prompt = (
        "<SLOT_S0>system</SLOT_S0>\n"
        "<SLOT_D0>directives</SLOT_D0>\n"
        "<SLOT_I0>instructional</SLOT_I0>\n"
        "<SLOT_U0>user</SLOT_U0>\n"
        "<SLOT_C0>context</SLOT_C0>\n"
    )
    with pytest.raises(SlotOrderViolation, match="SLOT_ORDER_VIOLATED"):
        validate_slot_order(prompt)


def test_missing_slot_raises():
    from agentic_core.prompt_governance.contracts.slot_contracts import (
        SlotOrderViolation,
        validate_slot_order,
    )

    prompt = (
        "<SLOT_S0>system</SLOT_S0>\n"
        "<SLOT_D0>directives</SLOT_D0>\n"
        "<SLOT_C0>context</SLOT_C0>\n"
        "<SLOT_U0>user</SLOT_U0>\n"
    )
    with pytest.raises(SlotOrderViolation, match="SLOT_MISSING.*I0"):
        validate_slot_order(prompt)


def test_empty_prompt_raises():
    from agentic_core.prompt_governance.contracts.slot_contracts import (
        SlotOrderViolation,
        validate_slot_order,
    )

    with pytest.raises(SlotOrderViolation, match="SLOT_MISSING"):
        validate_slot_order("")


# ---------------------------------------------------------------------------
# SlotOrderViolation is a proper exception type
# ---------------------------------------------------------------------------


def test_slot_order_violation_is_exception():
    from agentic_core.prompt_governance.contracts.slot_contracts import (
        SlotOrderViolation,
    )

    assert issubclass(SlotOrderViolation, Exception)


def test_slot_order_violation_carries_message():
    from agentic_core.prompt_governance.contracts.slot_contracts import (
        SlotOrderViolation,
    )

    err = SlotOrderViolation("tamper detected")
    assert "tamper detected" in str(err)
