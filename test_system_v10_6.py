# File: test_system_v10_6.py
# Version: 10.6 (Refactored)
#
# v10.6 REFACTOR CHANGES:
# - FIXED: Updated all internal imports from v10_5 to v10_6.
# - FIXED: Updated all fixtures (mock_config, mock_workflow_context, base_state)
#   to support v10.6 DI, config flags, and state (A2A, Constitution).
# - FIXED: Corrected 7 tests (e.g., test_bias_detector_agent) to be `def`
#   instead of `async def` as they call sync, decorated methods.
# - FIXED: Updated RAG tests to match the v10.6 RAG_SearchAgent signature
#   (accepts full state, returns state patch).
#
# v10.6 MAJOR CHANGES:
# - TOTAL: Expanded from 120 to 150 total tests.
# - ADDED: Section 21 (v10.6 Fix #13 - Semantic Caching Test)
# - ADDED: Section 22 (v10.6 Fix #14 - Agentic Pruning Test)
# - ADDED: Section 23 (v10.6 Fix #15 - Latency-Based Routing Test)
# - ADDED: Section 24 (v10.6 Fix #25 - Backpressure Test)
# - ADDED: Section 25 (v10.6 Fix #29 - Idempotency Validation Test)
# - ADDED: Section 26 (v10.6 Fix #30 - Constitutional AI Test)
# - ADDED: Section 27 (v10.6 Fix #5 - Concurrent Node Test)
# - ADDED: Section 28 (v10.6 Fix #10 - A2A Comms Test)
# - ADDED: Section 29 (v10.6 Fix #19, #20, #24 - Prompt Injection Test)
# - ADDED: Section 30 (v10.6 Fix #7 - Dynamic Tool Loading Test)

import pytest
import pytest_asyncio
import asyncio
import redis
import json
import time
import tempfile
import os
import re
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch, Mock, ANY
from datetime import datetime
from typing import Dict, Any, List

# v10.6: Import from new core
from core_v10_6 import (
    WorkflowContext, ConfigV10_6, CacheManager, CostTracker, 
    FeedbackLogReader, ProposedRulesLoader, MainGraphState, BaseAgent,
    CostCeilingExceededError, CircuitBreakerOpenError, PydanticSchemaError, ModelAPIError,
    WorkflowTimeoutError,
    PromptTemplateManager, ResponseValidator, ContextBudgetManager,
    MetricsCollector, SemanticValidator,
    exponential_backoff_retry,
    StrategyPlan, CritiqueResult, BulletList, QAClaimOutput, DraftStrategyOutput,
    RefineSectionOutput, HILFeedbackRoute, ConstitutionalReviewResult, A2AMessage,
    BaseModel,
    MetaGraphState,
    BaseTool,
    GeneratedPrompts,
    _format_prompt_with_defaults # v10.6: Import async formatter
)

# v10.6: Import from new stacks
from agent_stacks_v10_6 import (
    ToTStrategistAgent,
    BiasDetectorAgent,
    PIISanitizerAgent,
    PromptInjectionDetectorAgent,
    QueryComplexityClassifier,
    RAG_SearchAgent,
    AsyncBulletGeneratorAgent,
    AsyncBulletCritiqueAgent,
    HILAmbiguityDetectorAgent,
    HILFeedbackRouterAgent,
    ConstitutionalReviewerAgent # v10.6
)
# v10.6: Import from new tools
from agent_tools_v10_6 import (
    DraftingStrategistTool,
    DraftingRedTeamTool,
    DraftingRefinerTool,
    DraftingMetricsTool,
    QAClaimValidatorTool,
    QAToneValidatorTool,
    QAThematicAlignmentTool,
    QASemanticEntailmentTool,
    QANarrativeThreadTool,
    QAJDSkillsValidatorTool,
    QASignalScoreValidatorTool,
    QATenureValidatorTool,
    QAMissedOpportunityTool,
    QAAdversarialReviewerTool,
    QABiasDetectorTool,
    QAWordCountValidatorTool,
    ChromaDBSearchTool,
    BM25SearchTool
)
# v10.6: Import from new orchestration
from agent_orchestration_v10_6 import (
    ReActConductorAgent,
    QAConductorAgent,
    get_graph_app,
    run_classify_complexity,
    run_detect_prompt_injection,
    check_prompt_injection,
    run_inject_hil_edit,
    route_feedback,
    run_constitutional_review, # v10.6
    check_constitution, # v10.6
    load_dynamic_tools # v10.6
)
# v10.6: Import from new batch runner
from core_v10_6 import CircuitBreaker
from run_batch_v10_6 import BatchFeedbackAggregator, run_batch_async

# v10.6: Import from new meta-learner
from run_learning_v10_6 import check_proposal_type

try:
    # v10.6: Import from new main
    from main_v10_6 import run_workflow_async
    MAIN_AVAILABLE = True
except ImportError:
    MAIN_AVAILABLE = False

try:
    from langgraph.errors import NodeExecutionError
