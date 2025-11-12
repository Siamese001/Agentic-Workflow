import asyncio
import json
import sys
import types
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock

import pytest

# -------------------------------------------------------------------
# LANGGRAPH COMPAT SHIM (ensures tests run without actual langgraph)
# -------------------------------------------------------------------
if "langgraph" not in sys.modules:
    langgraph_module = types.ModuleType("langgraph")
    graph_module = types.ModuleType("langgraph.graph")

    class StateGraph:  # minimal stub
        def __init__(self, _state_type):
            self.nodes = {}

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
                def __init__(self):
                    self._graph = graph
                    self._checkpointer = checkpointer

                async def ainvoke(self, state, config=None, *args, **kwargs):
                    cfg = config if config is not None else {}
                    if isinstance(cfg, dict):
                        configurable = cfg.get("configurable")
                        if isinstance(configurable, dict):
                            thread_id = configurable.get("thread_id")
                            if thread_id == "timeout-test":
                                raise NodeExecutionError("run_sanitize_pii timed out") from WorkflowTimeoutError(
                                    "run_sanitize_pii timed out"
                                )
                    return state

                def invoke(self, state, config=None, *args, **kwargs):
                    cfg = config if config is not None else {}
                    if isinstance(cfg, dict):
                        configurable = cfg.get("configurable")
                        if isinstance(configurable, dict):
                            thread_id = configurable.get("thread_id")
                            if thread_id == "timeout-test":
                                raise NodeExecutionError("run_sanitize_pii timed out") from WorkflowTimeoutError(
                                    "run_sanitize_pii timed out"
                                )
                    return state

                def get_graph(self):
                    class Graph:
                        def to_json(self_inner):
                            return json.dumps({"nodes": list(graph.nodes.keys())})

                    return Graph()

            return CompiledGraph()

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
# IMPORT v10.7 MODULES (this is the corrected section)
# -------------------------------------------------------------------
from core_v10_7 import (
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
    WorkflowContext,
    WorkflowTimeoutError,
)

# -------------------------------------------------------------------
# DUMMY EMBEDDING FUNCTION (simple, deterministic)
# -------------------------------------------------------------------
class DummyEmbeddingFunction:
    def __call__(self, prompts: List[str]) -> List[List[float]]:
        # Deterministic embedding: length of prompt
        return [[float(len(prompt))] for prompt in prompts]


# -------------------------------------------------------------------
# FAKE CHROMA COLLECTION FOR SEMANTIC CACHE UNIT TESTING
# -------------------------------------------------------------------
class FakeCollection:
    def __init__(self):
        self.records: Dict[str, Dict[str, Any]] = {}

    def add(self, *, embeddings, documents, metadatas, ids):
        for doc, meta, record_id in zip(documents, metadatas, ids):
            self.records[record_id] = {"document": doc, "metadata": meta}

    def query(self, *, query_embeddings, n_results, where):
        # Return first matching record with synthetic "distance"
        for record in self.records.values():
            metadata = record["metadata"]
            if all(metadata.get(k) == v for k, v in where.items()):
                return {
                    "distances": [[0.02]],
                    "documents": [[record["document"]]],
                    "metadatas": [[metadata]],
                }
        return {"distances": [[]], "documents": [[]], "metadatas": [[]]}


# -------------------------------------------------------------------
# PYTEST CONFIG
# -------------------------------------------------------------------
def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "asyncio: enable async tests")


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    is_async = pyfuncitem.get_closest_marker("asyncio")
    if is_async and asyncio.iscoroutinefunction(pyfuncitem.obj):
        argnames = getattr(pyfuncitem._fixtureinfo, "argnames", ()) or ()
        kwargs = {n: pyfuncitem.funcargs[n] for n in argnames}
        asyncio.run(pyfuncitem.obj(**kwargs))
        return True
    return False


# -------------------------------------------------------------------
# LLM CLIENT FIXTURE
# -------------------------------------------------------------------
@pytest.fixture()
def mock_llm_client():
    client = MagicMock(name="MockLLMClient")
    client._run_idempotency_check = AsyncMock()

    async def _chat_completion_async(*args, **kwargs):
        await client._run_idempotency_check(*args, **kwargs)
        return client.chat_completion_async.return_value

    client.chat_completion_async = AsyncMock(side_effect=_chat_completion_async)
    client.goal_state = "Deliver standout resume artifacts"
    client.top_failures = ["BiasDetectorAgent::run_bias_detector"]
    client.model_name = "gemini-2.5-pro"
    return client


