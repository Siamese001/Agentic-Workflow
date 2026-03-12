"""ADG-driven tests for L5_safety/utils/location_utils_util.py — fan_in=1."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.utils.location_utils_util import (
    get_agent_files,
    normalize_location_path,
)


class TestNormalizeLocationPath:
    def test_forward_slashes(self):
        result = normalize_location_path("foo/bar/baz.py")
        assert "\\" not in result

    def test_handles_backslashes(self):
        result = normalize_location_path("foo\\bar\\baz.py")
        assert "\\" not in result

    def test_returns_string(self):
        result = normalize_location_path("foo/bar")
        assert isinstance(result, str)

    def test_simple_path_unchanged(self):
        result = normalize_location_path("foo.py")
        assert result == "foo.py"


class TestGetAgentFiles:
    def test_returns_list(self, tmp_path):
        result = get_agent_files(str(tmp_path))
        assert isinstance(result, list)

    def test_finds_py_files(self, tmp_path):
        (tmp_path / "test_agent.py").write_text("# agent", encoding="utf-8")
        result = get_agent_files(str(tmp_path))
        assert any("test_agent.py" in f for f in result)

    def test_excludes_dunder_files(self, tmp_path):
        (tmp_path / "__init__.py").write_text("", encoding="utf-8")
        result = get_agent_files(str(tmp_path))
        assert not any("__init__.py" in f for f in result)

    def test_empty_directory(self, tmp_path):
        result = get_agent_files(str(tmp_path))
        assert result == []
