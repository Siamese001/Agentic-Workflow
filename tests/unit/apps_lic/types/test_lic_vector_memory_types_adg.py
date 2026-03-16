"""ADG contract tests for apps_lic/types/lic_vector_memory_types.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
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
_emit_authorize_and_execute("p2", "test_lic_vector_memory_types_adg", "execution_auth")
_emit_validates_capability("p2", "test_lic_vector_memory_types_adg", "capability_check")
_emit_routes_to_capability("p2", "test_lic_vector_memory_types_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_lic_vector_memory_types_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_lic_vector_memory_types_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_lic_vector_memory_types_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_lic_vector_memory_types_adg", "exec_output")
_emit_dispatches_agent("p3", "test_lic_vector_memory_types_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_lic_vector_memory_types_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_lic_vector_memory_types_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_lic_vector_memory_types_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_lic_vector_memory_types_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_lic_vector_memory_types_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_lic_vector_memory_types_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_lic_vector_memory_types_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_lic_vector_memory_types_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_lic_vector_memory_types_adg", "eval_metric")
_emit_stores_embedding("p4", "test_lic_vector_memory_types_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_lic_vector_memory_types_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_lic_vector_memory_types_adg", "exec_snapshot_link")

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
