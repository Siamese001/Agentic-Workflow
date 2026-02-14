"""End-to-end import contract: RAG orchestrator + manager + all loader shims resolve."""


def test_rag_import_contract_no_side_effects(monkeypatch):
    """Full RAG import graph resolves without triggering external clients."""
    # Prevent any provider client initialization on import
    monkeypatch.setenv("PINECONE_API_KEY", "")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("GOOGLE_API_KEY", "")

    # --- Orchestrator + Manager modules import cleanly ---
    import agentic_core.knowledge.engine.rag_orchestrator as ro
    import agentic_core.knowledge.reasoning.SovereignRAGManagerAgent as rm

    assert hasattr(ro, "SovereignRagOrchestrator")
    assert hasattr(rm, "SovereignRAGManager")

    # --- All legacy loader shims resolve ---
    from agentic_core.knowledge.document_loaders.csv_loader import CSVDocumentLoader
    from agentic_core.knowledge.document_loaders.html_loader import HTMLDocumentLoader
    from agentic_core.knowledge.document_loaders.pdf_loader import PDFDocumentLoader
    from agentic_core.knowledge.document_loaders.text_loader import TextDocumentLoader

    assert CSVDocumentLoader is not None
    assert PDFDocumentLoader is not None
    assert TextDocumentLoader is not None
    assert HTMLDocumentLoader is not None

    # --- ResearchCache shim resolves to canonical ---
    from agentic_core.knowledge.document_loaders.research_cache import ResearchCache as A
    from agentic_core.knowledge.research_cache.cache_store_util import ResearchCache as B

    assert A is B
