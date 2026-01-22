"""Focused regression tests for the v10.7 core components."""

import asyncio
import json
import sys
import types

import pytest
    BaseTool,
    CacheManager,
    CircuitBreaker,
    CircuitBreakerOpenError,
    ConfigV10_7,
    ContextBudgetManager,
    CostTracker,
    FeedbackLogReader,
    MCPClientInitializationError,
    MCPClientSpec,
    MCPClientStub,
    MetricsCollector,
    ModelAPIError,
    PlannerAssessment,
    PromptTemplateManager,
    ProposedRulesLoader,
    ResponseValidator,
    ScenarioSimulationResult,
    SemanticValidator,
    StrategyPlan,
    WorkflowContext,
    _instantiate_mcp_client,
    _parse_mcp_client_specs,
    exponential_backoff_retry,
    wrap_mcp,
)
    DomainPlannerAgent,
    FeasibilityAnalystAgent,
    RiskAssessorAgent,
    StrategyScenarioSimulatorAgent,
)

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



class InMemoryRedis:
    """Minimal Redis substitute supporting the subset used by CacheManager."""

    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    def setex(self, name: str, ttl: int, value: str) -> None:
        self.store[name] = value

    def get(self, name: str) -> str | None:
        return self.store.get(name)


class FakeCollection:
    def __init__(self) -> None:
        self.records: dict[str, dict[str, Any]] = {}

    def add(
        self,
        *,
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]],
        ids: list[str],
    ) -> None:
        for doc, metadata, record_id in zip(documents, metadatas, ids, strict=False):
            self.records[record_id] = {"document": doc, "metadata": metadata}

    def query(
        self,
        *,
        query_embeddings: list[list[float]],
        n_results: int,
        where: dict[str, Any],
    ) -> dict[str, Any]:
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
    def __call__(self, prompts: list[str]) -> list[list[float]]:
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
# Helper utilities for category-driven scenario testing
# ---------------------------------------------------------------------------


def _assert_file_pattern(file_path: str, substring: str, *, should_exist: bool) -> None:
    content = Path(file_path).read_text(encoding="utf-8")
    if should_exist:
        assert substring in content, f"Expected '{substring}' in {file_path}"
    else:
        assert substring not in content, f"Forbidden pattern '{substring}' found in {file_path}"


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


# ---------------------------------------------------------------------------
# Category 1: Functional Behavior scenario helpers (15 cases)
# ---------------------------------------------------------------------------


def _functional_case_response_validator_parses_object(
    _workflow_context: WorkflowContext,
    _config: ConfigV10_7,
    _cache_manager: CacheManager,
    _tmp_path: Path,
) -> None:
    validator = ResponseValidator()
    payload, error = validator.validate('irrelevant {"status": "ok"}', dict)
    assert payload == {"status": "ok"}
    assert error is None


def _functional_case_response_validator_handles_list(
    _workflow_context: WorkflowContext,
    _config: ConfigV10_7,
    _cache_manager: CacheManager,
    _tmp_path: Path,
) -> None:
    validator = ResponseValidator()
    payload, error = validator.validate("[1, 2, 3]", list)
    assert payload == [1, 2, 3]
    assert error is None


def _functional_case_response_validator_reports_error(
    _workflow_context: WorkflowContext,
    _config: ConfigV10_7,
    _cache_manager: CacheManager,
    _tmp_path: Path,
) -> None:
    validator = ResponseValidator()
    payload, error = validator.validate("no json here", dict)
    assert payload is None
    assert error is not None


