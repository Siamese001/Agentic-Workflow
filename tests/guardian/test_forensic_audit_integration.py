#!/usr/bin/env python3
"""
End-to-End and Integration Tests for AI-Checking-AI Forensic Audit

This module provides comprehensive integration tests that verify all six phases
of the AI-Checking-AI forensic audit work together correctly.

Phases Integrated:
- Phase 1: Forensic Audit Scope (Agent Discovery)
- Phase 2: LLM-Based Structural Validation Detection
- Phase 3: Apps Layer Validation Logic Detection
- Phase 4: Missing Guardian Test Links Detection
- Phase 5: Remediation Strategy (Deterministic Extraction)
- Phase 6: Apps Layer Specific Focus Analysis

The Law: AI Agents are prohibited from performing structural validation.
These checks must be deterministic Python scripts in tests/guardian/.
"""

from dataclasses import dataclass, field
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Import all phase modules
from tests.guardian.test_forensic_audit_phase1 import (
    AuditResult as Phase1Result,
    run_forensic_audit as run_phase1,
)
from tests.guardian.test_forensic_audit_phase2 import (
    Phase2AuditResult,
    run_phase2_audit as run_phase2,
)
from tests.guardian.test_forensic_audit_phase3 import (
    Phase3AuditResult,
    run_phase3_audit as run_phase3,
)
from tests.guardian.test_forensic_audit_phase4 import (
    Phase4AuditResult,
    run_phase4_audit as run_phase4,
)
from tests.guardian.test_forensic_audit_phase5 import (
    Phase5AuditResult,
    run_phase5_audit as run_phase5,
)
from tests.guardian.test_forensic_audit_phase6 import (
    Phase6AuditResult,
    run_phase6_audit as run_phase6,
)


@dataclass
class FullAuditResult:
    """Combined result from all audit phases."""

    phase1: Phase1Result | None = None
    phase2: Phase2AuditResult | None = None
    phase3: Phase3AuditResult | None = None
    phase4: Phase4AuditResult | None = None
    phase5: Phase5AuditResult | None = None
    phase6: Phase6AuditResult | None = None
    overall_health_score: float = 0.0
    total_violations: int = 0
    total_agents: int = 0
    execution_errors: list[str] = field(default_factory=list)


def run_full_audit(project_root: Path | None = None) -> FullAuditResult:
    """Run the complete forensic audit across all phases."""
    if project_root is None:
        project_root = PROJECT_ROOT

    result = FullAuditResult()

    # Phase 1: Agent Discovery
    try:
        result.phase1 = run_phase1(project_root)
        result.total_agents = result.phase1.total_agents
    except Exception as e:
        result.execution_errors.append(f"Phase 1 error: {e}")

    # Phase 2: LLM Validation Detection
    try:
        result.phase2 = run_phase2(project_root)
        result.total_violations += result.phase2.total_violations
    except Exception as e:
        result.execution_errors.append(f"Phase 2 error: {e}")

    # Phase 3: Apps Layer Validation
    try:
        result.phase3 = run_phase3(project_root)
        result.total_violations += result.phase3.total_violations
    except Exception as e:
        result.execution_errors.append(f"Phase 3 error: {e}")

    # Phase 4: Missing Guardian Links
    try:
        result.phase4 = run_phase4(project_root)
        result.total_violations += result.phase4.total_issues
    except Exception as e:
        result.execution_errors.append(f"Phase 4 error: {e}")

    # Phase 5: Remediation Strategy
    try:
        result.phase5 = run_phase5(project_root)
    except Exception as e:
        result.execution_errors.append(f"Phase 5 error: {e}")

    # Phase 6: Apps Layer Focus
    try:
        result.phase6 = run_phase6(project_root)
    except Exception as e:
        result.execution_errors.append(f"Phase 6 error: {e}")

    # Calculate overall health score
    result.overall_health_score = calculate_overall_health(result)

    return result


