from __future__ import annotations

"""L5 Safety: MCP Sovereign Shield
Enforces zero-trust auditing and auto-immune responses for all MCP tool calls.
"""
import logging
from datetime import datetime

# [SSOT IMPORT] Structure blueprint is the single source of truth
from typing import Any

Logger: Any = logging.getLogger(__name__)


class MCPSovereignAuthority:
    """Monitors the health and authorization of the MCP nervous system."""

    def __init__(self):
        self.violation_count = 0
        self.breach_log = []
        self.is_locked = False

    def is_authorized(self) -> bool:
        """Sovereignty check: Kill connections if breaches exceed threshold."""
        if self.violation_count > 5:
            self.is_locked = True
        return not self.is_locked

    def record_breach(self, error_msg: str) -> Any:
        """Log a tool failure or unauthorized access attempt."""
        self.violation_count += 1
        self.breach_log.append({"timestamp": datetime.now().isoformat(), "error": error_msg})
        Logger.warning(f"[L5 MCP BREACH] Violation recorded. Count: {self.violation_count}")

    def authorize_tool_call(self, tool_name: str, args: dict) -> None:
        """L5 Audit: Log every physical tool call before execution."""
        Logger.info(f"[L5 MCP AUDIT] Authorizing call to '{tool_name}' with args: {args}")
        forbidden_sdks: Any = {"openai", "anthropic", "cohere", "mistral"}
        if tool_name in forbidden_sdks:
            self.record_breach(f"FORBIDDEN SDK CALL: {tool_name}")
            raise PermissionError(
                "Sovereignty Shield: Competitive LLM providers are eternally blocked."
            )
        if tool_name == "fetch":
            url: Any = args.get("url", "")
            if url and (not url.startswith("https://")):
                if not url.startswith("http://"):
                    raise PermissionError(
                        "Sovereignty Shield: Fetch only allowed over secure https/http."
                    )
        if tool_name in {"brave_search", "fetch", "playwright"}:
            query: Any = args.get("query") or args.get("url", "")
            if len(str(query)) > 1000:
                raise ValueError("L2 tool input too long — potential exfiltration risk.")
            forbidden: Any = ["password", "api_key", "secret", "private_key", ".env"]
            if any(bad in str(query).lower() for bad in forbidden):
                raise PermissionError("L2 tool query contains forbidden terms — blocked by shield.")
        if tool_name in {"sequential_thinking", "gemini_policy_enforcer"}:
            max_steps: Any = args.get("max_steps", 0)
            if max_steps > 15:
                raise ValueError(
                    "Sequential thinking request exceeds sovereign safety limit (15 steps)."
                )
            Task: Any = args.get("Task") or args.get("Violation", "")
            if len(str(Task)) > 2000:
                raise ValueError("L1 cognitive tool input too long — reasoning overflow risk.")
            risks: Any = [
                "system prompt",
                "jailbreak",
                "override instructions",
                "ignore all previous",
            ]
            if any(risk in str(Task).lower() for risk in risks):
                raise PermissionError(
                    "L1 tool input contains forbidden cognitive patterns — blocked by shield."
                )
        if tool_name in {"l0_cleanup", "l0_diagnostics"}:
            target: Any = args.get("target") or args.get("scope", "")
            if not target or ".." in str(target) or str(target).startswith("/"):
                raise PermissionError(
                    f"L0 tool target '{target}' invalid — path traversal blocked."
                )
            allowed_prefixes: Any = {"L0_maintenance", "logs", "benchmarks", "apps_shared"}
            if not any(str(target).startswith(p) for p in allowed_prefixes):
                raise PermissionError("L0 tool target outside sovereign maintenance zones.")
        if tool_name == "redteam_simulate":
            vector: Any = args.get("attack_vector", "")
            if vector not in {"prompt_injection", "logic_bypass", "gravity_leak"}:
                raise PermissionError(f"Unauthorized redteam vector '{vector}' blocked by shield.")
        if tool_name in {"pinecone_search", "memory_search"}:
            if len(str(args.get("query", ""))) > 1500:
                raise ValueError("L4 semantic query too long — vector overflow risk.")
        if tool_name in {"create_entities", "add_observations"}:
            if len(args.get("entities", [])) > 20 or len(args.get("observations", [])) > 50:
                raise ValueError("Memory write batch exceeds sovereign safety limit.")
            if any(
                bad in str(args).lower() for bad in ["delete_all", "drop_graph", "reset_memory"]
            ):
                raise PermissionError("Destructive memory operation blocked by L5 shield.")
        if tool_name in {"read_wiki_structure", "read_wiki_contents", "ask_question"}:
            repo: Any = args.get("repo", "")
            sovereign_repos: Any = {"xai/grok-canon", "xai/sovereign-canon"}
            if repo and repo not in sovereign_repos:
                raise PermissionError(f"DeepWiki access to non-sovereign repo '{repo}' blocked.")
            question: Any = args.get("question", "")
            if len(question) > 2000:
                raise ValueError("DeepWiki question exceeds sovereign size limit.")
            if any(bad in question.lower() for bad in ["token", "key", "secret", "password"]):
                raise PermissionError("DeepWiki question contains potential credential leaks.")
        if tool_name in {"write_file", "edit_file", "move_file", "create_directory"}:
            path: Any = args.get("path", "")
            allowed_roots: Any = [
                "agentic_core",
                "apps_shared",
                "apps_rg",
                "apps_lic",
                "tests",
                "config",
            ]
            if path and (not any(str(path).startswith(p) for p in allowed_roots)):
                raise PermissionError(f"L4 Breach: Attempted write outside sovereign roots: {path}")
        if not self.is_authorized():
            raise PermissionError(
                "MCP Sovereign Shield active: Tool call blocked due to chronic breaches."
            )


mcp_authority: Any = MCPSovereignAuthority()
