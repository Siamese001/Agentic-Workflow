import json
from types import MethodType, SimpleNamespace

import pytest

from core_v10_7.services import WorldModelStore
from stacks_v10_7 import rag as rag_module
from stacks_v10_7 import strategy as strategy_module


class FakeRedis:
    def __init__(self):
        self.storage = {}
        self.set_calls = []
        self.get_calls = []

    def setex(self, key, ttl, value):
        self.storage[key] = value
        self.set_calls.append((key, ttl, value))

    def get(self, key):
        self.get_calls.append(key)
        return self.storage.get(key)


class RecordingWorldModelStore:
    def __init__(self):
        self.append_calls = []
        self.set_calls = []

    def enabled(self):
        return True

    def append_strategy_outcome(self, payload):
        self.append_calls.append(payload)

    def set_json(self, key, value):
        self.set_calls.append((key, value))


class DummyModelClient:
    def __init__(self, response):
        self._response = response
        self.goal_state = "goal"
        self.top_failures = "fail"

    async def chat_completion_async(self, **_):
        return self._response


class DummyBudgetManager:
    async def prune(self, document, _max_tokens):
        return document


class DummyMetrics:
    def get_average_latency(self, *_args, **_kwargs):
        return None

    def record(self, *_args, **_kwargs):
        return None


class DummyPolicyAutoTuner:
    def enabled(self):
        return False


class DummyPromptManager:
    goal_state = "goal"
    top_failures = "fail"

    def get_template(self, _name):
        return "template"


class StubContext:
    def __init__(self, config, world_model_store, model_clients):
        self.config = config
        self.world_model_store = world_model_store
        self.prompt_manager = DummyPromptManager()
        self.response_validator = SimpleNamespace(validate=lambda _c, _s: ({}, None))
        self.context_budget_manager = DummyBudgetManager()
        self.metrics_collector = DummyMetrics()
        self.cache_manager = None
        self.cost_tracker = SimpleNamespace()
        self.feedback_reader = SimpleNamespace()
        self.rules_loader = SimpleNamespace()
        self.semantic_validator = SimpleNamespace()
        self.embedding_function = object()
        self.arbitration_engine = SimpleNamespace()
        self.predictive_cache_manager = None
        self.precompute_engine = SimpleNamespace()
        self.self_correction_manager = None
        self.tuning_profile = SimpleNamespace(temperature=0.5, rag_force_multi_tool=False)
        self.policy_auto_tuner = DummyPolicyAutoTuner()
        self.workflow_id = "wf-test"
        self.complexity = "complex"
        self.chromadb_client = SimpleNamespace()
        self._model_clients = list(model_clients)

    def ensure_mcp_clients(self):
        return {}

    def is_mcp_enabled(self):
        return False

    def get_model_client(self, _provider=None, _model_name=None, **_kwargs):
        if not self._model_clients:
            raise RuntimeError("No model clients available")
        return self._model_clients.pop(0)


def make_base_config():
    model_config = SimpleNamespace(
        strategy_model_simple=SimpleNamespace(provider="stub", model_name="simple", temperature=0.1),
        strategy_model=SimpleNamespace(provider="stub", model_name="strategy", temperature=0.1),
        reranker_model=SimpleNamespace(provider="stub", model_name="reranker", temperature=0.1),
        react_conductor_model=SimpleNamespace(provider="stub", model_name="react", temperature=0.1),
    )
    agent_stacks = SimpleNamespace(
        strategy_tot_branching_factor=1,
        reranking_top_k=5,
        conductor_max_steps=1,
        conductor_temperature=0.0,
    )
    return SimpleNamespace(
        model_config=model_config,
        agent_stacks=agent_stacks,
        meta_loop_config=SimpleNamespace(feedback_log_path="./logs/test_feedback.jsonl"),
        performance_config=SimpleNamespace(max_complex_model_latency_ms=5000),
        chromadb_config=SimpleNamespace(default_collection_name="test_collection", persistent_path="", use_http_client=False),
    )


def test_world_model_disabled_noop():
    redis_client = FakeRedis()
    config = SimpleNamespace(world_model_config=SimpleNamespace(enabled=False, key_prefix="wm"))
    store = WorldModelStore(config, redis_client)

    store.set_json("test", {"a": 1})
    assert redis_client.set_calls == []

    result = store.get_json("test")
    assert result == {}
    assert redis_client.get_calls == []


