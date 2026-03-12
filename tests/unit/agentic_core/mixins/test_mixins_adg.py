"""ADG-driven tests for agentic_core/mixins/ — fan_in batch.

Covers:
  agentic_core/mixins/mcp_hardened_mixin.py        fan_in=5
  agentic_core/mixins/subatomic_testing_mixin.py   fan_in=5
"""
from __future__ import annotations

import pytest

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
