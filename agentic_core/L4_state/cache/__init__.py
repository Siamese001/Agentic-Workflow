"""L2 Execution Cache Module - GPTCache Integration

Provides spec-compliant L2 Semantic Cache using GPTCache.
"""

from agentic_core.L4_state.cache.gptcache_client import (
    GPTCacheClient,
    cache_response,
    get_cached_response,
    get_global_gptcache,
)

__all__ = [
    "GPTCacheClient",
    "cache_response",
    "get_cached_response",
    "get_global_gptcache",
]
