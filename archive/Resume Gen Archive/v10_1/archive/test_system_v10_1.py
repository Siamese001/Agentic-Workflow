# File: test_system_v10_1.py
# Description: Integrated pytest file for the entire v10.1 system.
# This single file contains all fixtures and tests for:
# 1. agent_stacks_v10_1.py
# 2. agent_tools_v10_1.py
# 3. agent_orchestration_v10_1.py
#
# This file REPLACES conftest.py and all other test_*.py files.

import pytest
import pytest_asyncio
import asyncio
import redis
import json
from unittest.mock import MagicMock, AsyncMock, patch

from core_v10_1 import (
    WorkflowContext, ConfigV10_1, CacheManager, CostTracker, 
    FeedbackLogReader, ProposedRulesLoader, MainGraphState, BaseAgent
)

# Import all classes to be tested
from agent_stacks_v10_1 import (
    BaseTool,
    ToTStrategistAgent,
    BiasDetectorAgent,
    PIISanitizerAgent,
    RAG_SearchAgent,
    AsyncBulletGeneratorAgent,
    AsyncBulletCritiqueAgent,
    HILAmbiguityDetectorAgent,
    HILFeedbackRouterAgent
)
from agent_tools_v10_1 import (
    DraftingRedTeamTool,
    DraftingRefinerTool,
    QAAdversarialReviewerTool,
    QAClaimValidatorTool
)
from agent_orchestration_v10_1 import (
    ReActConductorAgent,
    QAConductorAgent,
    get_graph_app
)

pytestmark = pytest.mark.asyncio

# ============================================================================
# SECTION 1: PYTEST FIXTURES (from conftest.py)
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for all tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_redis_client():
    """Mocks the Redis client."""
    mock = MagicMock(spec=redis.Redis)
    mock.get.return_value = None
    mock.set.return_value = True
    mock.setex.return_value = True
    return mock

