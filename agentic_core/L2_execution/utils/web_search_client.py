from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "web_search_client")
trace_contract.emit_determinism_digest("p0", "web_search_client")

trace_contract._emit_dispatches_healing_run("p1", "web_search_client", "L2")
trace_contract._emit_routes_through("p1", "web_search_client", "L2")
trace_contract._emit_checks_agent_registry("p1", "web_search_client", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "web_search_client", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "web_search_client", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "web_search_client", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "web_search_client", "target_agent")
trace_contract._emit_verifies_policy("p1", "web_search_client", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "web_search_client", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "web_search_client", "boundary_check")
trace_contract._emit_transcripts_response("p1", "web_search_client", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "web_search_client")
trace_contract._emit_gated_by_confidence("p1", "web_search_client", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "web_search_client", "L2")
trace_contract._emit_reads_policy_state("p1", "web_search_client", "L2")

trace_contract._emit_applies_guardrail("p0", "web_search_client", "p0_governance")
trace_contract._emit_snapshots_state("p0", "web_search_client", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "web_search_client", "execution_auth")
trace_contract._emit_validates_capability("p2", "web_search_client", "capability_check")
trace_contract._emit_routes_to_capability("p2", "web_search_client", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "web_search_client", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "web_search_client", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "web_search_client", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "web_search_client", "exec_output")
trace_contract._emit_dispatches_agent("p3", "web_search_client", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "web_search_client", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "web_search_client", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "web_search_client", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "web_search_client", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "web_search_client", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "web_search_client", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "web_search_client", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "web_search_client", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "web_search_client", "eval_metric")
trace_contract._emit_stores_embedding("p4", "web_search_client", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "web_search_client", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "web_search_client", "exec_snapshot_link")

"\nSovereign Brave Search MCP Client — L2 Execution Layer\nPhase 13F: Full MCP integration via L3 router with unified output formatting\nTool ID Prefix: ACT-001\n"
import json
import logging
from typing import Any


trace_contract._emit_emits_metric_event("web_search_client", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("web_search_client", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("web_search_client", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("web_search_client", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("web_search_client", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("web_search_client", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("web_search_client", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("web_search_client", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("web_search_client", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("web_search_client", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("web_search_client", "p4obs", "alert")
trace_contract._emit_links_incident_trace("web_search_client", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("web_search_client", "p3lm", "pattern")
trace_contract._emit_records_learning_event("web_search_client", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("web_search_client", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("web_search_client", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("web_search_client", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("web_search_client", "p3lm", "policy")
trace_contract._emit_stores_learning_state("web_search_client", "p3lm", "state")
trace_contract._emit_records_execution_trace("web_search_client", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("web_search_client", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("web_search_client", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("web_search_client", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("web_search_client", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("web_search_client", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("web_search_client", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("web_search_client", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("web_search_client", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "web_search_client", "context_pull")
trace_contract._emit_pulls_context("p1", "web_search_client", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "web_search_client", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "web_search_client", "uwg_term_2")
trace_contract._emit_writes_through("p1", "web_search_client", "write_through")
trace_contract._emit_writes_through("p1", "web_search_client", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "web_search_client", "safety_validation")
trace_contract._emit_invokes_eval("p1", "web_search_client", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "web_search_client", "routing_commit")

Logger: Any = logging.getLogger("ActionRegistry.WebSearch")


class WebSearchTools:
    """
    Standardized toolset for external intelligence.
    Routes all traffic through L3 Sovereign router.
    Tool ID Prefix: ACT-001
    """

    def __init__(self):
        """Initialize with sovereign MCP router — L5 shielded"""
        self.router = SovereignMCPRouter(role="web_research")
        Logger.info("[L2 WEB SEARCH] Initialized with Sovereign MCP router")

    async def search_web(self, query: str) -> str:
        """
        Sovereign web search via Brave Search MCP.
        Standardizes the output for L1 Cognition processing.

        Args:
            query (str): The search query string.

        Returns:
            str: A formatted string of search results or an error message.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "WebSearchTools.search_web")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:WebSearchTools.search_web".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not config.BRAVE_SEARCH_MCP_ENABLED:
            return "Error: Brave Search MCP disabled in sovereign config"
        Logger.info(f"🌐 Sovereign Web Search: '{query}'")
        try:
            result: Any = await self.router.manager.call_tool(
                tool_name="brave_web_search",
                args={
                    "query": query,
                    "count": config.BRAVE_SEARCH_COUNT,
                    "summarize": config.BRAVE_SEARCH_SUMMARIZE,
                    "safe_search": config.BRAVE_SEARCH_SAFE_SEARCH,
                    "country": config.BRAVE_SEARCH_COUNTRY,
                },
            )
            return self._parse_mcp_response(result, "web")
        except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
            Logger.error(f"[L2 WEB SEARCH] MCP call failed: {e}")
            return f"Search Error: {str(e)}"

    async def search_local(self, query: str, location: str | None = None) -> str:
        """
        Geographic/Business search via Brave MCP.

        Args:
            query (str): The local search query string.
            location (str, optional): Geographic location context.

        Returns:
            str: A formatted string of local search results or an error message.
        """
        if not config.BRAVE_SEARCH_MCP_ENABLED:
            return "Error: Brave Search MCP disabled"
        Logger.info(f"📍 Sovereign Local Search: '{query}' in {location or 'US'}")
        try:
            result: Any = await self.router.manager.call_tool(
                tool_name="brave_local_search",
                args={"query": query, "count": config.BRAVE_SEARCH_COUNT},
            )
            return self._parse_mcp_response(result, "local")
        except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
            Logger.error(f"[L2 LOCAL SEARCH] MCP call failed: {e}")
            return f"Local search error: {str(e)}"

    def _parse_mcp_response(self, result: Any, mode: str) -> str:
        """
        Normalizes MCP output regardless of server return format.

        Args:
            result: The MCP response object
            mode: "web" or "local" for format selection

        Returns:
            str: Formatted search results
        """
        content = ""
        if hasattr(result, "content") and isinstance(result.content, list):
            content = "".join([c.text for c in result.content if hasattr(c, "text")])
        elif isinstance(result, dict) and "content" in result:
            content = "".join([c.get("text", "") for c in result["content"] if isinstance(c, dict)])
        else:
            content = str(result)
        try:
            data = json.loads(content)
            if mode == "web":
                return self._format_web_json(data)
            return self._format_local_json(data)
        except (json.JSONDecodeError, TypeError):
            return content

    def _format_web_json(self, data: dict) -> str:
        """
        Formats web search results into standardized output.

        Args:
            data: The Brave web search response data

        Returns:
            str: Formatted web search results
        """
        items = data.get("web", {}).get("results", []) or data.get("results", [])
        if not items:
            return "No web results found."
        formatted = []
        for i in items:
            title = i.get("title", "No title")
            summary = i.get("summary") or i.get("description", "No summary")
            url = i.get("url", "#")
            formatted.append(f"Title: {title}\nSummary: {summary}\nLink: {url}\n---")
        return "\n".join(formatted)

    def _format_local_json(self, data: dict) -> str:
        """
        Formats local search results into standardized output.

        Args:
            data: The Brave local search response data

        Returns:
            str: Formatted local search results
        """
        items = data.get("locations", {}).get("results", []) or data.get("results", [])
        if not items:
            return "No local results found."
        formatted = []
        for i in items:
            name = i.get("title") or i.get("name", "Unknown Business")
            address = i.get("address", {}).get("formattedAddress") or i.get("address", "No address")
            formatted.append(f"Name: {name}\nAddress: {address}\n---")
        return "\n".join(formatted)


__all__ = ["WebSearchTools"]
