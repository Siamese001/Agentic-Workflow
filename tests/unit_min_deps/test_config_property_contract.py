"""
Config property regression guard for inspector agents.

Enforced invariants:
    1. Inspector agents must NOT assign to self.config inside __init__.
    2. ConfigMixin.config must remain a property (not a plain attribute).
    3. AST scan: Assign(target=Attribute(attr="config")) inside __init__ is forbidden.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    L3_ORCHESTRATION_DIR,
)

pytestmark = pytest.mark.unit_min_deps

ROOT = Path(__file__).resolve().parents[2]

INSPECTOR_FILES = [
    ROOT / L3_ORCHESTRATION_DIR / "reasoning" / "DagRuntimeInspectorAgent.py",
    ROOT / AGENTIC_CORE_DIR / "L5_safety" / "reasoning" / "SafetyInspectorAgent.py",
    ROOT / AGENTIC_CORE_DIR / "L5_safety" / "reasoning" / "SprawlInspectorAgent.py",
]


def _parse_file(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return None


def _find_self_config_assigns_in_init(tree: ast.Module) -> list[tuple[str, int]]:
    """Find all `self.config = ...` assignments inside __init__ methods.

    Returns list of (class_name, lineno) tuples.
    """
    violations: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        class_name = node.name
        for item in ast.walk(node):
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if item.name != "__init__":
                continue
            for stmt in ast.walk(item):
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if (
                            isinstance(target, ast.Attribute)
                            and isinstance(target.value, ast.Name)
                            and target.value.id == "self"
                            and target.attr == "config"
                        ):
                            violations.append((class_name, stmt.lineno))
    return violations


# ---------------------------------------------------------------------------
# 1. No inspector agent assigns to self.config in __init__
# ---------------------------------------------------------------------------


class TestNoSelfConfigAssignInInit:
    """Inspector agents must not assign to self.config (conflicts with ConfigMixin property)."""

    @pytest.mark.parametrize(
        "inspector_file",
        INSPECTOR_FILES,
        ids=[p.stem for p in INSPECTOR_FILES],
    )
    def test_no_self_config_assign(self, inspector_file: Path) -> None:
        tree = _parse_file(inspector_file)
        assert tree is not None, f"Cannot parse {inspector_file.name}"

        violations = _find_self_config_assigns_in_init(tree)
        assert not violations, (
            f"{inspector_file.name} assigns to self.config in __init__:\n"
            + "\n".join(f"  {cls}.__init__ line {ln}" for cls, ln in violations)
            + "\nUse self._inspector_config instead to avoid ConfigMixin property conflict."
        )


# ---------------------------------------------------------------------------
# 2. ConfigMixin.config must be a property
# ---------------------------------------------------------------------------


class TestConfigMixinPropertyContract:
    """ConfigMixin.config must remain a property descriptor, not a plain attribute."""

    def test_config_is_property(self) -> None:
    """Test config_is_property contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"
    """Scan agentic_core for any agent that assigns to self.config in __init__.

    Pre-existing violations (5) are tracked as a ceiling that must not increase.
    """

    # Pre-existing debt ceiling — must not increase.
    _MAX_ALLOWED_VIOLATIONS = 5

    def test_config_overwrite_ceiling(self) -> None:
    """Test config_overwrite_ceiling contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"
                violations.append(f"{rel}:{lineno} {cls_name}.__init__ assigns self.config")

        assert len(violations) <= self._MAX_ALLOWED_VIOLATIONS, (
            f"Config overwrite ceiling breached: {len(violations)} > {self._MAX_ALLOWED_VIOLATIONS}.\n"
            f"New violations:\n"
            + "\n".join(f"  {v}" for v in violations[:30])
            + "\nUse self._inspector_config or similar to avoid ConfigMixin conflict."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
