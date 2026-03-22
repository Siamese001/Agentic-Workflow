"""Tests that legacy loader import paths resolve after compatibility shims are in place."""

import importlib

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
