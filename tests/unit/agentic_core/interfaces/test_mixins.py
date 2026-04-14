"""Behavioral tests for mixins.py: HealerMixin, MetaLearningMixin, _missing_dependency."""

from __future__ import annotations

import pytest


@pytest.mark.unit
class TestMixinsModule:
    # --- happy path ---

    def test_module_importable(self):
        from agentic_core.interfaces import mixins

        assert mixins is not None

    def test_exports_healer_mixin(self):
        from agentic_core.interfaces.mixins import HealerMixin

        assert HealerMixin is not None

    def test_exports_meta_learning_mixin(self):
        from agentic_core.interfaces.mixins import MetaLearningMixin

        assert MetaLearningMixin is not None

    # --- failure path ---

    def test_missing_dependency_raises_on_instantiation(self):
        from agentic_core.interfaces.mixins import _missing_dependency

        stub_cls = _missing_dependency("HealerMixin", "L5 module not found")
        with pytest.raises(ModuleNotFoundError, match="HealerMixin"):
            stub_cls()

    # --- edge case ---

    def test_missing_dependency_message_contains_reason(self):
        from agentic_core.interfaces.mixins import _missing_dependency

        stub_cls = _missing_dependency("MetaLearningMixin", "package x not installed")
        with pytest.raises(ModuleNotFoundError, match="package x not installed"):
            stub_cls()
