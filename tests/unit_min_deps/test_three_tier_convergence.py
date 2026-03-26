"""Three-Tier Convergence Tests.

Validates:
  Tier 1 — UWG grant/revoke/record lifecycle round-trips.
  Tier 2 — Threshold constants from healing_tier_config match execute_ssot defaults.
  Tier 3 — adapt_heal_result() produces valid HealCheckResult from every input shape,
            including absolute-path sanitisation.
"""

from __future__ import annotations

from pathlib import Path

import pytest

#  # MOVED: from agentic_core.L2_execution.heal_result_adapter import adapt_heal_result
#  # MOVED: from agentic_core.L2_execution.types.heal_contract_types import HealCheckResult, HealStatus
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_three_tier_convergence")
# REMOVED: _emit_applies_guardrail("p0", "test_three_tier_convergence", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_three_tier_convergence", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_three_tier_convergence", "state_snapshot")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_three_tier_convergence", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_three_tier_convergence", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_three_tier_convergence", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_three_tier_convergence", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_three_tier_convergence", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_three_tier_convergence", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_three_tier_convergence", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_three_tier_convergence", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_three_tier_convergence", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_three_tier_convergence", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_three_tier_convergence", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_three_tier_convergence", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_three_tier_convergence", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_three_tier_convergence", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_three_tier_convergence", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_three_tier_convergence", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_three_tier_convergence", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_three_tier_convergence", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_three_tier_convergence", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_three_tier_convergence", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_three_tier_convergence", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_three_tier_convergence", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_three_tier_convergence", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_three_tier_convergence", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_three_tier_convergence", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_three_tier_convergence", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_three_tier_convergence", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_three_tier_convergence", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_three_tier_convergence", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_three_tier_convergence", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_three_tier_convergence", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_three_tier_convergence", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_three_tier_convergence", "write_through")
# REMOVED: _emit_writes_through("p1", "test_three_tier_convergence", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_three_tier_convergence", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_three_tier_convergence", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_three_tier_convergence", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_three_tier_convergence", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_three_tier_convergence", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_three_tier_convergence", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_three_tier_convergence", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_three_tier_convergence", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_three_tier_convergence", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_three_tier_convergence", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_three_tier_convergence", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_three_tier_convergence", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_three_tier_convergence", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_three_tier_convergence", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_three_tier_convergence")
# REMOVED: _emit_gated_by_confidence("p1", "test_three_tier_convergence", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_three_tier_convergence")
# REMOVED: emit_determinism_digest("p0", "test_three_tier_convergence")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_three_tier_convergence", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_three_tier_convergence", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_three_tier_convergence", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_three_tier_convergence", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_three_tier_convergence", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_three_tier_convergence", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_three_tier_convergence", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_three_tier_convergence", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_three_tier_convergence", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_three_tier_convergence", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_three_tier_convergence", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_three_tier_convergence", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_three_tier_convergence", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_three_tier_convergence", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_three_tier_convergence", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_three_tier_convergence", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_three_tier_convergence", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_three_tier_convergence", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_three_tier_convergence", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_three_tier_convergence", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ---------------------------------------------------------------------------
# Tier 1 — UniversalWriteGateway lifecycle
# ---------------------------------------------------------------------------


class TestTier1UWG:
    """UWG permission + ledger lifecycle."""

    def _fresh_uwg(self):
