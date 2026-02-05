#!/usr/bin/env python3
"""
Phase 3: Apps Layer Validation Logic Detection

This module provides deterministic detection of validation logic in apps layer
agents (apps_lic, apps_rg, apps_shared) that may constitute AI-Checking-AI
violations.

Key Focus Areas:
- apps_lic engines: 40+ agents with heal_repository methods
- apps_rg engines: 18+ agents with validation logic
- GovernanceShieldAgent: Risk scanning validation
- ContentQualityAgent: Quality validation without Guardian tests

The Law: AI Agents are prohibited from performing structural validation.
These checks must be deterministic Python scripts in tests/guardian/.
"""

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class AppsLayerViolation:
    """A detected apps layer validation violation."""

    agent_name: str
    file_path: Path
    territory: str  # apps_lic, apps_rg, apps_shared
    method_name: str
    line_number: int
    violation_type: str
    description: str
    has_guardian_test: bool = False
    severity: str = "HIGH"


@dataclass
class Phase3AuditResult:
    """Result of Phase 3 Apps Layer audit."""

    total_apps_agents: int = 0
    apps_lic_count: int = 0
    apps_rg_count: int = 0
    apps_shared_count: int = 0
    agents_with_validation: int = 0
    agents_with_heal_repository: int = 0
    total_violations: int = 0
    violations: list[AppsLayerViolation] = field(default_factory=list)
    compliant_agents: list[str] = field(default_factory=list)


# Apps layer validation patterns
APPS_VALIDATION_PATTERNS = {
    "inline_validation": {
        "patterns": [
            r"def\s+(?:validate|check|verify)_\w+\s*\(",
            r"if\s+not\s+(?:self\.)?(?:validate|check|verify)",
            r"(?:validation|check)_result\s*=",
        ],
        "description": "Inline validation logic that should be in Guardian tests",
        "severity": "HIGH",
    },
    "quality_scoring": {
        "patterns": [
            r"(?:quality|compliance)_score\s*[=<>]",
            r"calculate_(?:score|quality|compliance)",
            r"score\s*(?:>=|<=|>|<)\s*(?:threshold|min|max)",
        ],
        "description": "Quality/compliance scoring logic embedded in agent",
        "severity": "MEDIUM",
    },
    "content_validation": {
        "patterns": [
            r"def\s+_validate_content\s*\(",
            r"content_(?:valid|check|verify)",
            r"validate_(?:text|content|input)",
        ],
        "description": "Content validation that should be deterministic",
        "severity": "HIGH",
    },
    "heal_without_guardian": {
        "patterns": [
            r"def\s+heal_repository\s*\([^)]*\)\s*:\s*\n\s*.*?return\s+super\(\)\.heal_repository",
        ],
        "description": "heal_repository delegates to super() without Guardian test link",
        "severity": "MEDIUM",
    },
    "risk_assessment": {
        "patterns": [
            r"(?:risk|threat)_(?:level|score|assessment)",
            r"assess_(?:risk|threat|compliance)",
            r"scan_risk_level",
        ],
        "description": "Risk assessment logic that should be deterministic",
        "severity": "HIGH",
    },
}

# Known apps layer agents to audit
APPS_LIC_FOCUS = [
    "CampaignBalanceAgent",
    "GovernanceShieldAgent",
    "MessageDiversityValidator",
    "OutreachProactiveAgent",
    "TwoPhaseDeduplicationAgent",
    "ValidatorAgent",
]

APPS_RG_FOCUS = [
    "ATSCompatibilityAgent",
    "BrandComplianceAgent",
    "ContentQualityAgent",
    "FactCheckAgent",
]

APPS_SHARED_FOCUS = [
    "DuplicateCodeDetectorAgent",
    "SecurityLevelAgent",
]


def extract_territory(file_path: Path) -> str:
    """Extract territory from file path."""
    path_str = str(file_path).replace("\\", "/")
    if "apps_lic" in path_str:
        return "apps_lic"
    if "apps_rg" in path_str:
        return "apps_rg"
    if "apps_shared" in path_str:
        return "apps_shared"
    return "unknown"


