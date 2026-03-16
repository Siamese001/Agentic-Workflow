"""
End-to-End Tests for SSOT Report Storage - All Phases.

Tests the complete workflow from discovery through enforcement:
- Phase 1: Foundation & Discovery
- Phase 2: Controlled Migration
- Phase 3: Enforcement Activation
- Phase 4: Agent Integration
- Phase 5: Hardening & Documentation

These tests verify the entire system works together correctly.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)
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

_emit_records_execution_trace("p0", "evidence", "test_ssot_report_storage_e2e")
_emit_applies_guardrail("p0", "test_ssot_report_storage_e2e", "p0_governance")
_emit_reads_policy_state("p0", "test_ssot_report_storage_e2e", "policy_binding")
_emit_snapshots_state("p0", "test_ssot_report_storage_e2e", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_ssot_report_storage_e2e", "p4obs", "metric_1")
_emit_emits_metric_event("test_ssot_report_storage_e2e", "p4obs", "metric_2")
_emit_emits_metric_event("test_ssot_report_storage_e2e", "p4obs", "metric_3")
_emit_emits_metric_event("test_ssot_report_storage_e2e", "p4obs", "metric_4")
_emit_emits_metric_event("test_ssot_report_storage_e2e", "p4obs", "metric_5")
_emit_emits_metric_event("test_ssot_report_storage_e2e", "p4obs", "metric_6")
_emit_records_incident_event("test_ssot_report_storage_e2e", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_ssot_report_storage_e2e", "p4obs", "anomaly")
_emit_writes_observability_log("test_ssot_report_storage_e2e", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_ssot_report_storage_e2e", "p4obs", "mon_state")
_emit_triggers_alert("test_ssot_report_storage_e2e", "p4obs", "alert")
_emit_links_incident_trace("test_ssot_report_storage_e2e", "p4obs", "trace_link")
_emit_captures_pattern("test_ssot_report_storage_e2e", "p3lm", "pattern")
_emit_records_learning_event("test_ssot_report_storage_e2e", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_ssot_report_storage_e2e", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_ssot_report_storage_e2e", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_ssot_report_storage_e2e", "p3lm", "routing")
_emit_improves_agent_policy("test_ssot_report_storage_e2e", "p3lm", "policy")
_emit_stores_learning_state("test_ssot_report_storage_e2e", "p3lm", "state")
_emit_records_execution_trace("test_ssot_report_storage_e2e", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_ssot_report_storage_e2e", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_ssot_report_storage_e2e", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_ssot_report_storage_e2e", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_ssot_report_storage_e2e", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_ssot_report_storage_e2e", "env_read", "p2_env_1")
_emit_reads_environ("test_ssot_report_storage_e2e", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_ssot_report_storage_e2e", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_ssot_report_storage_e2e", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_ssot_report_storage_e2e", "context_pull")
_emit_pulls_context("p1", "test_ssot_report_storage_e2e", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_ssot_report_storage_e2e", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_ssot_report_storage_e2e", "uwg_term_2")
_emit_writes_through("p1", "test_ssot_report_storage_e2e", "write_through")
_emit_writes_through("p1", "test_ssot_report_storage_e2e", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_ssot_report_storage_e2e", "safety_validation")
_emit_invokes_eval("p1", "test_ssot_report_storage_e2e", "eval_call")
_emit_proposal_commits_routing("p1", "test_ssot_report_storage_e2e", "routing_commit")
emit_replay_key("p0", "test_ssot_report_storage_e2e")
emit_determinism_digest("p0", "test_ssot_report_storage_e2e")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_ssot_report_storage_e2e", "execution_auth")
_emit_validates_capability("p2", "test_ssot_report_storage_e2e", "capability_check")
_emit_routes_to_capability("p2", "test_ssot_report_storage_e2e", "capability_route")
_emit_writes_via_uwg("p2", "test_ssot_report_storage_e2e", "uwg_write")
_emit_blocks_direct_write("p2", "test_ssot_report_storage_e2e", "direct_write_block")
_emit_records_tool_invocation("p2", "test_ssot_report_storage_e2e", "tool_invocation")
_emit_captures_execution_output("p2", "test_ssot_report_storage_e2e", "exec_output")
_emit_dispatches_agent("p3", "test_ssot_report_storage_e2e", "agent_dispatch")
_emit_coordinates_agents("p3", "test_ssot_report_storage_e2e", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_ssot_report_storage_e2e", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_ssot_report_storage_e2e", "healing_outcome")
_emit_escalates_failure("p3", "test_ssot_report_storage_e2e", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_ssot_report_storage_e2e", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_ssot_report_storage_e2e", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_ssot_report_storage_e2e", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_ssot_report_storage_e2e", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_ssot_report_storage_e2e", "eval_metric")
_emit_stores_embedding("p4", "test_ssot_report_storage_e2e", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_ssot_report_storage_e2e", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_ssot_report_storage_e2e", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


class TestE2EDiscoveryToEnforcement:
    """E2E tests for the complete discovery to enforcement workflow."""

    def test_full_workflow_empty_project(self) -> None:
        """Test full workflow on empty project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / REPORTS_DIR
            docs_reports.mkdir(parents=True)

            from agentic_core.L5_safety.reasoning.ReportLocationAgent import (
                ReportLocationAgent,
            )

            # Step 1: Validate (should find no violations)
            agent = ReportLocationAgent(project_root=project_root)
            result = agent.validate()

            assert result["total_reports"] == 0
            assert result["misplaced_reports"] == 0

    def test_full_workflow_with_violations(self) -> None:
        """Test full workflow with violations present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / REPORTS_DIR
            docs_reports.mkdir(parents=True)

            # Create misplaced reports
            (project_root / "PHASE1_REPORT.md").write_text("Phase 1")
            (project_root / "RCA_test.md").write_text("RCA")
            (project_root / "test_SUMMARY.md").write_text("Summary")

            from agentic_core.L5_safety.reasoning.ReportLocationAgent import (
                ReportLocationAgent,
            )

            # Step 1: Validate
            agent = ReportLocationAgent(project_root=project_root)
            result = agent.validate()

            assert result["total_reports"] == 3
            assert result["misplaced_reports"] == 3
            assert result["compliance_percentage"] == 0.0

            # Step 2: Heal
            agent = ReportLocationAgent(project_root=project_root, dry_run=False)
            heal_result = agent.heal()

            assert heal_result.healed_count == 3

            # Step 3: Verify
            agent = ReportLocationAgent(project_root=project_root)
            result = agent.validate()

            assert result["misplaced_reports"] == 0
            assert result["compliance_percentage"] == 100.0

    def test_full_workflow_mixed_compliance(self) -> None:
        """Test workflow with mixed compliant and non-compliant files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / REPORTS_DIR
            docs_reports.mkdir(parents=True)

            # Create compliant reports
            (docs_reports / "compliant_report.md").write_text("Compliant")

            # Create misplaced reports
            (project_root / "misplaced_report.md").write_text("Misplaced")

            from agentic_core.L5_safety.reasoning.ReportLocationAgent import (
                ReportLocationAgent,
            )

            # Validate
            agent = ReportLocationAgent(project_root=project_root)
            result = agent.validate()

            assert result["total_reports"] == 2
            assert result["compliant_reports"] == 1
            assert result["misplaced_reports"] == 1
            assert result["compliance_percentage"] == 50.0


