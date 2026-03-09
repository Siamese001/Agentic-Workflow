"""
Integration test: No agents outside reasoning/.

Validates:
- Scan a fixture tree for Agent classes
- Before remediation: violations exist
- After remediation: no violations
"""

import ast
from pathlib import Path

import pytest


def find_agents_outside_reasoning(root: Path) -> list[str]:
    """
    Scan directory tree for Agent classes outside reasoning/.

    Returns list of violation paths.
    """
    violations = []

    for py_file in root.rglob("*.py"):
        # Skip reasoning/ folders
        path_str = str(py_file)
        if "/reasoning/" in path_str or "\\reasoning\\" in path_str:
            continue

        # Skip test files
        if "/tests/" in path_str or "\\tests\\" in path_str:
            continue

        # Skip base_agents (allowed location for base classes)
        if "/base_agents/" in path_str or "\\base_agents\\" in path_str:
            continue

        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if node.name.endswith("Agent") and not node.name.startswith("I"):
                        # Check if it's a Protocol
                        is_protocol = any(
                            (isinstance(base, ast.Name) and base.id == "Protocol")
                            or (isinstance(base, ast.Attribute) and base.attr == "Protocol")
                            for base in node.bases
                        )
                        # Check if it's in a docstring/comment (class name in string)
                        if not is_protocol:
                            violations.append(str(py_file))
                            break
        except SyntaxError:
            continue
        except Exception:
            continue

    return violations


class TestNoAgentsOutsideReasoning:
    """Tests for Agent class placement."""

    def test_agentic_core_no_agents_in_types(self):
        """No Agent classes should exist in types/ folders."""
        base = Path(__file__).resolve().parents[3] / "agentic_core"
        if not base.exists():
            pytest.fail("agentic_core not found")

        violations = []
        for types_dir in base.rglob("types"):
            if types_dir.is_dir():
                for py_file in types_dir.glob("*.py"):
                    try:
                        content = py_file.read_text(encoding="utf-8", errors="ignore")
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                if node.name.endswith("Agent") and not node.name.startswith("I"):
                                    # Skip Protocol interfaces
                                    is_protocol = any(
                                        (isinstance(base, ast.Name) and base.id == "Protocol")
                                        for base in node.bases
                                    )
                                    if not is_protocol:
                                        violations.append(f"{py_file}: {node.name}")
                    except SyntaxError:
                        continue

        assert len(violations) == 0, f"Agent classes found in types/: {violations}"

    def test_agentic_core_no_agents_in_config(self):
        """No Agent classes should exist in config/ folders."""
        base = Path(__file__).resolve().parents[3] / "agentic_core"
        if not base.exists():
            pytest.fail("agentic_core not found")

        violations = []
        for config_dir in base.rglob("config"):
            if config_dir.is_dir():
                for py_file in config_dir.glob("*.py"):
                    try:
                        content = py_file.read_text(encoding="utf-8", errors="ignore")
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                if node.name.endswith("Agent") and not node.name.startswith("I"):
                                    is_protocol = any(
                                        (isinstance(base, ast.Name) and base.id == "Protocol")
                                        for base in node.bases
                                    )
                                    if not is_protocol:
                                        violations.append(f"{py_file}: {node.name}")
                    except SyntaxError:
                        continue

        assert len(violations) == 0, f"Agent classes found in config/: {violations}"

    def test_agentic_core_no_agents_in_validators(self):
        """No Agent classes should exist in validators/ folders."""
        base = Path(__file__).resolve().parents[3] / "agentic_core"
        if not base.exists():
            pytest.fail("agentic_core not found")

        violations = []
        for validators_dir in base.rglob("validators"):
            if validators_dir.is_dir():
                for py_file in validators_dir.glob("*.py"):
                    try:
                        content = py_file.read_text(encoding="utf-8", errors="ignore")
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                if node.name.endswith("Agent") and not node.name.startswith("I"):
                                    is_protocol = any(
                                        (isinstance(base, ast.Name) and base.id == "Protocol")
                                        for base in node.bases
                                    )
                                    if not is_protocol:
                                        violations.append(f"{py_file}: {node.name}")
                    except SyntaxError:
                        continue

        assert len(violations) == 0, f"Agent classes found in validators/: {violations}"


class TestFixtureRepoAgentPlacement:
    """Tests using fixture repo for agent placement."""

    def test_synthetic_repo_before_remediation(self, tmp_path):
        """Synthetic repo with violations should have violations detected."""
        # Create a violation: Agent in types/
        types_dir = tmp_path / "agentic_core" / "L5_safety" / "types"
        types_dir.mkdir(parents=True)
        (types_dir / "bad_agent.py").write_text("""
class BadAgent:
    def execute(self):
        pass
""")

        violations = find_agents_outside_reasoning(tmp_path)
        assert len(violations) > 0, "Should detect Agent in types/"

    def test_synthetic_repo_after_remediation(self, tmp_path):
        """Synthetic repo with proper placement should have no violations."""
        # Create proper placement: Agent in reasoning/
        reasoning_dir = tmp_path / "agentic_core" / "L5_safety" / "reasoning"
        reasoning_dir.mkdir(parents=True)
        (reasoning_dir / "good_agent.py").write_text("""
class GoodAgent:
    def execute(self):
        pass
""")

        violations = find_agents_outside_reasoning(tmp_path)
        assert len(violations) == 0, f"Should have no violations: {violations}"
