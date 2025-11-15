import pytest
from types import MethodType

from core_v10_7 import (
    AdvancedMetaLearner,
    ConfigV10_7,
    GeneratedPrompts,
    MetricsCollector,
    StrategyPlan,
)
from stacks_v10_7.prompting import PromptEngineerAgent


@pytest.mark.asyncio
async def test_advanced_meta_learner_reports_when_enabled():
    config = ConfigV10_7("master_config_v10_7.json")
    metrics = MetricsCollector()
    learner = AdvancedMetaLearner(config=config, metrics=metrics)

    assert learner.enabled() is False

    config.meta_learning_advanced_config.enabled = True
    assert learner.enabled() is True
    assert learner.analyze("wf-meta") == {"prune_boost": True}


@pytest.mark.asyncio
async def test_prompt_stack_receives_meta_hints(workflow_context):
    workflow_context.config.meta_learning_advanced_config.enabled = True
    workflow_context.advanced_meta_learner.config.meta_learning_advanced_config.enabled = True

    agent = PromptEngineerAgent(workflow_context)

    strategy = StrategyPlan(
        strategy_name="Expansion",
        focus_areas=["impact"],
        key_achievements_to_highlight=["led growth"],
        tone="confident",
    )
    prompts = GeneratedPrompts(
        bullet_generation_prompt="Use quantified achievements.",
        critique_prompt="Surface issues",
        qa_prompts={"qa": "check"},
    )

    async def fake_execute(self, *_args, **_kwargs):
        return {"prompts": prompts}, prompts

    async def fake_self_correct(self, _strategy, _complexity, _workflow_id, base_result, _validated_output):
        return base_result

    agent._execute_prompt_engineer = MethodType(fake_execute, agent)
    agent._maybe_self_correct = MethodType(fake_self_correct, agent)

    state: dict = {}
    result = await agent.run_async(strategy, "simple", "wf-meta", state=state)

    assert state["meta_hints"]["prune_boost"] is True
    assert result["prompts"] == prompts
