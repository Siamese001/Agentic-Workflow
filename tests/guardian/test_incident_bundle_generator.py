"""V15 P10.4 — Incident Bundle Generator Tests.

Validates deterministic bundle creation, idempotency, safety checks,
force mode, and sentinel-based user content preservation.
"""

from __future__ import annotations

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

# REMOVED: _emit_authorize_and_execute("p2", "test_incident_bundle_generator", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_incident_bundle_generator", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_incident_bundle_generator", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_incident_bundle_generator", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_incident_bundle_generator", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_incident_bundle_generator", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_incident_bundle_generator", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_incident_bundle_generator", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_incident_bundle_generator", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_incident_bundle_generator", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_incident_bundle_generator", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_incident_bundle_generator", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_incident_bundle_generator", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_incident_bundle_generator", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_incident_bundle_generator", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_incident_bundle_generator", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_incident_bundle_generator", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_incident_bundle_generator", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_incident_bundle_generator", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_incident_bundle_generator", "exec_snapshot_link")
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
from ops_scripts.incident.create_v15_incident_bundle import (
    BUNDLE_FILES,
    SENTINEL,
    create_bundle,
)

# REMOVED: _emit_emits_metric_event("test_incident_bundle_generator", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_incident_bundle_generator", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_incident_bundle_generator", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_incident_bundle_generator", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_incident_bundle_generator", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_incident_bundle_generator", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_incident_bundle_generator", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_incident_bundle_generator", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_incident_bundle_generator", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_incident_bundle_generator", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_incident_bundle_generator", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_incident_bundle_generator", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_incident_bundle_generator", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_incident_bundle_generator", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_incident_bundle_generator", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_incident_bundle_generator", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_incident_bundle_generator", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_incident_bundle_generator", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_incident_bundle_generator", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_incident_bundle_generator", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_incident_bundle_generator", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_incident_bundle_generator", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_incident_bundle_generator", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_incident_bundle_generator", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_incident_bundle_generator", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_incident_bundle_generator", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_incident_bundle_generator", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_incident_bundle_generator", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_incident_bundle_generator")
# REMOVED: _emit_applies_guardrail("p0", "test_incident_bundle_generator", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_incident_bundle_generator", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_incident_bundle_generator", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_incident_bundle_generator", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_incident_bundle_generator", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_incident_bundle_generator", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_incident_bundle_generator", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_incident_bundle_generator", "write_through")
# REMOVED: _emit_writes_through("p1", "test_incident_bundle_generator", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_incident_bundle_generator", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_incident_bundle_generator", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_incident_bundle_generator", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_incident_bundle_generator", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_incident_bundle_generator", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_incident_bundle_generator", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_incident_bundle_generator", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_incident_bundle_generator", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_incident_bundle_generator", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_incident_bundle_generator", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_incident_bundle_generator", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_incident_bundle_generator", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_incident_bundle_generator", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_incident_bundle_generator", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_incident_bundle_generator")
# REMOVED: _emit_gated_by_confidence("p1", "test_incident_bundle_generator", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_incident_bundle_generator")
# REMOVED: emit_determinism_digest("p0", "test_incident_bundle_generator")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

INCIDENT_ID = "INC-TEST-001"


# ===========================================================================
# A) First Run — Creates Exact Tree
# ===========================================================================


class TestFirstRun:
    """First run on empty dir creates the full bundle."""

    def test_exit_zero(self, tmp_path):
        out = tmp_path / "bundle"
        code, msgs = create_bundle(out, INCIDENT_ID)
        assert code == 0

    def test_readme_created(self, tmp_path):
        out = tmp_path / "bundle"
        create_bundle(out, INCIDENT_ID)
        readme = out / "README.md"
        assert readme.is_file()
        text = readme.read_text(encoding="utf-8")
        assert INCIDENT_ID in text
        assert SENTINEL in text

    def test_all_dirs_created(self, tmp_path):
        out = tmp_path / "bundle"
        create_bundle(out, INCIDENT_ID)
        for subdir in ["inputs", "artifacts", "analysis"]:
            assert (out / subdir).is_dir()

    def test_all_files_created(self, tmp_path):
        out = tmp_path / "bundle"
        create_bundle(out, INCIDENT_ID)
        for rel_path in BUNDLE_FILES:
            assert (out / rel_path).is_file(), f"Missing: {rel_path}"

    def test_all_files_have_sentinel(self, tmp_path):
        out = tmp_path / "bundle"
        create_bundle(out, INCIDENT_ID)
        for rel_path in BUNDLE_FILES:
            text = (out / rel_path).read_text(encoding="utf-8")
            assert SENTINEL in text, f"Missing sentinel in {rel_path}"

    def test_readme_contains_checklist(self, tmp_path):
        out = tmp_path / "bundle"
        create_bundle(out, INCIDENT_ID)
        text = (out / "README.md").read_text(encoding="utf-8")
        assert "test_v15_p1_compliance" in text
        assert "test_v15_p6_refinement" in text

    def test_incident_id_in_readme(self, tmp_path):
        out = tmp_path / "bundle"
        create_bundle(out, INCIDENT_ID)
        text = (out / "README.md").read_text(encoding="utf-8")
        assert f"`{INCIDENT_ID}`" in text

    def test_analysis_files_present(self, tmp_path):
        out = tmp_path / "bundle"
        create_bundle(out, INCIDENT_ID)
        for name in ["triage.md", "root_cause.md", "remediation.md"]:
            assert (out / "analysis" / name).is_file()


