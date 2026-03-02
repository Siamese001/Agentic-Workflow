"""Tests that legacy loader import paths resolve after compatibility shims are in place."""

import importlib


def test_import_manager_agent_now_succeeds():
    """SovereignRAGManagerAgent imports pdf_loader + text_loader internally."""
    mod = importlib.import_module(
        "agentic_core.knowledge.reasoning.SovereignRAGManagerAgent",
    )
    assert hasattr(mod, "SovereignRAGManager")


def test_import_orchestrator_now_succeeds():
    """rag_orchestrator imports csv_loader, html_loader, pdf_loader, text_loader internally."""
    from agentic_core.knowledge.engine.rag_orchestrator import SovereignRagOrchestrator

    assert SovereignRagOrchestrator is not None
