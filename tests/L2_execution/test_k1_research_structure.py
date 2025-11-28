import inspect
from l2.lic_k1_research import LIC_K1_Research

def test_class_exists():
    assert inspect.isclass(LIC_K1_Research)

def test_required_methods():
    required = [
        "execute",
        "execute_hyde_enrichment",
        "execute_hybrid_recall",
        "execute_cross_encoder_reranking",
        "execute_self_rag",
        "calculate_signal_quality",
    ]
    for m in required:
        assert hasattr(LIC_K1_Research, m)
