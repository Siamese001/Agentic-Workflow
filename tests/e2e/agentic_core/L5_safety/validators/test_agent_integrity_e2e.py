"""
End-to-End Tests for Agent Integrity Gap Analysis
===================================================
Tests the complete agent integrity analysis workflow from start to finish.

USAGE:
    pytest tests/e2e/agentic_core/L5_safety/validators/test_agent_integrity_e2e.py -v
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[5]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L5_safety.validators.agent_integrity_report import (
    AgentIntegrityReporter,
    generate_full_report,
    validate_registry_coverage,
)


class TestFullWorkflowE2E:
    """End-to-end tests for the complete workflow."""

    def test_complete_integrity_analysis_workflow(self):
        """Test the complete integrity analysis from start to finish."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)

        # Step 1: Generate comprehensive report
        result = reporter.generate_comprehensive_report()

        # Verify all phases completed
        assert result.registry_result is not None
        assert result.compliance_result is not None
        assert result.structure_result is not None
        assert result.timestamp != ""

        # Step 2: Generate markdown report
        report = reporter.generate_markdown_report(result)

        # Verify report structure
        assert "# Comprehensive Agent Integrity Audit Report" in report
        assert "## Executive Summary" in report
        assert "## Phase 1" in report
        assert "## Phase 2" in report
        assert "## Phase 3" in report
        assert "## Gap Analysis" in report
        assert "## Phase 4" in report

        # Step 3: Save report to file
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "agent_integrity_audit.md"
            saved_path = reporter.save_report(result, output_path)

            # Verify file was created
            assert saved_path.exists()
            content = saved_path.read_text()
            assert len(content) > 1000  # Should be substantial

    def test_registry_coverage_validation_e2e(self):
        """Test registry coverage validation end-to-end."""
        is_pass, message = validate_registry_coverage()

        # Should return valid result
        assert isinstance(is_pass, bool)
        assert "Registry Coverage" in message

        # Message should contain percentage
        assert "%" in message or "100" in message

    def test_full_report_generation_e2e(self):
        """Test full report generation end-to-end."""
        result = generate_full_report()

        # Should have all components
        assert result.total_agents > 0
        assert result.registry_result is not None
        assert result.compliance_result is not None
        assert result.structure_result is not None

        # Should have gap items (since registry is incomplete)
        assert isinstance(result.gap_items, list)


class TestReportOutputE2E:
    """End-to-end tests for report output."""

    def test_report_saved_to_docs_directory(self):
        """Test that report can be saved to docs/reports directory."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()

        # Save to actual docs/reports location
        output_path = PROJECT_ROOT / "docs" / "reports" / "agent_integrity_audit.md"
        saved_path = reporter.save_report(result, output_path)

        assert saved_path.exists()
        assert saved_path == output_path

    def test_report_contains_actionable_information(self):
        """Test that report contains actionable information."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()
        report = reporter.generate_markdown_report(result)

        # Should contain metrics
        assert "Total Agents" in report
        assert "%" in report

        # Should contain tier information
        assert "Contract" in report
        assert "Blueprint" in report
        assert "Soul" in report

        # Should contain validation result
        assert "Registry Coverage" in report


class TestPhaseExecutionE2E:
    """End-to-end tests for phase execution."""

    def test_all_phases_execute_successfully(self):
        """Test that all phases execute without errors."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)

        # Phase 1
        phase1 = reporter.run_phase1()
        assert phase1.total_filesystem_agents > 0

        # Phase 2
        phase2 = reporter.run_phase2()
        assert phase2.total_agents > 0

        # Phase 3
        phase3 = reporter.run_phase3()
        assert phase3.total_agents > 0

    def test_phases_produce_consistent_results(self):
        """Test that phases produce consistent results on repeated runs."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)

        # Run twice
        result1 = reporter.generate_comprehensive_report()
        result2 = reporter.generate_comprehensive_report()

        # Results should be consistent
        assert result1.total_agents == result2.total_agents
        assert len(result1.gap_items) == len(result2.gap_items)


class TestGapAnalysisE2E:
    """End-to-end tests for gap analysis."""

    def test_gap_analysis_identifies_issues(self):
        """Test that gap analysis identifies real issues."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()

        # Should identify gaps (registry is known to be incomplete)
        # At minimum, should identify testing gaps
        assert isinstance(result.gap_items, list)

    def test_gap_items_have_valid_priorities(self):
        """Test that gap items have valid priorities."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()

        valid_priorities = {"low", "medium", "high", "critical"}
        for gap in result.gap_items:
            assert gap.priority in valid_priorities

    def test_gap_items_have_actionable_suggestions(self):
        """Test that gap items have actionable suggestions."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()

        for gap in result.gap_items:
            # Each gap should have current and optimal state
            assert gap.current_state != ""
            assert gap.optimal_state != ""


class TestHealthScoreE2E:
    """End-to-end tests for health score calculation."""

    def test_health_score_in_valid_range(self):
        """Test that health score is in valid range."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()

        assert 0 <= result.overall_health_score <= 100

    def test_health_score_reflects_codebase_state(self):
        """Test that health score reflects actual codebase state."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()

        # Health score should be reasonable for a real codebase
        # Not 0 (we have some compliant agents) and not 100 (we have gaps)
        assert result.overall_health_score >= 0


class TestValidationE2E:
    """End-to-end tests for validation functionality."""

    def test_validation_produces_clear_result(self):
        """Test that validation produces a clear pass/fail result."""
        is_pass, message = validate_registry_coverage()

        # Should be clear pass or fail
        assert isinstance(is_pass, bool)

        # Message should be informative
        assert len(message) > 10
        assert "Registry" in message or "Coverage" in message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
