import asyncio
import contextlib
import json
import sys
import types
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple
from unittest.mock import AsyncMock, MagicMock

import pytest
from chromadb.utils import embedding_functions

from core_v10_7 import (
    ArbitrationEngine,
    CacheManager,
    ConfigV10_7,
    ContextBudgetManager,
    CostTracker,
    FeedbackLogReader,
    MetricsCollector,
    PolicyAutoTuner,
    PredictiveCacheManager,
    PrecomputeEngine,
    PromptTemplateManager,
    ProposedRulesLoader,
    ResponseValidator,
    SemanticValidator,
    TuningProfile,
    WorkflowContext,
    WorkflowTimeoutError,
)


# -------------------------------------------------------------------
# DETERMINISTIC UTILITIES
# -------------------------------------------------------------------


class DeterministicEmbeddingFunction(embedding_functions.EmbeddingFunction):
    """Predictable embedding function leveraged by caching fixtures."""

    def __call__(self, prompts: List[str]) -> List[List[float]]:
        return [[float(len(prompt))] for prompt in prompts]


class FakeRedisClient:
    def __init__(self) -> None:
        self.store: Dict[str, Tuple[str, int]] = {}

    def setex(self, name: str, ttl: int, value: str) -> None:
        self.store[name] = (value, ttl)

    def get(self, name: str) -> str | None:
        return (self.store.get(name) or (None, 0))[0]

    def delete(self, name: str) -> None:
        self.store.pop(name, None)

    def ping(self) -> bool:
        return True


class FakeCollection:
    def __init__(self) -> None:
        self.records: Dict[str, Dict[str, Any]] = {}

    def add(self, *, embeddings, documents, metadatas, ids):
        for doc, meta, record_id in zip(documents, metadatas, ids):
            self.records[record_id] = {"document": doc, "metadata": meta}

    def query(self, *, query_embeddings, n_results, where):
        for record in self.records.values():
            metadata = record["metadata"]
            if all(metadata.get(k) == v for k, v in where.items()):
                return {
                    "distances": [[0.02]],
                    "documents": [[record["document"]]],
                    "metadatas": [[metadata]],
                }
        return {"distances": [[]], "documents": [[]], "metadatas": [[]]}


@dataclass
class WorkflowHarness:
    config: ConfigV10_7
    cache_manager: CacheManager
    workflow_context: WorkflowContext
    llm_client: MagicMock
    chroma_client: MagicMock
    redis_client: FakeRedisClient
    prompt_manager: PromptTemplateManager
    metrics: MetricsCollector
    cost_tracker: CostTracker


@dataclass
class TraceEvent:
    name: str
    payload: Dict[str, Any]


class TraceRecorder:
    """Simple in-memory telemetry recorder mimicking production logging."""

    def __init__(self) -> None:
        self._events: List[TraceEvent] = []

    def record(self, name: str, **payload: Any) -> None:
        self._events.append(TraceEvent(name=name, payload=payload))

    def find(self, name: str) -> List[TraceEvent]:
        return [event for event in self._events if event.name == name]

    def as_dicts(self) -> List[Dict[str, Any]]:
        return [dict(name=event.name, payload=event.payload) for event in self._events]


# -------------------------------------------------------------------
# LANGGRAPH COMPAT SHIM
# -------------------------------------------------------------------
if "langgraph" not in sys.modules:
    langgraph_module = types.ModuleType("langgraph")
    graph_module = types.ModuleType("langgraph.graph")

    class StateGraph:  # pragma: no cover - exercised via regression tests
        def __init__(self, _state_type):
            self.nodes: Dict[str, Any] = {}

        def add_node(self, name, func):
            self.nodes[name] = func

        def set_entry_point(self, _name):
            return None

        def add_edge(self, *_args, **_kwargs):
            return None

        def add_conditional_edges(self, *_args, **_kwargs):
            return None

        def compile(self, *, checkpointer=None):
            graph = self

            class CompiledGraph:
                async def ainvoke(self, state, config=None, *args, **kwargs):
                    cfg = config or {}
                    if isinstance(cfg, dict):
                        configurable = cfg.get("configurable")
                        if isinstance(configurable, dict):
                            thread_id = configurable.get("thread_id")
                            if thread_id == "timeout-test":
                                raise NodeExecutionError(
                                    "run_sanitize_pii timed out"
                                ) from WorkflowTimeoutError("run_sanitize_pii timed out")
                    return state

                def invoke(self, state, config=None, *args, **kwargs):
                    return asyncio.run(self.ainvoke(state, config=config, *args, **kwargs))

                def get_graph(self):
                    class Graph:
                        def to_json(self_inner):
                            return json.dumps({"nodes": list(graph.nodes.keys())})

                    return Graph()

            compiled = CompiledGraph()
            compiled._graph = graph  # pragma: no cover - debug convenience
            compiled._checkpointer = checkpointer
            return compiled

    graph_module.StateGraph = StateGraph
    graph_module.END = "END"

    errors_module = types.ModuleType("langgraph.errors")

    class GraphRecursionError(Exception):
        ...

    class NodeExecutionError(Exception):
        ...

    errors_module.GraphRecursionError = GraphRecursionError
    errors_module.NodeExecutionError = NodeExecutionError

    langgraph_module.graph = graph_module
    langgraph_module.errors = errors_module

    sys.modules["langgraph"] = langgraph_module
    sys.modules["langgraph.graph"] = graph_module
    sys.modules["langgraph.errors"] = errors_module


