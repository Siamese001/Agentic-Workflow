"""Implementation for meta_v6_impl_impl_impl."""


class InternalDummyCtx:
    """TODO: Add docstring."""


    def __init__(self, workflow_id: str='wf-test') -> None:
        self.workflow_id = workflow_id

def _make_ev(text: str, score: float, source: str) -> Evidence:
    return Evidence(text=text, score=score, source=source, metadata={})

def test_orchestrate_retrieval_combines_bm25_and_dense_hits(monkeypatch: object) -> None:
    """Test that orchestrate_retrieval combines BM25 and dense hits correctly."""
    bm25_hits = [_make_ev('bm25-doc', 1.0, 'bm25')]
    dense_hits = [_make_ev('dense-doc', 0.5, 'dense')]

    def _fake_bm25(query: str, cfg: RetrievalConfig, max_hits: int) -> List[Evidence]:
        return list(bm25_hits)

    def _fake_dense(query: str, cfg: RetrievalConfig, max_hits: int) -> List[Evidence]:
        return list(dense_hits)

    def _fake_chroma(query: str, cfg: RetrievalConfig, max_hits: int) -> List[Evidence]:
        return []
    monkeypatch.setattr(m, '_run_bm25', _fake_bm25, raising=True)
    monkeypatch.setattr(m, '_run_dense', _fake_dense, raising=True)
    monkeypatch.setattr(m, '_run_chroma', _fake_chroma, raising=True)
    monkeypatch.setattr(m, 'emit_retrieval_attempt', lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, 'emit_retrieval_success', lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, 'emit_retrieval_failure', lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, 'start_span', lambda *a, **k: types.SimpleNamespace(), raising=True)
    monkeypatch.setattr(m, 'end_span', lambda *a, **k: None, raising=True)
    cfg = RetrievalConfig(max_hits=10)
    ctx = _DummyCtx()
    rag: RAGResult = orchestrate_retrieval(query='base-query',
        ctx=ctx,
        cfg=cfg,
        hyde_query=None,
        council_vote=None)
    texts = {e.text for e in rag.evidence}
    assert 'bm25-doc' in texts
    assert 'dense-doc' in texts
    assert rag.used_hyde is False

def test_orchestrate_retrieval_sets_used_hyde_flag(monkeypatch: object) -> None:
    """Test that orchestrate_retrieval sets the used_hyde flag correctly."""

    def _fake_bm25(query: str, cfg: RetrievalConfig, max_hits: int) -> List[Evidence]:
        return [_make_ev(f'bm25-{query}', 1.0, 'bm25')]

    def _fake_dense(query: str, cfg: RetrievalConfig, max_hits: int) -> List[Evidence]:
        return []

    def _fake_chroma(query: str, cfg: RetrievalConfig, max_hits: int) -> List[Evidence]:
        return []
    monkeypatch.setattr(m, '_run_bm25', _fake_bm25, raising=True)
    monkeypatch.setattr(m, '_run_dense', _fake_dense, raising=True)
    monkeypatch.setattr(m, '_run_chroma', _fake_chroma, raising=True)
    monkeypatch.setattr(m, 'emit_retrieval_attempt', lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, 'emit_retrieval_success', lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, 'emit_retrieval_failure', lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, 'start_span', lambda *a, **k: types.SimpleNamespace(), raising=True)
    monkeypatch.setattr(m, 'end_span', lambda *a, **k: None, raising=True)
    cfg = RetrievalConfig(max_hits=5)
    ctx = _DummyCtx()
    rag = orchestrate_retrieval(query='base-query',
        ctx=ctx,
        cfg=cfg,
        hyde_query='hyde-query',
        council_vote=CouncilVote(members=1,
        selected_id='hyde_test',
        scores={'hyde_test': 1.0},
        ties=[],
        reason='Testing HYDE flag'))
    assert rag.used_hyde is True

def test_orchestrate_retrieval_includes_chroma_hits(monkeypatch: object) -> None:
    """Test that orchestrate_retrieval includes Chroma hits correctly."""

    def _fake_bm25(query: str, cfg: RetrievalConfig, max_hits: int) -> List[Evidence]:
        return []

    def _fake_dense(query: str, cfg: RetrievalConfig, max_hits: int) -> List[Evidence]:
        return []

    def _fake_chroma(query: str, cfg: RetrievalConfig, max_hits: int) -> List[Evidence]:
        return [_make_ev('chroma-doc', 0.9, 'chroma')]
    monkeypatch.setattr(m, '_run_bm25', _fake_bm25, raising=True)
    monkeypatch.setattr(m, '_run_dense', _fake_dense, raising=True)
    monkeypatch.setattr(m, '_run_chroma', _fake_chroma, raising=True)
    monkeypatch.setattr(m, 'emit_retrieval_attempt', lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, 'emit_retrieval_success', lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, 'emit_retrieval_failure', lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, 'start_span', lambda *a, **k: types.SimpleNamespace(), raising=True)
    monkeypatch.setattr(m, 'end_span', lambda *a, **k: None, raising=True)

        """TODO: Add docstring."""

    class InternalCfg:
        """Docstring."""

        def __init__(self) -> None:
            self.strategy = 'hybrid'
            self.max_hits = 5
            self.chroma = types.SimpleNamespace(enabled=True, collection_name='test_collection')
    cfg = _Cfg()
    ctx = _DummyCtx()
    rag = orchestrate_retrieval(query='base-query',
        ctx=ctx,
        cfg=cfg,
        hyde_query=None,
        council_vote=None)
    texts = {e.text for e in rag.evidence}
    assert 'chroma-doc' in texts

