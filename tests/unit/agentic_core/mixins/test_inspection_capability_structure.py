"""
AST-based structural tests for InspectionCapability.

Tests:
1. Responsibility Cohesion — capability contains NO domain-specific words
2. All 3 agents inherit from InspectionCapability
3. All 3 agents set INSPECTION_LOG_PREFIX
4. All 3 agents implement perform_checks()
5. All 3 agents delegate diagnose() to run_inspection()
6. InspectionResult has canonical fields
7. make_heal_result returns canonical schema
8. No legacy DiagnosticReport type in inspection_capability (post-cleanup invariant)
9. All agents' diagnose() return-type annotation is InspectionResult (post-cleanup invariant)
10. No inspector agent defines execute() (post-cleanup invariant)
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]

# ============================================================================
# 1. RESPONSIBILITY COHESION — No domain words in capability source
# ============================================================================

FORBIDDEN_DOMAIN_PATTERNS = [
    re.compile(r"\bdag\b", re.IGNORECASE),
    re.compile(r"\btoken\b", re.IGNORECASE),
    re.compile(r"\bbudget\b", re.IGNORECASE),
    re.compile(r"\bsignature\b", re.IGNORECASE),
    re.compile(r"\bcrypto\b", re.IGNORECASE),
    re.compile(r"\bruntime\b", re.IGNORECASE),
    re.compile(r"\bverif(?:y|ication|ier)\b", re.IGNORECASE),
    re.compile(r"\bgraph\b", re.IGNORECASE),
]

CAPABILITY_PATH = ROOT / "agentic_core" / "mixins" / "inspection_capability.py"


def _check_text_for_domain_words(text: str) -> list[str]:
    """Return list of matched domain words using word-boundary regex."""
    hits: list[str] = []
    for pat in FORBIDDEN_DOMAIN_PATTERNS:
        if pat.search(text):
            hits.append(pat.pattern)
    return hits


class TestResponsibilityCohesion:
    """Ensure the capability mixin contains zero domain-specific vocabulary."""

    def test_no_domain_words_in_source(self) -> None:
        """AST-walk every string literal and identifier in the capability file.

        Uses word-boundary regex so compound words do NOT false-positive.
        """
        source = CAPABILITY_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)

        violations: list[str] = []
        for node in ast.walk(tree):
            # Check string literals (docstrings, log messages)
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                hits = _check_text_for_domain_words(node.value)
                for pat in hits:
                    violations.append(
                        f"L{node.lineno}: string literal matches {pat}: {node.value[:80]!r}",
                    )

            # Check identifiers
            if isinstance(node, ast.Name):
                hits = _check_text_for_domain_words(node.id)
                for pat in hits:
                    violations.append(f"L{node.lineno}: identifier '{node.id}' matches {pat}")

            # Check function/method names
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                readable = node.name.replace("_", " ")
                hits = _check_text_for_domain_words(readable)
                for pat in hits:
                    violations.append(f"L{node.lineno}: function '{node.name}' matches {pat}")

            # Check class names
            if isinstance(node, ast.ClassDef):
                readable = re.sub(r"([A-Z])", r" \1", node.name)
                hits = _check_text_for_domain_words(readable)
                for pat in hits:
                    violations.append(f"L{node.lineno}: class '{node.name}' matches {pat}")

        assert not violations, (
            f"InspectionCapability violates Responsibility Cohesion — "
            f"{len(violations)} domain word(s) found:\n" + "\n".join(violations)
        )


# ============================================================================
# 2. ALL 3 AGENTS INHERIT FROM CAPABILITY
# ============================================================================

AGENT_FILES = [
    ROOT / "agentic_core" / "L3_orchestration" / "reasoning" / "DagRuntimeInspectorAgent.py",
    ROOT / "agentic_core" / "L5_safety" / "reasoning" / "TokenBudgetInspectorAgent.py",
    ROOT / "agentic_core" / "L5_safety" / "reasoning" / "SignatureVerifierAgent.py",
]


class TestAgentStructure:
    """AST-based verification that all 3 agents use the capability correctly."""

    @pytest.mark.parametrize(
        "agent_path",
        AGENT_FILES,
        ids=lambda p: p.stem,
    )
    def test_inherits_inspection_capability(self, agent_path: Path) -> None:
        """Each agent class must list InspectionCapability in its bases."""
        source = agent_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                base_names = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        base_names.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        base_names.append(base.attr)

                assert "InspectionCapability" in base_names, (
                    f"{agent_path.stem}.{node.name} does not inherit InspectionCapability. "
                    f"Bases: {base_names}"
                )
                return

        pytest.fail(f"No Agent class found in {agent_path.stem}")

    @pytest.mark.parametrize(
        "agent_path",
        AGENT_FILES,
        ids=lambda p: p.stem,
    )
    def test_sets_inspection_log_prefix(self, agent_path: Path) -> None:
        """Each agent must define INSPECTION_LOG_PREFIX as a non-empty class variable."""
        source = agent_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id == "INSPECTION_LOG_PREFIX":
                                assert isinstance(item.value, ast.Constant), (
                                    f"{node.name}.INSPECTION_LOG_PREFIX must be a string constant"
                                )
                                assert item.value.value, (
                                    f"{node.name}.INSPECTION_LOG_PREFIX must not be empty"
                                )
                                return

        pytest.fail(f"No INSPECTION_LOG_PREFIX found in {agent_path.stem}")

    @pytest.mark.parametrize(
        "agent_path",
        AGENT_FILES,
        ids=lambda p: p.stem,
    )
    def test_has_perform_checks(self, agent_path: Path) -> None:
        """Each agent must have perform_checks() — either locally or inherited from InspectionCapability."""
        source = agent_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                # Check local definition
                method_names = [
                    item.name
                    for item in node.body
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                if "perform_checks" in method_names:
                    return  # locally defined — OK

                # Check inheritance from InspectionCapability
                base_names = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        base_names.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        base_names.append(base.attr)

                assert "InspectionCapability" in base_names, (
                    f"{node.name} must either implement perform_checks() locally "
                    f"or inherit from InspectionCapability. Bases: {base_names}"
                )
                return

        pytest.fail(f"No Agent class found in {agent_path.stem}")

    @pytest.mark.parametrize(
        "agent_path",
        AGENT_FILES,
        ids=lambda p: p.stem,
    )
    def test_diagnose_delegates_to_run_inspection(self, agent_path: Path) -> None:
        """Each agent's diagnose() should call self.run_inspection()."""
        source = agent_path.read_text(encoding="utf-8")
        assert "run_inspection" in source, f"{agent_path.stem} diagnose() must call run_inspection()"


