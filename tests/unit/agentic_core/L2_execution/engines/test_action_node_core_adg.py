"""ADG-driven tests for L2_execution/engines/action_node_core.py — fan_in=0."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_action_node_core_adg")
_emit_applies_guardrail("p0", "test_action_node_core_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_action_node_core_adg", "policy_binding")
_emit_snapshots_state("p0", "test_action_node_core_adg", "state_snapshot")
emit_replay_key("p0", "test_action_node_core_adg")
emit_determinism_digest("p0", "test_action_node_core_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