#  # MOVED: from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway

        return UniversalWriteGateway()

    def test_grant_then_revoke_permission(self) -> None:
                from agentic_core.L2_execution.heal_result_adapter import adapt_heal_result
                from agentic_core.L2_execution.types.heal_contract_types import HealCheckResult, HealStatus
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway
                from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway
                from agentic_core.interfaces.write_gateway import get_write_gateway
                from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway
                from agentic_core.L2_execution.healers.healing_tier_config import (
                from agentic_core.L2_execution.healers.healing_tier_config import (
                uwg = self._fresh_uwg()
                # UWG stores exact normalized key; check_write_permission looks up that exact key.
                test_path = "agentic_core/L2_execution/"
                uwg.grant_write_permission(test_path)
                assert uwg.check_write_permission(test_path)
                uwg.revoke_write_permission(test_path)
                assert not uwg.check_write_permission(test_path)

        assert not uwg.check_write_permission(test_path)

    def test_record_mutation_appends_to_ledger(self) -> None:
        uwg = self._fresh_uwg()
        uwg.grant_write_permission("apps_rg/")
        uwg.record_mutation(path="apps_rg/engines/foo.py", operation="heal_repository", permitted=True)
        ledger = uwg.get_mutation_ledger()
        assert len(ledger) == 1
        assert ledger[0].operation == "heal_repository"
        assert ledger[0].permitted is True

    def test_revoke_without_prior_grant_is_safe(self) -> None:
        """Revoking a path that was never granted must not raise."""
        uwg = self._fresh_uwg()
        uwg.revoke_write_permission("nonexistent/territory/")  # must not raise

    def test_replay_mode_skips_permission_changes(self) -> None:
#  # MOVED: from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway

        uwg = UniversalWriteGateway(replay_mode=True)
        uwg.grant_write_permission("apps_rg/")  # no-op in replay mode
        # In replay mode all paths are allowed
        assert uwg.check_write_permission("apps_rg/engines/foo.py")

    def test_get_write_gateway_returns_uwg_instance(self) -> None:
#  # MOVED: from agentic_core.interfaces.write_gateway import get_write_gateway
#  # MOVED: from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway

        assert isinstance(get_write_gateway(), UniversalWriteGateway)


# ---------------------------------------------------------------------------
# Tier 2 — Threshold SSOT consistency
# ---------------------------------------------------------------------------


class TestTier2Thresholds:
    """Canonical thresholds in healing_tier_config must match execute_ssot defaults."""

    def test_threshold_values_are_canonical(self) -> None:
#  # MOVED: from agentic_core.L2_execution.healers.healing_tier_config import (
            HEALING_CONFIDENCE_X,
            HEALING_CONFIDENCE_Y,
        )

        assert HEALING_CONFIDENCE_X == 0.80, "X threshold drifted from 0.80"
        assert HEALING_CONFIDENCE_Y == 0.50, "Y threshold drifted from 0.50"

    def test_thresholds_are_ordered(self) -> None:
#  # MOVED: from agentic_core.L2_execution.healers.healing_tier_config import (
            HEALING_CONFIDENCE_X,
            HEALING_CONFIDENCE_Y,
        )

        assert HEALING_CONFIDENCE_Y < HEALING_CONFIDENCE_X
        assert 0.0 <= HEALING_CONFIDENCE_Y < HEALING_CONFIDENCE_X <= 1.0

    def test_healing_tier_config_validates_on_load(self) -> None:
    """Test healing_tier_config_validates_on_load contract compliance."""
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
REPO_ROOT = Path(__file__).resolve().parents[2]  # c:\Git\Agentic-Workflow


