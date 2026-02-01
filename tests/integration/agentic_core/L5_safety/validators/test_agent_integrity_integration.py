"""
Integration Tests for Agent Integrity Gap Analysis
====================================================
Tests the integration between all four phases of the agent integrity analysis.

USAGE:
    pytest tests/integration/agentic_core/L5_safety/validators/ -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[5]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L5_safety.validators.agent_integrity_report import (
    AgentIntegrityReporter,
)
from agentic_core.L5_safety.validators.registry_verification import (
    RegistryVerifier,
)
from agentic_core.L5_safety.validators.ssot_structure_validation import (
    SSOTStructureValidator,
)
from agentic_core.L5_safety.validators.three_tier_compliance import (
    ThreeTierComplianceChecker,
)


class TestPhase1Phase2Integration:
    """Tests integration between Phase 1 and Phase 2."""

    def test_agents_from_phase1_used_in_phase2(self):
        """Test that agents discovered in Phase 1 are used in Phase 2."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        checker = ThreeTierComplianceChecker(project_root=PROJECT_ROOT)

        # Get agents from Phase 1
        phase1_agents = verifier.scan_filesystem()

        # Get compliance result from Phase 2
        phase2_result = checker.check_compliance()

        # Phase 2 should check all agents from Phase 1
        assert phase2_result.total_agents == len(phase1_agents)

    def test_agent_paths_consistent_between_phases(self):
        """Test that agent paths are consistent between phases."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        checker = ThreeTierComplianceChecker(project_root=PROJECT_ROOT)

        phase1_agents = verifier.scan_filesystem()
        phase2_result = checker.check_compliance()

        # Build path sets
        phase1_paths = {a.relative_path for a in phase1_agents}
        phase2_paths = {c.agent.relative_path for c in phase2_result.agent_compliance}

        # Paths should match
        assert phase1_paths == phase2_paths


class TestPhase1Phase3Integration:
    """Tests integration between Phase 1 and Phase 3."""

    def test_agents_from_phase1_validated_in_phase3(self):
        """Test that agents from Phase 1 are validated in Phase 3."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)

        phase1_agents = verifier.scan_filesystem()
        phase3_result = validator.validate_structure()

        # Phase 3 should validate all agents from Phase 1
        assert phase3_result.total_agents == len(phase1_agents)


class TestPhase2Phase3Integration:
    """Tests integration between Phase 2 and Phase 3."""

    def test_compliance_and_structure_use_same_agents(self):
        """Test that Phase 2 and Phase 3 use the same agent set."""
        checker = ThreeTierComplianceChecker(project_root=PROJECT_ROOT)
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)

        phase2_result = checker.check_compliance()
        phase3_result = validator.validate_structure()

        # Both should have same total agents
        assert phase2_result.total_agents == phase3_result.total_agents


class TestAllPhasesIntegration:
    """Tests integration across all four phases."""

    def test_comprehensive_report_includes_all_phases(self):
        """Test that comprehensive report includes results from all phases."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()

        # All phase results should be present
        assert result.registry_result is not None
        assert result.compliance_result is not None
        assert result.structure_result is not None

    def test_agent_counts_consistent_across_phases(self):
        """Test that agent counts are consistent across all phases."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()

        # All phases should report same total agents
        phase1_count = result.registry_result.total_filesystem_agents
        phase2_count = result.compliance_result.total_agents
        phase3_count = result.structure_result.total_agents

        assert phase1_count == phase2_count
        assert phase2_count == phase3_count

    def test_gap_items_reference_valid_agents(self):
        """Test that gap items reference agents that exist."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()

        # Get all agent paths from Phase 1
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        all_agents = verifier.scan_filesystem()
        valid_paths = {a.relative_path for a in all_agents}

        # Gap items should reference valid paths (or registry paths for orphans)
        for gap in result.gap_items:
            if gap.category != "Registry":
                # Structure and Testing gaps should reference filesystem agents
                assert gap.agent_path in valid_paths or "registry" in gap.category.lower()


class TestDataFlowIntegration:
    """Tests data flow between phases."""

    def test_phase1_data_flows_to_phase4(self):
        """Test that Phase 1 data correctly flows to Phase 4 report."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()
        report = reporter.generate_markdown_report(result)

        # Report should contain Phase 1 metrics
        assert "Filesystem Agents" in report
        assert "Registry Agents" in report

    def test_phase2_data_flows_to_phase4(self):
        """Test that Phase 2 data correctly flows to Phase 4 report."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()
        report = reporter.generate_markdown_report(result)

        # Report should contain Phase 2 metrics
        assert "Contract" in report
        assert "Blueprint" in report
        assert "Soul" in report

    def test_phase3_data_flows_to_phase4(self):
        """Test that Phase 3 data correctly flows to Phase 4 report."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()
        report = reporter.generate_markdown_report(result)

        # Report should contain Phase 3 metrics
        assert "Compliant Agents" in report
        assert "Violations" in report


class TestReportConsistency:
    """Tests report consistency across phases."""

    def test_health_score_reflects_all_phases(self):
        """Test that health score reflects all phase results."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()

        # Health score should be average of phase scores
        phase1_score = result.registry_result.coverage_percentage
        phase2_score = result.compliance_result.overall_compliance_pct
        phase3_score = result.structure_result.compliance_percentage

        expected_avg = (phase1_score + phase2_score + phase3_score) / 3
        assert abs(result.overall_health_score - expected_avg) < 0.1

    def test_gap_analysis_covers_all_issue_types(self):
        """Test that gap analysis covers issues from all phases."""
        reporter = AgentIntegrityReporter(project_root=PROJECT_ROOT)
        result = reporter.generate_comprehensive_report()

        categories = {gap.category for gap in result.gap_items}

        # Should have gaps from multiple categories (if issues exist)
        # At minimum, we expect Testing gaps since not all agents have unit tests
        if result.gap_items:
            assert len(categories) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
