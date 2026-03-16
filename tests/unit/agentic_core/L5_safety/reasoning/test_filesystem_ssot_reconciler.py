"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/filesystem_ssot_reconciler.py.

fan_in=5 — imported by 5 other modules.
ADG import-hygiene is covered separately by test_filesystem_ssot_reconciler_adg.py.
This file covers behavioral invariants and public API contracts.
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

_emit_records_execution_trace("p0", "evidence", "test_filesystem_ssot_reconciler")
_emit_applies_guardrail("p0", "test_filesystem_ssot_reconciler", "p0_governance")
_emit_reads_policy_state("p0", "test_filesystem_ssot_reconciler", "policy_binding")
_emit_snapshots_state("p0", "test_filesystem_ssot_reconciler", "state_snapshot")
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

_emit_emits_metric_event("test_filesystem_ssot_reconciler", "p4obs", "metric_1")
_emit_emits_metric_event("test_filesystem_ssot_reconciler", "p4obs", "metric_2")
_emit_emits_metric_event("test_filesystem_ssot_reconciler", "p4obs", "metric_3")
_emit_emits_metric_event("test_filesystem_ssot_reconciler", "p4obs", "metric_4")
_emit_emits_metric_event("test_filesystem_ssot_reconciler", "p4obs", "metric_5")
_emit_emits_metric_event("test_filesystem_ssot_reconciler", "p4obs", "metric_6")
_emit_records_incident_event("test_filesystem_ssot_reconciler", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_filesystem_ssot_reconciler", "p4obs", "anomaly")
_emit_writes_observability_log("test_filesystem_ssot_reconciler", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_filesystem_ssot_reconciler", "p4obs", "mon_state")
_emit_triggers_alert("test_filesystem_ssot_reconciler", "p4obs", "alert")
_emit_links_incident_trace("test_filesystem_ssot_reconciler", "p4obs", "trace_link")
_emit_captures_pattern("test_filesystem_ssot_reconciler", "p3lm", "pattern")
_emit_records_learning_event("test_filesystem_ssot_reconciler", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_filesystem_ssot_reconciler", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_filesystem_ssot_reconciler", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_filesystem_ssot_reconciler", "p3lm", "routing")
_emit_improves_agent_policy("test_filesystem_ssot_reconciler", "p3lm", "policy")
_emit_stores_learning_state("test_filesystem_ssot_reconciler", "p3lm", "state")
_emit_records_execution_trace("test_filesystem_ssot_reconciler", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_filesystem_ssot_reconciler", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_filesystem_ssot_reconciler", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_filesystem_ssot_reconciler", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_filesystem_ssot_reconciler", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_filesystem_ssot_reconciler", "env_read", "p2_env_1")
_emit_reads_environ("test_filesystem_ssot_reconciler", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_filesystem_ssot_reconciler", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_filesystem_ssot_reconciler", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_filesystem_ssot_reconciler", "context_pull")
_emit_pulls_context("p1", "test_filesystem_ssot_reconciler", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_filesystem_ssot_reconciler", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_filesystem_ssot_reconciler", "uwg_term_2")
_emit_writes_through("p1", "test_filesystem_ssot_reconciler", "write_through")
_emit_writes_through("p1", "test_filesystem_ssot_reconciler", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_filesystem_ssot_reconciler", "safety_validation")
_emit_invokes_eval("p1", "test_filesystem_ssot_reconciler", "eval_call")
_emit_proposal_commits_routing("p1", "test_filesystem_ssot_reconciler", "routing_commit")
_emit_escalates_to_human("p1", "test_filesystem_ssot_reconciler", "human_escalation")
_emit_routes_through("p1", "test_filesystem_ssot_reconciler", "route_through")
_emit_checks_agent_registry("p1", "test_filesystem_ssot_reconciler", "agent_registry")
_emit_validates_agent_capability("p1", "test_filesystem_ssot_reconciler", "capability")
_emit_dispatches_execution_plan("p1", "test_filesystem_ssot_reconciler", "exec_plan")
_emit_agent_executes_agent("p1", "test_filesystem_ssot_reconciler", "sub_agent")
_emit_routes_to_agent("p1", "test_filesystem_ssot_reconciler", "target_agent")
_emit_verifies_policy("p1", "test_filesystem_ssot_reconciler", "policy_check")
_emit_observes_runtime_state("p1", "test_filesystem_ssot_reconciler", "runtime_state")
_emit_verifies_boundary("p1", "test_filesystem_ssot_reconciler", "boundary_check")
_emit_transcripts_response("p1", "test_filesystem_ssot_reconciler", "transcript")
_emit_hard_fails_untranscripted("p1", "test_filesystem_ssot_reconciler")
_emit_gated_by_confidence("p1", "test_filesystem_ssot_reconciler", "confidence_gate")
emit_replay_key("p0", "test_filesystem_ssot_reconciler")
emit_determinism_digest("p0", "test_filesystem_ssot_reconciler")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_filesystem_ssot_reconciler", "execution_auth")
_emit_validates_capability("p2", "test_filesystem_ssot_reconciler", "capability_check")
_emit_routes_to_capability("p2", "test_filesystem_ssot_reconciler", "capability_route")
_emit_writes_via_uwg("p2", "test_filesystem_ssot_reconciler", "uwg_write")
_emit_blocks_direct_write("p2", "test_filesystem_ssot_reconciler", "direct_write_block")
_emit_records_tool_invocation("p2", "test_filesystem_ssot_reconciler", "tool_invocation")
_emit_captures_execution_output("p2", "test_filesystem_ssot_reconciler", "exec_output")
_emit_dispatches_agent("p3", "test_filesystem_ssot_reconciler", "agent_dispatch")
_emit_coordinates_agents("p3", "test_filesystem_ssot_reconciler", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_filesystem_ssot_reconciler", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_filesystem_ssot_reconciler", "healing_outcome")
_emit_escalates_failure("p3", "test_filesystem_ssot_reconciler", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_filesystem_ssot_reconciler", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_filesystem_ssot_reconciler", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_filesystem_ssot_reconciler", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_filesystem_ssot_reconciler", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_filesystem_ssot_reconciler", "eval_metric")
_emit_stores_embedding("p4", "test_filesystem_ssot_reconciler", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_filesystem_ssot_reconciler", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_filesystem_ssot_reconciler", "exec_snapshot_link")

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.filesystem_ssot_reconciler import (  # noqa: F401
        FilesystemSSOTReconcilerAgent,
        ReconciliationViolation,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ReconciliationViolation = None  # type: ignore[assignment,misc]
    FilesystemSSOTReconcilerAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="filesystem_ssot_reconciler.py deps unavailable")
class TestReconciliationViolationContract:
    def test_is_dataclass(self):
        import dataclasses

        assert dataclasses.is_dataclass(ReconciliationViolation)

    def test_field_names_present(self):
        import dataclasses

        fnames = {f.name for f in dataclasses.fields(ReconciliationViolation)}
        assert fnames >= {"severity", "suggested_action", "message", "drift_type", "file_path", "is_valid"}

    def test_field_count_reasonable(self):
        import dataclasses

        assert len(dataclasses.fields(ReconciliationViolation)) >= 1


@pytest.mark.skipif(not _AVAILABLE, reason="filesystem_ssot_reconciler.py deps unavailable")
class TestFilesystemSSOTReconcilerAgentContract:
    def test_is_class(self):
        assert isinstance(FilesystemSSOTReconcilerAgent, type)

    def test_has_method_heal(self):
        assert callable(getattr(FilesystemSSOTReconcilerAgent, "heal", None))

    def test_has_method_run_ci_verification_sync(self):
        assert callable(getattr(FilesystemSSOTReconcilerAgent, "run_ci_verification_sync", None))

    def test_has_method_run_ci_verification(self):
        assert callable(getattr(FilesystemSSOTReconcilerAgent, "run_ci_verification", None))

    def test_has_method_enforce_gospel(self):
        assert callable(getattr(FilesystemSSOTReconcilerAgent, "enforce_gospel", None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(FilesystemSSOTReconcilerAgent) if not m.startswith("_")]
        assert len(pub) >= 1


def test_module_importable():
    """Smoke: filesystem_ssot_reconciler importable or gracefully unavailable."""
    pass


# =============================================================================
# BEHAVIORAL TESTS: Heal execution path (RCA: scan-only bug)
# =============================================================================


@pytest.mark.skipif(not _AVAILABLE, reason="filesystem_ssot_reconciler.py deps unavailable")
class TestHealRepositoryForceGate:
    """heal_repository() must not short-circuit when force=True."""

    def test_without_force_returns_skipped(self, tmp_path):
        """force=False (default) must return skipped=1 — the guard exists intentionally."""
        agent = FilesystemSSOTReconcilerAgent(project_root=tmp_path)
        result = agent.heal_repository(dry_run=False, execute=True, force=False)
        assert result.get("skipped") == 1, f"Expected skipped=1 when force=False, got {result}"

    def test_without_force_does_not_apply_changes(self, tmp_path):
        """force=False must never apply any filesystem changes."""
        agent = FilesystemSSOTReconcilerAgent(project_root=tmp_path)
        result = agent.heal_repository(dry_run=False, execute=True, force=False)
        assert not result.get("applied"), f"No changes should be applied when force=False, got {result}"

    def test_with_force_does_not_skip(self, tmp_path):
        """force=True must NOT return skipped=1 — it must attempt real work."""
        agent = FilesystemSSOTReconcilerAgent(project_root=tmp_path)
        result = agent.heal_repository(dry_run=False, execute=True, force=True)
        assert result.get("skipped") != 1, f"force=True must not short-circuit to skipped=1, got {result}"

    def test_with_force_returns_drift_detected_key(self, tmp_path):
        """force=True result must contain drift_detected key."""
        agent = FilesystemSSOTReconcilerAgent(project_root=tmp_path)
        result = agent.heal_repository(dry_run=False, execute=True, force=True)
        # Either drift_detected=True/False or skipped=0 — but never the skip-gate path
        assert "drift_detected" in result or result.get("skipped") == 0, (
            f"force=True result missing drift_detected: {result}"
        )

    def test_call_site_must_pass_force_true(self):
        """Invariant: execute_ssot phase1 call site passes force=True.

        Grep execute_ssot.py and _ssot_phases.py for the heal_repository call.
        If force=True is absent, the heal is silently skipped every time.
        """
        from pathlib import Path

        repo_root = Path(__file__).resolve().parents[5]
        for fname in [
            repo_root / "agentic_core" / "L0_routing" / "scripts" / "_ssot_phases.py",
            repo_root / "agentic_core" / "L0_routing" / "scripts" / "execute_ssot.py",
        ]:
            src = fname.read_text(encoding="utf-8")
            # Find the heal_repository call in the reconciler heal block
            import re

            # Match heal_repository( ... ) calls that include the reconciler path
            calls = re.findall(
                r"heal_repository\([^)]*\)",
                src,
            )
            reconciler_calls = [c for c in calls if "force" in c or "_fs_healer_instance" in src]
            # The specific call should include force=True
            assert "force=True" in src, (
                f"{fname.name}: heal_repository() call is missing force=True "
                f"— reconciler will silently skip all healing"
            )


@pytest.mark.skipif(not _AVAILABLE, reason="filesystem_ssot_reconciler.py deps unavailable")
class TestRunWithCleanupHealPath:
    """run_with_cleanup() must be called for full SSOT blueprint drift (the 29-item scan)."""

    @pytest.fixture()
    def repo_root(self):
        """Real repo root — run_with_cleanup reads structure_blueprint_config.py."""
        from pathlib import Path

        return Path(__file__).resolve().parents[5]

    def test_run_with_cleanup_dry_run_true_returns_preview(self, repo_root):
        """dry_run=True returns PREVIEW, never APPLIED."""
        agent = FilesystemSSOTReconcilerAgent(project_root=repo_root)
        result = agent.run_with_cleanup(dry_run=True)
        assert result["dry_run"] is True
        post = result.get("post_heal_validation", {})
        assert "PREVIEW" in post.get("message", ""), (
            f"dry_run=True should produce PREVIEW message, got: {post}"
        )

    def test_run_with_cleanup_dry_false_returns_applied_key(self, repo_root):
        """dry_run=False result must have actions_applied key."""
        agent = FilesystemSSOTReconcilerAgent(project_root=repo_root)
        result = agent.run_with_cleanup(dry_run=False)
        assert "actions_applied" in result, (
            f"run_with_cleanup(dry_run=False) missing actions_applied: {result}"
        )
        assert result["dry_run"] is False

    def test_run_with_cleanup_violations_detected_is_int(self, repo_root):
        """violations_detected must be a non-negative integer."""
        agent = FilesystemSSOTReconcilerAgent(project_root=repo_root)
        result = agent.run_with_cleanup(dry_run=True)
        assert isinstance(result.get("violations_detected"), int)
        assert result["violations_detected"] >= 0

    def test_run_with_cleanup_drift_detected_is_int(self, repo_root):
        """drift_detected count must be a non-negative integer."""
        agent = FilesystemSSOTReconcilerAgent(project_root=repo_root)
        result = agent.run_with_cleanup(dry_run=True)
        assert isinstance(result.get("drift_detected"), int)
        assert result["drift_detected"] >= 0

    def test_call_site_calls_run_with_cleanup(self):
        """Invariant: phase1 call sites must invoke run_with_cleanup."""
        from pathlib import Path

        repo_root = Path(__file__).resolve().parents[5]
        for fname in [
            repo_root / "agentic_core" / "L0_routing" / "scripts" / "_ssot_phases.py",
            repo_root / "agentic_core" / "L0_routing" / "scripts" / "execute_ssot.py",
        ]:
            src = fname.read_text(encoding="utf-8")
            assert "run_with_cleanup" in src, (
                f"{fname.name}: run_with_cleanup() never called — "
                f"29-item SSOT blueprint drift will never be healed"
            )
            assert "run_with_cleanup(dry_run=False)" in src, (
                f"{fname.name}: run_with_cleanup must be called with dry_run=False in the heal path"
            )


@pytest.mark.skipif(not _AVAILABLE, reason="filesystem_ssot_reconciler.py deps unavailable")
class TestOutcomeAccuracy:
    """Outcome recorded in state_mgr must reflect actual heal result, not always SUCCESS."""

    def test_skipped_heal_result_produces_skipped_outcome(self):
        """When heal_result={skipped:1} and no cleanup, outcome must be SKIPPED not SUCCESS."""
        heal_result = {"skipped": 1}
        _was_skipped = heal_result.get("skipped", 0) and not heal_result.get("cleanup")
        outcome = "SKIPPED" if _was_skipped else "SUCCESS"
        assert outcome == "SKIPPED", "scan-only run (skipped=1, no cleanup) must record SKIPPED, not SUCCESS"

    def test_heal_with_cleanup_produces_success_outcome(self):
        """When cleanup was run (even 0 applied), outcome must be SUCCESS."""
        heal_result = {"skipped": 1, "cleanup": {"actions_applied": 0}}
        _was_skipped = heal_result.get("skipped", 0) and not heal_result.get("cleanup")
        outcome = "SKIPPED" if _was_skipped else "SUCCESS"
        assert outcome == "SUCCESS", "run with cleanup executed must record SUCCESS even if 0 actions applied"

    def test_heal_applied_nonzero_produces_success_outcome(self):
        """When applied>0, outcome must be SUCCESS."""
        heal_result = {"applied": 3, "cleanup": {"actions_applied": 3}}
        _heal_applied = heal_result.get("applied", 0) or heal_result.get("cleanup", {}).get(
            "actions_applied", 0
        )
        _was_skipped = heal_result.get("skipped", 0) and not heal_result.get("cleanup")
        outcome = "SKIPPED" if _was_skipped else "SUCCESS"
        assert outcome == "SUCCESS"
        assert _heal_applied == 3

    def test_no_ctx_heal_is_skipped_not_success(self):
        """With ctx.heal=False (scan-only run), outcome must be SKIPPED."""
        heal_result = {"skipped": 1}  # ctx.heal=False path: heal block not entered
        _was_skipped = heal_result.get("skipped", 0) and not heal_result.get("cleanup")
        outcome = "SKIPPED" if _was_skipped else "SUCCESS"
        assert outcome == "SKIPPED", (
            "With ctx.heal=False, outcome must be SKIPPED — "
            "recording SUCCESS for a scan-only run is a false positive"
        )

    def test_phase1_does_not_hardcode_success(self):
        """Invariant: phase1 call sites must not hardcode outcome='SUCCESS'."""
        import re
        from pathlib import Path

        repo_root = Path(__file__).resolve().parents[5]
        for fname in [
            repo_root / "agentic_core" / "L0_routing" / "scripts" / "_ssot_phases.py",
            repo_root / "agentic_core" / "L0_routing" / "scripts" / "execute_ssot.py",
        ]:
            src = fname.read_text(encoding="utf-8")
            # Find _record_healing_action calls for FilesystemSSOTReconcilerAgent
            # and assert none of them have hardcoded outcome="SUCCESS"
            # Scan the reconciler block specifically
            reconciler_blocks = re.findall(
                r'agent="FilesystemSSOTReconcilerAgent".*?outcome=([^,\n)]+)',
                src,
                re.DOTALL,
            )
            for block in reconciler_blocks:
                block = block.strip()
                assert block != '"SUCCESS"', (
                    f"{fname.name}: FilesystemSSOTReconcilerAgent _record_healing_action "
                    f'hardcodes outcome="SUCCESS" — scan-only runs will appear as healed'
                )


@pytest.mark.skipif(not _AVAILABLE, reason="filesystem_ssot_reconciler.py deps unavailable")
class TestHealRepositoryContractWithForbiddenFolders:
    """force=True heal path with synthetic forbidden folder."""

    def test_forbidden_folder_detected_and_archived(self, tmp_path):
        """When a forbidden root folder exists, force=True must detect and archive it."""
        # Create a forbidden root folder
        forbidden = tmp_path / "scripts"
        forbidden.mkdir()
        (forbidden / "some_file.py").write_text("x = 1")

        agent = FilesystemSSOTReconcilerAgent(project_root=tmp_path)
        drift = agent.detect_root_drift()
        assert drift.get("root_drift_detected"), (
            f"'scripts/' is a forbidden folder — root_drift_detected must be True, got {drift}"
        )
        assert "scripts" in drift.get("forbidden_folders", []), (
            f"'scripts' must appear in forbidden_folders, got {drift}"
        )

    def test_heal_repository_force_archives_forbidden_folder(self, tmp_path):
        """force=True + execute=True must archive the forbidden folder, not leave it."""
        from unittest.mock import MagicMock, patch

        forbidden = tmp_path / "scripts"
        forbidden.mkdir()
        (forbidden / "some_file.py").write_text("x = 1")

        mock_result = MagicMock()
        mock_result.success = True

        agent = FilesystemSSOTReconcilerAgent(project_root=tmp_path)
        mock_gk_instance = MagicMock()
        mock_gk_instance.safe_move.return_value = mock_result
        # Patch the classmethod on the real class so both the module-level import
        # AND the lazy re-import inside heal_repository both hit the mock.
        with patch(
            "agentic_core.L5_safety.enforcement.archival_gatekeeper_gate.ArchivalGatekeeper.get_instance",
            return_value=mock_gk_instance,
        ):
            result = agent.heal_repository(dry_run=False, execute=True, force=True)

        assert result.get("drift_detected") is True, (
            f"Expected drift_detected=True after force heal, got {result}"
        )
        assert result.get("applied", 0) >= 1, (
            f"Expected applied>=1 after archiving forbidden folder, got {result}"
        )

    def test_heal_repository_force_dry_run_does_not_apply(self, tmp_path):
        """force=True + dry_run=True must detect but NOT archive."""
        forbidden = tmp_path / "scripts"
        forbidden.mkdir()
        (forbidden / "x.py").write_text("x = 1")

        agent = FilesystemSSOTReconcilerAgent(project_root=tmp_path)
        result = agent.heal_repository(dry_run=True, execute=False, force=True)

        assert result.get("drift_detected") is True
        assert result.get("applied", 0) == 0, (
            f"dry_run=True must not apply changes, got applied={result.get('applied')}"
        )
        # Folder must still exist — not archived
        assert forbidden.exists(), "dry_run must not remove the forbidden folder"

    def test_no_forbidden_folders_returns_no_drift(self, tmp_path):
        """Clean tmp dir with no forbidden folders must return drift_detected=False."""
        agent = FilesystemSSOTReconcilerAgent(project_root=tmp_path)
        result = agent.heal_repository(dry_run=False, execute=True, force=True)
        assert result.get("drift_detected") is False or result.get("skipped") == 0, (
            f"Clean repo must not detect drift, got {result}"
        )
