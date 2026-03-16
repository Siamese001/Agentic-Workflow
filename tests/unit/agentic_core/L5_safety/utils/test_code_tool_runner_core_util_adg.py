"""ADG-driven tests for agentic_core/L5_safety/utils/code_tool_runner_core_util.py — fan_in=2.

Contract tests: CodeToolRunnerCapability API surface and importability.
"""
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

_emit_records_execution_trace("p0", "evidence", "test_code_tool_runner_core_util_adg")
_emit_applies_guardrail("p0", "test_code_tool_runner_core_util_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_code_tool_runner_core_util_adg", "policy_binding")
_emit_snapshots_state("p0", "test_code_tool_runner_core_util_adg", "state_snapshot")
emit_replay_key("p0", "test_code_tool_runner_core_util_adg")
emit_determinism_digest("p0", "test_code_tool_runner_core_util_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.utils.code_tool_runner_core_util import CodeToolRunnerCapability


class TestCodeToolRunnerCapabilityImport:
    def test_class_importable(self):
        assert callable(CodeToolRunnerCapability)


class TestCodeToolRunnerCapabilityInterface:
    def test_is_capability_mixin(self):
        assert hasattr(CodeToolRunnerCapability, "execute")
        assert hasattr(CodeToolRunnerCapability, "heal_repository")
        assert hasattr(CodeToolRunnerCapability, "heal")

    def test_execute_is_abstract(self):
        """execute() raises NotImplementedError unless overridden."""
        import asyncio

        cap = CodeToolRunnerCapability()
        with pytest.raises(NotImplementedError):
            asyncio.run(cap.execute("dummy.py"))

    def test_subclass_can_override_execute(self):
        import asyncio

        class ConcreteRunner(CodeToolRunnerCapability):
            async def execute(self, file_path: str):
                return {"status": "ok", "file": file_path}

        runner = ConcreteRunner()
        result = asyncio.run(runner.execute("test.py"))
        assert result["status"] == "ok"
        assert result["file"] == "test.py"

    def test_no_sovereign_base_agent_inheritance(self):
        """Capability is pure — must NOT inherit SovereignBaseAgent."""
        mro_names = [c.__name__ for c in CodeToolRunnerCapability.__mro__]
        assert "SovereignBaseAgent" not in mro_names