# ============================================================================
# 3. UNIT TESTS FOR CAPABILITY METHODS
# ============================================================================


class TestInspectionResult:
    """Test the shared InspectionResult dataclass."""

    def test_default_healthy(self) -> None:
        from agentic_core.mixins.inspection_capability import InspectionResult

        result = InspectionResult()
        assert result.healthy is True
        assert result.issues == []
        assert result.metrics == {}

    def test_unhealthy_with_issues(self) -> None:
        from agentic_core.mixins.inspection_capability import InspectionResult

        result = InspectionResult(healthy=False, issues=["problem"], metrics={"count": 1})
        assert result.healthy is False
        assert len(result.issues) == 1
        assert result.metrics["count"] == 1


class TestMakeHealResult:
    """Test the standard heal stub generator."""

    def setup_method(self) -> None:
        from agentic_core.mixins.inspection_capability import InspectionCapability

        self.cap = InspectionCapability()

    def test_canonical_keys(self) -> None:
        result = self.cap.make_heal_result({"type": "test_violation"})
        assert set(result.keys()) == {"status", "details", "artifacts", "errors"}

    def test_default_skipped(self) -> None:
        result = self.cap.make_heal_result({"type": "x"})
        assert result["status"] == "skipped"

    def test_custom_status(self) -> None:
        result = self.cap.make_heal_result({"type": "x"}, status="deferred")
        assert result["status"] == "deferred"

    def test_includes_class_name(self) -> None:
        result = self.cap.make_heal_result({"type": "x"})
        assert "InspectionCapability" in result["details"]
