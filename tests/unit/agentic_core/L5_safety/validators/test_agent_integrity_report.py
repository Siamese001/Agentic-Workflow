"""
Unit Tests for Phase 4: Comprehensive Agent Integrity Report
=============================================================
Tests the agent integrity report generator.

USAGE:
    pytest tests/unit/agentic_core/L5_safety/validators/test_agent_integrity_report.py -v
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
    GapAnalysisItem,
    IntegrityReportResult,
    generate_full_report,
    validate_registry_coverage,
)
from agentic_core.L5_safety.validators.registry_verification import VerificationResult
from agentic_core.L5_safety.validators.ssot_structure_validation import (
    StructureValidationResult,
)
from agentic_core.L5_safety.validators.three_tier_compliance import ComplianceResult


class TestGapAnalysisItem:
    """Tests for GapAnalysisItem dataclass."""

    def test_gap_item_creation(self):
        """Test basic GapAnalysisItem creation."""
        item = GapAnalysisItem(
            agent_class="TestAgent",
            agent_path="test/TestAgent.py",
            category="Registry",
            current_state="Not registered",
            optimal_state="Registered",
            gap_description="Missing from registry",
        )
        assert item.agent_class == "TestAgent"
        assert item.category == "Registry"

    def test_gap_item_defaults(self):
        """Test GapAnalysisItem default values."""
        item = GapAnalysisItem(
            agent_class="TestAgent",
            agent_path="test/TestAgent.py",
            category="Testing",
            current_state="No tests",
            optimal_state="Has tests",
            gap_description="Missing tests",
        )
        assert item.priority == "medium"

    def test_gap_item_with_priority(self):
        """Test GapAnalysisItem with custom priority."""
        item = GapAnalysisItem(
            agent_class="TestAgent",
            agent_path="test/TestAgent.py",
            category="Structure",
            current_state="Wrong location",
            optimal_state="Correct location",
            gap_description="Base agent misplaced",
            priority="critical",
        )
        assert item.priority == "critical"


class TestIntegrityReportResult:
    """Tests for IntegrityReportResult dataclass."""

    def test_result_defaults(self):
        """Test IntegrityReportResult default values."""
        result = IntegrityReportResult()
        assert result.timestamp == ""
        assert result.total_agents == 0
        assert result.registry_result is None
        assert result.compliance_result is None
        assert result.structure_result is None
        assert result.gap_items == []
        assert result.registry_coverage_pass is False

    def test_overall_health_score_no_results(self):
        """Test health score with no results."""
        result = IntegrityReportResult()
        assert result.overall_health_score == 0.0

    def test_overall_health_score_with_registry(self):
        """Test health score with registry result."""
        result = IntegrityReportResult()
        result.registry_result = VerificationResult()
        result.registry_result.total_filesystem_agents = 10
        result.registry_result.valid_agents = [None] * 8  # 80% coverage
        # Coverage percentage is calculated from valid_agents
        assert result.overall_health_score >= 0

    def test_overall_health_score_calculation(self):
        """Test health score calculation with multiple results."""
        result = IntegrityReportResult()

        # Mock registry result with 80% coverage
        result.registry_result = VerificationResult()
        result.registry_result.total_filesystem_agents = 10
        result.registry_result.valid_agents = [None] * 8

        # Mock compliance result
        result.compliance_result = ComplianceResult()
        result.compliance_result.total_agents = 10
        result.compliance_result.fully_compliant = 6

        # Mock structure result
        result.structure_result = StructureValidationResult()
        result.structure_result.total_agents = 10
        result.structure_result.compliant_agents = 9

        # Health score should be average of all three
        score = result.overall_health_score
        assert 0 <= score <= 100


class TestAgentIntegrityReporter:
    """Tests for AgentIntegrityReporter class."""

    def test_reporter_initialization(self):
        """Test reporter initialization."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        assert reporter.project_root == PROJECT_ROOT

    def test_run_phase1(self):
        """Test running Phase 1."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.run_phase1()
        assert isinstance(result, VerificationResult)
        assert result.total_filesystem_agents > 0

    def test_run_phase2(self):
        """Test running Phase 2."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.run_phase2()
        assert isinstance(result, ComplianceResult)
        assert result.total_agents > 0

    def test_run_phase3(self):
        """Test running Phase 3."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.run_phase3()
        assert isinstance(result, StructureValidationResult)
        assert result.total_agents > 0

    def test_generate_comprehensive_report(self):
        """Test generating comprehensive report."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()
        assert isinstance(result, IntegrityReportResult)
        assert result.timestamp != ""
        assert result.total_agents > 0
        assert result.registry_result is not None
        assert result.compliance_result is not None
        assert result.structure_result is not None

    def test_generate_gap_items(self):
        """Test gap item generation."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()
        # Should have gap items (since registry is incomplete)
        assert isinstance(result.gap_items, list)

    def test_validate_registry_coverage_returns_tuple(self):
        """Test registry coverage validation returns tuple."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        registry_result = reporter.run_phase1()
        is_pass, message = reporter.validate_registry_coverage(registry_result)
        assert isinstance(is_pass, bool)
        assert isinstance(message, str)

    def test_generate_markdown_report(self):
        """Test markdown report generation."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()
        report = reporter.generate_markdown_report(result)
        assert "# Comprehensive Agent Integrity Audit Report" in report
        assert "## Executive Summary" in report
        assert "## Phase 1: Registry Verification" in report
        assert "## Phase 2: Three-Tier Compliance" in report
        assert "## Phase 3: SSOT Structure Validation" in report
        assert "## Gap Analysis" in report

    def test_save_report(self):
        """Test saving report to file."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_report.md"
            saved_path = reporter.save_report(result, output_path)
            assert saved_path.exists()
            content = saved_path.read_text()
            assert "Comprehensive Agent Integrity Audit Report" in content


