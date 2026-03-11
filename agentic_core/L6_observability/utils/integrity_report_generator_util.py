"""
Phase 4: Comprehensive Agent Integrity Report Generator
========================================================
Generates a comprehensive agent integrity audit report combining all phases.

This module provides:
1. Combined report from Phase 1, 2, and 3
2. Gap analysis: Current State vs Optimal Target State
3. 100% registry coverage validation script
4. Markdown report output

USAGE:
    from agentic_core.L5_safety.validators.agent_integrity_report import (
        AgentIntegrityReporter
    )
    reporter = AgentIntegrityReporter()
    report = reporter.generate_comprehensive_report()
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.L2_execution.tools import write_gateway as _wg
from agentic_core.L5_safety.enforcement.registry_verification_enforcer import (
    RegistryVerifier,
    VerificationResult,
)
from agentic_core.L5_safety.enforcement.ssot_structure_validation_enforcer import (
    SSOTStructureValidator,
    StructureValidationResult,
)
from agentic_core.L5_safety.enforcement.three_tier_compliance_enforcer import (
    ComplianceResult,
    ThreeTierComplianceChecker,
)
from agentic_core.L5_safety.config.structure_blueprint_config import REPORTS_DIR


@dataclass
class GapAnalysisItem:
    """A single gap analysis item comparing current vs optimal state."""

    agent_class: str
    agent_path: str
    category: str
    current_state: str
    optimal_state: str
    gap_description: str
    priority: str = "medium"  # low, medium, high, critical


@dataclass
class IntegrityReportResult:
    """Complete integrity report result."""

    timestamp: str = ""
    total_agents: int = 0

    # Phase 1: Registry Verification
    registry_result: VerificationResult | None = None

    # Phase 2: Three-Tier Compliance
    compliance_result: ComplianceResult | None = None

    # Phase 3: SSOT Structure
    structure_result: StructureValidationResult | None = None

    # Gap Analysis
    gap_items: list[GapAnalysisItem] = field(default_factory=list)

    # Validation
    registry_coverage_pass: bool = False
    errors: list[str] = field(default_factory=list)

    @property
    def overall_health_score(self) -> float:
        """Calculate overall health score (0-100)."""
        scores = []

        if self.registry_result:
            scores.append(self.registry_result.coverage_percentage)

        if self.compliance_result:
            scores.append(self.compliance_result.overall_compliance_pct)

        if self.structure_result:
            scores.append(self.structure_result.compliance_percentage)

        if not scores:
            return 0.0
        return sum(scores) / len(scores)


class AgentIntegrityReporter:
    """Generates comprehensive agent integrity reports."""

    def __init__(self, project_root: Path | None = None):
        """Initialize reporter with project root."""
        self.registry_verifier = RegistryVerifier(project_root)
        self.project_root = self.registry_verifier.project_root
        self.compliance_checker = ThreeTierComplianceChecker(project_root)
        self.structure_validator = SSOTStructureValidator(project_root)

    def run_phase1(self) -> VerificationResult:
        """Run Phase 1: Registry Verification."""
        return self.registry_verifier.verify_registry()

    def run_phase2(self) -> ComplianceResult:
        """Run Phase 2: Three-Tier Compliance."""
        return self.compliance_checker.check_compliance()

    def run_phase3(self) -> StructureValidationResult:
        """Run Phase 3: SSOT Structure Validation."""
        return self.structure_validator.validate_structure()

    def _generate_gap_items(
        self,
        registry_result: VerificationResult,
        compliance_result: ComplianceResult,
        structure_result: StructureValidationResult,
    ) -> list[GapAnalysisItem]:
        """Generate gap analysis items from all phase results."""
        gaps: list[GapAnalysisItem] = []

        # Gap items from Phase 1: Missing from registry
        for agent in registry_result.missing_agents:
            gaps.append(
                GapAnalysisItem(
                    agent_class=agent.class_name,
                    agent_path=agent.relative_path,
                    category="Registry",
                    current_state="Not in agent_discovery_full.json",
                    optimal_state="Registered in agent_discovery_full.json",
                    gap_description="Agent exists in filesystem but not in registry",
                    priority="high",
                ),
            )

        # Gap items from Phase 1: Orphan agents
        for orphan in registry_result.orphan_agents:
            gaps.append(
                GapAnalysisItem(
                    agent_class=orphan["class_name"],
                    agent_path=orphan["registry_path"],
                    category="Registry",
                    current_state="In registry but file missing",
                    optimal_state="File exists or removed from registry",
                    gap_description=orphan["reason"],
                    priority="critical",
                ),
            )

        # Gap items from Phase 2: Missing Soul tier (unit tests)
        for compliance in compliance_result.agent_compliance:
            if not compliance.soul_tier.is_covered:
                gaps.append(
                    GapAnalysisItem(
                        agent_class=compliance.agent.class_name,
                        agent_path=compliance.agent.relative_path,
                        category="Testing",
                        current_state="No dedicated unit tests",
                        optimal_state="Has dedicated unit test file",
                        gap_description="Agent lacks Soul tier coverage",
                        priority="medium",
                    ),
                )

        # Gap items from Phase 3: Structure violations
        for violation in structure_result.violations:
            priority = "medium"
            if violation.severity == "critical":
                priority = "critical"
            elif violation.severity == "error":
                priority = "high"

            gaps.append(
                GapAnalysisItem(
                    agent_class=violation.agent_class,
                    agent_path=violation.agent_path,
                    category="Structure",
                    current_state=violation.message,
                    optimal_state=violation.suggested_fix or "Compliant with SSOT",
                    gap_description=f"{violation.violation_type}: {violation.message}",
                    priority=priority,
                ),
            )

        return gaps

    def validate_registry_coverage(self, registry_result: VerificationResult) -> tuple[bool, str]:
        """Validate 100% registry coverage."""
        if registry_result.total_filesystem_agents == 0:
            return False, "No agents found in filesystem"

        coverage = registry_result.coverage_percentage

        if coverage == 100.0:
            return True, "Registry Coverage: 100% Pass"

        missing_count = len(registry_result.missing_agents)
        return False, f"Registry Coverage: {coverage:.1f}% ({missing_count} agents missing)"

    def generate_comprehensive_report(self) -> IntegrityReportResult:
        """Generate comprehensive integrity report from all phases."""
        result = IntegrityReportResult()
        result.timestamp = datetime.now().isoformat()

        # Run all phases
        result.registry_result = self.run_phase1()
        result.compliance_result = self.run_phase2()
        result.structure_result = self.run_phase3()

        # Set total agents
        result.total_agents = result.registry_result.total_filesystem_agents

        # Generate gap analysis
        result.gap_items = self._generate_gap_items(
            result.registry_result,
            result.compliance_result,
            result.structure_result,
        )

        # Validate registry coverage
        result.registry_coverage_pass, _ = self.validate_registry_coverage(result.registry_result)

        return result

    def generate_markdown_report(self, result: IntegrityReportResult) -> str:
        """Generate markdown report from integrity result."""
        lines = [
            "# Comprehensive Agent Integrity Audit Report",
            "",
            f"**Generated:** {result.timestamp}",
            "",
            "## Executive Summary",
            "",
            f"- **Total Agents Scanned:** {result.total_agents}",
            f"- **Overall Health Score:** {result.overall_health_score:.1f}%",
            f"- **Registry Coverage:** {'PASS' if result.registry_coverage_pass else 'FAIL'}",
            "",
            "---",
            "",
        ]

        # Phase 1 Summary
        if result.registry_result:
            reg = result.registry_result
            lines.extend(
                [
                    "## Phase 1: Registry Verification",
                    "",
                    "| Metric | Value |",
                    "|--------|-------|",
                    f"| Filesystem Agents | {reg.total_filesystem_agents} |",
                    f"| Registry Agents | {reg.total_registry_agents} |",
                    f"| Valid (Matched) | {len(reg.valid_agents)} |",
                    f"| Missing from Registry | {len(reg.missing_agents)} |",
                    f"| Orphan Agents | {len(reg.orphan_agents)} |",
                    f"| Path Mismatches | {len(reg.path_mismatches)} |",
                    f"| Coverage | {reg.coverage_percentage:.1f}% |",
                    "",
                ],
            )

        # Phase 2 Summary
        if result.compliance_result:
            comp = result.compliance_result
            lines.extend(
                [
                    "## Phase 2: Three-Tier Compliance",
                    "",
                    "| Tier | Covered | Percentage |",
                    "|------|---------|------------|",
                    f"| Contract (Pre-Commit) | {comp.contract_covered} | "
                    f"{comp.contract_coverage_pct:.1f}% |",
                    f"| Blueprint (Guardian) | {comp.blueprint_covered} | "
                    f"{comp.blueprint_coverage_pct:.1f}% |",
                    f"| Soul (Unit Tests) | {comp.soul_covered} | {comp.soul_coverage_pct:.1f}% |",
                    "",
                    f"**Fully Compliant Agents:** {comp.fully_compliant} "
                    f"({comp.overall_compliance_pct:.1f}%)",
                    "",
                ],
            )

        # Phase 3 Summary
        if result.structure_result:
            struct = result.structure_result
            lines.extend(
                [
                    "## Phase 3: SSOT Structure Validation",
                    "",
                    "| Metric | Value |",
                    "|--------|-------|",
                    f"| Compliant Agents | {struct.compliant_agents} |",
                    f"| Total Violations | {len(struct.violations)} |",
                    f"| Base Agent Violations | {len(struct.base_agent_violations)} |",
                    f"| Layer Violations | {len(struct.layer_violations)} |",
                    f"| Depth Violations | {len(struct.depth_violations)} |",
                    f"| Territory Violations | {len(struct.territory_violations)} |",
                    f"| Compliance | {struct.compliance_percentage:.1f}% |",
                    "",
                ],
            )

        # Gap Analysis
        lines.extend(
            [
                "---",
                "",
                "## Gap Analysis: Current State vs Optimal Target State",
                "",
            ],
        )

        # Group gaps by priority
        critical_gaps = [g for g in result.gap_items if g.priority == "critical"]
        high_gaps = [g for g in result.gap_items if g.priority == "high"]
        medium_gaps = [g for g in result.gap_items if g.priority == "medium"]

        if critical_gaps:
            lines.extend(
                [
                    "### Critical Priority Gaps",
                    "",
                    "| Agent | Category | Current State | Optimal State |",
                    "|-------|----------|---------------|---------------|",
                ],
            )
            for gap in critical_gaps[:15]:
                lines.append(
                    f"| {gap.agent_class} | {gap.category} | "
                    f"{gap.current_state[:40]} | {gap.optimal_state[:40]} |",
                )
            if len(critical_gaps) > 15:
                lines.append(f"| ... | ({len(critical_gaps) - 15} more) | ... | ... |")
            lines.append("")

        if high_gaps:
            lines.extend(
                [
                    "### High Priority Gaps",
                    "",
                    f"Found {len(high_gaps)} high priority gaps.",
                    "",
                ],
            )

        if medium_gaps:
            lines.extend(
                [
                    "### Medium Priority Gaps",
                    "",
                    f"Found {len(medium_gaps)} medium priority gaps (unit test coverage).",
                    "",
                ],
            )

        # Validation Script Result
        lines.extend(
            [
                "---",
                "",
                "## Phase 4: Registry Coverage Validation",
                "",
                "```",
                f"Registry Coverage: {'100% Pass' if result.registry_coverage_pass else 'FAIL'}",
                "```",
                "",
            ],
        )

        return "\n".join(lines)

    def save_report(self, result: IntegrityReportResult, output_path: Path | None = None) -> Path:
        """Save report to markdown file."""
        if output_path is None:
            output_path = self.project_root / "docs" / REPORTS_DIR / "agent_integrity_audit.md"

        _wg.ensure_dir(output_path.parent)

        report_content = self.generate_markdown_report(result)
        assert_no_persistent_write("L6", "write_text")  # G-12-1: mutation prohibition guard
        _wg.write_text(output_path, report_content, encoding="utf-8")

        return output_path


def validate_registry_coverage() -> tuple[bool, str]:
    """Validate 100% registry coverage - standalone function."""
    reporter = AgentIntegrityReporter()
    registry_result = reporter.run_phase1()
    return reporter.validate_registry_coverage(registry_result)


def generate_full_report() -> IntegrityReportResult:
    """Generate full integrity report - standalone function."""
    reporter = AgentIntegrityReporter()
    return reporter.generate_comprehensive_report()


if __name__ == "__main__":
    reporter = AgentIntegrityReporter()
    result = reporter.generate_comprehensive_report()
    report = reporter.generate_markdown_report(result)
    print(report)

    # Save to file
    output_path = reporter.save_report(result)
    print(f"\nReport saved to: {output_path}")