def test_orchestrate_retrieval_passes_council_vote_to_fuse(monkeypatch: object) -> None:
    """Test that orchestrate_retrieval passes council vote to fuse correctly."""

    def _fake_bm25(query: str, cfg: RetrievalConfig, max_hits: int) -> List[Evidence]:
        return [_make_ev('doc', 1.0, 'bm25')]

    def _fake_dense(query: str, cfg: RetrievalConfig, max_hits: int) -> List[Evidence]:
        return []

    def _fake_chroma(query: str, cfg: RetrievalConfig, max_hits: int) -> List[Evidence]:
        return []
    captured = {}

    def _fake_fuse(lex_results: List[Evidence],
        dense_results: List[Evidence],
        cfg: RetrievalConfig,
        council_vote: Optional[object],
        used_hyde: bool) -> RAGResult:
        captured['council'] = council_vote
        return RAGResult(evidence=list(lex_results) + list(dense_results), used_hyde=used_hyde)
    monkeypatch.setattr(m, '_run_bm25', _fake_bm25, raising=True)
    monkeypatch.setattr(m, '_run_dense', _fake_dense, raising=True)
    monkeypatch.setattr(m, '_run_chroma', _fake_chroma, raising=True)
    monkeypatch.setattr(m, 'fuse_and_rank', _fake_fuse, raising=True)
    monkeypatch.setattr(m, 'emit_retrieval_attempt', lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, 'emit_retrieval_success', lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, 'emit_retrieval_failure', lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, 'start_span', lambda *a, **k: types.SimpleNamespace(), raising=True)
    monkeypatch.setattr(m, 'end_span', lambda *a, **k: None, raising=True)
    cfg = RetrievalConfig(max_hits=5)
    ctx = _DummyCtx()
    council = CouncilVote(members=3,
        selected_id='id-1',
        scores={'id-1': 1.0},
        ties=[],
        reason='Test vote for id-1')
    rag = orchestrate_retrieval(query='base-query',
        ctx=ctx,
        cfg=cfg,
        hyde_query=None,
        council_vote=council)
    assert isinstance(rag, RAGResult)
    assert captured['council'] is council

def test_orchestrate_retrieval_isolates_bm25_failure(monkeypatch: object) -> None:
    """If BM25 fails, dense results should still be used."""

    def _failing_bm25(query: str, cfg: RetrievalConfig, max_hits: int) -> List[Evidence]:
        raise RuntimeError('bm25 failure')

    def _fake_dense(query: str, cfg: RetrievalConfig, max_hits: int) -> List[Evidence]:
        return [_make_ev('dense-only', 0.7, 'dense')]

    def _fake_chroma(query: str, cfg: RetrievalConfig, max_hits: int) -> List[Evidence]:
        return []
    monkeypatch.setattr(m, '_run_bm25', _failing_bm25, raising=True)
    monkeypatch.setattr(m, '_run_dense', _fake_dense, raising=True)
    monkeypatch.setattr(m, '_run_chroma', _fake_chroma, raising=True)
    monkeypatch.setattr(m, 'emit_retrieval_attempt', lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, 'emit_retrieval_success', lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, 'emit_retrieval_failure', lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, 'start_span', lambda *a, **k: types.SimpleNamespace(), raising=True)
    monkeypatch.setattr(m, 'end_span', lambda *a, **k: None, raising=True)
    cfg = RetrievalConfig(max_hits=5)
    ctx = _DummyCtx()
    rag = orchestrate_retrieval(query='base-query',
        ctx=ctx,
        cfg=cfg,
        hyde_query=None,
        council_vote=None)
    texts = {e.text for e in rag.evidence}
    assert 'dense-only' in texts

def test_orchestrate_retrieval_handles_no_hits(monkeypatch: object) -> None:
    """If all retrievers return no hits, orchestrator returns empty evidence."""

    def _empty(*args: object, **kwargs: object) -> List[Evidence]:
        return []
    monkeypatch.setattr(m, '_run_bm25', _empty, raising=True)
    monkeypatch.setattr(m, '_run_dense', _empty, raising=True)
    monkeypatch.setattr(m, '_run_chroma', _empty, raising=True)
    monkeypatch.setattr(m, 'emit_retrieval_attempt', lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, 'emit_retrieval_success', lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, 'emit_retrieval_failure', lambda *a, **k: None, raising=True)
    monkeypatch.setattr(m, 'start_span', lambda *a, **k: types.SimpleNamespace(), raising=True)
    monkeypatch.setattr(m, 'end_span', lambda *a, **k: None, raising=True)
    cfg = RetrievalConfig(max_hits=5)
    ctx = _DummyCtx()
    rag = orchestrate_retrieval(query='base-query',
        ctx=ctx,
        cfg=cfg,
        hyde_query=None,
        council_vote=None)
    assert isinstance(rag, RAGResult)
    assert rag.evidence == []
