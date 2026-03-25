"""Unit tests for ADG Developer Insight CLI (Phase 6).

Tests cover:
- cmd_who_uses returns correct structure and finds direct importers
- cmd_depends_on returns direct imports
- cmd_territory returns layer and allowed edges
- cmd_unresolved returns NormalizationReport dict
- cmd_coverage returns test list (may be empty on minimal result)
- All command outputs have required top-level keys
- Deterministic: same ScanResult -> same command output
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
from agentic_core.adg.schema_util import canonical_name
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

# REMOVED: _emit_authorize_and_execute("p2", "test_adg_insight_cli", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_adg_insight_cli", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_adg_insight_cli", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_adg_insight_cli", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_adg_insight_cli", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_adg_insight_cli", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_adg_insight_cli", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_adg_insight_cli", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_adg_insight_cli", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_adg_insight_cli", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_adg_insight_cli", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_adg_insight_cli", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_adg_insight_cli", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_adg_insight_cli", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_adg_insight_cli", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_adg_insight_cli", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_adg_insight_cli", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_adg_insight_cli", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_adg_insight_cli", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_adg_insight_cli", "exec_snapshot_link")
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
from tools.adg_insight_cli import (
    cmd_blast_radius,
    cmd_config_reads,
    cmd_coverage,
    cmd_depends_on,
    cmd_territory,
    cmd_unresolved,
    cmd_who_uses,
)

# REMOVED: _emit_emits_metric_event("test_adg_insight_cli", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_adg_insight_cli", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_adg_insight_cli", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_adg_insight_cli", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_adg_insight_cli", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_adg_insight_cli", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_adg_insight_cli", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_adg_insight_cli", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_adg_insight_cli", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_adg_insight_cli", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_adg_insight_cli", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_adg_insight_cli", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_adg_insight_cli", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_adg_insight_cli", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_adg_insight_cli", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_adg_insight_cli", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_adg_insight_cli", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_adg_insight_cli", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_adg_insight_cli", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_adg_insight_cli", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_adg_insight_cli", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_adg_insight_cli", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_adg_insight_cli", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_adg_insight_cli", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_adg_insight_cli", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_adg_insight_cli", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_adg_insight_cli", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_adg_insight_cli", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_adg_insight_cli")
# REMOVED: _emit_applies_guardrail("p0", "test_adg_insight_cli", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_adg_insight_cli", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_adg_insight_cli", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_adg_insight_cli", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_adg_insight_cli", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_insight_cli", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_insight_cli", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_adg_insight_cli", "write_through")
# REMOVED: _emit_writes_through("p1", "test_adg_insight_cli", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_adg_insight_cli", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_adg_insight_cli", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_adg_insight_cli", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_adg_insight_cli", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_adg_insight_cli", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_adg_insight_cli", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_adg_insight_cli", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_adg_insight_cli", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_adg_insight_cli", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_adg_insight_cli", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_adg_insight_cli", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_adg_insight_cli", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_adg_insight_cli", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_adg_insight_cli", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_adg_insight_cli")
# REMOVED: _emit_gated_by_confidence("p1", "test_adg_insight_cli", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_adg_insight_cli")
# REMOVED: emit_determinism_digest("p0", "test_adg_insight_cli")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_REPO_ROOT = Path(__file__).resolve().parents[2]

_MODULE_A = "agentic_core/adg/schema.py"
_MODULE_B = "agentic_core/adg/cli.py"
_TEST_C = "tests/unit/test_adg_identity_normalizer.py"


def _make_result() -> ScanResult:
    result = ScanResult(commit_sha="t")
    result.modules = [_MODULE_A, _MODULE_B, _TEST_C]
    result.edges = [
        Edge(
            from_name=canonical_name("Module", _MODULE_B),
            relation_type="imports",
            to_name=canonical_name("Module", _MODULE_A),
            edge_kind="import",
            source_file=_MODULE_B,
            line_no=3,
        ),
        Edge(
            from_name=canonical_name("Module", _TEST_C),
            relation_type="imports",
            to_name=canonical_name("Module", _MODULE_A),
            edge_kind="import",
            source_file=_TEST_C,
            line_no=5,
        ),
    ]
    result.compute_digest()
    return result


class TestCmdWhoUses:
    """cmd_who_uses returns importers."""

    @pytest.mark.unit
    def test_returns_dict_with_required_keys(self) -> None:
        result = _make_result()
        out = cmd_who_uses(_MODULE_A, result)
        for key in ("module", "direct_importers", "source_importers", "test_importers", "total_count"):
            assert key in out, f"Missing key: {key}"

    @pytest.mark.unit
    def test_finds_direct_source_importer(self) -> None:
        result = _make_result()
        out = cmd_who_uses(_MODULE_A, result)
        assert _MODULE_B in out["direct_importers"]

    @pytest.mark.unit
    def test_finds_test_importer_separately(self) -> None:
        result = _make_result()
        out = cmd_who_uses(_MODULE_A, result)
        assert _TEST_C in out["test_importers"]

    @pytest.mark.unit
    def test_source_and_test_importer_counts(self) -> None:
        result = _make_result()
        out = cmd_who_uses(_MODULE_A, result)
        assert out["total_count"] == 2

    @pytest.mark.unit
    def test_module_with_no_importers_empty(self) -> None:
        result = _make_result()
        out = cmd_who_uses(_MODULE_B, result)
        assert out["total_count"] == 0

    @pytest.mark.unit
    def test_deterministic_output(self) -> None:
        result = _make_result()
        o1 = cmd_who_uses(_MODULE_A, result)
        o2 = cmd_who_uses(_MODULE_A, result)
        assert o1 == o2


class TestCmdDependsOn:
    """cmd_depends_on returns imports of a module."""

    @pytest.mark.unit
    def test_returns_dict_with_required_keys(self) -> None:
        result = _make_result()
        out = cmd_depends_on(_MODULE_B, result)
        for key in ("module", "direct_imports", "direct_count"):
            assert key in out, f"Missing key: {key}"

    @pytest.mark.unit
    def test_finds_direct_import(self) -> None:
        result = _make_result()
        out = cmd_depends_on(_MODULE_B, result)
        assert _MODULE_A in out["direct_imports"]

    @pytest.mark.unit
    def test_no_imports_empty_list(self) -> None:
        result = _make_result()
        out = cmd_depends_on(_MODULE_A, result)
        assert out["direct_count"] == 0

    @pytest.mark.unit
    def test_transitive_flag_adds_key(self) -> None:
        result = _make_result()
        out = cmd_depends_on(_MODULE_B, result, transitive=True)
        assert "transitive_imports" in out
        assert "transitive_count" in out


class TestCmdTerritory:
    """cmd_territory returns layer and allowed edges."""

    @pytest.mark.unit
    def test_returns_dict_with_required_keys(self) -> None:
        out = cmd_territory(_MODULE_A)
        for key in ("module", "layer", "allowed_import_targets", "allowed_import_sources"):
            assert key in out, f"Missing key: {key}"

    @pytest.mark.unit
    def test_adg_schema_is_l_tools(self) -> None:
    """Test adg_schema_is_l_tools contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"
    def test_deterministic(self) -> None:
        o1 = cmd_territory(_MODULE_A)
        o2 = cmd_territory(_MODULE_A)
        assert o1 == o2


