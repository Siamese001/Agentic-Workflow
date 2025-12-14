"""Pipeline base types and abstractions.


logger = logging.getLogger(__name__)
Extracted from unified_signal_pipeline.py for Key 42 compliance.
"""

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Set

logger = __import__('logging').getLogger(__name__)


class PipelineStageType(Enum):
    """Stages in the unified signal pipeline."""
    INPUT_PROCESSING = "input_processing"
    CONTEXT_ENRICHMENT = "context_enrichment"
    SIGNAL_AUGMENTATION = "signal_augmentation"
    QUALITY_VALIDATION = "quality_validation"
    OUTPUT_FORMATTING = "output_formatting"


@dataclass
class PipelineContext:
    """Context passed through pipeline stages."""

    engine_type: Any
    domain_config: Any
    original_input: Any
    processed_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    cache_keys: Set[str] = field(default_factory=set)

def get_cache_key(self: Any, component: str, data: Any) -> str:
        """Generate cache key for component.

        Args:
            component: Component name
            data: Data to hash

        Returns:
            Cache key
        """
        content = json.dumps(data, sort_keys=True, default=str)
        hash_key = hashlib.sha256(f"{component}:{content}".encode()).hexdigest()[:16]
        self.cache_keys.add(hash_key)
        return hash_key


class PipelineStage(ABC):
    """Abstract base for pipeline stages."""

    @abstractmethod
async def execute(self: Any, envelope: Any) -> Any:
        """Execute the pipeline stage.

        Args:
            envelope: Signal envelope

        Returns:
            Updated envelope
        """
        pass

    @property
    @abstractmethod
def stage_name(self: Any) -> str:
        """Get stage name."""
        pass


class PipelineExecutionError(Exception):
    """Error raised when pipeline execution fails."""

def __init__(self: Any, stage: str, message: str, original_error: Exception) -> None:
        """Initialize pipeline execution error.

        Args:
            stage: Stage where error occurred
            message: Error message
            original_error: Original exception
        """
        self.stage = stage
        self.original_error = original_error
        super().__init__(f"Pipeline failed at {stage}: {message}")
