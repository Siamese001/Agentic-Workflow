"""ADG-driven tests for L5_safety/validators/PascalSovereigntyAgent.py — fan_in=1."""
from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.validators.PascalSovereigntyAgent import (
    PascalSovereigntyAgent,
    get_python_files_fast,
)


class TestGetPythonFilesFast:
    def test_returns_list(self, tmp_path):
        result = get_python_files_fast(tmp_path)
        assert isinstance(result, list)

    def test_finds_py_files(self, tmp_path):
        (tmp_path / "foo_agent.py").write_text("# agent", encoding="utf-8")
        result = get_python_files_fast(tmp_path)
        assert any(f.name == "foo_agent.py" for f in result)

    def test_empty_dir_returns_empty(self, tmp_path):
        result = get_python_files_fast(tmp_path)
        assert result == []


class TestPascalSovereigntyAgent:
    def test_creates(self):
        agent = PascalSovereigntyAgent()
        assert agent is not None

    def test_has_heal_repository(self):
        assert hasattr(PascalSovereigntyAgent, "heal_repository")

    def test_is_class(self):
        assert isinstance(PascalSovereigntyAgent, type)
