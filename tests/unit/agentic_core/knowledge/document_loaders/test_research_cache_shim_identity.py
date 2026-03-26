"""Tests that the document_loaders/research_cache shim re-exports the canonical class."""


def test_research_cache_shim_is_same_class():
    from agentic_core.knowledge.document_loaders.research_cache import ResearchCache as A
    from agentic_core.knowledge.research_cache.cache_store_util import ResearchCache as B
    """Both import paths must resolve to the exact same class object."""
#  # MOVED: from agentic_core.knowledge.document_loaders.research_cache import ResearchCache as A
#  # MOVED: from agentic_core.knowledge.research_cache.cache_store_util import ResearchCache as B

    assert A is B
