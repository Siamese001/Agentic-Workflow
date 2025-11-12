import asyncio, sys, types, pytest
from pathlib import Path
from typing import Any, Dict, List

# Ensure repository root is importable when pytest rootdir resolves to tests/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ---- LangGraph stub (so imports succeed in tests) ----
if "langgraph" not in sys.modules:  # setup code only
    langgraph = types.ModuleType("langgraph")
    graph_module = types.ModuleType("langgraph.graph")

    class StateGraph:  # type: ignore[override]
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
    class GraphRecursionError(Exception): ...
    errors_module.GraphRecursionError = GraphRecursionError

    langgraph.graph = graph_module
    langgraph.errors = errors_module
    sys.modules["langgraph"] = langgraph
    sys.modules["langgraph.graph"] = graph_module
    sys.modules["langgraph.errors"] = errors_module

# ---- Lightweight test doubles for cache layer ----
class InMemoryRedis:
    def __init__(self) -> None:
        self.store: Dict[str, str] = {}
    def setex(self, name: str, ttl: int, value: str) -> None:
        self.store[name] = value
    def get(self, name: str) -> str | None:
        return self.store.get(name)

class FakeCollection:
    def __init__(self) -> None:
        self.records: Dict[str, Dict[str, Any]] = {}
    def add(self, *, embeddings: List[List[float]], documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
        for doc, metadata, record_id in zip(documents, metadatas, ids):
            self.records[record_id] = {"document": doc, "metadata": metadata}
    def query(self, *, query_embeddings: List[List[float]], n_results: int, where: Dict[str, Any]) -> Dict[str, Any]:
        for record in self.records.values():
            md = record["metadata"]
            if all(md.get(k) == v for k, v in where.items()):
                return {"distances": [[0.02]], "documents": [[record["document"]]]}
        return {"distances": [[]], "documents": [[]]}

class FakeChromaClient:
    def __init__(self, collection: FakeCollection) -> None:
        self.collection = collection
    def get_or_create_collection(self, name: str, embedding_function: Any) -> FakeCollection:
        return self.collection

class DummyEmbeddingFunction:
    def __call__(self, prompts: List[str]) -> List[List[float]]:
        return [[float(len(p))] for p in prompts]

# ---- Core fixtures pulled together like your v10_7 tests ----
from core_v10_7 import (
    CacheManager, ConfigV10_7, CostTracker, FeedbackLogReader, ProposedRulesLoader,
    PromptTemplateManager, ResponseValidator, MetricsCollector, SemanticValidator,
    ContextBudgetManager, WorkflowContext
)

@pytest.fixture(scope="session")
def config() -> ConfigV10_7:
    return ConfigV10_7("master_config_v10_7.json")

@pytest.fixture()
def cache_manager(config: ConfigV10_7) -> CacheManager:
    collection = FakeCollection()
    chroma = FakeChromaClient(collection)
    redis_client = InMemoryRedis()
    embedding_fn = DummyEmbeddingFunction()
    return CacheManager(config, redis_client, chroma, embedding_fn)

@pytest.fixture()
def workflow_context(config: ConfigV10_7) -> WorkflowContext:
    redis_client = InMemoryRedis()
    collection = FakeCollection()
    chroma = FakeChromaClient(collection)
    embedding_fn = DummyEmbeddingFunction()
    cache_mgr = CacheManager(config, redis_client, chroma, embedding_fn)
    cost_tracker = CostTracker()
    feedback_reader = FeedbackLogReader(config.meta_loop_config.feedback_log_path)
    rules_loader = ProposedRulesLoader(config.meta_loop_config.proposed_rules_path)
    prompt_manager = PromptTemplateManager(feedback_reader=feedback_reader)
    response_validator = ResponseValidator()
    metrics = MetricsCollector()
    semantic_validator = SemanticValidator(metrics_collector=metrics)
    ctx = WorkflowContext(
        config=config, redis_client=redis_client, chromadb_client=chroma,
        cache_manager=cache_mgr, cost_tracker=cost_tracker,
        feedback_reader=feedback_reader, rules_loader=rules_loader,
        prompt_manager=prompt_manager, response_validator=response_validator,
        metrics_collector=metrics, semantic_validator=semantic_validator,
        embedding_function=embedding_fn,
    )
    ctx.context_budget_manager = ContextBudgetManager(config=config, model_client_getter=ctx.get_model_client)
    ctx.reset_mcp_clients()
    return ctx
