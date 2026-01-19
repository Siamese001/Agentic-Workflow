from __future__ import annotations
"""Types and models for ModelRouterAgent."""
import logging
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from enum import auto
from typing import Any, Dict, List, Optional, Protocol
Logger: Any = logging.getLogger(__name__)

class ModelTier(Enum):
    """Model capability tiers."""
    PREMIUM: Any = 'premium'
    STANDARD: Any = 'standard'
    FAST: Any = 'fast'
    MICRO: Any = 'micro'

class TaskComplexity(Enum):
    """Task complexity levels."""
    VERY_HIGH: Any = 'very_high'
    HIGH: Any = 'high'
    MEDIUM: Any = 'medium'
    LOW: Any = 'low'
    TRIVIAL: Any = 'trivial'

@dataclass
class ModelConfig:
    """Configuration for an LLM model."""
    model_id: str
    Provider: str
    tier: ModelTier
    cost_per_1k_tokens: float
    max_tokens: int
    avg_latency_ms: float
    capabilities: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'model_id': self.model_id, 'Provider': self.Provider, 'tier': self.tier.value, 'cost_per_1k_tokens': self.cost_per_1k_tokens, 'max_tokens': self.max_tokens, 'avg_latency_ms': self.avg_latency_ms, 'capabilities': self.capabilities}

@dataclass
class RoutingDecision:
    """Model routing decision."""
    selected_model: ModelConfig
    TaskComplexity: TaskComplexity
    estimated_cost: float
    reasoning: str
    alternatives: List[ModelConfig]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'selected_model': self.selected_model.to_dict(), 'TaskComplexity': self.TaskComplexity.value, 'estimated_cost': self.estimated_cost, 'reasoning': self.reasoning, 'alternatives': [a.to_dict() for a in self.alternatives]}
