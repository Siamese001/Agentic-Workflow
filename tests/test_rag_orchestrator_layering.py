"""Tests for the RAG orchestrator thin-layer behavior."""
from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from rag_orchestration import RAGOrchestratorStack


def test_rag_orchestrator_applies_patches_without_mutation():
    context = SimpleNamespace(config=SimpleNamespace(agent_stacks=SimpleNamespace()))
    orchestrator = RAGOrchestratorStack(context)
    orchestrator._planner.run_async = AsyncMock(return_value={"rag": {"plan": {"goal": "goal"}}})
    orchestrator._execution.run_async = AsyncMock(return_value={"rag": {"results": [{"status": "ok"}]}})

    initial_state = {"metadata": {"workflow_id": "wf"}, "rag": {}}
    baseline_copy = {"metadata": {"workflow_id": "wf"}, "rag": {}}
    patch = asyncio.run(orchestrator.run_async(initial_state))

    assert initial_state == baseline_copy
    assert "a2a" in patch
    orchestrator._planner.run_async.assert_awaited_once()
    orchestrator._execution.run_async.assert_awaited()
    assert not hasattr(orchestrator, "log_feedback")
