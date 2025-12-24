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
            # [L5 SAFETY INTEGRATION] Route safety violations to red-team MCP
            if key_id in {19, 50}:  # Safety Guardrail, RedSentinel
                try:
                    redteam_result = await self.manager.call_tool("redteam_simulate", {
                        "target_file": file_path,
                        "violation_type": violation_desc,
                        "attack_vector": "prompt_injection" if "prompt" in violation_desc.lower() else "logic_bypass"
                    })
                    return {
                        "status": "l5_redteam",
                        "tool": "redteam_simulate",
                        "findings": redteam_result.get("vulnerabilities", []),
                        "insight": "L5 shield tested against adversarial simulation"
                    }
                except Exception as red_e:
                    logger.error(f"[L5 MCP] RedTeam simulation failed: {red_e}")

            # [L4 STATE INTEGRATION] Semantic drift -> Pinecone/Memory search
            elif key_id in {21, 13}:  # Semantic memory, Mission history drift
                try:
                    pinecone_result = await self.manager.call_tool("pinecone_search", {
                        "query": violation_desc,
                        "index": "canon-patterns",
                        "top_k": 3
                    })
                    return {
                        "status": "l4_semantic",
                        "tool": "pinecone_search",
                        "matches": pinecone_result.get("matches", []),
                        "insight": "Last known good pattern retrieved from eternal memory"
                    }
                except Exception as pine_e:
                    logger.warning(f"[L4 MCP] Pinecone failed: {pine_e}")

            # [L3 ORCHESTRATION INTEGRATION] State recovery via Redis
            elif key_id == 18:  # Workflow state drift
                redis_result = await self.manager.call_tool("redis_recover", {
                    "key_prefix": "mission:state",
                    "operation": "restore_last_good"
                })
                return {"status": "l3_recovery", "tool": "redis_recover", "restored": redis_result.get("keys_restored", 0)}

            # [L1 COGNITION INTEGRATION] Route reasoning violations to L1 tools
            if key_id in {41, 49}:  # Cognitive Complexity, Naming Signal
                try:
                    # Sequential Thinking MCP for step-by-step breakdown
                    reasoning_result = await self.manager.call_tool("sequential_thinking", {
                        "task": violation_desc,
                        "goal": f"Break down Key {key_id} violation into atomic reasoning steps",
                        "max_steps": 5
                    })
                    return {
                        "status": "l1_reasoning",
                        "tool": "sequential_thinking",
                        "steps": reasoning_result,
                        "insight": "Cognitive breakdown complete — feed to healer"
                    }
                except Exception as reasoning_e:
                    logger.warning(f"[L1 MCP] Sequential thinking failed: {reasoning_e}")
                    # Fallback to direct Gemini policy guidance
                    policy_result = await self.manager.call_tool("gemini_policy_enforcer", {
                        "key_id": key_id, "violation": violation_desc, "file_context": file_path
                    })
                    return {"status": "l1_policy", "tool": "gemini_policy_enforcer", "guidance": policy_result}

            # [L0 MAINTENANCE INTEGRATION] Route hygiene/diagnostic violations to L0 tools
            elif key_id in {20, 21}:  # Support layers, Execution/Pattern hygiene
                try:
                    # L0 cleanup tool — prune dead scripts/logs
                    cleanup_result = await self.manager.call_tool("l0_cleanup", {
                        "target": "L0_maintenance/scripts",
                        "patterns": ["*_old.py", "temp_*.py", "backup_*.py"]
                    })
                    return {
                        "status": "l0_cleanup",
                        "tool": "l0_cleanup",
                        "pruned": cleanup_result.get("pruned_files", []),
                        "insight": "L0 hygiene restored via automated pruning"
                    }
                except Exception as cleanup_e:
                    logger.warning(f"[L0 MCP] Cleanup failed: {cleanup_e} — falling back to diagnostics")
                    diag_result = await self.manager.call_tool("l0_diagnostics", {"scope": "repository"})
                    return {"status": "l0_diagnostics", "tool": "l0_diagnostics", "report": diag_result}

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
