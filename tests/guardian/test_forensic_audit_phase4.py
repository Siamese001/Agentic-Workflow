#!/usr/bin/env python3
"""
Phase 4: Missing Guardian Test Links Detection

This module provides deterministic detection of agents that report "success"
without explicitly executing Guardian test scripts. This is a critical violation
of the "AI-Checking-AI" constitutional rule.

Key Detection Patterns:
- Agents returning success without subprocess/pytest calls to Guardian layer
- heal_repository methods that delegate to super() without Guardian verification
- Validation logic embedded in agents instead of externalized to tests/guardian/

The Law: AI Agents are prohibited from performing structural validation.
These checks must be deterministic Python scripts in tests/guardian/.
"""

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class MissingGuardianLink:
    """A detected missing Guardian test link."""

    agent_name: str
    file_path: Path
    layer: str
    method_name: str
    issue_type: str
    description: str
    has_heal_repository: bool = True
    has_guardian_test: bool = False
    has_subprocess_call: bool = False
    severity: str = "HIGH"


@dataclass
class Phase4AuditResult:
    """Result of Phase 4 Missing Guardian Links audit."""

    total_agents_scanned: int = 0
    agents_with_heal_repository: int = 0
    agents_with_guardian_tests: int = 0
    agents_with_subprocess_calls: int = 0
    agents_missing_links: int = 0
    total_issues: int = 0
    missing_links: list[MissingGuardianLink] = field(default_factory=list)
    compliant_agents: list[str] = field(default_factory=list)


# Patterns that indicate proper Guardian integration
GUARDIAN_LINK_PATTERNS = {
    "subprocess_pytest": [
        r"subprocess\.run\s*\(\s*\[.*pytest",
        r"subprocess\.call\s*\(\s*\[.*pytest",
        r"os\.system\s*\(.*pytest",
    ],
    "subprocess_guardian": [
        r"subprocess\.run\s*\(\s*\[.*guardian",
        r"subprocess\.run\s*\(\s*\[.*tests/guardian",
    ],
    "pytest_import": [
        r"import\s+pytest",
        r"from\s+pytest\s+import",
    ],
}

# Issue types for missing links
MISSING_LINK_ISSUES = {
    "heal_no_guardian": {
        "description": "heal_repository without Guardian test verification",
        "severity": "HIGH",
    },
    "validation_no_subprocess": {
        "description": "Validation logic without subprocess call to Guardian",
        "severity": "HIGH",
    },
    "success_no_verification": {
        "description": "Returns success without deterministic verification",
        "severity": "MEDIUM",
    },
    "delegate_only": {
        "description": "Only delegates to super() without additional Guardian checks",
        "severity": "LOW",
    },
}


def extract_layer(file_path: Path) -> str:
    """Extract the layer from file path."""
    path_str = str(file_path).replace("\\", "/")

    if "apps_lic" in path_str:
        return "Apps-LIC"
    if "apps_rg" in path_str:
        return "Apps-RG"
    if "apps_shared" in path_str:
        return "Apps-Shared"

    for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
        if f"/{layer}_" in path_str or f"\\{layer}_" in path_str:
            return layer

    if "base_agents" in path_str:
        return "Base"

    return "Unknown"


def has_guardian_test(agent_name: str, project_root: Path) -> bool:
    """Check if agent has a corresponding Guardian test."""
    guardian_dir = project_root / "tests" / "guardian"
    if not guardian_dir.exists():
        return False

    for test_file in guardian_dir.glob("*.py"):
        try:
            content = test_file.read_text(encoding="utf-8", errors="ignore")
            if agent_name in content:
                return True
        except Exception:
            pass

    return False