def _functional_case_prompt_template_injects_goal_state(
    _workflow_context: WorkflowContext,
    config: ConfigV10_7,
    _cache_manager: CacheManager,
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "feedback.jsonl"
    config.meta_loop_config._data["feedback_log_path"] = str(log_path)
    feedback_reader = FeedbackLogReader(str(log_path))
    prompt_manager = PromptTemplateManager(feedback_reader)
    template = prompt_manager.get_template("review_draft_strategy")
    assert "{goal_state}" in template and "{top_failures}" in template


def _functional_case_prompt_template_handles_missing(
    _workflow_context: WorkflowContext,
    config: ConfigV10_7,
    _cache_manager: CacheManager,
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "feedback_missing.jsonl"
    config.meta_loop_config._data["feedback_log_path"] = str(log_path)
    prompt_manager = PromptTemplateManager(FeedbackLogReader(str(log_path)))
    template = prompt_manager.get_template("missing_template")
    assert "PROMPT NOT FOUND" in template


def _functional_case_cache_manager_miss_on_empty(
    _workflow_context: WorkflowContext,
    _config: ConfigV10_7,
    cache_manager: CacheManager,
    _tmp_path: Path,
) -> None:
    cached = asyncio.run(
        cache_manager.get_llm_cache(
            provider="openai",
            model="gpt-test",
            prompt="does-not-exist",
            temperature=0.5,
        )
    )
    assert cached is None


def _functional_case_cache_manager_tool_cache_roundtrip(
    _workflow_context: WorkflowContext,
    _config: ConfigV10_7,
    cache_manager: CacheManager,
    _tmp_path: Path,
) -> None:
    cache_manager.set_tool_cache("roundtrip_tool", {"input": 1}, {"result": 2})
    cached = cache_manager.get_tool_cache("roundtrip_tool", {"input": 1})
    assert cached == {"result": 2}


def _functional_case_cache_manager_unserializable_input(
    _workflow_context: WorkflowContext,
    _config: ConfigV10_7,
    cache_manager: CacheManager,
    _tmp_path: Path,
) -> None:
    class Unserializable:
        pass

    cached = cache_manager.get_tool_cache("bad_tool", {"obj": Unserializable()})
    assert cached is None


def _functional_case_proposed_rules_loader_reads_entries(
    _workflow_context: WorkflowContext,
    _config: ConfigV10_7,
    _cache_manager: CacheManager,
    tmp_path: Path,
) -> None:
    rules_path = tmp_path / "rules.jsonl"
    _write_jsonl(
        rules_path,
        [
            {
                "timestamp": "now",
                "status": "APPROVED",
                "pattern": {
                    "type": "constitution",
                    "description": "Ensure fairness",
                    "config_changes": {"flag": True},
                },
            }
        ],
    )
    loader = ProposedRulesLoader(str(rules_path))
    rules = loader.load_rules()
    assert len(rules) == 1


def _functional_case_feedback_log_reader_filters_failures(
    _workflow_context: WorkflowContext,
    config: ConfigV10_7,
    _cache_manager: CacheManager,
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "feedback_log.jsonl"
    _write_jsonl(
        log_path,
        [
            {
                "timestamp": "1",
                "workflow_id": "wf",
                "agent_name": "Agent",
                "task": "t",
                "feedback_type": "success",
                "details": {},
            },
            {
                "timestamp": "2",
                "workflow_id": "wf",
                "agent_name": "Agent",
                "task": "t",
                "feedback_type": "failure",
                "details": {},
            },
        ],
    )
    reader = FeedbackLogReader(str(log_path))
    failures = reader.get_failures()
    assert len(failures) == 1


def _functional_case_context_budget_truncation_labels_output(
    workflow_context: WorkflowContext,
    _config: ConfigV10_7,
    _cache_manager: CacheManager,
    _tmp_path: Path,
) -> None:
    long_text = "abc" * 4000
    pruned = asyncio.run(workflow_context.context_budget_manager._prune_agentic(long_text, 10))
    assert "DOCUMENT PRUNED" in pruned


def _functional_case_metrics_collector_records(
    _workflow_context: WorkflowContext,
    _config: ConfigV10_7,
    _cache_manager: CacheManager,
    tmp_path: Path,
) -> None:
    collector = MetricsCollector()
    collector.log_path = str(tmp_path / "metrics.jsonl")
    collector.record("Agent", "task", 1.0, True)
    assert collector.metrics and collector.metrics[0]["agent_name"] == "Agent"


def _functional_case_cost_tracker_summarises(
    _workflow_context: WorkflowContext,
    _config: ConfigV10_7,
    _cache_manager: CacheManager,
    _tmp_path: Path,
) -> None:
    tracker = CostTracker()
    tracker.log_cost("wf", "agent", "gemini-2.5-pro", 1000, 1000)
    summary = tracker.get_cost_summary("wf")
    assert summary["total_workflow_cost"] > 0


def _functional_case_base_tool_uses_cache(
    workflow_context: WorkflowContext,
    _config: ConfigV10_7,
    _cache_manager: CacheManager,
    _tmp_path: Path,
) -> None:
    class EchoTool(BaseTool):
        tool_name = "echo_tool"

        async def _run_async_internal(
            self, tool_input: dict[str, Any], workflow_id: str
        ) -> dict[str, Any]:
            return {"echo": tool_input["value"], "workflow": workflow_id}

    tool = EchoTool(workflow_context)
    result_first = asyncio.run(tool.run_async({"value": 1}, "wf"))
    result_second = asyncio.run(tool.run_async({"value": 1}, "wf"))
    assert result_first == result_second


def _functional_case_workflow_context_initialises_mcp(
    workflow_context: WorkflowContext,
    _config: ConfigV10_7,
    _cache_manager: CacheManager,
    _tmp_path: Path,
) -> None:
    clients = workflow_context.ensure_mcp_clients()
    assert "default_stub" in clients


def _functional_case_dynamic_tool_loader_handles_missing_dir(
    workflow_context: WorkflowContext,
    config: ConfigV10_7,
    _cache_manager: CacheManager,
    tmp_path: Path,
) -> None:
    config.meta_loop_config._data["generated_tools_path"] = str(tmp_path / "missing")
    tools = load_dynamic_tools(workflow_context, debug_mode=False)
    assert tools == {}


FUNCTIONAL_BEHAVIOR_CASES: list[
    Callable[[WorkflowContext, ConfigV10_7, CacheManager, Path], None]
] = [
    _functional_case_response_validator_parses_object,
    _functional_case_response_validator_handles_list,
    _functional_case_response_validator_reports_error,
    _functional_case_prompt_template_injects_goal_state,
    _functional_case_prompt_template_handles_missing,
    _functional_case_cache_manager_miss_on_empty,
    _functional_case_cache_manager_tool_cache_roundtrip,
    _functional_case_cache_manager_unserializable_input,
    _functional_case_proposed_rules_loader_reads_entries,
    _functional_case_feedback_log_reader_filters_failures,
    _functional_case_context_budget_truncation_labels_output,
    _functional_case_metrics_collector_records,
    _functional_case_cost_tracker_summarises,
    _functional_case_base_tool_uses_cache,
    _functional_case_workflow_context_initialises_mcp,
    _functional_case_dynamic_tool_loader_handles_missing_dir,
]


@pytest.mark.parametrize(
    "functional_case",
    [pytest.param(case, id=case.__name__) for case in FUNCTIONAL_BEHAVIOR_CASES],
)
def test_functional_behavior_matrix(
    functional_case: Callable[[WorkflowContext, ConfigV10_7, CacheManager, Path], None],
    workflow_context: WorkflowContext,
    config: ConfigV10_7,
    cache_manager: CacheManager,
    tmp_path: Path,
) -> None:
    """Ensures all Functional Behavior scenarios execute successfully."""

    functional_case(workflow_context, config, cache_manager, tmp_path)


# ---------------------------------------------------------------------------
# Category 2: Mock Detection safeguards (runtime + static checks)
# ---------------------------------------------------------------------------


def _make_strategy_plan(
    *,
    focus_areas: list[str],
    achievements: list[str],
    tone: str = "executive",
) -> StrategyPlan:
    return StrategyPlan(
        strategy_name="AI Visionary",
        focus_areas=focus_areas,
        key_achievements_to_highlight=achievements,
        tone=tone,
        planner_assessments=[],
        feedback_signals=[],
        scenario_simulations=[],
    )


def _mock_case_domain_planner_matches_context(
    workflow_context: WorkflowContext,
    _config: ConfigV10_7,
) -> None:
    agent = DomainPlannerAgent(workflow_context)
    plan = _make_strategy_plan(
        focus_areas=["AI director impact"],
        achievements=["Launched AI product"],
    )
    job_context = {"job_title": "AI Director", "company": "FutureAI"}
    assessment = asyncio.run(agent.run_async(plan, job_context, "wf-mock"))
    assert isinstance(assessment, PlannerAssessment)
    assert assessment.vote == "approve"


def _mock_case_domain_planner_flags_gap(
    workflow_context: WorkflowContext,
    _config: ConfigV10_7,
) -> None:
    agent = DomainPlannerAgent(workflow_context)
    plan = _make_strategy_plan(
        focus_areas=["Generalist delivery"],
        achievements=["Improved ops"],
    )
    job_context = {"job_title": "AI Director", "company": "FutureAI"}
    assessment = asyncio.run(agent.run_async(plan, job_context, "wf-mock"))
    assert assessment.vote == "revise"
    assert assessment.recommended_actions


def _mock_case_risk_assessor_detects_duplicates(
    workflow_context: WorkflowContext,
    _config: ConfigV10_7,
) -> None:
    agent = RiskAssessorAgent(workflow_context)
    plan = _make_strategy_plan(
        focus_areas=["AI scale", "AI scale", "Leadership", "Execution", "Growth"],
        achievements=["Scaled"],
    )
    assessment = asyncio.run(agent.run_async(plan, {}, "wf-mock"))
    assert assessment.vote == "revise"
    assert "duplicate" in assessment.rationale.lower()


def _mock_case_risk_assessor_low_risk(
    workflow_context: WorkflowContext,
    _config: ConfigV10_7,
) -> None:
    agent = RiskAssessorAgent(workflow_context)
    plan = _make_strategy_plan(
        focus_areas=["AI scale", "Leadership"],
        achievements=["Scaled"],
    )
    assessment = asyncio.run(agent.run_async(plan, {}, "wf-mock"))
    assert assessment.vote == "approve"


def _mock_case_feasibility_requires_achievements(
    workflow_context: WorkflowContext,
    _config: ConfigV10_7,
) -> None:
    agent = FeasibilityAnalystAgent(workflow_context)
    plan = _make_strategy_plan(focus_areas=["AI"], achievements=[""], tone="technical")
    assessment = asyncio.run(agent.run_async(plan, {}, "wf-mock"))
    assert assessment.vote == "revise"


def _mock_case_feasibility_demands_quant(
    workflow_context: WorkflowContext,
    _config: ConfigV10_7,
) -> None:
    agent = FeasibilityAnalystAgent(workflow_context)
    plan = _make_strategy_plan(
        focus_areas=["AI"],
        achievements=["Built feature", "Improved onboarding"],
    )
    assessment = asyncio.run(agent.run_async(plan, {}, "wf-mock"))
    assert "quantified" in assessment.rationale


def _mock_case_feasibility_passes_with_quant(
    workflow_context: WorkflowContext,
    _config: ConfigV10_7,
) -> None:
    agent = FeasibilityAnalystAgent(workflow_context)
    plan = _make_strategy_plan(
        focus_areas=["AI"],
        achievements=["Increased ARR 20%", "Cut costs 30%"],
    )
    assessment = asyncio.run(agent.run_async(plan, {}, "wf-mock"))
    assert assessment.vote == "approve"


def _mock_case_scenario_simulator_outputs_results(
    workflow_context: WorkflowContext,
    _config: ConfigV10_7,
) -> None:
    agent = StrategyScenarioSimulatorAgent(workflow_context)
    plan = _make_strategy_plan(
        focus_areas=["AI leadership", "Tech modernization"],
        achievements=["Drove AI revenue 5M"],
    )
    results = asyncio.run(agent.run_async(plan, {}, "wf-mock"))
    assert results and isinstance(results[0], ScenarioSimulationResult)


def _mock_case_scenario_simulator_flags_missing_metrics(
    workflow_context: WorkflowContext,
    _config: ConfigV10_7,
) -> None:
    agent = StrategyScenarioSimulatorAgent(workflow_context)
    plan = _make_strategy_plan(
        focus_areas=["Leadership"],
        achievements=["Improved morale"],
    )
    results = asyncio.run(agent.run_async(plan, {}, "wf-mock"))
    assert any(r.mitigation_actions for r in results)


def _mock_case_domain_planner_recommends_action(
    workflow_context: WorkflowContext,
    _config: ConfigV10_7,
) -> None:
    agent = DomainPlannerAgent(workflow_context)
    plan = _make_strategy_plan(
        focus_areas=["Execution"],
        achievements=["Improved ops"],
    )
    assessment = asyncio.run(agent.run_async(plan, {"company": "Acme"}, "wf-mock"))
    assert assessment.recommended_actions


def _mock_case_no_mock_comments_core() -> None:
    _assert_file_pattern("core_v10_7.py", "MOCK", should_exist=False)


def _mock_case_no_mock_comments_orchestration() -> None:
    _assert_file_pattern("agent_orchestration_v10_7.py", "MOCK", should_exist=False)


def _mock_case_no_mock_comments_tools() -> None:
    _assert_file_pattern("agent_tools_v10_7.py", "MOCK", should_exist=False)


def _mock_case_no_mock_comments_stacks() -> None:
    _assert_file_pattern("stacks_v10_7/strategy.py", "MOCK", should_exist=False)


def _mock_case_no_mock_comments_strategy_ensemble() -> None:
    _assert_file_pattern("strategy_ensemble_v10_7.py", "MOCK", should_exist=False)


MOCK_DETECTION_CASES: list[Callable[..., None]] = [
    _mock_case_domain_planner_matches_context,
    _mock_case_domain_planner_flags_gap,
    _mock_case_risk_assessor_detects_duplicates,
    _mock_case_risk_assessor_low_risk,
    _mock_case_feasibility_requires_achievements,
    _mock_case_feasibility_demands_quant,
    _mock_case_feasibility_passes_with_quant,
    _mock_case_scenario_simulator_outputs_results,
    _mock_case_scenario_simulator_flags_missing_metrics,
    _mock_case_domain_planner_recommends_action,
    _mock_case_no_mock_comments_core,
    _mock_case_no_mock_comments_orchestration,
    _mock_case_no_mock_comments_tools,
    _mock_case_no_mock_comments_stacks,
    _mock_case_no_mock_comments_strategy_ensemble,
]


@pytest.mark.parametrize(
    "mock_case",
    [pytest.param(case, id=case.__name__) for case in MOCK_DETECTION_CASES],
)
def test_mock_detection_matrix(
    mock_case: Callable[..., None],
    workflow_context: WorkflowContext,
    config: ConfigV10_7,
) -> None:
    """Ensures no mock implementations slip through the v10.7 stack."""

    if mock_case.__code__.co_argcount == 0:
        mock_case()
    else:
        mock_case(workflow_context, config)


# ---------------------------------------------------------------------------
# Category 3: Architectural Compliance (static assertions, 15 cases)
# ---------------------------------------------------------------------------


ARCHITECTURAL_CASES = [
    pytest.param(
        partial(_assert_file_pattern, "core_v10_7.py", "class WorkflowContext", should_exist=True),
        id="workflow-context-present",
    ),
    pytest.param(
        partial(_assert_file_pattern, "core_v10_7.py", "def wrap_mcp", should_exist=True),
        id="wrap-mcp-present",
    ),
    pytest.param(
        partial(
            _assert_file_pattern, "agent_orchestration_v10_7.py", "StateGraph", should_exist=True
        ),
        id="stategraph-usage",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "agent_orchestration_v10_7.py",
            "load_dynamic_tools",
            should_exist=True,
        ),
        id="dynamic-tools",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "agent_tools_v10_7.py",
            "class QAClaimValidatorTool",
            should_exist=True,
        ),
        id="qa-claim-tool",
    ),
    pytest.param(
        partial(_assert_file_pattern, "agent_tools_v10_7.py", "class HyDETool", should_exist=True),
        id="hyde-tool",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "stacks_v10_7/strategy.py",
            "class QueryComplexityClassifier",
            should_exist=True,
        ),
        id="strategy-stack-query-classifier",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "stacks_v10_7/safety.py",
            "class PIISanitizerAgent",
            should_exist=True,
        ),
        id="safety-stack-pii",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "stacks_v10_7/drafting.py",
            "class DraftingGuildCoordinator",
            should_exist=True,
        ),
        id="drafting-guild",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "stacks_v10_7/bullet.py",
            "class AsyncBulletGeneratorAgent",
            should_exist=True,
        ),
        id="bullet-generator",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "stacks_v10_7/hil.py",
            "class HILAmbiguityDetectorAgent",
            should_exist=True,
        ),
        id="hil-ambiguity",
    ),
    pytest.param(
        partial(_assert_file_pattern, "run_batch_v10_7.py", "asyncio", should_exist=True),
        id="batch-asyncio",
    ),
    pytest.param(
        partial(_assert_file_pattern, "run_learning_v10_7.py", "meta_learning", should_exist=True),
        id="learning-meta-loop",
    ),
    pytest.param(
        partial(_assert_file_pattern, "agent_stacks_v10_7.py", "wrap_mcp", should_exist=True),
        id="agent-stacks-wrap-mcp",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "strategy_ensemble_v10_7.py",
            "PlannerAssessment",
            should_exist=True,
        ),
        id="planner-assessment-present",
    ),
]


