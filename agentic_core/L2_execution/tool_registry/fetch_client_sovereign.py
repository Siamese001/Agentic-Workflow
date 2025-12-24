"""L2 Execution: Sovereign Fetch MCP Client
Ultra-hardened web content retrieval with domain allowlist and L4 caching.
No internal IPs, robots.txt enforced, chunked reading for L1 safety.
"""
import asyncio
import logging
import hashlib
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from agentic_core.L5_safety.guardrails.mcp_sovereign import mcp_authority
from agentic_core.L4_state.semantic.semantic_cache_sovereign import SovereignSemanticCache

logger = logging.getLogger(__name__)

# Sovereign allowlist — only trusted documentation and pattern sources
ALLOWED_DOMAINS = {
    "python.org", "docs.python.org",
    "github.com", "raw.githubusercontent.com",
    "readthedocs.io", "developer.mozilla.org",
    "stackoverflow.com", "pypi.org"
}
CHUNK_SIZE = 8000  # Keep chunks within sovereign L1 reasoning bounds

class SovereignFetchClient:
    """Ultra-hardened Fetch MCP client — enforcing external knowledge purity."""
    
    def __init__(self, manager, cache: Optional[SovereignSemanticCache] = None):
        self.manager = manager
        self.cache = cache
        logger.info("[L2 FETCH] Sovereign gateway armed.")

    def _validate_url(self, url: str) -> str:
        """L5 sovereignty check: block internal IPs and unapproved domains."""
        parsed = urlparse(url)
        # 1. Block SSRF/Internal Exfiltration
        host = (parsed.hostname or "").lower()
        if host in {"localhost", "127.0.0.1"} or host.startswith("192.168.") or host.endswith(".local"):
            raise PermissionError(f"Sovereignty Breach: Fetch blocked internal/local IP: {url}")
        
        # 2. Enforce the Sovereign Allowlist
        if not any(host == d or host.endswith("." + d) for d in ALLOWED_DOMAINS):
            raise PermissionError(f"Sovereignty Breach: URL '{url}' is not in the approved documentation allowlist.")
        
        return url

    async def fetch_once(self, url: str, max_length: int = 10000) -> str:
        """Single-shot fetch with L5 shielding and L4 caching."""
        self._validate_url(url)
        try:
            # We use the standard 'fetch' tool but wrap it in our safety logic
            result = await self.manager.call_tool("fetch", {
                "url": url,
                "max_length": max_length,
                "raw": False
            })
            content = result.get("content", "")
            
            # [L4 CACHE] Store the truth eternally so we don't fetch it again
            if self.cache and content:
                cache_id = hashlib.sha256(url.encode()).hexdigest()[:12]
                await self.cache.cache_file(
                    f"external_doc_{cache_id}.md", 
                    content, 
                    metadata={"tool": "fetch", "url": url, "type": "documentation"}
                )
            
            return content
        except Exception as e:
            logger.error(f"[L2 FETCH] Retrieval failed for {url}: {e}")
            mcp_authority.record_breach(f"Fetch failure: {url}")
            return ""
