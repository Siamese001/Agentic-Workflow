"""Implementation for titanium_v6_impl_impl_impl."""

from typing import Any, Dict, List, Optional

class TitaniumSearchWrapper:
    """Wrapper class to provide synchronous interface to async Titanium search."""

    def __init__(self):
        self._loop = None
        self._initialized = False

    def _ensure_loop(self):
        """Ensure we have an event loop."""
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

    def search(self,
        query: str,
        context: Optional[str]=None,
        max_results: int=5,
        include_metadata: bool=False) -> str:
        """Synchronous search wrapper.

        Args:
            query: Search query
            context: Optional context
            max_results: Maximum results
            include_metadata: Include source metadata

        Returns:
            Formatted search results
        """
        self._ensure_loop()
        return self._loop.run_until_complete(get_titanium_search_tool(query,
            context,
            max_results,
            include_metadata))

    def search_with_sources(self, query: str, context: Optional[str]=None) -> Dict[str, Any]:
        """Synchronous search with sources wrapper.

        Args:
            query: Search query
            context: Optional context

        Returns:
            Dictionary with sources and metadata
        """
        self._ensure_loop()
        return self._loop.run_until_complete(get_titanium_search_with_sources(query, context))

    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return get_pipeline_stats()

    def clear_cache(self):
        """Clear semantic cache."""
        self._ensure_loop()
        self._loop.run_until_complete(clear_cache())

class TitaniumAwareAgent:
    """Mixin class for agents to use Titanium search."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.titanium = _titanium_wrapper

    def search_knowledge(self, query: str, context: Optional[str]=None) -> str:
        """Search knowledge base using Titanium pipeline.

        Args:
            query: Search query
            context: Optional context

        Returns:
            Formatted search results
        """
        return self.titanium.search(query, context)

    def get_relevant_sources(self, query: str, context: Optional[str]=None) -> List[Dict[str, Any]]:
        """Get relevant sources with full metadata.

        Args:
            query: Search query
            context: Optional context

        Returns:
            List of sources with metadata
        """
        result = self.titanium.search_with_sources(query, context)
        return result.get('sources', [])

def get_titanium_wrapper() -> TitaniumSearchWrapper:
    """Get the global Titanium search wrapper."""
    return _titanium_wrapper

def inject_titanium_tools(context: Dict[str, Any]) -> Dict[str, Any]:
    """Inject Titanium search tools into agent context.

    Args:
        context: Agent execution context

    Returns:
        Updated context with Titanium tools
    """
    context['titanium_search'] = _titanium_wrapper.search
    context['titanium_search_with_sources'] = _titanium_wrapper.search_with_sources
    context['titanium_stats'] = _titanium_wrapper.get_stats
    context['titanium_clear_cache'] = _titanium_wrapper.clear_cache
    context['available_tools'] = context.get('available_tools', [])
    context['available_tools'].extend([{'name': 'titanium_search',
        'description': 'Search using the Titanium RAG Pipeline with precision,
        reasoning,
        and SOTA ranking',
        'parameters': {'query': {'type': 'string',
        'required': True},
        'context': {'type': 'string',
        'required': False},
        'max_results': {'type': 'integer',
        'required': False,
        'default': 5},
        'include_metadata': {'type': 'boolean',
        'required': False,
        'default': False}}},
        {'name': 'titanium_search_with_sources',
        'description': 'Search with full source information for citations',
        'parameters': {'query': {'type': 'string',
        'required': True},
        'context': {'type': 'string',
        'required': False}}}])
    logger.info('Injected Titanium RAG tools into agent context')
    return context

def with_titanium_search(agent_class):
    """Decorator to add Titanium search capabilities to any agent.

    Args:
        agent_class: Agent class to enhance

    Returns:
        Enhanced agent class with Titanium search
    """

    class TitaniumEnhancedAgent(TitaniumAwareAgent, agent_class):
        pass
    TitaniumEnhancedAgent.__name__ = agent_class.__name__
    TitaniumEnhancedAgent.__qualname__ = agent_class.__qualname__
    return TitaniumEnhancedAgent

def enhance_system_prompt(system_prompt: str) -> str:
    """Enhance system prompt with Titanium search instructions.

    Args:
        system_prompt: Original system prompt

    Returns:
        Enhanced system prompt
    """
    return system_prompt + TITANIUM_SYSTEM_PROMPT_ADDITION

async def prepare_titanium_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare context with Titanium search for async execution.

    Args:
        context: Original context

    Returns:
        Context enhanced with Titanium search capabilities
    """
    context['async_titanium_search'] = get_titanium_search_tool
    context['async_titanium_search_with_sources'] = get_titanium_search_with_sources
    context['titanium_pipeline_stats'] = get_pipeline_stats()
    return context

def log_titanium_usage(hop_id: str, query: str, results: Dict[str, Any]):
    """Log Titanium search usage for monitoring.

    Args:
        hop_id: Hop identifier
        query: Search query
        results: Search results
    """
    metadata = results.get('metadata', {})
    logger.info(f'Titanium Search Usage - Hop: {hop_id}')
    logger.info(f'  Query: {query[:100]}...')
    logger.info(f"  Cached: {metadata.get('cached', False)}")
    logger.info(f"  Decomposed: {metadata.get('decomposed', False)}")
    logger.info(f"  Reranked: {metadata.get('reranked', False)}")
    stats = get_pipeline_stats()
    if stats.get('status') == 'active':
        stats_data = stats.get('statistics', {})
        logger.info(f"  Pipeline Stats - Total: {stats_data.get('total_queries',
            0)},
            Cache Hit Rate: {stats_data.get('cache_hit_rate',
            0):.1%}")
