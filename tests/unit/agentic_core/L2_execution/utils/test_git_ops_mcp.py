"""Smoke tests for git_ops_mcp exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestGitOpsMcp:
    """Smoke tests for git_ops_mcp exports."""

    def test_git_ops_mcp_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "git_ops_mcp")
        assert module is not None

    def test_git_ops_mcp_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "GitOpsMcp")
        assert klass is not None

    def test_git_ops_mcp_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_git_ops_mcp")
        assert callable(validator)
