import json
from types import SimpleNamespace

import pytest

from core_v10_7.models import StrategyPlan
from core_v10_7.services import WorldModelStore
from stacks_v10_7.strategy import QueryComplexityClassifier, ToTStrategistAgent
from stacks_v10_7.rag import RAG_SearchAgent


class _DummyRedis:
    def __init__(self):
        self.set_calls = []
        self.get_calls = []
        self.storage = {}

    def setex(self, key, ttl, value):
        self.set_calls.append((key, ttl, value))
        self.storage[key] = value

    def get(self, key):
        self.get_calls.append(key)
        return self.storage.get(key)


def _config(enabled=True, key_prefix="wm", max_history=5):
    return SimpleNamespace(
        world_model_config=SimpleNamespace(
            enabled=enabled,
            key_prefix=key_prefix,
            max_strategy_history=max_history,
        )
    )


def test_world_model_disabled_noop():
    redis = _DummyRedis()
    store = WorldModelStore(_config(enabled=False), redis)

    store.set_json("sample", {"a": 1})
    data = store.get_json("sample")

    assert redis.set_calls == []
    assert redis.get_calls == []
    assert data == {}


def test_world_model_company_knowledge_roundtrip():
    redis = _DummyRedis()
    store = WorldModelStore(_config(enabled=True), redis)

    store.update_company_knowledge("Acme", {"score": 1})
    store.update_company_knowledge("Acme", {"notes": "Updated"})

    result = store.get_company_knowledge("Acme")
    assert result == {"score": 1, "notes": "Updated"}


def test_world_model_strategy_history_bounded():
    redis = _DummyRedis()
    store = WorldModelStore(_config(enabled=True, max_history=3), redis)

    for i in range(5):
        store.append_strategy_outcome({"idx": i})

    history = store.get_strategy_history()
    assert len(history["history"]) == 3
    assert [entry["idx"] for entry in history["history"]] == [2, 3, 4]


class _RecordingStore:
    def __init__(self):
        self.payloads = []

    def enabled(self):
        return True

    def append_strategy_outcome(self, payload):
        self.payloads.append(payload)

    def set_json(self, key, value):
        self.payloads.append({"key": key, "value": value})


class _StubValidator:
    def validate(self, content, schema):
        if isinstance(content, str):
            data = json.loads(content)
        else:
            data = content
        return SimpleNamespace(**data), None


class _StubBudgetManager:
    async def prune(self, text, *_):
        return text


class _StubMetrics:
    def get_average_latency(self, **_):
        return 0

    def record(self, *_, **__):
        return None


class _StubPolicyAutoTuner:
    def enabled(self):
        return False


class _StubContext:
    def __init__(self, world_model_store):
        self.config = SimpleNamespace(
            model_config=SimpleNamespace(
                strategy_model_simple=SimpleNamespace(provider="stub", model_name="stub", temperature=0.5),
                strategy_model=SimpleNamespace(provider="stub", model_name="stub", temperature=0.5),
            ),
            meta_loop_config=SimpleNamespace(feedback_log_path="/tmp/meta_feedback.jsonl"),
            agent_stacks=SimpleNamespace(strategy_tot_branching_factor=1),
        )
        self.prompt_manager = SimpleNamespace(goal_state="goal", top_failures="fail", get_template=lambda *_: "template")
        self.response_validator = _StubValidator()
        self.context_budget_manager = _StubBudgetManager()
        self.metrics_collector = _StubMetrics()
        self.self_correction_manager = None
        self.policy_auto_tuner = _StubPolicyAutoTuner()
        self.tuning_profile = SimpleNamespace(temperature=0.5)
        self.world_model_store = world_model_store
        self.workflow_id = "wf"

    def ensure_mcp_clients(self):
        return {}

    def is_mcp_enabled(self):
        return False


class _StubLLMClient:
    def __init__(self, payload):
        self.goal_state = "goal"
        self.top_failures = "fail"
        self._payload = payload

    async def chat_completion_async(self, **_):
        return {"content": json.dumps(self._payload)}


@pytest.mark.asyncio
async def test_strategy_stack_updates_world_model_store():
    store = _RecordingStore()
    context = _StubContext(store)
    agent = QueryComplexityClassifier(context)
    agent.get_model_client = lambda *_: _StubLLMClient({"complexity": "simple", "reason": "ok"})

    result = await agent.run_async("Build systems", "workflow-123")

    assert result == "simple"
    assert store.payloads[0]["workflow_id"] == "workflow-123"
    assert store.payloads[0]["complexity"] == "simple"


@pytest.mark.asyncio
async def test_tot_strategist_records_world_model_outcomes(monkeypatch):
    store = _RecordingStore()
    context = _StubContext(store)
    context.config.agent_stacks.strategy_tot_branching_factor = 1
    agent = ToTStrategistAgent(context)

    async def fake_generate_branches(self, *_):
        strategy = StrategyPlan(
            strategy_name="Plan A",
            focus_areas=["focus"],
            key_achievements_to_highlight=["achievement"],
            tone="bold",
        )
        return [{"branch_id": "branch_0", "strategy": strategy}]

    async def fake_format_prompt(*_args, **_kwargs):
        return "prompt"

    agent.get_model_client = lambda *_: _StubLLMClient({"best_branch_id": "branch_0", "reason": "clear"})
    monkeypatch.setattr(ToTStrategistAgent, "_generate_branches", fake_generate_branches)
    monkeypatch.setattr("stacks_v10_7.strategy._format_prompt_with_defaults", fake_format_prompt)
    agent.log_feedback = lambda *_, **__: None

    result = await agent.run_async({"job_description": ""}, "wf-1")

    assert "strategy_plan" in result
    assert store.payloads[0]["strategy_name"] == "Plan A"
    assert store.payloads[0]["tone"] == "bold"


def test_rag_stack_records_world_model_runs():
    store = _RecordingStore()
    context = SimpleNamespace(world_model_store=store)
    agent = SimpleNamespace(context=context)

    RAG_SearchAgent._record_world_model_rag_run(agent, "wf-5", "query", [1, 2, 3])

    assert store.payloads[0]["key"].endswith("wf-5")
    assert store.payloads[0]["value"]["num_results"] == 3
