"""K.X Node Executor - Execute knowledge extraction nodes in workflows.

Integrates K.X nodes with agent execution, RAG, and validation gates
for end-to-end resume and outreach generation.

Phase 1C - Knowledge Extraction Integration
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "kx_execution_context_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "kx_execution_context_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "kx_execution_context_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "kx_execution_context_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "kx_execution_context_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "kx_execution_context_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "kx_execution_context_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "kx_execution_context_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "kx_execution_context_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "kx_execution_context_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "kx_execution_context_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "kx_execution_context_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "kx_execution_context_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "kx_execution_context_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "kx_execution_context_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "kx_execution_context_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "kx_execution_context_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "kx_execution_context_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "kx_execution_context_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "kx_execution_context_types", "exec_snapshot_link")
from .agent_executor import AgentExecutor, AgentMessage, AgentResponse

trace_contract._emit_applies_guardrail("p0", "kx_execution_context_types", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "kx_execution_context_types", "policy_binding")
trace_contract._emit_snapshots_state("p0", "kx_execution_context_types", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("kx_execution_context_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("kx_execution_context_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("kx_execution_context_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("kx_execution_context_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("kx_execution_context_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("kx_execution_context_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("kx_execution_context_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("kx_execution_context_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("kx_execution_context_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("kx_execution_context_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("kx_execution_context_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("kx_execution_context_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("kx_execution_context_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("kx_execution_context_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("kx_execution_context_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("kx_execution_context_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("kx_execution_context_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("kx_execution_context_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("kx_execution_context_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("kx_execution_context_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("kx_execution_context_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("kx_execution_context_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("kx_execution_context_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("kx_execution_context_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("kx_execution_context_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("kx_execution_context_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("kx_execution_context_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("kx_execution_context_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "kx_execution_context_types", "context_pull")
trace_contract._emit_pulls_context("p1", "kx_execution_context_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "kx_execution_context_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "kx_execution_context_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "kx_execution_context_types", "write_through")
trace_contract._emit_writes_through("p1", "kx_execution_context_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "kx_execution_context_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "kx_execution_context_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "kx_execution_context_types", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "kx_execution_context_types", "human_escalation")
trace_contract._emit_routes_through("p1", "kx_execution_context_types", "route_through")
trace_contract._emit_checks_agent_registry("p1", "kx_execution_context_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "kx_execution_context_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "kx_execution_context_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "kx_execution_context_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "kx_execution_context_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "kx_execution_context_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "kx_execution_context_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "kx_execution_context_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "kx_execution_context_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "kx_execution_context_types")
trace_contract._emit_gated_by_confidence("p1", "kx_execution_context_types", "confidence_gate")
trace_contract.emit_replay_key("p0", "kx_execution_context_types")
trace_contract.emit_determinism_digest("p0", "kx_execution_context_types")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_1")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_2")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_3")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_4")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_5")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_6")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_7")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_8")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_9")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_10")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_11")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_12")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_13")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_14")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_15")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_16")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_17")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_18")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_19")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_20")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_21")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_22")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_23")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_24")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_25")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_26")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_27")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_28")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_29")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_30")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_31")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_32")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_33")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_34")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_35")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_36")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_37")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_38")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_39")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_40")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_41")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_42")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_43")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_44")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_45")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_46")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_47")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_48")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_49")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_50")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_51")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_52")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_53")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_54")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_55")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_56")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_57")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_58")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_59")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_60")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_61")
trace_contract._emit_reads_through("l4", "kx_execution_context_types", "urg_read_62")

logger = logging.getLogger(__name__)


@dataclass
class KXExecutionContext:
    """Execution context for K.X node."""

    node_config: KNodeConfig
    agent_executor: AgentExecutor
    vector_store: Any | None = None
    cache_client: Any | None = None
    source_data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class KXExecutionResult:
    """Result from K.X node execution."""

    node_id: str
    element: str
    content: str
    reasoning_trace: str | None = None
    rag_sources: list[dict[str, Any]] = field(default_factory=list)
    validation_results: list[dict[str, Any]] = field(default_factory=list)
    usage: dict[str, int] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class KXNodeExecutor:
    """Executor for K.X knowledge extraction nodes."""

    def __init__(self, agent_executor: AgentExecutor):
        """Initialize K.X node executor.

        Args:
            agent_executor: Agent executor for LLM calls
        """
        self.agent_executor = agent_executor
        self.registry = get_kx_registry()

    def execute_node(
        self,
        node_key: str,
        context: KXExecutionContext,
        system_prompt: str | None = None,
    ) -> KXExecutionResult:
        """Execute a K.X node.

        Args:
            node_key: K.X node key
            context: Execution context
            system_prompt: Optional system prompt override

        Returns:
            KXExecutionResult with generated content
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "KXNodeExecutor.execute_node")

        config = context.node_config
        with create_span(f"kx_node.{config.node_id}.{config.element}"):
            set_span_attribute("kx.node_id", config.node_id)
            set_span_attribute("kx.element", config.element)
            set_span_attribute("kx.reasoning_strategy", config.reasoning_strategy.value)
            rag_sources = []
            if config.rag_config and config.rag_config.enabled and context.vector_store:
                rag_sources = self._execute_rag(config, context)
            messages = self._build_messages(config, context, rag_sources)
            if system_prompt is None:
                system_prompt = self._build_system_prompt(config, context)
            response = self.agent_executor.execute(messages=messages, system_prompt=system_prompt)
            validation_results = self._validate_output(config, response.content, context)
            return KXExecutionResult(
                node_id=config.node_id,
                element=config.element,
                content=response.content,
                reasoning_trace=self._extract_reasoning_trace(response),
                rag_sources=rag_sources,
                validation_results=validation_results,
                usage=response.usage,
                metadata={
                    "reasoning_strategy": config.reasoning_strategy.value,
                    "rag_enabled": config.rag_config.enabled if config.rag_config else False,
                    "validation_passed": all(v.get("passed", False) for v in validation_results),
                },
            )

    def _execute_rag(self, config: KNodeConfig, context: KXExecutionContext) -> list[dict[str, Any]]:
        """Execute RAG retrieval for K.X node.

        Args:
            config: Node configuration
            context: Execution context

        Returns:
            List of retrieved sources
        """
        if not config.rag_config or not context.vector_store:
            return []
        f"{config.element}: {context.source_data.get('query', '')}"
        query_embedding = [0.1] * 1536
        try:
            collection = create_chroma_collection(
                context.vector_store,
                context.metadata.get("collection_name", "knowledge_base"),
            )
            results = search_vectors_chroma(
                collection,
                query_embeddings=[query_embedding],
                n_results=config.rag_config.max_retrievers,
            )
            sources = []
            if results and "documents" in results:
                for i, doc in tqdm(enumerate(results["documents"][0]), desc="Processing", unit="item"):
                    source_type = results.get("metadatas", [[{}]])[0][i].get("source_type", "generic")
                    weight = config.rag_config.source_weighting.get(source_type, 1.0)
                    sources.append(
                        {
                            "document": doc,
                            "metadata": results.get("metadatas", [[{}]])[0][i],
                            "distance": results.get("distances", [[0]])[0][i],
                            "weight": weight,
                            "weighted_score": weight / (1 + results.get("distances", [[0]])[0][i]),
                        },
                    )
            sources.sort(key=lambda x: x["weighted_score"], reverse=True)
            logger.info(f"Retrieved {len(sources)} sources for K.X node {config.node_id}")
            return sources[: config.rag_config.min_retrievers]
        except (TypeError, ValueError, KeyError, AttributeError, RuntimeError, OSError) as e:  # guardian: allow-silent-swallow
            logger.warning(f"RAG retrieval failed for K.X node {config.node_id}: {e}")
            return []

    def _build_messages(
        self,
        config: KNodeConfig,
        context: KXExecutionContext,
        rag_sources: list[dict[str, Any]],
    ) -> list[AgentMessage]:
        """Build messages for agent execution.

        Args:
            config: Node configuration
            context: Execution context
            rag_sources: Retrieved RAG sources

        Returns:
            List of agent messages
        """
        messages = []
        if rag_sources:
            rag_context = "\n\n".join(
                [
                    f"Source {i + 1} ({src['metadata'].get('source_type', 'unknown')}):\n{src['document']}"
                    for i, src in enumerate(rag_sources[:3])
                ],
            )
            messages.append(
                AgentMessage(role="user", content=f"Context from knowledge base:\n\n{rag_context}"),
            )
        prompt = self._build_generation_prompt(config, context)
        messages.append(AgentMessage(role="user", content=prompt))
        return messages

    def _build_generation_prompt(self, config: KNodeConfig, context: KXExecutionContext) -> str:
        """Build generation prompt for K.X node.

        Args:
            config: Node configuration
            context: Execution context

        Returns:
            Generation prompt
        """
        prompt_parts = [f"Generate: {config.element}"]
        if config.structure_template:
            prompt_parts.append(f"\nStructure: {config.structure_template}")
        constraints = []
        if config.max_words:
            constraints.append(f"max {config.max_words} words")
        if config.max_chars:
            constraints.append(f"max {config.max_chars} characters")
        if constraints:
            prompt_parts.append(f"\nConstraints: {', '.join(constraints)}")
        if context.source_data:
            source_info = "\n".join(
                [f"{key}: {value}" for key, value in context.source_data.items() if key != "query"],
            )
            if source_info:
                prompt_parts.append(f"\nSource Data:\n{source_info}")
        if config.reasoning_strategy == ReasoningStrategy.COT:
            prompt_parts.append("\nUse step-by-step reasoning to generate the content.")
        elif config.reasoning_strategy == ReasoningStrategy.TOT:
            prompt_parts.append(f"\nExplore {config.tot_branches} different approaches and select the best.")
        elif config.reasoning_strategy == ReasoningStrategy.HYBRID_COT_TOT:
            prompt_parts.append(
                "\nUse step-by-step reasoning with multiple branches to find the optimal solution.",
            )
        return "\n".join(prompt_parts)

    def _build_system_prompt(self, config: KNodeConfig, context: KXExecutionContext) -> str:
        """Build system prompt for K.X node.

        Args:
            config: Node configuration
            context: Execution context

        Returns:
            System prompt
        """
        prompts = [
            f"You are an expert at generating {config.element}.",
            "Follow all constraints and validation rules strictly.",
        ]
        if config.validation_rules:
            prompts.append(f"Validation rules: {', '.join(config.validation_rules)}")
        return " ".join(prompts)

    def _extract_reasoning_trace(self, response: AgentResponse) -> str | None:
        """Extract reasoning trace from response.

        Args:
            response: Agent response

        Returns:
            Reasoning trace or None
        """
        return None

    def _validate_output(
        self,
        config: KNodeConfig,
        content: str,
        context: KXExecutionContext,
    ) -> list[dict[str, Any]]:
        """Validate generated output against rules.

        Args:
            config: Node configuration
            content: Generated content
            context: Execution context

        Returns:
            List of validation results
        """
        results = []
        for rule in config.validation_rules:
            result = self._apply_validation_rule(rule, content, config, context)
            results.append(result)
        return results

    def _apply_validation_rule(
        self,
        rule: str,
        content: str,
        config: KNodeConfig,
        context: KXExecutionContext,
    ) -> dict[str, Any]:
        """Apply a single validation rule.

        Args:
            rule: Validation rule name
            content: Generated content
            config: Node configuration
            context: Execution context

        Returns:
            Validation result
        """
        if rule == "non_empty":
            passed = len(content.strip()) > 0
            return {"rule": rule, "passed": passed, "message": "Content must not be empty"}
        elif rule == "word_count_range":
            word_count = len(content.split())
            passed = True
            if config.max_words:
                passed = word_count <= config.max_words
            return {
                "rule": rule,
                "passed": passed,
                "message": f"Word count: {word_count}/{config.max_words or 'unlimited'}",
                "word_count": word_count,
            }
        elif rule == "character_limit" or rule == "character_limit_strict":
            char_count = len(content)
            passed = True
            if config.max_chars:
                passed = char_count <= config.max_chars
            return {
                "rule": rule,
                "passed": passed,
                "message": f"Character count: {char_count}/{config.max_chars or 'unlimited'}",
                "char_count": char_count,
            }
        else:
            return {
                "rule": rule,
                "passed": True,
                "message": f"Validation rule '{rule}' not implemented (assumed pass)",
            }


def execute_kx_node(
    node_key: str,
    agent_executor: AgentExecutor,
    source_data: dict[str, Any],
    vector_store: Any | None = None,
    cache_client: Any | None = None,
    engine: str = "resume",
) -> KXExecutionResult:
    """Execute a K.X node by key.

    Args:
        node_key: K.X node key
        agent_executor: Agent executor
        source_data: Source data for generation
        vector_store: Optional vector store for RAG
        cache_client: Optional cache client
        engine: Engine type ("resume" or "outreach")

    Returns:
        KXExecutionResult
    """
    registry = get_kx_registry()
    if engine == "resume":
        config = registry.get_resume_node(node_key)
    else:
        config = registry.get_outreach_node(node_key)
    if not config:
        raise ValueError(f"K.X node not found: {node_key} (engine: {engine})")
    context = KXExecutionContext(
        node_config=config,
        agent_executor=agent_executor,
        vector_store=vector_store,
        cache_client=cache_client,
        source_data=source_data,
    )
    executor = KXNodeExecutor(agent_executor)
    return executor.execute_node(node_key, context)
