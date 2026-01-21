from __future__ import annotations

# import archives.legacy_resume_gen.Agentic_Workflow-10_10.l4.types  # INVALID: Cannot import from path with hyphens

# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.tests.test_retrieval import orchestrate_retrieval  # INVALID: Cannot import from path with hyphens
# from archives.legacy_root_folders.core.models.models import Evidence, RetrievalConfig, CouncilVote, RAGResult  # DEPRECATED: Archive import removed to protect archives from validation edits


class _DummyCtx:
    def __init__(self, workflow_id: str = "wf-test") -> None:
        self.workflow_id = workflow_id


def _make_ev(text: str, score: float, source: str) -> Evidence:
    return Evidence(text=text, score=score, source=source, metadata={})


def test_orchestrate_retrieval_combines_bm25_and_dense_hits(monkeypatch: object) -> None:
    """Test that orchestrate_retrieval combines BM25 and dense hits correctly."""
    # Arrange
#     import archives.legacy_resume_gen.Agentic-Workflow-10_8_core.tests.test_retrieval  # INVALID: Cannot import from path with hyphens

    bm25_hits = [_make_ev("bm25-doc", 1.0, "bm25")]
    dense_hits = [_make_ev("dense-doc", 0.5, "dense")]

    def _fake_bm25(query: str, cfg: RetrievalConfig, max_hits: int) -> list[Evidence]:  # noqa: ARG001
        return list(bm25_hits)

    def _fake_dense(query: str, cfg: RetrievalConfig, max_hits: int) -> list[Evidence]:  # noqa: ARG001
        return list(dense_hits)

    def _fake_chroma(query: str, cfg: RetrievalConfig, max_hits: int) -> list[Evidence]:  # noqa: ARG001
        return []

    # No-op telemetry
    monkeypatch.setattr(m, "_run_bm25", _fake_bm25, raising=True)
    monkeypatch.setattr(m, "_run_dense", _fake_dense, raising=True)
    monkeypatch.setattr(m, "_run_chroma", _fake_chroma, raising=True)
    monkeypatch.setattr(m, "emit_retrieval_attempt", lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, "emit_retrieval_success", lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, "emit_retrieval_failure", lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, "start_span", lambda *a, **k: types.SimpleNamespace(), raising=True)
    monkeypatch.setattr(m, "end_span", lambda *a, **k: None, raising=True)

    cfg = RetrievalConfig(max_hits=10)
    ctx = _DummyCtx()

    # Act
    rag: RAGResult = orchestrate_retrieval(
        query="base-query",
        ctx=ctx,
        cfg=cfg,
        hyde_query=None,
        council_vote=None,
    )

    # Assert
    texts = {e.text for e in rag.evidence}
    assert "bm25-doc" in texts
    assert "dense-doc" in texts
    assert rag.used_hyde is False


def test_orchestrate_retrieval_sets_used_hyde_flag(monkeypatch: object) -> None:
    """Test that orchestrate_retrieval sets the used_hyde flag correctly."""
#     import archives.legacy_resume_gen.Agentic-Workflow-10_8_core.tests.test_retrieval  # INVALID: Cannot import from path with hyphens

    def _fake_bm25(query: str, cfg: RetrievalConfig, max_hits: int) -> list[Evidence]:  # noqa: ARG001
        return [_make_ev(f"bm25-{query}", 1.0, "bm25")]

    def _fake_dense(query: str, cfg: RetrievalConfig, max_hits: int) -> list[Evidence]:  # noqa: ARG001
        return []

    def _fake_chroma(query: str, cfg: RetrievalConfig, max_hits: int) -> list[Evidence]:  # noqa: ARG001
        return []

    monkeypatch.setattr(m, "_run_bm25", _fake_bm25, raising=True)
    monkeypatch.setattr(m, "_run_dense", _fake_dense, raising=True)
    monkeypatch.setattr(m, "_run_chroma", _fake_chroma, raising=True)
    monkeypatch.setattr(m, "emit_retrieval_attempt", lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, "emit_retrieval_success", lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, "emit_retrieval_failure", lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, "start_span", lambda *a, **k: types.SimpleNamespace(), raising=True)
    monkeypatch.setattr(m, "end_span", lambda *a, **k: None, raising=True)

    cfg = RetrievalConfig(max_hits=5)
    ctx = _DummyCtx()

    rag = orchestrate_retrieval(
        query="base-query",
        ctx=ctx,
        cfg=cfg,
        hyde_query="hyde-query",
        council_vote=CouncilVote(
            members=1,
            selected_id="hyde_test",
            scores={"hyde_test": 1.0},
            ties=[],
            reason="Testing HYDE flag"
        ),
    )

    assert rag.used_hyde is True