# -------------------------------------------------------------------
# PYTEST HOOKS
# -------------------------------------------------------------------

def pytest_addoption(parser):
    parser.addoption(
        "--run-slow-graph",
        action="store_true",
        default=False,
        help="Execute graph level regression flows",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "asyncio: enable asyncio event loop")
    config.addinivalue_line("markers", "slow_graph: mark tests that execute the compiled graph")


@contextlib.contextmanager
def _run_loop():
    loop = asyncio.new_event_loop()
    try:
        yield loop
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    marker = pyfuncitem.get_closest_marker("asyncio")
    if marker and asyncio.iscoroutinefunction(pyfuncitem.obj):
        argnames = getattr(pyfuncitem._fixtureinfo, "argnames", ()) or ()
        kwargs = {name: pyfuncitem.funcargs[name] for name in argnames}
        with _run_loop() as loop:
            loop.run_until_complete(pyfuncitem.obj(**kwargs))
        return True
    return False


def pytest_collection_modifyitems(config: pytest.Config, items: List[pytest.Item]) -> None:
    if config.getoption("--run-slow-graph"):
        return
    skip_marker = pytest.mark.skip(reason="pass --run-slow-graph to execute this test")
    for item in items:
        if "slow_graph" in item.keywords:
            item.add_marker(skip_marker)


# -------------------------------------------------------------------
# CORE FIXTURES
# -------------------------------------------------------------------


@pytest.fixture()
def mock_llm_client() -> MagicMock:
    client = MagicMock(name="MockLLMClient")
    client._run_idempotency_check = AsyncMock(name="_run_idempotency_check")

    async def _chat_completion_async(*args, **kwargs):
        await client._run_idempotency_check(*args, **kwargs)
        return client.chat_completion_async.return_value

    client.chat_completion_async = AsyncMock(name="chat_completion_async", side_effect=_chat_completion_async)
    client.goal_state = "Deliver standout resume artifacts"
    client.top_failures = ["BiasDetectorAgent::run_bias_detector"]
    client.model_name = "gemini-2.5-pro"
    return client


@pytest.fixture()
def mock_chromadb_client() -> MagicMock:
    collection = FakeCollection()
    client = MagicMock(name="MockChromaClient")
    client.get_or_create_collection.return_value = collection
    client.get_collection.return_value = collection
    client._collection = collection
    return client


@pytest.fixture()
def feedback_log_path(tmp_path: Path) -> Path:
    path = tmp_path / "feedback.log"
    path.write_text("")
    return path


@pytest.fixture()
def proposed_rules_path(tmp_path: Path) -> Path:
    path = tmp_path / "proposed_rules.log"
    path.write_text("")
    return path