def has_guardian_test(agent_name: str, project_root: Path) -> bool:
    """Check if agent has a corresponding Guardian test."""
    guardian_dir = project_root / "tests" / "guardian"
    if not guardian_dir.exists():
        return False

    # Look for test files that reference this agent
    for test_file in guardian_dir.glob("*.py"):
        try:
            content = test_file.read_text(encoding="utf-8", errors="ignore")
            if agent_name in content:
                return True
        except Exception:
            pass

    return False


def has_heal_repository(file_path: Path) -> bool:
    """Check if file contains heal_repository method."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        return "def heal_repository" in content
    except Exception:
        return False


def find_validation_methods(file_path: Path) -> list[tuple[str, int]]:
    """Find validation-related methods in a file."""
    methods = []

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)

        validation_keywords = ["validate", "check", "verify", "audit", "assess"]

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                if any(kw in node.name.lower() for kw in validation_keywords):
                    methods.append((node.name, node.lineno))

    except Exception:
        pass

    return methods


def scan_apps_agent(file_path: Path, project_root: Path) -> list[AppsLayerViolation]:
    """Scan an apps layer agent for validation violations."""
    violations = []
    territory = extract_territory(file_path)

    if territory == "unknown":
        return []

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        # Extract agent class name
        agent_name = "Unknown"
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                    agent_name = node.name
                    break
        except Exception:
            pass

        has_guardian = has_guardian_test(agent_name, project_root)

        # Check for validation patterns
        for pattern_name, pattern_info in APPS_VALIDATION_PATTERNS.items():
            for pattern in pattern_info["patterns"]:
                matches = list(re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE))
                for match in matches:
                    line_number = content[: match.start()].count("\n") + 1

                    # Find method context
                    method_name = "unknown"
                    try:
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                                end_line = node.end_lineno or node.lineno + 100
                                if node.lineno <= line_number <= end_line:
                                    method_name = node.name
                                    break
                    except Exception:
                        pass

                    violations.append(
                        AppsLayerViolation(
                            agent_name=agent_name,
                            file_path=file_path,
                            territory=territory,
                            method_name=method_name,
                            line_number=line_number,
                            violation_type=pattern_name,
                            description=pattern_info["description"],
                            has_guardian_test=has_guardian,
                            severity=pattern_info["severity"],
                        )
                    )

        # Check validation methods without Guardian tests
        if not has_guardian:
            validation_methods = find_validation_methods(file_path)
            for method_name, line_num in validation_methods:
                # Avoid duplicates
                already_recorded = any(
                    v.line_number == line_num and v.file_path == file_path for v in violations
                )
                if not already_recorded:
                    violations.append(
                        AppsLayerViolation(
                            agent_name=agent_name,
                            file_path=file_path,
                            territory=territory,
                            method_name=method_name,
                            line_number=line_num,
                            violation_type="validation_method_no_guardian",
                            description=f"Validation method '{method_name}' without Guardian test",
                            has_guardian_test=False,
                            severity="MEDIUM",
                        )
                    )

    except Exception:
        pass

    return violations


def run_phase3_audit(project_root: Path | None = None) -> Phase3AuditResult:
    """Run the Phase 3 Apps Layer Validation audit."""
    if project_root is None:
        project_root = PROJECT_ROOT

    result = Phase3AuditResult()

    apps_territories = {
        "apps_lic": project_root / "apps_lic",
        "apps_rg": project_root / "apps_rg",
        "apps_shared": project_root / "apps_shared",
    }

    for territory_name, territory_path in apps_territories.items():
        if not territory_path.exists():
            continue

        for file_path in territory_path.rglob("*Agent.py"):
            if "__pycache__" in str(file_path):
                continue

            result.total_apps_agents += 1

            if territory_name == "apps_lic":
                result.apps_lic_count += 1
            elif territory_name == "apps_rg":
                result.apps_rg_count += 1
            elif territory_name == "apps_shared":
                result.apps_shared_count += 1

            if has_heal_repository(file_path):
                result.agents_with_heal_repository += 1

            violations = scan_apps_agent(file_path, project_root)

            if violations:
                result.agents_with_validation += 1
                result.violations.extend(violations)
            else:
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                            result.compliant_agents.append(node.name)
                            break
                except Exception:
                    pass

    result.total_violations = len(result.violations)
    return result


def generate_phase3_report(result: Phase3AuditResult) -> str:
    """Generate a formatted Phase 3 audit report."""
    report = []
    report.append("=" * 70)
    report.append("PHASE 3: APPS LAYER VALIDATION LOGIC DETECTION REPORT")
    report.append("=" * 70)
    report.append("")
    report.append(f"Total Apps Layer Agents: {result.total_apps_agents}")
    report.append(f"  - apps_lic: {result.apps_lic_count}")
    report.append(f"  - apps_rg: {result.apps_rg_count}")
    report.append(f"  - apps_shared: {result.apps_shared_count}")
    report.append("")
    report.append(f"Agents with heal_repository: {result.agents_with_heal_repository}")
    report.append(f"Agents with Validation Logic: {result.agents_with_validation}")
    report.append(f"Total Violations Found: {result.total_violations}")
    report.append("")

    if result.violations:
        report.append("VIOLATIONS BY TERRITORY:")
        report.append("-" * 50)

        # Group by territory
        by_territory: dict[str, list[AppsLayerViolation]] = {}
        for v in result.violations:
            if v.territory not in by_territory:
                by_territory[v.territory] = []
            by_territory[v.territory].append(v)

        for territory, violations in sorted(by_territory.items()):
            report.append(f"\n📁 {territory.upper()} ({len(violations)} violations)")

            # Group by agent within territory
            by_agent: dict[str, list[AppsLayerViolation]] = {}
            for v in violations:
                if v.agent_name not in by_agent:
                    by_agent[v.agent_name] = []
                by_agent[v.agent_name].append(v)

            for agent_name, agent_violations in by_agent.items():
                guardian_status = "✅" if agent_violations[0].has_guardian_test else "❌"
                report.append(f"   {guardian_status} {agent_name}")
                for v in agent_violations[:3]:  # Limit to first 3
                    sev_icon = "🔴" if v.severity == "HIGH" else "🟡"
                    report.append(f"      {sev_icon} Line {v.line_number}: {v.violation_type}")

        report.append("")

    # Focus agents check
    report.append("FOCUS AGENTS STATUS:")
    report.append("-" * 50)
    detected_agents = {v.agent_name for v in result.violations}

    report.append("  apps_lic:")
    for agent in APPS_LIC_FOCUS:
        status = "⚠️ VIOLATIONS" if agent in detected_agents else "✅ CLEAN"
        report.append(f"    - {agent}: {status}")

    report.append("  apps_rg:")
    for agent in APPS_RG_FOCUS:
        status = "⚠️ VIOLATIONS" if agent in detected_agents else "✅ CLEAN"
        report.append(f"    - {agent}: {status}")

    report.append("")
    report.append("=" * 70)

    return "\n".join(report)


# ============================================================================
# PYTEST TEST CASES
# ============================================================================


class TestForensicAuditPhase3:
    """Test suite for Phase 3 Apps Layer Validation Detection."""

    def test_scan_runs_without_error(self):
        """Test that the scanner runs without errors."""
        result = run_phase3_audit(PROJECT_ROOT)
        assert result is not None

    def test_apps_lic_discovered(self):
        """Test that apps_lic agents are discovered."""
        result = run_phase3_audit(PROJECT_ROOT)
        assert result.apps_lic_count >= 20, f"Expected 20+ apps_lic agents, got {result.apps_lic_count}"

    def test_apps_rg_discovered(self):
        """Test that apps_rg agents are discovered."""
        result = run_phase3_audit(PROJECT_ROOT)
        assert result.apps_rg_count >= 10, f"Expected 10+ apps_rg agents, got {result.apps_rg_count}"

    def test_apps_shared_discovered(self):
        """Test that apps_shared agents are discovered."""
        result = run_phase3_audit(PROJECT_ROOT)
        assert result.apps_shared_count >= 3, (
            f"Expected 3+ apps_shared agents, got {result.apps_shared_count}"
        )

    def test_territory_extraction(self):
        """Test territory extraction from file paths."""
        test_cases = [
            (Path("apps_lic/engines/TestAgent.py"), "apps_lic"),
            (Path("apps_rg/engines/TestAgent.py"), "apps_rg"),
            (Path("apps_shared/utils/TestAgent.py"), "apps_shared"),
            (Path("agentic_core/L5_safety/TestAgent.py"), "unknown"),
        ]
        for path, expected in test_cases:
            assert extract_territory(path) == expected

    def test_heal_repository_detection(self):
        """Test that heal_repository methods are detected."""
        result = run_phase3_audit(PROJECT_ROOT)
        assert result.agents_with_heal_repository > 0

    def test_violation_dataclass(self):
        """Test AppsLayerViolation dataclass."""
        violation = AppsLayerViolation(
            agent_name="TestAgent",
            file_path=Path("test.py"),
            territory="apps_lic",
            method_name="test_method",
            line_number=10,
            violation_type="inline_validation",
            description="Test description",
        )
        assert violation.agent_name == "TestAgent"
        assert violation.severity == "HIGH"
        assert violation.has_guardian_test is False

    def test_report_generation(self):
        """Test that report is properly generated."""
        result = run_phase3_audit(PROJECT_ROOT)
        report = generate_phase3_report(result)

        assert "PHASE 3" in report
        assert "APPS LAYER" in report
        assert "apps_lic" in report
        assert "apps_rg" in report

    def test_focus_agents_defined(self):
        """Test that focus agents are properly defined."""
        assert len(APPS_LIC_FOCUS) >= 5
        assert len(APPS_RG_FOCUS) >= 4
        assert "CampaignBalanceAgent" in APPS_LIC_FOCUS
        assert "ATSCompatibilityAgent" in APPS_RG_FOCUS

    def test_validation_patterns_defined(self):
        """Test that validation patterns are properly defined."""
        assert len(APPS_VALIDATION_PATTERNS) > 0
        for name, info in APPS_VALIDATION_PATTERNS.items():
            assert "patterns" in info
            assert "description" in info
            assert "severity" in info

    def test_compliant_agents_tracked(self):
        """Test that compliant agents are tracked."""
        result = run_phase3_audit(PROJECT_ROOT)
        # Some agents should be compliant
        assert isinstance(result.compliant_agents, list)

    def test_no_agentic_core_scanned(self):
        """Test that agentic_core is not scanned in Phase 3."""
        result = run_phase3_audit(PROJECT_ROOT)

        for v in result.violations:
            assert "agentic_core" not in str(v.file_path)


def test_forensic_audit_phase3():
    """Main test entry point for Phase 3 Apps Layer Detection."""
    print("\n" + "=" * 70)
    print("PHASE 3: APPS LAYER VALIDATION LOGIC DETECTION - RUNNING TESTS")
    print("=" * 70 + "\n")

    result = run_phase3_audit(PROJECT_ROOT)
    report = generate_phase3_report(result)
    print(report)

    # Assertions
    assert result.total_apps_agents >= 30, f"Expected 30+ apps agents, found {result.total_apps_agents}"

    print("\n✅ Phase 3 Apps Layer Detection: PASSED")
    print(f"   Scanned {result.total_apps_agents} apps layer agents")
    print(f"   Found {result.agents_with_validation} agents with validation logic")
    print(f"   Total violations: {result.total_violations}")


if __name__ == "__main__":
    test_forensic_audit_phase3()
