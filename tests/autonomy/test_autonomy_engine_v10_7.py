import logging
from types import MethodType, SimpleNamespace

import pytest

from core_v10_7.services import AutonomyEngine
from agent_stacks_v10_8.components.drafting import DraftingGuildCoordinator


class _DummyMetrics:
    def record(self, *_, **__):
        return None

    def get_average_latency(self, *_, **__):
        return None


def _build_agent(agent_cls, context):
    agent = agent_cls.__new__(agent_cls)
    agent.context = context
    agent.config = context.config
    agent.logger = logging.getLogger(agent_cls.__name__)
    agent.debug_mode = False
    agent.prompt_manager = context.prompt_manager
    agent.validator = context.response_validator
    agent.budget_manager = context.context_budget_manager
    agent.metrics = context.metrics_collector
    agent.self_correction_manager = None
    return agent


def test_autonomy_disabled_noop():
    config = SimpleNamespace(autonomy_config=SimpleNamespace(enabled=False))
    engine = AutonomyEngine(config=config, metrics=None)

    assert engine.enabled() is False
    assert engine.decide("wf-0") == {}


def test_autonomy_generates_routing_hints_from_signals():
    events = [
        {"event": "rag_iteration"},
        {"event": "qa_validation"},
    ]
    episodic_memory = SimpleNamespace(get=lambda _workflow_id: {"events": events})
    config = SimpleNamespace(autonomy_config=SimpleNamespace(enabled=True))
    engine = AutonomyEngine(config=config, metrics=None, episodic_memory=episodic_memory)

    hints = engine.decide("wf-123")

    assert hints["rag_branch_factor"] == 2
    assert hints["qa_temperature_bias"] == -0.1


@pytest.mark.asyncio
async def test_autonomy_injected_into_stacks_without_breakage():
    class _StubAutonomy:
        def __init__(self):
            self.calls = []

        def enabled(self):
            return True

        def decide(self, workflow_id):
            self.calls.append(workflow_id)
            return {"drafting_override": True}

    predictive_cfg = SimpleNamespace(enabled=False, max_background_tasks=0)
    config = SimpleNamespace(
        predictive_caching_config=predictive_cfg,
        auto_tuning_config=SimpleNamespace(enabled=False),
        agent_stacks=SimpleNamespace(conductor_max_steps=1),
    )
    context = SimpleNamespace(
        config=config,
        predictive_cache_manager=SimpleNamespace(
            enabled=lambda: False,
            schedule=lambda *_: None,
            run_scheduled=lambda: None,
        ),
        precompute_engine=SimpleNamespace(),
        metrics_collector=_DummyMetrics(),
        prompt_manager=SimpleNamespace(goal_state="", top_failures="", get_template=lambda *_: ""),
        response_validator=SimpleNamespace(),
        context_budget_manager=SimpleNamespace(),
        self_correction_manager=None,
        is_mcp_enabled=lambda: False,
        ensure_mcp_clients=lambda: {},
        policy_auto_tuner=SimpleNamespace(enabled=lambda: False),
        tuning_profile=SimpleNamespace(),
        episodic_memory=None,
        autonomy_engine=_StubAutonomy(),
    )

    agent = _build_agent(DraftingGuildCoordinator, context)

    async def fake_execute(self, task_context, workflow_id, overrides=None):
        return {"final_output": {}}, {}

    async def fake_self_correct(self, task_context, workflow_id, base_result, meta):
        return base_result

    agent._execute_guild = MethodType(fake_execute, agent)
    agent._maybe_self_correct = MethodType(fake_self_correct, agent)

    state = {"metadata": {"workflow_id": "wf-test"}}
    task_context = {"bullets": [], "strategy": {}, "resume": {}}

    result = await agent.run_async(task_context, "wf-test", state=state)

    assert result == {"final_output": {}}
    assert state["autonomy_hints"]["drafting_override"] is True