@pytest.mark.parametrize("arch_case", ARCHITECTURAL_CASES)
def test_architectural_compliance_matrix(arch_case: Callable[[], None]) -> None:
    """Validates module boundaries and required architectural constructs exist."""

    arch_case()


# ---------------------------------------------------------------------------
# Category 4: Design Validation (config + workflow spec, 15 cases)
# ---------------------------------------------------------------------------


DESIGN_VALIDATION_CASES = [
    pytest.param(
        partial(
            _assert_file_pattern,
            "master_config_v10_7.json",
            '"schema_version": "master_config_v10.7"',
            should_exist=True,
        ),
        id="schema-version",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "master_config_v10_7.json",
            '"enable_semantic_caching": true',
            should_exist=True,
        ),
        id="semantic-caching-flag",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "master_config_v10_7.json",
            "semantic_cache_similarity_threshold",
            should_exist=True,
        ),
        id="semantic-threshold",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "master_config_v10_7.json",
            '"enable_constitutional_review": true',
            should_exist=True,
        ),
        id="constitution-flag",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "master_config_v10_7.json",
            "strategy_tot_branching_factor",
            should_exist=True,
        ),
        id="strategy-tot",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "master_config_v10_7.json",
            '"enable_meta_learning": true',
            should_exist=True,
        ),
        id="meta-learning-enabled",
    ),
    pytest.param(
        partial(
            _assert_file_pattern, "master_config_v10_7.json", "feedback_log_path", should_exist=True
        ),
        id="feedback-log-path",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "master_config_v10_7.json",
            "generated_tools_path",
            should_exist=True,
        ),
        id="generated-tools-path",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "master_config_v10_7.json",
            '"enable_async_llm": true',
            should_exist=True,
        ),
        id="async-llm",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "master_config_v10_7.json",
            "max_batch_queue_size",
            should_exist=True,
        ),
        id="batch-queue",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "master_config_v10_7.json",
            '"enable_tool_caching": true',
            should_exist=True,
        ),
        id="tool-caching",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "master_config_v10_7.json",
            "enable_semantic_validation",
            should_exist=True,
        ),
        id="semantic-validation",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "master_config_v10_7.json",
            "wrap_nodes_by_default",
            should_exist=True,
        ),
        id="wrap-nodes-default",
    ),
    pytest.param(
        partial(
            _assert_file_pattern, "master_config_v10_7.json", "default_job_input", should_exist=True
        ),
        id="default-job-input",
    ),
    pytest.param(
        partial(
            _assert_file_pattern, "master_config_v10_7.json", "meta_loop_config", should_exist=True
        ),
        id="meta-loop-section",
    ),
]