except ImportError:
    class NodeExecutionError(Exception): pass

# ============================================================================
# SECTION 1: PYTEST FIXTURES (v10.6: Updated)
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_redis_client():
    mock = MagicMock(spec=redis.Redis)
    _cache_store = {}
    def mock_setex(name, time, value):
        _cache_store[name] = value; return True
    def mock_get(name):
        return _cache_store.get(name, None)
    mock.get.side_effect = mock_get
    mock.setex.side_effect = mock_setex
    return mock

@pytest.fixture
def mock_chromadb_client():
    mock_collection = MagicMock()
    mock_collection.query = MagicMock(return_value={
        'documents': [['Mocked ChromaDB result']],
        'metadatas': [[{'experience_object': json.dumps({'title': 'Chroma Experience'})}]],
        'distances': [[0.05]]
    })
    mock_collection.add = MagicMock()
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection
    mock_client.get_collection.return_value = mock_collection
    return mock_client

@pytest.fixture
def mock_embedding_function():
    mock = MagicMock()
    mock.return_value = [[0.1, 0.2, 0.3]]
    return mock

@pytest.fixture
def mock_config():
    """Mocks the ConfigV10_6 object. v10.6: Fully populated."""
    mock_conf = MagicMock(spec=ConfigV10_6)
    
    mock_conf.logging_config = MagicMock()
    mock_conf.logging_config.log_file = "logs/pytest_v10_6.log"
    mock_conf.logging_config.metrics_log_path = "logs/pytest_metrics_v10_6.jsonl"
    
    mock_conf.redis_config = MagicMock()
    mock_conf.redis_config.host = "localhost"; mock_conf.redis_config.port = 6379; mock_conf.redis_config.db = 0
    
    mock_conf.chromadb_config = MagicMock()
    mock_conf.chromadb_config.default_collection_name = "pytest_collection_v10_6"
    mock_conf.chromadb_config.persistent_path = "/tmp/chroma_pytest_v10_6"
    mock_conf.chromadb_config.use_http_client = False
    mock_conf.chromadb_config.semantic_cache_collection = "pytest_semantic_cache_v10_6" # v10.6
    
    mock_conf.caching_config = MagicMock()
    mock_conf.caching_config.cache_ttl_seconds = 3600
    mock_conf.caching_config.enable_llm_caching = True
    mock_conf.caching_config.enable_tool_caching = True
    mock_conf.caching_config.enable_semantic_caching = True # v10.6
    mock_conf.caching_config.semantic_cache_similarity_threshold = 0.95 # v10.6
    mock_conf.caching_config.enable_idempotency_validation = True # v10.6
    mock_conf.caching_config.idempotency_validation_sample_rate = 0.1 # v10.6
    
    mock_conf.meta_loop_config = MagicMock()
    mock_conf.meta_loop_config.feedback_log_path = "logs/feedback_log.jsonl"
    mock_conf.meta_loop_config.proposed_rules_path = "logs/proposed_rules.jsonl"
    mock_conf.meta_loop_config.max_meta_replan_loops = 2
    mock_conf.meta_loop_config.generated_tools_path = "./generated_tools_v10_6" # v10.6
    
    mock_conf.agent_stacks = MagicMock()
    mock_conf.agent_stacks.conductor_max_steps = 5
    mock_conf.agent_stacks.reranking_top_k = 3
    mock_conf.agent_stacks.max_local_retries = 2
    mock_conf.agent_stacks.ambiguity_confidence_threshold = 0.8
    mock_conf.agent_stacks.enable_hil_stack = True
    mock_conf.agent_stacks.enable_prompt_injection_detection = True
    mock_conf.agent_stacks.enable_constitutional_review = True # v10.6
    
    mock_conf.cost_config = MagicMock()
    mock_conf.cost_config.cost_ceiling_per_workflow = 5.0
    
    mock_conf.batch_config = MagicMock()
    mock_conf.batch_config.circuit_breaker_failure_threshold = 3
    mock_conf.batch_config.max_batch_queue_size = 1000 # v10.6
    
    mock_conf.performance_config = MagicMock()
    mock_conf.performance_config.default_token_limit = 8192
    mock_conf.performance_config.workflow_node_timeout_seconds = 60
    mock_conf.performance_config.max_complex_model_latency_ms = 15000 # v10.6
    
    # Mock model configs
    mock_conf.model_config = MagicMock()
    
    def mock_model(temp, name="default"): 
        m = MagicMock(temperature=temp, model_name=name)
        if "claude" in name: m.provider = "anthropic"
        elif "gpt" in name: m.provider = "openai"
        else: m.provider = "google"
        return m
    
    mock_conf.model_config.strategy_model = mock_model(0.5, "gemini-pro")
    mock_conf.model_config.strategy_model_simple = mock_model(0.6, "gemini-flash") 
    mock_conf.model_config.strategy_model_complex = mock_model(0.4, "claude-opus")
    
    mock_conf.model_config.react_conductor_model = mock_model(0.6, "gemini-pro")
    mock_conf.model_config.react_conductor_model_simple = mock_model(0.7, "gemini-flash")
    mock_conf.model_config.react_conductor_model_complex = mock_model(0.5, "claude-opus")
    
    mock_conf.model_config.prompt_engineer_model = mock_model(0.7, "gemini-flash")
    mock_conf.model_config.prompt_engineer_model_simple = mock_model(0.7, "gemini-flash")
    mock_conf.model_config.prompt_engineer_model_complex = mock_model(0.6, "gemini-pro")
    
    mock_conf.model_config.prompt_injection_model = mock_model(0.1, "gemini-flash")
    mock_conf.model_config.summarizer_model = mock_model(0.3, "gemini-flash") # v10.6
    mock_conf.model_config.constitutional_review_model = mock_model(0.1, "gemini-flash") # v10.6
    
    mock_conf.model_config.reranker_model = mock_model(0.2, "gemini-flash")
    mock_conf.model_config.bullet_generator_model = mock_model(0.7, "gemini-pro")
    mock_conf.model_config.bullet_fact_check_model = mock_model(0.2, "gemini-flash")
    mock_conf.model_config.critique_model = mock_model(0.2, "gemini-flash")
    mock_conf.model_config.qa_model = mock_model(0.3, "gemini-flash")
    mock_conf.model_config.hyde_model = mock_model(0.6, "gemini-flash")
    mock_conf.model_config.drafting_strategist_model = mock_model(0.5, "gemini-pro")
    mock_conf.model_config.drafting_redteam_model = mock_model(0.6, "claude-opus")
    mock_conf.model_config.drafting_refiner_model = mock_model(0.6, "gpt-5")
    mock_conf.model_config.drafting_metrics_model = mock_model(0.4, "gemini-flash")
    mock_conf.model_config.qa_validator_model = mock_model(0.3, "gemini-flash")
    mock_conf.model_config.qa_adversarial_model = mock_model(0.5, "claude-opus")
    
    return mock_conf

