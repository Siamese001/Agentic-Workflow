"""ADG-driven tests for agentic_core/L5_safety/utils/code_tool_runner_core_util.py — fan_in=2.

Contract tests: CodeToolRunnerCapability API surface and importability.
"""
from __future__ import annotations

import pytest

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