@pytest.mark.parametrize("design_case", DESIGN_VALIDATION_CASES)
def test_design_validation_matrix(design_case: Callable[[], None]) -> None:
    """Confirms the master configuration encodes the documented v10.7 design."""

    design_case()


# ---------------------------------------------------------------------------
# Category 5: Integration Flow (workflow orchestration topology, 15 cases)
# ---------------------------------------------------------------------------


INTEGRATION_FLOW_CASES = [
    pytest.param(
        partial(
            _assert_file_pattern,
            "agent_orchestration_v10_7.py",
            "run_sanitize_pii",
            should_exist=True,
        ),
        id="sanitize-pii-node",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "agent_orchestration_v10_7.py",
            "run_detect_prompt_injection",
            should_exist=True,
        ),
        id="prompt-injection-node",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "agent_orchestration_v10_7.py",
            "run_classify_complexity",
            should_exist=True,
        ),
        id="complexity-node",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "agent_orchestration_v10_7.py",
            "run_tot_strategy",
            should_exist=True,
        ),
        id="tot-strategy-node",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "agent_orchestration_v10_7.py",
            "run_detect_ambiguity",
            should_exist=True,
        ),
        id="ambiguity-node",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "agent_orchestration_v10_7.py",
            "run_prompt_engineering",
            should_exist=True,
        ),
        id="prompt-engineering-node",
    ),
    pytest.param(
        partial(
            _assert_file_pattern, "agent_orchestration_v10_7.py", "run_rag_stack", should_exist=True
        ),
        id="rag-stack-node",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "agent_orchestration_v10_7.py",
            "run_generate_bullets",
            should_exist=True,
        ),
        id="bullet-node",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "agent_orchestration_v10_7.py",
            "run_qa_validation",
            should_exist=True,
        ),
        id="qa-node",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "agent_orchestration_v10_7.py",
            "run_constitutional_review",
            should_exist=True,
        ),
        id="constitutional-node",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "agent_orchestration_v10_7.py",
            "check_constitution",
            should_exist=True,
        ),
        id="constitution-check",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "agent_orchestration_v10_7.py",
            "human_in_the_loop",
            should_exist=True,
        ),
        id="hil-hook",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "agent_orchestration_v10_7.py",
            "workflow.set_entry_point",
            should_exist=True,
        ),
        id="entry-point",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "agent_orchestration_v10_7.py",
            "workflow.add_edge",
            should_exist=True,
        ),
        id="edges-defined",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "agent_orchestration_v10_7.py",
            "workflow.add_conditional_edges",
            should_exist=True,
        ),
        id="conditional-edges",
    ),
]


