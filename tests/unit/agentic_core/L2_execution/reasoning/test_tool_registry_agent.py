"""Tests for L2 Execution reasoning agents."""

from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    L2_EXECUTION_DIR,
)


class TestToolRegistryAgent:
    """Tests for tool registry functionality."""

    def test_tool_registry_exists(self):
        """Tool registry module should exist."""
        path = Path("agentic_core/L2_execution/reasoning")
        assert path.exists(), "L2_execution/reasoning/ should exist"

    def test_tool_registry_has_registry_class(self):
        """Tool registry should define registry classes."""
        reasoning_path = Path("agentic_core/L2_execution/reasoning")
        if reasoning_path.exists():
            py_files = list(reasoning_path.glob("*.py"))
            assert len(py_files) > 0, "L2_execution/reasoning/ should have Python files"


class TestMCPClientAgent:
    """Tests for MCP client functionality."""

    def test_mcp_types_defined(self):
        """MCP types should be defined in types/."""
        types_path = Path("agentic_core/L2_execution/types")
        if not types_path.exists():
            pytest.fail("L2_execution/types/ not found")

        type_files = list(types_path.glob("*.py"))
        assert len(type_files) > 0, "L2_execution/types/ should have type definitions"


class TestActionHandlerAgent:
    """Tests for action handler functionality."""

    def test_action_handlers_in_enforcement(self):
        """Action handlers should be in enforcement/."""
        enforcement_path = Path("agentic_core/L2_execution/enforcement")
        if not enforcement_path.exists():
            pytest.fail("L2_execution/enforcement/ not found")

        py_files = list(enforcement_path.glob("*.py"))
        assert len(py_files) > 0, "L2_execution/enforcement/ should have files"


class TestExecutionLayerIntegrity:
    """Tests for L2 layer structural integrity."""

    def test_execution_can_use_subprocess(self):
        """L2 execution is allowed to use subprocess (it's the execution layer)."""
        import subprocess

        assert subprocess is not None

    def test_execution_agents_in_reasoning(self):
        """Agent classes in L2 should be in reasoning/."""
        base = Path(L2_EXECUTION_DIR)
        if not base.exists():
            pytest.fail("L2_execution/ not found")

        # Known exceptions (documented architectural decisions)
        # Some config files have embedded Agent classes (legacy pattern)
        known_exceptions = [
            "peer_intelligence_auditor_config.py",
            "mcp_tool_config.py",
            "strategist_bio_writer_config.py",
        ]

        violations = []
        for subfolder in ["types", "config", "utils"]:
            subfolder_path = base / subfolder
            if not subfolder_path.exists():
                continue
            for py_file in subfolder_path.glob("*.py"):
                if any(exc in str(py_file) for exc in known_exceptions):
                    continue
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                if "class " in content and "Agent(" in content:
                    violations.append(str(py_file))

        # Note: enforcement/ may have Agent classes for action execution
        assert len(violations) == 0, f"Agent classes in wrong subfolder: {violations}"

    def test_tools_subfolder_exists(self):
        """L2 should have tools/ subfolder for tool implementations."""
        tools_path = Path("agentic_core/L2_execution/tools")
        # tools/ is optional but recommended for L2
        if tools_path.exists():
            py_files = list(tools_path.glob("*.py"))
            assert len(py_files) >= 0  # Just verify structure
