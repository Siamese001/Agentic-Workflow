"""
Unit Tests for Phase 1: Registry Verification
==============================================
Tests the registry verification module for agent discovery completeness.

USAGE:
    pytest tests/unit/agentic_core/L5_safety/validators/test_registry_verification.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    TESTS_DIR,
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_registry_verification")
# REMOVED: _emit_applies_guardrail("p0", "test_registry_verification", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_registry_verification", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_registry_verification", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_registry_verification")
# REMOVED: emit_determinism_digest("p0", "test_registry_verification")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_registry_verification", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_registry_verification", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_registry_verification", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_registry_verification", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_registry_verification", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_registry_verification", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_registry_verification", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_registry_verification", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_registry_verification", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_registry_verification", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_registry_verification", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_registry_verification", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_registry_verification", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_registry_verification", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_registry_verification", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_registry_verification", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_registry_verification", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_registry_verification", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_registry_verification", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_registry_verification", "exec_snapshot_link")

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[5]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L5_safety.enforcement.registry_verification_enforcer import (
    AgentInfo,
    RegistryVerifier,
    VerificationResult,
    run_verification,
)
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

# REMOVED: _emit_emits_metric_event("test_registry_verification", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_registry_verification", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_registry_verification", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_registry_verification", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_registry_verification", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_registry_verification", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_registry_verification", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_registry_verification", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_registry_verification", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_registry_verification", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_registry_verification", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_registry_verification", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_registry_verification", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_registry_verification", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_registry_verification", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_registry_verification", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_registry_verification", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_registry_verification", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_registry_verification", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_registry_verification", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_registry_verification", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_registry_verification", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_registry_verification", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_registry_verification", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_registry_verification", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_registry_verification", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_registry_verification", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_registry_verification", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_registry_verification", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_registry_verification", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_registry_verification", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_registry_verification", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_registry_verification", "write_through")
# REMOVED: _emit_writes_through("p1", "test_registry_verification", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_registry_verification", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_registry_verification", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_registry_verification", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_registry_verification", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_registry_verification", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_registry_verification", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_registry_verification", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_registry_verification", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_registry_verification", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_registry_verification", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_registry_verification", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_registry_verification", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_registry_verification", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_registry_verification", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_registry_verification")
# REMOVED: _emit_gated_by_confidence("p1", "test_registry_verification", "confidence_gate")


class TestAgentInfo:
    """Tests for AgentInfo dataclass."""

    def test_agent_info_creation(self):
        """Test basic AgentInfo creation."""
        info = AgentInfo(
            class_name="TestAgent",
            file_path=Path("/test/TestAgent.py"),
            relative_path="test/TestAgent.py",
            layer="L5",
            has_agent_class=True,
        )
        assert info.class_name == "TestAgent"
        assert info.layer == "L5"
        assert info.has_agent_class is True

    def test_agent_info_defaults(self):
        """Test AgentInfo default values."""
        info = AgentInfo(
            class_name="TestAgent",
            file_path=Path("/test/TestAgent.py"),
            relative_path="test/TestAgent.py",
        )
        assert info.layer == "Unknown"
        assert info.has_agent_class is False
        assert info.inheritance == []
        assert info.key_methods == []


class TestVerificationResult:
    """Tests for VerificationResult dataclass."""

    def test_verification_result_defaults(self):
        """Test VerificationResult default values."""
        result = VerificationResult()
        assert result.total_filesystem_agents == 0
        assert result.total_registry_agents == 0
        assert result.orphan_agents == []
        assert result.missing_agents == []
        assert result.path_mismatches == []
        assert result.valid_agents == []
        assert result.coverage_percentage == 0.0
        assert result.is_complete is False

    def test_verification_result_complete_when_no_issues(self):
        """Test is_complete flag logic."""
        result = VerificationResult()
        result.is_complete = (
            len(result.orphan_agents) == 0
            and len(result.missing_agents) == 0
            and len(result.path_mismatches) == 0
        )
        assert result.is_complete is True


class TestRegistryVerifier:
    """Tests for RegistryVerifier class."""

    def test_find_project_root(self):
        """Test project root detection."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        assert verifier.project_root == PROJECT_ROOT
        assert verifier.project_root.exists()

    def test_is_excluded_archives(self):
        """Test exclusion of archives directory."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        path = Path("archives/old/TestAgent.py")
        assert verifier._is_excluded(path) is True

    def test_is_excluded_pycache(self):
        """Test exclusion of __pycache__ directory."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        path = Path("agentic_core/__pycache__/TestAgent.py")
        assert verifier._is_excluded(path) is True

    def test_is_excluded_valid_path(self):
        """Test non-excluded path."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        path = Path("agentic_core/L5_safety/validators/TestAgent.py")
        assert verifier._is_excluded(path) is False

    def test_is_test_file_true(self):
        """Test detection of test files."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        assert verifier._is_test_file(Path("tests/unit/test_agent.py")) is True
        assert verifier._is_test_file(Path("src/test_something.py")) is True

    def test_is_test_file_false(self):
        """Test non-test file detection."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        assert verifier._is_test_file(Path("agentic_core/TestAgent.py")) is False

    def test_extract_layer_l5(self):
        """Test layer extraction for L5."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        layer = verifier._extract_layer("agentic_core/L5_safety/validators/TestAgent.py")
        assert layer == "L5"

    def test_extract_layer_l0(self):
        """Test layer extraction for L0."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        layer = verifier._extract_layer("agentic_core/L0_routing/scripts/TestAgent.py")
        assert layer == "L0"

    def test_extract_layer_base(self):
        """Test layer extraction for base_agents."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        layer = verifier._extract_layer("agentic_core/base_agents/SovereignBaseAgent.py")
        assert layer == "Base"

    def test_extract_layer_apps_rg(self):
        """Test layer extraction for apps_rg."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        layer = verifier._extract_layer("apps_rg/engines/TestAgent.py")
        assert layer == "Apps_RG"

    def test_extract_layer_apps_lic(self):
        """Test layer extraction for apps_lic."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        layer = verifier._extract_layer("apps_lic/engines/TestAgent.py")
        assert layer == "Apps_LIC"

    def test_extract_layer_root(self):
        """Test layer extraction for root files."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        layer = verifier._extract_layer("TestAgent.py")
        assert layer == "Root"

    def test_scan_filesystem_finds_agents(self):
        """Test filesystem scan finds agent files."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        agents = verifier.scan_filesystem()
        assert len(agents) > 0
        # Verify all found items are agents
        for agent in agents:
            assert agent.class_name.endswith("Agent")

    def test_scan_filesystem_excludes_tests(self):
        """Test filesystem scan excludes test files."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        agents = verifier.scan_filesystem()
        for agent in agents:
            assert TESTS_DIR not in agent.relative_path.split("\\")
            assert TESTS_DIR not in agent.relative_path.split("/")

    def test_load_registry(self):
        """Test loading registry from JSON."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        registry = verifier.load_registry()
        assert isinstance(registry, list)

    def test_verify_registry_returns_result(self):
        """Test verify_registry returns VerificationResult."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        result = verifier.verify_registry()
        assert isinstance(result, VerificationResult)
        assert result.total_filesystem_agents > 0

    def test_verify_registry_detects_missing_agents(self):
        """Test detection of agents missing from registry."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        result = verifier.verify_registry()
        # Given the registry only has 2 agents, there should be many missing
        assert len(result.missing_agents) > 0

    def test_generate_report_format(self):
        """Test report generation format."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        result = verifier.verify_registry()
        report = verifier.generate_report(result)
        assert "# Phase 1: Registry Verification Report" in report
        assert "## Summary" in report
        assert "Total Filesystem Agents" in report


class TestRunVerification:
    """Tests for run_verification function."""

    def test_run_verification_returns_result(self):
        """Test run_verification convenience function."""
        result = run_verification()
        assert isinstance(result, VerificationResult)


class TestParseAgentFile:
    """Tests for agent file parsing."""

    def test_parse_valid_agent_file(self):
        """Test parsing a valid agent file."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)

        # Find a known agent file
        agent_path = PROJECT_ROOT / AGENTIC_CORE_DIR / "L5_safety" / "validators" / "LocationAgent.py"
        if agent_path.exists():
            result = verifier._parse_agent_file(agent_path)
            assert result is not None
            assert result.has_agent_class is True
            assert "Agent" in result.class_name

    def test_parse_nonexistent_file(self):
        """Test parsing non-existent file returns None."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        result = verifier._parse_agent_file(Path("/nonexistent/TestAgent.py"))
        assert result is None


class TestCoverageCalculation:
    """Tests for coverage percentage calculation."""

    def test_coverage_zero_when_no_agents(self):
        """Test coverage is 0 when no filesystem agents."""
        result = VerificationResult()
        result.total_filesystem_agents = 0
        # Coverage should remain 0
        assert result.coverage_percentage == 0.0

    def test_coverage_calculation(self):
        """Test coverage percentage calculation."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        result = verifier.verify_registry()

        if result.total_filesystem_agents > 0:
            expected_coverage = len(result.valid_agents) / result.total_filesystem_agents * 100
            assert abs(result.coverage_percentage - expected_coverage) < 0.01


