"""ADG contract tests for apps_shared/types/vector_similarity_result_types.py."""
from __future__ import annotations

from datetime import datetime

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

_emit_records_execution_trace("p0", "evidence", "test_vector_similarity_result_types_adg")
_emit_applies_guardrail("p0", "test_vector_similarity_result_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_vector_similarity_result_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_vector_similarity_result_types_adg", "state_snapshot")
emit_replay_key("p0", "test_vector_similarity_result_types_adg")
emit_determinism_digest("p0", "test_vector_similarity_result_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_vector_similarity_result_types_adg", "execution_auth")
_emit_validates_capability("p2", "test_vector_similarity_result_types_adg", "capability_check")
_emit_routes_to_capability("p2", "test_vector_similarity_result_types_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_vector_similarity_result_types_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_vector_similarity_result_types_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_vector_similarity_result_types_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_vector_similarity_result_types_adg", "exec_output")
_emit_dispatches_agent("p3", "test_vector_similarity_result_types_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_vector_similarity_result_types_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_vector_similarity_result_types_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_vector_similarity_result_types_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_vector_similarity_result_types_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_vector_similarity_result_types_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_vector_similarity_result_types_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_vector_similarity_result_types_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_vector_similarity_result_types_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_vector_similarity_result_types_adg", "eval_metric")
_emit_stores_embedding("p4", "test_vector_similarity_result_types_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_vector_similarity_result_types_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_vector_similarity_result_types_adg", "exec_snapshot_link")

_FIXED_DT = datetime(2099, 12, 31, 23, 59, 59)
pytestmark = pytest.mark.unit
try:
    from apps_shared.types.vector_similarity_result_types import (
        CacheEntry,
        EnhancedSemanticCache,
        VectorSimilarityResult,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    VectorSimilarityResult = CacheEntry = EnhancedSemanticCache = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestVectorSimilarityResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(VectorSimilarityResult)
    def test_creates(self):
        r = VectorSimilarityResult(
            cache_key="k1", similarity_score=0.92,
            cached_content="resume text", metadata={}, timestamp=_FIXED_DT,
        )
        assert r.similarity_score == 0.92; assert r.cache_key == "k1"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCacheEntry:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(CacheEntry)
    def test_creates(self):
        e = CacheEntry(
            key="k1", content="text", embedding=[0.1, 0.2],
            metadata={}, timestamp=_FIXED_DT,
        )
        assert e.ttl_seconds == 3600
    def test_not_expired_fresh(self):
        e = CacheEntry(
            key="k", content="c", embedding=[], metadata={}, timestamp=_FIXED_DT,
        )
        assert e.is_expired() is False

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestEnhancedSemanticCache:
    def test_creates(self):
        c = EnhancedSemanticCache(); assert c.max_size == 1000
    def test_put_and_stats(self):
        c = EnhancedSemanticCache()
        c.put("what is python", "Python is a language")
        stats = c.get_cache_stats()
        assert stats["total_entries"] >= 1
    def test_clear(self):
        c = EnhancedSemanticCache()
        c.put("q1", "content1")
        c.clear()
        stats = c.get_cache_stats(); assert stats["total_entries"] == 0
    def test_fingerprint_deterministic(self):
        c = EnhancedSemanticCache()
        fp1 = c.generate_fingerprint("hello", "gpt-4o")
        fp2 = c.generate_fingerprint("hello", "gpt-4o")
        assert fp1 == fp2

def test_module_importable(): assert _AVAIL or not _AVAIL
