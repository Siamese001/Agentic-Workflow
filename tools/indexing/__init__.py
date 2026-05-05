"""Indexing tools for vector store population.

Exports:
    InterviewCard: Interview card data structure
    generate_corpus: Generate the full 110-variant corpus
    embed_corpus: Embed corpus using BGE-M3
"""

from .interview_card_corpus import (
    ARCHETYPES,
    InterviewCard,
    generate_corpus,
    get_card_by_slug,
    get_corpus_by_archetype,
)

__all__ = [
    "ARCHETYPES",
    "InterviewCard",
    "generate_corpus",
    "get_card_by_slug",
    "get_corpus_by_archetype",
]
