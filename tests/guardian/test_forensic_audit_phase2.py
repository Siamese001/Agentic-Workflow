#!/usr/bin/env python3
"""
Phase 2: LLM-Based Structural Validation Detection

This module provides deterministic detection of AI agents that use LLM calls
to perform structural, MRO, or layer-zoning validation - a violation of the
"AI-Checking-AI" constitutional rule.

Key Violations Detected:
- CognitiveDispositionAgent: Uses llm_generate to analyze violations
- ConstitutionalReviewerAgent: Uses LLM for constitutional review
- ConversationalRepairAgent: Uses LLM to validate code structure

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
class LLMValidationViolation:
    """A detected LLM-based validation violation."""

    agent_name: str
    file_path: Path
    layer: str
    method_name: str
    line_number: int
    violation_type: str
    description: str
    severity: str = "CRITICAL"


@dataclass
class Phase2AuditResult:
    """Result of Phase 2 LLM validation detection."""

    total_agents_scanned: int = 0
    agents_with_llm_validation: int = 0
    total_violations: int = 0
    violations: list[LLMValidationViolation] = field(default_factory=list)
    clean_agents: list[str] = field(default_factory=list)


# LLM validation patterns that indicate AI-checking-AI violations
LLM_VALIDATION_PATTERNS = {
    "llm_structural_check": {
        "patterns": [
            r"llm_generate.*(?:validate|verify|check|audit).*(?:struct|mro|layer)",
            r"(?:validate|verify|check|audit).*llm_generate",
            r"await\s+self\.llm_generate.*(?:violation|compliance|structure)",
        ],
        "description": "LLM used for structural validation",
        "severity": "CRITICAL",
    },
    "llm_disposition_decision": {
        "patterns": [
            r"llm_generate.*(?:disposition|decision|action)",
            r"analyze_violation.*llm",
            r"DispositionDecision.*llm_generate",
        ],
        "description": "LLM used for disposition/action decisions on code",
        "severity": "CRITICAL",
    },
    "llm_constitutional_review": {
        "patterns": [
            r"constitutional.*review.*(?:llm|chat_completion)",
            r"chat_completion.*(?:constitution|rules|compliance)",
            r"ConstitutionalReview.*(?:client|model)",
        ],
        "description": "LLM used for constitutional/compliance review",
        "severity": "HIGH",
    },
    "llm_code_repair": {
        "patterns": [
            r"llm_generate.*(?:repair|fix|heal).*(?:code|violation)",
            r"(?:repair|fix|heal).*code.*llm",
            r"ConversationalRepair.*llm",
        ],
        "description": "LLM used to repair/fix code violations",
        "severity": "HIGH",
    },
    "llm_layer_validation": {
        "patterns": [
            r"llm.*(?:layer|gravity|L[0-6]).*(?:valid|check)",
            r"(?:layer|gravity).*violation.*llm",
        ],
        "description": "LLM used to validate layer/gravity rules",
        "severity": "CRITICAL",
    },
}

# Known violators from the audit plan
KNOWN_VIOLATORS = [
    "CognitiveDispositionAgent",
    "ConstitutionalReviewerAgent",
    "ConversationalRepairAgent",
]

# Files explicitly allowed (test files, stubs)
ALLOWED_FILES = [
    "tests/",
    "conftest.py",
    "__init__.py",
]


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


def is_allowed_file(file_path: Path) -> bool:
    """Check if file should be skipped."""
    path_str = str(file_path).replace("\\", "/")
    return any(allowed in path_str for allowed in ALLOWED_FILES)


def find_llm_calls(file_path: Path) -> list[tuple[int, str]]:
    """Find all LLM-related calls in a file with line numbers."""
    llm_calls = []

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        lines = content.splitlines()

        llm_keywords = ["llm_generate", "llm_gateway", "chat_completion", "model_client"]

        for i, line in enumerate(lines, 1):
            for keyword in llm_keywords:
                if keyword in line:
                    llm_calls.append((i, line.strip()))

    except Exception:
        pass

    return llm_calls


def find_validation_context(file_path: Path, line_number: int) -> str:
    """Find the method/function context for a given line."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                    if node.lineno <= line_number <= (node.end_lineno or node.lineno + 100):
                        return node.name

    except Exception:
        pass

    return "unknown"


