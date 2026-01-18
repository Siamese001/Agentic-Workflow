from __future__ import annotations
"""
Sovereign Fetch MCP Client – Phase 15
Sanitized Content Ingestion
L3 Routed | L5 Shielded

Replaces legacy requests calls with MCP tool that automatically converts
HTML to clean Markdown—essential for feeding L1 Cognition high-signal data.
"""
import logging
from typing import Dict, Any, Optional
from agentic_core.config.blueprint_sovereign.sovereign_config import config

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint_2 import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

Logger: Any = logging.getLogger('L2.Fetch')

class SovereignFetchMcpClient(MCPHardenedMixin, HealerMixin, SubatomicTestingMixin):
    """
    Fetch MCP Client for sanitized content ingestion.
    
    Automatically converts HTML to clean Markdown, bypasses cookie walls,
    and standardizes formatting for L1 Cognition processing.
    """

    def __init__(self):
        """Initialize Fetch client with sovereign routing."""
        super().__init__()
        self.router = SovereignMCPRouter(role='content_ingestion')
        self.initialized = False
        self._mcp_audit('init')
        Logger.info('[L2 FETCH] Client initialized')

    async def initialize(self) -> Any:
        """Async initialization of MCP router."""
        try:
            await self.router.initialize()
            self.initialized = True
            Logger.info('[L2 FETCH] Router initialized successfully')
        except Exception as e:
            Logger.error(f'[L2 FETCH] Initialization failed: {e}')
            raise

    async def _ensure_initialized(self):
        """Ensure MCP client is initialized."""
        if not self.initialized:
            await self.initialize()

    async def get_clean_content(self, url: str, max_length: Optional[int]=None) -> str:
        """
        Fetches URL and returns sanitized Markdown text.
        Bypasses cookie walls and standardizes formatting.
        
        Args:
            url: Target URL to fetch
            max_length: Optional max content length (uses config default if not specified)
            
        Returns:
            Clean markdown content
        """
        if not config.FETCH_MCP_ENABLED:
            return 'Error: Fetch MCP disabled in sovereign config'
        await self._ensure_initialized()
        Logger.info(f'📥 [L2 FETCH] Fetching clean content from: {url}')
        try:
            result: Any = await self.router.manager.call_tool(tool_name='mcp3_fetch_url', args={'url': url, 'max_length': max_length or config.FETCH_MAX_CONTENT_LENGTH, 'start_index': 0, 'raw': False})
            content: Any = ''
            if isinstance(result, dict):
                content: Any = result.get('content', '') or result.get('text', '')
            elif hasattr(result, 'content'):
                if isinstance(result.content, list):
                    content: Any = ''.join([c.text for c in result.content if hasattr(c, 'text')])
                else:
                    content: Any = str(result.content)
            else:
                content: Any = str(result)
            if len(content) < 10:
                Logger.warning(f'⚠️ [L2 FETCH] Extremely low content signal for {url}')
                return f'Warning: Minimal content extracted from {url}'
            Logger.info(f'✅ [L2 FETCH] Successfully fetched {len(content)} chars from: {url}')
            return content
        except Exception as e:
            Logger.error(f'[L2 FETCH] Fetch failed for {url}: {e}')
            return f'Error fetching content from {url}: {str(e)}'

    async def fetch_raw_html(self, url: str, max_length: Optional[int]=None) -> str:
        """
        Fetches URL and returns raw HTML (no Markdown conversion).
        
        Args:
            url: Target URL to fetch
            max_length: Optional max content length
            
        Returns:
            Raw HTML content
        """
        if not config.FETCH_MCP_ENABLED:
            return 'Error: Fetch MCP disabled in sovereign config'
        await self._ensure_initialized()
        Logger.info(f'📥 [L2 FETCH] Fetching raw HTML from: {url}')
        try:
            result: Any = await self.router.manager.call_tool(tool_name='mcp3_fetch_url', args={'url': url, 'max_length': max_length or config.FETCH_MAX_CONTENT_LENGTH, 'start_index': 0, 'raw': True})
            content: Any = ''
            if isinstance(result, dict):
                content: Any = result.get('content', '') or result.get('text', '')
            elif hasattr(result, 'content'):
                if isinstance(result.content, list):
                    content: Any = ''.join([c.text for c in result.content if hasattr(c, 'text')])
                else:
                    content: Any = str(result.content)
            else:
                content: Any = str(result)
            Logger.info(f'✅ [L2 FETCH] Successfully fetched {len(content)} chars (raw) from: {url}')
            return content
        except Exception as e:
            Logger.error(f'[L2 FETCH] Raw fetch failed for {url}: {e}')
            return f'Error fetching raw content from {url}: {str(e)}'

    async def fetch_youtube_transcript(self, url: str) -> str:
        """
        Fetch transcript for a YouTube video.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Video transcript text
        """
        if not config.FETCH_MCP_ENABLED:
            return 'Error: Fetch MCP disabled in sovereign config'
        await self._ensure_initialized()
        Logger.info(f'📺 [L2 FETCH] Fetching YouTube transcript from: {url}')
        try:
            result: Any = await self.router.manager.call_tool(tool_name='mcp3_fetch_youtube_transcript', args={'url': url})
            transcript: Any = ''
            if isinstance(result, dict):
                transcript: Any = result.get('transcript', '') or result.get('text', '')
            elif hasattr(result, 'content'):
                if isinstance(result.content, list):
                    transcript: Any = ''.join([c.text for c in result.content if hasattr(c, 'text')])
                else:
                    transcript: Any = str(result.content)
            else:
                transcript: Any = str(result)
            if len(transcript) < 10:
                Logger.warning(f'⚠️ [L2 FETCH] No transcript found for: {url}')
                return f'Warning: No transcript available for {url}'
            Logger.info(f'✅ [L2 FETCH] Successfully fetched transcript ({len(transcript)} chars) from: {url}')
            return transcript
        except Exception as e:
            Logger.error(f'[L2 FETCH] YouTube transcript fetch failed for {url}: {e}')
            return f'Error fetching YouTube transcript from {url}: {str(e)}'

    async def fetch_multiple_urls(self, urls: list[str], max_length: Optional[int]=None) -> Dict[str, str]:
        """
        Fetch content from multiple URLs concurrently.
        
        Args:
            urls: List of URLs to fetch
            max_length: Optional max content length per URL
            
        Returns:
            Dict mapping URLs to their content
        """
        if not config.FETCH_MCP_ENABLED:
            return {url: 'Error: Fetch MCP disabled' for url in urls}
        await self._ensure_initialized()
        Logger.info(f'📥 [L2 FETCH] Fetching content from {len(urls)} URLs')
        results: Any = {}
        for url in urls:
            try:
                content: Any = await self.get_clean_content(url, max_length)
                results[url] = content
            except Exception as e:
                Logger.error(f'[L2 FETCH] Failed to fetch {url}: {e}')
                results[url] = f'Error: {str(e)}'
        successful: Any = sum((1 for v in results.values() if not v.startswith('Error')))
        Logger.info(f'✅ [L2 FETCH] Successfully fetched {successful}/{len(urls)} URLs')
        return results

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Fetch connection.
        
        Returns:
            Health status
        """
        try:
            content: Any = await self.get_clean_content('https://example.com')
            if 'Error' not in content and len(content) > 0:
                return {'status': 'healthy', 'max_content_length': config.FETCH_MAX_CONTENT_LENGTH, 'extract_markdown': config.FETCH_EXTRACT_MARKDOWN, 'timeout': config.FETCH_TIMEOUT_SECONDS, 'initialized': self.initialized}
            else:
                return {'status': 'unhealthy', 'error': 'Failed to fetch test URL'}
        except Exception as e:
            Logger.error(f'[L2 FETCH] Health check failed: {e}')
            return {'status': 'unhealthy', 'error': str(e)}

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
_fetch_client: Optional[SovereignFetchMCPClient] = None

def get_fetch_client() -> SovereignFetchMCPClient:
    """Get or create the global Fetch client."""
    global _fetch_client
    if _fetch_client is None:
        _fetch_client = SovereignFetchMCPClient()
    return _fetch_client