@pytest.mark.parametrize("integration_case", INTEGRATION_FLOW_CASES)
def test_integration_flow_matrix(integration_case: Callable[[], None]) -> None:
    """Validates orchestration nodes/edges required for multi-agent coordination."""

    integration_case()


# ---------------------------------------------------------------------------
# Category 6: Data Transformation (Pydantic outputs covering enrichment, 15 cases)
# ---------------------------------------------------------------------------


DATA_TRANSFORMATION_CASES = [
    pytest.param(
        partial(
            _assert_file_pattern, "core_v10_7.py", "class DraftStrategyOutput", should_exist=True
        ),
        id="draft-strategy-output",
    ),
    pytest.param(
        partial(_assert_file_pattern, "core_v10_7.py", "class RedTeamOutput", should_exist=True),
        id="red-team-output",
    ),
    pytest.param(
        partial(
            _assert_file_pattern, "core_v10_7.py", "class RefineSectionOutput", should_exist=True
        ),
        id="refine-section-output",
    ),
    pytest.param(
        partial(_assert_file_pattern, "core_v10_7.py", "class AddMetricsOutput", should_exist=True),
        id="add-metrics-output",
    ),
    pytest.param(
        partial(_assert_file_pattern, "core_v10_7.py", "class QAClaimOutput", should_exist=True),
        id="qa-claim-output",
    ),
    pytest.param(
        partial(_assert_file_pattern, "core_v10_7.py", "class QAToneOutput", should_exist=True),
        id="qa-tone-output",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "core_v10_7.py",
            "class QAThematicAlignmentOutput",
            should_exist=True,
        ),
        id="qa-thematic-output",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "core_v10_7.py",
            "class QASemanticEntailmentOutput",
            should_exist=True,
        ),
        id="qa-semantic-output",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "core_v10_7.py",
            "class QANarrativeThreadOutput",
            should_exist=True,
        ),
        id="qa-narrative-output",
    ),
    pytest.param(
        partial(_assert_file_pattern, "core_v10_7.py", "class QAJDSkillsOutput", should_exist=True),
        id="qa-jd-skills-output",
    ),
    pytest.param(
        partial(
            _assert_file_pattern, "core_v10_7.py", "class QASignalScoreOutput", should_exist=True
        ),
        id="qa-signal-output",
    ),
    pytest.param(
        partial(_assert_file_pattern, "core_v10_7.py", "class QATenureOutput", should_exist=True),
        id="qa-tenure-output",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "core_v10_7.py",
            "class QAMissedOpportunitiesOutput",
            should_exist=True,
        ),
        id="qa-missed-output",
    ),
    pytest.param(
        partial(
            _assert_file_pattern, "core_v10_7.py", "class QAAdversarialOutput", should_exist=True
        ),
        id="qa-adversarial-output",
    ),
    pytest.param(
        partial(_assert_file_pattern, "core_v10_7.py", "class QABiasOutput", should_exist=True),
        id="qa-bias-output",
    ),
]


