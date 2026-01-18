from __future__ import annotations
"""
Sovereign Brave Search MCP Client — L2 Execution Layer
Phase 13F: Full MCP integration via L3 router with unified output formatting
Tool ID Prefix: ACT-001
"""
import logging
import json
from typing import Any, Dict, List, Optional
from agentic_core.config.blueprint_sovereign.sovereign_config_1 import config

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

Logger: Any = logging.getLogger('ActionRegistry.WebSearch')

class WebSearchTools:
    """
    Standardized toolset for external intelligence.
    Routes all traffic through L3 Sovereign Router.
    Tool ID Prefix: ACT-001
    """

    def __init__(self):
        """Initialize with sovereign MCP router — L5 shielded"""
        self.router = SovereignMCPRouter(role='web_research')
        Logger.info('[L2 WEB SEARCH] Initialized with Sovereign MCP Router')

    async def search_web(self, query: str) -> str:
        """
        Sovereign web search via Brave Search MCP.
        Standardizes the output for L1 Cognition processing.

        Args:
            query (str): The search query string.

        Returns:
            str: A formatted string of search results or an error message.
        """
        if not config.BRAVE_SEARCH_MCP_ENABLED:
            return 'Error: Brave Search MCP disabled in sovereign config'
        Logger.info(f"🌐 Sovereign Web Search: '{query}'")
        try:
            result: Any = await self.router.manager.call_tool(tool_name='brave_web_search', args={'query': query, 'count': config.BRAVE_SEARCH_COUNT, 'summarize': config.BRAVE_SEARCH_SUMMARIZE, 'safe_search': config.BRAVE_SEARCH_SAFE_SEARCH, 'country': config.BRAVE_SEARCH_COUNTRY})
            return self._parse_mcp_response(result, 'web')
        except Exception as e:
            Logger.error(f'[L2 WEB SEARCH] MCP call failed: {e}')
            return f'Search Error: {str(e)}'

    async def search_local(self, query: str, location: Optional[str]=None) -> str:
        """
        Geographic/Business search via Brave MCP.

        Args:
            query (str): The local search query string.
            location (str, optional): Geographic location context.

        Returns:
            str: A formatted string of local search results or an error message.
        """
        if not config.BRAVE_SEARCH_MCP_ENABLED:
            return 'Error: Brave Search MCP disabled'
        Logger.info(f"📍 Sovereign Local Search: '{query}' in {location or 'US'}")
        try:
            result: Any = await self.router.manager.call_tool(tool_name='brave_local_search', args={'query': query, 'count': config.BRAVE_SEARCH_COUNT})
            return self._parse_mcp_response(result, 'local')
        except Exception as e:
            Logger.error(f'[L2 LOCAL SEARCH] MCP call failed: {e}')
            return f'Local search error: {str(e)}'

    def _parse_mcp_response(self, result: Any, mode: str) -> str:
        """
        Normalizes MCP output regardless of server return format.

        Args:
            result: The MCP response object
            mode: "web" or "local" for format selection

        Returns:
            str: Formatted search results
        """
        content = ''
        if hasattr(result, 'content') and isinstance(result.content, list):
            content = ''.join([c.text for c in result.content if hasattr(c, 'text')])
        elif isinstance(result, dict) and 'content' in result:
            content = ''.join([c.get('text', '') for c in result['content'] if isinstance(c, dict)])
        else:
            content = str(result)
        try:
            data = json.loads(content)
            if mode == 'web':
                return self._format_web_json(data)
            return self._format_local_json(data)
        except (json.JSONDecodeError, TypeError):
            return content

    def _format_web_json(self, data: Dict) -> str:
        """
        Formats web search results into standardized output.

        Args:
            data: The Brave web search response data

        Returns:
            str: Formatted web search results
        """
        items = data.get('web', {}).get('results', []) or data.get('results', [])
        if not items:
            return 'No web results found.'
        formatted = []
        for i in items:
            title = i.get('title', 'No title')
            summary = i.get('summary') or i.get('description', 'No summary')
            url = i.get('url', '#')
            formatted.append(f'Title: {title}\nSummary: {summary}\nLink: {url}\n---')
        return '\n'.join(formatted)

    def _format_local_json(self, data: Dict) -> str:
        """
        Formats local search results into standardized output.

        Args:
            data: The Brave local search response data

        Returns:
            str: Formatted local search results
        """
        items = data.get('locations', {}).get('results', []) or data.get('results', [])
        if not items:
            return 'No local results found.'
        formatted = []
        for i in items:
            name = i.get('title') or i.get('name', 'Unknown Business')
            address = i.get('address', {}).get('formattedAddress') or i.get('address', 'No address')
            formatted.append(f'Name: {name}\nAddress: {address}\n---')
        return '\n'.join(formatted)
__all__ = ['WebSearchTools']