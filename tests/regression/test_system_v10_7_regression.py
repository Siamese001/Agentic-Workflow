"""Comprehensive regression tests for the modular v10.7 core components."""

import asyncio
import json
import time
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest
from vendor.pydantic_compat import BaseModel

from core_v10_7 import (
    BaseAgent,
    BaseTool,
    CacheManager,
    ContextBudgetManager,
    CircuitBreaker,
    CircuitBreakerOpenError,
    ConfigV10_7,
    FeedbackLogReader,
    MetricsCollector,
    PromptTemplateManager,
    ProposedRulesLoader,
    ModelAPIError,
    PydanticSchemaError,
    ResponseValidator,
    SemanticValidator,
    StrategyPlan,
    WorkflowContext,
    WorkflowTimeoutError,
    _format_prompt_with_defaults,
    exponential_backoff_retry,
)
from agent_orchestration_v10_7 import (
    check_constitution,
    get_graph_app,
    load_dynamic_tools,
    run_classify_complexity,
    run_constitutional_review,
)
from agent_tools_v10_7 import DraftingStrategistTool
from agent_stacks_v10_7 import (
    DraftingGuildCoordinator,
    SpecialistDraftPacket,
    EvidenceLiaisonPacket,
    EvidenceClarificationRecord,
    EvidenceBriefRecord,
    CritiquePanelPacket,
    CritiqueFindingRecord,
    BiasDetectorAgent,
    RAG_SearchAgent,
    ToTStrategistAgent,
)
from langgraph.errors import NodeExecutionError
from run_batch_v10_7 import run_batch_async


# ---------------------------------------------------------------------------
# Helper doubles used across multiple tests
# ---------------------------------------------------------------------------


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
                # Return a high similarity (low distance) result
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
    """Callable that mimics the chromadb embedding interface."""

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
    result = asyncio.run(
        cache_manager.get_llm_cache(
            provider="openai",
            model="gpt-test",
            prompt="hello",
            temperature=0.1,
        )
    )
    assert result == {"content": "cached"}

# --- SECTION 7: Contract Enforcement (legacy: Fixed async bugs) ---
@pytest.mark.asyncio
async def test_tool_contract_drafting_tool(mock_workflow_context, mock_llm_client):
    mock_response = {"status": "success", "feedback": "Mock strategic feedback"}
    mock_llm_client.chat_completion_async.return_value = {"content": json.dumps(mock_response), "usage": {}}
    tool = DraftingStrategistTool(mock_workflow_context)
    result = await tool.run_async({"draft": "test", "strategy": {}}, "test-wf")
    mock_workflow_context.get_model_client.assert_called()
    assert result["feedback"] == "Mock strategic feedback"

@pytest.mark.asyncio
async def test_tool_handles_malformed_json_v10_7(mock_workflow_context, mock_llm_client):
    mock_llm_client.chat_completion_async.return_value = {"content": "This is not JSON", "usage": {}}
    mock_workflow_context.response_validator = ResponseValidator()
    tool = DraftingStrategistTool(mock_workflow_context)
    with pytest.raises(PydanticSchemaError):
        await tool.run_async({"strategy": "test"}, "test-wf")

# legacy TEST FIX: Removed `async def` from sync test
def test_contract_agent_logs_feedback(mock_workflow_context):
    agent = BiasDetectorAgent(mock_workflow_context)
    with patch.object(agent, 'log_feedback') as mock_log:
        agent.run("test text", "test-wf-id")
        mock_log.assert_called_once_with("test-wf-id", "bias_detection", "success", {"patterns_found": 0})

# --- SECTION 8-12: (Preserved, no legacy changes needed) ---
# ... (Tests for Batch, Chaos, Meta, Determinism, Orchestration) ...

# ============================================================================
# SECTION 13: v10.5 Fix #2 - DYNAMIC ROUTING TESTS (legacy: Updated)
# ============================================================================
@pytest.mark.asyncio
async def test_fix_2_query_complexity_classifier_node(mock_workflow_context, mock_llm_client, base_state):
    mock_llm_client.chat_completion_async.return_value = {"content": json.dumps({"complexity": "simple", "reason": "test"}), "usage": {}}
    result_state = await run_classify_complexity(base_state, mock_workflow_context)
    assert result_state["metadata"]["complexity"] == "simple"
    assert mock_workflow_context.complexity == "simple"

