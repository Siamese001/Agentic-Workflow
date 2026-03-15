from __future__ import annotations

"L3 Orchestration: Sovereign MCP Marketplace Integration\nSafe discovery and registration of marketplace MCPs with L5 sovereignty enforcement.\nGEMINI-ONLY policy — forbidden providers auto-blocked.\n"
import logging

from agentic_core.seams.contracts.authority import get_mcp_authority
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

Logger = logging.getLogger(__name__)
sovereign_safe_mcps = {
    "Filesystem",
    "Time",
    "Redis",
    "Pinecone",
    "Playwright",
    "Figma",
    "Brave Search",
    "Fetch",
    "GitHub",
    "Memory",
}
forbidden_providers = {"OpenAI", "Anthropic", "Claude", "GPT", "o1", "Llama"}


class SovereignMcpMarketplace:
    """Ultra-hardened marketplace integration — auto-register safe MCPs only."""

    def __init__(self, manager):
        self.manager = manager
        self.safe_tools: list[str] = []

    def discover_and_register_safe(self, marketplace_data: dict) -> None:
        """Parse marketplace and register only sovereign-safe MCPs."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SovereignMcpMarketplace.discover_and_register_safe")

        installed = marketplace_data.get("installed", [])
        available = marketplace_data.get("available", [])
        for mcp in installed + available:
            name = mcp.get("name", "")
            Provider = mcp.get("Provider", "")
            if any(forbidden in Provider for forbidden in forbidden_providers):
                Logger.critical(f"[L5 MCP BREACH] Forbidden Provider detected: {Provider} — blocked.")
                get_mcp_authority().record_breach(f"Attempted Marketplace Load: {Provider}")
                continue
            if name in sovereign_safe_mcps:
                try:
                    self.safe_tools.append(name)
                    Logger.info(f"[L3 MARKETPLACE] Sovereign MCP validated and armed: {name}")
                except Exception as e:
                    Logger.warning(f"Failed to register {name}: {e}")
                    raise
        if not self.safe_tools:
            Logger.warning("[L3 MARKETPLACE] No safe MCPs found. Running in LLM-only mode.")

    def get_safe_tools(self) -> list[str]:
        return self.safe_tools
