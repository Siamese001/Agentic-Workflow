"""L3 Orchestration: Sovereign MCP Router — Eternal Integration
Hardened routing of canon violations to MCP tools across all layers and apps.
L5 safety shielded + auto-immune on breach.
"""
import asyncio
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

from agentic_core.L3_orchestration.mcp.mcp_manager import MCPConnectionManager, load_mcp_config
from agentic_core.L5_safety.policy.mcp_sovereign import mcp_authority

logger = logging.getLogger(__name__)

class SovereignMCPRouter:
    """Ultra-hardened L3 MCP switchboard — zero tolerance for failure"""
    
    def __init__(self, role: str = "validator", config_path: str = "config/mcp_mappings.yaml"):
        self.role = role
        self.config_path = Path(config_path)
        self.manager: Optional[MCPConnectionManager] = None
        self.initialized = False

    async def initialize(self):
        """Async initialization with L5 shielding and immediate fail-fast"""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"MCP config missing: {self.config_path}")
            
            config = load_mcp_config(str(self.config_path))
            self.manager = MCPConnectionManager(config)
            
            # Sovereign connection handshake
            await self.manager.connect(self.role)
            
            self.initialized = True
            logger.info(f"[L3 MCP] Sovereign router ARMED for role '{self.role}'")
        except Exception as e:
            logger.critical(f"[L3 MCP BREACH] Initialization failed: {e}")
            mcp_authority.record_breach(str(e))
            raise

    async def resolve_violation(self, key_id: int, file_path: str, violation_desc: str) -> Dict[str, Any]:
        """Route canon key violation to hardened MCP tool — L5 shielded"""
        if not mcp_authority.is_authorized():
            return {"status": "blocked", "reason": "MCP sovereignty compromised"}
        
        if not self.initialized or not self.manager:
            return {"status": "error", "reason": "MCP router not initialized"}
        
        try:
            # [L2 EXECUTION INTEGRATION] Route research violations to L2 tools
            if key_id in {40, 41, 49}:  # Gravity, Atomicity, Naming
                try:
                    search_result = await self.manager.call_tool("brave_search", {
                        "query": f"python canon key {key_id} compliance best practices {violation_desc}",
                        "count": 3
                    })
                    return {"status": "l2_research", "tool": "brave_search", "results": search_result}
                except Exception as search_e:
                    logger.warning(f"[L2 MCP] Brave Search failed: {search_e}")
                    return {"status": "fallback", "reason": str(search_e)}

            # [L4 STATE] Existing L4 tool routing
            elif key_id == 42: # Atomicity -> Trigger Fission
                return await self.manager.call_tool("fission_write", {"monolith_path": file_path, "files": {}})
            
            return {"status": "no_route", "key_id": key_id}
            
        except Exception as e:
            logger.error(f"[MCP FAILURE] Tool call failed for Key {key_id}: {e}")
            mcp_authority.record_breach(str(e))
            return {"status": "error", "exception": str(e)}

    async def cleanup(self):
        """Graceful eternal shutdown"""
        if self.manager:
            await self.manager.cleanup()
            logger.info("[L3 MCP] Sovereign router cleaned — connections severed")