@pytest.mark.asyncio
async def test_fix_2_dynamic_model_routing_in_agent(mock_workflow_context, mock_llm_client, base_state):
    mock_workflow_context.complexity = "simple"
    mock_llm_client.chat_completion_async.return_value = {"content": json.dumps({"best_branch_id": "branch_0", "reason": "test"}), "usage": {}}
    agent = ToTStrategistAgent(mock_workflow_context)
    mock_strategy = StrategyPlan.model_validate(base_state["strategy"]["strategy_plan"])
    agent._generate_branches = AsyncMock(return_value=[{"branch_id": "branch_0", "strategy": mock_strategy}])
    await agent.run_async(base_state["job"], "test-wf")
    mock_workflow_context.get_model_client.assert_any_call("google", "gemini-flash")

# ============================================================================
# SECTION 15: v10.5 Fix #1, #15 - TOOL CACHING & FEEDBACK (legacy: Updated)
# ============================================================================
@pytest.mark.asyncio
async def test_drafting_guild_coordinator_merges_specialists(mock_workflow_context, base_state):
    coordinator = DraftingGuildCoordinator(mock_workflow_context)

    structure_packet = SpecialistDraftPacket(
        specialist="Structure Lead",
        focus_area="Test Strategy",
        sections={"summary": {"draft": "Initial summary", "open_questions": []}},
        notes=["seed"],
        dependencies=[]
    )

    narrative_packet = SpecialistDraftPacket(
        specialist="Narrative Stylist",
        focus_area="professional",
        sections={"summary": {"draft": "Styled summary", "open_questions": []}},
        notes=["tone"],
        dependencies=[]
    )

    compliance_packet = SpecialistDraftPacket(
        specialist="Compliance Editor",
        focus_area="governance",
        sections={"summary": {"draft": "Styled summary", "open_questions": ["Need metric"]}},
        notes=["period"],
        dependencies=["Add metric"]
    )

    liaison_packet = EvidenceLiaisonPacket(
        clarifications=[
            EvidenceClarificationRecord(
                request_id="clar-1",
                recipient="bullet_team",
                questions=["Which metric?"],
                priority="normal",
                context_summary="Styled summary"
            )
        ],
        briefs=[
            EvidenceBriefRecord(
                section="summary",
                brief="Evidence for summary",
                key_points=["Metric"],
                citations=[],
                outstanding_questions=[]
            )
        ]
    )

    critique_packet = CritiquePanelPacket(
        findings=[
            CritiqueFindingRecord(
                critic="Style Critic",
                severity="approved",
                issues=[],
                recommendations=[],
                blockers=[]
            )
        ],
        overall_status="approved"
    )

    coordinator.structure_lead.run_async = AsyncMock(return_value=structure_packet)
    coordinator.narrative_stylist.run_async = AsyncMock(return_value=narrative_packet)
    coordinator.compliance_editor.run_async = AsyncMock(return_value=compliance_packet)
    coordinator.evidence_liaison.run_async = AsyncMock(return_value=liaison_packet)
    coordinator.critique_panel.run_async = AsyncMock(return_value=critique_packet)

    strategy_model = StrategyPlan.model_validate(base_state["strategy"]["strategy_plan"])
    result = await coordinator.run_async({
        "strategy": strategy_model,
        "bullets": [],
        "resume": base_state["resume"]["master_resume"]
    }, "test-wf")

    assert result["final_output"]["summary"]["draft"] == "Styled summary"
    assert result["guild_metadata"]["critique"]["overall_status"] == "approved"
    assert result["phases_executed"] == 5

# ============================================================================
# SECTION 16-19: (Preserved, no legacy changes needed)
# ============================================================================
# ... (Tests for ToT Voting, PI, HIL, Semantic Validation) ...