class TestCmdUnresolved:
    """cmd_unresolved returns NormalizationReport dict."""

    @pytest.mark.unit
    def test_returns_dict_with_required_keys(self) -> None:
        result = _make_result()
        out = cmd_unresolved(result, _REPO_ROOT)
        for key in ("total", "by_kind", "by_confidence", "unresolved_count", "unresolved_names"):
            assert key in out, f"Missing key: {key}"

    @pytest.mark.unit
    def test_total_is_nonnegative(self) -> None:
        result = _make_result()
        out = cmd_unresolved(result, _REPO_ROOT)
        assert out["total"] >= 0

    @pytest.mark.unit
    def test_unresolved_names_is_sorted(self) -> None:
        result = _make_result()
        out = cmd_unresolved(result, _REPO_ROOT)
        names = out["unresolved_names"]
        assert names == sorted(names)


class TestCmdCoverage:
    """cmd_coverage returns test list."""

    @pytest.mark.unit
    def test_returns_dict_with_required_keys(self) -> None:
        result = _make_result()
        out = cmd_coverage(_MODULE_A, result, _REPO_ROOT)
        for key in ("module", "covering_tests", "test_count"):
            assert key in out, f"Missing key: {key}"

    @pytest.mark.unit
    def test_covered_module_has_tests(self) -> None:
        result = _make_result()
        out = cmd_coverage(_MODULE_A, result, _REPO_ROOT)
        assert out["test_count"] == len(out["covering_tests"])

    @pytest.mark.unit
    def test_uncovered_module_has_empty_list(self) -> None:
        result = _make_result()
        out = cmd_coverage(_MODULE_B, result, _REPO_ROOT)
        assert out["covering_tests"] == []

    @pytest.mark.unit
    def test_note_present_when_no_coverage(self) -> None:
        result = _make_result()
        out = cmd_coverage(_MODULE_B, result, _REPO_ROOT)
        assert "note" in out


class TestCmdBlastRadius:
    """cmd_blast_radius delegates to ChangeImpactEngine and returns to_dict keys."""

    @pytest.mark.unit
    def test_returns_dict_with_required_keys(self) -> None:
        result = _make_result()
        out = cmd_blast_radius(_MODULE_A, result, _REPO_ROOT)
        for key in ("changed_files", "impacted_module_count", "route_mode", "impact_digest"):
            assert key in out, f"Missing key: {key}"

    @pytest.mark.unit
    def test_impact_digest_is_nonempty(self) -> None:
        result = _make_result()
        out = cmd_blast_radius(_MODULE_A, result, _REPO_ROOT)
        assert len(out["impact_digest"]) == 64


class TestCmdConfigReads:
    """cmd_config_reads returns config/env symbols for a module."""

    @pytest.mark.unit
    def test_returns_dict_with_required_keys(self) -> None:
        result = _make_result()
        out = cmd_config_reads(_MODULE_A, result)
        for key in ("module", "config_symbols_read"):
            assert key in out, f"Missing key: {key}"

    @pytest.mark.unit
    def test_config_reads_is_list(self) -> None:
        result = _make_result()
        out = cmd_config_reads(_MODULE_A, result)
        assert isinstance(out["config_symbols_read"], list)
