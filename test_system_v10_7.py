"""Focused regression tests for the v10.7 core components."""

import asyncio
import sys
import types
from typing import Any, Dict, List

import pytest

from core_v10_7 import (
    BaseTool,
    CacheManager,
    CircuitBreaker,
    CircuitBreakerOpenError,
    ConfigV10_7,
    ContextBudgetManager,
    CostTracker,
    FeedbackLogReader,
    MCPClientStub,
    MetricsCollector,
    ModelAPIError,
    MCPClientInitializationError,
    ProposedRulesLoader,
    PromptTemplateManager,
    ResponseValidator,
    SemanticValidator,
    WorkflowContext,
    exponential_backoff_retry,
    _instantiate_mcp_client,
    _parse_mcp_client_specs,
    MCPClientSpec,
    wrap_mcp,
)
from agent_tools_v10_7 import resolve_mcp_client

# Provide minimal langgraph stubs so agent_orchestration imports succeed in tests.
if "langgraph" not in sys.modules:  # pragma: no cover - setup code
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

    class GraphRecursionError(Exception):
        pass

    errors_module.GraphRecursionError = GraphRecursionError

    langgraph.graph = graph_module
    langgraph.errors = errors_module
    sys.modules["langgraph"] = langgraph
    sys.modules["langgraph.graph"] = graph_module
    sys.modules["langgraph.errors"] = errors_module

from agent_orchestration_v10_7 import load_dynamic_tools


class InMemoryRedis:
    """Minimal Redis substitute supporting the subset used by CacheManager."""

    def __init__(self) -> None:
        self.store: Dict[str, str] = {}

    def setex(self, name: str, ttl: int, value: str) -> None:
        self.store[name] = value

    def get(self, name: str) -> str | None:
        return self.store.get(name)


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


class FakeChromaClient:
    def __init__(self, collection: FakeCollection) -> None:
        self.collection = collection

    def get_or_create_collection(self, name: str, embedding_function: Any) -> FakeCollection:
        return self.collection


class DummyEmbeddingFunction:
    def __call__(self, prompts: List[str]) -> List[List[float]]:
        return [[float(len(prompt))] for prompt in prompts]


@pytest.fixture()
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

    context = WorkflowContext(
        config=config,
        redis_client=redis_client,
        chromadb_client=chroma,
        cache_manager=cache_mgr,
        cost_tracker=cost_tracker,
        feedback_reader=feedback_reader,
        rules_loader=rules_loader,
        prompt_manager=prompt_manager,
        response_validator=response_validator,
        metrics_collector=metrics,
        semantic_validator=semantic_validator,
        embedding_function=embedding_fn,
    )

    context.context_budget_manager = ContextBudgetManager(
        config=config,
        model_client_getter=context.get_model_client,
    )
    context.reset_mcp_clients()
    return context


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------


def test_config_provides_nested_sections(config: ConfigV10_7) -> None:
    assert config.logging_config.log_level == "INFO"
    assert config.agent_stacks.enable_constitutional_review is True
    assert config.agent_stacks.conductor_max_steps == 10


def test_config_missing_section_raises_attribute_error(config: ConfigV10_7) -> None:
    with pytest.raises(AttributeError):
        _ = config.this_section_does_not_exist


# ---------------------------------------------------------------------------
# Circuit breaker behaviour
# ---------------------------------------------------------------------------


def test_circuit_breaker_trips_after_failures() -> None:
    breaker = CircuitBreaker(failure_threshold=2)

    breaker.record_failure()
    assert breaker.is_open is False

    breaker.record_failure()
    assert breaker.is_open is True

    with pytest.raises(CircuitBreakerOpenError):
        breaker.check()


def test_circuit_breaker_resets_on_success() -> None:
    breaker = CircuitBreaker(failure_threshold=1)
    breaker.record_failure()
    assert breaker.is_open is True

    breaker.record_success()
    assert breaker.is_open is False
    breaker.check()  # Should not raise after reset


# ---------------------------------------------------------------------------
# Exponential backoff decorator
# ---------------------------------------------------------------------------


def test_exponential_backoff_retry_eventually_succeeds() -> None:
    attempts: Dict[str, int] = {"count": 0}

    @exponential_backoff_retry(max_retries=3, initial_delay=0)
    async def flaky_call() -> str:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise ModelAPIError("temporary issue")
        return "success"

    result = asyncio.run(flaky_call())
    assert result == "success"
    assert attempts["count"] == 3


def test_exponential_backoff_retry_propagates_after_max_attempts() -> None:
    @exponential_backoff_retry(max_retries=2, initial_delay=0)
    async def always_fail() -> None:
        raise ModelAPIError("still broken")

    with pytest.raises(ModelAPIError):
        asyncio.run(always_fail())


