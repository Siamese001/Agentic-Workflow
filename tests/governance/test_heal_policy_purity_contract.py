"""
Governance contract: Heal policy module purity enforcement.

Ensures heal_policy_types.py remains pure (stdlib-only, no routing/executor imports).

Phase 5 Wave 5.1 acceptance test.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.governance


POLICY_MODULE_PATH = Path("agentic_core/L5_safety/types/heal_policy_types.py")

BANNED_IMPORT_ROOTS = {
    "agentic_core.L0_routing",
    "agentic_core.executors",
    "apps_",
}

BANNED_KEYWORDS = {
    "router",
    "executor",
    "openai",
    "gemini",
    "vllm",
    "anthropic",
}


class TestHealPolicyPurityContract:
    """Enforce heal_policy_types.py remains pure (stdlib-only)."""

    def test_stdlib_only_imports(self) -> None:
        """Heal policy module must import stdlib only (no routing/executor imports)."""
        module_path = Path.cwd() / POLICY_MODULE_PATH
        assert module_path.exists(), f"Policy module not found: {module_path}"

        source = module_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(module_path))

        violations: list[str] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for banned_root in BANNED_IMPORT_ROOTS:
                        if alias.name.startswith(banned_root):
                            violations.append(
                                f"Line {node.lineno}: Banned import '{alias.name}' (matches '{banned_root}')"
                            )

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for banned_root in BANNED_IMPORT_ROOTS:
                        if node.module.startswith(banned_root):
                            violations.append(
                                f"Line {node.lineno}: Banned import from '{node.module}' "
                                f"(matches '{banned_root}')"
                            )

        assert not violations, "Policy module contains banned imports:\n" + "\n".join(violations)

    def test_no_network_model_keywords(self) -> None:
        """Heal policy module must not contain network/model keywords."""
        module_path = Path.cwd() / POLICY_MODULE_PATH
        assert module_path.exists(), f"Policy module not found: {module_path}"

        source = module_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(module_path))

        violations: list[str] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                name_lower = node.id.lower()
                for banned_keyword in BANNED_KEYWORDS:
                    if banned_keyword in name_lower:
                        violations.append(
                            f"Line {node.lineno}: Banned keyword '{node.id}' (contains '{banned_keyword}')"
                        )

            elif isinstance(node, ast.Attribute):
                attr_lower = node.attr.lower()
                for banned_keyword in BANNED_KEYWORDS:
                    if banned_keyword in attr_lower:
                        violations.append(
                            f"Line {node.lineno}: Banned attribute '{node.attr}' "
                            f"(contains '{banned_keyword}')"
                        )

        assert not violations, "Policy module contains banned keywords:\n" + "\n".join(violations)

    def test_no_banned_string_literals(self) -> None:
        """Heal policy module must not contain banned keywords in string literals."""
        module_path = Path.cwd() / POLICY_MODULE_PATH
        assert module_path.exists(), f"Policy module not found: {module_path}"

        source = module_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(module_path))

        violations: list[str] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                value_lower = node.value.lower()
                for banned_keyword in BANNED_KEYWORDS:
                    if banned_keyword in value_lower:
                        violations.append(
                            f"Line {node.lineno}: Banned keyword in string '{node.value[:50]}...' "
                            f"(contains '{banned_keyword}')"
                        )

        assert not violations, "Policy module contains banned keywords in strings:\n" + "\n".join(violations)
