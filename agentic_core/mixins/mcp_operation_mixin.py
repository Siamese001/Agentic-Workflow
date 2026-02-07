"""
MCPOperationMixin - Unified MCP Access for Agents

[PHASE 3 MIGRATION] Provides single interface to all MCP operations.
"""


class MCPOperationMixin:
    """
    Mixin providing unified MCP gateway access.

    [PHASE 3 MIGRATION] Replaces individual client imports.

    Usage:
        class MyAgent(MCPOperationMixin, SovereignBaseAgent):
            async def process(self):
                result = await self.mcp_llm_route("prompt")
    """

    _mcp_gateway = None

    @property
    def mcp_gateway(self):
        """Lazy-load MCP gateway singleton."""
        if self._mcp_gateway is None:
            from agentic_core.L2_execution.enforcement.SovereignMCPGateway import get_mcp_gateway

            self._mcp_gateway = get_mcp_gateway()
        return self._mcp_gateway

    async def mcp_llm_route(self, prompt: str, **kwargs) -> dict:
        """Route LLM request through MCP gateway."""
        return await self.mcp_gateway.llm_route(prompt, **kwargs)

    async def mcp_kg_query(self, query: str, **kwargs) -> dict:
        """Query knowledge graph through MCP gateway."""
        return await self.mcp_gateway.kg_query(query, **kwargs)

    async def mcp_archive_op(self, operation: str, **kwargs) -> dict:
        """Execute archive operation through MCP gateway."""
        return await self.mcp_gateway.archive_operation(operation, **kwargs)
