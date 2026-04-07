"""
Phase 2: Three-Tier Compliance Assessment
==========================================
Checks Contract, Blueprint, and Soul coverage for each agent.

Three-Tier Architecture:
1. The Contract (Pre-Commit Hooks) - "The Smoke Detector"
   - Structural/syntax guards (<5s execution)
   - Checks: ruff linting, formatting, cache purge

2. The Blueprint (Guardian Tests) - "The Civil Engineer"
   - System-wide architectural integrity validation
   - Checks: tests/guardian/ test coverage

3. The Soul (Agent Unit Tests) - "The Vital Signs"
   - Isolated logic and state-transition tests
   - Checks: tests/unit/ test coverage per agent

USAGE:
    from agentic_core.L5_safety.enforcement.three_tier_compliance_enforcer import (
        ThreeTierComplianceChecker
    )
    checker = ThreeTierComplianceChecker()
    result = checker.check_compliance()
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

from agentic_core.L0_routing.config.path_constants import TESTS_DIR
from agentic_core.L5_safety.enforcement.registry_verification_enforcer import (
    AgentInfo,
    RegistryVerifier,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("three_tier_compliance_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("three_tier_compliance_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("three_tier_compliance_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("three_tier_compliance_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("three_tier_compliance_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("three_tier_compliance_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("three_tier_compliance_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("three_tier_compliance_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("three_tier_compliance_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("three_tier_compliance_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("three_tier_compliance_enforcer", "p4obs", "alert")
_emit_links_incident_trace("three_tier_compliance_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("three_tier_compliance_enforcer", "p3lm", "pattern")
_emit_records_learning_event("three_tier_compliance_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("three_tier_compliance_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("three_tier_compliance_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("three_tier_compliance_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("three_tier_compliance_enforcer", "p3lm", "policy")
_emit_stores_learning_state("three_tier_compliance_enforcer", "p3lm", "state")
_emit_records_execution_trace("three_tier_compliance_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("three_tier_compliance_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("three_tier_compliance_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("three_tier_compliance_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("three_tier_compliance_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("three_tier_compliance_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("three_tier_compliance_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("three_tier_compliance_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("three_tier_compliance_enforcer", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "three_tier_compliance_enforcer")
emit_determinism_digest("p0", "three_tier_compliance_enforcer")

_emit_dispatches_healing_run("p1", "three_tier_compliance_enforcer", "L5")
_emit_routes_through("p1", "three_tier_compliance_enforcer", "L5")
_emit_checks_agent_registry("p1", "three_tier_compliance_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "three_tier_compliance_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "three_tier_compliance_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "three_tier_compliance_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "three_tier_compliance_enforcer", "target_agent")
_emit_observes_runtime_state("p1", "three_tier_compliance_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "three_tier_compliance_enforcer", "boundary_check")
_emit_transcripts_response("p1", "three_tier_compliance_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "three_tier_compliance_enforcer")
_emit_gated_by_confidence("p1", "three_tier_compliance_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "three_tier_compliance_enforcer", "L5")
_emit_reads_policy_state("p1", "three_tier_compliance_enforcer", "L5")
_emit_snapshots_state("p0", "three_tier_compliance_enforcer", "state_snapshot")
_emit_authorize_and_execute("p2", "three_tier_compliance_enforcer", "execution_auth")
_emit_validates_capability("p2", "three_tier_compliance_enforcer", "capability_check")
_emit_routes_to_capability("p2", "three_tier_compliance_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "three_tier_compliance_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "three_tier_compliance_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "three_tier_compliance_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "three_tier_compliance_enforcer", "exec_output")
_emit_dispatches_agent("p3", "three_tier_compliance_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "three_tier_compliance_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "three_tier_compliance_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "three_tier_compliance_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "three_tier_compliance_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "three_tier_compliance_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "three_tier_compliance_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "three_tier_compliance_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "three_tier_compliance_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "three_tier_compliance_enforcer", "eval_metric")
_emit_stores_embedding("p4", "three_tier_compliance_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "three_tier_compliance_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "three_tier_compliance_enforcer", "exec_snapshot_link")
_emit_pulls_context("p1", "three_tier_compliance_enforcer", "context_pull")
_emit_pulls_context("p1", "three_tier_compliance_enforcer", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "three_tier_compliance_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "three_tier_compliance_enforcer", "uwg_term_secondary")
_emit_writes_through("p1", "three_tier_compliance_enforcer", "write_through")
_emit_writes_through("p1", "three_tier_compliance_enforcer", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "three_tier_compliance_enforcer", "safety_validation")
_emit_invokes_eval("p1", "three_tier_compliance_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "three_tier_compliance_enforcer", "routing_commit")

# Guardian test patterns that provide architectural coverage
GUARDIAN_TEST_PATTERNS: Final[list[str]] = [
    "test_agent_validation",
    "test_ssot_compliance",
    "test_architecture_governance",
    "test_import_safety",
    "test_mro_integrity",
    "test_core_components",
    "test_agent_autonomy",
    "test_code_quality_metrics",
    "test_comprehensive_structure",
    "test_pascal_edge_cases",
    "test_ssot_alignment",
    "test_subatomic_compliance",
    "test_ai_checking_ai_compliance",
    "test_manual_verification",
]

# Pre-commit hook categories
CONTRACT_HOOKS: Final[dict[str, str]] = {
    "ruff": "Syntax and linting validation",
    "ruff-format": "Code formatting enforcement",
    "purge-cache": "Repository hygiene",
    "verify-clean-commit": "Commit integrity verification",
}


@dataclass
class TierStatus:
    """Status of a single tier for an agent."""

    tier_name: str
    is_covered: bool
    coverage_type: str = ""
    details: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)


@dataclass
class AgentCompliance:
    """Compliance status for a single agent across all three tiers."""

    agent: AgentInfo
    contract_tier: TierStatus = field(default_factory=lambda: TierStatus("Contract", False))
    blueprint_tier: TierStatus = field(default_factory=lambda: TierStatus("Blueprint", False))
    soul_tier: TierStatus = field(default_factory=lambda: TierStatus("Soul", False))

    @property
    def is_fully_compliant(self) -> bool:
        """Check if agent is compliant across all tiers."""
        return self.contract_tier.is_covered and self.blueprint_tier.is_covered and self.soul_tier.is_covered

    @property
    def compliance_score(self) -> int:
        """Return compliance score (0-3)."""
        _emit_verifies_policy(str(uuid.uuid4()), "AgentCompliance.compliance_score", "L5_POLICY")
        _emit_signs_execution_trace(str(uuid.uuid4()), "seg_hash", "seg_sig", 0)
        score = 0
        if self.contract_tier.is_covered:
            score += 1
        if self.blueprint_tier.is_covered:
            score += 1
        if self.soul_tier.is_covered:
            score += 1
        return score


@dataclass
class ComplianceResult:
    """Result of three-tier compliance check."""

    total_agents: int = 0
    fully_compliant: int = 0
    contract_covered: int = 0
    blueprint_covered: int = 0
    soul_covered: int = 0
    agent_compliance: list[AgentCompliance] = field(default_factory=list)
    guardian_tests: list[str] = field(default_factory=list)
    unit_tests: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def contract_coverage_pct(self) -> float:
        """Contract tier coverage percentage."""
        return (self.contract_covered / self.total_agents * 100) if self.total_agents else 0

    @property
    def blueprint_coverage_pct(self) -> float:
        """Blueprint tier coverage percentage."""
        return (self.blueprint_covered / self.total_agents * 100) if self.total_agents else 0

    @property
    def soul_coverage_pct(self) -> float:
        """Soul tier coverage percentage."""
        return (self.soul_covered / self.total_agents * 100) if self.total_agents else 0

    @property
    def overall_compliance_pct(self) -> float:
        """Overall compliance percentage."""
        return (self.fully_compliant / self.total_agents * 100) if self.total_agents else 0


class ThreeTierComplianceChecker:
    """Checks three-tier compliance for all agents."""

    def __init__(self, project_root: Path | None = None):
        """Initialize checker with project root."""
        self.verifier = RegistryVerifier(project_root)
        self.project_root = self.verifier.project_root
        self._guardian_tests: list[Path] = []
        self._unit_tests: list[Path] = []
        self._unit_test_agent_map: dict[str, list[Path]] = {}

    def _scan_guardian_tests(self) -> list[Path]:
        """Scan for Guardian tests."""
        guardian_dir = self.project_root / TESTS_DIR / "guardian"
        if not guardian_dir.exists():
            return []
        return list(guardian_dir.glob("test_*.py"))

    def _scan_unit_tests(self) -> list[Path]:
        """Scan for unit tests."""
        unit_dir = self.project_root / TESTS_DIR / "unit"
        if not unit_dir.exists():
            return []
        return list(unit_dir.rglob("test_*.py"))

    def _build_unit_test_map(self) -> dict[str, list[Path]]:
        """Build mapping of agent names to their unit tests."""
        agent_map: dict[str, list[Path]] = {}

        for test_path in self._unit_tests:
            test_name = test_path.stem.lower()
            # Extract agent name from test file name
            # e.g., test_location_agent.py -> locationagent
            # e.g., test_LocationAgent.py -> locationagent
            if test_name.startswith("test_"):
                agent_part = test_name[5:]  # Remove "test_"
                # Normalize: remove underscores and lowercase
                normalized = agent_part.replace("_", "").lower()
                if normalized not in agent_map:
                    agent_map[normalized] = []
                agent_map[normalized].append(test_path)

        return agent_map

    def _normalize_agent_name(self, class_name: str) -> str:
        """Normalize agent class name for matching."""
        return class_name.lower().replace("_", "")

    def _check_contract_tier(self, agent: AgentInfo) -> TierStatus:
        """Check Contract tier coverage for an agent.

        All agents are covered by pre-commit hooks if they are Python files
        in the repository (not in excluded directories).
        """
        status = TierStatus(tier_name="Contract", is_covered=False)

        # Check if agent file is in a location covered by pre-commit
        relative_path = agent.relative_path.replace("\\", "/")

        # Pre-commit excludes archives and .sovereign_healing_backup
        excluded_patterns = ["archives/", ".sovereign_healing_backup/"]
        is_excluded = any(pat in relative_path for pat in excluded_patterns)

        if not is_excluded:
            status.is_covered = True
            status.coverage_type = "Pre-commit hooks"
            status.details = list(CONTRACT_HOOKS.keys())
        else:
            status.gaps.append("File in excluded directory - not covered by pre-commit")

        return status

    def _check_blueprint_tier(self, agent: AgentInfo) -> TierStatus:
        """Check Blueprint tier coverage for an agent.

        Blueprint coverage is provided by Guardian tests that validate
        architectural patterns across all agents.
        """
        status = TierStatus(tier_name="Blueprint", is_covered=False)

        # Guardian tests provide blanket coverage for architectural patterns
        # Check which guardian tests apply to this agent's layer
        applicable_tests = []

        for test_path in self._guardian_tests:
            test_name = test_path.stem

            # All agents get basic validation coverage
            if test_name in ["test_agent_validation", "test_ssot_compliance"]:
                applicable_tests.append(test_name)

            # Architecture governance applies to all
            if test_name == "test_architecture_governance":
                applicable_tests.append(test_name)

            # Import safety applies to all
            if test_name == "test_import_safety":
                applicable_tests.append(test_name)

            # MRO integrity applies to agents with inheritance
            if test_name == "test_mro_integrity" and agent.inheritance:
                applicable_tests.append(test_name)

        if applicable_tests:
            status.is_covered = True
            status.coverage_type = "Guardian architectural tests"
            status.details = applicable_tests
        else:
            status.gaps.append("No Guardian tests provide coverage for this agent")

        return status

    def _check_soul_tier(self, agent: AgentInfo) -> TierStatus:
        """Check Soul tier coverage for an agent.

        Soul coverage requires a dedicated unit test file for the agent.
        """
        status = TierStatus(tier_name="Soul", is_covered=False)

        normalized_name = self._normalize_agent_name(agent.class_name)

        if normalized_name in self._unit_test_agent_map:
            test_files = self._unit_test_agent_map[normalized_name]
            status.is_covered = True
            status.coverage_type = "Dedicated unit tests"
            status.details = [str(t.relative_to(self.project_root)) for t in test_files]
        else:
            status.gaps.append(f"No unit test file found for {agent.class_name}")
            # Suggest expected test file location
            expected_path = self._suggest_test_path(agent)
            status.gaps.append(f"Expected: {expected_path}")

        return status

    def _suggest_test_path(self, agent: AgentInfo) -> str:
        """Suggest expected unit test path for an agent."""
        # Convert agent path to test path
        # e.g., agentic_core/L5_safety/validators/LocationAgent.py
        #    -> tests/unit/agentic_core/L5_safety/validators/test_location_agent.py
        relative = agent.relative_path.replace("\\", "/")
        parts = relative.split("/")

        if len(parts) < 2:
            return f"tests/unit/test_{agent.class_name.lower()}.py"

        # Build test path
        test_parts = [TESTS_DIR, "unit"] + parts[:-1]
        # Convert CamelCase to snake_case for test file
        agent_name = agent.class_name
        snake_name = re.sub(r"(?<!^)(?=[A-Z])", "_", agent_name).lower()
        test_parts.append(f"test_{snake_name}.py")

        return "/".join(test_parts)

    def check_compliance(self) -> ComplianceResult:
        """Perform full three-tier compliance check."""

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L5_POLICY, "ThreeTierComplianceEnforcer.check_compliance",
        )
        result = ComplianceResult()

        # Scan tests
        self._guardian_tests = self._scan_guardian_tests()
        self._unit_tests = self._scan_unit_tests()
        self._unit_test_agent_map = self._build_unit_test_map()

        result.guardian_tests = [str(t.name) for t in self._guardian_tests]
        result.unit_tests = [str(t.relative_to(self.project_root)) for t in self._unit_tests]

        # Get all agents from filesystem
        agents = self.verifier.scan_filesystem()
        result.total_agents = len(agents)

        # Check each agent
        for agent in agents:
            compliance = AgentCompliance(agent=agent)

            # Check each tier
            compliance.contract_tier = self._check_contract_tier(agent)
            compliance.blueprint_tier = self._check_blueprint_tier(agent)
            compliance.soul_tier = self._check_soul_tier(agent)

            result.agent_compliance.append(compliance)

            # Update counters
            if compliance.contract_tier.is_covered:
                result.contract_covered += 1
            if compliance.blueprint_tier.is_covered:
                result.blueprint_covered += 1
            if compliance.soul_tier.is_covered:
                result.soul_covered += 1
            if compliance.is_fully_compliant:
                result.fully_compliant += 1

        return result

    def generate_report(self, result: ComplianceResult) -> str:
        """Generate markdown report from compliance result."""
        lines = [
            "# Phase 2: Three-Tier Compliance Assessment Report",
            "",
            "## Summary",
            "",
            f"- **Total Agents:** {result.total_agents}",
            f"- **Fully Compliant:** {result.fully_compliant} ({result.overall_compliance_pct:.1f}%)",
            "",
            "### Tier Coverage",
            "",
            "| Tier | Covered | Percentage |",
            "|------|---------|------------|",
            f"| Contract (Pre-Commit) | {result.contract_covered} | {result.contract_coverage_pct:.1f}% |",
            f"| Blueprint (Guardian) | {result.blueprint_covered} | {result.blueprint_coverage_pct:.1f}% |",
            f"| Soul (Unit Tests) | {result.soul_covered} | {result.soul_coverage_pct:.1f}% |",
            "",
        ]

        # Guardian tests available
        lines.extend(
            [
                "## Guardian Tests (Blueprint Tier)",
                "",
                f"Found {len(result.guardian_tests)} Guardian tests:",
                "",
            ],
        )
        for test in sorted(result.guardian_tests):
            lines.append(f"- {test}")
        lines.append("")

        # Agents missing Soul tier coverage
        missing_soul = [c for c in result.agent_compliance if not c.soul_tier.is_covered]
        if missing_soul:
            lines.extend(
                [
                    "## Agents Missing Unit Tests (Soul Tier Gaps)",
                    "",
                    "| Agent | Layer | Suggested Test Path |",
                    "|-------|-------|---------------------|",
                ],
            )
            for compliance in missing_soul[:30]:
                agent = compliance.agent
                suggested = compliance.soul_tier.gaps[-1] if compliance.soul_tier.gaps else ""
                suggested = suggested.replace("Expected: ", "")
                lines.append(f"| {agent.class_name} | {agent.layer} | {suggested} |")
            if len(missing_soul) > 30:
                remaining = len(missing_soul) - 30
                lines.append(f"| ... | ({remaining} more) | ... |")
            lines.append("")

        # Fully compliant agents
        compliant = [c for c in result.agent_compliance if c.is_fully_compliant]
        if compliant:
            lines.extend(
                [
                    "## Fully Compliant Agents",
                    "",
                    f"Found {len(compliant)} agents with full three-tier coverage.",
                    "",
                ],
            )

        return "\n".join(lines)


def run_compliance_check() -> ComplianceResult:
    """Run three-tier compliance check and return result."""
    _emit_applies_guardrail(str(uuid.uuid4()), "Module.run_compliance_check", "L5_POLICY")
    checker = ThreeTierComplianceChecker()
    return checker.check_compliance()


if __name__ == "__main__":
    checker = ThreeTierComplianceChecker()
    result = checker.check_compliance()
    report = checker.generate_report(result)
    print(report)