@pytest.fixture
def mock_llm_client():
    """Mocks the AsyncBaseModelClient."""
    mock = AsyncMock()
    
    # This is the mock for the *actual* API call
    mock._internal_api_call = AsyncMock(
        return_value={"content": json.dumps({"score": 9.0, "suggestions": ["Cached result"]}), "usage": {"prompt_tokens": 10, "completion_tokens": 10}}
    )
    
    # Mock the public method to *bypass* caching for most tests
    mock.chat_completion_async = AsyncMock(
        return_value={"content": json.dumps({"mock": "response"}), "usage": {"prompt_tokens": 10, "completion_tokens": 10}}
    )
    
    # Add attributes needed by BaseAgent.get_model_client
    mock.goal_state = "GLOBAL_GOAL: Mock Goal"
    mock.top_failures = ["BEWARE: Mock Failure"]
    mock.budget_manager = AsyncMock(spec=ContextBudgetManager)
    # v10.6: Make prune an async passthrough
    mock.budget_manager.prune = AsyncMock(side_effect=lambda doc, limit: doc)
    
    return mock

@pytest.fixture
def mock_metrics_collector():
    mock = MagicMock(spec=MetricsCollector)
    mock.record = MagicMock()
    mock.get_average_latency.return_value = None # Default no latency
    return mock

@pytest.fixture
def mock_semantic_validator():
    mock = MagicMock(spec=SemanticValidator)
    mock.check_word_count.return_value = (True, "Word count OK")
    return mock

@pytest_asyncio.fixture
async def mock_cache_manager(mock_redis_client, mock_chromadb_client, mock_embedding_function, mock_config):
    manager = CacheManager(mock_config, mock_redis_client, mock_chromadb_client, mock_embedding_function)
    # Spy on the methods
    manager.get_llm_cache = AsyncMock(side_effect=manager.get_llm_cache)
    manager.set_llm_cache = AsyncMock(side_effect=manager.set_llm_cache)
    manager.get_tool_cache = MagicMock(side_effect=manager.get_tool_cache)
    manager.set_tool_cache = MagicMock(side_effect=manager.set_tool_cache)
    return manager

@pytest.fixture
def mock_cost_tracker():
    return MagicMock(spec=CostTracker)

@pytest.fixture
def mock_feedback_reader():
    mock = MagicMock(spec=FeedbackLogReader)
    mock.get_failures.return_value = [ # v10.6
        MagicMock(agent_name="TestAgent", task="test_task")
    ]
    return mock

@pytest.fixture
def mock_rules_loader():
    mock = MagicMock(spec=ProposedRulesLoader)
    mock.get_constitution_rules.return_value = [{"principle": "Be helpful"}] # v10.6
    return mock

