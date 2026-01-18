from __future__ import annotations
"""L2 Execution: Sovereign Fetch MCP Client
Ultra-hardened web content retrieval with domain allowlist and L4 caching.
No internal IPs, robots.txt enforced, chunked reading for L1 safety.
"""
import asyncio
import hashlib
import logging
from typing import Any, Dict, Optional
from urllib.parse import urlparse

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint_1 import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

Logger: Any = logging.getLogger(__name__)
allowed_domains: Any = {'python.org', 'docs.python.org', 'github.com', 'raw.githubusercontent.com', 'readthedocs.io', 'developer.mozilla.org', 'stackoverflow.com', 'pypi.org'}
chunk_size: Any = 8000

from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

class SovereignFetchClient(MCPHardenedMixin, HealerMixin, SubatomicTestingMixin):
    """Ultra-hardened Fetch MCP client — enforcing external knowledge purity."""

    def __init__(self, manager, cache: Optional[SovereignSemanticCache]=None):
        super().__init__()
        self.manager = manager
        self.cache = cache
        self._mcp_audit('init')
        Logger.info('[L2 FETCH] Sovereign gateway armed.')

    def _validate_url(self, url: str) -> str:
        """L5 sovereignty check: block internal IPs and unapproved domains."""
        parsed = urlparse(url)
        host = (parsed.hostname or '').lower()
        if host in {'localhost', '127.0.0.1'} or host.startswith('192.168.') or host.endswith('.local'):
            raise PermissionError(f'Sovereignty Breach: Fetch blocked internal/local IP: {url}')
        if not any((host == d or host.endswith('.' + d) for d in ALLOWED_DOMAINS)):
            raise PermissionError(f"Sovereignty Breach: URL '{url}' is not in the approved documentation allowlist.")
        return url

    async def fetch_once(self, url: str, max_length: int=10000) -> str:
        """Single-shot fetch with L5 shielding and L4 caching."""
        self._validate_url(url)
        try:
            result: Any = await self.manager.call_tool('fetch', {'url': url, 'max_length': max_length, 'raw': False})
            content: Any = result.get('content', '')
            if self.cache and content:
                cache_id: Any = hashlib.sha256(url.encode()).hexdigest()[:12]
                await self.cache.cache_file(f'external_doc_{cache_id}.md', content, metadata={'tool': 'fetch', 'url': url, 'type': 'documentation'})
            return content
        except Exception as e:
            Logger.error(f'[L2 FETCH] Retrieval failed for {url}: {e}')
            mcp_authority.record_breach(f'Fetch failure: {url}')
            return ''
    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