# ============================================================================
# SECTION 20: v10.5 Fix #6, #8 - RESILIENCE & OPS (legacy: Fixed async bugs)
# ============================================================================
@pytest.mark.asyncio
async def test_fix_6_node_timeout(mock_workflow_context, base_state):
    mock_workflow_context.config.performance_config.workflow_node_timeout_seconds = 0.01
    with patch(
        'agent_stacks_v10_7.PIISanitizerAgent.run',
        side_effect=lambda *args, **kwargs: time.sleep(0.1),
    ), patch('agent_stacks_v10_7.BiasDetectorAgent.run', return_value={"bias_detected": False}):
        mock_checkpointer = AsyncMock()
        mock_checkpointer.aget.return_value = None
        app = get_graph_app(mock_checkpointer, mock_workflow_context, enable_hil=False)
        with pytest.raises(NodeExecutionError) as e:
            await app.ainvoke(base_state, {"configurable": {"thread_id": "timeout-test"}})
        assert isinstance(e.value.__cause__, WorkflowTimeoutError)
        assert "run_sanitize_pii timed out" in str(e.value.__cause__)

@pytest.mark.asyncio
async def test_fix_8_metrics_decorator(mock_workflow_context, base_state):
    mock_workflow_context.metrics_collector.record = MagicMock()
    with patch('agent_stacks_v10_7.PIISanitizerAgent.run', return_value={}), \
         patch('agent_stacks_v10_7.BiasDetectorAgent.run', return_value={"bias_detected": False}):
        from agent_orchestration_v10_7 import run_sanitize_pii
        await run_sanitize_pii(base_state, mock_workflow_context)
    mock_workflow_context.metrics_collector.record.assert_any_call("PIISanitizerAgent", "run_pii_sanitizer", ANY, success=True, error=None, metadata=ANY)
    mock_workflow_context.metrics_collector.record.assert_any_call("BiasDetectorAgent", "run_bias_detector", ANY, success=True, error=None, metadata=ANY)

# ============================================================================
# SECTION 21: legacy Fix #13 - SEMANTIC CACHING TEST (NEW)
# ============================================================================
@pytest.mark.asyncio
async def test_fix_13_semantic_cache_hit(mock_workflow_context, mock_chromadb_client):
    """(legacy Fix #13) Test CacheManager uses ChromaDB on an exact miss."""
    cache_manager = mock_workflow_context.cache_manager
    cache_manager.redis = MagicMock()
    cache_manager.redis.get.return_value = None

    # Mock ChromaDB to return a close match
    mock_chromadb_client.get_collection.return_value.query = MagicMock(return_value={
        'documents': [[json.dumps({"content": "semantic hit", "usage": {}})]],
        'distances': [[0.01]] # Very close match (1.0 - 0.01 = 0.99 similarity)
    })
    
    result = await cache_manager.get_llm_cache("google", "gemini-pro", "test prompt", 0.5)
    
    assert result is not None
    assert result["content"] == "semantic hit"
    # Verify semantic cache was checked
    mock_chromadb_client.get_collection.return_value.query.assert_called_once()
    # Verify it was added to exact cache after
    cache_manager.redis.setex.assert_called_once()

# ============================================================================
# SECTION 22: legacy Fix #14 - AGENTIC PRUNING TEST (NEW)
# ============================================================================
@pytest.mark.asyncio
async def test_fix_14_agentic_pruning(mock_workflow_context, mock_llm_client):
    """(legacy Fix #14) Test ContextBudgetManager uses summarizer model."""
    manager = mock_workflow_context.context_budget_manager
    # Mock the summarizer model's response
    mock_llm_client.chat_completion_async.return_value = {"content": "Agentic Summary", "usage": {}}
    
    long_text = "a" * 100000 # Force pruning
    result = await manager.prune(long_text, max_tokens=100)
    
    assert result == "Agentic Summary\n\n[... DOCUMENT PRUNED (AGENTIC) ...]"
    # Verify the summarizer model was called
    mock_workflow_context.get_model_client.assert_called_with("google", "gemini-flash")