def test_orchestrate_retrieval_includes_chroma_hits(monkeypatch: object) -> None:
    """Test that orchestrate_retrieval includes Chroma hits correctly."""
#     import archives.legacy_resume_gen.Agentic-Workflow-10_8_core.tests.test_retrieval  # INVALID: Cannot import from path with hyphens

    def _fake_bm25(query: str, cfg: RetrievalConfig, max_hits: int) -> list[Evidence]:  # noqa: ARG001
        return []

    def _fake_dense(query: str, cfg: RetrievalConfig, max_hits: int) -> list[Evidence]:  # noqa: ARG001
        return []

    def _fake_chroma(query: str, cfg: RetrievalConfig, max_hits: int) -> list[Evidence]:  # noqa: ARG001
        return [_make_ev("chroma-doc", 0.9, "chroma")]

    monkeypatch.setattr(m, "_run_bm25", _fake_bm25, raising=True)
    monkeypatch.setattr(m, "_run_dense", _fake_dense, raising=True)
    monkeypatch.setattr(m, "_run_chroma", _fake_chroma, raising=True)
    monkeypatch.setattr(m, "emit_retrieval_attempt", lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, "emit_retrieval_success", lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, "emit_retrieval_failure", lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, "start_span", lambda *a, **k: types.SimpleNamespace(), raising=True)
    monkeypatch.setattr(m, "end_span", lambda *a, **k: None, raising=True)

    class _Cfg:
        def __init__(self) -> None:
            self.strategy = "hybrid"
            self.max_hits = 5
            # Minimal object with the attributes orchestrate_retrieval checks.
            self.chroma = types.SimpleNamespace(enabled=True, collection_name="test_collection")

    cfg = _Cfg()
    ctx = _DummyCtx()

    rag = orchestrate_retrieval(
        query="base-query",
        ctx=ctx,
        cfg=cfg,
        hyde_query=None,
        council_vote=None,
    )

    texts = {e.text for e in rag.evidence}
    assert "chroma-doc" in texts


def test_orchestrate_retrieval_passes_council_vote_to_fuse(monkeypatch: object) -> None:
    """Test that orchestrate_retrieval passes council vote to fuse correctly."""
#     import archives.legacy_resume_gen.Agentic-Workflow-10_8_core.tests.test_retrieval  # INVALID: Cannot import from path with hyphens

    def _fake_bm25(query: str, cfg: RetrievalConfig, max_hits: int) -> list[Evidence]:  # noqa: ARG001
        return [_make_ev("doc", 1.0, "bm25")]

    def _fake_dense(query: str, cfg: RetrievalConfig, max_hits: int) -> list[Evidence]:  # noqa: ARG001
        return []

    def _fake_chroma(query: str, cfg: RetrievalConfig, max_hits: int) -> list[Evidence]:  # noqa: ARG001
        return []

    captured = {}

    def _fake_fuse(lex_results: list[Evidence], dense_results: list[Evidence], cfg: RetrievalConfig, council_vote: Optional[object], used_hyde: bool) -> RAGResult:  # noqa: ARG001
        captured["council"] = council_vote
        return RAGResult(evidence=list(lex_results) + list(dense_results), used_hyde=used_hyde)

    monkeypatch.setattr(m, "_run_bm25", _fake_bm25, raising=True)
    monkeypatch.setattr(m, "_run_dense", _fake_dense, raising=True)
    monkeypatch.setattr(m, "_run_chroma", _fake_chroma, raising=True)
    monkeypatch.setattr(m, "fuse_and_rank", _fake_fuse, raising=True)
    monkeypatch.setattr(m, "emit_retrieval_attempt", lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, "emit_retrieval_success", lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, "emit_retrieval_failure", lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, "start_span", lambda *a, **k: types.SimpleNamespace(), raising=True)
    monkeypatch.setattr(m, "end_span", lambda *a, **k: None, raising=True)

    cfg = RetrievalConfig(max_hits=5)
    ctx = _DummyCtx()
    council = CouncilVote(
        members=3,
        selected_id="id-1",
        scores={"id-1": 1.0},
        ties=[],
        reason="Test vote for id-1"
    )

    rag = orchestrate_retrieval(
        query="base-query",
        ctx=ctx,
        cfg=cfg,
        hyde_query=None,
        council_vote=council,
    )

    assert isinstance(rag, RAGResult)
    assert captured["council"] is council