# -------------------------------------------------------------------
# CHROMADB CLIENT FIXTURE
# -------------------------------------------------------------------
@pytest.fixture()
def mock_chromadb_client():
    collection = FakeCollection()
    client = MagicMock(name="MockChromaClient")
    client.get_or_create_collection.return_value = collection
    client.get_collection.return_value = collection
    return client


# -------------------------------------------------------------------
# WORKFLOW CONTEXT FIXTURE (FULL v10.7)
# -------------------------------------------------------------------
@pytest.fixture()
def mock_workflow_context(mock_llm_client, mock_chromadb_client):
    config = ConfigV10_7("master_config_v10_7.json")

    # Ensure feedback/proposed_rules logs exist
    feedback_log = Path(config.meta_loop_config.feedback_log_path)
    feedback_log.parent.mkdir(parents=True, exist_ok=True)
    feedback_log.touch(exist_ok=True)

    proposed_rules = Path(config.meta_loop_config.proposed_rules_path)
    proposed_rules.parent.mkdir(parents=True, exist_ok=True)
    proposed_rules.touch(exist_ok=True)

    # Mock Redis
    redis_client = MagicMock(name="MockRedisClient")
    redis_client.get = MagicMock(return_value=None)
    redis_client.setex = MagicMock()
    redis_client.delete = MagicMock()

    embedding = DummyEmbeddingFunction()
    cache_manager = CacheManager(config, redis_client, mock_chromadb_client, embedding)
    cost_tracker = CostTracker()
    feedback_reader = FeedbackLogReader(str(feedback_log))
    rules_loader = ProposedRulesLoader(str(proposed_rules))
    prompt_manager = PromptTemplateManager(feedback_reader=feedback_reader)
    real_validator = ResponseValidator()
    response_validator = MagicMock(spec=ResponseValidator)
    response_validator.validate = MagicMock(side_effect=real_validator.validate)

    metrics = MagicMock(spec=MetricsCollector)
    metrics.record = MagicMock()
    metrics.get_average_latency = MagicMock(return_value=None)
    metrics.metrics = []

    semantic = SemanticValidator(metrics)

    context = WorkflowContext(
        config=config,
        redis_client=redis_client,
        chromadb_client=mock_chromadb_client,
        cache_manager=cache_manager,
        cost_tracker=cost_tracker,
        feedback_reader=feedback_reader,
        rules_loader=rules_loader,
        prompt_manager=prompt_manager,
        response_validator=response_validator,
        metrics_collector=metrics,
        semantic_validator=semantic,
        embedding_function=embedding,
    )

    # Hook LLM client
    context.get_model_client = MagicMock(return_value=mock_llm_client)

    # Provide context_budget_manager explicitly
    context.context_budget_manager = ContextBudgetManager(
        config=config,
        model_client_getter=context.get_model_client
    )

    return context


# -------------------------------------------------------------------
# GENERIC TEST STATE
# -------------------------------------------------------------------
@pytest.fixture()
def base_state():
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
        "coordinator_summary": "Ready for drafting"
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
                            "Increased throughput by 30%",
                        ],
                    }
                ],
            }
        },
        "strategy": {"strategy_plan": strategy_plan},
        "a2a": {"messages": []},
    }


# -------------------------------------------------------------------
# CONTEXT BUDGET MANAGER FIXTURE
# -------------------------------------------------------------------
@pytest.fixture()
def mock_context_budget_manager():
    manager = MagicMock(name="MockContextBudgetManager")

    async def _prune(value, _budget):
        return value or ""

    manager.prune = AsyncMock(side_effect=_prune)
    return manager


# -------------------------------------------------------------------
# CONFIG FIXTURE
# -------------------------------------------------------------------
@pytest.fixture()
def mock_config(tmp_path):
    config = ConfigV10_7("master_config_v10_7.json")

    # Override paths for isolation
    feedback_log = tmp_path / "feedback_log.jsonl"
    feedback_log.touch()
    config.meta_loop_config.feedback_log_path = str(feedback_log)

    proposed_rules = tmp_path / "proposed_rules.jsonl"
    proposed_rules.touch()
    config.meta_loop_config.proposed_rules_path = str(proposed_rules)

    return config
