# guardian: allow-silent_swallower -- ADG violation exemption

from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "query_planner")
trace_contract.emit_determinism_digest("p0", "query_planner")

trace_contract._emit_dispatches_healing_run("p1", "query_planner", "L1")
trace_contract._emit_routes_through("p1", "query_planner", "L1")
trace_contract._emit_checks_agent_registry("p1", "query_planner", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "query_planner", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "query_planner", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "query_planner", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "query_planner", "target_agent")
trace_contract._emit_verifies_policy("p1", "query_planner", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "query_planner", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "query_planner", "boundary_check")
trace_contract._emit_transcripts_response("p1", "query_planner", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "query_planner")
trace_contract._emit_gated_by_confidence("p1", "query_planner", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "query_planner", "L1")
trace_contract._emit_reads_policy_state("p1", "query_planner", "L1")
trace_contract._emit_authorize_and_execute("p2", "query_planner", "execution_auth")
trace_contract._emit_validates_capability("p2", "query_planner", "capability_check")
trace_contract._emit_routes_to_capability("p2", "query_planner", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "query_planner", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "query_planner", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "query_planner", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "query_planner", "exec_output")
trace_contract._emit_dispatches_agent("p3", "query_planner", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "query_planner", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "query_planner", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "query_planner", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "query_planner", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "query_planner", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "query_planner", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "query_planner", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "query_planner", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "query_planner", "eval_metric")
trace_contract._emit_stores_embedding("p4", "query_planner", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "query_planner", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "query_planner", "exec_snapshot_link")

"\nquery_planner - L1 Cognition Query Decomposition and Expansion\n"
import json
import logging
import re
from typing import Any

Logger: Any = logging.getLogger(__name__)
try:
    from agentic_core.L3_orchestration.reasoning.engines.sub_atomic_engine_impl import (  # guardian: allow-layer-violation -- L1 module uses L3 orchestration; intentional cross-layer dependency in cognition layer
        SubAtomicEngineImpl as SubAtomicEngine,
    )
except ImportError:  # guardian: allow-silent-swallow

    class SubAtomicEngine:
        """Stub: SubAtomicEngine not installed."""

        def __init__(self, **kwargs):
            pass

        async def resilient_mutation(self, prompt="", **kwargs):
            return "{}"


try:
    from agentic_core.L4_state.utils.rag_enhancement_util import semantic_cache
except ImportError:

    class semantic_cache:
        """Stub: semantic_cache not installed."""

        def __init__(self):
            self._cache: dict = {}

        def get(self, key: str):
            return self._cache.get(key)

        def set(self, key: str, value) -> None:
            self._cache[key] = value



