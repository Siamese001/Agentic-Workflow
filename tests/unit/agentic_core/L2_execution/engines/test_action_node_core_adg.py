"""ADG-driven tests for L2_execution/engines/action_node_core.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.engines.action_node_core import ActionNodeCore


class TestActionNodeCore:
    def test_has_tool_map(self):
        assert isinstance(ActionNodeCore.TOOL_MAP, dict)
        assert "read_file" in ActionNodeCore.TOOL_MAP

    def test_creates(self, tmp_path):
        core = ActionNodeCore(work_dir=str(tmp_path), allowed_tools={})
        assert core is not None

    def test_work_dir_resolved(self, tmp_path):
        core = ActionNodeCore(work_dir=str(tmp_path), allowed_tools={})
        assert core.work_dir.is_absolute()