# ===========================================================================
# B) Idempotency — Second Run No Changes
# ===========================================================================


class TestIdempotency:
    """Second run on existing bundle makes no changes."""

    def test_second_run_exit_zero(self, tmp_path):
    """Test second_run_exit_zero runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute second_run_exit_zero
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
            before[rel_path] = (out / rel_path).read_bytes()
        before["README.md"] = (out / "README.md").read_bytes()

        # Second run
        create_bundle(out, INCIDENT_ID)

        # Compare
        for rel_path, data in before.items():
            assert (out / rel_path).read_bytes() == data, f"Changed: {rel_path}"


# ===========================================================================
# C) Non-Empty Dir Without --force Exits 2
# ===========================================================================


class TestNonEmptyDirSafety:
    """Non-empty dir without --force must exit 2."""

    def test_non_bundle_dir_exits_2(self, tmp_path):
        out = tmp_path / "existing"
        out.mkdir()
        (out / "user_file.txt").write_text("user content", encoding="utf-8")

        code, msgs = create_bundle(out, INCIDENT_ID)
        assert code == 2
        assert any("--force" in m for m in msgs)

    def test_non_bundle_dir_files_untouched(self, tmp_path):
        out = tmp_path / "existing"
        out.mkdir()
        user_file = out / "user_file.txt"
        user_file.write_text("user content", encoding="utf-8")

        create_bundle(out, INCIDENT_ID)
        assert user_file.read_text(encoding="utf-8") == "user content"


# ===========================================================================
# D) --force Mode
# ===========================================================================


class TestForceMode:
    """--force overwrites placeholders in non-bundle dirs."""

    def test_force_on_non_bundle_dir(self, tmp_path):
        out = tmp_path / "existing"
        out.mkdir()
        (out / "user_file.txt").write_text("user content", encoding="utf-8")

        code, msgs = create_bundle(out, INCIDENT_ID, force=True)
        assert code == 0
        assert (out / "README.md").is_file()

    def test_force_preserves_existing_user_file(self, tmp_path):
        out = tmp_path / "existing"
        out.mkdir()
        user_file = out / "user_file.txt"
        user_file.write_text("user content", encoding="utf-8")

        create_bundle(out, INCIDENT_ID, force=True)
        assert user_file.read_text(encoding="utf-8") == "user content"


# ===========================================================================
# E) Sentinel-Based Content Preservation
# ===========================================================================


class TestSentinelPreservation:
    """User-edited files (sentinel removed) must not be overwritten."""

    def test_user_edited_triage_preserved(self, tmp_path):
        out = tmp_path / "bundle"
        create_bundle(out, INCIDENT_ID)

        # Simulate user editing triage.md (removing sentinel)
        triage = out / "analysis" / "triage.md"
        triage.write_text("# My custom triage\nReal analysis here.", encoding="utf-8")

        # Re-run (idempotent path won't even enter file-writing)
        # But test with force=True to prove sentinel protection
        create_bundle(out, INCIDENT_ID, force=True)

        # force=True overwrites files WITH sentinel but _write_if_placeholder
        # checks: sentinel in existing => overwrite; else keep
        text = triage.read_text(encoding="utf-8")
        assert "My custom triage" in text
        assert SENTINEL not in text

    def test_placeholder_file_overwritten_by_force(self, tmp_path):
        out = tmp_path / "bundle"
        create_bundle(out, INCIDENT_ID)

        # File still has sentinel — force should overwrite
        triage = out / "analysis" / "triage.md"
        assert SENTINEL in triage.read_text(encoding="utf-8")

        create_bundle(out, INCIDENT_ID, force=True)
        assert SENTINEL in triage.read_text(encoding="utf-8")


# ===========================================================================
# F) Determinism
# ===========================================================================


class TestDeterminism:
    """Same inputs produce identical bundle bytes."""

    def test_two_bundles_identical(self, tmp_path):
        out1 = tmp_path / "b1"
        out2 = tmp_path / "b2"
        create_bundle(out1, INCIDENT_ID)
        create_bundle(out2, INCIDENT_ID)

        all_files = ["README.md"] + sorted(BUNDLE_FILES.keys())
        for rel_path in all_files:
            b1 = (out1 / rel_path).read_bytes()
            b2 = (out2 / rel_path).read_bytes()
            assert b1 == b2, f"Non-deterministic: {rel_path}"

    def test_different_incident_id_different_readme(self, tmp_path):
        out1 = tmp_path / "b1"
        out2 = tmp_path / "b2"
        create_bundle(out1, "INC-A")
        create_bundle(out2, "INC-B")

        r1 = (out1 / "README.md").read_text(encoding="utf-8")
        r2 = (out2 / "README.md").read_text(encoding="utf-8")
        assert r1 != r2
        assert "INC-A" in r1
        assert "INC-B" in r2
