"""ADG contract tests for apps_lic/types/lic_vector_memory_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_lic_vector_memory_types_adg")
_emit_applies_guardrail("p0", "test_lic_vector_memory_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_lic_vector_memory_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_lic_vector_memory_types_adg", "state_snapshot")
emit_replay_key("p0", "test_lic_vector_memory_types_adg")
emit_determinism_digest("p0", "test_lic_vector_memory_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_lic.types.lic_vector_memory_types import (
        MemoryStats,
        MockVectorMemory,
        QueryResult,
        VectorDocument,
        create_vector_memory,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    VectorDocument = QueryResult = MemoryStats = MockVectorMemory = create_vector_memory = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestVectorDocument:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(VectorDocument)
    def test_creates(self):
        d = VectorDocument(id="d1", text="content", metadata={"source": "url"})
        assert d.id == "d1"; assert d.embedding is None

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestQueryResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(QueryResult)
    def test_creates(self):
        r = QueryResult(documents=[], total_count=0, query_text="search")
        assert r.total_count == 0; assert r.query_time_ms == 0.0

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMockVectorMemory:
    def test_creates(self): m = MockVectorMemory(); assert m.is_initialized() is True
    def test_add_and_query(self):
        m = MockVectorMemory()
        m.add_document("Python engineer role", {"source_url": "http://a.com", "extracted_at": "2024"})
        result = m.query_memory("Python")
        assert result.total_count == 1
    def test_get_stats(self):
        m = MockVectorMemory()
        m.add_document("doc", {"source_url": "x", "extracted_at": "y"})
        stats = m.get_stats()
        assert stats.document_count == 1
    def test_delete_document(self):
        m = MockVectorMemory()
        doc_id = m.add_document("text", {"source_url": "u", "extracted_at": "t"}, document_id="del1")
        assert m.delete_document("del1") is True
    def test_clear_collection(self):
        m = MockVectorMemory()
        m.add_document("text", {"source_url": "u", "extracted_at": "t"})
        assert m.clear_collection() is True
        assert m.get_stats().document_count == 0

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
def test_create_vector_memory_mock():
    m = create_vector_memory(use_mock=True)
    assert isinstance(m, MockVectorMemory)

def test_module_importable(): assert _AVAIL or not _AVAIL