def test_world_model_company_knowledge_roundtrip():
    redis_client = FakeRedis()
    config = SimpleNamespace(world_model_config=SimpleNamespace(enabled=True, key_prefix="wm"))
    store = WorldModelStore(config, redis_client)

    store.update_company_knowledge("Acme", {"role": "Engineer"})
    store.update_company_knowledge("Acme", {"size": "100"})

    data = store.get_company_knowledge("Acme")
    assert data["role"] == "Engineer"
    assert data["size"] == "100"


def test_world_model_strategy_history_bounded():
    redis_client = FakeRedis()
    config = SimpleNamespace(
        world_model_config=SimpleNamespace(enabled=True, key_prefix="wm", max_strategy_history=3)
    )
    store = WorldModelStore(config, redis_client)

    for idx in range(5):
        store.append_strategy_outcome({"id": idx})

    history = store.get_strategy_history()["history"]
    assert len(history) == 3
    assert history[0]["id"] == 2
    assert history[-1]["id"] == 4


@pytest.mark.asyncio
async def test_strategy_classifier_records_world_model():
    recording_store = RecordingWorldModelStore()
    config = make_base_config()
    context = StubContext(config, recording_store, [DummyModelClient({"content": "{}"})])
    validated_output = SimpleNamespace(complexity="simple", reason="ok")
    validator = SimpleNamespace(validate=lambda _c, _s: (validated_output, None))
    context.response_validator = validator

    agent = strategy_module.QueryComplexityClassifier(context)
    agent.validator = validator
    await agent.run_async("Sample job description", workflow_id="wf-123")

    assert recording_store.append_calls
    last_entry = recording_store.append_calls[-1]
    assert last_entry["workflow_id"] == "wf-123"
    assert last_entry["complexity"] == "simple"


@pytest.mark.asyncio
async def test_tot_agent_records_world_model(monkeypatch):
    recording_store = RecordingWorldModelStore()
    config = make_base_config()
    context = StubContext(
        config,
        recording_store,
        [DummyModelClient({"content": "{}"}), DummyModelClient({"content": json.dumps({"best_branch_id": "branch_0", "reason": "ok"})})],
    )
    vote_output = SimpleNamespace(best_branch_id="branch_0", reason="ok")
    validator = SimpleNamespace(validate=lambda _c, _s: (vote_output, None))
    context.response_validator = validator

    agent = strategy_module.ToTStrategistAgent(context)
    agent.validator = validator

    class FakePlan:
        def __init__(self):
            self.strategy_name = "Alpha"
            self.tone = "Warm"

        def model_dump(self):
            return {"strategy_name": self.strategy_name, "tone": self.tone}

    async def fake_generate(self, *_args, **_kwargs):
        return [{"branch_id": "branch_0", "strategy": FakePlan()}]

    agent._generate_branches = MethodType(fake_generate, agent)

    async def fake_format(*_args, **_kwargs):
        return "prompt"

    monkeypatch.setattr(strategy_module, "_format_prompt_with_defaults", fake_format)

    await agent.run_async({"job_description": "desc", "job_title": "title"}, workflow_id="wf-strat")

    assert recording_store.append_calls
    entry = recording_store.append_calls[-1]
    assert entry["workflow_id"] == "wf-strat"
    assert entry["strategy_name"] == "Alpha"
    assert entry["tone"] == "Warm"


@pytest.mark.asyncio
async def test_rag_agent_records_world_model(monkeypatch):
    recording_store = RecordingWorldModelStore()
    config = make_base_config()
    context = StubContext(
        config,
        recording_store,
        [
            DummyModelClient({"content": json.dumps({"final_results": [{"company": "Acme", "title": "Eng"}]})}),
            DummyModelClient({"content": "{}"}),
        ],
    )
    context.chromadb_client = SimpleNamespace()
    agent = rag_module.RAG_SearchAgent(context)

    async def fake_ingest(*_args, **_kwargs):
        return None

    agent._ingest_resume_to_chroma_async = MethodType(fake_ingest, agent)
    agent.validator = SimpleNamespace(validate=lambda content, _schema: (json.loads(content), None))

    async def fake_rerank(self, _query, merged, _client):
        return merged

    agent.rerank_results = MethodType(fake_rerank, agent)

    state = {
        "metadata": {"workflow_id": "wf-rag"},
        "job": {"job_title": "Engineer", "company": "Acme"},
        "resume": {"master_resume": {"professional_experience": []}},
        "a2a": {"messages": []},
    }

    await agent._execute_rag(state)

    assert recording_store.set_calls
    key, payload = recording_store.set_calls[-1]
    assert key == "rag_last_run:wf-rag"
    assert payload["num_results"] >= 1
    assert payload["query"] == "Engineer at Acme"
