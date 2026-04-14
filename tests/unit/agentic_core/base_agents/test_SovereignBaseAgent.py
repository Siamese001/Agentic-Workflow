"""Tests for phase-hardened SovereignBaseAgent behaviors."""

from pathlib import Path

import pytest

from agentic_core.base_agents.SovereignBaseAgent import (
    ConfigurationError,
    SovereignError,
    SovereignBaseAgent,
    sanitize_tool_output,
)


@pytest.mark.unit
class TestSovereignBaseAgentHardening:
    """Behavioral coverage for phase-hardened SovereignBaseAgent."""

    def test_module_symbols_defined_at_module_level(self):
        """Happy: ConfigurationError, SovereignError, sanitize_tool_output are module-level names."""
        assert ConfigurationError is not None
        assert SovereignError is not None
        assert callable(sanitize_tool_output)

    def test_is_safe_path_accepts_child_of_project_root(self, tmp_path):
        """Happy: path inside project_root resolves True."""
        agent = SovereignBaseAgent(project_root=tmp_path)
        assert agent._is_safe_path(tmp_path / "subdir" / "file.py") is True

    def test_is_safe_path_rejects_path_outside_project_root(self, tmp_path):
        """Failure: path that escapes project_root resolves False."""
        agent = SovereignBaseAgent(project_root=tmp_path)
        assert agent._is_safe_path(tmp_path.parent) is False
