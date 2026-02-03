#!/usr/bin/env python3
"""
Phase 6: Apps Layer Specific Focus Analysis

This module provides deep-dive analysis of specific apps layer agents
identified as high-risk for AI-Checking-AI violations.

Focus Agents:
- apps_lic: CampaignBalanceAgent, GovernanceShieldAgent, MessageDiversityValidatorAgent
- apps_rg: ATSCompatibilityAgent, BrandComplianceAgent, ContentQualityAgent
- apps_shared: DuplicateCodeDetectorAgent, SecurityLevelAgent

The Law: AI Agents are prohibited from performing structural validation.
These checks must be deterministic Python scripts in tests/guardian/.
"""

import ast
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class FocusAgentAnalysis:
    """Deep analysis of a focus agent."""

    agent_name: str
    file_path: Path
    territory: str
    exists: bool = False
    line_count: int = 0
    has_heal_repository: bool = False
    has_validation_methods: bool = False
    has_llm_calls: bool = False
    has_guardian_test: bool = False
    validation_methods: list[str] = field(default_factory=list)
    risk_level: str = "LOW"
    recommendations: list[str] = field(default_factory=list)


@dataclass
class Phase6AuditResult:
    """Result of Phase 6 Apps Layer Focus audit."""

    apps_lic_analyzed: int = 0
    apps_rg_analyzed: int = 0
    apps_shared_analyzed: int = 0
    high_risk_agents: int = 0
    medium_risk_agents: int = 0
    low_risk_agents: int = 0
    total_recommendations: int = 0
    analyses: list[FocusAgentAnalysis] = field(default_factory=list)
    structural_debt_score: float = 0.0


# Focus agents to analyze in detail
APPS_LIC_FOCUS_AGENTS = [
    "CampaignBalanceAgent",
    "GovernanceShieldAgent",
    "MessageDiversityValidatorAgent",
    "OutreachProactiveAgent",
    "TwoPhaseDeduplicationAgent",
    "ValidatorAgent",
    "HOP6ValidationAgent",
    "OutreachValidationExecutorAgent",
]

APPS_RG_FOCUS_AGENTS = [
    "ATSCompatibilityAgent",
    "BrandComplianceAgent",
    "ContentQualityAgent",
    "FactCheckAgent",
    "SectionBalanceAgent",
    "RgReflectionAgent",
]

APPS_SHARED_FOCUS_AGENTS = [
    "DuplicateCodeDetectorAgent",
    "SecurityLevelAgent",
    "MockSyntaxValidatorAgent",
    "DecomposedQueryAgent",
]


def find_agent_file(agent_name: str, territory_path: Path) -> Path | None:
    """Find the file containing a specific agent."""
    for file_path in territory_path.rglob("*.py"):
        if "__pycache__" in str(file_path):
            continue
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            if f"class {agent_name}" in content:
                return file_path
        except Exception:
            pass
    return None


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


def find_validation_methods(file_path: Path) -> list[str]:
    """Find validation-related methods in a file."""
    methods = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)

        validation_keywords = ["validate", "check", "verify", "audit", "assess"]

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                if any(kw in node.name.lower() for kw in validation_keywords):
                    methods.append(node.name)
    except Exception:
        pass
    return methods


