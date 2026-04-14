"""Behavioral tests for agentic_core/utils/project_root_util.py hardening changes."""

from __future__ import annotations

from pathlib import Path


class TestGetProjectRootFunction:
    def test_is_callable(self):
        """get_project_root is callable."""
        from agentic_core.utils.project_root_util import get_project_root

        assert callable(get_project_root)

    def test_returns_path_with_git_dir(self):
        """get_project_root() returns a Path that contains a .git directory."""
        from agentic_core.utils.project_root_util import get_project_root

        root = get_project_root()
        assert (root / ".git").is_dir()

    def test_get_project_root_safe_returns_existing_path(self):
        """get_project_root_safe() returns a path that exists on disk."""
        from agentic_core.utils.project_root_util import get_project_root_safe

        root = get_project_root_safe()
        assert root.exists()


class TestValidatedRoot:
    def test_none_input_returns_none(self):
        """_validated_root(None) returns None without raising."""
        from agentic_core.utils.project_root_util import _validated_root

        assert _validated_root(None) is None

    def test_nonexistent_path_returns_none(self):
        """_validated_root with a non-existent path returns None (strict=True catches OSError)."""
        from agentic_core.utils.project_root_util import _validated_root

        result = _validated_root(Path("/this_path_absolutely_does_not_exist_abc_xyz_123"))
        assert result is None

    def test_valid_repo_root_returns_resolved_path(self):
        """_validated_root on the real project root returns the resolved path."""
        from agentic_core.utils.project_root_util import _validated_root, get_project_root

        root = get_project_root()
        result = _validated_root(root)
        assert result is not None
        assert result == root
