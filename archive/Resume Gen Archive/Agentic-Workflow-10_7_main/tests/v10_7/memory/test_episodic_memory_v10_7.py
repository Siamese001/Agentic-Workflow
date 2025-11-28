from types import SimpleNamespace

import pytest

from core_v10_7.models import StrategyPlan
from core_v10_7.services import EpisodicMemory
from agent_stacks_v10_8.components.bullet import AsyncBulletGeneratorAgent


class FakeRedis:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def setex(self, key, ttl, value):
        self.store[key] = value


class DummyMetrics:
    def get_average_latency(self, **_kwargs):
        return None

    def record(self, *_args, **_kwargs):
        return None


class DummyContext:
    def __init__(self, episodic_memory):
        self.config = SimpleNamespace(
            meta_loop_config=SimpleNamespace(feedback_log_path="/tmp/feedback.json"),
            model_config=SimpleNamespace(),
            agent_stacks=SimpleNamespace(),
            performance_config=SimpleNamespace(max_complex_model_latency_ms=1000),
        )
        self.prompt_manager = SimpleNamespace(
            goal_state="",
            top_failures="",
            get_template=lambda *_, **__: "",
        )
        self.response_validator = SimpleNamespace()
        self.context_budget_manager = SimpleNamespace()
        self.metrics_collector = DummyMetrics()
        self.self_correction_manager = None
        self.tuning_profile = SimpleNamespace()
        self.policy_auto_tuner = None
        self.world_model_store = None
        self.predictive_cache_manager = None
        self.precompute_engine = SimpleNamespace()
        self.embedding_function = None
        self.arbitration_engine = None
        self.cache_manager = None
        self.cost_tracker = None
        self.feedback_reader = None
        self.rules_loader = None
        self.workflow_id = ""
        self.episodic_memory = episodic_memory

    def ensure_mcp_clients(self):
        return {}

    def is_mcp_enabled(self):
        return False

    def get_mcp_client(self, *_args, **_kwargs):
        return None

    def get_model_client(self, *_args, **_kwargs):
        raise RuntimeError("model client should not be requested in this test")


class FakeMemory:
    def __init__(self):
        self.get_calls = []
        self.append_calls = []

    def get(self, workflow_id):
        self.get_calls.append(workflow_id)
        return {"events": []}

    def append(self, workflow_id, event):
        self.append_calls.append((workflow_id, event))


@pytest.fixture
def dummy_config():
    return SimpleNamespace()


def test_episodic_append_and_get_roundtrip(dummy_config):
    redis_client = FakeRedis()
    memory = EpisodicMemory(config=dummy_config, redis_client=redis_client)

    for idx in range(205):
        memory.append("workflow-123", {"idx": idx})

    payload = memory.get("workflow-123")
    assert len(payload["events"]) == 200
    assert payload["events"][0]["idx"] == 5
    assert payload["events"][-1]["idx"] == 204


def test_episodic_empty_for_unknown_workflow(dummy_config):
    redis_client = FakeRedis()
    memory = EpisodicMemory(config=dummy_config, redis_client=redis_client)

    assert memory.get("missing") == {"events": []}


@pytest.mark.asyncio
async def test_bullet_stack_appends_episodic_event(monkeypatch):
    fake_memory = FakeMemory()
    context = DummyContext(fake_memory)
    agent = AsyncBulletGeneratorAgent(context)

    async def fake_execute(self, *_args, **_kwargs):
        return {"bullets": [{"id": "b1"}]}

    async def fake_self_correct(self, _task_context, _strategy, _workflow_id, base_result):
        return base_result

    monkeypatch.setattr(
        AsyncBulletGeneratorAgent,
        "_execute_bullet_generator",
        fake_execute,
    )
    monkeypatch.setattr(
        AsyncBulletGeneratorAgent,
        "_maybe_self_correct",
        fake_self_correct,
    )

    strategy = StrategyPlan(
        strategy_name="test",
        focus_areas=[],
        key_achievements_to_highlight=[],
        tone="warm",
    )

    result = await agent.run_async({}, strategy, "wf-test")

    assert result["bullets"][0]["id"] == "b1"
    assert fake_memory.get_calls == ["wf-test"]
    assert fake_memory.append_calls
    _, event = fake_memory.append_calls[0]
    assert event["stack"] == "bullets"
    assert event["event"] == "bullets_generated"
    assert event["count"] == 1