def calculate_overall_health(result: FullAuditResult) -> float:
    """Calculate overall health score from all phases."""
    scores = []

    if result.phase5 and result.phase5.health_score > 0:
        scores.append(result.phase5.health_score)

    if result.phase6 and result.phase6.structural_debt_score > 0:
        scores.append(result.phase6.structural_debt_score)

    if result.phase4:
        if result.phase4.total_agents_scanned > 0:
            coverage = (
                result.phase4.agents_with_guardian_tests / result.phase4.total_agents_scanned * 100
            )
            scores.append(coverage)

    if not scores:
        return 50.0  # Default neutral score

    return sum(scores) / len(scores)


def generate_full_report(result: FullAuditResult) -> str:
    """Generate a comprehensive audit report."""
    report = []
    report.append("=" * 70)
    report.append("AI-CHECKING-AI FORENSIC AUDIT - FULL INTEGRATION REPORT")
    report.append("=" * 70)
    report.append("")

    # Summary
    report.append("EXECUTIVE SUMMARY")
    report.append("-" * 50)
    report.append(f"Total Agents Discovered: {result.total_agents}")
    report.append(f"Total Violations Found: {result.total_violations}")
    report.append(f"Overall Health Score: {result.overall_health_score:.1f}/100")
    report.append("")

    # Phase-by-phase summary
    report.append("PHASE-BY-PHASE RESULTS")
    report.append("-" * 50)

    if result.phase1:
        report.append(f"✅ Phase 1: {result.phase1.total_agents} agents discovered")
    else:
        report.append("❌ Phase 1: FAILED")

    if result.phase2:
        report.append(
            f"✅ Phase 2: {result.phase2.agents_with_llm_validation} LLM validation violations"
        )
    else:
        report.append("❌ Phase 2: FAILED")

    if result.phase3:
        report.append(
            f"✅ Phase 3: {result.phase3.agents_with_validation} apps layer validation issues"
        )
    else:
        report.append("❌ Phase 3: FAILED")

    if result.phase4:
        report.append(f"✅ Phase 4: {result.phase4.agents_missing_links} missing Guardian links")
    else:
        report.append("❌ Phase 4: FAILED")

    if result.phase5:
        report.append(f"✅ Phase 5: {result.phase5.remediations_proposed} remediations proposed")
    else:
        report.append("❌ Phase 5: FAILED")

    if result.phase6:
        report.append(f"✅ Phase 6: {result.phase6.high_risk_agents} high-risk agents identified")
    else:
        report.append("❌ Phase 6: FAILED")

    report.append("")

    # Errors
    if result.execution_errors:
        report.append("EXECUTION ERRORS")
        report.append("-" * 50)
        for error in result.execution_errors:
            report.append(f"  ❌ {error}")
        report.append("")

    # Health Assessment
    report.append("OVERALL HEALTH ASSESSMENT")
    report.append("-" * 50)
    if result.overall_health_score >= 80:
        report.append("✅ HEALTHY: Repository meets AI-Checking-AI compliance")
    elif result.overall_health_score >= 60:
        report.append("⚠️  MODERATE: Some compliance issues need attention")
    elif result.overall_health_score >= 40:
        report.append("🟡 CONCERNING: Significant compliance gaps detected")
    else:
        report.append("🔴 CRITICAL: Major AI-Checking-AI violations detected")

    report.append("")
    report.append("=" * 70)

    return "\n".join(report)


# ============================================================================
# INTEGRATION TEST CASES
# ============================================================================


