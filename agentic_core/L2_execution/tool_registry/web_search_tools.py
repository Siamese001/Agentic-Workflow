"""
Web Search Tools - Atomic Module
Extracted from action_registry.py via Atomic Fission Protocol
Tool ID Prefix: ACT-001

Phase 14: Refactored to use Brave Search MCP via L3 Sovereign Router
"""
import logging
import json
from typing import Any, Dict, List, Optional
from agentic_core.L3_orchestration.workflow_engines.mcp_router_sovereign import SovereignMCPRouter
from agentic_core.config.blueprint_sovereign.environments.sovereign_config import config

logger = logging.getLogger("ActionRegistry.WebSearch")


class WebSearchTools:
    """
    Sovereign Brave Search MCP Client — L2 Execution Layer
    Phase 14: Full MCP integration via L3 router
    Tool ID Prefix: ACT-001
    """

    def __init__(self):
        """Initialize with sovereign MCP router — L5 shielded"""
        # Role 'web_research' maps to the Brave MCP server in the router config
        self.router = SovereignMCPRouter(role="web_research")
        logger.info("[L2 WEB SEARCH] Initialized with Sovereign MCP Router")

    async def search_web(self, query: str) -> str:
        """
        Sovereign web search via Brave Search MCP
        L5 shielded, L6 observable
        Tool ID: ACT-001

        Args:
            query (str): The search query string.

        Returns:
            str: A formatted string of search results or an error message.
        """
        if not config.BRAVE_SEARCH_MCP_ENABLED:
            return "Error: Brave Search MCP disabled in sovereign config"
        
        logger.info(f"🌐 Sovereign Web Search: '{query}'")
        
        try:
            # L3 → L2 MCP call with L5 shielding
            # Note: Official Brave MCP usually exposes 'mcp1_brave_web_search'
            result = await self.router.manager.call_tool(
                tool_name="mcp1_brave_web_search",
                args={
                    "query": query,
                    "count": config.BRAVE_SEARCH_COUNT,
                    "offset": 0
                }
            )
            
            return self._parse_mcp_response(result)
        
        except Exception as e:
            logger.error(f"[L2 WEB SEARCH] MCP call failed: {e}")
            return f"Search Error: {str(e)}"

    async def search_local(self, query: str) -> str:
        """
        Local business search via Brave MCP
        Useful for finding physical locations/businesses

        Args:
            query (str): The local search query string.

        Returns:
            str: A formatted string of local search results or an error message.
        """
        if not config.BRAVE_SEARCH_MCP_ENABLED:
            return "Error: Brave Search MCP disabled."

        logger.info(f"📍 Sovereign Local Search: '{query}'")

        try:
            result = await self.router.manager.call_tool(
                tool_name="mcp1_brave_local_search",
                args={
                    "query": query,
                    "count": 5  # Local results are usually denser
                }
            )
            return self._parse_mcp_response(result)
        
        except Exception as e:
            logger.error(f"[L2 LOCAL SEARCH] MCP call failed: {e}")
            return f"Local Search Error: {str(e)}"

    def _parse_mcp_response(self, result: Any) -> str:
        """
        Robustly parses MCP results which might be:
        1. A dict with 'content' list (standard MCP)
        2. A raw dict from a wrapped tool
        3. Stringified JSON

        Args:
            result: The MCP response object

        Returns:
            str: Formatted search results
        """
        try:
            # Case 1: Standard MCP response structure (list of Content objects)
            content_blocks = []
            if isinstance(result, dict) and "content" in result:
                content_blocks = result["content"]
            elif hasattr(result, "content"):
                content_blocks = result.content
            
            # If we found content blocks, process them
            if content_blocks:
                text_content = ""
                for block in content_blocks:
                    # Handle both object attributes and dict keys
                    if hasattr(block, "text"):
                        text_content += block.text
                    elif isinstance(block, dict) and "text" in block:
                        text_content += block["text"]
                
                # If the text is JSON, try to format it nicely
                try:
                    data = json.loads(text_content)
                    return self._format_brave_json(data)
                except json.JSONDecodeError:
                    return text_content  # Return raw text if not JSON

            # Case 2: Direct Dict (legacy or simplified wrapper)
            if isinstance(result, dict):
                return self._format_brave_json(result)

            return str(result)

        except Exception as e:
            logger.error(f"Error parsing search results: {e}")
            return "Error parsing search results."

    def _format_brave_json(self, data: Dict) -> str:
        """
        Formats Brave JSON data into readable string

        Args:
            data: The Brave search response data

        Returns:
            str: Formatted search results
        """
        output = []
        
        # Web results
        if "web" in data and "results" in data["web"]:
            for item in data["web"]["results"]:
                title = item.get('title', 'No Title')
                desc = item.get('description', 'No description')
                url = item.get('url', '#')
                output.append(f"**{title}**\n{desc}\nSource: {url}")
        
        # Local results
        elif "locations" in data and "results" in data["locations"]:
            for item in data["locations"]["results"]:
                title = item.get('title', 'No Title')
                address = item.get('address', {}).get('formattedAddress', 'No Address')
                rating = item.get('rating', {}).get('ratingValue', 'N/A')
                output.append(f"**{title}** (Rating: {rating})\nAddress: {address}")
        
        # Fallback for generic results
        elif isinstance(data, list):
            for item in data:
                output.append(str(item))
        else:
            # Last ditch dump
            return json.dumps(data, indent=2)

        if not output:
            return "No relevant results found."
            
        return "\n\n---\n\n".join(output)


__all__ = ['WebSearchTools']
