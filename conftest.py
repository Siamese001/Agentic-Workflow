import asyncio
import json
import sys
import types
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, ANY, patch

import pytest

from core_v10_6 import (
    BaseAgent,
    CacheManager,
    ConfigV10_6,
    ContextBudgetManager,
    CostTracker,
    FeedbackLogReader,
    MetricsCollector,
    PromptTemplateManager,
    ProposedRulesLoader,
    ResponseValidator,
    SemanticValidator,
    StrategyPlan,
    WorkflowContext,
)
if "langgraph" not in sys.modules:
    langgraph_module = types.ModuleType("langgraph")
    graph_module = types.ModuleType("langgraph.graph")

    class StateGraph:  # type: ignore
        def __init__(self, _state_type):
            self.nodes = {}

        def add_node(self, name, func):
            self.nodes[name] = func

        def set_entry_point(self, _name):
            return None

        def add_edge(self, *_args, **_kwargs):
            return None

    graph_module.StateGraph = StateGraph
    graph_module.END = "END"

    errors_module = types.ModuleType("langgraph.errors")

    class GraphRecursionError(Exception):
        ...

    errors_module.GraphRecursionError = GraphRecursionError

    langgraph_module.graph = graph_module
    langgraph_module.errors = errors_module
    sys.modules["langgraph"] = langgraph_module
    sys.modules["langgraph.graph"] = graph_module
    sys.modules["langgraph.errors"] = errors_module

from agent_orchestration_v10_6 import (
    check_constitution,
    get_graph_app,
    load_dynamic_tools,
    run_classify_complexity,
    run_constitutional_review,
    run_sanitize_pii,
)
from agent_stacks_v10_6 import BiasDetectorAgent, RAG_SearchAgent, ToTStrategistAgent


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
    client.chat_completion_async = AsyncMock(name="chat_completion_async")
    client._run_idempotency_check = AsyncMock(name="_run_idempotency_check")
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
    return client


@pytest.fixture()
def mock_workflow_context(mock_llm_client: MagicMock, mock_chromadb_client: MagicMock) -> WorkflowContext:
    config = ConfigV10_6("master_config_v10_6.json")

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
    context.get_model_client = MagicMock(return_value=mock_llm_client)
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

    return context


@pytest.fixture(autouse=True)
def _inject_test_utilities(request: pytest.FixtureRequest, mock_llm_client: MagicMock) -> None:
    module = request.module
    if module.__name__ != "test_system_v10_6":
        return

    if not hasattr(module, "json"):
        module.json = json
    module.ANY = ANY
    module.AsyncMock = AsyncMock
    module.patch = patch
    if not hasattr(StrategyPlan, "model_validate"):
        StrategyPlan.model_validate = classmethod(lambda cls, data: cls(**data))
    module.BaseAgent = BaseAgent
    module.BiasDetectorAgent = BiasDetectorAgent
    module.RAG_SearchAgent = RAG_SearchAgent
    module.ToTStrategistAgent = ToTStrategistAgent
    module.check_constitution = check_constitution
    module.get_graph_app = get_graph_app
    module.load_dynamic_tools = load_dynamic_tools
    module.mock_llm_client = mock_llm_client
    module.run_classify_complexity = run_classify_complexity
    module.run_constitutional_review = run_constitutional_review
    module.run_sanitize_pii = run_sanitize_pii
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
def mock_config(tmp_path: Path) -> ConfigV10_6:
    config = ConfigV10_6("master_config_v10_6.json")

    feedback_log = tmp_path / "feedback_log.jsonl"
    feedback_log.touch()
    config.meta_loop_config.feedback_log_path = str(feedback_log)

    proposed_rules = tmp_path / "proposed_rules.jsonl"
    proposed_rules.touch()
    config.meta_loop_config.proposed_rules_path = str(proposed_rules)

    return config