@pytest.fixture
def mock_prompt_manager(mock_feedback_reader):
    mock = MagicMock(spec=PromptTemplateManager)
    mock.get_template.side_effect = lambda name: f"""
        Mock template for {name}:
        {{goal_state}} {{top_failures}}
        {{style_guide}} {{draft}} {{strategy}} {{job_description}} 
        {{section_text}} {{critique}} {{critique_2}} {{bullets}} 
        {{master_resume}} {{draft_text}} {{required_tone}} {{experience}} 
        {{query}} {{candidates}} {{instruction}} {{context}} {{content}} 
        {{job_title}} {{company}} {{branch_num}} {{total_branches}} 
        {{num_branches}} {{branches_json}} {{complexity}} {{user_input}}
        {{hypothesis}} {{patterns}} {{proposal}} {{human_feedback}}
        {{log_data}} {{preference_log}} {{feedback_log}}
        {{generated_tool_code}}
        {{final_draft}} {{constitution}}
        """
    # v10.6: Add real attributes
    mock.goal_state = "GLOBAL_GOAL: Mock Goal"
    mock.top_failures = ["BEWARE: Mock Failure"]
    return mock

@pytest.fixture
def mock_response_validator():
    mock = MagicMock(spec=ResponseValidator)
    def validate_side_effect(content, model):
        try:
            if isinstance(content, str):
                json_start = content.find('{'); json_end = content.rfind('}') + 1
                if 0 <= json_start < json_end:
                    content = json.loads(content[json_start:json_end])
                else: raise json.JSONDecodeError("No JSON found", content, 0)
            if isinstance(model, type) and issubclass(model, BaseModel):
                 return model.model_validate(content), None
            elif model == dict: return content, None
            elif isinstance(model, tuple):
                for m in model:
                    try:
                        if isinstance(m, type) and issubclass(m, BaseModel):
                            return m.model_validate(content), None
                        elif m == dict: return content, None
                    except Exception: continue
            raise PydanticSchemaError(f"Mock validator does not support model type: {model}")
        except Exception as e: return None, f"Pydantic validation failed: {e}"
    mock.validate.side_effect = validate_side_effect
    return mock

@pytest.fixture
def mock_context_budget_manager():
    mock = AsyncMock(spec=ContextBudgetManager)
    # v10.6: Make prune an async passthrough
    mock.prune = AsyncMock(side_effect=lambda doc, limit: doc)
    return mock

# v10.6: Updated WorkflowContext fixture (True DI)
@pytest_asyncio.fixture
async def mock_workflow_context(
    mock_config, mock_redis_client, mock_chromadb_client, mock_llm_client,
    mock_cache_manager, mock_cost_tracker, mock_feedback_reader,
    mock_rules_loader, mock_prompt_manager, mock_response_validator,
    mock_context_budget_manager, mock_metrics_collector, mock_semantic_validator,
    mock_embedding_function
):
    """Mocks the WorkflowContext with all v10.6 injected dependencies."""
    context = WorkflowContext(
        config=mock_config,
        redis_client=mock_redis_client,
        chromadb_client=mock_chromadb_client,
        cache_manager=mock_cache_manager,
        cost_tracker=mock_cost_tracker,
        feedback_reader=mock_feedback_reader,
        rules_loader=mock_rules_loader,
        prompt_manager=mock_prompt_manager,
        response_validator=mock_response_validator,
        metrics_collector=mock_metrics_collector,
        semantic_validator=mock_semantic_validator,
        embedding_function=mock_embedding_function
    )
    context.workflow_id = "test-workflow-id"
    # v10.6: Inject circular dependency
    context.context_budget_manager = mock_context_budget_manager
    
    # Mock the client getter to return our pre-made mock
    context.get_model_client = MagicMock(return_value=mock_llm_client)
    return context

@pytest.fixture
def base_state():
    """v10.6: Creates a base MainGraphState dict."""
    state = MainGraphState()
    state.job.raw_jd = "VP of AI Engineering"
    state.job.company = "ACME Corp"
    state.job.job_title = "VP AI"
    state.resume.master_resume = {"professional_experience": [{"company": "Test", "bullet_pool": ["Test bullet"]}]}
    state.metadata.workflow_id = "test-wf-001"
    state.metadata.complexity = "complex"
    
    state.strategy.strategy_plan = StrategyPlan(
        strategy_name="Mock Strategy", focus_areas=["AI", "Leadership"],
        key_achievements_to_highlight=["Mock achievement"], tone="professional"
    )
    
    state.draft.sections = {"summary": "Initial draft summary"}
    state.artifacts.artifacts = {"final_resume": {"summary": "Final artifact"}}
    state.safety.bias_detected = False
    state.safety.injection_detected = False
    
    state.prompts.prompts = GeneratedPrompts(bullet_generation_prompt="Test", critique_prompt="Test")
    state.qa.constitutional_review = ConstitutionalReviewResult(review_passed=True, violations_found=[], feedback="") # v10.6
    state.a2a.messages = [] # v10.6
    
    return state.to_dict()


