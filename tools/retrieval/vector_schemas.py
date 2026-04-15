"""Typed request/response models for the retrieval service."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class OperationReport:
    message: str


@dataclass
class CollectionSummary:
    name: str
    id: str
    metadata: dict[str, Any] | None
    count: int | None = None
    count_error: str | None = None


@dataclass
class QueryHit:
    collection: str
    document: str
    distance: float | None
    metadata: dict[str, Any] | None = None


@dataclass
class QueryCollectionReport:
    collection_name: str
    query_text: str
    embedding_time_s: float
    query_time_s: float
    requested_results: int
    hits: list[QueryHit] = field(default_factory=list)


@dataclass
class CollectionInfoReport:
    name: str
    id: str
    document_count: int | None
    metadata: dict[str, Any] | None
    sample_documents: list[str] = field(default_factory=list)
    sample_error: str | None = None


@dataclass
class EmbeddingPreview:
    text: str
    preview: list[float]
    full_vector: list[float] | None = None


@dataclass
class EmbedTextReport:
    texts_processed: int
    processing_time_s: float
    embedding_dimension: int | None
    texts_per_second: float
    return_vectors: bool
    previews: list[EmbeddingPreview] = field(default_factory=list)


@dataclass
class SemanticSearchReport:
    query: str
    collections: list[str]
    total_search_time_s: float
    hits: list[QueryHit] = field(default_factory=list)
    collection_errors: dict[str, str] = field(default_factory=dict)


@dataclass
class CollectionStat:
    name: str
    count: int | None
    metadata: dict[str, Any] | None
    count_error: str | None = None


@dataclass
class VectorStatsReport:
    chroma_path: str
    total_collections: int
    embedding_model: str
    model_loaded: bool
    embedding_dimension: int | None
    encode_timeout_s: float
    encode_queue_wait_timeout_s: float
    query_timeout_s: float
    search_per_collection_timeout_s: float
    background_prewarm_enabled: bool
    collections: list[CollectionStat] = field(default_factory=list)
    total_documents: int = 0
    disk_bytes: int | None = None


@dataclass
class ReadinessReport:
    chroma_ready: bool
    chroma_loading: bool
    embedding_model_ready: bool
    embedding_model_loading: bool
    chroma_timeout_s: float
    model_timeout_s: float
    encode_timeout_s: float
    query_timeout_s: float
    background_prewarm_enabled: bool
