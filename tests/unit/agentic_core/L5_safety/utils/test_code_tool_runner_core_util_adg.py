"""Test CodeToolRunnerCoreUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCodeToolRunnerCoreUtilAdg:
    """Test CodeToolRunnerCoreUtilAdg functionality."""

    def test_code_tool_runner_core_util_adg_imports(self):
        """Test code_tool_runner_core_util_adg module imports."""
        from agentic_core import code_tool_runner_core_util_adg

        assert code_tool_runner_core_util_adg is not None

    def test_code_tool_runner_core_util_adg_class(self):
        """Test CodeToolRunnerCoreUtilAdg class exists."""
        from agentic_core import CodeToolRunnerCoreUtilAdg

        assert CodeToolRunnerCoreUtilAdg is not None

    def test_code_tool_runner_core_util_adg_callable(self):
        """Test code_tool_runner_core_util_adg functions are callable."""
        from agentic_core import validate_code_tool_runner_core_util_adg

        assert callable(validate_code_tool_runner_core_util_adg)