class TestTier3Adapter:
    """adapt_heal_result() produces a valid HealCheckResult for every input shape."""

    # --- status extraction ---

    def test_success_bool_true(self) -> None:
        hcr = adapt_heal_result("AgentA", {"success": True}, repo_root=REPO_ROOT)
        assert hcr.status == HealStatus.HEALED

    def test_success_bool_false(self) -> None:
        hcr = adapt_heal_result("AgentA", {"success": False}, repo_root=REPO_ROOT)
        assert hcr.status == HealStatus.FAILED

    def test_explicit_status_healed(self) -> None:
        hcr = adapt_heal_result("AgentA", {"status": "HEALED"}, repo_root=REPO_ROOT)
        assert hcr.status == HealStatus.HEALED

    def test_explicit_status_partial(self) -> None:
        hcr = adapt_heal_result("AgentA", {"status": "PARTIAL"}, repo_root=REPO_ROOT)
        assert hcr.status == HealStatus.PARTIAL

    def test_explicit_status_skipped(self) -> None:
        hcr = adapt_heal_result("AgentA", {"status": "SKIPPED"}, repo_root=REPO_ROOT)
        assert hcr.status == HealStatus.SKIPPED

    def test_status_success_alias(self) -> None:
        hcr = adapt_heal_result("AgentA", {"status": "SUCCESS"}, repo_root=REPO_ROOT)
        assert hcr.status == HealStatus.HEALED

    def test_error_key_implies_failed(self) -> None:
        hcr = adapt_heal_result("AgentA", {"error": "boom"}, repo_root=REPO_ROOT)
        assert hcr.status == HealStatus.FAILED

    def test_files_healed_zero_implies_skipped(self) -> None:
        hcr = adapt_heal_result("AgentA", {"files_healed": 0}, repo_root=REPO_ROOT)
        assert hcr.status == HealStatus.SKIPPED

    def test_files_healed_positive_implies_healed(self) -> None:
        hcr = adapt_heal_result("AgentA", {"files_healed": 3}, repo_root=REPO_ROOT)
        assert hcr.status == HealStatus.HEALED

    # --- string / None normalisation ---

    def test_string_input_stored_in_changes_made(self) -> None:
        hcr = adapt_heal_result("AgentA", "Fixed 3 files", repo_root=REPO_ROOT)
        assert any("Fixed 3 files" in c for c in hcr.changes_made)

    def test_none_input_stored_in_changes_made(self) -> None:
        hcr = adapt_heal_result("AgentA", None, repo_root=REPO_ROOT)
        assert any("No output returned" in c for c in hcr.changes_made)

    # --- absolute path sanitisation (critical contract requirement) ---

    def test_absolute_windows_path_sanitised(self) -> None:
        """HealCheckResult rejects absolute paths — adapter must convert them."""
        raw = {"success": True, "files_healed": [r"C:\Git\Agentic-Workflow\agentic_core\foo.py"]}
        hcr = adapt_heal_result("AgentA", raw, repo_root=REPO_ROOT)
        for change in hcr.changes_made:
            assert not change.startswith("C:"), f"Absolute path leaked: {change}"
            assert not change.startswith("/"), f"Absolute path leaked: {change}"

    def test_absolute_posix_path_sanitised(self) -> None:
        raw = {"success": True, "changes_made": ["/home/user/repo/agentic_core/foo.py"]}
        hcr = adapt_heal_result("AgentA", raw, repo_root=REPO_ROOT)
        for change in hcr.changes_made:
            assert not change.startswith("/"), f"Absolute path leaked: {change}"

    def test_relative_paths_pass_through(self) -> None:
        raw = {"success": True, "files_healed": ["agentic_core/foo.py", "tests/bar.py"]}
        hcr = adapt_heal_result("AgentA", raw, repo_root=REPO_ROOT)
        assert "agentic_core/foo.py" in hcr.changes_made
        assert "tests/bar.py" in hcr.changes_made

    # --- return type is always HealCheckResult ---

    def test_return_type_is_heal_check_result(self) -> None:
    """Test return_type_is_heal_check_result contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data
    """Test check_id_matches_agent_name contract compliance."""
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
        hcr = adapt_heal_result(
            "AgentA", {"success": False, "error": "complex rewrite required"}, repo_root=REPO_ROOT
        )
        assert hcr.needs_llm_escalation is True

    def test_simple_failure_does_not_trigger_escalation(self) -> None:
        hcr = adapt_heal_result("AgentA", {"success": False, "error": "missing import"}, repo_root=REPO_ROOT)
        assert hcr.needs_llm_escalation is False

    def test_large_change_set_triggers_escalation(self) -> None:
        raw = {"success": True, "changes_made": [f"file{i}.py" for i in range(12)]}
        hcr = adapt_heal_result("AgentA", raw, repo_root=REPO_ROOT)
        assert hcr.needs_llm_escalation is True

    def test_explicit_escalation_flag_respected(self) -> None:
    """Test explicit_escalation_flag_respected contract compliance."""
    # Arrange
    # TODO: Set up specification test case
    spec_input = {}  # Replace with actual specification input
    """Test explicit_no_escalation_flag_respected contract compliance."""
    # Arrange
    # TODO: Set up specification test case
    spec_input = {}  # Replace with actual specification input

    # Act
    # TODO: Test specification compliance
    compliance_result = None  # Replace with actual compliance test

    # Assert - Specification Contract
    assert compliance_result is not None, "Specification compliance should be testable"
    assert isinstance(compliance_result, (bool, dict)), "Compliance result should be structured"
    # TODO: Add specific specification assertions
    # assert compliance_result.get("meets_spec", False), "Should meet specification requirements"
    def test_escalation_hint_absent_when_not_needed(self) -> None:
        hcr = adapt_heal_result("AgentA", {"success": True, "files_healed": 1}, repo_root=REPO_ROOT)
        assert hcr.escalation_hint is None

    # --- to_dict round-trip ---

    def test_to_dict_round_trip(self) -> None:
        raw = {"success": True, "files_healed": ["agentic_core/foo.py"]}
        hcr = adapt_heal_result("AgentA", raw, repo_root=REPO_ROOT)
        d = hcr.to_dict()
        assert d["check_id"] == "AgentA"
        assert d["status"] == "HEALED"
        assert isinstance(d["changes_made"], list)
        assert d["needs_llm_escalation"] is False
