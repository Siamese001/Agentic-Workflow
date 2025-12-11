"""
RAG Request Understanding Load Planner - Plans loading for RAG request understanding.

This planner manages the loading phase for understanding RAG requests,
including query analysis, context extraction, and retrieval strategy planning.
Follows the canonical pattern with dataclass-first design and proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class RequestType(Enum):
    """Types of RAG requests."""
    QUERY = "query"
    SEMANTIC_SEARCH = "semantic_search"
    HYBRID_SEARCH = "hybrid_search"
    FILTERED_RETRIEVAL = "filtered_retrieval"
    CONTEXTUAL_QA = "contextual_qa"
    SUMMARIZATION = "summarization"


class RetrievalStrategy(Enum):
    """Retrieval strategies."""
    VECTOR_ONLY = "vector_only"
    KEYWORD_ONLY = "keyword_only"
    HYBRID = "hybrid"
    MULTI_STAGE = "multi_stage"
    RERANK = "rerank"
    ADAPTIVE = "adaptive"


class ProcessingLevel(Enum):
    """Processing levels for requests."""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    DEEP = "deep"


@dataclass
class QueryInfo:
    """Information about the query."""
    text: str
    type: RequestType
    intent: str
    entities: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    embeddings: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextInfo:
    """Information about context requirements."""
    required_domains: List[str] = field(default_factory=list)
    excluded_domains: List[str] = field(default_factory=list)
    time_range: Optional[Dict[str, Any]] = None
    source_types: List[str] = field(default_factory=list)
    metadata_filters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalConfig:
    """Configuration for retrieval."""
    strategy: RetrievalStrategy
    top_k: int = 10
    similarity_threshold: float = 0.7
    rerank_top_k: Optional[int] = None
    include_metadata: bool = True
    enable_cache: bool = True
    cache_ttl: int = 300


@dataclass
class RAGLoadPlan:
    """Complete plan for RAG request loading."""
    id: str
    name: str
    query_info: QueryInfo
    context_info: ContextInfo
    retrieval_config: RetrievalConfig
    processing_level: ProcessingLevel = ProcessingLevel.STANDARD
    enable_reranking: bool = False
    enable_filtering: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGLoadConfig:
    """Configuration for RAG load planning."""
    enable_query_expansion: bool = True
    enable_intent_detection: bool = True
    enable_entity_extraction: bool = True
    max_query_length: int = 1000
    default_top_k: int = 10
    default_processing_level: str = "standard"
    log_level: str = "INFO"


@dataclass
class RAGLoadResult:
    """Result of RAG load planning."""
    success: bool
    load_plan: Optional[RAGLoadPlan] = None
    query_complexity: str = "medium"
    estimated_retrieval_time: int = 0
    memory_estimate: int = 0
    document_count_estimate: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    safety_validated: bool = False