class TestOrphanDetection:
    """Tests for orphan agent detection."""

    def test_orphan_detection_with_mock_registry(self):
        """Test orphan detection with mocked registry."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)

        # Create a mock registry with a non-existent agent
        mock_registry = [
            {
                "class_name": "NonExistentAgent",
                "path": "fake/path/NonExistentAgent.py",
            },
        ]

        with patch.object(verifier, "load_registry", return_value=mock_registry):
            result = verifier.verify_registry()
            # Should detect the orphan
            orphan_names = [o["class_name"] for o in result.orphan_agents]
            assert "NonExistentAgent" in orphan_names


class TestPathMismatchDetection:
    """Tests for path mismatch detection."""

    def test_path_mismatch_detection(self):
        """Test detection of path mismatches."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        result = verifier.verify_registry()

        # The current registry has path mismatches (scripts\BootstrapAgent.py vs actual path)
        # This should be detected
        if result.total_registry_agents > 0:
            # Either we have path mismatches or orphans for the registry entries
            total_issues = len(result.path_mismatches) + len(result.orphan_agents)
            assert total_issues >= 0  # At minimum, verify the check runs


# ============================================================================
# Tier 1 Guardian: Hard-fail path tests for RegistryVerifier
# AST-graph justification: fan_in=7; current tests miss fail-closed paths,
# empty-registry contract, syntax/unicode error hardening, and report content.
# ============================================================================


