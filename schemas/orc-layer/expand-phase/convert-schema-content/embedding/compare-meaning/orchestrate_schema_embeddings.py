"""
Schema definitions for orchestration-level schema embedding operations.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class EmbeddingStrategy(Enum):
    """Orchestration embedding strategies."""
    BATCH_PROCESSING = "batch_processing"
    STREAMING = "streaming"
    DISTRIBUTED = "distributed"
    CACHED = "cached"


class CoordinationMode(Enum):
    """Embedding coordination modes."""
    CENTRALIZED = "centralized"
    DECENTRALIZED = "decentralized"
    HYBRID = "hybrid"
    PEER_TO_PEER = "peer_to_peer"


@dataclass
class EmbeddingTask:
    """Schema for individual embedding task."""
    task_id: str
    schema_id: str
    embedding_model: str
    priority: str
    resource_requirements: Dict[str, int]


@dataclass
class EmbeddingOrchestration:
    """Schema for embedding orchestration."""
    orchestration_id: str
    strategy: EmbeddingStrategy
    coordination_mode: CoordinationMode
    tasks: List[EmbeddingTask]
    total_estimated_time_ms: int


@dataclass
class EmbeddingOrchestrationResult:
    """Schema for embedding orchestration results."""
    result_id: str
    orchestration: EmbeddingOrchestration
    completed_tasks: List[str]
    failed_tasks: List[str]
    resource_utilization: Dict[str, float]
    orchestration_time_ms: int
