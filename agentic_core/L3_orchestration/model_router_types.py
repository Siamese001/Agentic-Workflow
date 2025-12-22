"""Types and models for model_router."""
import logging
from dataclasses import dataclass  # Added import for dataclass
from enum import Enum  # Added import for Enum
from typing import Any, Dict, List  # Added imports for List, Dict, Any

LOGGER = logging.getLogger(__name__)
class ModelTier(Enum):
    """Model capability tiers."""
    PREMIUM = 'premium'
    STANDARD = 'standard'
    FAST = 'fast'
    MICRO = 'micro'

class TaskComplexity(Enum):
    """Task complexity levels."""
    VERY_HIGH = 'very_high'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'
    TRIVIAL = 'trivial'

@dataclass
class ModelConfig:
    """Configuration for an LLM model."""
    model_id: str
    provider: str
    tier: ModelTier
    cost_per_1k_tokens: float
    max_tokens: int
    avg_latency_ms: float
    capabilities: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'model_id': self.model_id,
            'provider': self.provider,
            'tier': self.tier.value,
            'cost_per_1k_tokens': self.cost_per_1k_tokens,
            'max_tokens': self.max_tokens,
            'avg_latency_ms': self.avg_latency_ms,
            'capabilities': self.capabilities
        }

@dataclass
class RoutingDecision:
    """Model routing decision."""
    selected_model: ModelConfig
    task_complexity: TaskComplexity
    estimated_cost: float
    reasoning: str
    alternatives: List[ModelConfig]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'selected_model': self.selected_model.to_dict(),
            'task_complexity': self.task_complexity.value,
            'estimated_cost': self.estimated_cost,
            'reasoning': self.reasoning,
            'alternatives': [a.to_dict() for a in self.alternatives]}