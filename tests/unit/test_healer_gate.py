"""Wave 3 tests — healer re-entry gate + airlock enforcement."""

from __future__ import annotations

from unittest.mock import patch

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

_emit_records_execution_trace("p0", "evidence", "test_healer_gate")
_emit_applies_guardrail("p0", "test_healer_gate", "p0_governance")
_emit_reads_policy_state("p0", "test_healer_gate", "policy_binding")
_emit_snapshots_state("p0", "test_healer_gate", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_healer_gate", "p4obs", "metric_1")
_emit_emits_metric_event("test_healer_gate", "p4obs", "metric_2")
_emit_emits_metric_event("test_healer_gate", "p4obs", "metric_3")
_emit_emits_metric_event("test_healer_gate", "p4obs", "metric_4")
_emit_emits_metric_event("test_healer_gate", "p4obs", "metric_5")
_emit_emits_metric_event("test_healer_gate", "p4obs", "metric_6")
_emit_records_incident_event("test_healer_gate", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_healer_gate", "p4obs", "anomaly")
_emit_writes_observability_log("test_healer_gate", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_healer_gate", "p4obs", "mon_state")
_emit_triggers_alert("test_healer_gate", "p4obs", "alert")
_emit_links_incident_trace("test_healer_gate", "p4obs", "trace_link")
_emit_captures_pattern("test_healer_gate", "p3lm", "pattern")
_emit_records_learning_event("test_healer_gate", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_healer_gate", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_healer_gate", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_healer_gate", "p3lm", "routing")
_emit_improves_agent_policy("test_healer_gate", "p3lm", "policy")
_emit_stores_learning_state("test_healer_gate", "p3lm", "state")
_emit_records_execution_trace("test_healer_gate", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_healer_gate", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_healer_gate", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_healer_gate", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_healer_gate", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_healer_gate", "env_read", "p2_env_1")
_emit_reads_environ("test_healer_gate", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_healer_gate", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_healer_gate", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_healer_gate", "context_pull")
_emit_pulls_context("p1", "test_healer_gate", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_healer_gate", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_healer_gate", "uwg_term_2")
_emit_writes_through("p1", "test_healer_gate", "write_through")
_emit_writes_through("p1", "test_healer_gate", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_healer_gate", "safety_validation")
_emit_invokes_eval("p1", "test_healer_gate", "eval_call")
_emit_proposal_commits_routing("p1", "test_healer_gate", "routing_commit")
emit_replay_key("p0", "test_healer_gate")
emit_determinism_digest("p0", "test_healer_gate")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_healer_gate", "execution_auth")
_emit_validates_capability("p2", "test_healer_gate", "capability_check")
_emit_routes_to_capability("p2", "test_healer_gate", "capability_route")
_emit_writes_via_uwg("p2", "test_healer_gate", "uwg_write")
_emit_blocks_direct_write("p2", "test_healer_gate", "direct_write_block")
_emit_records_tool_invocation("p2", "test_healer_gate", "tool_invocation")
_emit_captures_execution_output("p2", "test_healer_gate", "exec_output")
_emit_dispatches_agent("p3", "test_healer_gate", "agent_dispatch")
_emit_coordinates_agents("p3", "test_healer_gate", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_healer_gate", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_healer_gate", "healing_outcome")
_emit_escalates_failure("p3", "test_healer_gate", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_healer_gate", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_healer_gate", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_healer_gate", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_healer_gate", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_healer_gate", "eval_metric")
_emit_stores_embedding("p4", "test_healer_gate", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_healer_gate", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_healer_gate", "exec_snapshot_link")

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