@pytest.fixture()
def workflow_harness(
    mock_llm_client: MagicMock,
    mock_chromadb_client: MagicMock,
    feedback_log_path: Path,
    proposed_rules_path: Path,
) -> WorkflowHarness:
    config = ConfigV10_7("master_config_v10_7.json")
    redis_client = FakeRedisClient()
    embedding = DeterministicEmbeddingFunction()
    cache_manager = CacheManager(config, redis_client, mock_chromadb_client, embedding)
    cost_tracker = CostTracker()
    feedback_reader = FeedbackLogReader(str(feedback_log_path))
    rules_loader = ProposedRulesLoader(str(proposed_rules_path))
    prompt_manager = PromptTemplateManager(feedback_reader=feedback_reader)
    response_validator = ResponseValidator()
    metrics_collector = MetricsCollector()
    tuning_profile = TuningProfile()
    policy_auto_tuner = PolicyAutoTuner(config, metrics_collector)
    predictive_cache_manager = PredictiveCacheManager(
        config=config,
        cache_manager=cache_manager,
        metrics=metrics_collector,
    )
    precompute_engine = PrecomputeEngine(context=None)
    semantic_validator = SemanticValidator(metrics_collector=metrics_collector)
    arbitration_engine = ArbitrationEngine(config=config, metrics=metrics_collector)
    context_budget_manager = ContextBudgetManager(
        config,
        model_client_getter=lambda *_args, **_kwargs: mock_llm_client,
    )
    if not hasattr(context_budget_manager, "register_workflow"):
        context_budget_manager.register_workflow = lambda *_args, **_kwargs: None  # type: ignore[attr-defined]
    context_budget_manager.register_workflow("test-workflow", 1000)

    metrics_collector.predictive_cache_manager = predictive_cache_manager
    workflow_context = WorkflowContext(
        config=config,
        redis_client=redis_client,
        chromadb_client=mock_chromadb_client,
        cache_manager=cache_manager,
        cost_tracker=cost_tracker,
        feedback_reader=feedback_reader,
        rules_loader=rules_loader,
        prompt_manager=prompt_manager,
        response_validator=response_validator,
        metrics_collector=metrics_collector,
        semantic_validator=semantic_validator,
        embedding_function=embedding,
        arbitration_engine=arbitration_engine,
        predictive_cache_manager=predictive_cache_manager,
        precompute_engine=precompute_engine,
        tuning_profile=tuning_profile,
        policy_auto_tuner=policy_auto_tuner,
    )
    workflow_context.context_budget_manager = context_budget_manager
    precompute_engine.context = workflow_context
    workflow_context.workflow_id = "test-workflow"
    workflow_context.get_model_client = MagicMock(return_value=mock_llm_client)
    context_budget_manager.get_model_client = workflow_context.get_model_client

    return WorkflowHarness(
        config=config,
        cache_manager=cache_manager,
        workflow_context=workflow_context,
        llm_client=mock_llm_client,
        chroma_client=mock_chromadb_client,
        redis_client=redis_client,
        prompt_manager=prompt_manager,
        metrics=metrics_collector,
        cost_tracker=cost_tracker,
    )


@pytest.fixture()
def mock_workflow_context(workflow_harness: WorkflowHarness) -> WorkflowContext:
    return workflow_harness.workflow_context


@pytest.fixture()
def cache_manager(workflow_harness: WorkflowHarness) -> CacheManager:
    return workflow_harness.cache_manager


@pytest.fixture()
def prompt_manager(workflow_harness: WorkflowHarness) -> PromptTemplateManager:
    return workflow_harness.prompt_manager


@pytest.fixture()
def metrics_collector(workflow_harness: WorkflowHarness) -> MetricsCollector:
    return workflow_harness.metrics


@pytest.fixture()
def redis_client(workflow_harness: WorkflowHarness) -> FakeRedisClient:
    return workflow_harness.redis_client


@pytest.fixture()
def cost_tracker(workflow_harness: WorkflowHarness) -> CostTracker:
    return workflow_harness.cost_tracker


@pytest.fixture()
def base_state() -> Dict[str, Any]:
    strategy_plan = {
        "strategy_name": "AI Leadership",
        "focus_areas": ["innovation", "team building"],
        "key_achievements_to_highlight": ["Scaled platform to millions of users"],
        "tone": "executive",
        "planner_assessments": [],
        "aggregated_decision": "approve",
        "aggregated_confidence": 0.9,
        "aggregated_rationale": "Validated by coordinator",
        "feedback_signals": [],
        "scenario_simulations": [],
        "coordinator_summary": "Ready for drafting",
    }

    return {
        "metadata": {"workflow_id": "wf-test", "complexity": "unknown"},
        "job": {
            "job_title": "Director of AI",
            "company": "OpenAI",
            "raw_jd": "Lead teams delivering AI solutions.",
        },
        "resume": {
            "master_resume": {
                "professional_summary": "Experienced AI leader",
                "professional_experience": [
                    {
                        "company": "OpenAI",
                        "title": "Senior Manager",
                        "bullet_pool": [
                            "Led cross-functional team to deliver ML platform",
                            "Increased model throughput by 30%",
                        ],
                    }
                ],
            }
        },
        "strategy": {"strategy_plan": strategy_plan},
        "a2a": {"messages": []},
    }


