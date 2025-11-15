"""Draft orchestrator layering tests."""
from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from draft_orchestration import DraftOrchestratorStack


def test_draft_orchestrator_runs_stacks_once():
    context = SimpleNamespace(config=SimpleNamespace(agent_stacks=SimpleNamespace()))
    orchestrator = DraftOrchestratorStack(context)
    orchestrator._bullet_planning.run_async = AsyncMock(return_value={"bullets": {"plan": {"target_sections": [1]}}})
    orchestrator._bullet_execution.run_async = AsyncMock(return_value={"bullets": {"generated": []}})
    orchestrator._draft_planning.run_async = AsyncMock(return_value={"draft": {"plan": {"sections": ["summary"]}}})
    orchestrator._draft_execution.run_async = AsyncMock(return_value={"draft": {"sections": {"summary": "text"}}})

    base_state = {"metadata": {"workflow_id": "wf"}, "draft": {}}
    snapshot = {"metadata": {"workflow_id": "wf"}, "draft": {}}

    patch = asyncio.run(orchestrator.run_async(base_state))
    assert base_state == snapshot
    assert patch["draft"]["sections"]["summary"] == "text"
    orchestrator._bullet_planning.run_async.assert_awaited_once()
    orchestrator._bullet_execution.run_async.assert_awaited_once()
    orchestrator._draft_planning.run_async.assert_awaited_once()
    orchestrator._draft_execution.run_async.assert_awaited_once()
    assert not hasattr(orchestrator, "log_feedback")
