"""
MCP Router - L3 Orchestration Switchboard

Routes layer-specific failures to appropriate MCPs for resolution.
Prevents L1 Cognition from wasting reasoning tokens on tasks that
specialized tools can solve instantly.

MCP Assignment by Layer:
- L5 Safety: Sequential Thinking, GitKraken
- L4 State: Pinecone, Memory, Filesystem
- L3 Orchestration: Redis, Fetch, Playwright
- L2 Execution: Brave Search, DeepWiki
- L1 Cognition: Gemini/Claude (Core)
"""
import logging
from typing import Any, Dict, List, Optional, Protocol

logger = logging.getLogger(__name__)


class MCPRouter:
    """
    L3 Orchestration switchboard: Hardens the L1-L5 stack by routing
    specific layer failures to the appropriate installed MCP.
    
    Strategy:
    - L1 failures → Sequential Thinking for reasoning breakdown
    - L2 failures → Brave Search for documentation/fixes
    - L3 failures → Redis for state recovery
    - L4 failures → Pinecone for structural patterns
    - L5 failures → GitKraken for version control verification
    """
    
    def __init__(self, tui_handle=None):
        """
        Initialize MCP Router.
        
        Args:
            tui_handle: Optional TUI dashboard for status updates
        """
        self.tui = tui_handle
        
        # MCP Registry by Layer
        self.registry = {
            "L1": ["sequential_thinking"],
            "L2": ["brave_search", "deepwiki", "fetch"],
            "L3": ["redis", "playwright"],
            "L4": ["pinecone", "memory", "filesystem"],
            "L5": ["sequential_thinking", "gitkraken"]
        }
        
        logger.info("[OK] MCP Router initialized with L1-L5 registry")
    
    async def resolve_failure(self, layer: str, error_context: str) -> Dict[str, Any]:
        """
        Hardens the implementation by selecting the best tool for the layer.
        
        Args:
            layer: Layer identifier (L1-L5)
            error_context: Error description or context
            
        Returns:
            Resolution result from MCP
        """
        logger.info(f"🔀 MCP Router: Resolving {layer} failure")
        
        if layer == "L1":
            # Logic Loop: Use Sequential Thinking to break down reasoning
            logger.info(f"   → Routing to Sequential Thinking for reasoning breakdown")
            return await self.call_mcp("sequential_thinking", {
                "query": error_context,
                "purpose": "Break down complex reasoning into atomic steps"
            })
        
        if layer == "L2":
            # Execution/Syntax Error: Search for documentation or fixes
            logger.info(f"   → Routing to Brave Search for documentation")
            return await self.call_mcp("brave_search", {
                "query": f"python fix {error_context}",
                "purpose": "Find documentation or fixes for syntax errors"
            })
        
        if layer == "L3":
            # Orchestration State: Use Redis for state recovery
            logger.info(f"   → Routing to Redis for state recovery")
            return await self.call_mcp("redis", {
                "action": "get",
                "key": f"state:{error_context}",
                "purpose": "Recover orchestration state"
            })
        
        if layer == "L4":
            # State Desync: Use Pinecone to find last known good pattern
            logger.info(f"   → Routing to Pinecone for structural patterns")
            return await self.call_mcp("pinecone", {
                "query": error_context,
                "top_k": 1,
                "purpose": "Find last known good structural pattern"
            })
        
        if layer == "L5":
            # Safety Block: Use GitKraken to verify history
            logger.info(f"   → Routing to GitKraken for version control verification")
            return await self.call_mcp("gitkraken", {
                "action": "status",
                "file": error_context,
                "purpose": "Verify git history before override"
            })
        
        logger.warning(f"   [!]  Unknown layer: {layer}")
        return {"status": "error", "message": f"Unknown layer: {layer}"}
    
    async def call_mcp(self, mcp_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interface with specific MCP server.
        
        Args:
            mcp_name: Name of MCP to invoke
            params: Parameters for MCP call
            
        Returns:
            MCP response
        """
        if self.tui:
            self.tui.update_state(
                file="MCP_ROUTER",
                key="ROUTING",
                round_num=0,
                tokens=0,
                log_msg=f"📡 Invoking {mcp_name}..."
            )
        
        logger.info(f"   📡 Calling MCP: {mcp_name}")
        logger.debug(f"      Parameters: {params}")
        
        # MCP interface logic would go here
        # For now, return mock response
        return {
            "status": "success",
            "mcp": mcp_name,
            "params": params,
            "result": f"Mock response from {mcp_name}"
        }
    
    def get_available_mcps(self, layer: Optional[str] = None) -> Dict[str, list]:
        """
        Get available MCPs for a layer or all layers.
        
        Args:
            layer: Optional layer identifier
            
        Returns:
            Dictionary of layer -> MCP list
        """
        if layer:
            return {layer: self.registry.get(layer, [])}
        return self.registry
    
    async def health_check(self) -> Dict[str, bool]:
        """
        Check health of all registered MCPs.
        
        Returns:
            Dictionary of MCP -> health status
        """
        health = {}
        
        for layer, mcps in self.registry.items():
            for mcp in mcps:
                try:
                    # Attempt to call MCP with health check
                    result = await self.call_mcp(mcp, {"action": "health_check"})
                    health[mcp] = result.get("status") == "success"
                except Exception as e:
                    logger.warning(f"   [!]  MCP {mcp} health check failed: {e}")
                    health[mcp] = False
        
        return health


def get_mcp_router(tui_handle=None) -> MCPRouter:
    """
    Factory function to create MCPRouter instance.
    
    Args:
        tui_handle: Optional TUI dashboard handle
        
    Returns:
        MCPRouter instance
    """
    return MCPRouter(tui_handle=tui_handle)