def test_orchestrate_retrieval_isolates_bm25_failure(monkeypatch: object) -> None:
    """If BM25 fails, dense results should still be used."""

#     import archives.legacy_resume_gen.Agentic-Workflow-10_8_core.tests.test_retrieval  # INVALID: Cannot import from path with hyphens

    def _failing_bm25(query: str, cfg: RetrievalConfig, max_hits: int) -> list[Evidence]:  # noqa: ARG001
        raise RuntimeError("bm25 failure")

    def _fake_dense(query: str, cfg: RetrievalConfig, max_hits: int) -> list[Evidence]:  # noqa: ARG001
        return [_make_ev("dense-only", 0.7, "dense")]

    def _fake_chroma(query: str, cfg: RetrievalConfig, max_hits: int) -> list[Evidence]:  # noqa: ARG001
        return []

    monkeypatch.setattr(m, "_run_bm25", _failing_bm25, raising=True)
    monkeypatch.setattr(m, "_run_dense", _fake_dense, raising=True)
    monkeypatch.setattr(m, "_run_chroma", _fake_chroma, raising=True)
    monkeypatch.setattr(m, "emit_retrieval_attempt", lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, "emit_retrieval_success", lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, "emit_retrieval_failure", lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, "start_span", lambda *a, **k: types.SimpleNamespace(), raising=True)
    monkeypatch.setattr(m, "end_span", lambda *a, **k: None, raising=True)

    cfg = RetrievalConfig(max_hits=5)
    ctx = _DummyCtx()

    rag = orchestrate_retrieval(
        query="base-query",
        ctx=ctx,
        cfg=cfg,
        hyde_query=None,
        council_vote=None,
    )

    texts = {e.text for e in rag.evidence}
    assert "dense-only" in texts


def test_orchestrate_retrieval_handles_no_hits(monkeypatch: object) -> None:
    """If all retrievers return no hits, orchestrator returns empty evidence."""

#     import archives.legacy_resume_gen.Agentic-Workflow-10_8_core.tests.test_retrieval  # INVALID: Cannot import from path with hyphens

    def _empty(*args: object, **kwargs: object) -> list[Evidence]:  # type: ignore[override]
        return []

    monkeypatch.setattr(m, "_run_bm25", _empty, raising=True)
    monkeypatch.setattr(m, "_run_dense", _empty, raising=True)
    monkeypatch.setattr(m, "_run_chroma", _empty, raising=True)
    monkeypatch.setattr(m, "emit_retrieval_attempt", lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, "emit_retrieval_success", lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, "emit_retrieval_failure", lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, "start_span", lambda *a, **k: types.SimpleNamespace(), raising=True)
    monkeypatch.setattr(m, "end_span", lambda *a, **k: None, raising=True)

    cfg = RetrievalConfig(max_hits=5)
    ctx = _DummyCtx()

    rag = orchestrate_retrieval(
        query="base-query",
        ctx=ctx,
        cfg=cfg,
        hyde_query=None,
        council_vote=None,
    )

    assert isinstance(rag, RAGResult)
    assert rag.evidence == []