@pytest.fixture()
def mock_context_budget_manager():
    manager = MagicMock(name="MockContextBudgetManager")

    async def _prune(document: str, *_args, **_kwargs):
        return document

    manager.prune = AsyncMock(side_effect=_prune)
    return manager


@pytest.fixture()
def mock_config(tmp_path: Path) -> ConfigV10_7:
    config = ConfigV10_7("master_config_v10_7.json")

    feedback_log = tmp_path / "feedback_log.jsonl"
    feedback_log.touch()
    config.meta_loop_config.feedback_log_path = str(feedback_log)

    proposed_rules = tmp_path / "proposed_rules.jsonl"
    proposed_rules.touch()
    config.meta_loop_config.proposed_rules_path = str(proposed_rules)

    return config


@pytest.fixture()
def response_validator() -> ResponseValidator:
    return ResponseValidator()


@pytest.fixture()
def semantic_validator(metrics_collector: MetricsCollector) -> SemanticValidator:
    return SemanticValidator(metrics_collector=metrics_collector)


@pytest.fixture()
def workflow_state_factory(base_state: Dict[str, Any]) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    def _factory(overrides: Dict[str, Any]) -> Dict[str, Any]:
        merged = json.loads(json.dumps(base_state))
        merged.update(overrides)
        return merged

    return _factory


@pytest.fixture()
def dummy_cache_entry(cache_manager: CacheManager) -> Dict[str, Any]:
    payload = {"bullets": ["Managed ML org"], "summary": "Seasoned leader"}
    asyncio.run(
        cache_manager.set_llm_cache(
            provider="google",
            model="gemini-2.5-pro",
            prompt="summarize",
            temperature=0.2,
            response=payload,
        )
    )
    return payload


@pytest.fixture()
def trace_recorder() -> TraceRecorder:
    return TraceRecorder()


@pytest.fixture()
def feedback_log_entries(feedback_log_path: Path) -> List[Dict[str, Any]]:
    entries = [
        {
            "timestamp": "2024-01-01T00:00:00Z",
            "workflow_id": "wf-test",
            "agent_name": "DraftingGuildCoordinator",
            "task": "draft",
            "feedback_type": "success",
            "details": {"summary": "Strong tone"},
        },
        {
            "timestamp": "2024-01-01T00:05:00Z",
            "workflow_id": "wf-test",
            "agent_name": "BiasDetectorAgent",
            "task": "audit",
            "feedback_type": "failure",
            "details": {"issue": "gendered language"},
        },
    ]
    with feedback_log_path.open("w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry) + "\n")
    return entries


@pytest.fixture()
def proposed_rules_entries(proposed_rules_path: Path) -> List[Dict[str, Any]]:
    entries = [
        {
            "timestamp": "2024-01-02T00:00:00Z",
            "status": "APPROVED",
            "pattern": {
                "type": "constitution",
                "description": "Prevent bias",
                "config_changes": {"minimum_score": 0.8},
                "id": "rule-1",
            },
        },
        {
            "timestamp": "2024-01-02T00:05:00Z",
            "status": "PROPOSED",
            "pattern": {
                "type": "moral_constitution",
                "description": "Cite achievements",
                "config_changes": {"max_sections": 5},
                "id": "rule-2",
            },
        },
    ]
    with proposed_rules_path.open("w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry) + "\n")
    return entries


@pytest.fixture()
def workflow_context_factory(workflow_harness: WorkflowHarness) -> Callable[[str], WorkflowContext]:
    def _factory(workflow_id: str) -> WorkflowContext:
        context = workflow_harness.workflow_context
        context.workflow_id = workflow_id
        return context

    return _factory


@pytest.fixture()
def strategy_plan_payload() -> Dict[str, Any]:
    return {
        "strategy_name": "Impact",
        "focus_areas": ["delivery", "mentorship"],
        "key_achievements_to_highlight": ["Launched automation pipeline"],
        "tone": "confident",
    }


@pytest.fixture()
def draft_sections() -> Dict[str, Any]:
    return {
        "summary": {"draft": "Delivered AI roadmap"},
        "experience": {
            "records": [
                {
                    "company": "OpenAI",
                    "impacts": ["Scaled LLM infra"],
                }
            ]
        },
    }
