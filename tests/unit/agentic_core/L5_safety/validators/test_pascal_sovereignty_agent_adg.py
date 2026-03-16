"""ADG-driven tests for L5_safety/validators/PascalSovereigntyAgent.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_pascal_sovereignty_agent_adg")
_emit_applies_guardrail("p0", "test_pascal_sovereignty_agent_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_pascal_sovereignty_agent_adg", "policy_binding")
_emit_snapshots_state("p0", "test_pascal_sovereignty_agent_adg", "state_snapshot")
emit_replay_key("p0", "test_pascal_sovereignty_agent_adg")
emit_determinism_digest("p0", "test_pascal_sovereignty_agent_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