# ---------------------------------------------------------------------------
# CacheManager integration
# ---------------------------------------------------------------------------


def test_cache_manager_reads_exact_cache(cache_manager: CacheManager) -> None:
    asyncio.run(
        cache_manager.set_llm_cache(
            provider="openai",
            model="gpt-test",
            prompt="hello",
            temperature=0.1,
            response={"content": "cached"},
        )
    )

    cached = asyncio.run(
        cache_manager.get_llm_cache(
            provider="openai",
            model="gpt-test",
            prompt="hello",
            temperature=0.1,
        )
    )

    assert cached["content"] == "cached"


def test_cache_manager_sets_tool_cache(cache_manager: CacheManager) -> None:
    cache_manager.set_tool_cache("demo", {"a": 1}, {"result": 42})
    cached = cache_manager.get_tool_cache("demo", {"a": 1})
    assert cached == {"result": 42}


# ---------------------------------------------------------------------------
# MCP integration
# ---------------------------------------------------------------------------


def test_parse_mcp_client_specs_rejects_non_mappings() -> None:
    with pytest.raises(ValueError):
        _ = _parse_mcp_client_specs(["not-a-mapping"])  # type: ignore[list-item]


def test_parse_mcp_client_specs_requires_parameter_mapping() -> None:
    with pytest.raises(ValueError):
        _parse_mcp_client_specs(
            [
                {
                    "name": "broken",
                    "parameters": ["not", "a", "dict"],
                }
            ]
        )


def test_instantiate_mcp_client_missing_class_raises() -> None:
    module_name = "failing_mcp_module"
    module = types.ModuleType(module_name)
    sys.modules[module_name] = module

    spec = MCPClientSpec(
        name="missing",
        provider="custom",
        module=module_name,
        class_name="DoesNotExist",
    )

    try:
        with pytest.raises(AttributeError):
            _instantiate_mcp_client(spec)
    finally:
        sys.modules.pop(module_name, None)


def test_instantiate_mcp_client_unknown_provider_returns_stub() -> None:
    spec = MCPClientSpec(name="mystery", provider="unknown")
    client = _instantiate_mcp_client(spec)
    assert isinstance(client, MCPClientStub)
    assert client.parameters["provider"] == "unknown"


def test_workflow_context_initialises_mcp_stub(workflow_context: WorkflowContext) -> None:
    workflow_context.wrap_mcp_nodes = True
    workflow_context.reset_mcp_clients()

    clients = workflow_context.ensure_mcp_clients()

    assert "default_stub" in clients
    assert isinstance(clients["default_stub"], MCPClientStub)


def test_wrap_mcp_decorator_initialises_clients(workflow_context: WorkflowContext) -> None:
    workflow_context.wrap_mcp_nodes = True
    workflow_context.reset_mcp_clients()

    @wrap_mcp
    async def noop(state: Dict[str, Any], workflow_context: WorkflowContext) -> Dict[str, Any]:
        return state

    asyncio.run(noop({}, workflow_context))

    assert "default_stub" in workflow_context.mcp_clients


def test_resolve_mcp_client_optional_returns_stub(workflow_context: WorkflowContext) -> None:
    workflow_context.wrap_mcp_nodes = True
    workflow_context.reset_mcp_clients()

    class DummyTool(BaseTool):
        tool_name = "dummy"

        async def _run_async_internal(
            self, tool_input: Dict[str, Any], workflow_id: str
        ) -> Dict[str, Any]:
            return {}

    tool = DummyTool(workflow_context)
    stub = resolve_mcp_client(tool, "nonexistent", optional=True)

    assert isinstance(stub, MCPClientStub)
    assert tool.get_mcp_client("nonexistent") is stub


def test_resolve_mcp_client_required_raises_without_fallback(workflow_context: WorkflowContext) -> None:
    workflow_context.config._config["mcp_config"]["fallback_mode"] = "error"
    workflow_context._load_mcp_config()
    workflow_context.reset_mcp_clients()

    class DummyTool(BaseTool):
        tool_name = "dummy-required"

        async def _run_async_internal(
            self, tool_input: Dict[str, Any], workflow_id: str
        ) -> Dict[str, Any]:
            return {}

    tool = DummyTool(workflow_context)

    with pytest.raises(KeyError):
        resolve_mcp_client(tool, "nonexistent", optional=False)


