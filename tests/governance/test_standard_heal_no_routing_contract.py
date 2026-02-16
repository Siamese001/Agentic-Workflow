"""
Governance contract: standard_heal routing/executor ban enforcement.

Ensures standard_heal decorator and its wrapper do not contain routing/executor calls.

Phase 5 Wave 5.2 acceptance test.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.governance


DECORATORS_MODULE_PATH = Path("agentic_core/utils/decorators_util.py")

BANNED_IMPORT_MODULES = {
    "L0_routing",
    "executors",
    "model_router",
    "openai",
    "gemini",
    "vllm",
    "anthropic",
}

BANNED_CALL_NAMES = {
    "route",
    "router",
    "execute_model",
    "call_llm",
    "completion",
    "chat",
    "invoke",
}

# Allowlist: Controlled seam variables (not actual routing calls)
ALLOWED_SEAM_VARIABLES = {
    "_HEAL_MODEL_ROUTER",
    "_HEAL_TIER_OBSERVER",
}


class TestStandardHealNoRoutingContract:
    """Enforce standard_heal contains no routing/executor calls."""

    def test_no_banned_imports(self) -> None:
        """standard_heal module must not import routing/executor modules."""
        module_path = Path.cwd() / DECORATORS_MODULE_PATH
        assert module_path.exists(), f"Decorators module not found: {module_path}"

        source = module_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(module_path))

        violations: list[str] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for banned_module in BANNED_IMPORT_MODULES:
                        if banned_module in alias.name:
                            violations.append(
                                f"Line {node.lineno}: Banned import '{alias.name}' "
                                f"(contains '{banned_module}')"
                            )

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for banned_module in BANNED_IMPORT_MODULES:
                        if banned_module in node.module:
                            violations.append(
                                f"Line {node.lineno}: Banned import from '{node.module}' "
                                f"(contains '{banned_module}')"
                            )

        assert not violations, "Decorators module contains banned imports:\n" + "\n".join(violations)

    def test_standard_heal_no_routing_calls(self) -> None:
        """standard_heal function must not contain routing/executor calls."""
        module_path = Path.cwd() / DECORATORS_MODULE_PATH
        assert module_path.exists(), f"Decorators module not found: {module_path}"

        source = module_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(module_path))

        standard_heal_func = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "standard_heal":
                standard_heal_func = node
                break

        assert standard_heal_func is not None, "standard_heal function not found"

        violations: list[str] = []

        for node in ast.walk(standard_heal_func):
            if isinstance(node, ast.Call):
                call_name = None

                if isinstance(node.func, ast.Name):
                    call_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    call_name = node.func.attr

                if call_name:
                    # Skip allowlisted seam variables
                    if call_name in ALLOWED_SEAM_VARIABLES:
                        continue

                    call_name_lower = call_name.lower()
                    for banned_name in BANNED_CALL_NAMES:
                        if banned_name in call_name_lower:
                            violations.append(
                                f"Line {node.lineno}: Banned call '{call_name}' (contains '{banned_name}')"
                            )

        assert not violations, "standard_heal contains banned calls:\n" + "\n".join(violations)

    def test_wrapper_function_no_routing_calls(self) -> None:
        """Nested wrapper function in standard_heal must not contain routing calls."""
        module_path = Path.cwd() / DECORATORS_MODULE_PATH
        assert module_path.exists(), f"Decorators module not found: {module_path}"

        source = module_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(module_path))

        standard_heal_func = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "standard_heal":
                standard_heal_func = node
                break

        assert standard_heal_func is not None, "standard_heal function not found"

        wrapper_func = None
        for node in ast.walk(standard_heal_func):
            if isinstance(node, ast.FunctionDef) and node.name == "wrapper":
                wrapper_func = node
                break

        assert wrapper_func is not None, "wrapper function not found in standard_heal"

        violations: list[str] = []

        for node in ast.walk(wrapper_func):
            if isinstance(node, ast.Call):
                call_name = None

                if isinstance(node.func, ast.Name):
                    call_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    call_name = node.func.attr

                if call_name:
                    # Skip allowlisted seam variables
                    if call_name in ALLOWED_SEAM_VARIABLES:
                        continue

                    call_name_lower = call_name.lower()
                    for banned_name in BANNED_CALL_NAMES:
                        if banned_name in call_name_lower:
                            violations.append(
                                f"Line {node.lineno}: Banned call '{call_name}' (contains '{banned_name}')"
                            )

        assert not violations, "standard_heal wrapper contains banned calls:\n" + "\n".join(violations)
