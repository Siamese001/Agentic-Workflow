"""Knowledge Enrichment Module - Semantic Knowledge Object Creation

Implements Pipeline B Step 3: Transform raw text chunks into structured
Knowledge Objects via LLM-based enrichment.
"""

from agentic_core.knowledge.enrichment.semantic_enricher import (
    SemanticEnricher,
    SemanticKnowledgeObject,
    enrich_chunk,
    get_global_enricher,
)

__all__ = [
    "SemanticEnricher",
    "SemanticKnowledgeObject",
    "enrich_chunk",
    "get_global_enricher",
]