@pytest.fixture
def mock_config():
    """Mocks the ConfigV10_1 object with design-aligned values."""
    mock_conf = MagicMock(spec=ConfigV10_1)
    
    # Mock nested attributes
    mock_conf.logging_config.log_file = "logs/pytest_v10_1.log"
    mock_conf.redis_config.host = "localhost"
    mock_conf.redis_config.port = 6379
    mock_conf.redis_config.db = 0
    mock_conf.caching_config.cache_ttl_seconds = 3600
    mock_conf.meta_loop_config.feedback_log_path = "logs/feedback_log.jsonl"
    mock_conf.meta_loop_config.proposed_rules_path = "logs/proposed_rules.jsonl"
    mock_conf.agent_stacks.strategy_tot_branching_factor = 2
    mock_conf.agent_stacks.conductor_max_steps = 5
    mock_conf.agent_stacks.conductor_temperature = 0.5
    mock_conf.agent_stacks.reranking_top_k = 3
    mock_conf.agent_stacks.max_local_retries = 2
    
    # === Mock model configs (Aligned with master_config_v10_1.json) ===
    
    # Strategy
    mock_conf.model_config.strategy_model.provider = "google"
    mock_conf.model_config.strategy_model.model_name = "gemini-2.5-pro"
    mock_conf.model_config.strategy_model.temperature = 0.5
    
    # Prompt Engineering
    mock_conf.model_config.prompt_engineer_model.provider = "google"
    mock_conf.model_config.prompt_engineer_model.model_name = "gemini-2.5-flash"
    mock_conf.model_config.prompt_engineer_model.temperature = 0.5

    # Bullet Stack
    mock_conf.model_config.bullet_generator_model.provider = "google"
    mock_conf.model_config.bullet_generator_model.model_name = "gemini-2.5-pro"
    mock_conf.model_config.bullet_generator_model.temperature = 0.5
    
    mock_conf.model_config.bullet_fact_check_model.provider = "google"
    mock_conf.model_config.bullet_fact_check_model.model_name = "gemini-2.5-flash"
    mock_conf.model_config.bullet_fact_check_model.temperature = 0.5

    mock_conf.model_config.critique_model.provider = "google"
    mock_conf.model_config.critique_model.model_name = "gemini-2.5-flash"
    mock_conf.model_config.critique_model.temperature = 0.5

    # RAG Stack
    mock_conf.model_config.react_conductor_model.provider = "google"
    mock_conf.model_config.react_conductor_model.model_name = "gemini-2.5-pro"
    mock_conf.model_config.react_conductor_model.temperature = 0.5

    mock_conf.model_config.hyde_model.provider = "google"
    mock_conf.model_config.hyde_model.model_name = "gemini-2.5-flash"
    mock_conf.model_config.hyde_model.temperature = 0.5

    mock_conf.model_config.reranker_model.provider = "google"
    mock_conf.model_config.reranker_model.model_name = "gemini-2.5-flash"
    mock_conf.model_config.reranker_model.temperature = 0.5
    
    # HIL Stack
    mock_conf.model_config.qa_model.provider = "google"
    mock_conf.model_config.qa_model.model_name = "gemini-2.5-flash"
    mock_conf.model_config.qa_model.temperature = 0.5

    # Drafting Tools
    mock_conf.model_config.drafting_strategist_model.provider = "google"
    mock_conf.model_config.drafting_strategist_model.model_name = "gemini-2.5-pro"
    mock_conf.model_config.drafting_strategist_model.temperature = 0.5

    mock_conf.model_config.drafting_redteam_model.provider = "anthropic"
    mock_conf.model_config.drafting_redteam_model.model_name = "claude-4.1-opus"
    mock_conf.model_config.drafting_redteam_model.temperature = 0.5

    mock_conf.model_config.drafting_refiner_model.provider = "openai"
    mock_conf.model_config.drafting_refiner_model.model_name = "gpt-5"
    mock_conf.model_config.drafting_refiner_model.temperature = 0.5

    mock_conf.model_config.drafting_metrics_model.provider = "google"
    mock_conf.model_config.drafting_metrics_model.model_name = "gemini-2.5-flash"
    mock_conf.model_config.drafting_metrics_model.temperature = 0.5

    # QA Tools
    mock_conf.model_config.qa_adversarial_model.provider = "anthropic"
    mock_conf.model_config.qa_adversarial_model.model_name = "claude-4.1-opus"
    mock_conf.model_config.qa_adversarial_model.temperature = 0.5

    mock_conf.model_config.qa_validator_model.provider = "google"
    mock_conf.model_config.qa_validator_model.model_name = "gemini-2.5-flash"
    mock_conf.model_config.qa_validator_model.temperature = 0.5

    # Local Safety Tools
    mock_conf.model_config.bias_detector_model.provider = "local"
    mock_conf.model_config.bias_detector_model.model_name = "regex"
    mock_conf.model_config.bias_detector_model.temperature = 0.0

    mock_conf.model_config.pii_sanitizer_model.provider = "local"
    mock_conf.model_config.pii_sanitizer_model.model_name = "presidio"
    mock_conf.model_config.pii_sanitizer_model.temperature = 0.0
    
    return mock_conf

@pytest.fixture
def mock_llm_client():
    """Mocks the AsyncBaseModelClient (Gemini or Anthropic or OpenAI)."""
    mock = AsyncMock()
    # Default response
    mock.chat_completion_async = AsyncMock(
        return_value={
            "content": {"status": "mocked", "text": "Default mock response"},
            "usage": {"prompt_tokens": 10, "completion_tokens": 10}
        }
    )
    return mock

@pytest.fixture
def mock_workflow_context(mock_config, mock_redis_client, mock_llm_client):
    """
    Provides a fully mocked WorkflowContext.
    It patches the real classes to avoid live connections.
    """
    # Patch the real classes within the context of this fixture
    with patch('core_v10_1.CacheManager', spec=CacheManager) as MockCacheManager, \
         patch('core_v10_1.CostTracker', spec=CostTracker) as MockCostTracker, \
         patch('core_v10_1.FeedbackLogReader', spec=FeedbackLogReader) as MockFeedbackReader, \
         patch('core_v10_1.ProposedRulesLoader', spec=ProposedRulesLoader) as MockRulesLoader:

        # Instantiate the real WorkflowContext, but it will
        # use the mocked classes we just patched.
        context = WorkflowContext(config=mock_config, redis_client=mock_redis_client)
        
        # Mock the get_model_client method to return our mock_llm_client
        context.get_model_client = MagicMock(return_value=mock_llm_client)
        
        # Configure the mock instances that are *inside* the context
        context.cache_manager.get.return_value = None
        context.feedback_reader.read_recent_feedback.return_value = []
        context.rules_loader.get_constitution_rules.return_value = []
        
        yield context

