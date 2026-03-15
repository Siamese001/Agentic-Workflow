from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "web_search_client", "L2")
_emit_routes_through("p1", "web_search_client", "L2")
_emit_escalates_to_human("p1", "web_search_client", "L2")
_emit_reads_policy_state("p1", "web_search_client", "L2")

_emit_applies_guardrail("p0", "web_search_client", "p0_governance")
_emit_snapshots_state("p0", "web_search_client", "state_snapshot")

"\nSovereign Brave Search MCP Client — L2 Execution Layer\nPhase 13F: Full MCP integration via L3 router with unified output formatting\nTool ID Prefix: ACT-001\n"
import json
import logging
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)

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
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "WebSearchTools.search_web")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:WebSearchTools.search_web".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
        # guardian: allow-silent-swallow
        except Exception as e:
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
                tool_name="brave_local_search", args={"query": query, "count": config.BRAVE_SEARCH_COUNT}
            )
            return self._parse_mcp_response(result, "local")
        # guardian: allow-silent-swallow
        except Exception as e:
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