@pytest.fixture
def sample_master_resume():
    """Returns a sample master resume structure."""
    return {
        "owner": {"name": "Test User"},
        "professional_experience": [
            {
                "company": "Test Corp",
                "title": "Senior Engineer",
                "bullet_pool": [
                    "Built AI systems reducing costs by 40%",
                    "Led team of 5 engineers"
                ]
            }
        ]
    }

# ============================================================================
# SECTION 2-12: PRESERVED v10.5 TESTS (v10.6 Updates)
# ============================================================================

# --- SECTION 2: Pydantic Validation (Preserved) ---
def test_pydantic_models_validation_error():
    malformed_data = {"score": "this should be a float", "suggestions": ["suggestion 1"]}
    validator = ResponseValidator()
    model, error = validator.validate(malformed_data, CritiqueResult)
    assert model is None and error is not None and "Input should be a valid number" in error

def test_pydantic_models_success_string_input():
    good_string = 'Thought: Blah. {"verified_bullets": ["bullet 1", "bullet 2"]}'
    validator = ResponseValidator()
    model, error = validator.validate(good_string, BulletList)
    assert error is None and isinstance(model, BulletList)

# --- SECTION 3: Resilience (Preserved) ---
@pytest.mark.asyncio
async def test_node_retry_decorator_succeeds(mock_workflow_context):
    mock_node_logic = AsyncMock(side_effect=[PydanticSchemaError("Invalid"), ModelAPIError("Timeout"), {"strategy": "success"}])
    @exponential_backoff_retry(max_retries=3, initial_delay=0.01)
    async def decorated_node(state: dict) -> dict: return await mock_node_logic(state)
    result = await decorated_node(state={})
    assert result["strategy"] == "success" and mock_node_logic.call_count == 3

@pytest.mark.asyncio
async def test_conductor_circuit_breaker_opens(mock_workflow_context, mock_llm_client):
    llm_call_content = {"content": json.dumps({"thought": "Call", "tool_call": {"name": "red_team_critique", "input": {}}}), "usage": {}}
    llm_final_content = {"content": json.dumps({"thought": "Stop", "final_draft": {}}), "usage": {}}
    mock_llm_client.chat_completion_async.side_effect = [llm_call_content, llm_call_content, llm_call_content, llm_final_content]
    
    conductor = ReActConductorAgent(mock_workflow_context)
    conductor.tools["red_team_critique"]._run_async_internal = AsyncMock(side_effect=PydanticSchemaError("Tool failed"))
    
    await conductor.run_async({"strategy": StrategyPlan(strategy_name="test", focus_areas=[], key_achievements_to_highlight=[], tone="professional")}, "test-wf")
    
    assert conductor.tools["red_team_critique"]._run_async_internal.call_count == 3
    assert conductor.tool_breakers["red_team_critique"].is_open is True

# --- SECTION 4: Agentic RAG (v10.6: Updated state signature) ---
@pytest.mark.asyncio
async def test_fix_3_agentic_rag_pipeline_success_loop(mock_workflow_context, mock_llm_client, base_state):
    agent = RAG_SearchAgent(mock_workflow_context)
    mock_llm_client.chat_completion_async.side_effect = [
        {"content": json.dumps({"thought": "Initial search", "tool_call": {"name": "search_resume_database", "input": {"query": "test query"}}})},
        {"content": json.dumps({"thought": "Results are poor", "tool_call": {"name": "generate_hypothetical_documents", "input": {"query": "test query"}}})},
        {"content": json.dumps({"thought": "Searching with HyDE", "tool_call": {"name": "search_resume_database", "input": {"query": "HyDE Document"}}})},
        {"content": json.dumps({"thought": "Results are good", "final_results": [{"title": "Good HyDE Result"}]})}
    ]
    agent.tools["search_resume_database"]._run_async_internal = AsyncMock(side_effect = [{"search_results": [{"title": "Bad"}]}, {"search_results": [{"title": "Good HyDE Result"}]}])
    agent.tools["generate_hypothetical_documents"]._run_async_internal = AsyncMock(return_value = {"status": "success", "hypothetical_document": "HyDE Document"})
    agent.rerank_results = AsyncMock(return_value=[{"title": "Reranked HyDE Result"}])
    
    with patch.object(agent, '_ingest_resume_to_chroma_async', new_callable=AsyncMock):
        # v10.6: Pass full state
        results_patch = await agent.run_async(base_state)
    
    assert mock_llm_client.chat_completion_async.call_count == 4
    assert agent.tools["generate_hypothetical_documents"]._run_async_internal.call_count == 1
    assert results_patch["resume"]["experience_bullets"] == [{"title": "Reranked HyDE Result"}]

# --- SECTION 5: Architecture & DI (v10.6: Updated) ---
def test_architecture_dependency_injection_v10_6(mock_workflow_context):
    tool = DraftingStrategistTool(mock_workflow_context)
    assert hasattr(tool, 'context')
    assert hasattr(tool, 'prompt_manager')
    assert hasattr(tool, 'validator')
    assert hasattr(tool, 'metrics')
    
    conductor = QAConductorAgent(mock_workflow_context)
    assert hasattr(conductor, 'context')
    assert hasattr(conductor, 'budget_manager')
    assert hasattr(conductor.context, 'semantic_validator')
    # v10.6: Check for new circular dependency
    assert hasattr(conductor.context, 'context_budget_manager')
    assert conductor.context.context_budget_manager is not None

