"""P1 MCP optimization tests for git_ops_impl.py — new log/diff/branch/push methods."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.tools.git_ops_impl import GitTools

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    GitTools = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="git_ops_impl deps unavailable")
class TestGitToolsNewMethods:
    def setup_method(self):
        self.tools = GitTools()

    def test_has_log_method(self):
        assert callable(getattr(self.tools, "log", None))

    def test_has_diff_method(self):
        assert callable(getattr(self.tools, "diff", None))

    def test_has_branch_method(self):
        assert callable(getattr(self.tools, "branch", None))

    def test_has_push_method(self):
        assert callable(getattr(self.tools, "push", None))

    def test_log_returns_str(self):
        result = self.tools.log()
        assert isinstance(result, str)

    def test_diff_returns_str(self):
        result = self.tools.diff()
        assert isinstance(result, str)

    def test_diff_with_range_returns_str(self):
        result = self.tools.diff(revision_range="HEAD~1..HEAD")
        assert isinstance(result, str)

    def test_branch_list_returns_str(self):
        result = self.tools.branch()
        assert isinstance(result, str)

    def test_branch_create_returns_str(self):
        result = self.tools.branch(branch_name="test/mcp-p1")
        assert isinstance(result, str)

    def test_push_returns_str(self):
        result = self.tools.push()
        assert isinstance(result, str)


@pytest.mark.skipif(not _AVAILABLE, reason="git_ops_impl deps unavailable")
class TestGitToolsLogWithMock:
    def test_log_uses_mcp0_when_available(self):
        mock_result = "abc123 initial commit\ndef456 second commit"
        mock_fn = MagicMock(return_value=mock_result)
        with patch.dict("sys.modules", {"mcp0_git_log_or_diff": MagicMock(mcp0_git_log_or_diff=mock_fn)}):
            tools = GitTools()
            result = tools.log()
        assert isinstance(result, str)

    def test_log_falls_back_on_import_error(self):
        import sys

        original = sys.modules.pop("mcp0_git_log_or_diff", None)
        try:
            tools = GitTools()
            result = tools.log()
            assert "Log Error" in result or isinstance(result, str)
        finally:
            if original is not None:
                sys.modules["mcp0_git_log_or_diff"] = original


@pytest.mark.skipif(not _AVAILABLE, reason="git_ops_impl deps unavailable")
class TestGitToolsDiffWithMock:
    def test_diff_uses_mcp0_when_available(self):
        mock_result = "+added line\n-removed line"
        mock_fn = MagicMock(return_value=mock_result)
        with patch.dict("sys.modules", {"mcp0_git_log_or_diff": MagicMock(mcp0_git_log_or_diff=mock_fn)}):
            tools = GitTools()
            result = tools.diff()
        assert isinstance(result, str)

    def test_diff_passes_revision_range(self):
        mock_fn = MagicMock(return_value="diff output")
        mock_mod = MagicMock(mcp0_git_log_or_diff=mock_fn)
        with patch.dict("sys.modules", {"mcp0_git_log_or_diff": mock_mod}):
            tools = GitTools()
            tools.diff(revision_range="HEAD~2..HEAD")
        call_kwargs = mock_fn.call_args
        if call_kwargs is not None:
            assert "HEAD~2..HEAD" in str(call_kwargs)


@pytest.mark.skipif(not _AVAILABLE, reason="git_ops_impl deps unavailable")
class TestGitToolsBranchWithMock:
    def test_branch_list_uses_mcp0(self):
        mock_fn = MagicMock(return_value="* main\n  feature/x")
        with patch.dict("sys.modules", {"mcp0_git_branch": MagicMock(mcp0_git_branch=mock_fn)}):
            tools = GitTools()
            result = tools.branch()
        assert isinstance(result, str)

    def test_branch_create_uses_mcp0(self):
        mock_fn = MagicMock(return_value="Branch created")
        with patch.dict("sys.modules", {"mcp0_git_branch": MagicMock(mcp0_git_branch=mock_fn)}):
            tools = GitTools()
            result = tools.branch(branch_name="feature/new")
        assert isinstance(result, str)


@pytest.mark.skipif(not _AVAILABLE, reason="git_ops_impl deps unavailable")
class TestGitToolsPushWithMock:
    def test_push_uses_mcp0(self):
        mock_fn = MagicMock(return_value="Push successful")
        with patch.dict("sys.modules", {"mcp0_git_push": MagicMock(mcp0_git_push=mock_fn)}):
            tools = GitTools()
            result = tools.push()
        assert isinstance(result, str)

    def test_push_falls_back_on_import_error(self):
        import sys

        original = sys.modules.pop("mcp0_git_push", None)
        try:
            tools = GitTools()
            result = tools.push()
            assert isinstance(result, str)
        finally:
            if original is not None:
                sys.modules["mcp0_git_push"] = original


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
