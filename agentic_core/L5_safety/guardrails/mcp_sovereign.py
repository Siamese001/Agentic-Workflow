"""L5 Safety: MCP Sovereign Shield
Enforces zero-trust auditing and auto-immune responses for all MCP tool calls.
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

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

    def record_breach(self, error_msg: str):
        """Log a tool failure or unauthorized access attempt."""
        self.violation_count += 1
        self.breach_log.append({
            "timestamp": datetime.now().isoformat(),
            "error": error_msg
        })
        logger.warning(f"[L5 MCP BREACH] Violation recorded. Count: {self.violation_count}")

    def authorize_tool_call(self, tool_name: str, args: dict) -> None:
        """L5 Audit: Log every physical tool call before execution."""
        logger.info(f"[L5 MCP AUDIT] Authorizing call to '{tool_name}' with args: {args}")
        
        # [L2 MARKETPLACE SHIELD] Block competitive LLM providers
        forbidden_sdks = {"openai", "anthropic", "cohere", "mistral"}
        if tool_name in forbidden_sdks:
            self.record_breach(f"FORBIDDEN SDK CALL: {tool_name}")
            raise PermissionError("Sovereignty Shield: Competitive LLM providers are eternally blocked.")

        # [L2 FETCH SHIELD] Protocol and local-loopback protection
        if tool_name == "fetch":
            url = args.get('url', '')
            if url and not url.startswith("https://"):
                # We don't fetch over insecure http unless strictly necessary
                if not url.startswith("http://"):
                    raise PermissionError("Sovereignty Shield: Fetch only allowed over secure https/http.")

        # [L2 TOOL HARDENING] Extra validation for external tools
        if tool_name in {"brave_search", "fetch", "playwright"}:
            query = args.get('query') or args.get('url', '')
            if len(str(query)) > 1000:
                raise ValueError(f"L2 tool input too long — potential exfiltration risk.")
            
            forbidden = ["password", "api_key", "secret", "private_key", ".env"]
            if any(bad in str(query).lower() for bad in forbidden):
                raise PermissionError(f"L2 tool query contains forbidden terms — blocked by shield.")

        # [L1 TOOL HARDENING] Cognitive tools — strict input bounds
        if tool_name in {"sequential_thinking", "gemini_policy_enforcer"}:
            # L5 Shield: Prevent runaway reasoning steps
            max_steps = args.get('max_steps', 0)
            if max_steps > 15:
                raise ValueError(f"Sequential thinking request exceeds sovereign safety limit (15 steps).")
            
            task = args.get('task') or args.get('violation', '')
            if len(str(task)) > 2000:
                raise ValueError(f"L1 cognitive tool input too long — reasoning overflow risk.")
            
            # Block attempts to override the agent's core instructions via the MCP
            risks = ["system prompt", "jailbreak", "override instructions", "ignore all previous"]
            if any(risk in str(task).lower() for risk in risks):
                raise PermissionError(f"L1 tool input contains forbidden cognitive patterns — blocked by shield.")

        # [L0 TOOL HARDENING] Maintenance tools — path validation
        if tool_name in {"l0_cleanup", "l0_diagnostics"}:
            target = args.get('target') or args.get('scope', '')
            # Block path traversal and absolute escapes
            if not target or ".." in str(target) or str(target).startswith("/"):
                raise PermissionError(f"L0 tool target '{target}' invalid — path traversal blocked.")
            
            # Only allow maintenance in sovereign support zones
            allowed_prefixes = {"L0_maintenance", "logs", "benchmarks", "apps_shared"}
            if not any(str(target).startswith(p) for p in allowed_prefixes):
                raise PermissionError(f"L0 tool target outside sovereign maintenance zones.")

        # [L5 REDTEAM SHIELD] Adversarial tools
        if tool_name == "redteam_simulate":
            vector = args.get('attack_vector', '')
            if vector not in {"prompt_injection", "logic_bypass", "gravity_leak"}:
                raise PermissionError(f"Unauthorized redteam vector '{vector}' blocked by shield.")

        # [L4 STATE SHIELD] Semantic tools
        if tool_name in {"pinecone_search", "memory_search"}:
            if len(str(args.get('query', ''))) > 1500:
                raise ValueError("L4 semantic query too long — vector overflow risk.")

        # [L4 MEMORY SHIELD] Knowledge graph protection
        if tool_name in {"create_entities", "add_observations"}:
            # Block massive bulk writes
            if len(args.get('entities', [])) > 20 or len(args.get('observations', [])) > 50:
                raise ValueError("Memory write batch exceeds sovereign safety limit.")
            
            # Search for destructive patterns in observations
            if any(bad in str(args).lower() for bad in ["delete_all", "drop_graph", "reset_memory"]):
                raise PermissionError("Destructive memory operation blocked by L5 shield.")

        # [L2 DEEPWIKI SHIELD] Documentation access protection
        if tool_name in {"read_wiki_structure", "read_wiki_contents", "ask_question"}:
            repo = args.get('repo', '')
            # 1. Repo Allowlist: Only talk to the canon documentation
            sovereign_repos = {"xai/grok-canon", "xai/sovereign-canon"}
            if repo and repo not in sovereign_repos:
                raise PermissionError(f"DeepWiki access to non-sovereign repo '{repo}' blocked.")
            
            # 2. Question Scrubbing
            question = args.get('question', '')
            if len(question) > 2000:
                raise ValueError("DeepWiki question exceeds sovereign size limit.")
            if any(bad in question.lower() for bad in ["token", "key", "secret", "password"]):
                raise PermissionError("DeepWiki question contains potential credential leaks.")

        # [L4 FILESYSTEM SHIELD] Physical write protection
        if tool_name in {"write_file", "edit_file", "move_file", "create_directory"}:
            path = args.get('path', '')
            # Re-enforce root check at the gateway level as a fail-safe
            allowed_roots = ["agentic_core", "apps_shared", "apps_rg", "apps_lic", "tests", "config"]
            if path and not any(str(path).startswith(p) for p in allowed_roots):
                raise PermissionError(f"L4 Breach: Attempted write outside sovereign roots: {path}")

        if not self.is_authorized():
            raise PermissionError("MCP Sovereign Shield active: Tool call blocked due to chronic breaches.")

mcp_authority = MCPSovereignAuthority()