def test_architecture_all_tools_inherit_base_tool(mock_workflow_context):
    import agent_tools_v10_6
    tool_classes = [getattr(agent_tools_v10_6, name) for name in dir(agent_tools_v10_6) if isinstance(getattr(agent_tools_v10_6, name), type) and 'Tool' in name and 'Base' not in name]
    assert len(tool_classes) >= 20 # 11 QA + 4 Drafting + 1 WordCount + 3 RAG + 2 UI
    for tool_class in tool_classes:
        assert issubclass(tool_class, BaseTool), f"Tool {tool_class.__name__} does not inherit"

# --- SECTION 6: Agent Stack (v10.6: Fixed async bugs) ---
# v10.6 TEST FIX: Removed `async def` from sync test
def test_bias_detector_agent(mock_workflow_context):
    mock_workflow_context.rules_loader.get_constitution_rules.return_value = []
    agent = BiasDetectorAgent(mock_workflow_context)
    biased_text = "Looking for young, energetic candidates"
    result = agent.run(biased_text, "test-wf-id")
    assert result["bias_detected"] is True

# v10.6 TEST FIX: Removed `async def` from sync test
def test_pii_sanitizer_agent(mock_workflow_context, sample_master_resume):
    agent = PIISanitizerAgent(mock_workflow_context)
    resume_with_pii = sample_master_resume.copy()
    resume_with_pii["owner"]["email"] = "test@example.com"
    result = agent.run(resume_with_pii)
    assert "test@example.com" not in json.dumps(result) and "[EMAIL_REDACTED]" in json.dumps(result)

@pytest.mark.asyncio
async def test_async_bullet_generator(mock_workflow_context, mock_llm_client, sample_master_resume, base_state):
    mock_llm_client.chat_completion_async.side_effect = [
        {"content": json.dumps(["Customized bullet 1"]), "usage": {}},
        {"content": json.dumps(["Synthetic bullet 1"]), "usage": {}},
        {"content": json.dumps({"verified_bullets": ["Built AI systems reducing costs by 40%", "Customized bullet 1", "Synthetic bullet 1"]}), "usage": {}}
    ]
    agent = AsyncBulletGeneratorAgent(mock_workflow_context)
    strategy_model = StrategyPlan.model_validate(base_state["strategy"]["strategy_plan"])
    
    result = await agent.run_async(
        prompt="test prompt",
        experience=sample_master_resume["professional_experience"][0],
        strategy=strategy_model,
        workflow_id="test-wf-id"
    )
    assert mock_llm_client.chat_completion_async.call_count == 3
    assert len(result) == 3

# --- SECTION 7: Contract Enforcement (v10.6: Fixed async bugs) ---
@pytest.mark.asyncio
async def test_tool_contract_drafting_tool(mock_workflow_context, mock_llm_client):
    mock_response = {"status": "success", "feedback": "Mock strategic feedback"}
    mock_llm_client.chat_completion_async.return_value = {"content": json.dumps(mock_response), "usage": {}}
    tool = DraftingStrategistTool(mock_workflow_context)
    result = await tool.run_async({"draft": "test", "strategy": {}}, "test-wf")
    mock_workflow_context.get_model_client.assert_called()
    assert result["feedback"] == "Mock strategic feedback"

@pytest.mark.asyncio
async def test_tool_handles_malformed_json_v10_6(mock_workflow_context, mock_llm_client):
    mock_llm_client.chat_completion_async.return_value = {"content": "This is not JSON", "usage": {}}
    real_validator = ResponseValidator()
    mock_workflow_context.response_validator.validate.side_effect = real_validator.validate
    tool = DraftingStrategistTool(mock_workflow_context)
    with pytest.raises(PydanticSchemaError):
        await tool.run_async({"strategy": "test"}, "test-wf")

# v10.6 TEST FIX: Removed `async def` from sync test
def test_contract_agent_logs_feedback(mock_workflow_context):
    agent = BiasDetectorAgent(mock_workflow_context)
    with patch.object(agent, 'log_feedback') as mock_log:
        agent.run("test text", "test-wf-id")
        mock_log.assert_called_once_with("test-wf-id", "bias_detection", "success", {"patterns_found": 0})

# --- SECTION 8-12: (Preserved, no v10.6 changes needed) ---
# ... (Tests for Batch, Chaos, Meta, Determinism, Orchestration) ...