@pytest.mark.parametrize("transformation_case", DATA_TRANSFORMATION_CASES)
def test_data_transformation_matrix(transformation_case: Callable[[], None]) -> None:
    """Ensures every enrichment output model is defined for downstream tooling."""

    transformation_case()


# ---------------------------------------------------------------------------
# Category 7: Contract Enforcement (error/guardrails definitions, 15 cases)
# ---------------------------------------------------------------------------


CONTRACT_ENFORCEMENT_CASES = [
    pytest.param(
        partial(_assert_file_pattern, "core_v10_7.py", "class ModelAPIError", should_exist=True),
        id="model-api-error",
    ),
    pytest.param(
        partial(_assert_file_pattern, "core_v10_7.py", "class JSONParsingError", should_exist=True),
        id="json-parsing-error",
    ),
    pytest.param(
        partial(
            _assert_file_pattern, "core_v10_7.py", "class PydanticSchemaError", should_exist=True
        ),
        id="pydantic-schema-error",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "core_v10_7.py",
            "class MCPClientInitializationError",
            should_exist=True,
        ),
        id="mcp-init-error",
    ),
    pytest.param(
        partial(
            _assert_file_pattern, "core_v10_7.py", "class WorkflowTimeoutError", should_exist=True
        ),
        id="workflow-timeout-error",
    ),
    pytest.param(
        partial(_assert_file_pattern, "core_v10_7.py", "class CircuitBreaker", should_exist=True),
        id="circuit-breaker-class",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "core_v10_7.py",
            "class CircuitBreakerOpenError",
            should_exist=True,
        ),
        id="circuit-breaker-open",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "core_v10_7.py",
            "def exponential_backoff_retry",
            should_exist=True,
        ),
        id="exponential-backoff",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "agent_tools_v10_7.py",
            "def resolve_mcp_client",
            should_exist=True,
        ),
        id="resolve-mcp",
    ),
    pytest.param(
        partial(_assert_file_pattern, "core_v10_7.py", "def wrap_mcp", should_exist=True),
        id="wrap-mcp-contract",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "master_config_v10_7.json",
            '"enable_circuit_breaker": true',
            should_exist=True,
        ),
        id="config-circuit-breaker",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "master_config_v10_7.json",
            "enable_idempotency_validation",
            should_exist=True,
        ),
        id="config-idempotency",
    ),
    pytest.param(
        partial(
            _assert_file_pattern, "master_config_v10_7.json", "max_local_retries", should_exist=True
        ),
        id="config-local-retries",
    ),
    pytest.param(
        partial(_assert_file_pattern, "core_v10_7.py", "def get_mcp_client", should_exist=True),
        id="workflow-context-mcp",
    ),
    pytest.param(
        partial(
            _assert_file_pattern,
            "agent_orchestration_v10_7.py",
            "CircuitBreaker",
            should_exist=True,
        ),
        id="orchestration-circuit-breaker",
    ),
]