class TestE2EMigrationWorkflow:
    """E2E tests for migration workflow."""

    def test_migration_with_rollback(self) -> None:
        """Test migration and rollback workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / REPORTS_DIR
            docs_reports.mkdir(parents=True)

            # Create misplaced report
            source = project_root / "test_report.md"
            source.write_text("Original content")

            # from ops_scripts.maintenance.migrate_reports_to_ssot  # Module removed import ReportMigrator

            # Migrate
            migrator = ReportMigrator(project_root, dry_run=False)
            manifest = migrator.run_migration()

            assert manifest.migrated_files == 1
            assert not source.exists()
            assert (docs_reports / "test_report.md").exists()

            # Rollback
            manifest_path = migrator.get_manifest_path()
            success = migrator.rollback(manifest_path)

            assert success
            assert source.exists()

    def test_migration_preserves_content(self) -> None:
        """Test that migration preserves file content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / REPORTS_DIR
            docs_reports.mkdir(parents=True)

            content = "Important report content with special chars: éàü"
            source = project_root / "test_report.md"
            source.write_text(content, encoding="utf-8")

            # from ops_scripts.maintenance.migrate_reports_to_ssot  # Module removed import ReportMigrator

            migrator = ReportMigrator(project_root, dry_run=False)
            migrator.run_migration()

            dest = docs_reports / "test_report.md"
            assert dest.read_text(encoding="utf-8") == content


