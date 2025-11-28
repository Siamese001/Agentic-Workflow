import logging
from types import MethodType, SimpleNamespace

import pytest

from core_v10_7.services import PolicyAutoTuner, PredictiveCacheManager, TuningProfile
from agent_stacks_v10_8.components.drafting import DraftingGuildCoordinator
from agent_stacks_v10_8.components.prompting import PromptEngineerAgent
from agent_stacks_v10_8.components.rag import RAG_SearchAgent


class DummyMetricsCollector:
    def __init__(self):
        self.records = []
        self.predictive_cache_manager = None

    def record(self, agent_name, task_name, duration_ms, success, error=None, metadata=None):
        self.records.append(
            {
                "agent": agent_name,
                "task": task_name,
                "duration_ms": duration_ms,
                "success": success,
                "error": error,
                "metadata": metadata or {},
            }
        )

    def get_average_latency(self, *_, **__):
        return None


class StubPrecomputeEngine:
    def __init__(self):
        self.embeddings_calls = []
        self.hyde_calls = []
        self.prompt_plan_calls = []

    async def precompute_embeddings(self, text):
        self.embeddings_calls.append(text)

    async def precompute_hyde_document(self, query):
        self.hyde_calls.append(query)

    async def precompute_prompt_plan(self, strategy_json, complexity):
        self.prompt_plan_calls.append((strategy_json, complexity))


def _make_context(enabled=True):
    predictive_cfg = SimpleNamespace(enabled=enabled, max_background_tasks=5)
    config = SimpleNamespace(
        predictive_caching_config=predictive_cfg,
        auto_tuning_config=SimpleNamespace(enabled=False),
    )
    metrics = DummyMetricsCollector()
    precompute_engine = StubPrecomputeEngine()
    pcm = PredictiveCacheManager(
        config=config,
        cache_manager=SimpleNamespace(),
        metrics=metrics,
    )
    metrics.predictive_cache_manager = pcm
    tuning_profile = TuningProfile()
    policy_auto_tuner = PolicyAutoTuner(config, metrics)
    context = SimpleNamespace(
        config=config,
        predictive_cache_manager=pcm,
        precompute_engine=precompute_engine,
        metrics_collector=metrics,
        prompt_manager=SimpleNamespace(goal_state="", top_failures="", get_template=lambda *_: ""),
        response_validator=SimpleNamespace(),
        context_budget_manager=SimpleNamespace(),
        self_correction_manager=None,
        is_mcp_enabled=lambda: False,
        ensure_mcp_clients=lambda: {},
        workflow_id="wf-test",
        complexity="complex",
        policy_auto_tuner=policy_auto_tuner,
        tuning_profile=tuning_profile,
    )
    return context, pcm, precompute_engine


def _build_agent(agent_cls, context):
    agent = agent_cls.__new__(agent_cls)
    agent.context = context
    agent.config = context.config
    agent.logger = logging.getLogger(agent_cls.__name__)
    agent.prompt_manager = context.prompt_manager
    agent.validator = context.response_validator
    agent.budget_manager = context.context_budget_manager
    agent.metrics = context.metrics_collector
    agent.self_correction_manager = None
    return agent


@pytest.mark.asyncio
async def test_predictive_disabled_noop():
    cfg = SimpleNamespace(predictive_caching_config=SimpleNamespace(enabled=False, max_background_tasks=1))
    pcm = PredictiveCacheManager(cfg, SimpleNamespace(), DummyMetricsCollector())
    called = False

    async def marker():
        nonlocal called
        called = True

    pcm.schedule({"coroutine": lambda: marker})
    await pcm.run_scheduled()
    assert pcm._queue == []
    assert called is False


@pytest.mark.asyncio
async def test_predictive_prefetch_embeddings():
    context, _, precompute_engine = _make_context(enabled=True)
    agent = _build_agent(RAG_SearchAgent, context)

    async def fake_execute(self, state, self_heal_hint=None):
        return {"resume": {}}, {}

    async def fake_self_correct(self, state, base_result, meta):
        return base_result

    agent._execute_rag = MethodType(fake_execute, agent)
    agent._maybe_self_correct = MethodType(fake_self_correct, agent)

    state = {"job": {"job_title": "Engineer", "company": "Acme"}, "metadata": {"workflow_id": "wf"}}
    result = await agent.run_async(state=state)

    assert result == {"resume": {}}
    assert precompute_engine.embeddings_calls == ["Engineer at Acme"]


@pytest.mark.asyncio
async def test_predictive_prefetch_hyde():
    context, _, precompute_engine = _make_context(enabled=True)
    agent = _build_agent(RAG_SearchAgent, context)

    async def fake_execute(self, state, self_heal_hint=None):
        return {"resume": {}}, {}

    async def fake_self_correct(self, state, base_result, meta):
        return base_result

    agent._execute_rag = MethodType(fake_execute, agent)
    agent._maybe_self_correct = MethodType(fake_self_correct, agent)

    state = {"job": {"job_title": "Engineer", "company": "Acme"}, "metadata": {"workflow_id": "wf"}}
    await agent.run_async(state=state)

    assert precompute_engine.hyde_calls == ["Engineer at Acme"]


class _DummyStrategy:
    def model_dump_json(self):
        return "{\"strategy\": true}"


@pytest.mark.asyncio
async def test_predictive_prompt_prefetch():
    context, _, precompute_engine = _make_context(enabled=True)
    agent = _build_agent(PromptEngineerAgent, context)

    async def fake_generate(self, strategy, complexity, workflow_id, **_):
        return {"prompts": []}, SimpleNamespace()

    async def fake_self_correct(self, strategy, complexity, workflow_id, base_result, validated_output):
        return base_result

    agent._execute_prompt_engineer = MethodType(fake_generate, agent)
    agent._maybe_self_correct = MethodType(fake_self_correct, agent)

    strategy = _DummyStrategy()
    await agent.run_async(strategy=strategy, complexity="complex", workflow_id="wf")

    assert precompute_engine.prompt_plan_calls == [(strategy.model_dump_json(), "complex")]


@pytest.mark.asyncio
async def test_predictive_drafting_prefetch():
    context, _, precompute_engine = _make_context(enabled=True)
    agent = _build_agent(DraftingGuildCoordinator, context)

    async def fake_execute(self, task_context, workflow_id):
        return {"final": True}, {}

    async def fake_self_correct(self, task_context, workflow_id, base_result, meta):
        return base_result

    agent._execute_guild = MethodType(fake_execute, agent)
    agent._maybe_self_correct = MethodType(fake_self_correct, agent)

    bullets = [
        {"text": "one"},
        {"text": "two"},
        {"text": "three"},
        {"text": "four"},
    ]
    await agent.run_async(task_context={"bullets": bullets}, workflow_id="wf")

    assert precompute_engine.embeddings_calls == ["one", "two", "three"]
