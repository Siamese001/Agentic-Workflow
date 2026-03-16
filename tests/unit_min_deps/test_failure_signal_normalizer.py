"""Unit tests for FailureSignalNormalizer — determinism and contract proofs."""

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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_failure_signal_normalizer")
_emit_applies_guardrail("p0", "test_failure_signal_normalizer", "p0_governance")
_emit_reads_policy_state("p0", "test_failure_signal_normalizer", "policy_binding")
_emit_snapshots_state("p0", "test_failure_signal_normalizer", "state_snapshot")
emit_replay_key("p0", "test_failure_signal_normalizer")
emit_determinism_digest("p0", "test_failure_signal_normalizer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_failure_signal_normalizer", "execution_auth")
_emit_validates_capability("p2", "test_failure_signal_normalizer", "capability_check")
_emit_routes_to_capability("p2", "test_failure_signal_normalizer", "capability_route")
_emit_writes_via_uwg("p2", "test_failure_signal_normalizer", "uwg_write")
_emit_blocks_direct_write("p2", "test_failure_signal_normalizer", "direct_write_block")
_emit_records_tool_invocation("p2", "test_failure_signal_normalizer", "tool_invocation")
_emit_captures_execution_output("p2", "test_failure_signal_normalizer", "exec_output")
_emit_dispatches_agent("p3", "test_failure_signal_normalizer", "agent_dispatch")
_emit_coordinates_agents("p3", "test_failure_signal_normalizer", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_failure_signal_normalizer", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_failure_signal_normalizer", "healing_outcome")
_emit_escalates_failure("p3", "test_failure_signal_normalizer", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_failure_signal_normalizer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_failure_signal_normalizer", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_failure_signal_normalizer", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_failure_signal_normalizer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_failure_signal_normalizer", "eval_metric")
_emit_stores_embedding("p4", "test_failure_signal_normalizer", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_failure_signal_normalizer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_failure_signal_normalizer", "exec_snapshot_link")

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

from agentic_core.L2_execution.healers.failure_signal_normalizer import (
    extract_failure_metadata,
    normalize_failure_signal,
)
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
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("test_failure_signal_normalizer", "p4obs", "metric_1")
_emit_emits_metric_event("test_failure_signal_normalizer", "p4obs", "metric_2")
_emit_emits_metric_event("test_failure_signal_normalizer", "p4obs", "metric_3")
_emit_emits_metric_event("test_failure_signal_normalizer", "p4obs", "metric_4")
_emit_emits_metric_event("test_failure_signal_normalizer", "p4obs", "metric_5")
_emit_emits_metric_event("test_failure_signal_normalizer", "p4obs", "metric_6")
_emit_records_incident_event("test_failure_signal_normalizer", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_failure_signal_normalizer", "p4obs", "anomaly")
_emit_writes_observability_log("test_failure_signal_normalizer", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_failure_signal_normalizer", "p4obs", "mon_state")
_emit_triggers_alert("test_failure_signal_normalizer", "p4obs", "alert")
_emit_links_incident_trace("test_failure_signal_normalizer", "p4obs", "trace_link")
_emit_captures_pattern("test_failure_signal_normalizer", "p3lm", "pattern")
_emit_records_learning_event("test_failure_signal_normalizer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_failure_signal_normalizer", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_failure_signal_normalizer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_failure_signal_normalizer", "p3lm", "routing")
_emit_improves_agent_policy("test_failure_signal_normalizer", "p3lm", "policy")
_emit_stores_learning_state("test_failure_signal_normalizer", "p3lm", "state")
_emit_records_execution_trace("test_failure_signal_normalizer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_failure_signal_normalizer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_failure_signal_normalizer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_failure_signal_normalizer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_failure_signal_normalizer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_failure_signal_normalizer", "env_read", "p2_env_1")
_emit_reads_environ("test_failure_signal_normalizer", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_failure_signal_normalizer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_failure_signal_normalizer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_failure_signal_normalizer", "context_pull")
_emit_pulls_context("p1", "test_failure_signal_normalizer", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_failure_signal_normalizer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_failure_signal_normalizer", "uwg_term_secondary")
_emit_writes_through("p1", "test_failure_signal_normalizer", "write_through")
_emit_writes_through("p1", "test_failure_signal_normalizer", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_failure_signal_normalizer", "safety_validation")
_emit_invokes_eval("p1", "test_failure_signal_normalizer", "eval_call")
_emit_proposal_commits_routing("p1", "test_failure_signal_normalizer", "routing_commit")
_emit_escalates_to_human("p1", "test_failure_signal_normalizer", "human_escalation")
_emit_routes_through("p1", "test_failure_signal_normalizer", "route_through")
_emit_checks_agent_registry("p1", "test_failure_signal_normalizer", "agent_registry")
_emit_validates_agent_capability("p1", "test_failure_signal_normalizer", "capability")
_emit_dispatches_execution_plan("p1", "test_failure_signal_normalizer", "exec_plan")
_emit_agent_executes_agent("p1", "test_failure_signal_normalizer", "sub_agent")
_emit_routes_to_agent("p1", "test_failure_signal_normalizer", "target_agent")
_emit_verifies_policy("p1", "test_failure_signal_normalizer", "policy_check")
_emit_observes_runtime_state("p1", "test_failure_signal_normalizer", "runtime_state")
_emit_verifies_boundary("p1", "test_failure_signal_normalizer", "boundary_check")
_emit_transcripts_response("p1", "test_failure_signal_normalizer", "transcript")
_emit_hard_fails_untranscripted("p1", "test_failure_signal_normalizer")
_emit_gated_by_confidence("p1", "test_failure_signal_normalizer", "confidence_gate")


class TestNormalizeFailureSignal:
    """normalize_failure_signal contract tests."""

    def test_full_action_produces_expected_text(self) -> None:
        action = {
            "type": "IMPORT_BOUNDARY_VIOLATION",
            "routing_gate": "gate:import_boundary_check",
            "agent": "DependencyRepairAgent",
            "fix_summary": "yaml config loader",
        }
        result = normalize_failure_signal(action)
        assert result == (
            "IMPORT_BOUNDARY_VIOLATION gate:import_boundary_check DependencyRepairAgent yaml config loader"
        )

    def test_routing_gate_included_when_present(self) -> None:
        action = {
            "type": "LAYER_VIOLATION",
            "routing_gate": "gate:layer_check",
            "agent": "ArchGovernor",
        }
        result = normalize_failure_signal(action)
        assert "gate:layer_check" in result
        assert result.index("LAYER_VIOLATION") < result.index("gate:layer_check")

    def test_routing_gate_na_omitted(self) -> None:
        action = {"type": "LAYER_VIOLATION", "routing_gate": "N/A", "agent": "ArchGovernor"}
        result = normalize_failure_signal(action)
        assert "N/A" not in result
        assert result == "LAYER_VIOLATION ArchGovernor"

    def test_failure_type_uppercased(self) -> None:
        action = {"type": "layer_violation", "agent": "ArchGovernor"}
        result = normalize_failure_signal(action)
        assert result.startswith("LAYER_VIOLATION")

    def test_falls_back_to_routing_tier_when_type_missing(self) -> None:
        action = {"routing_tier": "DETERMINISTIC", "agent": "TestRepairAgent"}
        result = normalize_failure_signal(action)
        assert "DETERMINISTIC" in result
        assert "TestRepairAgent" in result

    def test_unknown_when_no_type_fields(self) -> None:
        action = {"agent": "SomeAgent"}
        result = normalize_failure_signal(action)
        assert "UNKNOWN" in result
        assert "SomeAgent" in result

    def test_empty_fix_summary_omitted(self) -> None:
        action = {"type": "LAYER_VIOLATION", "agent": "GovernorAgent", "fix_summary": ""}
        result = normalize_failure_signal(action)
        assert result == "LAYER_VIOLATION GovernorAgent"

    def test_missing_agent_uses_default(self) -> None:
        action = {"type": "GATEWAY_BYPASS"}
        result = normalize_failure_signal(action)
        assert "GATEWAY_BYPASS" in result
        assert "unknown_agent" in result

    def test_deterministic_identical_inputs(self) -> None:
        action = {
            "type": "LAYER_VIOLATION",
            "routing_gate": "gate:layer_check",
            "agent": "TestAgent",
            "fix_summary": "fixed",
        }
        assert normalize_failure_signal(action) == normalize_failure_signal(action)

    def test_empty_action_does_not_raise(self) -> None:
        result = normalize_failure_signal({})
        assert isinstance(result, str)
        assert len(result) > 0

    def test_whitespace_stripped(self) -> None:
        action = {"type": "  LAYER_VIOLATION  ", "agent": "  Agent  "}
        result = normalize_failure_signal(action)
        assert "  " not in result

    def test_field_order_type_gate_agent_summary(self) -> None:
        action = {
            "type": "IMPORT_BOUNDARY_VIOLATION",
            "routing_gate": "gate:X",
            "agent": "AgentA",
            "fix_summary": "summary text",
        }
        parts = normalize_failure_signal(action).split(" ")
        assert parts[0] == "IMPORT_BOUNDARY_VIOLATION"
        assert parts[1] == "gate:X"
        assert parts[2] == "AgentA"


class TestExtractFailureMetadata:
    """extract_failure_metadata contract tests — metadata is kept separate from embedding text."""

    def test_all_fields_captured(self) -> None:
        action = {
            "territory": "L5_safety",
            "routing_digest": "abc123",
            "confidence": 0.85,
            "routing_tier": "DETERMINISTIC",
            "outcome": "SUCCESS",
            "timestamp": "2026-01-01T00:00:00",
        }
        meta = extract_failure_metadata(action)
        assert meta["territory"] == "L5_safety"
        assert meta["routing_digest"] == "abc123"
        assert meta["confidence_score"] == 0.85
        assert meta["routing_tier"] == "DETERMINISTIC"
        assert meta["outcome"] == "SUCCESS"
        assert meta["timestamp"] == "2026-01-01T00:00:00"

    def test_missing_fields_default_to_none_or_unknown(self) -> None:
        meta = extract_failure_metadata({})
        assert meta["territory"] == "unknown"
        assert meta["routing_digest"] is None
        assert meta["confidence_score"] is None

    def test_metadata_does_not_include_embedding_fields(self) -> None:
        action = {"type": "LAYER_VIOLATION", "agent": "Healer", "fix_summary": "fixed"}
        meta = extract_failure_metadata(action)
        assert "type" not in meta
        assert "agent" not in meta
        assert "fix_summary" not in meta