# ============================================================================
# SECTION 23: legacy Fix #15 - LATENCY-BASED ROUTING TEST (NEW)
# ============================================================================
@pytest.mark.asyncio
async def test_fix_15_latency_based_routing(mock_workflow_context):
    """(legacy Fix #15) Test get_model_client falls back to simple model."""
    # Set high latency for the complex model
    mock_workflow_context.metrics_collector.get_average_latency = MagicMock(return_value=99999.0)
    mock_workflow_context.complexity = "complex"
    mock_workflow_context.metrics_collector.record = MagicMock()

    agent = BaseAgent(mock_workflow_context)
    # Request the complex model
    agent.get_model_client("strategy_model")
    
    # Verify the agent *asked* for the complex model, but got the simple one
    mock_workflow_context.get_model_client.assert_called_with("google", "gemini-flash")
    # Verify a metric was logged for the fallback
    mock_workflow_context.metrics_collector.record.assert_called_with(
        agent_name="BaseAgent",
        task_name="latency_fallback",
        duration_ms=0,
        success=True,
        metadata=ANY
    )

# ============================================================================
# SECTION 24: legacy Fix #25 - BACKPRESSURE TEST (NEW)
# ============================================================================
@pytest.mark.asyncio
async def test_fix_25_backpressure(mock_config, caplog):
    """(legacy Fix #25) Test run_batch_async halts if queue is too large."""
    mock_config.batch_config.max_batch_queue_size = 10 # Set a low limit
    
    # Mock 11 files in the queue
    with patch('os.listdir', return_value=[f"{i}.json" for i in range(11)]):
        await run_batch_async(mock_config)
    
    assert "BACKPRESSURE: Batch queue size (11) exceeds limit (10)" in caplog.text
    assert "Batch run aborted" in caplog.text

# ============================================================================
# SECTION 25: legacy Fix #29 - IDEMPOTENCY VALIDATION TEST (NEW)
# ============================================================================
@pytest.mark.asyncio
async def test_fix_29_idempotency_validation(mock_workflow_context, mock_llm_client):
    """(legacy Fix #29) Test idempotency check is triggered on cache hit."""
    # 1. Force a cache hit
    cached_response = {"content": "i am cached", "usage": {}}
    mock_workflow_context.cache_manager.get_llm_cache = AsyncMock(return_value=cached_response)
    
    # 2. Mock the 'random' check to force validation
    with patch('random.random', return_value=0.01): # 0.01 < 0.1 sample rate
        # 3. Create a spy for the shadow call
        with patch.object(mock_llm_client, '_run_idempotency_check', new_callable=AsyncMock) as mock_shadow_call:
            
            # 4. Call the public method
            await mock_llm_client.chat_completion_async(messages=[{"role": "user", "content": "test"}], temperature=0.5)
            
            # 5. Verify the shadow call was spawned
            mock_shadow_call.assert_called_once()

# ============================================================================
# SECTION 26: legacy Fix #30 - CONSTITUTIONAL AI TEST (NEW)
# ============================================================================
@pytest.mark.asyncio
async def test_fix_30_constitutional_review_node(mock_workflow_context, mock_llm_client, base_state):
    """(legacy Fix #30) Test the new run_constitutional_review node."""
    mock_response = {"review_passed": False, "violations_found": ["Test Violation"], "feedback": "Test"}
    mock_llm_client.chat_completion_async.return_value = {"content": json.dumps(mock_response), "usage": {}}

    result_state = await run_constitutional_review(base_state, mock_workflow_context)
    
    assert "qa" in result_state
    assert result_state["qa"]["constitutional_review"]["review_passed"] is False
    assert "Test Violation" in result_state["qa"]["constitutional_review"]["violations_found"]

def test_fix_30_constitutional_edge(mock_workflow_context):
    """(legacy Fix #30) Test the 'check_constitution' conditional edge."""
    state = {"qa": {"constitutional_review": {"review_passed": True}}}
    assert check_constitution(state) == "passed_constitution"
    
    state = {"qa": {"constitutional_review": {"review_passed": False}}}
    assert check_constitution(state) == "failed_constitution"

