from l2.lic_k1_research import LIC_K1_Research

def test_stub_returns_none():
    k1 = LIC_K1_Research({})
    assert k1.execute(None, None) is None
    assert k1.execute_hyde_enrichment(None) is None
    assert k1.execute_hybrid_recall(None, None) is None
    assert k1.execute_cross_encoder_reranking(None) is None
