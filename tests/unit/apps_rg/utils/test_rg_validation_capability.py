"""
AST-based structural tests for RGValidationCapability.

Tests:
1. Responsibility Cohesion — capability contains NO domain-specific words
2. All 4 agents inherit from RGValidationCapability
3. All 4 agents set required ClassVar constants
4. All 4 agents implement collect_issues()
5. content_to_string handles all types correctly
6. make_heal_result returns canonical schema
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
    re.compile(r"\bats\b", re.IGNORECASE),
    re.compile(r"\bbrand\b", re.IGNORECASE),
    re.compile(r"\bfact\b", re.IGNORECASE),
    re.compile(r"\bsection\b", re.IGNORECASE),
    re.compile(r"\bresume\b", re.IGNORECASE),
    re.compile(r"\bcompliance\b", re.IGNORECASE),
    re.compile(r"\bhallucination\b", re.IGNORECASE),
    re.compile(r"\bbalance\b", re.IGNORECASE),
    re.compile(r"\bkeyword\b", re.IGNORECASE),
    re.compile(r"\bheader\b", re.IGNORECASE),
    re.compile(r"\bforbidden.phrases\b", re.IGNORECASE),
    re.compile(r"\bpower.verbs\b", re.IGNORECASE),
]

CAPABILITY_PATH = ROOT / "apps_rg" / "utils" / "rg_validation_capability.py"


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

        Uses word-boundary regex so 'artifacts' does NOT match 'fact',
        but standalone 'fact' DOES match.
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

            # Check identifiers (variable names, function names, class names)
            if isinstance(node, ast.Name):
                hits = _check_text_for_domain_words(node.id)
                for pat in hits:
                    violations.append(f"L{node.lineno}: identifier '{node.id}' matches {pat}")

            # Check function/method names — use underscore-split for word boundaries
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Replace _ with space for word-boundary matching
                readable = node.name.replace("_", " ")
                hits = _check_text_for_domain_words(readable)
                for pat in hits:
                    violations.append(f"L{node.lineno}: function '{node.name}' matches {pat}")

            # Check class names — use CamelCase split for word boundaries
            if isinstance(node, ast.ClassDef):
                readable = re.sub(r"([A-Z])", r" \1", node.name)
                hits = _check_text_for_domain_words(readable)
                for pat in hits:
                    violations.append(f"L{node.lineno}: class '{node.name}' matches {pat}")

        assert not violations, (
            f"RGValidationCapability violates Responsibility Cohesion — "
            f"{len(violations)} domain word(s) found:\n" + "\n".join(violations)
        )


# ============================================================================
# 2. ALL 4 AGENTS INHERIT FROM CAPABILITY
# ============================================================================

AGENT_FILES = [
    ROOT / "apps_rg" / "reasoning" / "ATSCompatibilityAgent.py",
    ROOT / "apps_rg" / "reasoning" / "BrandComplianceAgent.py",
    ROOT / "apps_rg" / "reasoning" / "FactCheckAgent.py",
    ROOT / "apps_rg" / "reasoning" / "SectionBalanceAgent.py",
]


class TestAgentStructure:
    """AST-based verification that all 4 agents use the capability correctly."""

    @pytest.mark.parametrize(
        "agent_path",
        AGENT_FILES,
        ids=lambda p: p.stem,
    )
    def test_inherits_rg_validation_capability(self, agent_path: Path) -> None:
        """Each agent class must list RGValidationCapability in its bases."""
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

                assert "RGValidationCapability" in base_names, (
                    f"{agent_path.stem}.{node.name} does not inherit RGValidationCapability. "
                    f"Bases: {base_names}"
                )
                return

        pytest.fail(f"No Agent class found in {agent_path.stem}")

    @pytest.mark.parametrize(
        "agent_path",
        AGENT_FILES,
        ids=lambda p: p.stem,
    )
    def test_sets_validation_signal(self, agent_path: Path) -> None:
        """Each agent must define VALIDATION_SIGNAL as a non-empty class variable."""
        source = agent_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id == "VALIDATION_SIGNAL":
                                assert isinstance(item.value, ast.Constant), (
                                    f"{node.name}.VALIDATION_SIGNAL must be a string constant"
                                )
                                assert item.value.value, f"{node.name}.VALIDATION_SIGNAL must not be empty"
                                return

        pytest.fail(f"No VALIDATION_SIGNAL found in {agent_path.stem}")

    @pytest.mark.parametrize(
        "agent_path",
        AGENT_FILES,
        ids=lambda p: p.stem,
    )
    def test_implements_collect_issues(self, agent_path: Path) -> None:
        """Each agent must implement async def collect_issues()."""
        source = agent_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                method_names = [
                    item.name
                    for item in node.body
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                assert "collect_issues" in method_names, f"{node.name} must implement collect_issues()"
                # Verify it's async
                for item in node.body:
                    if isinstance(item, ast.AsyncFunctionDef) and item.name == "collect_issues":
                        return
                pytest.fail(f"{node.name}.collect_issues must be async")

        pytest.fail(f"No Agent class found in {agent_path.stem}")

    @pytest.mark.parametrize(
        "agent_path",
        AGENT_FILES,
        ids=lambda p: p.stem,
    )
    def test_execute_delegates_to_run_validation(self, agent_path: Path) -> None:
        """Each agent's execute() should call self.run_validation() (directly or after guards)."""
        source = agent_path.read_text(encoding="utf-8")
        assert "run_validation" in source, f"{agent_path.stem} execute() must call run_validation()"


# ============================================================================
# 3. UNIT TESTS FOR CAPABILITY METHODS
# ============================================================================


class TestContentToString:
    """Test the shared content_to_string utility."""

    def setup_method(self) -> None:
        from apps_rg.utils.rg_validation_capability import RGValidationCapability

        self.cap = RGValidationCapability()

    def test_string_passthrough(self) -> None:
        assert self.cap.content_to_string("hello") == "hello"

    def test_list_join(self) -> None:
        assert self.cap.content_to_string(["a", "b", "c"]) == "a b c"

    def test_dict_json(self) -> None:
        result = self.cap.content_to_string({"key": "val"})
        assert '"key"' in result and '"val"' in result

    def test_other_str(self) -> None:
        assert self.cap.content_to_string(42) == "42"

    def test_empty_list(self) -> None:
        assert self.cap.content_to_string([]) == ""


class TestMakeHealResult:
    """Test the standard heal stub generator."""

    def setup_method(self) -> None:
        from apps_rg.utils.rg_validation_capability import RGValidationCapability

        self.cap = RGValidationCapability()

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
        assert "RGValidationCapability" in result["details"]