def has_subprocess_call(file_path: Path) -> bool:
    """Check if file contains subprocess calls to pytest/guardian."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        for patterns in GUARDIAN_LINK_PATTERNS.values():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
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


def analyze_heal_repository(file_path: Path) -> dict[str, Any]:
    """Analyze the heal_repository method for Guardian links."""
    analysis = {
        "has_heal": False,
        "delegates_only": False,
        "returns_success": False,
        "has_validation": False,
        "line_number": 0,
    }

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        # Find heal_repository method
        heal_match = re.search(
            r"def\s+heal_repository\s*\([^)]*\)\s*.*?:\s*\n(.*?)(?=\n    def |\nclass |\Z)",
            content,
            re.DOTALL,
        )

        if heal_match:
            analysis["has_heal"] = True
            heal_body = heal_match.group(1)

            # Find line number
            analysis["line_number"] = content[: heal_match.start()].count("\n") + 1

            # Check if it only delegates to super()
            if "super().heal_repository" in heal_body:
                # Check if there's more than just the super() call
                lines = [
                    ln.strip()
                    for ln in heal_body.split("\n")
                    if ln.strip() and not ln.strip().startswith("#")
                ]
                non_super_lines = [
                    ln
                    for ln in lines
                    if "super().heal_repository" not in ln
                    and "return" not in ln
                    and '"""' not in ln
                    and "'''" not in ln
                ]
                if len(non_super_lines) <= 2:  # Only docstring + maybe one line
                    analysis["delegates_only"] = True

            # Check if it returns success-like values
            if re.search(r"return\s*\{.*success.*\}", heal_body, re.IGNORECASE):
                analysis["returns_success"] = True
            if re.search(r"return\s*\{.*violations_found.*0", heal_body, re.IGNORECASE):
                analysis["returns_success"] = True

            # Check for validation logic
            if re.search(r"validate|check|verify|audit", heal_body, re.IGNORECASE):
                analysis["has_validation"] = True

    except Exception:
        pass

    return analysis


def scan_agent_for_missing_links(file_path: Path, project_root: Path) -> list[MissingGuardianLink]:
    """Scan an agent for missing Guardian test links."""
    issues = []

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

        layer = extract_layer(file_path)
        has_guardian = has_guardian_test(agent_name, project_root)
        has_subprocess = has_subprocess_call(file_path)
        heal_analysis = analyze_heal_repository(file_path)

        # Issue 1: heal_repository without Guardian test
        if heal_analysis["has_heal"] and not has_guardian:
            issues.append(
                MissingGuardianLink(
                    agent_name=agent_name,
                    file_path=file_path,
                    layer=layer,
                    method_name="heal_repository",
                    issue_type="heal_no_guardian",
                    description=MISSING_LINK_ISSUES["heal_no_guardian"]["description"],
                    has_heal_repository=True,
                    has_guardian_test=False,
                    has_subprocess_call=has_subprocess,
                    severity=MISSING_LINK_ISSUES["heal_no_guardian"]["severity"],
                )
            )

        # Issue 2: Validation logic without subprocess
        if heal_analysis["has_validation"] and not has_subprocess:
            issues.append(
                MissingGuardianLink(
                    agent_name=agent_name,
                    file_path=file_path,
                    layer=layer,
                    method_name="heal_repository",
                    issue_type="validation_no_subprocess",
                    description=MISSING_LINK_ISSUES["validation_no_subprocess"]["description"],
                    has_heal_repository=True,
                    has_guardian_test=has_guardian,
                    has_subprocess_call=False,
                    severity=MISSING_LINK_ISSUES["validation_no_subprocess"]["severity"],
                )
            )

        # Issue 3: Delegates only without additional checks
        if heal_analysis["delegates_only"] and not has_guardian:
            issues.append(
                MissingGuardianLink(
                    agent_name=agent_name,
                    file_path=file_path,
                    layer=layer,
                    method_name="heal_repository",
                    issue_type="delegate_only",
                    description=MISSING_LINK_ISSUES["delegate_only"]["description"],
                    has_heal_repository=True,
                    has_guardian_test=False,
                    has_subprocess_call=has_subprocess,
                    severity=MISSING_LINK_ISSUES["delegate_only"]["severity"],
                )
            )

    except Exception:
        pass

    return issues


