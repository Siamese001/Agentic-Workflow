"""ADG-driven tests for mixins/meta_learning_contract_mixin.py — fan_in=1."""
from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

from agentic_core.mixins.meta_learning_contract_mixin import BaseMetaLearner


class TestBaseMetaLearner:
    def test_is_abstract(self):
        assert inspect.isabstract(BaseMetaLearner)

    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            BaseMetaLearner()

    def test_has_recall_experience(self):
        assert hasattr(BaseMetaLearner, "recall_experience")

    def test_has_learn_experience(self):
        assert hasattr(BaseMetaLearner, "learn_experience")

    def test_has_recall_or_execute(self):
        assert hasattr(BaseMetaLearner, "recall_or_execute")

    def test_concrete_subclass_works(self):
        class ConcreteMetaLearner(BaseMetaLearner):
            @property
            def _namespace(self) -> str:
                return "test"

            def recall_experience(self, context):
                return None

            async def learn_experience(self, context, result):
                pass

            def recall_or_execute(self, context, execution_fn, **kwargs):
                return execution_fn()

        learner = ConcreteMetaLearner()
        assert learner._namespace == "test"
