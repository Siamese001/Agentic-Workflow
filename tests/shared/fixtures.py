from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

from core_v10_7 import (
    AdvancedMetaLearner,
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
)
from tests.shared.mock_clients import (
    DeterministicEmbeddingFunction,
    DummyEmbeddingFunction,
    FakeChromaClient,
    FakeCollection,
    FakeRedisClient,
    InMemoryRedis,
    TraceRecorder,
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
    tuning_profile = TuningProfile()
    policy_auto_tuner = PolicyAutoTuner(config, metrics)
    predictive_cache_manager = PredictiveCacheManager(
        config=config,
        cache_manager=cache_mgr,
        metrics=metrics,
    )
    precompute_engine = PrecomputeEngine(context=None)
    semantic_validator = SemanticValidator(metrics_collector=metrics)
    arbitration_engine = ArbitrationEngine(config=config, metrics=metrics)
    metrics.predictive_cache_manager = predictive_cache_manager
    ctx = WorkflowContext(
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
        arbitration_engine=arbitration_engine,
        predictive_cache_manager=predictive_cache_manager,
        precompute_engine=precompute_engine,
        tuning_profile=tuning_profile,
        policy_auto_tuner=policy_auto_tuner,
        advanced_meta_learner=AdvancedMetaLearner(config=config, metrics=metrics),
    )
    ctx.context_budget_manager = ContextBudgetManager(
        config=config, model_client_getter=ctx.get_model_client
    )
    precompute_engine.context = ctx
    ctx.reset_mcp_clients()
    return ctx


@pytest.fixture()
def benchmark():
    """Lightweight stand-in for pytest-benchmark's fixture."""

    def _runner(func, *args, **kwargs):
        return func(*args, **kwargs)

    return _runner


@pytest.fixture()
def mock_llm_client() -> MagicMock:
    client = MagicMock(name="MockLLMClient")
    client._run_idempotency_check = AsyncMock(name="_run_idempotency_check")

    async def _chat_completion_async(*args, **kwargs):
        await client._run_idempotency_check(*args, **kwargs)
        return client.chat_completion_async.return_value

    client.chat_completion_async = AsyncMock(
        name="chat_completion_async", side_effect=_chat_completion_async
    )
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
) -> WorkflowContext:
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
        context_budget_manager.register_workflow = (  # type: ignore[attr-defined]
            lambda *_args, **_kwargs: None
        )
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

    return workflow_context


@pytest.fixture()
def mock_workflow_context(workflow_harness: WorkflowContext) -> WorkflowContext:
    return workflow_harness


@pytest.fixture()
def prompt_manager(workflow_harness: WorkflowContext) -> PromptTemplateManager:
    return workflow_harness.prompt_manager


@pytest.fixture()
def metrics_collector(workflow_harness: WorkflowContext) -> MetricsCollector:
    return workflow_harness.metrics_collector


@pytest.fixture()
def redis_client(workflow_harness: WorkflowContext) -> FakeRedisClient:
    return workflow_harness.redis_client


@pytest.fixture()
def cost_tracker(workflow_harness: WorkflowContext) -> CostTracker:
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
            "company": "OpenAI",
            "job_title": "AI Executive",
            "job_description": "Lead AI initiatives",
        },
        "resume": {
            "candidate": "Test Candidate",
            "job_title": "AI Executive",
            "summary": "Experienced AI leader",
            "highlights": ["Built AI products"],
            "skills": ["Python", "ML"],
            "sections": [
                {
                    "title": "Experience",
                    "entries": [
                        {
                            "title": "Senior Manager",
                            "bullet_pool": [
                                "Led cross-functional team to deliver ML platform",
                                "Increased model throughput by 30%",
                            ],
                        }
                    ],
                }
            ],
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
def workflow_context_factory(workflow_harness: WorkflowContext) -> Callable[[str], WorkflowContext]:
    def _factory(workflow_id: str) -> WorkflowContext:
        context = workflow_harness
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
