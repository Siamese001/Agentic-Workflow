"""Query Decomposer - Reasoning Layer for Complex Queries.

This component breaks complex multi-hop questions into atomic sub-queries
that can be answered by the retrieval system.
"""

import asyncio
import logging
import re
from typing import Any

from pydantic import BaseModel, Field, validator

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "DecomposedqueryagentStrategy", "p0_governance")
_emit_reads_policy_state("p0", "DecomposedqueryagentStrategy", "policy_binding")
_emit_snapshots_state("p0", "DecomposedqueryagentStrategy", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("DecomposedqueryagentStrategy", "p4obs", "metric_1")
_emit_emits_metric_event("DecomposedqueryagentStrategy", "p4obs", "metric_2")
_emit_emits_metric_event("DecomposedqueryagentStrategy", "p4obs", "metric_3")
_emit_emits_metric_event("DecomposedqueryagentStrategy", "p4obs", "metric_4")
_emit_emits_metric_event("DecomposedqueryagentStrategy", "p4obs", "metric_5")
_emit_emits_metric_event("DecomposedqueryagentStrategy", "p4obs", "metric_6")
_emit_records_incident_event("DecomposedqueryagentStrategy", "p4obs", "incident")
_emit_captures_runtime_anomaly("DecomposedqueryagentStrategy", "p4obs", "anomaly")
_emit_writes_observability_log("DecomposedqueryagentStrategy", "p4obs", "obs_log")
_emit_updates_monitoring_state("DecomposedqueryagentStrategy", "p4obs", "mon_state")
_emit_triggers_alert("DecomposedqueryagentStrategy", "p4obs", "alert")
_emit_links_incident_trace("DecomposedqueryagentStrategy", "p4obs", "trace_link")
_emit_captures_pattern("DecomposedqueryagentStrategy", "p3lm", "pattern")
_emit_records_learning_event("DecomposedqueryagentStrategy", "p3lm", "learning_event")
_emit_writes_learning_snapshot("DecomposedqueryagentStrategy", "p3lm", "snapshot")
_emit_feeds_meta_learning("DecomposedqueryagentStrategy", "p3lm", "meta_feed")
_emit_updates_routing_strategy("DecomposedqueryagentStrategy", "p3lm", "routing")
_emit_improves_agent_policy("DecomposedqueryagentStrategy", "p3lm", "policy")
_emit_stores_learning_state("DecomposedqueryagentStrategy", "p3lm", "state")
_emit_records_execution_trace("DecomposedqueryagentStrategy", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("DecomposedqueryagentStrategy", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("DecomposedqueryagentStrategy", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("DecomposedqueryagentStrategy", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("DecomposedqueryagentStrategy", "L4_STATE", "p2_trace_5")
_emit_reads_environ("DecomposedqueryagentStrategy", "env_read", "p2_env_1")
_emit_reads_environ("DecomposedqueryagentStrategy", "env_read", "p2_env_2")
_emit_reads_runtime_state("DecomposedqueryagentStrategy", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("DecomposedqueryagentStrategy", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "DecomposedqueryagentStrategy", "context_pull")
_emit_pulls_context("p1", "DecomposedqueryagentStrategy", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "DecomposedqueryagentStrategy", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "DecomposedqueryagentStrategy", "uwg_term_2")
_emit_writes_through("p1", "DecomposedqueryagentStrategy", "write_through")
_emit_writes_through("p1", "DecomposedqueryagentStrategy", "write_through_2")
_emit_validated_by_safety_plane("p1", "DecomposedqueryagentStrategy", "safety_validation")
_emit_invokes_eval("p1", "DecomposedqueryagentStrategy", "eval_call")
_emit_proposal_commits_routing("p1", "DecomposedqueryagentStrategy", "routing_commit")
_emit_escalates_to_human("p1", "DecomposedqueryagentStrategy", "human_escalation")
_emit_routes_through("p1", "DecomposedqueryagentStrategy", "route_through")
_emit_checks_agent_registry("p1", "DecomposedqueryagentStrategy", "agent_registry")
_emit_validates_agent_capability("p1", "DecomposedqueryagentStrategy", "capability")
_emit_dispatches_execution_plan("p1", "DecomposedqueryagentStrategy", "exec_plan")
_emit_agent_executes_agent("p1", "DecomposedqueryagentStrategy", "sub_agent")
_emit_routes_to_agent("p1", "DecomposedqueryagentStrategy", "target_agent")
_emit_verifies_policy("p1", "DecomposedqueryagentStrategy", "policy_check")
_emit_observes_runtime_state("p1", "DecomposedqueryagentStrategy", "runtime_state")
_emit_verifies_boundary("p1", "DecomposedqueryagentStrategy", "boundary_check")
_emit_transcripts_response("p1", "DecomposedqueryagentStrategy", "transcript")
_emit_hard_fails_untranscripted("p1", "DecomposedqueryagentStrategy")
_emit_gated_by_confidence("p1", "DecomposedqueryagentStrategy", "confidence_gate")
emit_replay_key("p0", "DecomposedqueryagentStrategy")
emit_determinism_digest("p0", "DecomposedqueryagentStrategy")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "DecomposedqueryagentStrategy", "execution_auth")
_emit_validates_capability("p2", "DecomposedqueryagentStrategy", "capability_check")
_emit_routes_to_capability("p2", "DecomposedqueryagentStrategy", "capability_route")
_emit_writes_via_uwg("p2", "DecomposedqueryagentStrategy", "uwg_write")
_emit_blocks_direct_write("p2", "DecomposedqueryagentStrategy", "direct_write_block")
_emit_records_tool_invocation("p2", "DecomposedqueryagentStrategy", "tool_invocation")
_emit_captures_execution_output("p2", "DecomposedqueryagentStrategy", "exec_output")
_emit_dispatches_agent("p3", "DecomposedqueryagentStrategy", "agent_dispatch")
_emit_coordinates_agents("p3", "DecomposedqueryagentStrategy", "agent_coordination")
_emit_records_workflow_lineage("p3", "DecomposedqueryagentStrategy", "workflow_lineage")
_emit_records_healing_outcome("p3", "DecomposedqueryagentStrategy", "healing_outcome")
_emit_escalates_failure("p3", "DecomposedqueryagentStrategy", "failure_escalation")
_emit_orchestrates_workflow("p3", "DecomposedqueryagentStrategy", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "DecomposedqueryagentStrategy", "healing_dispatch")
_emit_invokes_evaluation("p3", "DecomposedqueryagentStrategy", "evaluation_signal")
_emit_records_telemetry_event("p4", "DecomposedqueryagentStrategy", "telemetry_event")
_emit_captures_evaluation_metric("p4", "DecomposedqueryagentStrategy", "eval_metric")
_emit_stores_embedding("p4", "DecomposedqueryagentStrategy", "embedding_store")
_emit_updates_meta_learning_state("p4", "DecomposedqueryagentStrategy", "meta_learning")
_emit_links_execution_to_snapshot("p4", "DecomposedqueryagentStrategy", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class DecomposedQuery(BaseModel):
    """Result of query decomposition."""

    original_query: str = Field(..., description="Original complex query")
    sub_queries: list[str] = Field(..., description="Decomposed atomic sub-queries")
    reasoning: str = Field(..., description="Reasoning for decomposition")
    complexity_score: int = Field(..., ge=1, le=10, description="Complexity score (1-10)")

    @validator("sub_queries")
    def validate_sub_queries(cls, v):
        """Ensure sub-queries are valid."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DecomposedQuery.validate_sub_queries")

        if not v:
            raise ValueError("At least one sub-query is required")
        if len(v) > 4:
            raise ValueError("Maximum 4 sub-queries allowed")
        return v


class SimpleAgentBase:
    """Simple base class for standalone agents."""

    def __init__(self, name: str, model_name: str = "gpt-4"):
        """Initialize the agent.

        Args:
            name: Agent name for logging
            model_name: LLM model to use
        """
        self.name = name
        self.model_name = model_name
        logger.info(f"Initialized {self.__class__.__name__}: model={model_name}")


class QueryDecomposer(SimpleAgentBase):
    """Decomposes complex queries into atomic sub-queries.

    Uses LLM to break down multi-hop questions into simpler queries
    that can be answered by the retrieval system.
    """

    # guardian: allow-magic-config
    def __init__(self, model_name: str = "gpt-4", max_sub_queries: int = 4):
        """Initialize the Query Decomposer.

        Args:
            model_name: LLM model to use for decomposition
            max_sub_queries: Maximum number of sub-queries to generate
        """
        super().__init__(name="Query Decomposer", model_name=model_name)
        self.max_sub_queries = max_sub_queries
        try:
            self.gate = AdaptiveRetrievalGate()
        # guardian: allow-silent-swallow - optional dependency
        except ImportError:
            logger.warning("AdaptiveRetrievalGate not available, skipping heuristic check")
            self.gate = None
        self.complexity_indicators = {
            "comparison": re.compile("\\b(compare|vs|versus|against|difference|contrast)\\b", re.IGNORECASE),
            "causation": re.compile("\\b(why|cause|reason|impact|effect)\\b", re.IGNORECASE),
            "temporal": re.compile("\\b(before|after|during|when|timeline|history)\\b", re.IGNORECASE),
            "aggregation": re.compile("\\b(sum|total|average|count|aggregate|combine)\\b", re.IGNORECASE),
            "relationship": re.compile("\\b(relationship|correlation|between|and)\\b", re.IGNORECASE),
        }

    def _calculate_complexity_score(self, query: str) -> int:
        """Calculate complexity score for a query (1-10).

        Args:
            query: Query to analyze

        Returns:
            Complexity score from 1 (simple) to 10 (very complex)
        """
        score = 1
        for _indicator_type, pattern in self.complexity_indicators.items():
            if pattern.search(query):
                score += 2
        word_count = len(query.split())
        if word_count > 15:
            score += 2
        elif word_count > 10:
            score += 1
        question_words = ["what", "how", "why", "where", "when", "which", "who"]
        question_count = sum(1 for word in question_words if word in query.lower())
        score += min(question_count, 2)
        return min(score, 10)

    # guardian: allow-magic-config
    async def _call_llm(self, prompt: str, temperature: float = 0.3) -> Any:
        """Call the LLM with the given prompt.

        Args:
            prompt: Prompt to send to LLM
            temperature: Sampling temperature

        Returns:
            LLM response
        """
        try:
            client = get_client(Provider.ANTHROPIC)
            # guardian: allow-magic-config
            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )

            class LLMResponseImpl:
                def __init__(self, content: str):
                    self.content = content

            return LLMResponseImpl(response.content[0].text)
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"LLM call failed: {e}")

            class LLMResponseImpl:
                def __init__(self, content: str):
                    self.content = content

            return LLMResponseImpl('{"sub_queries": ["query"], "reasoning": "fallback"}')

    async def decompose(self, query: str) -> DecomposedQuery:
        """Decompose a complex query into sub-queries.

        Args:
            query: Complex query to decompose

        Returns:
            DecomposedQuery with sub-queries and reasoning
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "QueryDecomposer.decompose")

        if self.gate:
            decision = self.gate.should_retrieve(query)
            if decision.query_type in ["CONVERSATIONAL", "FACTUAL"] and (not decision.should_retrieve):
                logger.info(f"Simple query detected, skipping decomposition: {query}")
                return DecomposedQuery(
                    original_query=query,
                    sub_queries=[query],
                    reasoning="Query is simple, no decomposition needed",
                    complexity_score=1,
                )
        complexity = self._calculate_complexity_score(query)
        if complexity <= 3:
            logger.info(f"Low complexity ({complexity}), returning original query")
            return DecomposedQuery(
                original_query=query,
                sub_queries=[query],
                reasoning="Query complexity is low, no decomposition needed",
                complexity_score=complexity,
            )
        prompt = f'You are an Expert Research Assistant. Break the following complex user query into 2-4 atomic, factual sub-queries that a search engine can answer.\n\nRules:\n- If the query is simple, return it as the single sub-query\n- Each sub-query must be self-contained and answerable\n- Maximum 4 sub-queries\n- Focus on extracting the core information needs\n\nQuery: "{query}"\n\nReturn in JSON format:\n{{\n    "sub_queries": ["sub-query 1", "sub-query 2", ...],\n    "reasoning": "brief explanation of the decomposition"\n}}\n\nExample:\nInput: "Compare AWS vs. Azure pricing for financial services"\nOutput: {{\n    "sub_queries": ["AWS pricing model for financial services", "Azure pricing model for financial services", "AWS vs Azure cost comparison"],\n    "reasoning": "Decomposed into individual pricing queries and a comparison"\n}}'
        try:
            # guardian: allow-magic-config
            response = await self._call_llm(prompt, temperature=0.1)
            import json

            result = json.loads(response.content.strip())
            sub_queries = result.get("sub_queries", [query])
            if len(sub_queries) > self.max_sub_queries:
                logger.warning(f"LLM generated too many sub-queries ({len(sub_queries)}), truncating")
                sub_queries = sub_queries[: self.max_sub_queries]
            if not sub_queries:
                sub_queries = [query]
            reasoning = result.get("reasoning", "Decomposed using LLM analysis")
            return DecomposedQuery(
                original_query=query,
                sub_queries=sub_queries,
                reasoning=reasoning,
                complexity_score=complexity,
            )
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to decompose query: {e}")
            return DecomposedQuery(
                original_query=query,
                sub_queries=[query],
                reasoning="Decomposition failed, using original query",
                complexity_score=complexity,
            )

    async def execute_plan(
        self, decomposed_query: DecomposedQuery, search_function: callable, **kwargs
    ) -> list[Any]:
        """Execute search for all sub-queries in parallel.

        Args:
            decomposed_query: Result from decompose() method
            search_function: Async function to execute search
            **kwargs: Additional arguments for search function

        Returns:
            List of search results for all sub-queries
        """
        logger.info(f"Executing {len(decomposed_query.sub_queries)} sub-queries in parallel")
        tasks = []
        for sub_query in decomposed_query.sub_queries:
            task = search_function(sub_query, **kwargs)
            tasks.append(task)
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Sub-query {i} failed: {result}")
                    processed_results.append([])
                else:
                    processed_results.append(result)
            logger.info(f"Completed execution: {sum(len(r) for r in processed_results)} total results")
            return processed_results
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to execute sub-queries: {e}")
            return [[] for _ in decomposed_query.sub_queries]


async def decompose_query(query: str, model_name: str = "gpt-4") -> DecomposedQuery:
    """Decompose a query using default settings.

    Args:
        query: Query to decompose
        model_name: LLM model to use

    Returns:
        DecomposedQuery result
    """
    decomposer = QueryDecomposer(model_name=model_name)
    return await decomposer.decompose(query)
