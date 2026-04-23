"""Hybrid Retrieval, Reranking, and Completeness-Aware Retrieval package.

Note: Many submodules were archived in Wave B (2026-04-23). This package
now exports only the surviving primitives from `completeness`, `interfaces`,
and `l4_registries`. Wave B.5 repaired this __init__ on 2026-04-23.
"""

from .completeness import (
    ContextCompletenessScore,
    GroundedDocument,
    IAnswerSupportValidator,
    IContextCompletenessScorer,
    IParentChildExpander,
    SupportedAnswerCheck,
)
from .interfaces import (
    Document,
    ICandidateFusion,
    IReranker,
    IRetrieverLexical,
    IRetrieverVector,
)
from .l4_registries import (
    ChunkManifest,
    ChunkManifestRegistry,
    ContextCompletenessSnapshot,
    ContextCompletenessSnapshotStore,
    ParentChildIndexRegistry,
    ParentChildLink,
    RetrievalEvaluationRecord,
    RetrievalEvaluationRegistry,
)

__all__ = [
    "ContextCompletenessScore",
    "GroundedDocument",
    "IAnswerSupportValidator",
    "IContextCompletenessScorer",
    "IParentChildExpander",
    "SupportedAnswerCheck",
    "Document",
    "ICandidateFusion",
    "IReranker",
    "IRetrieverLexical",
    "IRetrieverVector",
    "ChunkManifest",
    "ChunkManifestRegistry",
    "ContextCompletenessSnapshot",
    "ContextCompletenessSnapshotStore",
    "ParentChildIndexRegistry",
    "ParentChildLink",
    "RetrievalEvaluationRecord",
    "RetrievalEvaluationRegistry",
]
