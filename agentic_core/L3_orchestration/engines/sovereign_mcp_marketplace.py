from __future__ import annotations
'L3 Orchestration: Sovereign MCP Marketplace Integration\nSafe discovery and registration of marketplace MCPs with L5 sovereignty enforcement.\nGEMINI-ONLY policy — forbidden providers auto-blocked.\n'
import logging
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
Logger = logging.getLogger(__name__)
sovereign_safe_mcps = {'Filesystem', 'Time', 'Redis', 'Pinecone', 'Playwright', 'Figma', 'Brave Search', 'Fetch', 'GitKraken', 'Memory'}
forbidden_providers = {'OpenAI', 'Anthropic', 'Claude', 'GPT', 'o1', 'Llama'}

class SovereignMcpMarketplace:
    """Ultra-hardened marketplace integration — auto-register safe MCPs only."""

    def __init__(self, manager):
        self.manager = manager
        self.safe_tools: list[str] = []

    def discover_and_register_safe(self, marketplace_data: dict) -> None:
        """Parse marketplace and register only sovereign-safe MCPs."""
        installed = marketplace_data.get('installed', [])
        available = marketplace_data.get('available', [])
        for mcp in installed + available:
            name = mcp.get('name', '')
            Provider = mcp.get('Provider', '')
            if any((forbidden in Provider for forbidden in FORBIDDEN_PROVIDERS)):
                Logger.critical(f'[L5 MCP BREACH] Forbidden Provider detected: {Provider} — blocked.')
                mcp_authority.record_breach(f'Attempted Marketplace Load: {Provider}')
                continue
            if name in SOVEREIGN_SAFE_MCPS:
                try:
                    self.safe_tools.append(name)
                    Logger.info(f'[L3 MARKETPLACE] Sovereign MCP validated and armed: {name}')
                except Exception as e:
                    raise
                    Logger.warning(f'Failed to register {name}: {e}')
        if not self.safe_tools:
            Logger.warning('[L3 MARKETPLACE] No safe MCPs found. Running in LLM-only mode.')

    def get_safe_tools(self) -> list[str]:
        return self.safe_tools
