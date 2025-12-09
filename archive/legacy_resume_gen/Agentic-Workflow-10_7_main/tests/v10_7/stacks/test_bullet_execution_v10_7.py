import pytest

from stacks_v10_8.bullet_execution import BulletExecutionStack


@pytest.mark.asyncio
async def test_generate_from_state_async_builds_expected_patch(workflow_context):
    state = {
        "metadata": {"workflow_id": "wf-bullets"},
        "prompts": {"prompts": {"bullet_generation_prompt": "Write impact bullets."}},
        "strategy": {
            "strategy_plan": {
                "strategy_name": "default",
                "focus_areas": ["impact"],
                "key_achievements_to_highlight": ["growth"],
                "tone": "Bold",
            }
        },
        "resume": {
            "experience_bullets": [
                {"id": "exp-1", "text": "Improved retention"},
                {"id": "exp-2", "text": "Cut churn"},
            ]
        },
    }
    stack = BulletExecutionStack(workflow_context)
    captured = {}

    async def fake_generate_async(prompt, experiences, strategy, workflow_id):
        captured["prompt"] = prompt
        captured["experiences"] = experiences
        captured["workflow_id"] = workflow_id
        captured["strategy_tone"] = strategy.tone if hasattr(strategy, "tone") else None
        return {"bullets": {"generated_bullets": experiences}}

    stack.generate_async = fake_generate_async  # type: ignore[assignment]
    patch = await stack.generate_from_state_async(state, "wf-bullets")

    assert captured["prompt"] == "Write impact bullets."
    assert captured["workflow_id"] == "wf-bullets"
    assert captured["strategy_tone"] == "Bold"
    assert patch["bullets"]["generated_bullets"] == state["resume"]["experience_bullets"][:3]


@pytest.mark.asyncio
async def test_critique_from_state_async_uses_generated_bullets(workflow_context):
    state = {
        "metadata": {"workflow_id": "wf-critique"},
        "prompts": {"prompts": {"critique_prompt": "Score bullets"}},
        "bullets": {
            "generated_bullets": [
                {"id": "b-1", "text": "Shipped features"},
                {"id": "b-2", "text": "Optimized ops"},
            ]
        },
    }
    stack = BulletExecutionStack(workflow_context)
    captured = {}

    async def fake_critique_async(bullets, critique_prompt, workflow_id):
        captured["bullets"] = bullets
        captured["prompt"] = critique_prompt
        captured["workflow_id"] = workflow_id
        return {"bullets": {"critiqued_bullets": bullets}}

    stack.critique_async = fake_critique_async  # type: ignore[assignment]
    patch = await stack.critique_from_state_async(state, None)

    assert captured["prompt"] == "Score bullets"
    assert captured["workflow_id"] == "wf-critique"
    assert patch["bullets"]["critiqued_bullets"] == state["bullets"]["generated_bullets"]
