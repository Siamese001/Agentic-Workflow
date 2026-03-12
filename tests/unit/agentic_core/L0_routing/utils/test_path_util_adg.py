"""ADG-driven tests for agentic_core/L0_routing/utils/path_util.py — fan_in=5.

Pure path utility functions with no governance logic.
Tests cover validate_path_within_project, safe_path_join, safe_prefixed_filename,
validate_no_duplicate_prefix, is_path_allowed, get_python_files.
"""
from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.utils.path_util import (
    is_path_allowed,
    safe_path_join,
    safe_prefixed_filename,
    validate_no_duplicate_prefix,
    validate_path_within_project,
)


class TestAllExports:
    def test_all_exports_present(self):
        import agentic_core.L0_routing.utils.path_util as m
        for name in m.__all__:
            assert hasattr(m, name), f"Missing __all__ member: {name}"


class TestValidatePathWithinProject:
    def test_path_inside_root_returns_true(self, tmp_path):
        sub = tmp_path / "subdir" / "file.py"
        sub.parent.mkdir(parents=True)
        sub.touch()
        assert validate_path_within_project(sub, project_root=tmp_path) is True

    def test_path_outside_root_returns_false(self, tmp_path):
        other = tmp_path.parent / "outside.py"
        assert validate_path_within_project(other, project_root=tmp_path) is False

    def test_root_itself_is_valid(self, tmp_path):
        assert validate_path_within_project(tmp_path, project_root=tmp_path) is True

    def test_string_path_accepted(self, tmp_path):
        sub = tmp_path / "x.py"
        sub.touch()
        assert validate_path_within_project(str(sub), project_root=tmp_path) is True


class TestSafePathJoin:
    def test_joins_within_root(self, tmp_path):
        result = safe_path_join(tmp_path, "subdir", "file.py")
        assert result == (tmp_path / "subdir" / "file.py").resolve()

    def test_raises_on_traversal_outside_root(self, tmp_path):
        with pytest.raises(ValueError, match="SAFETY VIOLATION"):
            safe_path_join(tmp_path, "..", "..", "etc", "passwd")

    def test_returns_path_object(self, tmp_path):
        result = safe_path_join(tmp_path, "a.py")
        assert isinstance(result, Path)


class TestSafePrefixedFilename:
    def test_adds_prefix_when_missing(self):
        result = safe_prefixed_filename("agent.py", "Test")
        assert result == "TestAgent.py" or result == "Testagent.py" or result.startswith("Test")

    def test_no_duplicate_prefix(self):
        result = safe_prefixed_filename("TestAgent.py", "Test")
        assert result == "TestAgent.py"

    def test_already_prefixed_unchanged(self):
        assert safe_prefixed_filename("MyFile.py", "My") == "MyFile.py"

    def test_adds_prefix_to_plain_name(self):
        assert safe_prefixed_filename("agent.py", "Test") == "Testagent.py"


class TestValidateNoDuplicatePrefix:
    def test_no_duplicate_returns_true(self):
        assert validate_no_duplicate_prefix("TestAgent.py", "Test") is True

    def test_duplicate_prefix_returns_false(self):
        assert validate_no_duplicate_prefix("TestTestAgent.py", "Test") is False

    def test_non_matching_prefix_returns_true(self):
        assert validate_no_duplicate_prefix("anything.py", "Xyz") is True


class TestIsPathAllowed:
    def test_path_in_allowed_dir_returns_true(self):
        allowed = frozenset({"agentic_core", "apps_lic"})
        assert is_path_allowed("agentic_core/L0/foo.py", allowed) is True

    def test_path_not_in_allowed_returns_false(self):
        allowed = frozenset({"agentic_core"})
        assert is_path_allowed("system_learning/foo.py", allowed) is False

    def test_nested_path_matched(self):
        allowed = frozenset({"tests"})
        assert is_path_allowed("/repo/tests/unit/foo.py", allowed) is True


class TestGetPythonFiles:
    def test_yields_py_files(self, tmp_path):
        from agentic_core.L0_routing.utils.path_util import get_python_files
        (tmp_path / "a.py").touch()
        (tmp_path / "b.py").touch()
        (tmp_path / "c.txt").touch()
        files = list(get_python_files(tmp_path))
        names = {f.name for f in files}
        assert "a.py" in names
        assert "b.py" in names
        assert "c.txt" not in names

    def test_excludes_specified_dirs(self, tmp_path):
        from agentic_core.L0_routing.utils.path_util import get_python_files
        excluded = tmp_path / "__pycache__"
        excluded.mkdir()
        (excluded / "cached.py").touch()
        (tmp_path / "real.py").touch()
        files = list(get_python_files(tmp_path, exclude_dirs=frozenset({"__pycache__"})))
        names = {f.name for f in files}
        assert "real.py" in names
        assert "cached.py" not in names
