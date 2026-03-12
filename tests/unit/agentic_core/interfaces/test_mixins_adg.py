"""ADG-driven tests for agentic_core/interfaces/mixins.py — fan_in=5.

Contract tests: HealerMixin and MetaLearningMixin must be importable,
have correct types, and gracefully degrade to stubs when deps unavailable.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestMixinsPublicAPI:
    def test_all_exports_present(self):
        import agentic_core.interfaces.mixins as m
        for name in m.__all__:
            assert hasattr(m, name), f"Missing __all__ member: {name}"

    def test_healer_mixin_importable(self):
        from agentic_core.interfaces.mixins import HealerMixin
        assert HealerMixin is not None

    def test_meta_learning_mixin_importable(self):
        from agentic_core.interfaces.mixins import MetaLearningMixin
        assert MetaLearningMixin is not None

    def test_healer_mixin_is_class(self):
        from agentic_core.interfaces.mixins import HealerMixin
        assert isinstance(HealerMixin, type)

    def test_meta_learning_mixin_is_class(self):
        from agentic_core.interfaces.mixins import MetaLearningMixin
        assert isinstance(MetaLearningMixin, type)


class TestMixinsShimBehavior:
    """Stub or canonical — both are acceptable; module must not raise on import."""

    def test_healer_mixin_instantiable_as_base(self):
        from agentic_core.interfaces.mixins import HealerMixin

        class ConcreteAgent(HealerMixin):
            pass

        obj = ConcreteAgent()
        assert isinstance(obj, HealerMixin)

    def test_meta_learning_mixin_instantiable_as_base(self):
        from agentic_core.interfaces.mixins import MetaLearningMixin

        class ConcreteAgent(MetaLearningMixin):
            pass

        obj = ConcreteAgent()
        assert isinstance(obj, MetaLearningMixin)

    def test_both_mixins_can_be_combined(self):
        from agentic_core.interfaces.mixins import HealerMixin, MetaLearningMixin

        class FullAgent(HealerMixin, MetaLearningMixin):
            pass

        obj = FullAgent()
        assert isinstance(obj, HealerMixin)
        assert isinstance(obj, MetaLearningMixin)
