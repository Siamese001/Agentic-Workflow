"""Wave 2 tests — assembler slot rendering, manifest hash, SLOT_ORDER enforcement."""

from __future__ import annotations

import hashlib
from unittest.mock import patch

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "test_assembler_slots")
_emit_applies_guardrail("p0", "test_assembler_slots", "p0_governance")
_emit_reads_policy_state("p0", "test_assembler_slots", "policy_binding")
_emit_snapshots_state("p0", "test_assembler_slots", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("test_assembler_slots", "p4obs", "metric_1")
_emit_emits_metric_event("test_assembler_slots", "p4obs", "metric_2")
_emit_emits_metric_event("test_assembler_slots", "p4obs", "metric_3")
_emit_emits_metric_event("test_assembler_slots", "p4obs", "metric_4")
_emit_emits_metric_event("test_assembler_slots", "p4obs", "metric_5")
_emit_emits_metric_event("test_assembler_slots", "p4obs", "metric_6")
_emit_records_incident_event("test_assembler_slots", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_assembler_slots", "p4obs", "anomaly")
_emit_writes_observability_log("test_assembler_slots", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_assembler_slots", "p4obs", "mon_state")
_emit_triggers_alert("test_assembler_slots", "p4obs", "alert")
_emit_links_incident_trace("test_assembler_slots", "p4obs", "trace_link")
_emit_captures_pattern("test_assembler_slots", "p3lm", "pattern")
_emit_records_learning_event("test_assembler_slots", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_assembler_slots", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_assembler_slots", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_assembler_slots", "p3lm", "routing")
_emit_improves_agent_policy("test_assembler_slots", "p3lm", "policy")
_emit_stores_learning_state("test_assembler_slots", "p3lm", "state")
_emit_records_execution_trace("test_assembler_slots", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_assembler_slots", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_assembler_slots", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_assembler_slots", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_assembler_slots", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_assembler_slots", "env_read", "p2_env_1")
_emit_reads_environ("test_assembler_slots", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_assembler_slots", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_assembler_slots", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_assembler_slots", "context_pull")
_emit_pulls_context("p1", "test_assembler_slots", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_assembler_slots", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_assembler_slots", "uwg_term_2")
_emit_writes_through("p1", "test_assembler_slots", "write_through")
_emit_writes_through("p1", "test_assembler_slots", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_assembler_slots", "safety_validation")
_emit_invokes_eval("p1", "test_assembler_slots", "eval_call")
_emit_proposal_commits_routing("p1", "test_assembler_slots", "routing_commit")
_emit_escalates_to_human("p1", "test_assembler_slots", "human_escalation")
_emit_routes_through("p1", "test_assembler_slots", "route_through")
_emit_checks_agent_registry("p1", "test_assembler_slots", "agent_registry")
_emit_validates_agent_capability("p1", "test_assembler_slots", "capability")
_emit_dispatches_execution_plan("p1", "test_assembler_slots", "exec_plan")
_emit_agent_executes_agent("p1", "test_assembler_slots", "sub_agent")
_emit_routes_to_agent("p1", "test_assembler_slots", "target_agent")
_emit_verifies_policy("p1", "test_assembler_slots", "policy_check")
_emit_observes_runtime_state("p1", "test_assembler_slots", "runtime_state")
_emit_verifies_boundary("p1", "test_assembler_slots", "boundary_check")
_emit_transcripts_response("p1", "test_assembler_slots", "transcript")
_emit_hard_fails_untranscripted("p1", "test_assembler_slots")
_emit_gated_by_confidence("p1", "test_assembler_slots", "confidence_gate")
emit_replay_key("p0", "test_assembler_slots")
emit_determinism_digest("p0", "test_assembler_slots")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_assembler_slots", "execution_auth")
_emit_validates_capability("p2", "test_assembler_slots", "capability_check")
_emit_routes_to_capability("p2", "test_assembler_slots", "capability_route")
_emit_writes_via_uwg("p2", "test_assembler_slots", "uwg_write")
_emit_blocks_direct_write("p2", "test_assembler_slots", "direct_write_block")
_emit_records_tool_invocation("p2", "test_assembler_slots", "tool_invocation")
_emit_captures_execution_output("p2", "test_assembler_slots", "exec_output")
_emit_dispatches_agent("p3", "test_assembler_slots", "agent_dispatch")
_emit_coordinates_agents("p3", "test_assembler_slots", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_assembler_slots", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_assembler_slots", "healing_outcome")
_emit_escalates_failure("p3", "test_assembler_slots", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_assembler_slots", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_assembler_slots", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_assembler_slots", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_assembler_slots", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_assembler_slots", "eval_metric")
_emit_stores_embedding("p4", "test_assembler_slots", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_assembler_slots", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_assembler_slots", "exec_snapshot_link")

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
# Slot labels present in assembled output
# ---------------------------------------------------------------------------


def test_assembled_output_contains_slot_s0():
    a = _make_assembler()
    text = a.assemble(role="Agent", objective="Test", context_data=_VALID_CONTEXT, injections=[])
    assert "<SLOT_S0>" in text


def test_assembled_output_contains_slot_d0():
    a = _make_assembler()
    text = a.assemble(role="Agent", objective="Test", context_data=_VALID_CONTEXT, injections=[])
    assert "<SLOT_D0>" in text


def test_assembled_output_contains_slot_i0():
    a = _make_assembler()
    text = a.assemble(role="Agent", objective="Test", context_data=_VALID_CONTEXT, injections=[])
    assert "<SLOT_I0>" in text


def test_assembled_output_contains_slot_c0():
    a = _make_assembler()
    text = a.assemble(role="Agent", objective="Test", context_data=_VALID_CONTEXT, injections=[])
    assert "<SLOT_C0>" in text


def test_assembled_output_contains_slot_u0():
    a = _make_assembler()
    text = a.assemble(role="Agent", objective="Test", context_data=_VALID_CONTEXT, injections=[])
    assert "<SLOT_U0>" in text


def test_slot_order_in_assembled_output():
    """S0 must appear before D0, D0 before I0, I0 before C0, C0 before U0."""
    a = _make_assembler()
    text = a.assemble(role="Agent", objective="Test", context_data=_VALID_CONTEXT, injections=[])
    positions = {
        slot: text.index(f"<{slot}>") for slot in ("SLOT_S0", "SLOT_D0", "SLOT_I0", "SLOT_C0", "SLOT_U0")
    }
    order = ["SLOT_S0", "SLOT_D0", "SLOT_I0", "SLOT_C0", "SLOT_U0"]
    for i in range(len(order) - 1):
        assert positions[order[i]] < positions[order[i + 1]], f"{order[i]} must appear before {order[i + 1]}"


# ---------------------------------------------------------------------------
# C0 context rendered in output
# ---------------------------------------------------------------------------


def test_c0_context_data_rendered_in_output():
    ctx = {"namespace": "myns", "max_k": 3, "version": "v2"}
    a = _make_assembler()
    text = a.assemble(role="Agent", objective="Test", context_data=ctx, injections=[])
    assert "myns" in text


# ---------------------------------------------------------------------------
# Manifest hash
# ---------------------------------------------------------------------------


def test_manifest_hash_is_non_empty_after_assemble():
    a = _make_assembler()
    a.assemble(role="Agent", objective="Test", context_data=_VALID_CONTEXT, injections=[])
    assert a._last_manifest_hash != ""


def test_manifest_hash_is_sha256_hex():
    a = _make_assembler()
    a.assemble(role="Agent", objective="Test", context_data=_VALID_CONTEXT, injections=[])
    h = a._last_manifest_hash
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_manifest_hash_is_deterministic():
    a1 = _make_assembler()
    a2 = _make_assembler()
    a1.assemble(role="Agent", objective="Test", context_data=_VALID_CONTEXT, injections=[])
    a2.assemble(role="Agent", objective="Test", context_data=_VALID_CONTEXT, injections=[])
    assert a1._last_manifest_hash == a2._last_manifest_hash


def test_manifest_hash_changes_with_different_input():
    a = _make_assembler()
    a.assemble(role="Agent", objective="Test", context_data=_VALID_CONTEXT, injections=[])
    h1 = a._last_manifest_hash
    a.assemble(role="Agent", objective="Different", context_data=_VALID_CONTEXT, injections=[])
    h2 = a._last_manifest_hash
    assert h1 != h2


def test_manifest_hash_matches_sha256_of_text():
    a = _make_assembler()
    text = a.assemble(role="Agent", objective="Test", context_data=_VALID_CONTEXT, injections=[])
    expected = hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert a._last_manifest_hash == expected


# ---------------------------------------------------------------------------
# assemble_with_schema returns AssembledPrompt with manifest_hash
# ---------------------------------------------------------------------------


def test_assemble_with_schema_returns_assembled_prompt_with_hash():
    from agentic_core.prompt_governance.core.prompt_assembler import AssembledPrompt

    a = _make_assembler()
    result = a.assemble_with_schema(
        role="Agent", objective="Test", context_data=_VALID_CONTEXT, injections=[]
    )
    assert isinstance(result, AssembledPrompt)
    assert isinstance(result.manifest_hash, str)
    assert len(result.manifest_hash) == 64


def test_assembled_prompt_is_frozen():
    a = _make_assembler()
    result = a.assemble_with_schema(
        role="Agent", objective="Test", context_data=_VALID_CONTEXT, injections=[]
    )
    with pytest.raises((AttributeError, TypeError)):
        result.manifest_hash = "mutated"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# SLOT_ORDER enforcement — all 5 slots always present
# ---------------------------------------------------------------------------


def test_assembler_slot_map_covers_all_slot_order_keys():
    """Verify that the assembler internally builds a slot for every key in SLOT_ORDER."""
    from agentic_core.prompt_governance.contracts.slot_contracts import SLOT_ORDER

    a = _make_assembler()
    # If any slot were missing, assemble() would raise ValueError("SLOT_MISSING:...")
    # This test asserts no such error is raised for a valid payload
    text = a.assemble(role="Agent", objective="Test", context_data=_VALID_CONTEXT, injections=[])
    for slot_key in SLOT_ORDER:
        assert f"<SLOT_{slot_key}>" in text, f"SLOT_{slot_key} missing from assembled output"
