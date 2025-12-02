"""
Schema definitions for schema algorithm application and execution.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class AlgorithmType(Enum):
    """Types of schema processing algorithms."""
    SORTING = "sorting"
    FILTERING = "filtering"
    CLUSTERING = "clustering"
    CLASSIFICATION = "classification"
    OPTIMIZATION = "optimization"


class AlgorithmMode(Enum):
    """Algorithm execution modes."""
    BATCH = "batch"
    STREAMING = "streaming"
    INCREMENTAL = "incremental"
    REAL_TIME = "real_time"


@dataclass
class AlgorithmParameters:
    """Schema for algorithm execution parameters."""
    algorithm_type: AlgorithmType
    mode: AlgorithmMode
    configuration: Dict[str, Any]
    resource_limits: Optional[Dict[str, int]] = None
    quality_threshold: Optional[float] = None


@dataclass
class AlgorithmInput:
    """Schema for algorithm input data."""
    input_id: str
    schema_components: List[Dict[str, Any]]
    context: Optional[Dict[str, Any]] = None
    preprocessing_required: bool = False


@dataclass
class AlgorithmResult:
    """Schema for algorithm execution result."""
    result_id: str
    algorithm_type: AlgorithmType
    processed_components: List[Dict[str, Any]]
    execution_metadata: Dict[str, Any]
    quality_metrics: Dict[str, float]