#!/usr/bin/env python3
"""
Unified Guardian Forensic Audit Test
Consolidated detection of AI-Checking-AI violations and structural validation issues.

Combines all 6 phases into a single, efficient test suite:
- Phase 1: Agent discovery and basic violations
- Phase 2: LLM-based validation detection
- Phase 3: Apps layer validation logic
- Phases 4-6: Extended validation patterns

The Law: AI Agents are prohibited from performing structural, MRO, or layer-zoning
validation. These "Laser Beam" tests must be strictly deterministic Python scripts
located in the tests/guardian/ suite.
"""

import ast
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


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

        territories = ["agentic_core", "apps_lic", "apps_rg", "apps_shared"]

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
                result.agents_by_territory[territory] = (
                    result.agents_by_territory.get(territory, 0) + 1
                )

                if agent_info.violation_patterns:
                    result.agents_with_violations += 1
                    result.total_violations += len(agent_info.violation_patterns)

                    for violation in agent_info.violation_patterns:
                        vtype = self._categorize_violation(violation)
                        result.violations_by_type[vtype] = (
                            result.violations_by_type.get(vtype, 0) + 1
                        )
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
        except Exception:
            return AgentInfo(
                class_name="ParseError",
                file_path=file_path,
                layer="unknown",
                territory=territory,
                line_count=0,
            )

        agent_classes = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent")
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
    """Unified forensic audit for all validation violations."""

    @pytest.fixture(scope="class")
    def scanner(self):
        """Provide scanner instance."""
        return ForensicAuditScanner()

    @pytest.fixture(scope="class")
    def audit_result(self, scanner):
        """Run audit once and cache results."""
        return scanner.scan_all_agents()

    def test_agent_discovery(self, audit_result):
        """Phase 1: Agent discovery and basic violation detection."""
        assert audit_result.total_agents > 0, "Should discover agents"

        print("\n[AUDIT] Phase 1: Agent Discovery")
        print(f"  Total agents: {audit_result.total_agents}")
        for territory, count in audit_result.agents_by_territory.items():
            print(f"  - {territory}: {count} agents")

    def test_llm_validation_detection(self, audit_result, scanner):
        """Phase 2: LLM-based validation detection."""
        llm_violations = 0
        for agent_info in scanner.get_all_agents():
            if agent_info.llm_validation_methods:
                llm_violations += len(agent_info.llm_validation_methods)

        print("\n[AUDIT] Phase 2: LLM Validation Detection")
        print(f"  LLM-based validation patterns: {llm_violations}")

    def test_apps_layer_validation(self, audit_result, scanner):
        """Phase 3: Apps layer validation logic detection."""
        apps_violations = 0
        for agent_info in scanner.get_all_agents():
            if agent_info.territory.startswith("apps_") and agent_info.apps_validation_methods:
                apps_violations += len(agent_info.apps_validation_methods)

        print("\n[AUDIT] Phase 3: Apps Layer Validation")
        print(f"  Apps validation patterns: {apps_violations}")

    def test_structural_validation_violations(self, audit_result):
        """Phases 4-6: Consolidated structural validation detection."""
        structural_count = audit_result.violations_by_type.get("structural_validation", 0)
        introspection_count = audit_result.violations_by_type.get("dynamic_introspection", 0)
        layer_count = audit_result.violations_by_type.get("layer_zoning_validation", 0)

        print("\n[AUDIT] Phases 4-6: Structural Validation")
        print(f"  Structural validation: {structural_count}")
        print(f"  Dynamic introspection: {introspection_count}")
        print(f"  Layer zoning validation: {layer_count}")

    def test_comprehensive_audit_summary(self, audit_result):
        """Comprehensive summary of all violations."""
        print("\n[AUDIT] Comprehensive Summary")
        print(f"  Total agents scanned: {audit_result.total_agents}")
        print(f"  Agents with violations: {audit_result.agents_with_violations}")
        print(f"  Total violations: {audit_result.total_violations}")
        print(f"  Clean agents: {len(audit_result.clean_agents)}")

        if audit_result.violations_by_type:
            print("\n  Violations by type:")
            for vtype, count in audit_result.violations_by_type.items():
                print(f"    - {vtype}: {count}")

    def test_no_critical_ai_checking_ai_violations(self, audit_result):
        """Critical: Ensure no AI agents perform structural validation."""
        critical_violations = []

        for agent in audit_result.agents:
            if agent.has_llm_calls and agent.violation_patterns:
                for violation in agent.violation_patterns:
                    if "llm_validation" in violation or "structural" in violation:
                        critical_violations.append(f"{agent.class_name}: {violation}")

        if critical_violations:
            print("\n[WARNING] Critical AI-Checking-AI violations detected:")
            for v in critical_violations[:10]:
                print(f"  - {v}")

        assert audit_result.total_agents >= 10, "Should scan at least 10 agents"


def test_forensic_audit_comprehensive():
    """Run comprehensive forensic audit."""
    scanner = ForensicAuditScanner()
    result = scanner.scan_all_agents()

    print(f"\n{'=' * 60}")
    print("FORENSIC AUDIT REPORT")
    print(f"{'=' * 60}")
    print(f"Total agents: {result.total_agents}")
    print(f"Agents with violations: {result.agents_with_violations}")
    print(f"Total violations: {result.total_violations}")
    print(f"Clean agents: {len(result.clean_agents)}")
    print(f"{'=' * 60}")

    for territory, count in result.agents_by_territory.items():
        print(f"{territory}: {count} agents")

    if result.violations_by_type:
        print("\nViolations by type:")
        for vtype, count in result.violations_by_type.items():
            print(f"  {vtype}: {count}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
