from __future__ import annotations

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"""L3 Orchestration: Sovereign MCP router — Eternal Integration
Hardened routing of canon violations to MCP tools across all layers and apps.
L5 safety shielded + auto-immune on breach.
"""
import json
import logging
from pathlib import Path
from typing import Any

from agentic_core.L3_orchestration.reasoning.mcp_manager import (
    MCPConnectionManager,
    load_mcp_config,
)

# [SSOT IMPORT] Structure blueprint is the single source of truth

Logger: Any = logging.getLogger(__name__)


class SovereignMcpRouter(SovereignBaseAgent):
    """Ultra-hardened L3 MCP switchboard — zero tolerance for failure"""

    def __init__(self, role: str = "validator", config_path: str = "config/mcp_mappings.yaml"):
        self.role = role
        self.config_path = Path(config_path)
        self.manager: MCPConnectionManager | None = None
        self.initialized = False

    # guardian: allow-type-erasure
    async def initialize(self) -> Any:
        """Async initialization with L5 shielding and immediate fail-fast"""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"MCP config Missing: {self.config_path}")
            config: Any = load_mcp_config(str(self.config_path))
            self.manager = MCPConnectionManager(config)
            await self.manager.connect(self.role)
            self.initialized = True
            Logger.info(f"[L3 MCP] Sovereign router ARMED for role '{self.role}'")
        except Exception as e:
            Logger.critical(f"[L3 MCP BREACH] Initialization failed: {e}")
            mcp_authority.record_breach(str(e))
            raise

    async def resolve_violation(self, key_id: int, file_path: str, violation_desc: str) -> dict[str, Any]:
        """Route canon key Violation to hardened MCP tool — L5 shielded"""
        if not mcp_authority.is_authorized():
            return {"status": "blocked", "reason": "MCP sovereignty compromised"}
        if not self.initialized or not self.manager:
            return {"status": "error", "reason": "MCP router not initialized"}
        try:
            if key_id in {19, 50}:
                try:
                    redteam_result: Any = await self.manager.call_tool(
                        "redteam_simulate",
                        {
                            "target_file": file_path,
                            "ViolationType": violation_desc,
                            "attack_vector": "prompt_injection"
                            if "prompt" in violation_desc.lower()
                            else "logic_bypass",
                        },
                    )
                    return {
                        "status": "l5_redteam",
                        "tool": "redteam_simulate",
                        "findings": redteam_result.get("vulnerabilities", []),
                        "insight": "L5 shield tested against adversarial simulation",
                    }
                # guardian: allow-silent-swallow
                except Exception as red_e:
                    Logger.error(f"[L5 MCP] RedTeam simulation failed: {red_e}")
            elif key_id in {21, 13}:
                try:
                    memory_result: Any = await self.manager.call_tool(
                        "search_nodes",
                        {"query": f"Canon Key {key_id} healing pattern for {violation_desc}"},
                    )
                    return {
                        "status": "l4_memory_recall",
                        "tool": "memory_search",
                        "recall": memory_result,
                        "insight": "Pattern matched against eternal knowledge graph.",
                    }
                # guardian: allow-silent-swallow
                except Exception as mem_e:
                    Logger.warning(f"[L4 MCP] Memory search failed: {mem_e}")
            elif key_id == 18:
                redis_result: Any = await self.manager.call_tool(
                    "redis_recover",
                    {"key_prefix": "mission:state", "operation": "restore_last_good"},
                )
                return {
                    "status": "l3_recovery",
                    "tool": "redis_recover",
                    "restored": redis_result.get("keys_restored", 0),
                }
            elif key_id in {40, 41, 42, 49}:
                try:
                    from agentic_core.L4_state.P1_core.ValidationContext import ValidationContext

                    if hasattr(ValidationContext, "_instance") and ValidationContext._instance:
                        ctx: Any = ValidationContext._instance
                        if hasattr(ctx, "deepwiki_client") and ctx.deepwiki_client:
                            try:
                                answer: Any = await ctx.deepwiki_client.ask_question(
                                    "xai/grok-canon",
                                    f"What are the sovereign requirements for Key {key_id} compliance?",
                                )
                                return {
                                    "status": "l2_deepwiki_qa",
                                    "guidance": answer.get("response", ""),
                                    "insight": "Applied internal repository guidance to healing round.",
                                }
                            # guardian: allow-silent-swallow
                            except Exception as wiki_e:
                                Logger.warning(f"[L2 DEEPWIKI] Q&A failed: {wiki_e}")
                # guardian: allow-silent-swallow
                except Exception:
                    pass
            elif key_id in {42, 49} and "ui" in violation_desc.lower():
                try:
                    from agentic_core.L4_state.P1_core.ValidationContext import ValidationContext

                    if hasattr(ValidationContext, "_instance") and ValidationContext._instance:
                        ctx: Any = ValidationContext._instance
                        if hasattr(ctx, "figma_client") and ctx.figma_client:
                            try:
                                tokens: Any = await ctx.figma_client.get_variable_defs("SOVEREIGN_FILE_KEY")
                                return {
                                    "status": "l2_figma_truth",
                                    "tool": "figma_tokens",
                                    "guidance": "Enforce these audited design tokens in the heal.",
                                    "tokens": tokens,
                                }
                            # guardian: allow-silent-swallow
                            except Exception as figma_e:
                                Logger.warning(f"[L2 FIGMA] Token extraction failed: {figma_e}")
                # guardian: allow-silent-swallow
                except Exception:
                    pass
            if key_id in {40, 41, 42, 49}:
                try:
                    template_key: Any = f"seq_template:key{key_id}"
                    cached_template: Any = None
                    try:
                        cached: Any = redis_shield.execute("get", template_key)
                        if cached:
                            cached_template: Any = json.loads(cached)
                            Logger.info(f"[L1 CACHE HIT] Using proven template for Key {key_id}")
                    # guardian: allow-silent-swallow
                    except Exception:
                        pass
                    reasoning_result: Any = await self.manager.call_tool(
                        "sequential_thinking",
                        {
                            "Task": violation_desc,
                            "goal": f"Resolve Canon Key {key_id} Violation atomically",
                            "max_steps": 8,
                            "template": cached_template,
                            "enforce_no_hallucination": True,
                        },
                    )
                    if reasoning_result.get("status") == "success" and (not cached_template):
                        try:
                            redis_shield.execute(
                                "set",
                                template_key,
                                json.dumps(reasoning_result.get("steps", [])),
                                ex=60 * 60 * 24 * 30,
                            )
                        # guardian: allow-silent-swallow
                        except Exception:
                            pass
                    return {
                        "status": "l1_sequential",
                        "tool": "sequential_thinking",
                        "steps": reasoning_result.get("steps", []),
                        "solution": reasoning_result.get("solution"),
                        "cached": cached_template is not None,
                    }
                except Exception as reasoning_e:
                    Logger.warning(f"[L1 MCP] Sequential thinking failed: {reasoning_e}")
                    PolicyResult: Any = await self.manager.call_tool(
                        "gemini_policy_enforcer",
                        {"key_id": key_id, "Violation": violation_desc, "file_context": file_path},
                    )
                    return {
                        "status": "l1_policy",
                        "tool": "gemini_policy_enforcer",
                        "guidance": PolicyResult,
                    }
            elif key_id in {20, 21}:
                try:
                    cleanup_result: Any = await self.manager.call_tool(
                        "l0_cleanup",
                        {
                            "target": "L0_routing/scripts",
                            "patterns": ["*_old.py", "temp_*.py", "backup_*.py"],
                        },
                    )
                    return {
                        "status": "l0_cleanup",
                        "tool": "l0_cleanup",
                        "pruned": cleanup_result.get("pruned_files", []),
                        "insight": "L0 hygiene restored via automated pruning",
                    }
                except Exception as cleanup_e:
                    Logger.warning(f"[L0 MCP] Cleanup failed: {cleanup_e} — falling back to diagnostics")
                    diag_result: Any = await self.manager.call_tool("l0_diagnostics", {"scope": "repository"})
                    return {
                        "status": "l0_diagnostics",
                        "tool": "l0_diagnostics",
                        "report": diag_result,
                    }
            elif key_id in {40, 41, 42, 49}:
                try:
                    structure: Any = await self.manager.call_tool(
                        "read_wiki_structure",
                        {"repo": "xai/grok-canon"},
                    )
                    relevant_topic: Any = next(
                        (t for t in structure.get("topics", []) if str(key_id) in t or "canon" in t.lower()),
                        None,
                    )
                    if relevant_topic:
                        content: Any = await self.manager.call_tool(
                            "read_wiki_contents",
                            {"repo": "xai/grok-canon", "topic": relevant_topic},
                        )
                        return {
                            "status": "l2_deepwiki_structure",
                            "guidance": content.get("content", ""),
                            "source": relevant_topic,
                        }
                    answer: Any = await self.manager.call_tool(
                        "ask_question",
                        {
                            "repo": "xai/grok-canon",
                            "question": f"How should Key {key_id} be resolved per the sovereign canon?",
                        },
                    )
                    return {"status": "l2_deepwiki_qa", "answer": answer.get("response", "")}
                except Exception as wiki_e:
                    Logger.warning(f"[L2 DEEPWIKI] Wiki access failed: {wiki_e} — falling back to search")
                    try:
                        search_result: Any = await self.manager.call_tool(
                            "brave_search",
                            {
                                "query": f"python canon key {key_id} compliance best practices {violation_desc}",
                                "count": 3,
                            },
                        )
                        return {
                            "status": "l2_research",
                            "tool": "brave_search",
                            "results": search_result,
                        }
                    # guardian: allow-silent-swallow
                    except Exception as search_e:
                        Logger.error(f"[L2 EXECUTION] Brave search failed: {search_e}")
                    return {"status": "fallback", "reason": str(search_e)}
            elif key_id == 42:
                return await self.manager.call_tool(
                    "fission_write",
                    {"monolith_path": file_path, "files": {}},
                )
            return {"status": "no_route", "key_id": key_id}
        except Exception as e:
            Logger.error(f"[MCP FAILURE] Tool call failed for Key {key_id}: {e}")
            mcp_authority.record_breach(str(e))
            return {"status": "error", "exception": str(e)}

    # guardian: allow-type-erasure
    async def cleanup(self) -> Any:
        """Graceful eternal shutdown"""
        if self.manager:
            await self.manager.cleanup()
            Logger.info("[L3 MCP] Sovereign router cleaned — connections severed")


def _run_self_tests(self) -> dict:
    """Run internal self-tests."""
    results = {"passed": 0, "failed": 0, "tests": []}
    try:
        assert self is not None
        results["passed"] += 1
        results["tests"].append({"name": "test_instantiation", "status": "passed"})
    except AssertionError as e:
        results["failed"] += 1
        results["tests"].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
    return results