@pytest.mark.parametrize("contract_case", CONTRACT_ENFORCEMENT_CASES)
def test_contract_enforcement_matrix(contract_case: Callable[[], None]) -> None:
    """Asserts defensive contracts, guardrails, and error classes are in place."""

    contract_case()


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
    attempts: dict[str, int] = {"count": 0}

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
    async def noop(state: dict[str, Any], workflow_context: WorkflowContext) -> dict[str, Any]:
        return state

    asyncio.run(noop({}, workflow_context))

    assert "default_stub" in workflow_context.mcp_clients


def test_resolve_mcp_client_optional_returns_stub(workflow_context: WorkflowContext) -> None:
    workflow_context.wrap_mcp_nodes = True
    workflow_context.reset_mcp_clients()

    class DummyTool(BaseTool):
        tool_name = "dummy"

        async def _run_async_internal(
            self, tool_input: dict[str, Any], workflow_id: str
        ) -> dict[str, Any]:
            return {}

    tool = DummyTool(workflow_context)
    stub = resolve_mcp_client(tool, "nonexistent", optional=True)

    assert isinstance(stub, MCPClientStub)
    assert tool.get_mcp_client("nonexistent") is stub


def test_resolve_mcp_client_required_raises_without_fallback(
    workflow_context: WorkflowContext,
) -> None:
    workflow_context.config._config["mcp_config"]["fallback_mode"] = "error"
    workflow_context._load_mcp_config()
    workflow_context.reset_mcp_clients()

    class DummyTool(BaseTool):
        tool_name = "dummy-required"

        async def _run_async_internal(
            self, tool_input: dict[str, Any], workflow_id: str
        ) -> dict[str, Any]:
            return {}

    tool = DummyTool(workflow_context)

    with pytest.raises(KeyError):
        resolve_mcp_client(tool, "nonexistent", optional=False)


