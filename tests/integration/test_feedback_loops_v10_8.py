import asyncio
from copy import deepcopy
from typing import Any, Dict

import pytest

from agent_orchestration_v10_7 import (
    run_prepare_hil_drafting_reentry,
    run_prepare_hil_strategy_reentry,
)
from core_v10_7 import SelfCorrectionManager
from stacks_v10_8 import DraftOrchestratorStack, RAGOrchestratorStack


class _StubPlanning:
    def __init__(self, patch: Dict[str, Any]):
        self.patch = patch
        self.calls = 0

    async def run_async(self, *_args, **_kwargs) -> Dict[str, Any]:
        self.calls += 1
        return deepcopy(self.patch)


class _StubRAGExecution:
    def __init__(self) -> None:
        self.calls = 0

    async def run_async(self, state: Dict[str, Any], *_args, **_kwargs) -> Dict[str, Any]:
        self.calls += 1
        if self.calls == 1:
            return {"resume": {"experience_bullets": []}, "rag": {"metadata": {"call": self.calls}}}
        return {"resume": {"experience_bullets": [{"id": "b1"}]}, "rag": {"metadata": {"call": self.calls}}}


class _StubBulletPlanning(_StubPlanning):
    pass


class _StubBulletExecution:
    def __init__(self) -> None:
        self.calls = 0

    async def run_async(self, *_args, **_kwargs) -> Dict[str, Any]:
        self.calls += 1
        return {"bullets": {"plan": {"target_sections": ["summary"]}, "generated_bullets": [{"id": "x"}]}}


class _StubDraftPlanning(_StubPlanning):
    pass


class _StubDraftExecution:
    def __init__(self) -> None:
        self.calls = 0

    async def run_async(self, *_args, **_kwargs) -> Dict[str, Any]:
        self.calls += 1
        status = "revise" if self.calls == 1 else "approved"
        sections = {"summary": {"draft": f"run-{self.calls}"}}
        critique = {"overall_status": status}
        return {
            "draft": {"sections": sections},
            "artifacts": {"artifacts": {"draft": {"critique": critique}}},
        }


@pytest.fixture()
def self_correction_enabled(workflow_context):
    manager = SelfCorrectionManager(workflow_context.config)
    manager.enabled = True
    manager.heuristics = {key: {"enable": True} for key in manager.heuristics}
    workflow_context.self_correction_manager = manager
    return workflow_context


@pytest.mark.asyncio
async def test_rag_orchestrator_emits_messages_and_retries(self_correction_enabled):
    context = self_correction_enabled
    orchestrator = RAGOrchestratorStack(context)
    orchestrator._planning = _StubPlanning({"rag": {"plan": {"goal": "evidence", "use_hyde": True, "retrieval_queries": ["a"]}}})
    orchestrator._execution = _StubRAGExecution()

    state = {"metadata": {"workflow_id": "wf-rag"}}
    result = await orchestrator.run_async(state, "wf-rag")

    messages = [m["message_type"] for m in result["a2a"]["messages"]]
    assert {"PLAN_CREATED", "EXECUTION_STARTED", "EXECUTION_COMPLETED", "RETRY_TRIGGERED"}.issubset(set(messages))
    assert result["resume"]["experience_bullets"], "RAG retry did not repopulate bullets"
    assert "prompt_rag_join" in result.get("arbitration", {}), "Arbitration report missing"
    reports = context.self_correction_manager.latest_reports("wf-rag", "rag")
    assert len(reports) == 1


@pytest.mark.asyncio
async def test_draft_orchestrator_hil_drafting_path_and_retry(self_correction_enabled):
    context = self_correction_enabled
    orchestrator = DraftOrchestratorStack(context)
    orchestrator._bullet_planning = _StubBulletPlanning({"bullets": {"plan": {"target_sections": ["summary"]}}})
    orchestrator._bullet_execution = _StubBulletExecution()
    orchestrator._draft_planning = _StubDraftPlanning({"draft": {"plan": {"structure": ["summary"]}}})
    orchestrator._draft_execution = _StubDraftExecution()

    state = {
        "metadata": {"workflow_id": "wf-draft"},
        "hil": {"next_step": "DRAFTING"},
        "bullets": {"generated_bullets": [{"id": "existing"}]},
        "draft": {"sections": {"summary": {"draft": "old"}}},
    }
    result = await orchestrator.run_async(state, "wf-draft")

    assert orchestrator._bullet_planning.calls == 0
    assert orchestrator._bullet_execution.calls == 0
    message_types = [m["message_type"] for m in result["a2a"]["messages"]]
    assert "DRAFT_RETRY_TRIGGERED" in message_types
    assert result["draft"]["sections"]["summary"]["draft"].startswith("run-"), "Draft sections not refreshed"
    assert "draft_post_assembly" in result.get("arbitration", {}), "Draft arbitration missing"
    reports = context.self_correction_manager.latest_reports("wf-draft", "drafting")
    assert len(reports) == 1


@pytest.mark.asyncio
async def test_hil_reentry_nodes_emit_signals(self_correction_enabled):
    context = self_correction_enabled
    state = {"metadata": {"workflow_id": "wf-hil"}, "hil": {"next_step": "STRATEGY"}}

    updated = await run_prepare_hil_strategy_reentry(state, context)
    assert updated["hil"]["next_step"] == "STRATEGY"
    assert updated["metadata"]["retries"]["hil_retries"] == 1
    assert any(m["message_type"] == "HIL_REENTRY_STRATEGY" for m in updated["a2a"]["messages"])

    updated = await run_prepare_hil_drafting_reentry(updated, context)
    assert updated["hil"]["next_step"] == "DRAFTING"
    assert updated["metadata"]["retries"]["hil_retries"] == 2
    assert any(m["message_type"] == "HIL_REENTRY_DRAFTING" for m in updated["a2a"]["messages"])