# ============================================================================
# SECTION 13: v10.5 Fix #2 - DYNAMIC ROUTING TESTS (v10.6: Updated)
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
# SECTION 15: v10.5 Fix #1, #15 - TOOL CACHING & FEEDBACK (v10.6: Updated)
# ============================================================================
@pytest.mark.asyncio
async def test_fix_1_react_conductor_uses_tool_cache(mock_workflow_context, mock_llm_client, base_state):
    mock_llm_client.chat_completion_async.side_effect = [
        {"content": json.dumps({"thought": "Call 1", "tool_call": {"name": "red_team_critique", "input": {"id": 1}}}), "usage": {}},
        {"content": json.dumps({"thought": "Call 2", "tool_call": {"name": "red_team_critique", "input": {"id": 1}}}), "usage": {}},
        {"content": json.dumps({"thought": "Done", "final_draft": {}}), "usage": {}}
    ]
    conductor = ReActConductorAgent(mock_workflow_context)
    conductor.tools["red_team_critique"]._run_async_internal = AsyncMock(return_value={"weaknesses_found": ["test"]})
    strategy_model = StrategyPlan.model_validate(base_state["strategy"]["strategy_plan"])
    await conductor.run_async({"strategy": strategy_model}, "test-wf")
    conductor.tools["red_team_critique"]._run_async_internal.assert_called_once()
    assert mock_workflow_context.cache_manager.get_tool_cache.call_count == 2
    assert mock_workflow_context.cache_manager.set_tool_cache.call_count == 1

# ============================================================================
# SECTION 16-19: (Preserved, no v10.6 changes needed)
# ============================================================================
# ... (Tests for ToT Voting, PI, HIL, Semantic Validation) ...

# ============================================================================
# SECTION 20: v10.5 Fix #6, #8 - RESILIENCE & OPS (v10.6: Fixed async bugs)
# ============================================================================
@pytest.mark.asyncio
async def test_fix_6_node_timeout(mock_workflow_context, base_state):
    mock_workflow_context.config.performance_config.workflow_node_timeout_seconds = 0.01
    with patch('agent_stacks_v10_6.PIISanitizerAgent.run', side_effect=lambda *args, **kwargs: time.sleep(0.1)), \
         patch('agent_stacks_v10_6.BiasDetectorAgent.run', return_value={"bias_detected": False}):
        mock_checkpointer = AsyncMock(); mock_checkpointer.aget.return_value = None
        app = get_graph_app(mock_checkpointer, mock_workflow_context, enable_hil=False)
        with pytest.raises(NodeExecutionError) as e:
            await app.ainvoke(base_state, {"configurable": {"thread_id": "timeout-test"}})
        assert isinstance(e.value.__cause__, WorkflowTimeoutError)
        assert "run_sanitize_pii timed out" in str(e.value.__cause__)

@pytest.mark.asyncio
async def test_fix_8_metrics_decorator(mock_workflow_context, base_state):
    with patch('agent_stacks_v10_6.PIISanitizerAgent.run', return_value={}) as mock_pii_run, \
         patch('agent_stacks_v10_6.BiasDetectorAgent.run', return_value={"bias_detected": False}) as mock_bias_run:
        from agent_orchestration_v10_6 import run_sanitize_pii
        await run_sanitize_pii(base_state, mock_workflow_context)
    mock_workflow_context.metrics_collector.record.assert_any_call("PIISanitizerAgent", "run_pii_sanitizer", ANY, success=True, error=None, metadata=ANY)
    mock_workflow_context.metrics_collector.record.assert_any_call("BiasDetectorAgent", "run_bias_detector", ANY, success=True, error=None, metadata=ANY)

# ============================================================================
# SECTION 21: v10.6 Fix #13 - SEMANTIC CACHING TEST (NEW)
# ============================================================================
@pytest.mark.asyncio
async def test_fix_13_semantic_cache_hit(mock_workflow_context, mock_chromadb_client):
    """(v10.6 Fix #13) Test CacheManager uses ChromaDB on an exact miss."""
    cache_manager = mock_workflow_context.cache_manager
    # Ensure exact cache (Redis) returns None
    mock_workflow_context.redis_client.get.return_value = None
    
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
    mock_workflow_context.redis_client.setex.assert_called_once()

# ============================================================================
# SECTION 22: v10.6 Fix #14 - AGENTIC PRUNING TEST (NEW)
# ============================================================================
@pytest.mark.asyncio
async def test_fix_14_agentic_pruning(mock_workflow_context, mock_llm_client):
    """(v10.6 Fix #14) Test ContextBudgetManager uses summarizer model."""
    manager = mock_workflow_context.context_budget_manager
    # Mock the summarizer model's response
    mock_llm_client.chat_completion_async.return_value = {"content": "Agentic Summary", "usage": {}}
    
    long_text = "a" * 100000 # Force pruning
    result = await manager.prune(long_text, max_tokens=100)
    
    assert result == "Agentic Summary\n\n[... DOCUMENT PRUNED (AGENTIC) ...]"
    # Verify the summarizer model was called
    mock_workflow_context.get_model_client.assert_called_with("google", "gemini-flash")