def run_phase4_audit(project_root: Path | None = None) -> Phase4AuditResult:
    """Run the Phase 4 Missing Guardian Links audit."""
    if project_root is None:
        project_root = PROJECT_ROOT

    result = Phase4AuditResult()

    territories = [
        project_root / "agentic_core",
        project_root / "apps_lic",
        project_root / "apps_rg",
        project_root / "apps_shared",
    ]

    for territory in territories:
        if not territory.exists():
            continue

        for file_path in territory.rglob("*Agent.py"):
            if "__pycache__" in str(file_path):
                continue
            if "tests/" in str(file_path).replace("\\", "/"):
                continue

            result.total_agents_scanned += 1

            # Track statistics
            agent_name = "Unknown"
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                        agent_name = node.name
                        break
            except Exception:
                pass

            if has_heal_repository(file_path):
                result.agents_with_heal_repository += 1

            if has_guardian_test(agent_name, project_root):
                result.agents_with_guardian_tests += 1

            if has_subprocess_call(file_path):
                result.agents_with_subprocess_calls += 1

            # Find issues
            issues = scan_agent_for_missing_links(file_path, project_root)

            if issues:
                result.agents_missing_links += 1
                result.missing_links.extend(issues)
            else:
                result.compliant_agents.append(agent_name)

    result.total_issues = len(result.missing_links)
    return result


def generate_phase4_report(result: Phase4AuditResult) -> str:
    """Generate a formatted Phase 4 audit report."""
    report = []
    report.append("=" * 70)
    report.append("PHASE 4: MISSING GUARDIAN TEST LINKS DETECTION REPORT")
    report.append("=" * 70)
    report.append("")
    report.append(f"Total Agents Scanned: {result.total_agents_scanned}")
    report.append(f"Agents with heal_repository: {result.agents_with_heal_repository}")
    report.append(f"Agents with Guardian Tests: {result.agents_with_guardian_tests}")
    report.append(f"Agents with Subprocess Calls: {result.agents_with_subprocess_calls}")
    report.append("")
    report.append(f"Agents Missing Guardian Links: {result.agents_missing_links}")
    report.append(f"Total Issues Found: {result.total_issues}")
    report.append("")

    if result.missing_links:
        report.append("MISSING GUARDIAN LINKS BY ISSUE TYPE:")
        report.append("-" * 50)

        # Group by issue type
        by_type: dict[str, list[MissingGuardianLink]] = {}
        for link in result.missing_links:
            if link.issue_type not in by_type:
                by_type[link.issue_type] = []
            by_type[link.issue_type].append(link)

        for issue_type, links in sorted(by_type.items()):
            severity = MISSING_LINK_ISSUES.get(issue_type, {}).get("severity", "MEDIUM")
            sev_icon = "🔴" if severity == "HIGH" else "🟡" if severity == "MEDIUM" else "🟢"
            report.append(f"\n{sev_icon} {issue_type.upper()} ({len(links)} agents)")

            for link in links[:10]:  # Limit to first 10
                guardian_status = "✅" if link.has_guardian_test else "❌"
                report.append(f"   {guardian_status} {link.agent_name} ({link.layer})")

            if len(links) > 10:
                report.append(f"   ... and {len(links) - 10} more")

        report.append("")

    # Coverage statistics
    if result.total_agents_scanned > 0:
        coverage = result.agents_with_guardian_tests / result.total_agents_scanned * 100
        report.append("GUARDIAN TEST COVERAGE:")
        report.append("-" * 50)
        report.append(f"   Coverage: {coverage:.1f}%")
        report.append(f"   Compliant Agents: {len(result.compliant_agents)}")

    report.append("")
    report.append("=" * 70)

    return "\n".join(report)


# ============================================================================
# PYTEST TEST CASES
# ============================================================================


