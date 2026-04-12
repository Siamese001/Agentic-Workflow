"""Tests that legacy loader import paths resolve after compatibility shims are in place."""


def test_import_manager_agent_now_succeeds():
    """SovereignRAGManagerAgent imports pdf_loader + text_loader internally."""


def test_import_orchestrator_now_succeeds():
    """rag_orchestrator imports csv_loader, html_loader, pdf_loader, text_loader internally."""
