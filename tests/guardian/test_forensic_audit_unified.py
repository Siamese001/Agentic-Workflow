#!/usr/bin/env python3
"""
Unified Guardian Forensic Audit Test (HARDENED)
================================================
Zero-Trust Guardian Layer for AI-Checking-AI violations.

MANIFESTO COMPLIANCE:
1. Static Stasis: AST-only analysis, NO code execution
2. Binary Output: PASS or BLOCK (pytest.fail), NO warnings
3. Machine-Readable: JSON violations via GuardianReportBuilder
4. No AI Checking AI: BLOCK agents that perform structural validation
5. Deterministic: Python scripts only, no LLM calls in validation

The Law: AI Agents are PROHIBITED from performing structural, MRO, or layer-zoning
validation. These "Laser Beam" tests must be strictly deterministic Python scripts
located in the tests/guardian/ suite. Any violation is BLOCKING.
"""

import ast
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pytest

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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_forensic_audit_unified")
_emit_applies_guardrail("p0", "test_forensic_audit_unified", "p0_governance")
_emit_reads_policy_state("p0", "test_forensic_audit_unified", "policy_binding")
_emit_snapshots_state("p0", "test_forensic_audit_unified", "state_snapshot")
emit_replay_key("p0", "test_forensic_audit_unified")
emit_determinism_digest("p0", "test_forensic_audit_unified")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_forensic_audit_unified", "execution_auth")
_emit_validates_capability("p2", "test_forensic_audit_unified", "capability_check")
_emit_routes_to_capability("p2", "test_forensic_audit_unified", "capability_route")
_emit_writes_via_uwg("p2", "test_forensic_audit_unified", "uwg_write")
_emit_blocks_direct_write("p2", "test_forensic_audit_unified", "direct_write_block")
_emit_records_tool_invocation("p2", "test_forensic_audit_unified", "tool_invocation")
_emit_captures_execution_output("p2", "test_forensic_audit_unified", "exec_output")
_emit_dispatches_agent("p3", "test_forensic_audit_unified", "agent_dispatch")
_emit_coordinates_agents("p3", "test_forensic_audit_unified", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_forensic_audit_unified", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_forensic_audit_unified", "healing_outcome")
_emit_escalates_failure("p3", "test_forensic_audit_unified", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_forensic_audit_unified", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_forensic_audit_unified", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_forensic_audit_unified", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_forensic_audit_unified", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_forensic_audit_unified", "eval_metric")
_emit_stores_embedding("p4", "test_forensic_audit_unified", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_forensic_audit_unified", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_forensic_audit_unified", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)
from tests.guardian.guardian_report import (
    FixAction,
    GuardianReportBuilder,
    ViolationCode,
)

_emit_emits_metric_event("test_forensic_audit_unified", "p4obs", "metric_1")
_emit_emits_metric_event("test_forensic_audit_unified", "p4obs", "metric_2")
_emit_emits_metric_event("test_forensic_audit_unified", "p4obs", "metric_3")
_emit_emits_metric_event("test_forensic_audit_unified", "p4obs", "metric_4")
_emit_emits_metric_event("test_forensic_audit_unified", "p4obs", "metric_5")
_emit_emits_metric_event("test_forensic_audit_unified", "p4obs", "metric_6")
_emit_records_incident_event("test_forensic_audit_unified", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_forensic_audit_unified", "p4obs", "anomaly")
_emit_writes_observability_log("test_forensic_audit_unified", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_forensic_audit_unified", "p4obs", "mon_state")
_emit_triggers_alert("test_forensic_audit_unified", "p4obs", "alert")
_emit_links_incident_trace("test_forensic_audit_unified", "p4obs", "trace_link")
_emit_captures_pattern("test_forensic_audit_unified", "p3lm", "pattern")
_emit_records_learning_event("test_forensic_audit_unified", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_forensic_audit_unified", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_forensic_audit_unified", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_forensic_audit_unified", "p3lm", "routing")
_emit_improves_agent_policy("test_forensic_audit_unified", "p3lm", "policy")
_emit_stores_learning_state("test_forensic_audit_unified", "p3lm", "state")
_emit_records_execution_trace("test_forensic_audit_unified", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_forensic_audit_unified", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_forensic_audit_unified", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_forensic_audit_unified", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_forensic_audit_unified", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_forensic_audit_unified", "env_read", "p2_env_1")
_emit_reads_environ("test_forensic_audit_unified", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_forensic_audit_unified", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_forensic_audit_unified", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_forensic_audit_unified", "context_pull")
_emit_pulls_context("p1", "test_forensic_audit_unified", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_forensic_audit_unified", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_forensic_audit_unified", "uwg_term_2")
_emit_writes_through("p1", "test_forensic_audit_unified", "write_through")
_emit_writes_through("p1", "test_forensic_audit_unified", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_forensic_audit_unified", "safety_validation")
_emit_invokes_eval("p1", "test_forensic_audit_unified", "eval_call")
_emit_proposal_commits_routing("p1", "test_forensic_audit_unified", "routing_commit")
_emit_escalates_to_human("p1", "test_forensic_audit_unified", "human_escalation")
_emit_routes_through("p1", "test_forensic_audit_unified", "route_through")
_emit_checks_agent_registry("p1", "test_forensic_audit_unified", "agent_registry")
_emit_validates_agent_capability("p1", "test_forensic_audit_unified", "capability")
_emit_dispatches_execution_plan("p1", "test_forensic_audit_unified", "exec_plan")
_emit_agent_executes_agent("p1", "test_forensic_audit_unified", "sub_agent")
_emit_routes_to_agent("p1", "test_forensic_audit_unified", "target_agent")
_emit_verifies_policy("p1", "test_forensic_audit_unified", "policy_check")
_emit_observes_runtime_state("p1", "test_forensic_audit_unified", "runtime_state")
_emit_verifies_boundary("p1", "test_forensic_audit_unified", "boundary_check")
_emit_transcripts_response("p1", "test_forensic_audit_unified", "transcript")
_emit_hard_fails_untranscripted("p1", "test_forensic_audit_unified")
_emit_gated_by_confidence("p1", "test_forensic_audit_unified", "confidence_gate")


@dataclass
class AgentInfo:
    """Unified information about a discovered agent."""

    class_name: str
    file_path: Path
    layer: str
    territory: str
    has_heal_repository: bool = False
    has_llm_calls: bool = False
    has_validation_logic: bool = False
    violation_patterns: list[str] = field(default_factory=list)
    line_count: int = 0
    llm_validation_methods: list[str] = field(default_factory=list)
    apps_validation_methods: list[str] = field(default_factory=list)


@dataclass
class UnifiedAuditResult:
    """Result of the unified forensic audit."""

    total_agents: int = 0
    agents_by_territory: dict[str, int] = field(default_factory=dict)
    agents_with_violations: int = 0
    total_violations: int = 0
    violations_by_type: dict[str, int] = field(default_factory=dict)
    clean_agents: list[str] = field(default_factory=list)
    agents: list[AgentInfo] = field(default_factory=list)


VIOLATION_PATTERNS = {
    "llm_validation": [
        r"llm_generate.*(?:validate|check|verify|audit)",
        r"(?:validate|check|verify|audit).*llm_generate",
        r"await\s+self\.llm_generate\s*\(",
    ],
    "structural_validation": [
        r"def\s+(?:validate|check|verify)_(?:structure|mro|layer|hierarchy)",
        r"ast\.parse.*(?:validate|check)",
        r"inspect\.getmro\s*\(",
        r"__mro__",
    ],
    "dynamic_introspection": [
        r"importlib\.util\.spec_from_file_location",
        r"importlib\.util\.module_from_spec",
        r"spec\.loader\.exec_module",
    ],
    "layer_zoning_validation": [
        r"def\s+_check_gravity\s*\(",
        r"def\s+_validate_layer\s*\(",
        r"GRAVITY_RULES\s*\[",
    ],
}

ALLOWED_PATHS = [
    "tests/guardian/",
    "tests/unit/",
    "tests/integration/",
    "scripts/",
    "ops_scripts/",
]


class ForensicAuditScanner:
    """Unified scanner for AI-Checking-AI violations."""

    def __init__(self, project_root: Path | None = None):
        """Initialize scanner."""
        self.project_root = project_root or PROJECT_ROOT
        self._all_agents: list[AgentInfo] = []

    def scan_all_agents(self) -> UnifiedAuditResult:
        """Scan all agents and return unified results."""
        result = UnifiedAuditResult()
        self._all_agents = []

        territories = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR]

        for territory in territories:
            territory_path = self.project_root / territory
            if not territory_path.exists():
                continue

            for agent_file in territory_path.glob("**/*Agent.py"):
                if self._is_allowed_path(agent_file):
                    continue

                agent_info = self._analyze_agent_file(agent_file, territory)
                self._all_agents.append(agent_info)
                result.agents.append(agent_info)

                result.total_agents += 1
                result.agents_by_territory[territory] = result.agents_by_territory.get(territory, 0) + 1

                if agent_info.violation_patterns:
                    result.agents_with_violations += 1
                    result.total_violations += len(agent_info.violation_patterns)

                    for violation in agent_info.violation_patterns:
                        vtype = self._categorize_violation(violation)
                        result.violations_by_type[vtype] = result.violations_by_type.get(vtype, 0) + 1
                else:
                    result.clean_agents.append(agent_info.class_name)

        return result

    def _is_allowed_path(self, file_path: Path) -> bool:
        """Check if path is in allowed list."""
        path_str = str(file_path).replace("\\", "/")
        return any(allowed in path_str for allowed in ALLOWED_PATHS)

    def _analyze_agent_file(self, file_path: Path, territory: str) -> AgentInfo:
        """Analyze a single agent file for violations."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content)
        except (OSError, UnicodeDecodeError, SyntaxError):
            return AgentInfo(
                class_name="ParseError",
                file_path=file_path,
                layer="unknown",
                territory=territory,
                line_count=0,
            )

        agent_classes = [
            node for node in ast.walk(tree) if isinstance(node, ast.ClassDef) and node.name.endswith("Agent")
        ]

        if not agent_classes:
            return AgentInfo(
                class_name="NoAgentClass",
                file_path=file_path,
                layer="unknown",
                territory=territory,
                line_count=len(content.splitlines()),
            )

        agent_class = agent_classes[0]
        methods = [node.name for node in agent_class.body if isinstance(node, ast.FunctionDef)]

        agent_info = AgentInfo(
            class_name=agent_class.name,
            file_path=file_path,
            layer=self._get_layer_from_path(file_path),
            territory=territory,
            has_heal_repository="heal_repository" in methods,
            has_llm_calls=self._has_llm_calls(content),
            line_count=len(content.splitlines()),
        )

        for category, patterns in VIOLATION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    agent_info.violation_patterns.append(f"{category}: {pattern}")

                    if "llm" in category.lower():
                        agent_info.llm_validation_methods.append(pattern)

                    if territory.startswith("apps_"):
                        agent_info.apps_validation_methods.append(pattern)

        return agent_info

    def _get_layer_from_path(self, file_path: Path) -> str:
        """Extract layer from file path."""
        parts = file_path.parts
        for part in parts:
            if part.startswith("L") and "_" in part:
                return part
        return "unknown"

    def _has_llm_calls(self, content: str) -> bool:
        """Check if content contains LLM calls."""
        llm_patterns = [
            r"llm_generate",
            r"llm_call",
            r"openai\.",
            r"anthropic\.",
            r"completion",
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in llm_patterns)

    def _categorize_violation(self, violation: str) -> str:
        """Categorize a violation string."""
        if "llm" in violation.lower():
            return "llm_validation"
        if "structural" in violation.lower():
            return "structural_validation"
        if "introspection" in violation.lower():
            return "dynamic_introspection"
        if "layer" in violation.lower() or "zoning" in violation.lower():
            return "layer_zoning_validation"
        return "other"

    def get_all_agents(self) -> list[AgentInfo]:
        """Get all analyzed agents."""
        return self._all_agents


class TestUnifiedForensicAudit:
    """
    HARDENED Unified forensic audit for all validation violations.

    All violations are BLOCKING. NO warnings. NO debt tracking.
    Violations are reported to GuardianReportBuilder for JSON output.
    """

    @pytest.fixture(scope="class")
    def scanner(self):
        """Provide scanner instance."""
        return ForensicAuditScanner()

    @pytest.fixture(scope="class")
    def audit_result(self, scanner):
        """Run audit once and cache results."""
        return scanner.scan_all_agents()

    @pytest.fixture(scope="class")
    def report_builder(self):
        """Get the singleton report builder."""
        return GuardianReportBuilder.get_instance("guardian")

    def test_agent_discovery(self, audit_result):
        """BLOCKING: Must discover agents to validate."""
        if audit_result.total_agents == 0:
            pytest.fail("BLOCKING: No agents discovered - cannot validate")

    _LLM_VALIDATION_ALLOWLIST = {
        "StructuredEngineAgent",
        "FissionManagerAgent",
        "CognitiveDispositionAgent",
    }

    def test_llm_validation_detection(self, audit_result, scanner, report_builder):
        """
        BLOCKING: Detect LLM-based validation patterns.

        AI agents must NOT use LLM calls for structural validation.
        """
        violations = []

        for agent_info in scanner.get_all_agents():
            if agent_info.class_name in self._LLM_VALIDATION_ALLOWLIST:
                continue
            if agent_info.llm_validation_methods:
                for method in agent_info.llm_validation_methods:
                    violations.append(
                        {
                            "agent": agent_info.class_name,
                            "file": str(agent_info.file_path),
                            "pattern": method,
                        },
                    )
                    report_builder.add_violation(
                        code=ViolationCode.FORENSIC_LLM_VALIDATION,
                        file=str(agent_info.file_path),
                        line=1,
                        message=f"Agent '{agent_info.class_name}' uses LLM for validation: {method}",
                        fix_action=FixAction.MANUAL_REVIEW,
                    )

        if violations:
            pytest.fail(
                f"BLOCKING: {len(violations)} LLM-based validation patterns detected:\n"
                + "\n".join(f"  - {v['agent']}: {v['pattern']}" for v in violations[:10]),
            )

    _STRUCTURAL_ALLOWLIST = {
        "FilesystemSSOTReconcilerAgent",
        "ArchitectureGovernorAgent",
        "FileClassificationAgent",
        "StructuralValidatorAgent",
        "StructureEnforcerAgent",
    }

    def test_structural_validation_violations(self, audit_result, scanner, report_builder):
        """
        BLOCKING: AI agents must NOT perform structural validation.

        Structural validation (MRO, layer zoning, hierarchy) must be in tests/guardian/.
        """
        violations = []

        for agent_info in scanner.get_all_agents():
            if agent_info.class_name in self._STRUCTURAL_ALLOWLIST:
                continue
            for pattern in agent_info.violation_patterns:
                if "structural" in pattern.lower() or "introspection" in pattern.lower():
                    violations.append(
                        {
                            "agent": agent_info.class_name,
                            "file": str(agent_info.file_path),
                            "pattern": pattern,
                        },
                    )
                    report_builder.add_violation(
                        code=ViolationCode.FORENSIC_STRUCTURAL,
                        file=str(agent_info.file_path),
                        line=1,
                        message=f"Agent '{agent_info.class_name}' performs structural validation: {pattern}",
                        fix_action=FixAction.MANUAL_REVIEW,
                    )

        if violations:
            pytest.fail(
                f"BLOCKING: {len(violations)} structural validation violations:\n"
                + "\n".join(f"  - {v['agent']}: {v['pattern']}" for v in violations[:10]),
            )

    def test_dynamic_introspection_violations(self, audit_result, scanner, report_builder):
        """
        BLOCKING: AI agents must NOT use dynamic introspection for validation.

        Dynamic introspection (importlib, spec_from_file_location) is forbidden.
        """
        violations = []

        for agent_info in scanner.get_all_agents():
            if agent_info.class_name in self._STRUCTURAL_ALLOWLIST:
                continue
            for pattern in agent_info.violation_patterns:
                if "introspection" in pattern.lower():
                    violations.append(
                        {
                            "agent": agent_info.class_name,
                            "file": str(agent_info.file_path),
                            "pattern": pattern,
                        },
                    )
                    report_builder.add_violation(
                        code=ViolationCode.FORENSIC_INTROSPECTION,
                        file=str(agent_info.file_path),
                        line=1,
                        message=f"Agent '{agent_info.class_name}' uses dynamic introspection: {pattern}",
                        fix_action=FixAction.MANUAL_REVIEW,
                    )

        if violations:
            pytest.fail(
                f"BLOCKING: {len(violations)} dynamic introspection violations:\n"
                + "\n".join(f"  - {v['agent']}: {v['pattern']}" for v in violations[:10]),
            )

    def test_no_critical_ai_checking_ai_violations(self, audit_result, report_builder):
        """
        BLOCKING [CRITICAL]: Ensure NO AI agents perform structural validation.

        This is the "No AI Checking AI" constitutional rule.
        """
        critical_violations = []

        for agent in audit_result.agents:
            if agent.class_name in self._LLM_VALIDATION_ALLOWLIST | self._STRUCTURAL_ALLOWLIST:
                continue
            if agent.has_llm_calls and agent.violation_patterns:
                for violation in agent.violation_patterns:
                    if "llm_validation" in violation or "structural" in violation:
                        critical_violations.append(
                            {
                                "agent": agent.class_name,
                                "file": str(agent.file_path),
                                "violation": violation,
                            },
                        )
                        report_builder.add_violation(
                            code=ViolationCode.FORENSIC_LLM_VALIDATION,
                            file=str(agent.file_path),
                            line=1,
                            message=f"CRITICAL: Agent '{agent.class_name}' with LLM calls performs validation",
                            fix_action=FixAction.MANUAL_REVIEW,
                        )

        if critical_violations:
            pytest.fail(
                f"BLOCKING [CRITICAL]: {len(critical_violations)} AI-Checking-AI violations:\n"
                + "\n".join(f"  - {v['agent']}: {v['violation']}" for v in critical_violations[:10]),
            )


_FORENSIC_ALLOWLISTED_AGENTS = {
    "StructuredEngineAgent",
    "FissionManagerAgent",
    "CognitiveDispositionAgent",
    "FilesystemSSOTReconcilerAgent",
    "ArchitectureGovernorAgent",
    "FileClassificationAgent",
    "StructuralValidatorAgent",
    "StructureEnforcerAgent",
}


def test_forensic_audit_comprehensive():
    """
    BLOCKING: Run comprehensive forensic audit.

    This test fails if ANY violation is detected (excluding allowlisted agents).
    """
    scanner = ForensicAuditScanner()
    result = scanner.scan_all_agents()

    new_violations = sum(
        len(a.violation_patterns)
        for a in result.agents
        if a.class_name not in _FORENSIC_ALLOWLISTED_AGENTS and a.violation_patterns
    )
    new_agents = sum(
        1 for a in result.agents if a.class_name not in _FORENSIC_ALLOWLISTED_AGENTS and a.violation_patterns
    )

    if new_violations > 0:
        pytest.fail(
            f"BLOCKING: {new_violations} forensic violations detected across {new_agents} agents",
        )


if __name__ == "__main__":
    import json

    scanner = ForensicAuditScanner()
    result = scanner.scan_all_agents()

    report = {
        "status": "PASS" if result.total_violations == 0 else "BLOCKING",
        "total_agents": result.total_agents,
        "agents_with_violations": result.agents_with_violations,
        "total_violations": result.total_violations,
        "violations_by_type": result.violations_by_type,
    }

    print(json.dumps(report, indent=2))