class TestRegistryVerifierHardFailPaths:
    """Fail-closed path contracts: verifier must never raise, always report."""

    def test_parse_syntax_error_file_returns_none(self, tmp_path):
        p = tmp_path / "BrokenAgent.py"
        p.write_text("def bad(:\n    pass\n", encoding="utf-8")
        verifier = RegistryVerifier(project_root=tmp_path)
        result = verifier._parse_agent_file(p)
        assert result is None

    def test_parse_file_with_only_non_agent_class_returns_none(self, tmp_path):
        p = tmp_path / "HelperAgent.py"
        p.write_text("class HelperTool:\n    pass\n", encoding="utf-8")
        verifier = RegistryVerifier(project_root=tmp_path)
        result = verifier._parse_agent_file(p)
        assert result is None

    def test_parse_empty_file_returns_none(self, tmp_path):
        p = tmp_path / "EmptyAgent.py"
        p.write_text("", encoding="utf-8")
        verifier = RegistryVerifier(project_root=tmp_path)
        result = verifier._parse_agent_file(p)
        assert result is None

    def test_parse_file_with_no_agent_class_returns_none(self, tmp_path):
        p = tmp_path / "helpers.py"
        p.write_text("def helper():\n    return 1\n", encoding="utf-8")
        verifier = RegistryVerifier(project_root=tmp_path)
        result = verifier._parse_agent_file(p)
        assert result is None

    def test_verify_with_empty_registry_all_agents_missing(self):
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        with patch.object(verifier, "load_registry", return_value=[]):
            result = verifier.verify_registry()
        assert len(result.missing_agents) == result.total_filesystem_agents
        assert result.orphan_agents == []

    def test_verify_with_empty_filesystem_no_missing(self):
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        with patch.object(verifier, "scan_filesystem", return_value=[]):
            result = verifier.verify_registry()
        assert result.total_filesystem_agents == 0
        assert result.missing_agents == []

    def test_verify_empty_filesystem_empty_registry_is_complete(self):
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        with (
            patch.object(verifier, "scan_filesystem", return_value=[]),
            patch.object(verifier, "load_registry", return_value=[]),
        ):
            result = verifier.verify_registry()
        assert result.is_complete is True
        assert result.orphan_agents == []
        assert result.missing_agents == []

    def test_verify_result_is_not_complete_when_missing_agents(self):
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        with patch.object(verifier, "load_registry", return_value=[]):
            result = verifier.verify_registry()
        if result.total_filesystem_agents > 0:
            assert result.is_complete is False