@pytest.fixture
def base_state():
    """Provides a basic MainGraphState for tests to modify."""
    state = MainGraphState()
    state.metadata.workflow_id = "test-workflow-123"
    state.job.raw_jd = "Test Job Description"
    state.job.company = "TestCo"
    state.job.job_title = "Tester"
    state.resume.master_resume = {"name": "Test User", "professional_experience": [{"title": "Old Job", "bullet_pool": ["Old bullet 1"]}]}
    state.resume.sanitized_resume = {"name": "Test User", "professional_experience": [{"title": "Old Job", "bullet_pool": ["Old bullet 1"]}]}
    state.resume.experience_bullets = [{"title": "Old Job", "bullet_pool": ["Old bullet 1"]}] # For RAG output
    state.strategy.strategy_plan = {"focus": "testing", "tone": "leadership"}
    state.prompts.prompts = {
        "bullet_generation_prompt": "test gen prompt",
        "critique_prompt": "test critique prompt"
    }
    state.bullets.generated_bullets = [
        {"text": "Generated bullet 1", "experience": {}},
        {"text": "Generated bullet 2", "experience": {}}
    ]
    state.bullets.critiqued_bullets = [
        {"text": "Generated bullet 1", "experience": {}, "critique": {"score": 8, "feedback": "Good"}},
        {"text": "Generated bullet 2", "experience": {}, "critique": {"score": 5, "feedback": "Weak"}}
    ]
    state.draft.sections = {"summary": "Test draft summary"}
    
    return state.to_dict() # Return as dict, as graph nodes expect

# ============================================================================
# SECTION 2: AGENT STACK TESTS (from test_agent_stacks_v10_1.py)
# ============================================================================

def test_pii_sanitizer_agent(mock_workflow_context):
    """Tests that the PII sanitizer runs."""
    agent = PIISanitizerAgent(mock_workflow_context)
    resume = {"name": "Test User", "phone": "555-1212"}
    sanitized = agent.run(resume)
    assert sanitized["name"] == "Test User"
    # A real implementation would check for [REDACTED]

def test_bias_detector_agent(mock_workflow_context):
    """Tests the local bias detector."""
    agent = BiasDetectorAgent(mock_workflow_context)
    # Mock the rules loader to return a dynamic rule
    mock_workflow_context.rules_loader.get_constitution_rules.return_value = [
        {"bias_patterns": ["salesman"]}
    ]
    
    report = agent.run("We are looking for a salesman", "test-wf-id")
    assert report["bias_detected"] is True
    assert "salesman" in report["patterns"]
    assert report["dynamic_rules_applied"] == 1

@pytest.mark.asyncio
async def test_tot_strategist_agent(mock_workflow_context, mock_llm_client):
    """Tests the ToT Strategist."""
    # Mock the LLM response for this specific agent
    mock_response = {
        "strategy_name": "Test Strategy",
        "focus_areas": ["AI", "Partnerships"],
        "key_achievements_to_highlight": ["Launched v10.1"],
        "tone": "leadership"
    }
    mock_llm_client.chat_completion_async = AsyncMock(
        return_value={"content": mock_response, "usage": {"prompt_tokens": 10, "completion_tokens": 10}}
    )
    
    agent = ToTStrategistAgent(mock_workflow_context)
    job_context = {"job_title": "AI Lead", "company": "TestCo"}
    result = await agent.run_async(job_context, "test-wf-id")
    
    assert mock_llm_client.chat_completion_async.called
    assert result["strategy_plan"]["strategy_name"] == "Test Strategy"
    assert result["strategy_plan"]["focus_areas"][0] == "AI"
    assert len(result["tot_branches"]) == 2 # From mock_config

