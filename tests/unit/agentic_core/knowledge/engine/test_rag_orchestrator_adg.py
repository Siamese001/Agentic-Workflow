"""ADG importability contract for agentic_core/knowledge/engine/rag_orchestrator.py."""
from __future__ import annotations

import agentic_core.knowledge.engine.rag_orchestrator  # noqa: F401


def test_module_importable():
    """Module rag_orchestrator must be importable."""
    assert agentic_core.knowledge.engine.rag_orchestrator is not None
