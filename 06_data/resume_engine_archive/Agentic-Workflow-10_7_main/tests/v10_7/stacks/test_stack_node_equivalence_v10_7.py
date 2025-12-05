import json

import pytest

from agent_stacks_v10_8 import (
    BulletExecutionStack,
    HILStackV10_8,
    SafetyStackV10_8,
)
from stacks_v10_8.drafting_execution import DraftingExecutionStack


@pytest.mark.asyncio
async def test_bullet_generation_helper_matches_node_inputs(workflow_context, monkeypatch):
    state = {
        "metadata": {"workflow_id": "wf-helpers"},
        "prompts": {"prompts": {"bullet_generation_prompt": "Write impact bullets"}},
        "resume": {
            "experience_bullets": [
                {"id": "exp-1"},
                {"id": "exp-2"},
                {"id": "exp-3"},
                {"id": "exp-4"},
            ]
        },
        "strategy": {
            "strategy_plan": {
                "strategy_name": "default",
                "focus_areas": ["impact"],
                "key_achievements_to_highlight": ["growth"],
                "tone": "bold",
            }
        },
    }
    stack = BulletExecutionStack(workflow_context)
    captured = {}

    async def fake_generate(prompt, experiences, strategy, workflow_id):
        captured["prompt"] = prompt
        captured["experiences"] = experiences
        captured["strategy"] = strategy
        captured["workflow_id"] = workflow_id
        return {"bullets": {"generated_bullets": [{"id": "b1"}]}}

    monkeypatch.setattr(stack, "generate_async", fake_generate)

    patch = await stack.generate_from_state_async(state, "wf-helpers")

    assert patch["bullets"]["generated_bullets"] == [{"id": "b1"}]
    assert captured["prompt"] == "Write impact bullets"
    assert len(captured["experiences"]) == 3  # sliced to top 3
    assert captured["workflow_id"] == "wf-helpers"


@pytest.mark.asyncio
async def test_bullet_critique_helper_matches_node_inputs(workflow_context, monkeypatch):
    state = {
        "metadata": {"workflow_id": "wf-critique"},
        "prompts": {"prompts": {"critique_prompt": "Rate bullets"}},
        "bullets": {"generated_bullets": [{"text": "Delivered impact"}]},
    }
    stack = BulletExecutionStack(workflow_context)
    captured = {}

    async def fake_critique(bullets, prompt, workflow_id):
        captured["bullets"] = bullets
        captured["prompt"] = prompt
        captured["workflow_id"] = workflow_id
        return {"bullets": {"critiqued_bullets": [{"text": "Delivered impact"}]}}

    monkeypatch.setattr(stack, "critique_async", fake_critique)

    patch = await stack.critique_from_state_async(state, "wf-critique")

    assert patch["bullets"]["critiqued_bullets"][0]["text"] == "Delivered impact"
    assert captured["prompt"] == "Rate bullets"
    assert captured["workflow_id"] == "wf-critique"


@pytest.mark.asyncio
async def test_constitutional_review_helper_follows_fallbacks(workflow_context, monkeypatch):
    state = {
        "metadata": {"workflow_id": "wf-constitution"},
        "draft": {
            "sections": {
                "summary": {
                    "draft": {"text": "final summary"},
                }
            }
        },
    }
    stack = SafetyStackV10_8(workflow_context)
    captured = {}

    async def fake_review(draft_text, workflow_id):
        captured["draft"] = json.loads(draft_text)
        captured["workflow_id"] = workflow_id
        class Result:
            def model_dump(self):
                return {"status": "ok"}
        return Result()

    monkeypatch.setattr(stack, "run_constitutional_review_async", fake_review)

    patch = await stack.constitutional_review_from_state_async(state, "wf-constitution")

    assert patch["qa"]["constitutional_review"] == {"status": "ok"}
    assert captured["draft"] == {"text": "final summary"}
    assert captured["workflow_id"] == "wf-constitution"


@pytest.mark.asyncio
async def test_hil_inject_helper_builds_summary_patch(workflow_context):
    state = {
        "metadata": {"workflow_id": "wf-hil"},
        "hil": {
            "payload": "Rewrite summary",
            "reconciliation": {"integrated_text": "merged summary"},
        },
        "draft": {"sections": {"summary": {"draft": "original"}}},
    }
    stack = HILStackV10_8(workflow_context)

    patch = await stack.inject_edit_from_state_async(state, "wf-hil")

    summary = patch["draft"]["sections"]["summary"]
    assert summary["draft"] == "merged summary"


@pytest.mark.asyncio
async def test_drafting_helper_routes_through_orchestrator(workflow_context, monkeypatch):
    calls = {}

    class DummyOrchestrator:
        def __init__(self, context, debug_mode=False):
            calls["context"] = context
            calls["debug_mode"] = debug_mode

        async def run_async(self, state, workflow_id, state_snapshot=None):
            calls["state"] = state
            calls["workflow_id"] = workflow_id
            calls["snapshot"] = state_snapshot
            return {"draft": {"sections": {"summary": {"draft": "ok"}}}}

    monkeypatch.setattr(
        "stacks_v10_8.draft_orchestration.DraftOrchestratorStack",
        DummyOrchestrator,
    )

    stack = DraftingExecutionStack(workflow_context)
    state = {"metadata": {"workflow_id": "wf-draft"}}
    result = await stack.run_from_state_async(state, "wf-draft")

    assert result["draft"]["sections"]["summary"]["draft"] == "ok"
    assert calls["snapshot"] is state
    assert calls["workflow_id"] == "wf-draft"
