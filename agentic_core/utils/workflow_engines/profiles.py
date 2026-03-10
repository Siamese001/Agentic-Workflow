"""
Retrieval Profiles

Named retrieval pipeline configurations: vector_only, hybrid, hybrid_reranked.
Each profile wires together retrieval, fusion, and reranking components.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .fusion import ReciprocalRankFusion
from .interfaces import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    Document,
    ICandidateFusion,
    IReranker,
    IRetrieverLexical,
    IRetrieverVector,
)
from .reranker import HeuristicReranker

PROFILE_VECTOR_ONLY = "vector_only"
PROFILE_HYBRID = "hybrid"
PROFILE_HYBRID_RERANKED = "hybrid_reranked"


@dataclass
class RetrievalProfileConfig:
    """Configuration for a named retrieval profile."""
    mode: str
    lexical_k: int = 50
    vector_k: int = 50
    rerank_k: int = 10
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "lexical_k": self.lexical_k,
            "vector_k": self.vector_k,
            "rerank_k": self.rerank_k,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RetrievalProfileConfig:
        return cls(
            mode=data["mode"],
            lexical_k=data.get("lexical_k", 50),
            vector_k=data.get("vector_k", 50),
            rerank_k=data.get("rerank_k", 10),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def load_from_file(cls, path: Path) -> RetrievalProfileConfig:
        """Load profile config from JSON file."""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)


class RetrievalPipeline:
    """Executes a retrieval profile against injected retriever components.

    Supports vector_only, hybrid, and hybrid_reranked modes.
    """

    def __init__(
        self,
        config: RetrievalProfileConfig,
        lexical_retriever: IRetrieverLexical | None = None,
        vector_retriever: IRetrieverVector | None = None,
        fusion: ICandidateFusion | None = None,
        reranker: IReranker | None = None,
    ):
        self.config = config
        self.lexical_retriever = lexical_retriever
        self.vector_retriever = vector_retriever
        self.fusion = fusion or ReciprocalRankFusion()
        self.reranker = reranker or HeuristicReranker(top_k=config.rerank_k)

    def retrieve(self, query: str) -> list[Document]:
        """Execute the configured retrieval pipeline for a query.

        Args:
            query: Search query string

        Returns:
            Ranked list of Document objects
        """
        mode = self.config.mode

        if mode == PROFILE_VECTOR_ONLY:
            return self._vector_only(query)
        elif mode == PROFILE_HYBRID:
            return self._hybrid(query)
        elif mode == PROFILE_HYBRID_RERANKED:
            return self._hybrid_reranked(query)
        else:
            raise ValueError(f"Unknown retrieval mode: {mode!r}")

    def _vector_only(self, query: str) -> list[Document]:
        """Vector-only retrieval."""
        if self.vector_retriever is None:
            return []
        embedding = self.vector_retriever.embed_query(query)
        return self.vector_retriever.retrieve(embedding, top_k=self.config.vector_k)

    def _hybrid(self, query: str) -> list[Document]:
        """Hybrid retrieval with fusion but no reranking."""
        lexical: list[Document] = []
        vector: list[Document] = []

        if self.lexical_retriever is not None:
            lexical = self.lexical_retriever.retrieve(query, top_k=self.config.lexical_k)
        if self.vector_retriever is not None:
            embedding = self.vector_retriever.embed_query(query)
            vector = self.vector_retriever.retrieve(embedding, top_k=self.config.vector_k)

        return self.fusion.merge(lexical, vector)

    def _hybrid_reranked(self, query: str) -> list[Document]:
        """Hybrid retrieval with fusion and reranking."""
        merged = self._hybrid(query)
        return self.reranker.rerank(query, merged)

    def to_retrieval_fn(self):
        """Return a callable compatible with OfflineEvaluationRunner.retrieval_fn."""
        def retrieval_fn(query: str) -> list[str]:
            docs = self.retrieve(query)
            return [d.doc_id for d in docs]
        return retrieval_fn


def make_profile(
    mode: str,
    lexical_k: int = 50,
    vector_k: int = 50,
    rerank_k: int = 10,
) -> RetrievalProfileConfig:
    """Factory for common retrieval profiles."""
    valid_modes = {PROFILE_VECTOR_ONLY, PROFILE_HYBRID, PROFILE_HYBRID_RERANKED}
    if mode not in valid_modes:
        raise ValueError(f"mode must be one of {valid_modes}, got {mode!r}")
    return RetrievalProfileConfig(
        mode=mode,
        lexical_k=lexical_k,
        vector_k=vector_k,
        rerank_k=rerank_k,
    )


__all__ = [
    "RetrievalProfileConfig",
    "RetrievalPipeline",
    "make_profile",
    "PROFILE_VECTOR_ONLY",
    "PROFILE_HYBRID",
    "PROFILE_HYBRID_RERANKED",
]
