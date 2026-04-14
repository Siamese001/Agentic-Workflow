"""Behavioral tests for orchestration.py: ActionRouter export, _MissingOptionalDependency."""

from __future__ import annotations

import pytest


@pytest.mark.unit
class TestOrchestrationModule:
    # --- happy path ---

    def test_module_importable(self):
        from agentic_core.interfaces import orchestration

        assert orchestration is not None

    def test_exports_action_router(self):
        from agentic_core.interfaces.orchestration import ActionRouter

        assert ActionRouter is not None

    # --- failure path ---

    def test_missing_optional_dependency_call_raises(self):
        from agentic_core.interfaces.orchestration import _MissingOptionalDependency

        proxy = _MissingOptionalDependency("ActionRouter", "L3 not installed")
        with pytest.raises(ModuleNotFoundError, match="ActionRouter"):
            proxy()

    def test_missing_optional_dependency_getattr_raises(self):
        from agentic_core.interfaces.orchestration import _MissingOptionalDependency

        proxy = _MissingOptionalDependency("ActionRouter", "L3 not installed")
        with pytest.raises(ModuleNotFoundError, match="ActionRouter"):
            _ = proxy.route

    # --- edge case ---

    def test_missing_optional_dependency_reason_in_message(self):
        from agentic_core.interfaces.orchestration import _MissingOptionalDependency

        proxy = _MissingOptionalDependency("ActionRouter", "custom reason text")
        with pytest.raises(ModuleNotFoundError, match="custom reason text"):
            proxy()