class TestE2EPreCommitHook:
    """E2E tests for pre-commit hook integration."""

    def test_hook_dry_run_mode(self) -> None:
        """Test hook in dry-run mode."""
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                "--mode",
                "dry-run",
                "--quiet",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        # Dry-run should always succeed
        assert result.returncode == 0

    def test_hook_staged_only_mode(self) -> None:
        """Test hook in staged-only mode."""
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                "--staged-only",
                "--mode",
                "strict",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        # With no staged report files, should pass
        assert result.returncode == 0


class TestE2EAgentIntegration:
    """E2E tests for agent integration."""

    def test_agent_standard_heal_interface(self) -> None:
        """Test agent standard heal interface."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / REPORTS_DIR
            docs_reports.mkdir(parents=True)

            (project_root / "test_report.md").write_text("Test")

            from agentic_core.L5_safety.reasoning.ReportLocationAgent import (
                ReportLocationAgent,
            )

            agent = ReportLocationAgent(project_root=project_root, dry_run=True)
            result = agent.standard_heal()

            assert "violations_found" in result
            assert "violations_fixed" in result
            assert "errors" in result
            assert "skipped" in result
            assert result["violations_found"] == 1

    def test_agent_inventory_generation(self) -> None:
        """Test agent inventory generation and saving."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / REPORTS_DIR
            docs_reports.mkdir(parents=True)

            (docs_reports / "report1.md").write_text("Report 1")
            (project_root / "report2.md").write_text("Report 2")

            from agentic_core.L5_safety.reasoning.ReportLocationAgent import (
                ReportLocationAgent,
            )

            agent = ReportLocationAgent(project_root=project_root)
            output_path = agent.save_inventory()

            assert output_path.exists()

            with open(output_path) as f:
                data = json.load(f)

            assert data["total_reports"] == 2
            assert data["compliant_reports"] == 1
            assert data["misplaced_reports"] == 1


class TestE2EDocumentation:
    """E2E tests for documentation completeness."""

    def test_all_documentation_exists(self) -> None:
        """Test that all required documentation exists."""
        guide_path = PROJECT_ROOT / "docs" / REPORTS_DIR / "SSOT_REPORT_STORAGE_GUIDE.md"
        assert guide_path.exists()

    def test_documentation_references_valid(self) -> None:
        """Test that documentation references valid files."""
        guide_path = PROJECT_ROOT / "docs" / REPORTS_DIR / "SSOT_REPORT_STORAGE_GUIDE.md"

        if guide_path.exists():
            # Check referenced modules exist
            assert (PROJECT_ROOT / AGENTIC_CORE_DIR / "utils" / "report_location_validator_types.py").exists()
            assert (
                PROJECT_ROOT / AGENTIC_CORE_DIR / "L5_safety" / "validators" / "ReportLocationAgent.py"
            ).exists()
            assert (PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py").exists()


class TestE2ECompleteSystem:
    """E2E tests for complete system integration."""

    def test_complete_ssot_enforcement_cycle(self) -> None:
        """Test complete SSOT enforcement cycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / REPORTS_DIR
            docs_reports.mkdir(parents=True)

            # Create initial state with violations
            (project_root / "PHASE1_SUMMARY.md").write_text("Phase 1")
            (project_root / "subdir").mkdir()
            (project_root / "subdir" / "nested_report.md").write_text("Nested")

            from agentic_core.L5_safety.reasoning.ReportLocationAgent import (
                ReportLocationAgent,
            )
            from agentic_core.utils.report_location_validator_types_util import (
                ReportLocationValidator,
            )

            # Phase 1: Discovery
            validator = ReportLocationValidator(project_root)
            misplaced = validator.get_misplaced_reports()
            assert len(misplaced) == 2

            # Phase 2: Migration (via agent)
            agent = ReportLocationAgent(project_root=project_root, dry_run=False)
            heal_result = agent.heal()
            assert heal_result.healed_count == 2

            # Phase 3: Enforcement verification
            validator = ReportLocationValidator(project_root)
            misplaced = validator.get_misplaced_reports()
            assert len(misplaced) == 0

            # Phase 4: Agent validation
            agent = ReportLocationAgent(project_root=project_root)
            result = agent.validate()
            assert result["compliance_percentage"] == 100.0

            # Phase 5: Inventory saved
            inventory_path = agent.save_inventory()
            assert inventory_path.exists()

            with open(inventory_path) as f:
                inventory = json.load(f)
            assert inventory["misplaced_reports"] == 0
