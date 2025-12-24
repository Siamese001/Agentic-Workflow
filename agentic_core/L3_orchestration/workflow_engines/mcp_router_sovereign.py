"""L3 Orchestration: Sovereign MCP Router — Eternal Integration
Hardened routing of canon violations to MCP tools across all layers and apps.
L5 safety shielded + auto-immune on breach.
"""
import asyncio
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
import json

from agentic_core.L3_orchestration.workflow_engines.mcp_manager import MCPConnectionManager, load_mcp_config
from agentic_core.L5_safety.guardrails.mcp_sovereign import mcp_authority

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

            # [L4 STATE INTEGRATION] Semantic drift -> Memory search
            elif key_id in {21, 13}:  # Semantic memory, Mission history drift
                try:
                    memory_result = await self.manager.call_tool("search_nodes", {
                        "query": f"Canon Key {key_id} healing pattern for {violation_desc}"
                    })
                    return {
                        "status": "l4_memory_recall",
                        "tool": "memory_search",
                        "recall": memory_result,
                        "insight": "Pattern matched against eternal knowledge graph."
                    }
                except Exception as mem_e:
                    logger.warning(f"[L4 MCP] Memory search failed: {mem_e}")

            # [L3 ORCHESTRATION INTEGRATION] State recovery via Redis
            elif key_id == 18:  # Workflow state drift
                redis_result = await self.manager.call_tool("redis_recover", {
                    "key_prefix": "mission:state",
                    "operation": "restore_last_good"
                })
                return {"status": "l3_recovery", "tool": "redis_recover", "restored": redis_result.get("keys_restored", 0)}

            # [L2 DEEPWIKI] Sovereign repository knowledge access
            elif key_id in {40, 41, 42, 49}:
                # Check if we have a DeepWiki client available in the context
                try:
                    from agentic_core.L4_state.P1_core.validation_context import ValidationContext
                    if hasattr(ValidationContext, '_instance') and ValidationContext._instance:
                        ctx = ValidationContext._instance
                        if hasattr(ctx, 'deepwiki_client') and ctx.deepwiki_client:
                            try:
                                answer = await ctx.deepwiki_client.ask_question(
                                    "xai/grok-canon",
                                    f"What are the sovereign requirements for Key {key_id} compliance?"
                                )
                                return {
                                    "status": "l2_deepwiki_qa",
                                    "guidance": answer.get("response", ""),
                                    "insight": "Applied internal repository guidance to healing round."
                                }
                            except Exception as wiki_e:
                                logger.warning(f"[L2 DEEPWIKI] Q&A failed: {wiki_e}")
                except Exception:
                    pass

            # [L2 FIGMA] Design system enforcement
            elif key_id in {42, 49} and "ui" in violation_desc.lower():
                # Check if we have a Figma client available in the context
                try:
                    # Import context to check for figma_client
                    from agentic_core.L4_state.P1_core.validation_context import ValidationContext
                    if hasattr(ValidationContext, '_instance') and ValidationContext._instance:
                        ctx = ValidationContext._instance
                        if hasattr(ctx, 'figma_client') and ctx.figma_client:
                            try:
                                # Try to find matching code for the UI violation
                                tokens = await ctx.figma_client.get_variable_defs("SOVEREIGN_FILE_KEY")
                                return {
                                    "status": "l2_figma_truth",
                                    "tool": "figma_tokens",
                                    "guidance": "Enforce these audited design tokens in the heal.",
                                    "tokens": tokens
                                }
                            except Exception as figma_e:
                                logger.warning(f"[L2 FIGMA] Token extraction failed: {figma_e}")
                except Exception:
                    pass

            # [L1 SEQUENTIAL THINKING OPTIMIZATION] Primary cognitive engine
            # Prioritize atomic reasoning for all core structural/cognitive keys
            if key_id in {40, 41, 42, 49}:  # Gravity, Complexity, Atomicity, Naming
                try:
                    # Check Redis for a successful "thought template" to speed up recall
                    template_key = f"seq_template:key{key_id}"
                    cached_template = None
                    from agentic_core.L5_safety.shield.redis_sovereign_shield import redis_shield
                    
                    try:
                        cached = redis_shield.execute("get", template_key)
                        if cached:
                            cached_template = json.loads(cached)
                            logger.info(f"[L1 CACHE HIT] Using proven template for Key {key_id}")
                    except Exception: pass

                    reasoning_result = await self.manager.call_tool("sequential_thinking", {
                        "task": violation_desc,
                        "goal": f"Resolve Canon Key {key_id} violation atomically",
                        "max_steps": 8,
                        "template": cached_template,
                        "enforce_no_hallucination": True
                    })
                    
                    # Cache the reasoning structure if it produced a viable solution
                    if reasoning_result.get("status") == "success" and not cached_template:
                        try:
                            redis_shield.execute(
                                "set", template_key, 
                                json.dumps(reasoning_result.get("steps", [])), 
                                ex=60*60*24*30 # 30-day template life
                            )
                        except Exception: pass

                    return {
                        "status": "l1_sequential",
                        "tool": "sequential_thinking",
                        "steps": reasoning_result.get("steps", []),
                        "solution": reasoning_result.get("solution"),
                        "cached": cached_template is not None
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

            # [L2 DEEPWIKI INTEGRATION] Sovereign repository knowledge access
            elif key_id in {40, 41, 42, 49}:  # Structural & Cognitive Keys
                try:
                    # 1. Look for the structural map of the wiki
                    structure = await self.manager.call_tool("read_wiki_structure", {
                        "repo": "xai/grok-canon"
                    })
                    
                    # 2. Find a topic that matches our violation or key
                    relevant_topic = next((t for t in structure.get("topics", []) 
                                         if str(key_id) in t or "canon" in t.lower()), None)
                    
                    if relevant_topic:
                        content = await self.manager.call_tool("read_wiki_contents", {
                            "repo": "xai/grok-canon",
                            "topic": relevant_topic
                        })
                        return {
                            "status": "l2_deepwiki_structure",
                            "guidance": content.get("content", ""),
                            "source": relevant_topic
                        }
                    
                    # 3. Fallback: Ask a direct question if no topic matches
                    answer = await self.manager.call_tool("ask_question", {
                        "repo": "xai/grok-canon",
                        "question": f"How should Key {key_id} be resolved per the sovereign canon?"
                    })
                    return {"status": "l2_deepwiki_qa", "answer": answer.get("response", "")}
                except Exception as wiki_e:
                    logger.warning(f"[L2 DEEPWIKI] Wiki access failed: {wiki_e} — falling back to search")
                    # Fallback to Brave Search
                    try:
                        search_result = await self.manager.call_tool("brave_search", {
                            "query": f"python canon key {key_id} compliance best practices {violation_desc}",
                            "count": 3
                        })
                        return {"status": "l2_research", "tool": "brave_search", "results": search_result}
                    except Exception as search_e:
                        logger.error(f"[L2 EXECUTION] Brave search failed: {search_e}")
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