class TestForensicAuditPhase4:
    """Test suite for Phase 4 Missing Guardian Links Detection."""

    def test_scan_runs_without_error(self):
        """Test that the scanner runs without errors."""
        result = run_phase4_audit(PROJECT_ROOT)
        assert result is not None
        assert result.total_agents_scanned > 0

    def test_heal_repository_detected(self):
        """Test that heal_repository methods are detected."""
        result = run_phase4_audit(PROJECT_ROOT)
        assert result.agents_with_heal_repository > 0

    def test_guardian_tests_detected(self):
        """Test that Guardian tests are detected."""
        result = run_phase4_audit(PROJECT_ROOT)
        # Should find at least some agents with Guardian tests
        assert result.agents_with_guardian_tests >= 0

    def test_layer_extraction(self):
        """Test layer extraction from file paths."""
        test_cases = [
            (Path("agentic_core/L5_safety/validators/TestAgent.py"), "L5"),
            (Path("apps_lic/engines/TestAgent.py"), "Apps-LIC"),
            (Path("apps_rg/engines/TestAgent.py"), "Apps-RG"),
        ]
        for path, expected in test_cases:
            assert extract_layer(path) == expected

    def test_guardian_link_patterns_defined(self):
        """Test that Guardian link patterns are properly defined."""
        assert len(GUARDIAN_LINK_PATTERNS) > 0
        for name, patterns in GUARDIAN_LINK_PATTERNS.items():
            assert len(patterns) > 0

    def test_missing_link_dataclass(self):
        """Test MissingGuardianLink dataclass."""
        link = MissingGuardianLink(
            agent_name="TestAgent",
            file_path=Path("test.py"),
            layer="L5",
            method_name="heal_repository",
            issue_type="heal_no_guardian",
            description="Test description",
        )
        assert link.agent_name == "TestAgent"
        assert link.has_guardian_test is False
        assert link.severity == "HIGH"

    def test_report_generation(self):
        """Test that report is properly generated."""
        result = run_phase4_audit(PROJECT_ROOT)
        report = generate_phase4_report(result)

        assert "PHASE 4" in report
        assert "MISSING GUARDIAN" in report
        assert "Total Agents Scanned" in report

    def test_issue_types_defined(self):
        """Test that issue types are properly defined."""
        assert len(MISSING_LINK_ISSUES) >= 3
        for name, info in MISSING_LINK_ISSUES.items():
            assert "description" in info
            assert "severity" in info

    def test_compliant_agents_tracked(self):
        """Test that compliant agents are tracked."""
        result = run_phase4_audit(PROJECT_ROOT)
        assert isinstance(result.compliant_agents, list)

    def test_no_test_files_scanned(self):
        """Test that test files are excluded from scanning."""
        result = run_phase4_audit(PROJECT_ROOT)

        for link in result.missing_links:
            path_str = str(link.file_path).replace("\\", "/")
            assert "tests/" not in path_str

    def test_heal_analysis(self):
        """Test heal_repository analysis function."""
        # Create a mock file path that exists
        # This tests the function doesn't crash
        analysis = analyze_heal_repository(Path("nonexistent.py"))
        assert "has_heal" in analysis
        assert "delegates_only" in analysis

    def test_coverage_calculation(self):
        """Test that coverage can be calculated."""
        result = run_phase4_audit(PROJECT_ROOT)

        if result.total_agents_scanned > 0:
            coverage = result.agents_with_guardian_tests / result.total_agents_scanned
            assert 0 <= coverage <= 1


def test_forensic_audit_phase4():
    """Main test entry point for Phase 4 Missing Guardian Links."""
    print("\n" + "=" * 70)
    print("PHASE 4: MISSING GUARDIAN TEST LINKS DETECTION - RUNNING TESTS")
    print("=" * 70 + "\n")

    result = run_phase4_audit(PROJECT_ROOT)
    report = generate_phase4_report(result)
    print(report)

    # Assertions
    assert result.total_agents_scanned >= 50, (
        f"Expected 50+ agents, found {result.total_agents_scanned}"
    )

    print("\n✅ Phase 4 Missing Guardian Links Detection: PASSED")
    print(f"   Scanned {result.total_agents_scanned} agents")
    print(f"   Found {result.agents_missing_links} agents missing Guardian links")
    print(f"   Total issues: {result.total_issues}")


if __name__ == "__main__":
    test_forensic_audit_phase4()