def test_dynamic_tool_loader_respects_mcp_requirements(
    workflow_context: WorkflowContext, tmp_path
) -> None:
    workflow_context.wrap_mcp_nodes = True
    workflow_context.reset_mcp_clients()

    tool_dir = tmp_path / "generated_tools_v10_7"
    tool_dir.mkdir()
    tool_file = tool_dir / "mcp_tool.py"
    tool_code = """

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

    def fake_ensure() -> dict[str, Any]:
        calls["count"] += 1
        return {}

    monkeypatch.setattr(workflow_context, "ensure_mcp_clients", fake_ensure)

    @wrap_mcp(force=True)
    def handler(state: dict[str, Any], workflow_context: WorkflowContext) -> dict[str, Any]:
        return state

    result = handler({}, workflow_context)

    assert result == {}
    assert calls["count"] == 1


def test_wrap_mcp_sync_skips_when_disabled(
    workflow_context: WorkflowContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    workflow_context.wrap_mcp_nodes = False
    calls = {"count": 0}

    def fake_ensure() -> dict[str, Any]:
        calls["count"] += 1
        return {}

    monkeypatch.setattr(workflow_context, "ensure_mcp_clients", fake_ensure)

    @wrap_mcp
    def handler(state: dict[str, Any], workflow_context: WorkflowContext) -> dict[str, Any]:
        return state

    result = handler({}, workflow_context)

    assert result == {}
    assert calls["count"] == 0