def test_dynamic_tool_loader_respects_mcp_requirements(workflow_context: WorkflowContext, tmp_path) -> None:
    workflow_context.wrap_mcp_nodes = True
    workflow_context.reset_mcp_clients()

    tool_dir = tmp_path / "generated_tools_v10_7"
    tool_dir.mkdir()
    tool_file = tool_dir / "mcp_tool.py"
    tool_code = """
from core_v10_7 import BaseTool, BaseToolOutput, track_metrics

class MCPSampleTool(BaseTool):
    tool_name = "mcp_sample_tool"
    required_mcp_clients = ["default_stub"]
    optional_mcp_clients = ["aux_client"]

    @track_metrics('tool_dynamic_test')
    async def _run_async_internal(self, tool_input, workflow_id):
        client = self.get_mcp_client('default_stub')
        return {"status": client.parameters.get("note", "missing")}
"""
    tool_file.write_text(tool_code)

    workflow_context.config.meta_loop_config._data["generated_tools_path"] = str(tool_dir)

    dynamic_tools = load_dynamic_tools(workflow_context, debug_mode=False)

    assert "mcp_sample_tool" in dynamic_tools
    tool_instance = dynamic_tools["mcp_sample_tool"]
    result = asyncio.run(tool_instance._run_async_internal({}, "wf"))
    assert result["status"] == "Default stub MCP client for testing"


def test_optional_mcp_client_failure_falls_back_to_stub(
    workflow_context: WorkflowContext,
) -> None:
    module_name = "optional_failure_mcp"
    module = types.ModuleType(module_name)

    class BrokenClient:
        def __init__(self, **_kwargs):
            raise RuntimeError("boom")

    module.BrokenClient = BrokenClient
    sys.modules[module_name] = module

    workflow_context.config._config["mcp_config"]["fallback_mode"] = "error"
    workflow_context.config._config["mcp_config"]["clients"].append(
        {
            "name": "optional_broken",
            "provider": "custom",
            "module": module_name,
            "class_name": "BrokenClient",
            "parameters": {"note": "from optional"},
            "optional": True,
        }
    )
    try:
        workflow_context._load_mcp_config()
        workflow_context.reset_mcp_clients()
        clients = workflow_context.ensure_mcp_clients()

        assert "optional_broken" in clients
        stub = clients["optional_broken"]
        assert isinstance(stub, MCPClientStub)
        assert stub.parameters["note"] == "from optional"
        assert "error" in stub.parameters
    finally:
        sys.modules.pop(module_name, None)


def test_required_mcp_client_failure_raises_error(
    workflow_context: WorkflowContext,
) -> None:
    module_name = "required_failure_mcp"
    module = types.ModuleType(module_name)

    class BrokenClient:
        def __init__(self, **_kwargs):
            raise RuntimeError("boom")

    module.BrokenClient = BrokenClient
    sys.modules[module_name] = module

    workflow_context.config._config["mcp_config"]["fallback_mode"] = "error"
    workflow_context.config._config["mcp_config"]["clients"].append(
        {
            "name": "required_broken",
            "provider": "custom",
            "module": module_name,
            "class_name": "BrokenClient",
            "parameters": {"note": "from required"},
            "optional": False,
        }
    )

    try:
        workflow_context._load_mcp_config()
        workflow_context.reset_mcp_clients()

        with pytest.raises(MCPClientInitializationError):
            workflow_context.ensure_mcp_clients()
    finally:
        sys.modules.pop(module_name, None)


def test_get_mcp_client_returns_fallback_stub_when_configured(
    workflow_context: WorkflowContext,
) -> None:
    workflow_context.config._config["mcp_config"]["fallback_mode"] = "stub"
    workflow_context.config._config["mcp_config"]["fallback_parameters"] = {"source": "test"}
    workflow_context._load_mcp_config()
    workflow_context.reset_mcp_clients()

    missing = workflow_context.get_mcp_client("auto_stub")
    assert isinstance(missing, MCPClientStub)
    assert missing.parameters["source"] == "test"


def test_wrap_mcp_sync_force_initialises_clients(
    workflow_context: WorkflowContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    workflow_context.wrap_mcp_nodes = False
    calls = {"count": 0}

    def fake_ensure() -> Dict[str, Any]:
        calls["count"] += 1
        return {}

    monkeypatch.setattr(workflow_context, "ensure_mcp_clients", fake_ensure)

    @wrap_mcp(force=True)
    def handler(state: Dict[str, Any], workflow_context: WorkflowContext) -> Dict[str, Any]:
        return state

    result = handler({}, workflow_context)

    assert result == {}
    assert calls["count"] == 1


def test_wrap_mcp_sync_skips_when_disabled(
    workflow_context: WorkflowContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    workflow_context.wrap_mcp_nodes = False
    calls = {"count": 0}

    def fake_ensure() -> Dict[str, Any]:
        calls["count"] += 1
        return {}

    monkeypatch.setattr(workflow_context, "ensure_mcp_clients", fake_ensure)

    @wrap_mcp
    def handler(state: Dict[str, Any], workflow_context: WorkflowContext) -> Dict[str, Any]:
        return state

    result = handler({}, workflow_context)

    assert result == {}
    assert calls["count"] == 0