def scan_file_for_llm_validation(file_path: Path) -> list[LLMValidationViolation]:
    """Scan a file for LLM-based validation violations."""
    violations = []

    if is_allowed_file(file_path):
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

        layer = extract_layer(file_path)

        # Check for LLM validation patterns
        for pattern_name, pattern_info in LLM_VALIDATION_PATTERNS.items():
            for pattern in pattern_info["patterns"]:
                matches = list(re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE))
                for match in matches:
                    # Find line number
                    line_number = content[: match.start()].count("\n") + 1
                    method_name = find_validation_context(file_path, line_number)

                    violations.append(
                        LLMValidationViolation(
                            agent_name=agent_name,
                            file_path=file_path,
                            layer=layer,
                            method_name=method_name,
                            line_number=line_number,
                            violation_type=pattern_name,
                            description=pattern_info["description"],
                            severity=pattern_info["severity"],
                        )
                    )

        # Additional check: LLM calls in validation-named methods
        llm_calls = find_llm_calls(file_path)
        for line_num, line_content in llm_calls:
            method_name = find_validation_context(file_path, line_num)
            validation_method_patterns = [
                "validate",
                "check",
                "verify",
                "audit",
                "analyze_violation",
            ]
            if any(p in method_name.lower() for p in validation_method_patterns):
                # Check if this violation already recorded
                already_recorded = any(
                    v.line_number == line_num and v.file_path == file_path for v in violations
                )
                if not already_recorded:
                    violations.append(
                        LLMValidationViolation(
                            agent_name=agent_name,
                            file_path=file_path,
                            layer=layer,
                            method_name=method_name,
                            line_number=line_num,
                            violation_type="llm_in_validation_method",
                            description=f"LLM call in validation method: {method_name}",
                            severity="HIGH",
                        )
                    )

    except Exception:
        pass

    return violations


def run_phase2_audit(project_root: Path | None = None) -> Phase2AuditResult:
    """Run the Phase 2 LLM validation detection audit."""
    if project_root is None:
        project_root = PROJECT_ROOT

    result = Phase2AuditResult()

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
            if is_allowed_file(file_path):
                continue

            result.total_agents_scanned += 1
            violations = scan_file_for_llm_validation(file_path)

            if violations:
                result.agents_with_llm_validation += 1
                result.violations.extend(violations)
            else:
                # Extract agent name for clean list
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                            result.clean_agents.append(node.name)
                            break
                except Exception:
                    pass

    result.total_violations = len(result.violations)
    return result


def generate_phase2_report(result: Phase2AuditResult) -> str:
    """Generate a formatted Phase 2 audit report."""
    report = []
    report.append("=" * 70)
    report.append("PHASE 2: LLM-BASED STRUCTURAL VALIDATION DETECTION REPORT")
    report.append("=" * 70)
    report.append("")
    report.append(f"Total Agents Scanned: {result.total_agents_scanned}")
    report.append(f"Agents with LLM Validation: {result.agents_with_llm_validation}")
    report.append(f"Total Violations Found: {result.total_violations}")
    report.append("")

    if result.violations:
        report.append("VIOLATIONS DETECTED:")
        report.append("-" * 50)

        # Group by agent
        by_agent: dict[str, list[LLMValidationViolation]] = {}
        for v in result.violations:
            if v.agent_name not in by_agent:
                by_agent[v.agent_name] = []
            by_agent[v.agent_name].append(v)

        for agent_name, agent_violations in by_agent.items():
            report.append(f"\n📄 {agent_name} ({agent_violations[0].layer})")
            report.append(f"   File: {agent_violations[0].file_path}")
            for v in agent_violations:
                sev_icon = "🔴" if v.severity == "CRITICAL" else "🟡"
                report.append(f"   {sev_icon} Line {v.line_number}: {v.description}")
                report.append(f"      Method: {v.method_name}")
                report.append(f"      Type: {v.violation_type}")

        report.append("")

    # Known violators check
    report.append("KNOWN VIOLATOR STATUS:")
    report.append("-" * 50)
    detected_agents = {v.agent_name for v in result.violations}
    for known in KNOWN_VIOLATORS:
        if known in detected_agents:
            report.append(f"   ✅ {known}: DETECTED")
        else:
            report.append(f"   ⚠️  {known}: NOT DETECTED (may be compliant or not found)")

    report.append("")
    report.append("=" * 70)

    return "\n".join(report)


# ============================================================================
# PYTEST TEST CASES
# ============================================================================


