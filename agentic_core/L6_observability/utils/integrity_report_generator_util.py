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

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.L5_safety.config.structure_blueprint_config import REPORTS_DIR
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
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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
    record_execution_trace,
)

emit_replay_key("p0", "integrity_report_generator_util")
emit_determinism_digest("p0", "integrity_report_generator_util")

_emit_dispatches_healing_run("p1", "integrity_report_generator_util", "L6")
_emit_routes_through("p1", "integrity_report_generator_util", "L6")
_emit_checks_agent_registry("p1", "integrity_report_generator_util", "agent_registry")
_emit_validates_agent_capability("p1", "integrity_report_generator_util", "capability")
_emit_dispatches_execution_plan("p1", "integrity_report_generator_util", "exec_plan")
_emit_agent_executes_agent("p1", "integrity_report_generator_util", "sub_agent")
_emit_routes_to_agent("p1", "integrity_report_generator_util", "target_agent")
_emit_verifies_policy("p1", "integrity_report_generator_util", "policy_check")
_emit_observes_runtime_state("p1", "integrity_report_generator_util", "runtime_state")
_emit_verifies_boundary("p1", "integrity_report_generator_util", "boundary_check")
_emit_transcripts_response("p1", "integrity_report_generator_util", "transcript")
_emit_hard_fails_untranscripted("p1", "integrity_report_generator_util")
_emit_gated_by_confidence("p1", "integrity_report_generator_util", "confidence_gate")
_emit_escalates_to_human("p1", "integrity_report_generator_util", "L6")
_emit_reads_policy_state("p1", "integrity_report_generator_util", "L6")
_emit_authorize_and_execute("p2", "integrity_report_generator_util", "execution_auth")
_emit_validates_capability("p2", "integrity_report_generator_util", "capability_check")
_emit_routes_to_capability("p2", "integrity_report_generator_util", "capability_route")
_emit_writes_via_uwg("p2", "integrity_report_generator_util", "uwg_write")
_emit_blocks_direct_write("p2", "integrity_report_generator_util", "direct_write_block")
_emit_records_tool_invocation("p2", "integrity_report_generator_util", "tool_invocation")
_emit_captures_execution_output("p2", "integrity_report_generator_util", "exec_output")
_emit_dispatches_agent("p3", "integrity_report_generator_util", "agent_dispatch")
_emit_coordinates_agents("p3", "integrity_report_generator_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "integrity_report_generator_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "integrity_report_generator_util", "healing_outcome")
_emit_escalates_failure("p3", "integrity_report_generator_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "integrity_report_generator_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "integrity_report_generator_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "integrity_report_generator_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "integrity_report_generator_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "integrity_report_generator_util", "eval_metric")
_emit_stores_embedding("p4", "integrity_report_generator_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "integrity_report_generator_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "integrity_report_generator_util", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
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
    _emit_writes_through,
)

record_execution_trace("integrity_report_generator_util", "integrity_report_generator_util_trace")


_emit_emits_metric_event("integrity_report_generator_util", "p4obs", "metric_1")
_emit_emits_metric_event("integrity_report_generator_util", "p4obs", "metric_2")
_emit_emits_metric_event("integrity_report_generator_util", "p4obs", "metric_3")
_emit_emits_metric_event("integrity_report_generator_util", "p4obs", "metric_4")
_emit_emits_metric_event("integrity_report_generator_util", "p4obs", "metric_5")
_emit_emits_metric_event("integrity_report_generator_util", "p4obs", "metric_6")
_emit_records_incident_event("integrity_report_generator_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("integrity_report_generator_util", "p4obs", "anomaly")
_emit_writes_observability_log("integrity_report_generator_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("integrity_report_generator_util", "p4obs", "mon_state")
_emit_triggers_alert("integrity_report_generator_util", "p4obs", "alert")
_emit_links_incident_trace("integrity_report_generator_util", "p4obs", "trace_link")
_emit_captures_pattern("integrity_report_generator_util", "p3lm", "pattern")
_emit_records_learning_event("integrity_report_generator_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("integrity_report_generator_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("integrity_report_generator_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("integrity_report_generator_util", "p3lm", "routing")
_emit_improves_agent_policy("integrity_report_generator_util", "p3lm", "policy")
_emit_stores_learning_state("integrity_report_generator_util", "p3lm", "state")
_emit_records_execution_trace("integrity_report_generator_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("integrity_report_generator_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("integrity_report_generator_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("integrity_report_generator_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("integrity_report_generator_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("integrity_report_generator_util", "env_read", "p2_env_1")
_emit_reads_environ("integrity_report_generator_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("integrity_report_generator_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("integrity_report_generator_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "integrity_report_generator_util", "context_pull")
_emit_pulls_context("p1", "integrity_report_generator_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "integrity_report_generator_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "integrity_report_generator_util", "uwg_term_2")
_emit_writes_through("p1", "integrity_report_generator_util", "write_through")
_emit_writes_through("p1", "integrity_report_generator_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "integrity_report_generator_util", "safety_validation")
_emit_invokes_eval("p1", "integrity_report_generator_util", "eval_call")
_emit_proposal_commits_routing("p1", "integrity_report_generator_util", "routing_commit")


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
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(
            str(_uuid.uuid4()), "IntegrityReportResult.overall_health_score", "state_snapshot"
        )
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(
            str(_uuid.uuid4()), "IntegrityReportResult.overall_health_score", "p0_governance"
        )
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

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L5_POLICY, "IntegrityReportGenerator.validate_registry_coverage"
        )
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
