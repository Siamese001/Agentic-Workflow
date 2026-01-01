"""Types and models for model_router."""
import logging
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from enum import auto
from typing import Any, Dict, List, Optional, Protocol
logger: Any = logging.getLogger(__name__)

class model_tier(Enum):
    """Model capability tiers."""
    PREMIUM: Any = 'premium'
    STANDARD: Any = 'standard'
    FAST: Any = 'fast'
    MICRO: Any = 'micro'

class task_complexity(Enum):
    """Task complexity levels."""
    VERY_HIGH: Any = 'very_high'
    HIGH: Any = 'high'
    MEDIUM: Any = 'medium'
    LOW: Any = 'low'
    TRIVIAL: Any = 'trivial'

@dataclass
class model_config:
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
        return {'model_id': self.model_id, 'provider': self.provider, 'tier': self.tier.value, 'cost_per_1k_tokens': self.cost_per_1k_tokens, 'max_tokens': self.max_tokens, 'avg_latency_ms': self.avg_latency_ms, 'capabilities': self.capabilities}

@dataclass
class routing_decision:
    """Model routing decision."""
    selected_model: ModelConfig
    task_complexity: TaskComplexity
    estimated_cost: float
    reasoning: str
    alternatives: List[ModelConfig]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'selected_model': self.selected_model.to_dict(), 'task_complexity': self.task_complexity.value, 'estimated_cost': self.estimated_cost, 'reasoning': self.reasoning, 'alternatives': [a.to_dict() for a in self.alternatives]}