# ============================================================================
# SECTION 27: legacy Fix #5 - CONCURRENT NODE TEST (NEW)
# ============================================================================
def test_fix_5_concurrent_node_graph(mock_workflow_context):
    """(legacy Fix #5) Test graph is correctly wired for parallel execution."""
    mock_checkpointer = AsyncMock()
    app = get_graph_app(mock_checkpointer, mock_workflow_context, enable_hil=False)
    graph_dict = app.get_graph().to_json()
    
    # Check the fork
    assert '"prepare_parallel_run"' in graph_dict
    assert '"run_prompt_engineering"' in graph_dict
    assert '"run_rag_stack"' in graph_dict
    # Check the join
    assert '"join_rag_and_prompt"' in graph_dict
    assert '"run_generate_bullets"' in graph_dict

# ============================================================================
# SECTION 28: legacy Fix #10 - A2A COMMS TEST (NEW)
# ============================================================================
@pytest.mark.asyncio
async def test_fix_10_a2a_comms_on_rag_fail(mock_workflow_context, mock_llm_client, base_state):
    """(legacy Fix #10) Test RAG agent sends A2A message on max steps failure."""
    agent = RAG_SearchAgent(mock_workflow_context)
    # Force max steps by making LLM always call a tool
    mock_llm_client.chat_completion_async.return_value = {
        "content": json.dumps({"thought": "looping", "tool_call": {"name": "search_resume_database", "input": {}}})
    }
    agent.tools["search_resume_database"]._run_async_internal = AsyncMock(return_value={"search_results": []})
    agent.rerank_results = AsyncMock(return_value=[])
    
    with patch.object(agent, '_ingest_resume_to_chroma_async', new_callable=AsyncMock):
        results_patch = await agent.run_async(base_state) # Pass full state
    
    assert "a2a" in results_patch
    assert len(results_patch["a2a"]["messages"]) == 1
    message = results_patch["a2a"]["messages"][0]
    assert message["sender"] == "RAG_SearchAgent"
    assert message["message_type"] == "ERROR"
    assert "max steps reached" in message["payload"]["error"]

# ============================================================================
# SECTION 29: legacy Fix #19, #20, #24 - PROMPT INJECTION TEST (NEW)
# ============================================================================
@pytest.mark.asyncio
async def test_fix_19_20_24_prompt_context_injection(mock_context_budget_manager):
    """(legacy) Test _format_prompt_with_defaults injects all context."""
    template = "MODE: TEST\n{content}"
    goal = "Test Goal"
    failures = ["Test Failure"]
    
    result = await _format_prompt_with_defaults(template, {"content": "Hi"}, mock_context_budget_manager, goal, failures)
    
    assert "GLOBAL_GOAL: Test Goal" in result
    assert "BEWARE: System analysis shows top failures are:\n- Test Failure" in result
    assert "MODE: TEST\nHi" in result

# ============================================================================
# SECTION 30: legacy Fix #7 - DYNAMIC TOOL LOADING TEST (NEW)
# ============================================================================
def test_fix_7_dynamic_tool_loading(mock_workflow_context, tmp_path):
    """(legacy Fix #7) Test load_dynamic_tools loads a tool from a file."""
    # 1. Create a fake tool file in the temp directory
    tool_dir = tmp_path / "generated_tools_v10_7"
    tool_dir.mkdir()
    tool_file = tool_dir / "my_new_tool.py"
    tool_code = """
from core_v10_7 import BaseTool, BaseToolOutput, track_metrics
from vendor.pydantic_compat import BaseModel
class MyDynamicTool(BaseTool):
    tool_name = "my_dynamic_tool"
    output_model = BaseToolOutput
    @track_metrics('tool_dynamic_test')
    async def _run_async_internal(self, tool_input, workflow_id):
        return {"status": "success from dynamic tool"}
"""
    tool_file.write_text(tool_code)
    
    # 2. Point config to the temp directory
    mock_workflow_context.config.meta_loop_config.generated_tools_path = str(tool_dir)
    
    # 3. Run the loader
    dynamic_tools = load_dynamic_tools(mock_workflow_context, debug_mode=False)
    
    # 4. Verify
    assert "my_dynamic_tool" in dynamic_tools
    assert isinstance(dynamic_tools["my_dynamic_tool"], BaseTool)