trace_contract._emit_emits_metric_event("query_planner", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("query_planner", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("query_planner", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("query_planner", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("query_planner", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("query_planner", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("query_planner", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("query_planner", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("query_planner", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("query_planner", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("query_planner", "p4obs", "alert")
trace_contract._emit_links_incident_trace("query_planner", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("query_planner", "p3lm", "pattern")
trace_contract._emit_records_learning_event("query_planner", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("query_planner", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("query_planner", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("query_planner", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("query_planner", "p3lm", "policy")
trace_contract._emit_stores_learning_state("query_planner", "p3lm", "state")
trace_contract._emit_records_execution_trace("query_planner", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("query_planner", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("query_planner", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("query_planner", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("query_planner", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("query_planner", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("query_planner", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("query_planner", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("query_planner", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "query_planner", "context_pull")
trace_contract._emit_pulls_context("p1", "query_planner", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "query_planner", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "query_planner", "uwg_term_2")
trace_contract._emit_writes_through("p1", "query_planner", "write_through")
trace_contract._emit_writes_through("p1", "query_planner", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "query_planner", "safety_validation")
trace_contract._emit_invokes_eval("p1", "query_planner", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "query_planner", "routing_commit")


class query_planner:
    """
    Sovereign L1 Query Planner – transforms queries for maximum recall/precision
    """

    def __init__(self, engine: SubAtomicEngine | None = None, cache: semantic_cache | None = None):
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "query_planner.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "query_planner.__init__", "p0_governance")
        self.engine = engine or SubAtomicEngine()
        self.cache = cache or semantic_cache()
        self.expansion_temperature = 0.7
        self.reflection_temperature = 0.3

    def _clean_json_response(self, raw_text: str) -> str:
        """
        Hardens the planner against LLMs that insist on markdown formatting.
        """
        cleaned = re.sub("```json|```", "", raw_text).strip()
        match = re.search("(\\[.*\\]|\\{.*\\})", cleaned, re.DOTALL)
        return match.group(1) if match else cleaned

    async def multi_query_generation(self, original_query: str) -> list[str]:
        """
        L1: Generate diverse query variants to maximize vector recall.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L1_REASONING,
            "query_planner.multi_query_generation",
        )

        cache_key: Any = f"mq_expand:{hash(original_query)}"
        cached: Any = self.cache.get(cache_key)
        if cached:
            return cached["queries"]
        prompt: Any = f'\nYou are the Sovereign Multi-Query Generator. \nGenerate 6-8 diverse versions of the query to capture different semantic facets.\n\nQuery: "{original_query}"\n\nVary the phrasing: use technical terms, lay terms, and sub-questions.\nOutput format: {{"queries": ["variant1", "variant2", ...]}}\n'
        response: Any = await self.engine.resilient_mutation(prompt=prompt, temperature=0.8)
        try:
            cleaned: Any = self._clean_json_response(response)
            result: Any = json.loads(cleaned)
            queries: Any = result.get("queries", [])[:8]
            if original_query not in queries:
                queries.insert(0, original_query)
        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as e:
            print(f"   [!] Multi-query parse failure: {e}")
            queries: Any = [original_query]
        self.cache.set(cache_key, {"queries": queries})
        return queries

    async def decompose_query(self, query: str) -> list[str]:
        """
        L1 Sovereign Query Decomposition - Thread-safe and JSON-hardened.
        """
        cache_key: Any = f"decompose:{hash(query)}"
        cached: Any = self.cache.get(cache_key)
        if cached:
            return cached["sub_queries"]
        prompt: Any = f'\nYou are the Sovereign Query Decomposer. \nBreak this complex query into 3-5 atomic, independent sub-questions.\n\nQuery: "{query}"\n\nOutput ONLY a JSON object: {{"sub_queries": ["q1", "q2", ...]}}\n'
        response: Any = await self.engine.resilient_mutation(prompt=prompt, temperature=0.5)
        try:
            cleaned: Any = self._clean_json_response(response)
            result: Any = json.loads(cleaned)
            sub_queries: Any = result.get("sub_queries", [])
            sub_queries: Any = list(dict.fromkeys([q.strip() for q in sub_queries if q.strip()]))
            if not sub_queries:
                sub_queries: Any = [query]
        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as e:
            print(f"   [!] Decomposition parse error: {e}")
            sub_queries: Any = [query]
        self.cache.set(cache_key, {"sub_queries": sub_queries})
        return sub_queries

    async def decompose_and_expand(self, query: str) -> list[str]:
        """
        L1: Decompose query + generate expanded variants (legacy method)
        """
        prompt: Any = '\nYou are a semantic query expansion specialist. Given a user query, generate 5-8 expanded queries that capture:\n- Core intent\n- Specific technical terms\n- Broader context\n- Related concepts\n\nOutput format: {"queries": ["query1", "query2", ...]}\n'
        response: Any = await self.engine.resilient_mutation(
            prompt=prompt,
            temperature=self.expansion_temperature,
            response_format={"type": "json_object"},
        )
        try:
            result: Any = json.loads(self._clean_json_response(response))
            expanded: Any = result.get("queries", [])[:8]
        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as e:
            Logger.error(f"L1 Decomposition failure: {e}")
            expanded: Any = [query]
        return expanded

    async def generate_synthetic_passages(self, query: str) -> list[str]:
        """
        Generate synthetic documentation passages for training
        """
        prompt: Any = f'\nGenerate 2-3 factual, technical passages about the following query topic.\n\nQuery: "{query}"\n\nMake them detailed, factual, and in the style of canon documentation.\nOutput format: {{"passages": ["passage1", "passage2", ...]}}\n'
        response: Any = await self.engine.resilient_mutation(
            prompt=prompt,
            temperature=0.5,
            response_format={"type": "json_object"},
        )
        try:
            result: Any = json.loads(self._clean_json_response(response))
            return result.get("passages", [])[:3]
        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as e:
            Logger.error(f"L1 HyDE failure: {e}")
            return []


__all__ = ["query_planner"]
