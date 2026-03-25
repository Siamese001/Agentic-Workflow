"""Wave 3 tests — healer re-entry gate + airlock enforcement."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_healer_gate")
# REMOVED: _emit_applies_guardrail("p0", "test_healer_gate", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_healer_gate", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_healer_gate", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
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
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_healer_gate", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_healer_gate", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_healer_gate", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_healer_gate", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_healer_gate", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_healer_gate", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_healer_gate", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_healer_gate", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_healer_gate", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_healer_gate", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_healer_gate", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_healer_gate", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_healer_gate", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_healer_gate", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_healer_gate", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_healer_gate", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_healer_gate", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_healer_gate", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_healer_gate", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_healer_gate", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_healer_gate", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_healer_gate", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_healer_gate", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_healer_gate", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_healer_gate", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_healer_gate", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_healer_gate", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_healer_gate", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_healer_gate", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_healer_gate", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_healer_gate", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_healer_gate", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_healer_gate", "write_through")
# REMOVED: _emit_writes_through("p1", "test_healer_gate", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_healer_gate", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_healer_gate", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_healer_gate", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_healer_gate", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_healer_gate", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_healer_gate", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_healer_gate", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_healer_gate", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_healer_gate", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_healer_gate", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_healer_gate", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_healer_gate", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_healer_gate", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_healer_gate", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_healer_gate")
# REMOVED: _emit_gated_by_confidence("p1", "test_healer_gate", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_healer_gate")
# REMOVED: emit_determinism_digest("p0", "test_healer_gate")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_healer_gate", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_healer_gate", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_healer_gate", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_healer_gate", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_healer_gate", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_healer_gate", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_healer_gate", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_healer_gate", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_healer_gate", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_healer_gate", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_healer_gate", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_healer_gate", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_healer_gate", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_healer_gate", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_healer_gate", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_healer_gate", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_healer_gate", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_healer_gate", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_healer_gate", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_healer_gate", "exec_snapshot_link")

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

_VALID_CONTEXT = {"namespace": "ns1", "max_k": 5, "version": "v1"}


def _make_assembler():
    from agentic_core.prompt_governance.core.prompt_assembler import PromptAssembler

    with patch(
        "agentic_core.prompt_governance.core.prompt_assembler.PromptAssembler._load_templates",
        return_value=None,
    ):
        return PromptAssembler()


# ---------------------------------------------------------------------------
# validate_healer_reentry
# ---------------------------------------------------------------------------


def test_healer_reentry_valid_passes():
    from agentic_core.prompt_governance.security.validators.output_schema_validator import (
        validate_healer_reentry,
    )

    ok, code = validate_healer_reentry({"healing_proposal": True, "reentry_gate": True})
    assert ok is True
    assert code is None


def test_healer_reentry_missing_gate_fails():
    from agentic_core.prompt_governance.security.validators.output_schema_validator import (
        validate_healer_reentry,
    )

    ok, code = validate_healer_reentry({"healing_proposal": True})
    assert ok is False
    assert code == "HEALER_REENTRY_VIOLATION"


def test_healer_reentry_gate_false_fails():
    from agentic_core.prompt_governance.security.validators.output_schema_validator import (
        validate_healer_reentry,
    )

    ok, code = validate_healer_reentry({"healing_proposal": True, "reentry_gate": False})
    assert ok is False
    assert code == "HEALER_REENTRY_VIOLATION"


def test_healer_reentry_no_healing_proposal_passes():
    from agentic_core.prompt_governance.security.validators.output_schema_validator import (
        validate_healer_reentry,
    )

    ok, code = validate_healer_reentry({"other": "data"})
    assert ok is True
    assert code is None


def test_healer_reentry_mutation_marker_fails():
    from agentic_core.prompt_governance.security.validators.output_schema_validator import (
        validate_healer_reentry,
    )

    ok, code = validate_healer_reentry(
        {"healing_proposal": True, "reentry_gate": True, "action": "durable_write"}
    )
    assert ok is False
    assert code == "HEALER_REENTRY_VIOLATION"


def test_healer_reentry_error_code_is_uppercase():
    from agentic_core.prompt_governance.security.validators import output_schema_validator as osv

    assert osv.HEALER_REENTRY_VIOLATION == osv.HEALER_REENTRY_VIOLATION.upper()


def test_healer_reentry_non_dict_fails():
    from agentic_core.prompt_governance.security.validators.output_schema_validator import (
        validate_healer_reentry,
    )

    ok, code = validate_healer_reentry("not a dict")  # type: ignore[arg-type]
    assert ok is False
    assert code == "HEALER_REENTRY_VIOLATION"


# ---------------------------------------------------------------------------
# Airlock enforcement in assembler
# ---------------------------------------------------------------------------


def test_airlock_violation_raised_on_u0_bypass_flag():
    from agentic_core.prompt_governance.contracts.slot_contracts import AirlockViolationError

    a = _make_assembler()
    with pytest.raises(AirlockViolationError, match="AIRLOCK_VIOLATION"):
        a.assemble(
            role="Agent",
            objective="Test",
            context_data=_VALID_CONTEXT,
            injections=[],
            metadata={"_u0_bypass": True},
        )


def test_airlock_not_raised_without_bypass_flag():
    a = _make_assembler()
    text = a.assemble(
        role="Agent",
        objective="Test",
        context_data=_VALID_CONTEXT,
        injections=[],
        metadata={"other": "data"},
    )
    assert isinstance(text, str)


# ---------------------------------------------------------------------------
# Healer directive injection in assembler
# ---------------------------------------------------------------------------


def test_healer_directive_injected_in_d0_when_healing_proposal():
    a = _make_assembler()
    text = a.assemble(
        role="Agent",
        objective="Test",
        context_data=_VALID_CONTEXT,
        injections=[],
        metadata={"healing_proposal": True, "reentry_gate": True},
    )
    assert "<HEALER_DIRECTIVE>" in text


def test_healer_directive_not_injected_without_healing_flag():
    from agentic_core.prompt_governance.core.invariant_registry import ITERATIVE_FEEDBACK_DIRECTIVE

    a = _make_assembler()
    text = a.assemble(
        role="Agent",
        objective="Test",
        context_data=_VALID_CONTEXT,
        injections=[],
    )
    assert ITERATIVE_FEEDBACK_DIRECTIVE not in text


def test_assembler_rejects_healing_proposal_without_reentry_gate():
    from agentic_core.prompt_governance.core.prompt_assembler import SecurityIntegrityError

    a = _make_assembler()
    with pytest.raises(SecurityIntegrityError, match="HEALER_REENTRY_VIOLATION"):
        a.assemble(
            role="Agent",
            objective="Test",
            context_data=_VALID_CONTEXT,
            injections=[],
            metadata={"healing_proposal": True},
        )