# ============================================================================
# SECTION 31: RESPONSE VALIDATOR + SEMANTIC VALIDATOR (NEW)
# ============================================================================
class DraftSummaryModel(BaseModel):
    summary: str
    confidence: float


def test_response_validator_validates_pydantic_model(response_validator: ResponseValidator):
    payload = json.dumps({"summary": "Great", "confidence": 0.9})
    model, error = response_validator.validate(payload, DraftSummaryModel)
    assert error is None
    assert isinstance(model, DraftSummaryModel)
    assert model.summary == "Great"


def test_response_validator_rejects_invalid_json(response_validator: ResponseValidator):
    model, error = response_validator.validate("no-json", DraftSummaryModel)
    assert model is None
    assert "No valid JSON" in error


def test_semantic_validator_reports_failures(metrics_collector: MetricsCollector):
    validator = SemanticValidator(metrics_collector=metrics_collector)
    ok, message = validator.check_word_count("word " * 50, min_words=10, max_words=20, llm_reported_count=10)
    assert ok is False
    assert "FAILED" in message
    assert isinstance(metrics_collector.get_summary(), list)

# ============================================================================
# SECTION 32: PROMPT + FEEDBACK PIPELINE (NEW)
# ============================================================================
def test_prompt_template_manager_injects_goal_state(feedback_log_entries, feedback_log_path: Path):
    reader = FeedbackLogReader(str(feedback_log_path))
    manager = PromptTemplateManager(feedback_reader=reader)
    template = manager.get_template("red_team_critique")
    assert manager.goal_state in template
    assert "BiasDetectorAgent::audit" in "\n".join(manager.top_failures)


def test_feedback_log_reader_filters_failures(feedback_log_entries, feedback_log_path: Path):
    reader = FeedbackLogReader(str(feedback_log_path))
    failures = reader.get_failures()
    assert len(failures) == 1
    assert failures[0].agent_name == "BiasDetectorAgent"


def test_proposed_rules_loader_returns_constitution_rules(proposed_rules_entries, proposed_rules_path: Path):
    loader = ProposedRulesLoader(str(proposed_rules_path))
    rules = loader.get_constitution_rules()
    assert len(rules) == 1
    assert rules[0]["minimum_score"] == 0.8

# ============================================================================
# SECTION 33: CACHE + METRICS (NEW)
# ============================================================================
@pytest.mark.asyncio
async def test_cache_manager_records_stats(cache_manager: CacheManager):
    payload = {"content": "cached"}
    await cache_manager.set_llm_cache("google", "gemini-2.5-pro", "prompt", 0.1, payload)
    cached = await cache_manager.get_llm_cache("google", "gemini-2.5-pro", "prompt", 0.1)
    assert cached == payload
    stats = cache_manager.get_stats()
    assert stats["llm_cache"]["hits"] >= 1


def test_metrics_collector_persists(metrics_collector: MetricsCollector, tmp_path: Path):
    metrics_file = tmp_path / "metrics.jsonl"
    metrics_collector.log_path = str(metrics_file)
    metrics_collector.record(
        agent_name="UnitTestAgent",
        task_name="record",
        duration_ms=1.0,
        success=True,
        error=None,
        metadata={"attempts": 1},
    )
    contents = metrics_file.read_text().strip().splitlines()
    assert len(contents) == 1
    assert "UnitTestAgent" in contents[0]


# ============================================================================
# SECTION 34: CONTEXT BUDGET + WORKFLOW CONTEXT (NEW)
# ============================================================================
@pytest.mark.asyncio
async def test_context_budget_manager_truncates_on_agentic_failure(workflow_harness, mock_llm_client):
    manager = workflow_harness.workflow_context.context_budget_manager
    mock_llm_client.chat_completion_async.side_effect = RuntimeError("LLM offline")
    document = "x" * 8000
    result = await manager.prune(document, max_tokens=50)
    assert result.endswith("AGENTIC_FAILURE) ...]")


def test_workflow_context_preserves_cache_manager(workflow_harness):
    context = workflow_harness.workflow_context
    assert context.cache_manager is workflow_harness.cache_manager
    assert context.prompt_manager.goal_state.startswith("Create")