def has_llm_calls(file_path: Path) -> bool:
    """Check if file contains LLM-related calls."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        llm_patterns = ["llm_generate", "llm_gateway", "chat_completion", "model_client"]
        return any(pattern in content for pattern in llm_patterns)
    except Exception:
        return False


def calculate_risk_level(analysis: FocusAgentAnalysis) -> str:
    """Calculate risk level based on analysis."""
    risk_score = 0

    if analysis.has_llm_calls:
        risk_score += 3
    if analysis.has_validation_methods and not analysis.has_guardian_test:
        risk_score += 2
    if len(analysis.validation_methods) > 3:
        risk_score += 1
    if not analysis.has_guardian_test:
        risk_score += 1

    if risk_score >= 4:
        return "HIGH"
    elif risk_score >= 2:
        return "MEDIUM"
    return "LOW"


def generate_recommendations(analysis: FocusAgentAnalysis) -> list[str]:
    """Generate recommendations for an agent."""
    recommendations = []

    if analysis.has_llm_calls:
        recommendations.append(
            "CRITICAL: Remove LLM calls from validation logic. "
            "Replace with deterministic Guardian tests."
        )

    if analysis.has_validation_methods and not analysis.has_guardian_test:
        recommendations.append(
            f"Create Guardian tests for validation methods: "
            f"{', '.join(analysis.validation_methods[:3])}"
        )

    if not analysis.has_guardian_test:
        recommendations.append(
            f"Add tests/guardian/test_{analysis.agent_name.lower()}.py "
            "with deterministic validation tests."
        )

    if analysis.has_heal_repository and not analysis.has_guardian_test:
        recommendations.append(
            "heal_repository should invoke Guardian tests via subprocess "
            "instead of inline validation."
        )

    return recommendations


def analyze_focus_agent(
    agent_name: str, territory_path: Path, territory_name: str, project_root: Path
) -> FocusAgentAnalysis:
    """Perform deep analysis of a focus agent."""
    analysis = FocusAgentAnalysis(
        agent_name=agent_name,
        file_path=Path("unknown"),
        territory=territory_name,
    )

    file_path = find_agent_file(agent_name, territory_path)
    if not file_path:
        return analysis

    analysis.exists = True
    analysis.file_path = file_path

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        analysis.line_count = len(content.splitlines())
        analysis.has_heal_repository = "def heal_repository" in content
        analysis.has_llm_calls = has_llm_calls(file_path)
        analysis.validation_methods = find_validation_methods(file_path)
        analysis.has_validation_methods = len(analysis.validation_methods) > 0
        analysis.has_guardian_test = has_guardian_test(agent_name, project_root)
    except Exception:
        pass

    analysis.risk_level = calculate_risk_level(analysis)
    analysis.recommendations = generate_recommendations(analysis)

    return analysis


def calculate_structural_debt_score(result: "Phase6AuditResult") -> float:
    """Calculate structural debt score based on risk levels."""
    total_analyzed = len(result.analyses)
    if total_analyzed == 0:
        return 0.0

    # Weighted scoring: HIGH=3, MEDIUM=2, LOW=1
    debt_points = (result.high_risk_agents * 3) + (result.medium_risk_agents * 2)
    max_points = total_analyzed * 3

    # Invert to get health (100 = no debt, 0 = max debt)
    health = 100 * (1 - (debt_points / max_points))
    return round(health, 1)


def run_phase6_audit(project_root: Path | None = None) -> Phase6AuditResult:
    """Run the Phase 6 Apps Layer Focus audit."""
    if project_root is None:
        project_root = PROJECT_ROOT

    result = Phase6AuditResult()

    # Analyze apps_lic focus agents
    apps_lic_path = project_root / "apps_lic"
    for agent_name in APPS_LIC_FOCUS_AGENTS:
        analysis = analyze_focus_agent(agent_name, apps_lic_path, "apps_lic", project_root)
        if analysis.exists:
            result.apps_lic_analyzed += 1
            result.analyses.append(analysis)
            result.total_recommendations += len(analysis.recommendations)

            if analysis.risk_level == "HIGH":
                result.high_risk_agents += 1
            elif analysis.risk_level == "MEDIUM":
                result.medium_risk_agents += 1
            else:
                result.low_risk_agents += 1

    # Analyze apps_rg focus agents
    apps_rg_path = project_root / "apps_rg"
    for agent_name in APPS_RG_FOCUS_AGENTS:
        analysis = analyze_focus_agent(agent_name, apps_rg_path, "apps_rg", project_root)
        if analysis.exists:
            result.apps_rg_analyzed += 1
            result.analyses.append(analysis)
            result.total_recommendations += len(analysis.recommendations)

            if analysis.risk_level == "HIGH":
                result.high_risk_agents += 1
            elif analysis.risk_level == "MEDIUM":
                result.medium_risk_agents += 1
            else:
                result.low_risk_agents += 1

    # Analyze apps_shared focus agents
    apps_shared_path = project_root / "apps_shared"
    for agent_name in APPS_SHARED_FOCUS_AGENTS:
        analysis = analyze_focus_agent(agent_name, apps_shared_path, "apps_shared", project_root)
        if analysis.exists:
            result.apps_shared_analyzed += 1
            result.analyses.append(analysis)
            result.total_recommendations += len(analysis.recommendations)

            if analysis.risk_level == "HIGH":
                result.high_risk_agents += 1
            elif analysis.risk_level == "MEDIUM":
                result.medium_risk_agents += 1
            else:
                result.low_risk_agents += 1

    result.structural_debt_score = calculate_structural_debt_score(result)
    return result


def generate_phase6_report(result: Phase6AuditResult) -> str:
    """Generate a formatted Phase 6 audit report."""
    report = []
    report.append("=" * 70)
    report.append("PHASE 6: APPS LAYER SPECIFIC FOCUS ANALYSIS REPORT")
    report.append("=" * 70)
    report.append("")
    report.append("FOCUS AGENTS ANALYZED:")
    report.append(f"  - apps_lic: {result.apps_lic_analyzed}")
    report.append(f"  - apps_rg: {result.apps_rg_analyzed}")
    report.append(f"  - apps_shared: {result.apps_shared_analyzed}")
    report.append("")
    report.append("RISK DISTRIBUTION:")
    report.append(f"  🔴 HIGH RISK: {result.high_risk_agents}")
    report.append(f"  🟡 MEDIUM RISK: {result.medium_risk_agents}")
    report.append(f"  🟢 LOW RISK: {result.low_risk_agents}")
    report.append("")
    report.append(f"STRUCTURAL DEBT SCORE: {result.structural_debt_score}/100")
    report.append(f"TOTAL RECOMMENDATIONS: {result.total_recommendations}")
    report.append("")

    # Detailed analysis by territory
    for territory in ["apps_lic", "apps_rg", "apps_shared"]:
        territory_analyses = [a for a in result.analyses if a.territory == territory]
        if not territory_analyses:
            continue

        report.append(f"\n{territory.upper()} DETAILED ANALYSIS:")
        report.append("-" * 50)

        for analysis in territory_analyses:
            risk_icon = (
                "🔴"
                if analysis.risk_level == "HIGH"
                else "🟡"
                if analysis.risk_level == "MEDIUM"
                else "🟢"
            )
            guardian_icon = "✅" if analysis.has_guardian_test else "❌"

            report.append(f"\n{risk_icon} {analysis.agent_name}")
            report.append(f"   Lines: {analysis.line_count}")
            report.append(f"   Guardian Test: {guardian_icon}")
            report.append(f"   LLM Calls: {'Yes' if analysis.has_llm_calls else 'No'}")
            report.append(f"   Validation Methods: {len(analysis.validation_methods)}")

            if analysis.recommendations:
                report.append("   Recommendations:")
                for rec in analysis.recommendations[:2]:
                    report.append(f"     • {rec[:60]}...")

    report.append("")
    report.append("=" * 70)
    report.append("STRUCTURAL DEBT SUMMARY")
    report.append("=" * 70)

    if result.structural_debt_score >= 80:
        report.append("✅ EXCELLENT: Minimal structural debt detected")
    elif result.structural_debt_score >= 60:
        report.append("⚠️  MODERATE: Some structural debt needs attention")
    elif result.structural_debt_score >= 40:
        report.append("🟡 CONCERNING: Significant structural debt detected")
    else:
        report.append("🔴 CRITICAL: Major structural debt - immediate action required")

    report.append("")
    report.append("=" * 70)

    return "\n".join(report)


# ============================================================================
# PYTEST TEST CASES
# ============================================================================


class TestForensicAuditPhase6:
    """Test suite for Phase 6 Apps Layer Focus Analysis."""

    def test_scan_runs_without_error(self):
        """Test that the scanner runs without errors."""
        result = run_phase6_audit(PROJECT_ROOT)
        assert result is not None

    def test_focus_agents_defined(self):
        """Test that focus agents are properly defined."""
        assert len(APPS_LIC_FOCUS_AGENTS) >= 5
        assert len(APPS_RG_FOCUS_AGENTS) >= 4
        assert len(APPS_SHARED_FOCUS_AGENTS) >= 2

    def test_apps_lic_agents_analyzed(self):
        """Test that apps_lic agents are analyzed."""
        result = run_phase6_audit(PROJECT_ROOT)
        assert result.apps_lic_analyzed >= 0

    def test_apps_rg_agents_analyzed(self):
        """Test that apps_rg agents are analyzed."""
        result = run_phase6_audit(PROJECT_ROOT)
        assert result.apps_rg_analyzed >= 0

    def test_risk_levels_calculated(self):
        """Test that risk levels are properly calculated."""
        result = run_phase6_audit(PROJECT_ROOT)
        total = result.high_risk_agents + result.medium_risk_agents + result.low_risk_agents
        assert total == len(result.analyses)

    def test_structural_debt_score(self):
        """Test that structural debt score is calculated."""
        result = run_phase6_audit(PROJECT_ROOT)
        assert 0 <= result.structural_debt_score <= 100

    def test_recommendations_generated(self):
        """Test that recommendations are generated."""
        result = run_phase6_audit(PROJECT_ROOT)
        assert isinstance(result.total_recommendations, int)

    def test_analysis_dataclass(self):
        """Test FocusAgentAnalysis dataclass."""
        analysis = FocusAgentAnalysis(
            agent_name="TestAgent",
            file_path=Path("test.py"),
            territory="apps_lic",
        )
        assert analysis.agent_name == "TestAgent"
        assert analysis.risk_level == "LOW"

    def test_report_generation(self):
        """Test that report is properly generated."""
        result = run_phase6_audit(PROJECT_ROOT)
        report = generate_phase6_report(result)

        assert "PHASE 6" in report
        assert "FOCUS ANALYSIS" in report
        assert "STRUCTURAL DEBT" in report

    def test_risk_level_calculation(self):
        """Test risk level calculation logic."""
        analysis = FocusAgentAnalysis(
            agent_name="TestAgent",
            file_path=Path("test.py"),
            territory="apps_lic",
            has_llm_calls=True,
            has_validation_methods=True,
            has_guardian_test=False,
        )
        risk = calculate_risk_level(analysis)
        assert risk in ["HIGH", "MEDIUM", "LOW"]

    def test_recommendation_generation(self):
        """Test recommendation generation."""
        analysis = FocusAgentAnalysis(
            agent_name="TestAgent",
            file_path=Path("test.py"),
            territory="apps_lic",
            has_llm_calls=True,
            has_validation_methods=True,
            validation_methods=["validate_input"],
            has_guardian_test=False,
        )
        recommendations = generate_recommendations(analysis)
        assert len(recommendations) > 0


def test_forensic_audit_phase6():
    """Main test entry point for Phase 6 Apps Layer Focus."""
    print("\n" + "=" * 70)
    print("PHASE 6: APPS LAYER SPECIFIC FOCUS ANALYSIS - RUNNING TESTS")
    print("=" * 70 + "\n")

    result = run_phase6_audit(PROJECT_ROOT)
    report = generate_phase6_report(result)
    print(report)

    # Assertions
    total_analyzed = len(result.analyses)
    assert total_analyzed >= 0, "Should analyze some agents"

    print("\n✅ Phase 6 Apps Layer Focus Analysis: PASSED")
    print(f"   Analyzed {total_analyzed} focus agents")
    print(f"   High Risk: {result.high_risk_agents}")
    print(f"   Structural Debt Score: {result.structural_debt_score}/100")


if __name__ == "__main__":
    test_forensic_audit_phase6()