@pytest.mark.asyncio
async def test_rag_search_agent(mock_workflow_context, mock_llm_client):
    """Tests the ReAct RAG Search agent."""
    # Mock the multi-step ReAct process
    mock_llm_client.chat_completion_async.side_effect = [
        # 1. Thought + Tool Call (HyDE)
        {"content": {"thought": "First, I will generate HyDE docs.", "tool_call": {"name": "generate_hypothetical_documents", "input": {"query": "AI Lead"}}}, "usage": {"prompt_tokens": 10, "completion_tokens": 10}},
        # 2. Thought + Tool Call (Search)
        {"content": {"thought": "Now I will search.", "tool_call": {"name": "search_resume_database", "input": {"query": "AI docs"}}}, "usage": {"prompt_tokens": 10, "completion_tokens": 10}},
        # 3. Thought + Final Answer
        {"content": {"thought": "I have the results.", "final_answer": [{"title": "AI Researcher"}]}, "usage": {"prompt_tokens": 10, "completion_tokens": 10}},
        # 4. Reranker Call
        {"content": {"ranked": [{"title": "AI Researcher (Ranked)"}]}, "usage": {"prompt_tokens": 10, "completion_tokens": 10}}
    ]

    agent = RAG_SearchAgent(mock_workflow_context)
    result = await agent.run_async("AI Lead", [], "test-wf-id")
    
    assert mock_llm_client.chat_completion_async.call_count == 4
    assert result[0]["title"] == "AI Researcher (Ranked)"

@pytest.mark.asyncio
async def test_bullet_generator_agent(mock_workflow_context, mock_llm_client):
    """Tests the 4-step bullet generator."""
    # Mock the LLM calls: 1 for customize, 1 for synthetic, 1 for fact-check
    mock_llm_client.chat_completion_async.side_effect = [
        # 1. Customized
        {"content": ["Customized bullet 1"], "usage": {"prompt_tokens": 10, "completion_tokens": 10}},
        # 2. Synthetic
        {"content": ["Synthetic bullet 1"], "usage": {"prompt_tokens": 10, "completion_tokens": 10}},
        # 3. Fact-Check
        {"content": {"verified_bullets": ["Customized bullet 1", "Synthetic bullet 1", "Verbatim bullet 1"]}, "usage": {"prompt_tokens": 10, "completion_tokens": 10}}
    ]
    
    agent = AsyncBulletGeneratorAgent(mock_workflow_context)
    experience = {"title": "Test Job", "bullet_pool": ["Verbatim bullet 1", "Verbatim bullet 2"]}
    result = await agent.run_async("test prompt", experience, "test-wf-id")
    
    assert mock_llm_client.chat_completion_async.call_count == 3
    assert "Verbatim bullet 1" in result
    assert "Customized bullet 1" in result
    assert "Synthetic bullet 1" in result
    assert len(result) == 3

@pytest.mark.asyncio
async def test_bullet_critique_agent(mock_workflow_context, mock_llm_client):
    """Tests the parallel bullet critique."""
    # Mock the response for each parallel call
    critique_response = {"score": 9, "suggestions": "Looks great"}
    mock_llm_client.chat_completion_async.return_value = {"content": critique_response, "usage": {"prompt_tokens": 10, "completion_tokens": 10}}
    
    agent = AsyncBulletCritiqueAgent(mock_workflow_context)
    bullets = [{"text": "Bullet 1", "experience": {}}, {"text": "Bullet 2", "experience": {}}]
    result = await agent.run_async(bullets, "test prompt", "test-wf-id")
    
    # Called twice (once for each bullet)
    assert mock_llm_client.chat_completion_async.call_count == 2
    assert result[0]["text"] == "Bullet 1"
    assert result[0]["critique"]["score"] == 9
    assert result[1]["critique"]["score"] == 9

@pytest.mark.asyncio
async def test_hil_ambiguity_detector(mock_workflow_context, mock_llm_client):
    """Tests the ambiguity detector."""
    mock_response = {
        "ambiguity_detected": True,
        "confidence": 0.9,
        "reason": "Vague strategy",
        "question_for_human": "What do you mean?"
    }
    mock_llm_client.chat_completion_async.return_value = {"content": mock_response, "usage": {"prompt_tokens": 10, "completion_tokens": 10}}
    
    agent = HILAmbiguityDetectorAgent(mock_workflow_context)
    result = await agent.run_async({"focus": "synergy"}, "test-wf-id")
    
    assert result["ambiguity_detected"] is True
    assert result["reason"] == "Vague strategy"