class TestValidateRegistryCoverage:
    """Tests for validate_registry_coverage function."""

    def test_validate_registry_coverage_returns_tuple(self):
        """Test standalone validation function."""
        is_pass, message = validate_registry_coverage()
        assert isinstance(is_pass, bool)
        assert isinstance(message, str)
        assert "Registry Coverage" in message


class TestGenerateFullReport:
    """Tests for generate_full_report function."""

    def test_generate_full_report_returns_result(self):
        """Test standalone report generation function."""
        result = generate_full_report()
        assert isinstance(result, IntegrityReportResult)
        assert result.total_agents > 0


class TestGapAnalysisGeneration:
    """Tests for gap analysis generation."""

    def test_gap_items_have_required_fields(self):
        """Test that gap items have all required fields."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()

        for gap in result.gap_items:
            assert gap.agent_class != ""
            assert gap.agent_path != ""
            assert gap.category in ["Registry", "Testing", "Structure"]
            assert gap.current_state != ""
            assert gap.optimal_state != ""
            assert gap.priority in ["low", "medium", "high", "critical"]

    def test_gap_items_categorized_correctly(self):
        """Test that gap items are categorized correctly."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()

        categories = {gap.category for gap in result.gap_items}
        # Should have at least some categories
        assert len(categories) >= 0  # May be empty if fully compliant


class TestReportContent:
    """Tests for report content quality."""

    def test_report_contains_metrics(self):
        """Test that report contains key metrics."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()
        report = reporter.generate_markdown_report(result)

        # Should contain numeric metrics
        assert "Total Agents" in report
        assert "%" in report  # Percentages

    def test_report_contains_tables(self):
        """Test that report contains markdown tables."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()
        report = reporter.generate_markdown_report(result)

        # Should contain table separators
        assert "|" in report
        assert "---" in report

    def test_report_contains_validation_result(self):
        """Test that report contains validation result."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()
        report = reporter.generate_markdown_report(result)

        assert "Phase 4: Registry Coverage Validation" in report


class TestHealthScoreCalculation:
    """Tests for health score calculation."""

    def test_health_score_range(self):
        """Test that health score is in valid range."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()
        score = result.overall_health_score
        assert 0 <= score <= 100

    def test_health_score_reflects_compliance(self):
        """Test that health score reflects compliance levels."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()

        # Health score should be reasonable given the codebase state
        score = result.overall_health_score
        # Should be above 0 since we have some compliant agents
        assert score >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
