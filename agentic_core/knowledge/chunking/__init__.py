"""Chunking module for knowledge processing.

Pipeline B Phase B4: Corpus classifier and enhanced chunking strategies.
"""

from .chunk_policy_engine import ChunkPolicy, ChunkPolicyEngine
from .corpus_classifier import CorpusClassifier, CorpusType

__all__ = [
    "CorpusClassifier",
    "CorpusType",
    "ChunkPolicyEngine",
    "ChunkPolicy",
]