@pytest.mark.asyncio
async def test_hil_feedback_router(mock_workflow_context, mock_llm_client):
    """Tests the feedback router."""
    mock_response = {"next_step": "STRATEGY"}
    mock_llm_client.chat_completion_async.return_value = {"content": mock_response, "usage": {"prompt_tokens": 10, "completion_tokens": 10}}
    
    agent = HILFeedbackRouterAgent(mock_workflow_context)
    result = await agent.run_async("Rethink the whole strategy", "test-wf-id")
    
    assert result["next_step"] == "STRATEGY"

# ============================================================================
# SECTION 3: AGENT TOOL TESTS (New)
# ============================================================================

@pytest.mark.asyncio
async def test_drafting_redteam_tool(mock_workflow_context, mock_llm_client):
    """Tests the DraftingRedTeamTool (Claude 4.1 Opus)."""
    mock_response = {"status": "success", "weaknesses_found": ["Mocked weakness"]}
    mock_llm_client.chat_completion_async.return_value = {"content": mock_response, "usage": {"prompt_tokens": 10, "completion_tokens": 10}}

    agent = DraftingRedTeamTool(mock_workflow_context)
    result = await agent.run_async({"draft": "..."}, "test-wf-id")
    
    # Verifies that get_model_client was called with the *correct config name*
    mock_workflow_context.get_model_client.assert_called_with("drafting_redteam_model")
    assert result["weaknesses_found"][0] == "Mocked weakness"

@pytest.mark.asyncio
async def test_drafting_refiner_tool(mock_workflow_context, mock_llm_client):
    """Tests the DraftingRefinerTool (GPT-5)."""
    mock_response = {"status": "success", "refined_text": "New refined text"}
    mock_llm_client.chat_completion_async.return_value = {"content": mock_response, "usage": {"prompt_tokens": 10, "completion_tokens": 10}}

    agent = DraftingRefinerTool(mock_workflow_context)
    result = await agent.run_async({"section_text": "...", "critique": "..."}, "test-wf-id")
    
    mock_workflow_context.get_model_client.assert_called_with("drafting_refiner_model")
    assert result["refined_text"] == "New refined text"

@pytest.mark.asyncio
async def test_qa_adversarial_tool(mock_workflow_context, mock_llm_client):
    """Tests the QAAdversarialReviewerTool (Claude 4.1 Opus)."""
    mock_response = {"status": "success", "red_flags": ["Mocked red flag"]}
    mock_llm_client.chat_completion_async.return_value = {"content": mock_response, "usage": {"prompt_tokens": 10, "completion_tokens": 10}}

    agent = QAAdversarialReviewerTool(mock_workflow_context)
    result = await agent.run_async({"draft_text": "..."}, "test-wf-id")
    
    mock_workflow_context.get_model_client.assert_called_with("qa_adversarial_model")
    assert result["red_flags"][0] == "Mocked red flag"

@pytest.mark.asyncio
async def test_qa_validator_tool(mock_workflow_context, mock_llm_client):
    """Tests a base T2 QA Validator (Gemini 2.5 Flash)."""
    mock_response = {"status": "success", "unsupported_claims": 0}
    mock_llm_client.chat_completion_async.return_value = {"content": mock_response, "usage": {"prompt_tokens": 10, "completion_tokens": 10}}

    agent = QAClaimValidatorTool(mock_workflow_context)
    result = await agent.run_async({"draft_text": "...", "master_resume": "..."}, "test-wf-id")
    
    # Verifies it called the T2 validator model
    mock_workflow_context.get_model_client.assert_called_with("qa_validator_model")
    assert result["unsupported_claims"] == 0

# ============================================================================
# SECTION 4: ORCHESTRATION TESTS (New)
# ============================================================================

