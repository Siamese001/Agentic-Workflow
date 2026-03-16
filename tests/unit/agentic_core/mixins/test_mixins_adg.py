"""ADG-driven tests for agentic_core/mixins/ — fan_in batch.

Covers:
  agentic_core/mixins/mcp_hardened_mixin.py        fan_in=5
  agentic_core/mixins/subatomic_testing_mixin.py   fan_in=5
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

_emit_records_execution_trace("p0", "evidence", "test_mixins_adg")
_emit_applies_guardrail("p0", "test_mixins_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_mixins_adg", "policy_binding")
_emit_snapshots_state("p0", "test_mixins_adg", "state_snapshot")
emit_replay_key("p0", "test_mixins_adg")
emit_determinism_digest("p0", "test_mixins_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit


class TestMCPHardenedMixin:
    """mcp_hardened_mixin.py — backwards-compat shim over MCPOperationMixin."""

    def test_class_importable(self):
        from agentic_core.mixins.mcp_hardened_mixin import MCPHardenedMixin
        assert callable(MCPHardenedMixin)

    def test_snake_case_alias_importable(self):
        from agentic_core.mixins.mcp_hardened_mixin import mcp_hardened_mixin
        assert mcp_hardened_mixin is not None

    def test_is_subclass_of_mcp_operation_mixin(self):
        from agentic_core.mixins.mcp_hardened_mixin import MCPHardenedMixin
        from agentic_core.mixins.mcp_operation_mixin import MCPOperationMixin
        assert issubclass(MCPHardenedMixin, MCPOperationMixin)

    def test_instantiable(self):
        from agentic_core.mixins.mcp_hardened_mixin import MCPHardenedMixin
        obj = MCPHardenedMixin()
        assert isinstance(obj, MCPHardenedMixin)

    def test_alias_same_as_class(self):
        from agentic_core.mixins.mcp_hardened_mixin import MCPHardenedMixin, mcp_hardened_mixin
        assert mcp_hardened_mixin is MCPHardenedMixin

    def test_can_be_used_as_mixin(self):
        from agentic_core.mixins.mcp_hardened_mixin import MCPHardenedMixin

        class ConcreteAgent(MCPHardenedMixin):
            pass

        obj = ConcreteAgent()
        assert isinstance(obj, MCPHardenedMixin)


class TestSubatomicTestingMixin:
    """subatomic_testing_mixin.py — self-testing mixin for L2 agents."""

    def test_class_importable(self):
        from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin
        assert callable(SubatomicTestingMixin)

    def test_is_class(self):
        from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin
        assert isinstance(SubatomicTestingMixin, type)

    def test_instantiable(self):
        from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin
        obj = SubatomicTestingMixin()
        assert isinstance(obj, SubatomicTestingMixin)

    def test_can_be_used_as_mixin(self):
        from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin

        class ConcreteL2Agent(SubatomicTestingMixin):
            pass

        obj = ConcreteL2Agent()
        assert isinstance(obj, SubatomicTestingMixin)

    def test_module_importable_without_raising(self):
        import importlib
        mod = importlib.import_module("agentic_core.mixins.subatomic_testing_mixin")
        assert mod is not None
