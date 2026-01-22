# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: guardrail
from __future__ import annotations
# This boosts alignment detection — review and integrate appropriately


# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, prompt, validator, workflow
# This boosts alignment detection — review and integrate appropriately

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

from dataclasses import dataclass

"""
TestGeneratorAgent: Automatically creates subatomic tests for agents.
Created: 2026-01-13 | Version: 2.0.0

This agent parses agent source files via AST and generates corresponding
test cases for methods, ensuring L0 maintenance health.
"""

import ast
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.validators.decorators import standard_heal

log = logging.getLogger(__name__)


@dataclass
class TestGeneratorAgent(SovereignBaseAgent):
    """
    Autonomous agent that generates subatomic tests for agent classes.

    Capabilities:
    - Parses agent source files using AST
    - Identifies public methods and their signatures
    - Generates pytest-compatible test skeletons
    - Detects mixin inheritance for specialized test patterns
    """

    def __init__(self, tests_dir: Path | None = None) -> None:
        """
        Initialize test generator agent.

        Args:
            tests_dir: Optional directory for generated tests (defaults to tests/autogen)
        """
        super().__init__()
        self.tests_dir: Path = tests_dir or Path("tests/autogen")
        self.tests_dir.mkdir(parents=True, exist_ok=True)
        self._generated_tests: list[dict[str, Any]] = []
        log.info("[L0 TESTING] TestGeneratorAgent initialized")

    def generate_tests_for_agent(self, agent_path: str) -> dict[str, Any]:
        """
        Scan agent file and generate corresponding test cases.

        Args:
            agent_path: Path to the agent Python file

        Returns:
            Dict with generation result: {success: bool, test_file: str, tests_count: int}
        """
        path = Path(agent_path)
        if not path.exists():
            return {"success": False, "error": f"File not found: {agent_path}"}

        if not path.suffix == ".py":
            return {"success": False, "error": "Not a Python file"}

        log.info(f"[L0 TESTING] Generating tests for: {agent_path}")

        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except SyntaxError as e:
            return {"success": False, "error": f"Syntax error: {e}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

        # Extract class information
        classes = self._extract_classes(tree)
        if not classes:
            return {"success": False, "error": "No classes found in file"}

        # Generate test file
        test_content = self._generate_test_file(path, classes)

        # Write test file
        test_filename = f"test_{path.stem}.py"
        test_path = self.tests_dir / test_filename

        try:
            test_path.write_text(test_content, encoding="utf-8")
        except Exception as e:
            return {"success": False, "error": f"Failed to write test file: {e}"}

        # Record generation
        record = {
            "source_file": str(path),
            "test_file": str(test_path),
            "classes": [c["name"] for c in classes],
            "tests_count": sum(len(c["methods"]) for c in classes),
            "timestamp": datetime.now().isoformat(),
        }
        self._generated_tests.append(record)

        log.info(f"[L0 TESTING] Generated {record['tests_count']} tests in {test_path}")
        return {
            "success": True,
            "test_file": str(test_path),
            "tests_count": record["tests_count"],
            "classes": record["classes"],
        }

    def _extract_classes(self, tree: ast.AST) -> list[dict[str, Any]]:
        """Extract class definitions and their methods from AST."""
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "bases": [self._get_base_name(b) for b in node.bases],
                    "methods": [],
                    "has_healer_mixin": False,
                    "has_mcp_mixin": False,
                }

                # Check for mixin inheritance
                for base in class_info["bases"]:
                    if "HealerMixin" in base:
                        class_info["has_healer_mixin"] = True
                    if "MCPHardenedMixin" in base:
                        class_info["has_mcp_mixin"] = True

                # Extract methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                        if not item.name.startswith("_"):  # Public methods only
                            method_info = {
                                "name": item.name,
                                "is_async": isinstance(item, ast.AsyncFunctionDef),
                                "args": self._extract_args(item),
                                "has_return": self._has_return(item),
                            }
                            class_info["methods"].append(method_info)

                classes.append(class_info)

        return classes

    def _get_base_name(self, base: ast.expr) -> str:
        """Extract base class name from AST node."""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return base.attr
        return "Unknown"

    def _extract_args(self, func: ast.FunctionDef) -> list[str]:
        """Extract argument names from function definition."""
        args = []
        for arg in func.args.args:
            if arg.arg != "self":
                args.append(arg.arg)
        return args

    def _has_return(self, func: ast.FunctionDef) -> bool:
        """Check if function has a return statement with a value."""
        for node in ast.walk(func):
            if isinstance(node, ast.Return) and node.value is not None:
                return True
        return False

    def _generate_test_file(self, source_path: Path, classes: list[dict[str, Any]]) -> str:
        """Generate pytest-compatible test file content."""
        module_path = self._path_to_module(source_path)

        lines = [
            '"""',
            f"Auto-generated tests for {source_path.name}",
            f"Generated: {datetime.now().isoformat()}",
            "By: TestGeneratorAgent v2.0.0",
            '"""',
            "import pytest",
            "from unittest.mock import MagicMock, patch, AsyncMock",
            "",
        ]

        # Add import for the module
        if module_path:
            class_names = ", ".join(c["name"] for c in classes)
            lines.append(f"from {module_path} import {class_names}")
        lines.append("")
        lines.append("")

        # Generate test class for each source class
        for cls in classes:
            lines.extend(self._generate_test_class(cls))
            lines.append("")

        return "\n".join(lines)

    def _generate_test_class(self, cls: dict[str, Any]) -> list[str]:
        """Generate test class for a source class."""
        lines = [
            f"class Test{cls['name']}:",
            f'    """Tests for {cls["name"]}."""',
            "",
        ]

        # Add fixture
        lines.extend(
            [
                "    @pytest.fixture",
                "    def instance(self):",
                '        """Create test instance."""',
                f"        return {cls['name']}()",
                "",
            ]
        )

        # Generate test for each method
        for method in cls["methods"]:
            lines.extend(self._generate_test_method(cls, method))
            lines.append("")

        # Add mixin-specific tests
        if cls["has_healer_mixin"]:
            lines.extend(self._generate_healer_tests(cls))

        if cls["has_mcp_mixin"]:
            lines.extend(self._generate_mcp_tests(cls))

        return lines

    def _generate_test_method(self, cls: dict[str, Any], method: dict[str, Any]) -> list[str]:
        """Generate test method for a source method."""
        test_name = f"test_{method['name']}"

        if method["is_async"]:
            lines = [
                "    @pytest.mark.asyncio",
                f"    async def {test_name}(self, instance):",
                f'        """Test {method["name"]} method."""',
            ]

            # Generate mock args
            args = ", ".join("MagicMock()" for _ in method["args"])
            call = f"await instance.{method['name']}({args})"

            if method["has_return"]:
                lines.append(f"        result = {call}")
                lines.append("        assert result is not None")
            else:
                lines.append(f"        {call}  # Should not raise")
        else:
            lines = [
                f"    def {test_name}(self, instance):",
                f'        """Test {method["name"]} method."""',
            ]

            args = ", ".join("MagicMock()" for _ in method["args"])
            call = f"instance.{method['name']}({args})"

            if method["has_return"]:
                lines.append(f"        result = {call}")
                lines.append("        assert result is not None")
            else:
                lines.append(f"        {call}  # Should not raise")

        return lines

    def _generate_healer_tests(self, cls: dict[str, Any]) -> list[str]:
        """Generate tests for HealerMixin compliance."""
        return [
            "    def test_has_heal_repository(self, instance):",
            '        """Verify HealerMixin compliance."""',
            "        assert hasattr(instance, 'heal_repository')",
            "        assert callable(instance.heal_repository)",
            "",
            "    def test_heal_repository_returns_dict(self, instance):",
            '        """Verify heal_repository returns proper structure."""',
            "        result = instance.heal_repository(dry_run=True)",
            "        assert isinstance(result, dict)",
            "",
        ]

    def _generate_mcp_tests(self, cls: dict[str, Any]) -> list[str]:
        """Generate tests for MCPHardenedMixin compliance."""
        return [
            "    def test_has_mcp_validate(self, instance):",
            '        """Verify MCPHardenedMixin compliance."""',
            "        assert hasattr(instance, 'validate_mcp_response') or hasattr(instance, 'mcp_validate')",
            "",
        ]

    def _path_to_module(self, path: Path) -> str | None:
        """Convert file path to Python module path."""
        try:
            parts = path.with_suffix("").parts
            # Find agentic_core or tests in path
            for i, part in enumerate(parts):
                if part in ("agentic_core", "tests", "apps_rg", "apps_lic", "apps_shared"):
                    return ".".join(parts[i:])
            return None
        except Exception:
            return None

    def get_generation_history(self) -> list[dict[str, Any]]:
        """Retrieve history of generated tests."""
        return self._generated_tests.copy()

    @standard_heal
    def heal_repository(self, dry_run: bool = True, **kwargs) -> dict[str, int]:
        """Invoke healing chain via super()."""
        return super().heal_repository(dry_run=dry_run, **kwargs)
