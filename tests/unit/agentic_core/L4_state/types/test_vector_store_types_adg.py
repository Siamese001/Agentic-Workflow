"""ADG-driven tests for L4 vector_store_types — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_vector_store_types_adg")
_emit_applies_guardrail("p0", "test_vector_store_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_vector_store_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_vector_store_types_adg", "state_snapshot")
emit_replay_key("p0", "test_vector_store_types_adg")
emit_determinism_digest("p0", "test_vector_store_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L4_state.types.vector_store_types import BaseVectorStore


class TestBaseVectorStore:
    def test_is_abstract(self):
        assert inspect.isabstract(BaseVectorStore)

    def test_has_initialize(self):
        assert hasattr(BaseVectorStore, "initialize")

    def test_has_upsert(self):
        assert hasattr(BaseVectorStore, "upsert")

    def test_has_query(self):
        assert hasattr(BaseVectorStore, "query")

    def test_has_delete(self):
        assert hasattr(BaseVectorStore, "delete")

    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            BaseVectorStore()  # type: ignore[abstract]

    def test_subclass_must_implement_all_methods(self):
        class ConcreteStore(BaseVectorStore):
            async def initialize(self): pass
            async def upsert(self, items): return True
            async def query(self, query): return []
            async def delete(self, item_ids): return True

        store = ConcreteStore()
        assert store is not None