class TestForensicAuditIntegration:
    """Integration tests for the full forensic audit."""

    def test_all_phases_execute(self):
        """Test that all phases execute without errors."""
        result = run_full_audit(PROJECT_ROOT)

        assert result.phase1 is not None, "Phase 1 should complete"
        assert result.phase2 is not None, "Phase 2 should complete"
        assert result.phase3 is not None, "Phase 3 should complete"
        assert result.phase4 is not None, "Phase 4 should complete"
        assert result.phase5 is not None, "Phase 5 should complete"
        assert result.phase6 is not None, "Phase 6 should complete"

    def test_no_execution_errors(self):
        """Test that no execution errors occur."""
        result = run_full_audit(PROJECT_ROOT)
        assert len(result.execution_errors) == 0, f"Errors: {result.execution_errors}"

    def test_agent_count_consistency(self):
        """Test that agent counts are consistent across phases."""
        result = run_full_audit(PROJECT_ROOT)

        # Phase 1 should discover agents
        assert result.phase1.total_agents >= 50

        # Phase 4 should scan similar number
        assert result.phase4.total_agents_scanned >= 50

    def test_overall_health_score_valid(self):
        """Test that overall health score is valid."""
        result = run_full_audit(PROJECT_ROOT)
        assert 0 <= result.overall_health_score <= 100

    def test_report_generation(self):
        """Test that full report is properly generated."""
        result = run_full_audit(PROJECT_ROOT)
        report = generate_full_report(result)

        assert "FORENSIC AUDIT" in report
        assert "EXECUTIVE SUMMARY" in report
        assert "PHASE-BY-PHASE" in report
        assert "HEALTH ASSESSMENT" in report

    def test_phase_data_integrity(self):
        """Test that phase data is properly structured."""
        result = run_full_audit(PROJECT_ROOT)

        # Phase 1 integrity
        assert hasattr(result.phase1, "total_agents")
        assert hasattr(result.phase1, "agents_by_territory")

        # Phase 2 integrity
        assert hasattr(result.phase2, "violations")
        assert hasattr(result.phase2, "clean_agents")

        # Phase 3 integrity
        assert hasattr(result.phase3, "apps_lic_count")
        assert hasattr(result.phase3, "apps_rg_count")

        # Phase 4 integrity
        assert hasattr(result.phase4, "agents_with_guardian_tests")
        assert hasattr(result.phase4, "missing_links")

        # Phase 5 integrity
        assert hasattr(result.phase5, "health_score")
        assert hasattr(result.phase5, "proposals")

        # Phase 6 integrity
        assert hasattr(result.phase6, "structural_debt_score")
        assert hasattr(result.phase6, "analyses")


class TestEndToEndScenarios:
    """End-to-end test scenarios."""

    def test_full_audit_completes(self):
        """Test that full audit completes end-to-end."""
        result = run_full_audit(PROJECT_ROOT)

        # Should complete without None results
        assert all(
            [
                result.phase1,
                result.phase2,
                result.phase3,
                result.phase4,
                result.phase5,
                result.phase6,
            ]
        )

    def test_violation_tracking_works(self):
        """Test that violations are properly tracked across phases."""
        result = run_full_audit(PROJECT_ROOT)

        # Total violations should be sum of phase violations
        expected_total = 0
        if result.phase2:
            expected_total += result.phase2.total_violations
        if result.phase3:
            expected_total += result.phase3.total_violations
        if result.phase4:
            expected_total += result.phase4.total_issues

        assert result.total_violations == expected_total

    def test_territory_coverage(self):
        """Test that all territories are covered."""
        result = run_full_audit(PROJECT_ROOT)

        # Phase 1 should cover all territories
        territories = result.phase1.agents_by_territory
        assert "agentic_core" in territories
        assert "apps_lic" in territories
        assert "apps_rg" in territories

    def test_remediation_proposals_generated(self):
        """Test that remediation proposals are generated."""
        result = run_full_audit(PROJECT_ROOT)

        # Phase 5 should generate proposals
        assert isinstance(result.phase5.proposals, list)

    def test_risk_assessment_works(self):
        """Test that risk assessment works end-to-end."""
        result = run_full_audit(PROJECT_ROOT)

        # Phase 6 should assess risk
        total_risk = (
            result.phase6.high_risk_agents
            + result.phase6.medium_risk_agents
            + result.phase6.low_risk_agents
        )
        assert total_risk == len(result.phase6.analyses)


def test_forensic_audit_integration():
    """Main integration test entry point."""
    print("\n" + "=" * 70)
    print("AI-CHECKING-AI FORENSIC AUDIT - FULL INTEGRATION TEST")
    print("=" * 70 + "\n")

    result = run_full_audit(PROJECT_ROOT)
    report = generate_full_report(result)
    print(report)

    # Assertions
    assert len(result.execution_errors) == 0, "Should have no errors"
    assert result.total_agents >= 50, "Should discover 50+ agents"

    print("\n✅ Full Integration Test: PASSED")
    print(f"   Total Agents: {result.total_agents}")
    print(f"   Total Violations: {result.total_violations}")
    print(f"   Health Score: {result.overall_health_score:.1f}/100")


if __name__ == "__main__":
    test_forensic_audit_integration()
