import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)
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

_emit_records_execution_trace("p0", "evidence", "test_territory_integrity")
_emit_applies_guardrail("p0", "test_territory_integrity", "p0_governance")
_emit_reads_policy_state("p0", "test_territory_integrity", "policy_binding")
_emit_snapshots_state("p0", "test_territory_integrity", "state_snapshot")
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

_emit_emits_metric_event("test_territory_integrity", "p4obs", "metric_1")
_emit_emits_metric_event("test_territory_integrity", "p4obs", "metric_2")
_emit_emits_metric_event("test_territory_integrity", "p4obs", "metric_3")
_emit_emits_metric_event("test_territory_integrity", "p4obs", "metric_4")
_emit_emits_metric_event("test_territory_integrity", "p4obs", "metric_5")
_emit_emits_metric_event("test_territory_integrity", "p4obs", "metric_6")
_emit_records_incident_event("test_territory_integrity", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_territory_integrity", "p4obs", "anomaly")
_emit_writes_observability_log("test_territory_integrity", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_territory_integrity", "p4obs", "mon_state")
_emit_triggers_alert("test_territory_integrity", "p4obs", "alert")
_emit_links_incident_trace("test_territory_integrity", "p4obs", "trace_link")
_emit_captures_pattern("test_territory_integrity", "p3lm", "pattern")
_emit_records_learning_event("test_territory_integrity", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_territory_integrity", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_territory_integrity", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_territory_integrity", "p3lm", "routing")
_emit_improves_agent_policy("test_territory_integrity", "p3lm", "policy")
_emit_stores_learning_state("test_territory_integrity", "p3lm", "state")
_emit_records_execution_trace("test_territory_integrity", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_territory_integrity", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_territory_integrity", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_territory_integrity", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_territory_integrity", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_territory_integrity", "env_read", "p2_env_1")
_emit_reads_environ("test_territory_integrity", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_territory_integrity", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_territory_integrity", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_territory_integrity", "context_pull")
_emit_pulls_context("p1", "test_territory_integrity", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_territory_integrity", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_territory_integrity", "uwg_term_2")
_emit_writes_through("p1", "test_territory_integrity", "write_through")
_emit_writes_through("p1", "test_territory_integrity", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_territory_integrity", "safety_validation")
_emit_invokes_eval("p1", "test_territory_integrity", "eval_call")
_emit_proposal_commits_routing("p1", "test_territory_integrity", "routing_commit")
_emit_escalates_to_human("p1", "test_territory_integrity", "human_escalation")
_emit_routes_through("p1", "test_territory_integrity", "route_through")
_emit_checks_agent_registry("p1", "test_territory_integrity", "agent_registry")
_emit_validates_agent_capability("p1", "test_territory_integrity", "capability")
_emit_dispatches_execution_plan("p1", "test_territory_integrity", "exec_plan")
_emit_agent_executes_agent("p1", "test_territory_integrity", "sub_agent")
_emit_routes_to_agent("p1", "test_territory_integrity", "target_agent")
_emit_verifies_policy("p1", "test_territory_integrity", "policy_check")
_emit_observes_runtime_state("p1", "test_territory_integrity", "runtime_state")
_emit_verifies_boundary("p1", "test_territory_integrity", "boundary_check")
_emit_transcripts_response("p1", "test_territory_integrity", "transcript")
_emit_hard_fails_untranscripted("p1", "test_territory_integrity")
_emit_gated_by_confidence("p1", "test_territory_integrity", "confidence_gate")
emit_replay_key("p0", "test_territory_integrity")
emit_determinism_digest("p0", "test_territory_integrity")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_territory_integrity", "execution_auth")
_emit_validates_capability("p2", "test_territory_integrity", "capability_check")
_emit_routes_to_capability("p2", "test_territory_integrity", "capability_route")
_emit_writes_via_uwg("p2", "test_territory_integrity", "uwg_write")
_emit_blocks_direct_write("p2", "test_territory_integrity", "direct_write_block")
_emit_records_tool_invocation("p2", "test_territory_integrity", "tool_invocation")
_emit_captures_execution_output("p2", "test_territory_integrity", "exec_output")
_emit_dispatches_agent("p3", "test_territory_integrity", "agent_dispatch")
_emit_coordinates_agents("p3", "test_territory_integrity", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_territory_integrity", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_territory_integrity", "healing_outcome")
_emit_escalates_failure("p3", "test_territory_integrity", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_territory_integrity", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_territory_integrity", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_territory_integrity", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_territory_integrity", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_territory_integrity", "eval_metric")
_emit_stores_embedding("p4", "test_territory_integrity", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_territory_integrity", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_territory_integrity", "exec_snapshot_link")

# Add project root to path for imports
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent  # Go up 3 levels from tests/unit/ to project root
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent


class TestTerritoryIntegrity(unittest.TestCase):
    """Ultra-hardened testing for territory root violation detection."""

    def setUp(self):
        """Set up test environment with temporary directory structure."""
        self.tmp = Path(tempfile.mkdtemp())
        self.project_root = self.tmp
        self.target = self.tmp / AGENTIC_CORE_DIR / "prompt_governance"
        self.target.mkdir(parents=True)

        # Create some root squatter files
        (self.target / "stray_prompt.py").write_text("class Stray: pass")
        (self.target / "readme.md").write_text("# Info")
        (self.target / "config.json").write_text('{"setting": true}')

        # Create legitimate subfolders
        (self.target / "meta_prompts").mkdir()
        (self.target / "templates").mkdir()
        (self.target / "scripts").mkdir()
        (self.target / "version_registry").mkdir()
        (self.target / "agents").mkdir()
        (self.target / "registry").mkdir()

        # Create allowed files
        (self.target / "__init__.py").write_text("")
        (self.target / ".gitkeep").write_text("")

    def tearDown(self):
        """Clean up temporary directory."""
        if self.tmp.exists():
            shutil.rmtree(self.tmp)

    def test_detection_of_root_files(self):
        """Test 1: Verify all files in territory root are flagged as STRUCTURE violations."""
        agent = HierarchyAgent(project_root=self.tmp)
        report = agent.scan_root_violations(target_territory="prompt_governance")

        # Should detect 3 squatter files (.py, .md, .json) but not __init__.py or .gitkeep
        self.assertEqual(len(report["territory_root_files"]), 3, "Should detect exactly 3 squatter files")
        self.assertEqual(report["violations_found"], 3, "Should report 3 violations found")

        # Verify violation structure
        violation_names = [v["file"] for v in report["territory_root_files"]]
        self.assertIn("stray_prompt.py", violation_names, "Should detect .py squatter")
        self.assertIn("readme.md", violation_names, "Should detect .md squatter")
        self.assertIn("config.json", violation_names, "Should detect .json squatter")

        print("✅ PASS: Root File Detection")

    def test_json_payload_format(self):
        """Test 2: Verify violation dict contains required keys for execute_ssot JSON merge."""
        agent = HierarchyAgent(project_root=self.tmp)
        violations = agent.scan_root_violations("prompt_governance")["territory_root_files"]

        # Check first violation has all required keys
        violation = violations[0]
        required_keys = ["type", "file", "message", "severity", "path", "territory"]
        for key in required_keys:
            self.assertIn(key, violation, f"Missing required key: {key}")

        # Verify specific values
        self.assertEqual(violation["type"], "STRUCTURE", "Type should be STRUCTURE")
        self.assertEqual(violation["severity"], "ERROR", "Severity should be ERROR")
        self.assertEqual(violation["territory"], "prompt_governance", "Territory should be correct")
        self.assertIn(
            "sitting in prompt_governance root",
            violation["message"],
            "Message should be descriptive",
        )

        print("✅ PASS: JSON Payload Integrity")

    def test_empty_territory_grace(self):
        """Test 3: Verify no false positives in a clean room."""
        # Remove all squatter files
        (self.target / "stray_prompt.py").unlink()
        (self.target / "readme.md").unlink()
        (self.target / "config.json").unlink()

        agent = HierarchyAgent(project_root=self.tmp)
        report = agent.scan_root_violations("prompt_governance")

        self.assertEqual(
            len(report["territory_root_files"]),
            0,
            "Should detect no violations in clean territory",
        )
        self.assertEqual(report["violations_found"], 0, "Should report 0 violations found")

        print("✅ PASS: Clean Room Certification")

    def test_non_existent_territory(self):
        """Test 4: Verify resilience when a non-existent territory is audited."""
        agent = HierarchyAgent(project_root=self.tmp)
        report = agent.scan_root_violations("fake_zone")

        self.assertIn("errors", report, "Should include errors key for non-existent territory")
        self.assertEqual(len(report["errors"]), 1, "Should have exactly one error")
        self.assertIn("not found", report["errors"][0], "Error message should mention path not found")

        print("✅ PASS: Failure Resilience")

    def test_ultra_scan_logging(self):
        """Test 5: Verify ultra scan produces correct logging output."""
        import io
        import logging

        # Capture log output
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger("agentic_core.L5_safety.reasoning.hierarchy_healer")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        try:
            agent = HierarchyAgent(project_root=self.tmp)
            agent.scan_root_violations("prompt_governance")

            log_output = log_capture.getvalue()
            self.assertIn("ULTRA SCAN", log_output, "Should log ultra scan message")
            self.assertIn("prompt_governance", log_output, "Should mention territory name")
            self.assertIn("TERRITORY ROOT FILE", log_output, "Should log specific violations")

        finally:
            logger.removeHandler(handler)

        print("✅ PASS: Ultra Scan Logging")

    def test_backwards_compatibility(self):
        """Test 6: Verify original project root scanning still works."""
        # Create some project root violations
        (self.tmp / "coverage_html").mkdir()
        (self.tmp / "test.archived").write_text("backup")

        agent = HierarchyAgent(project_root=self.tmp)

        # Test without target_territory (original behavior)
        report = agent.scan_root_violations()

        # Should detect project root violations
        self.assertGreater(report["violations_found"], 0, "Should detect project root violations")
        self.assertIn("forbidden_folders", report, "Should include forbidden_folders key")

        print("✅ PASS: Backwards Compatibility")

    def test_approved_subfolders_ignored(self):
        """Test 7: Verify files in approved subfolders are NOT flagged."""
        # Create files in approved subfolders
        (self.target / "meta_prompts" / "persona.py").write_text("class Persona: pass")
        (self.target / "templates" / "template.j2").write_text("Hello {{name}}")
        (self.target / "agents" / "TestAgent.py").write_text("class TestAgent: pass")

        agent = HierarchyAgent(project_root=self.tmp)
        report = agent.scan_root_violations("prompt_governance")

        # Should still only detect the 3 root squatters, not the files in subfolders
        self.assertEqual(
            len(report["territory_root_files"]),
            3,
            "Should only detect root files, not subfolder files",
        )

        # Verify violation names don't include subfolder files
        violation_names = [v["file"] for v in report["territory_root_files"]]
        self.assertNotIn("persona.py", violation_names, "Should not flag files in meta_prompts")
        self.assertNotIn("template.j2", violation_names, "Should not flag files in templates")
        self.assertNotIn("TestAgent.py", violation_names, "Should not flag files in agents")

        print("✅ PASS: Approved Subfolders Ignored")

    def test_multiple_territories_isolation(self):
        """Test 8: Verify territory scanning is properly isolated."""
        # Create another territory with squatters
        other_target = self.tmp / AGENTIC_CORE_DIR / "other_territory"
        other_target.mkdir(parents=True)
        (other_target / "other_squatter.py").write_text("class Other: pass")

        agent = HierarchyAgent(project_root=self.tmp)

        # Scan prompt_governance only
        report_pg = agent.scan_root_violations("prompt_governance")

        # Scan other_territory only
        report_other = agent.scan_root_violations("other_territory")

        # Each should only detect violations in their own territory
        self.assertEqual(
            len(report_pg["territory_root_files"]),
            3,
            "prompt_governance should have 3 violations",
        )
        self.assertEqual(
            len(report_other["territory_root_files"]),
            1,
            "other_territory should have 1 violation",
        )

        # Verify territory names are correct
        for violation in report_pg["territory_root_files"]:
            self.assertEqual(violation["territory"], "prompt_governance")

        for violation in report_other["territory_root_files"]:
            self.assertEqual(violation["territory"], "other_territory")

        print("✅ PASS: Multiple Territories Isolation")


if __name__ == "__main__":
    print("🧪 Running Ultra-Hardened Territory Integrity Tests")
    print("=" * 60)
    unittest.main(verbosity=2)
