"""Legacy compatibility shim — re-exports ResearchCache from canonical location."""

from agentic_core.knowledge.research_cache.cache_store_util import ResearchCache

__all__ = ["ResearchCache"]