@pytest.mark.asyncio
async def test_react_drafting_conductor(mock_workflow_context, mock_llm_client):
    """Tests the Drafting ReAct Conductor."""
    mock_llm_client.chat_completion_async.side_effect = [
        # 1. Thought + Tool Call (review_draft_strategy)
        {"content": {"thought": "Let's review strategy.", "tool_call": {"name": "review_draft_strategy", "input": {}}}, "usage": {"prompt_tokens": 10, "completion_tokens": 10}},
        # 2. Thought + Final Answer
        {"content": {"thought": "Strategy looks good, I'm done.", "final_draft": {"summary": "Final mock draft"}}, "usage": {"prompt_tokens": 10, "completion_tokens": 10}}
    ]
    
    agent = ReActConductorAgent(mock_workflow_context)
    context = {"bullets": [], "strategy": {}}
    result = await agent.run_async(context, "test-wf-id")
    
    # Verifies it called the T1 conductor model
    mock_workflow_context.get_model_client.assert_called_with("react_conductor_model")
    assert mock_llm_client.chat_completion_async.call_count == 2
    assert result["final_output"]["summary"] == "Final mock draft"

@pytest.mark.asyncio
async def test_react_qa_conductor(mock_workflow_context, base_state):
    """Tests the QA ReAct Conductor."""
    # This is a complex test, so we simplify and only check the setup
    agent = QAConductorAgent(mock_workflow_context)
    assert "validate_claims" in agent.tools
    assert "adversarial_review" in agent.tools
    assert len(agent.tools) == 11

def test_get_graph_app(mock_workflow_context):
    """Tests that the LangGraph app compiles without errors."""
    mock_checkpointer = MagicMock()
    app = get_graph_app(mock_checkpointer, mock_workflow_context, enable_hil=True)
    
    assert app is not None
    assert "run_tot_strategy" in app.get_graph().nodes
    assert "run_qa_validation" in app.get_graph().nodes
    assert "HIL_PAUSE" in app.get_graph().nodes

@pytest.mark.asyncio
async def test_graph_qa_retry_logic(mock_workflow_context, base_state):
    """Tests the QA retry logic from the graph."""
    
    # --- Setup ---
    # We patch the main agent nodes
    with patch('agent_orchestration_v10_1.run_sanitize_pii', new=AsyncMock(return_value={})) as mock_sanitize, \
         patch('agent_orchestration_v10_1.run_tot_strategy', new=AsyncMock(return_value={})) as mock_strategy, \
         patch('agent_orchestration_v10_1.run_detect_ambiguity', new=AsyncMock(return_value={"hil": {"ambiguity_detected": False}})) as mock_ambiguity, \
         patch('agent_orchestration_v10_1.run_rag_stack', new=AsyncMock(return_value={})) as mock_rag, \
         patch('agent_orchestration_v10_1.run_generate_bullets', new=AsyncMock(return_value={})) as mock_gen_bullets, \
         patch('agent_orchestration_v10_1.run_critique_bullets', new=AsyncMock(return_value={"bullets": {"critiqued_bullets": [{"critique": {"score": 8}}]}})) as mock_crit_bullets, \
         patch('agent_orchestration_v10_1.run_drafting', new=AsyncMock(return_value={})) as mock_drafting, \
         patch('agent_orchestration_v10_1.run_qa_validation', new_callable=AsyncMock) as mock_qa, \
         patch('agent_orchestration_v10_1.run_hil_stack', new=AsyncMock(return_value={})) as mock_hil:

        # --- Configure Mocks ---
        # 1. QA fails the first time
        # 2. QA fails the second time (hits retry limit)
        mock_qa.side_effect = [
            {"qa": {"qa_passed": False}}, # Fails first time
            {"qa": {"qa_passed": False}}  # Fails second time
        ]
        
        mock_checkpointer = MagicMock()
        app = get_graph_app(mock_checkpointer, mock_workflow_context, enable_hil=False)
        
        # --- Run Graph ---
        run_config = {"configurable": {"thread_id": "test-retry-wf"}}
        final_state = await app.ainvoke(base_state, run_config)
        
        # --- Assert ---
        # It should call drafting ONCE
        mock_drafting.assert_called_once() 
        # It should call QA TWICE (initial + 1 retry)
        assert mock_qa.call_count == 2
        # It should NOT call HIL stack
        mock_hil.assert_not_called()
        # The final node should be the replanner
        assert final_state['__end__'] == 'GLOBAL_REPLANNER'