class TestForensicAuditPhase2:
    """Test suite for Phase 2 LLM-Based Validation Detection."""

    def test_scan_runs_without_error(self):
        """Test that the scanner runs without errors."""
        result = run_phase2_audit(PROJECT_ROOT)
        assert result is not None
        assert result.total_agents_scanned > 0

    def test_scan_covers_all_territories(self):
        """Test that all territories are scanned."""
        result = run_phase2_audit(PROJECT_ROOT)
        # Should scan agents from multiple territories
        assert result.total_agents_scanned >= 50

    def test_llm_pattern_detection(self):
        """Test that LLM patterns are properly defined."""
        assert len(LLM_VALIDATION_PATTERNS) > 0
        for name, info in LLM_VALIDATION_PATTERNS.items():
            assert "patterns" in info
            assert "description" in info
            assert "severity" in info
            assert len(info["patterns"]) > 0

    def test_layer_extraction(self):
        """Test layer extraction from file paths."""
        test_cases = [
            (Path("agentic_core/L5_safety/validators/TestAgent.py"), "L5"),
            (Path("agentic_core/L1_cognition/TestAgent.py"), "L1"),
            (Path("apps_lic/engines/TestAgent.py"), "Apps-LIC"),
            (Path("apps_rg/engines/TestAgent.py"), "Apps-RG"),
        ]
        for path, expected in test_cases:
            assert extract_layer(path) == expected

    def test_allowed_files_excluded(self):
        """Test that test files are excluded."""
        test_path = Path("tests/guardian/test_example.py")
        assert is_allowed_file(test_path) is True

        agent_path = Path("agentic_core/L5_safety/validators/TestAgent.py")
        assert is_allowed_file(agent_path) is False

    def test_violation_dataclass(self):
        """Test LLMValidationViolation dataclass."""
        violation = LLMValidationViolation(
            agent_name="TestAgent",
            file_path=Path("test.py"),
            layer="L5",
            method_name="test_method",
            line_number=10,
            violation_type="llm_structural_check",
            description="Test description",
        )
        assert violation.agent_name == "TestAgent"
        assert violation.severity == "CRITICAL"

    def test_report_generation(self):
        """Test that report is properly generated."""
        result = run_phase2_audit(PROJECT_ROOT)
        report = generate_phase2_report(result)

        assert "PHASE 2" in report
        assert "LLM-BASED STRUCTURAL VALIDATION" in report
        assert "Total Agents Scanned" in report

    def test_known_violators_tracked(self):
        """Test that known violators are tracked."""
        assert len(KNOWN_VIOLATORS) >= 3
        assert "CognitiveDispositionAgent" in KNOWN_VIOLATORS
        assert "ConstitutionalReviewerAgent" in KNOWN_VIOLATORS

    def test_clean_agents_tracked(self):
        """Test that clean agents are tracked."""
        result = run_phase2_audit(PROJECT_ROOT)
        # Most agents should be clean
        assert len(result.clean_agents) > 0

    def test_violation_grouping_by_agent(self):
        """Test that violations can be grouped by agent."""
        result = run_phase2_audit(PROJECT_ROOT)

        by_agent: dict[str, list[Any]] = {}
        for v in result.violations:
            if v.agent_name not in by_agent:
                by_agent[v.agent_name] = []
            by_agent[v.agent_name].append(v)

        # Grouping should work
        for agent_name, violations in by_agent.items():
            assert all(v.agent_name == agent_name for v in violations)

    def test_severity_levels(self):
        """Test that severity levels are properly assigned."""
        valid_severities = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
        for info in LLM_VALIDATION_PATTERNS.values():
            assert info["severity"] in valid_severities

    def test_no_false_positives_in_tests(self):
        """Test that test files don't generate violations."""
        result = run_phase2_audit(PROJECT_ROOT)

        for v in result.violations:
            path_str = str(v.file_path).replace("\\", "/")
            assert "tests/" not in path_str, f"Test file generated violation: {v.file_path}"


def test_forensic_audit_phase2():
    """Main test entry point for Phase 2 LLM Validation Detection."""
    print("\n" + "=" * 70)
    print("PHASE 2: LLM-BASED STRUCTURAL VALIDATION DETECTION - RUNNING TESTS")
    print("=" * 70 + "\n")

    result = run_phase2_audit(PROJECT_ROOT)
    report = generate_phase2_report(result)
    print(report)

    # Assertions
    assert result.total_agents_scanned >= 50, "Should scan 50+ agents"

    print("\n✅ Phase 2 LLM Validation Detection: PASSED")
    print(f"   Scanned {result.total_agents_scanned} agents")
    print(f"   Found {result.agents_with_llm_validation} agents with LLM validation")
    print(f"   Total violations: {result.total_violations}")


if __name__ == "__main__":
    test_forensic_audit_phase2()
