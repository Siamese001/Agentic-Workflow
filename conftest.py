import asyncio
import copy
import inspect
import json
import random
import sys
import types
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import AsyncMock, MagicMock, ANY, DEFAULT, patch

import pytest

from core_v10_7 import (
    BaseAgent,
    CacheManager,
    ConfigV10_7,
    ContextBudgetManager,
    CostTracker,
    FeedbackLogReader,
    MetricsCollector,
    PromptTemplateManager,
    ProposedRulesLoader,
    ResponseValidator,
    SemanticValidator,
    StrategyPlan,
    WorkflowTimeoutError,
    WorkflowContext,
)
if "langgraph" not in sys.modules:
    langgraph_module = types.ModuleType("langgraph")
    graph_module = types.ModuleType("langgraph.graph")

    class NodeExecutionError(Exception):
        def __init__(self, message: str, node: Optional[str] = None) -> None:
            super().__init__(message)
            self.node = node

    def _deep_merge(target: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        for key, value in payload.items():
            if isinstance(value, dict) and isinstance(target.get(key), dict):
                _deep_merge(target[key], value)
            else:
                target[key] = value
        return target

    class _GraphView:
        def __init__(self, state_graph: "StateGraph") -> None:
            self._graph = state_graph

        def to_json(self) -> str:
            data = {
                "entry_point": self._graph.entry_point,
                "nodes": list(self._graph.nodes.keys()),
                "edges": self._graph.edges,
                "conditional_edges": {
                    node: mapping for node, (_, mapping) in self._graph.conditional_edges.items()
                },
            }
            return json.dumps(data)

    class _CompiledGraph:
        def __init__(self, state_graph: "StateGraph") -> None:
            self._graph = state_graph

        async def ainvoke(self, state: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
            del config  # API compatibility shim
            current = self._graph.entry_point
            result_state: Dict[str, Any] = copy.deepcopy(state)

            visited: set[str] = set()
            while current and current != graph_module.END:
                if current in visited:
                    raise NodeExecutionError("Detected cycle during execution", node=current)
                visited.add(current)

                node_callable = self._graph.nodes.get(current)
                if node_callable is None:
                    raise NodeExecutionError(f"Node '{current}' is not registered", node=current)

                try:
                    output = node_callable(result_state)
                    if inspect.isawaitable(output):
                        output = await output  # type: ignore[assignment]
                except WorkflowTimeoutError as exc:  # pragma: no cover - defensive
                    raise NodeExecutionError(f"{current} timed out", node=current) from exc
                except Exception as exc:  # pragma: no cover - defensive
                    raise NodeExecutionError(f"{current} failed: {exc}", node=current) from exc

                if isinstance(output, dict):
                    _deep_merge(result_state, output)

                next_node: Optional[str] = None
                if current in self._graph.conditional_edges:
                    condition, branches = self._graph.conditional_edges[current]
                    branch_key = condition(result_state)
                    next_node = branches.get(branch_key)
                else:
                    successors = self._graph.edges.get(current, [])
                    next_node = successors[0] if successors else None

                current = next_node

            return result_state

        def invoke(self, state: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
            return asyncio.run(self.ainvoke(state, config))

        def get_graph(self) -> _GraphView:
            return _GraphView(self._graph)

    class StateGraph:  # type: ignore
        def __init__(self, _state_type):
            self.nodes: Dict[str, Any] = {}
            self.entry_point: Optional[str] = None
            self.edges: Dict[str, List[str]] = {}
            self.conditional_edges: Dict[str, Tuple[Any, Dict[str, str]]] = {}

        def add_node(self, name: str, func: Any) -> None:
            self.nodes[name] = func

        def set_entry_point(self, name: str) -> None:
            self.entry_point = name

        def add_edge(self, source: str, target: str) -> None:
            self.edges.setdefault(source, []).append(target)

        def add_conditional_edges(self, source: str, condition: Any, mapping: Dict[str, str]) -> None:
            self.conditional_edges[source] = (condition, mapping)

        def compile(self, checkpointer=None):  # noqa: ARG002 - compatibility
            return _CompiledGraph(self)

    graph_module.StateGraph = StateGraph
    graph_module.END = "END"

    errors_module = types.ModuleType("langgraph.errors")

    class GraphRecursionError(Exception):
        ...

    errors_module.GraphRecursionError = GraphRecursionError
    errors_module.NodeExecutionError = NodeExecutionError

    checkpoint_module = types.ModuleType("langgraph.checkpoint")
    checkpoint_redis_module = types.ModuleType("langgraph.checkpoint.redis")

    class RedisSaver:  # type: ignore
        def __init__(self, *args, **kwargs) -> None:  # noqa: D401 - stub
            self.args = args
            self.kwargs = kwargs

        async def aget(self, *args, **kwargs):  # pragma: no cover - minimal stub
            return None

        async def aset(self, *args, **kwargs):  # pragma: no cover
            return None

    checkpoint_redis_module.RedisSaver = RedisSaver
    checkpoint_module.redis = checkpoint_redis_module

    langgraph_module.graph = graph_module
    langgraph_module.errors = errors_module
    langgraph_module.checkpoint = checkpoint_module
    sys.modules["langgraph"] = langgraph_module
    sys.modules["langgraph.graph"] = graph_module
    sys.modules["langgraph.errors"] = errors_module
    sys.modules["langgraph.checkpoint"] = checkpoint_module
    sys.modules["langgraph.checkpoint.redis"] = checkpoint_redis_module

from agent_orchestration_v10_7 import (
    check_constitution,
    get_graph_app,
    load_dynamic_tools,
    run_classify_complexity,
    run_constitutional_review,
    run_sanitize_pii,
)
from agent_stacks_v10_7 import BiasDetectorAgent, RAG_SearchAgent, ToTStrategistAgent
from run_batch_v10_7 import run_batch_async


class DummyEmbeddingFunction:
    def __call__(self, prompts: List[str]) -> List[List[float]]:
        return [[float(len(prompt))] for prompt in prompts]


class FakeCollection:
    def __init__(self) -> None:
        self.records: Dict[str, Dict[str, Any]] = {}

    def add(
        self,
        *,
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
    ) -> None:
        for doc, metadata, record_id in zip(documents, metadatas, ids):
            self.records[record_id] = {"document": doc, "metadata": metadata}

    def query(
        self,
        *,
        query_embeddings: List[List[float]],
        n_results: int,
        where: Dict[str, Any],
    ) -> Dict[str, Any]:
        for record in self.records.values():
            metadata = record["metadata"]
            if all(metadata.get(key) == value for key, value in where.items()):
                return {
                    "distances": [[0.02]],
                    "documents": [[record["document"]]],
                }
        return {"distances": [[]], "documents": [[]]}


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "asyncio: run asynchronous tests with asyncio.run")


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem: pytest.Function) -> bool:
    if pyfuncitem.get_closest_marker("asyncio") and asyncio.iscoroutinefunction(pyfuncitem.obj):
        argnames = getattr(pyfuncitem._fixtureinfo, "argnames", ())
        kwargs = {name: pyfuncitem.funcargs[name] for name in argnames or ()}
        asyncio.run(pyfuncitem.obj(**kwargs))
        return True
    return False


@pytest.fixture()
def mock_llm_client() -> MagicMock:
    client = MagicMock(name="MockLLMClient")
    chat_mock = AsyncMock(name="chat_completion_async")

    async def _chat_completion_with_cache(
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        response_format: Optional[str] = None,
    ) -> Dict[str, Any]:
        prompt = "\n".join(f"{m.get('role')}: {m.get('content')}" for m in messages)
        provider = "google" if "gemini" in client.model_name else "openai"

        cache_manager = getattr(client, "cache_manager", None)
        config = getattr(client, "config", None)

        if cache_manager is not None:
            cached_response = await cache_manager.get_llm_cache(provider, client.model_name, prompt, temperature)
            if cached_response:
                if (
                    config is not None
                    and getattr(config.caching_config, "enable_idempotency_validation", False)
                    and random.random() < getattr(
                        config.caching_config, "idempotency_validation_sample_rate", 0.0
                    )
                ):
                    await client._run_idempotency_check(
                        cached_response,
                        messages,
                        temperature,
                        response_format,
                    )
                return cached_response

        if chat_mock._mock_wraps is not None:
            return await chat_mock._mock_wraps(
                messages,
                temperature=temperature,
                response_format=response_format,
            )

        if chat_mock._mock_return_value is not DEFAULT:
            return chat_mock._mock_return_value  # type: ignore[return-value]

        return {"content": "", "usage": {}}

    chat_mock.side_effect = _chat_completion_with_cache
    client.chat_completion_async = chat_mock
    client._run_idempotency_check = AsyncMock(name="_run_idempotency_check")
    client.goal_state = "Deliver standout resume artifacts"
    client.top_failures = ["BiasDetectorAgent::run_bias_detector"]
    client.model_name = "gemini-pro"
    return client


@pytest.fixture()
def mock_chromadb_client() -> MagicMock:
    collection = FakeCollection()
    client = MagicMock(name="MockChromaClient")
    client.get_or_create_collection.return_value = collection
    client.get_collection.return_value = collection
    return client


@pytest.fixture()
def mock_workflow_context(mock_llm_client: MagicMock, mock_chromadb_client: MagicMock) -> WorkflowContext:
    config = ConfigV10_7("master_config_v10_7.json")
    config.caching_config.enable_idempotency_validation = True
    config.caching_config.idempotency_validation_sample_rate = 1.0

    feedback_log_path = Path(config.meta_loop_config.feedback_log_path)
    feedback_log_path.parent.mkdir(parents=True, exist_ok=True)
    feedback_log_path.touch(exist_ok=True)

    proposed_rules_path = Path(config.meta_loop_config.proposed_rules_path)
    proposed_rules_path.parent.mkdir(parents=True, exist_ok=True)
    proposed_rules_path.touch(exist_ok=True)

    redis_client = MagicMock(name="MockRedisClient")
    redis_client.get = MagicMock(return_value=None)
    redis_client.setex = MagicMock()
    redis_client.delete = MagicMock()

    embedding_function = DummyEmbeddingFunction()
    cache_manager = CacheManager(config, redis_client, mock_chromadb_client, embedding_function)
    semantic_collection = mock_chromadb_client.get_or_create_collection.return_value
    mock_chromadb_client.get_collection.return_value = semantic_collection
    cache_manager.semantic_cache_collection = semantic_collection

    cost_tracker = CostTracker()
    feedback_reader = FeedbackLogReader(str(feedback_log_path))
    rules_loader = ProposedRulesLoader(str(proposed_rules_path))
    prompt_manager = PromptTemplateManager(feedback_reader=feedback_reader)
    real_validator = ResponseValidator()

    metrics_collector = MagicMock(spec=MetricsCollector)
    metrics_collector.record = MagicMock()
    metrics_collector.get_average_latency = MagicMock(return_value=None)
    metrics_collector.metrics = []

    semantic_validator = SemanticValidator(metrics_collector=metrics_collector)

    context = WorkflowContext(
        config=config,
        redis_client=redis_client,
        chromadb_client=mock_chromadb_client,
        cache_manager=cache_manager,
        cost_tracker=cost_tracker,
        feedback_reader=feedback_reader,
        rules_loader=rules_loader,
        prompt_manager=prompt_manager,
        response_validator=real_validator,
        metrics_collector=metrics_collector,
        semantic_validator=semantic_validator,
        embedding_function=embedding_function,
    )

    context.workflow_id = "wf-test"

    def _mock_get_model_client(provider: str, model_name: str):
        mock_llm_client.model_name = model_name
        return mock_llm_client

    context.get_model_client = MagicMock(side_effect=_mock_get_model_client)
    context.context_budget_manager = ContextBudgetManager(
        config=config,
        model_client_getter=context.get_model_client,
    )
    context.response_validator = MagicMock(spec=ResponseValidator)
    context.response_validator.validate = MagicMock(side_effect=real_validator.validate)
    context.metrics_collector = metrics_collector
    context.cache_manager = cache_manager
    context.redis_client = redis_client
    context.chromadb_client = mock_chromadb_client
    context.prompt_manager = prompt_manager
    context.semantic_validator = semantic_validator

    mock_llm_client.cache_manager = cache_manager
    mock_llm_client.config = config
    mock_llm_client.metrics_collector = metrics_collector

    return context


@pytest.fixture(autouse=True)
def _inject_test_utilities(request: pytest.FixtureRequest, mock_llm_client: MagicMock) -> None:
    module = request.module
    if module is None or "test_system_v10_7" not in module.__name__:
        return

    if not hasattr(module, "json"):
        module.json = json
    module.ANY = ANY
    module.AsyncMock = AsyncMock
    module.MagicMock = MagicMock
    module.patch = patch
    if not hasattr(StrategyPlan, "model_validate"):
        StrategyPlan.model_validate = classmethod(lambda cls, data: cls(**data))
    module.BaseAgent = BaseAgent
    module.BiasDetectorAgent = BiasDetectorAgent
    module.RAG_SearchAgent = RAG_SearchAgent
    module.ToTStrategistAgent = ToTStrategistAgent
    module.check_constitution = check_constitution
    module.get_graph_app = get_graph_app
    module._format_prompt_with_defaults = getattr(
        __import__("core_v10_7"), "_format_prompt_with_defaults"
    )
    module.load_dynamic_tools = load_dynamic_tools
    module.mock_llm_client = mock_llm_client
    module.run_classify_complexity = run_classify_complexity
    module.run_constitutional_review = run_constitutional_review
    module.run_sanitize_pii = run_sanitize_pii
    module.NodeExecutionError = sys.modules["langgraph.errors"].NodeExecutionError
    module.run_batch_async = run_batch_async
    module.WorkflowTimeoutError = WorkflowTimeoutError
    module.time = __import__("time")
    module.StrategyPlan = StrategyPlan


@pytest.fixture()
def mock_context_budget_manager() -> Any:
    class _BudgetManager:
        async def prune(self, document: str, max_tokens: int | None = None) -> str:
            return document

    return _BudgetManager()


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
def mock_config(tmp_path: Path) -> ConfigV10_7:
    config = ConfigV10_7("master_config_v10_7.json")

    feedback_log = tmp_path / "feedback_log.jsonl"
    feedback_log.touch()
    config.meta_loop_config.feedback_log_path = str(feedback_log)

    proposed_rules = tmp_path / "proposed_rules.jsonl"
    proposed_rules.touch()
    config.meta_loop_config.proposed_rules_path = str(proposed_rules)

    return config
