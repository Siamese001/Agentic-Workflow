"""Hybrid Retrieval, Reranking, and Completeness-Aware Retrieval package."""

from .answer_support import KeywordAnswerSupportValidator
from .completeness import (
    ContextCompletenessScore,
    GroundedDocument,
    IAnswerSupportValidator,
    IContextCompletenessScorer,
    IParentChildExpander,
    SupportedAnswerCheck,
)
from .completeness_reranker import CompletenessReranker, CompletenessRerankerConfig
from .completeness_scorer import CompletenessScorerConfig, KeywordCompletenessScorer
from .fusion import ReciprocalRankFusion, ScoreFusion
from .interfaces import Document, ICandidateFusion, IReranker, IRetrieverLexical, IRetrieverVector
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
from .late_chunking import (
    VALID_MODES,
    LateChunkingMode,
    LateChunkingPipelineConfig,
    LateChunkingProfile,
    LateChunkManifest,
    build_late_chunk_manifests_for_corpus,
    segment_document,
)
from .meta_learning_bridge import (
    CompletenessChangePackage,
    CompletenessRAGProposer,
    EvaluationSignals,
)
from .parent_child import ChunkEntry, ParentChildExpander, ParentChildRegistry
from .profiles import (
    PROFILE_HYBRID,
    PROFILE_HYBRID_RERANKED,
    PROFILE_VECTOR_ONLY,
    RetrievalPipeline,
    RetrievalProfileConfig,
    make_profile,
)
from .reranker import HeuristicReranker, PassthroughReranker

__all__ = [
    "Document",
    "IRetrieverLexical",
    "IRetrieverVector",
    "ICandidateFusion",
    "IReranker",
    "ReciprocalRankFusion",
    "ScoreFusion",
    "HeuristicReranker",
    "PassthroughReranker",
    "RetrievalPipeline",
    "RetrievalProfileConfig",
    "make_profile",
    "PROFILE_VECTOR_ONLY",
    "PROFILE_HYBRID",
    "PROFILE_HYBRID_RERANKED",
    "ContextCompletenessScore",
    "GroundedDocument",
    "IParentChildExpander",
    "IContextCompletenessScorer",
    "IAnswerSupportValidator",
    "SupportedAnswerCheck",
    "CompletenessScorerConfig",
    "KeywordCompletenessScorer",
    "CompletenessRerankerConfig",
    "CompletenessReranker",
    "KeywordAnswerSupportValidator",
    "ChunkEntry",
    "ParentChildRegistry",
    "ParentChildExpander",
    "ChunkManifest",
    "ParentChildLink",
    "RetrievalEvaluationRecord",
    "ContextCompletenessSnapshot",
    "ChunkManifestRegistry",
    "ParentChildIndexRegistry",
    "RetrievalEvaluationRegistry",
    "ContextCompletenessSnapshotStore",
    "EvaluationSignals",
    "CompletenessChangePackage",
    "CompletenessRAGProposer",
    "LateChunkingProfile",
    "LateChunkManifest",
    "LateChunkingPipelineConfig",
    "LateChunkingMode",
    "VALID_MODES",
    "segment_document",
    "build_late_chunk_manifests_for_corpus",
]
