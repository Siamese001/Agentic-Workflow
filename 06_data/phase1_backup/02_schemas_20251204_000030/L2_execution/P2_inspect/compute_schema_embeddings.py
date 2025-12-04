"""
Schema definitions for schema embedding computation and vectorization.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import List
from enum import Enum


class EmbeddingModel(Enum):
    """Available embedding model types."""
    TRANSFORMER_SMALL = "transformer_small"
    TRANSFORMER_MEDIUM = "transformer_medium"
    TRANSFORMER_LARGE = "transformer_large"
    CUSTOM = "custom"


class VectorNormalization(Enum):
    """Vector normalization methods."""
    NONE = "none"
    L2 = "l2"
    L1 = "l1"
    MAX = "max"


@dataclass
class EmbeddingConfiguration:
    """Schema for embedding computation configuration."""
    model: EmbeddingModel
    normalization: VectorNormalization
    dimensions: int
    batch_size: int = 32
    include_metadata: bool = True


@dataclass
class SchemaEmbedding:
    """Schema for computed schema embedding."""
    schema_id: str
    embedding_vector: List[float]
    model_used: EmbeddingModel
    computation_timestamp: str
    confidence_score: float


@dataclass
class EmbeddingBatch:
    """Schema for batch embedding results."""
    batch_id: str
    embeddings: List[SchemaEmbedding]
    configuration: EmbeddingConfiguration
    processing_time_ms: int