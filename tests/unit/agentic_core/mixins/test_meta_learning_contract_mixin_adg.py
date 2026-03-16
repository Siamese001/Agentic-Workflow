"""ADG-driven tests for mixins/meta_learning_contract_mixin.py — fan_in=1."""
from __future__ import annotations

import inspect

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

_emit_records_execution_trace("p0", "evidence", "test_meta_learning_contract_mixin_adg")
_emit_applies_guardrail("p0", "test_meta_learning_contract_mixin_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_meta_learning_contract_mixin_adg", "policy_binding")
_emit_snapshots_state("p0", "test_meta_learning_contract_mixin_adg", "state_snapshot")
emit_replay_key("p0", "test_meta_learning_contract_mixin_adg")
emit_determinism_digest("p0", "test_meta_learning_contract_mixin_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