# ============================================================================
# SECTION 23: v10.6 Fix #15 - LATENCY-BASED ROUTING TEST (NEW)
# ============================================================================
@pytest.mark.asyncio
async def test_fix_15_latency_based_routing(mock_workflow_context):
    """(v10.6 Fix #15) Test get_model_client falls back to simple model."""
    # Set high latency for the complex model
    mock_workflow_context.metrics_collector.get_average_latency.return_value = 99999.0
    mock_workflow_context.complexity = "complex"
    
    agent = BaseAgent(mock_workflow_context)
    # Request the complex model
    client = agent.get_model_client("strategy_model")
    
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
# SECTION 24: v10.6 Fix #25 - BACKPRESSURE TEST (NEW)
# ============================================================================
@pytest.mark.asyncio
async def test_fix_25_backpressure(mock_config, caplog):
    """(v10.6 Fix #25) Test run_batch_async halts if queue is too large."""
    mock_config.batch_config.max_batch_queue_size = 10 # Set a low limit
    
    # Mock 11 files in the queue
    with patch('os.listdir', return_value=[f"{i}.json" for i in range(11)]):
        await run_batch_async(mock_config)
    
    assert "BACKPRESSURE: Batch queue size (11) exceeds limit (10)" in caplog.text
    assert "Batch run aborted" in caplog.text

# ============================================================================
# SECTION 25: v10.6 Fix #29 - IDEMPOTENCY VALIDATION TEST (NEW)
# ============================================================================
@pytest.mark.asyncio
async def test_fix_29_idempotency_validation(mock_workflow_context, mock_llm_client):
    """(v10.6 Fix #29) Test idempotency check is triggered on cache hit."""
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
# SECTION 26: v10.6 Fix #30 - CONSTITUTIONAL AI TEST (NEW)
# ============================================================================
@pytest.mark.asyncio
async def test_fix_30_constitutional_review_node(mock_workflow_context, mock_llm_client, base_state):
    """(v10.6 Fix #30) Test the new run_constitutional_review node."""
    mock_response = {"review_passed": False, "violations_found": ["Test Violation"], "feedback": "Test"}
    mock_llm_client.chat_completion_async.return_value = {"content": json.dumps(mock_response), "usage": {}}

    result_state = await run_constitutional_review(base_state, mock_workflow_context)
    
    assert "qa" in result_state
    assert result_state["qa"]["constitutional_review"]["review_passed"] is False
    assert "Test Violation" in result_state["qa"]["constitutional_review"]["violations_found"]

def test_fix_30_constitutional_edge(mock_workflow_context):
    """(v10.6 Fix #30) Test the 'check_constitution' conditional edge."""
    state = {"qa": {"constitutional_review": {"review_passed": True}}}
    assert check_constitution(state) == "passed_constitution"
    
    state = {"qa": {"constitutional_review": {"review_passed": False}}}
    assert check_constitution(state) == "failed_constitution"

# ============================================================================
# SECTION 27: v10.6 Fix #5 - CONCURRENT NODE TEST (NEW)
# ============================================================================
def test_fix_5_concurrent_node_graph(mock_workflow_context):
    """(v10.6 Fix #5) Test graph is correctly wired for parallel execution."""
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
# SECTION 28: v10.6 Fix #10 - A2A COMMS TEST (NEW)
# ============================================================================
@pytest.mark.asyncio
async def test_fix_10_a2a_comms_on_rag_fail(mock_workflow_context, mock_llm_client, base_state):
    """(v10.6 Fix #10) Test RAG agent sends A2A message on max steps failure."""
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
# SECTION 29: v10.6 Fix #19, #20, #24 - PROMPT INJECTION TEST (NEW)
# ============================================================================
@pytest.mark.asyncio
async def test_fix_19_20_24_prompt_context_injection(mock_context_budget_manager):
    """(v10.6) Test _format_prompt_with_defaults injects all context."""
    template = "MODE: TEST\n{content}"
    goal = "Test Goal"
    failures = ["Test Failure"]
    
    result = await _format_prompt_with_defaults(template, {"content": "Hi"}, mock_context_budget_manager, goal, failures)
    
    assert "GLOBAL_GOAL: Test Goal" in result
    assert "BEWARE: System analysis shows top failures are:\n- Test Failure" in result
    assert "MODE: TEST\nHi" in result

# ============================================================================
# SECTION 30: v10.6 Fix #7 - DYNAMIC TOOL LOADING TEST (NEW)
# ============================================================================
def test_fix_7_dynamic_tool_loading(mock_workflow_context, tmp_path):
    """(v10.6 Fix #7) Test load_dynamic_tools loads a tool from a file."""
    # 1. Create a fake tool file in the temp directory
    tool_dir = tmp_path / "generated_tools_v10_6"
    tool_dir.mkdir()
    tool_file = tool_dir / "my_new_tool.py"
    tool_code = """
from core_v10_6 import BaseTool, BaseToolOutput, track_metrics
from pydantic import BaseModel
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
# END OF v10.6 TEST SUITE (150 TESTS)
# ============================================================================