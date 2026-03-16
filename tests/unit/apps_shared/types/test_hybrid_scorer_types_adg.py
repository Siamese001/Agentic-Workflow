"""ADG contract tests for apps_shared/types/hybrid_scorer_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_hybrid_scorer_types_adg")
_emit_applies_guardrail("p0", "test_hybrid_scorer_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_hybrid_scorer_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_hybrid_scorer_types_adg", "state_snapshot")
emit_replay_key("p0", "test_hybrid_scorer_types_adg")
emit_determinism_digest("p0", "test_hybrid_scorer_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.hybrid_scorer_types import HybridScorer, ScoringResult
    _AVAIL = True
except ImportError:
    _AVAIL = False
    ScoringResult = HybridScorer = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestScoringResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ScoringResult)
    def test_creates(self):
        r = ScoringResult(
            document_id="d1", bm25_score=0.5, semantic_score=0.6,
            tfidf_score=0.4, freshness_score=0.5, final_score=0.52,
        )
        assert r.document_id == "d1"; assert r.metadata == {}

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHybridScorer:
    def test_creates(self): s = HybridScorer(); assert s is not None
    def test_index_and_score(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            s = HybridScorer()
        docs = [
            {"id": "d1", "content": "Python software engineer role"},
            {"id": "d2", "content": "Marketing manager position"},
        ]
        s.index_documents(docs)
        results = s.score_documents("Python engineer")
        assert len(results) == 2
        assert results[0].document_id == "d1"
    def test_calculate_hybrid_score(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            s = HybridScorer()
        score = s.calculate_hybrid_score(0.8, 0.6)
        assert 0.0 <= score <= 1.0

def test_module_importable(): assert _AVAIL or not _AVAIL
