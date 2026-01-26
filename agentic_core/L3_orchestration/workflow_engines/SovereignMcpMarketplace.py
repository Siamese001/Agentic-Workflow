from __future__ import annotations

"""L3 Orchestration: Sovereign MCP Marketplace Integration
Safe discovery and registration of marketplace MCPs with L5 sovereignty enforcement.
GEMINI-ONLY policy — forbidden providers auto-blocked.
"""
import logging

# [SSOT IMPORT] Structure blueprint is the single source of truth


Logger = logging.getLogger(__name__)

# Sovereign allowlist — tools that don't bring their own "brain"
# NAMING FIXED: SOVEREIGN_SAFE_MCPS → sovereign_safe_mcps
sovereign_safe_mcps = {
    "Filesystem",
    "Time",
    "Redis",
    "Pinecone",
    "Playwright",
    "Figma",
    "Brave Search",
    "Fetch",
    "GitKraken",
    "Memory",
}

# Forbidden providers — competitive LLM ecosystems
# NAMING FIXED: FORBIDDEN_PROVIDERS → forbidden_providers
forbidden_providers = {"OpenAI", "Anthropic", "Claude", "GPT", "o1", "Llama"}


# NAMING FIXED: SovereignMCPMarketplace → SovereignMcpMarketplace
class SovereignMcpMarketplace:
    """Ultra-hardened marketplace integration — auto-register safe MCPs only."""

    def __init__(self, manager):
        self.manager = manager
        self.safe_tools: list[str] = []

    def discover_and_register_safe(self, marketplace_data: dict) -> None:
        """Parse marketplace and register only sovereign-safe MCPs."""
        installed = marketplace_data.get("installed", [])
        available = marketplace_data.get("available", [])

        for mcp in installed + available:
            name = mcp.get("name", "")
            Provider = mcp.get("Provider", "")

            # L5 sovereignty check: block competitive brains
            if any(forbidden in Provider for forbidden in FORBIDDEN_PROVIDERS):
                Logger.critical(
                    f"[L5 MCP BREACH] Forbidden Provider detected: {Provider} — blocked."
                )
                mcp_authority.record_breach(f"Attempted Marketplace Load: {Provider}")
                continue

            if name in SOVEREIGN_SAFE_MCPS:
                try:
                    # In a real system, we'd add the server command to the manager's pool
                    self.safe_tools.append(name)
                    Logger.info(f"[L3 MARKETPLACE] Sovereign MCP validated and armed: {name}")
                except Exception as e:
                    Logger.warning(f"Failed to register {name}: {e}")

        if not self.safe_tools:
            Logger.warning("[L3 MARKETPLACE] No safe MCPs found. Running in LLM-only mode.")

    def get_safe_tools(self) -> list[str]:
        return self.safe_tools