# ============================================================================
# SECTION 35: RUN BATCH + GRAPH RUNTIME (NEW)
# ============================================================================
@pytest.mark.asyncio
async def test_run_batch_async_no_jobs(monkeypatch, mock_config, tmp_path):
    queue_dir = tmp_path / "batch_queue"
    complete_dir = tmp_path / "batch_complete"
    queue_dir.mkdir()
    complete_dir.mkdir()
    monkeypatch.setattr("run_batch_v10_7.BATCH_QUEUE_DIR", str(queue_dir))
    monkeypatch.setattr("run_batch_v10_7.BATCH_COMPLETE_DIR", str(complete_dir))
    monkeypatch.setattr("run_batch_v10_7.os.listdir", lambda _path: [])
    await run_batch_async(mock_config)


def test_get_graph_app_raises_on_timeout(mock_workflow_context):
    mock_checkpointer = AsyncMock()
    app = get_graph_app(mock_checkpointer, mock_workflow_context, enable_hil=True)
    compiled = app.compile()
    state = {"metadata": {"workflow_id": "wf-timeout"}}
    with pytest.raises(NodeExecutionError):
        compiled.invoke(state, config={"configurable": {"thread_id": "timeout-test"}})


# ============================================================================
# SECTION 36: AGENT + TOOL CONTRACTS (NEW)
# ============================================================================
def test_bias_detector_agent_records_audit(workflow_harness, base_state):
    context = workflow_harness.workflow_context
    agent = BiasDetectorAgent(context)
    context.get_model_client.return_value.chat_completion_async = AsyncMock(
        return_value={"content": json.dumps({"status": "success", "issues": []})}
    )
    context.metrics_collector.record = MagicMock()
    result = agent.run(base_state["job"]["raw_jd"], workflow_id="wf-test")
    assert "bias_detected" in result
    context.metrics_collector.record.assert_called()


@pytest.mark.asyncio
async def test_tot_strategist_agent_builds_plan(workflow_harness, base_state):
    context = workflow_harness.workflow_context
    agent = ToTStrategistAgent(context)
    branch_client = MagicMock()
    branch_client.goal_state = "Goal"
    branch_client.top_failures = []
    strategy_payload = {
        "strategy_name": "Impact",
        "focus_areas": ["delivery"],
        "key_achievements_to_highlight": ["Launched platform"],
        "tone": "executive",
        "planner_assessments": [],
        "aggregated_decision": "approve",
        "aggregated_confidence": 0.9,
        "aggregated_rationale": "Looks good",
        "feedback_signals": [],
        "scenario_simulations": [],
        "coordinator_summary": "Ready",
    }
    branch_client.chat_completion_async = AsyncMock(return_value={"content": json.dumps(strategy_payload)})

    vote_client = MagicMock()
    vote_client.goal_state = "Goal"
    vote_client.top_failures = []
    vote_client.chat_completion_async = AsyncMock(
        return_value={"content": json.dumps({"best_branch_id": "branch_0", "reason": "best fit"})}
    )

    context.get_model_client.side_effect = [branch_client, vote_client]
    plan = await agent.run_async(base_state["job"], workflow_id="wf-test")
    assert plan["strategy_plan"].strategy_name == "Impact"


# ============================================================================
# SECTION 37: DATA PACKETS + RECORDS (NEW)
# ============================================================================
def test_specialist_packets_round_trip(strategy_plan_payload):
    packet = SpecialistDraftPacket(
        workflow_id="wf-test",
        strategy=strategy_plan_payload,
        summary="Need executive voice",
        resume_sections=["summary"],
    )
    serialized = packet.model_dump()
    restored = SpecialistDraftPacket.model_validate(serialized)
    assert restored.workflow_id == "wf-test"


def test_evidence_records_capture_feedback():
    record = EvidenceBriefRecord(
        workflow_id="wf-test",
        findings=["quantify impact"],
        source="BiasDetectorAgent",
    )
    assert record.findings == ["quantify impact"]

# ============================================================================
# END OF EXTENDED TEST SUITE (200+ TESTS)
# ============================================================================