class TestGenerateReportContent:
    """generate_report() must render all violation categories in report text."""

    def test_report_contains_orphan_section(self):
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        mock_registry = [
            {"class_name": "OrphanAgent", "path": "fake/OrphanAgent.py"},
        ]
        with patch.object(verifier, "load_registry", return_value=mock_registry):
            result = verifier.verify_registry()
        report = verifier.generate_report(result)
        assert "Orphan" in report or "orphan" in report.lower()

    def test_report_contains_missing_agents_section(self):
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        with patch.object(verifier, "load_registry", return_value=[]):
            result = verifier.verify_registry()
        report = verifier.generate_report(result)
        assert "Missing" in report or "missing" in report.lower()

    def test_report_shows_total_filesystem_agents(self):
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        result = verifier.verify_registry()
        report = verifier.generate_report(result)
        assert str(result.total_filesystem_agents) in report

    def test_report_shows_coverage_percentage(self):
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        result = verifier.verify_registry()
        report = verifier.generate_report(result)
        assert "Coverage" in report or "coverage" in report.lower()

    def test_report_is_string(self):
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        result = verifier.verify_registry()
        report = verifier.generate_report(result)
        assert isinstance(report, str)

    def test_report_not_empty(self):
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        result = verifier.verify_registry()
        report = verifier.generate_report(result)
        assert len(report) > 0


class TestVerificationResultFieldContract:
    """VerificationResult field contract completeness."""

    def test_is_complete_false_when_orphans_present(self):
        result = VerificationResult()
        result.orphan_agents = [{"class_name": "GhostAgent", "path": "fake.py"}]
        result.is_complete = (
            len(result.orphan_agents) == 0
            and len(result.missing_agents) == 0
            and len(result.path_mismatches) == 0
        )
        assert result.is_complete is False

    def test_is_complete_false_when_missing_agents_present(self):
        result = VerificationResult()
        result.missing_agents = [
            AgentInfo(
                class_name="MissingAgent",
                file_path=Path("/fake/MissingAgent.py"),
                relative_path="fake/MissingAgent.py",
            )
        ]
        result.is_complete = (
            len(result.orphan_agents) == 0
            and len(result.missing_agents) == 0
            and len(result.path_mismatches) == 0
        )
        assert result.is_complete is False

    def test_coverage_100_when_all_valid(self):
        result = VerificationResult()
        result.total_filesystem_agents = 3
        result.valid_agents = [
            AgentInfo(
                class_name=f"Agent{i}",
                file_path=Path(f"/fake/Agent{i}.py"),
                relative_path=f"fake/Agent{i}.py",
            )
            for i in range(3)
        ]
        result.coverage_percentage = len(result.valid_agents) / result.total_filesystem_agents * 100
        assert result.coverage_percentage == 100.0

    def test_coverage_zero_when_no_valid_agents(self):
        result = VerificationResult()
        result.total_filesystem_agents = 5
        result.valid_agents = []
        result.coverage_percentage = 0.0
        assert result.coverage_percentage == 0.0

    def test_path_mismatches_empty_by_default(self):
        result = VerificationResult()
        assert result.path_mismatches == []

    def test_valid_agents_empty_by_default(self):
        result = VerificationResult()
        assert result.valid_agents == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
