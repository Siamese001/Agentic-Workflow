"""
Core routing module.

Provides routing policies for model selection, task assignment, and resource
allocation within the agentic system based on task characteristics and requirements.
"""

from __future__ import annotations

from typing import Any, Optional, Dict, List, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

from .models import ComplexityLevel, TaskType, TaskSpecification

logger = logging.getLogger(__name__)


class RoutingStrategy(str, Enum):
    """Strategies for routing decisions."""
    
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    PRIORITY_BASED = "priority_based"
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    AVAILABILITY_FIRST = "availability_first"


@dataclass
class ModelCapability:
    """Capabilities and characteristics of available models."""
    
    model_id: str
    supported_tasks: List[TaskType]
    max_complexity: ComplexityLevel
    cost_per_token: float
    avg_response_time_ms: float
    reliability_score: float  # 0.0 to 1.0
    concurrent_limit: int
    current_load: int = 0
    is_available: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def can_handle_task(self, task_type: TaskType, complexity: ComplexityLevel) -> bool:
        """Check if model can handle the given task and complexity."""
        return (
            self.is_available and
            task_type in self.supported_tasks and
            complexity <= self.max_complexity and
            self.current_load < self.concurrent_limit
        )
    
    def get_load_ratio(self) -> float:
        """Get current load as ratio of capacity."""
        return self.current_load / self.concurrent_limit if self.concurrent_limit > 0 else 1.0


@dataclass
class RoutingDecision:
    """Result of routing decision."""
    
    selected_model: str
    confidence: float  # 0.0 to 1.0
    reasoning: str
    alternatives: List[str] = field(default_factory=list)
    estimated_cost: Optional[float] = None
    estimated_time_ms: Optional[float] = None


class RoutingPolicy:
    """
    Core routing policy for model selection and task assignment.
    
    Uses various strategies to select the optimal model for a given task
    based on complexity, cost, performance, and availability requirements.
    """
    
    def __init__(self, strategy: RoutingStrategy = RoutingStrategy.PERFORMANCE_OPTIMIZED):
        """
        Initialize routing policy.
        
        Args:
            strategy: Primary routing strategy to use
        """
        self.strategy = strategy
        self.model_capabilities: Dict[str, ModelCapability] = {}
        self.routing_history: List[Dict[str, Any]] = []
        self.custom_rules: List[Callable[[TaskSpecification], Optional[str]]] = []
        
        # Initialize default model capabilities
        self._initialize_default_models()
    
    def _initialize_default_models(self) -> None:
        """Initialize default model capabilities."""
        default_models = [
            ModelCapability(
                model_id="gpt-4",
                supported_tasks=[TaskType.GENERATION, TaskType.ANALYSIS, TaskType.PLANNING],
                max_complexity=ComplexityLevel.EXPERT,
                cost_per_token=0.03,
                avg_response_time_ms=2000,
                reliability_score=0.95,
                concurrent_limit=10
            ),
            ModelCapability(
                model_id="gpt-3.5-turbo",
                supported_tasks=[TaskType.EXECUTION, TaskType.VALIDATION, TaskType.COORDINATION],
                max_complexity=ComplexityLevel.ADVANCED,
                cost_per_token=0.002,
                avg_response_time_ms=800,
                reliability_score=0.90,
                concurrent_limit=20
            ),
            ModelCapability(
                model_id="claude-3-sonnet",
                supported_tasks=[TaskType.ANALYSIS, TaskType.GENERATION, TaskType.MONITORING],
                max_complexity=ComplexityLevel.COMPLEX,
                cost_per_token=0.015,
                avg_response_time_ms=1500,
                reliability_score=0.92,
                concurrent_limit=15
            ),
            ModelCapability(
                model_id="llama-2-70b",
                supported_tasks=[TaskType.EXECUTION, TaskType.VALIDATION],
                max_complexity=ComplexityLevel.INTERMEDIATE,
                cost_per_token=0.001,
                avg_response_time_ms=1200,
                reliability_score=0.85,
                concurrent_limit=25
            ),
            ModelCapability(
                model_id="mock-model",
                supported_tasks=list(TaskType),
                max_complexity=ComplexityLevel.EXPERT,
                cost_per_token=0.0,
                avg_response_time_ms=100,
                reliability_score=0.99,
                concurrent_limit=100
            )
        ]
        
        for model in default_models:
            self.model_capabilities[model.model_id] = model
    
    def register_model(self, capability: ModelCapability) -> None:
        """Register a new model capability."""
        self.model_capabilities[capability.model_id] = capability
        logger.info(f"Registered model capability: {capability.model_id}")
    
    def select_model(
        self,
        task: str,
        complexity: Union[ComplexityLevel, str],
        meta_profile: Optional[Any] = None,
        task_type: Optional[TaskType] = None
    ) -> str:
        """
        Select the best model for a given task.
        
        Args:
            task: Task description or identifier
            complexity: Task complexity level
            meta_profile: Optional user/system profile for routing
            task_type: Optional explicit task type
            
        Returns:
            Selected model ID
        """
        # Convert complexity to enum if string
        if isinstance(complexity, str):
            complexity = ComplexityLevel.from_string(complexity)
        
        # Infer task type from description if not provided
        if task_type is None:
            task_type = self._infer_task_type(task)
        
        # Create task specification for routing
        task_spec = TaskSpecification(
            name=task,
            task_type=task_type,
            complexity_level=complexity
        )
        
        decision = self.route_task(task_spec, meta_profile)
        return decision.selected_model
    
    def route_task(
        self,
        task_spec: TaskSpecification,
        meta_profile: Optional[Any] = None
    ) -> RoutingDecision:
        """
        Route a task specification to the optimal model.
        
        Args:
            task_spec: Task specification to route
            meta_profile: Optional user/system profile
            
        Returns:
            Routing decision with selected model and reasoning
        """
        # Check custom rules first
        for rule in self.custom_rules:
            custom_model = rule(task_spec)
            if custom_model and custom_model in self.model_capabilities:
                return RoutingDecision(
                    selected_model=custom_model,
                    confidence=1.0,
                    reasoning="Custom rule matched"
                )
        
        # Filter available models that can handle the task
        candidates = [
            model for model in self.model_capabilities.values()
            if model.can_handle_task(task_spec.task_type, task_spec.complexity_level)
        ]
        
        if not candidates:
            # Fallback to mock model if no candidates available
            logger.warning(f"No suitable models found for task {task_spec.name}, using mock model")
            return RoutingDecision(
                selected_model="mock-model",
                confidence=0.5,
                reasoning="No suitable models available, using fallback"
            )
        
        # Apply routing strategy
        selected_model = self._apply_strategy(candidates, task_spec, meta_profile)
        
        # Calculate confidence and reasoning
        confidence = self._calculate_confidence(selected_model, task_spec)
        reasoning = self._generate_reasoning(selected_model, task_spec)
        
        # Get alternatives
        alternatives = [m.model_id for m in candidates[:3] if m.model_id != selected_model.model_id]
        
        # Record routing decision
        self._record_routing_decision(selected_model, task_spec, confidence)
        
        return RoutingDecision(
            selected_model=selected_model.model_id,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=alternatives,
            estimated_cost=self._estimate_cost(selected_model, task_spec),
            estimated_time_ms=self._estimate_time(selected_model, task_spec)
        )
    
    def _infer_task_type(self, task_description: str) -> TaskType:
        """Infer task type from description."""
        description_lower = task_description.lower()
        
        if any(word in description_lower for word in ["plan", "strategy", "design"]):
            return TaskType.PLANNING
        elif any(word in description_lower for word in ["execute", "run", "perform"]):
            return TaskType.EXECUTION
        elif any(word in description_lower for word in ["analyze", "examine", "investigate"]):
            return TaskType.ANALYSIS
        elif any(word in description_lower for word in ["generate", "create", "write", "draft"]):
            return TaskType.GENERATION
        elif any(word in description_lower for word in ["validate", "check", "verify"]):
            return TaskType.VALIDATION
        elif any(word in description_lower for word in ["coordinate", "manage", "orchestrate"]):
            return TaskType.COORDINATION
        elif any(word in description_lower for word in ["monitor", "track", "observe"]):
            return TaskType.MONITORING
        else:
            return TaskType.EXECUTION  # Default
    
    def _apply_strategy(
        self,
        candidates: List[ModelCapability],
        task_spec: TaskSpecification,
        meta_profile: Optional[Any]
    ) -> ModelCapability:
        """Apply routing strategy to select from candidates."""
        if self.strategy == RoutingStrategy.PERFORMANCE_OPTIMIZED:
            # Select model with best reliability and lowest response time
            return min(candidates, key=lambda m: (m.avg_response_time_ms, -m.reliability_score))
        
        elif self.strategy == RoutingStrategy.COST_OPTIMIZED:
            # Select cheapest model
            return min(candidates, key=lambda m: m.cost_per_token)
        
        elif self.strategy == RoutingStrategy.LEAST_LOADED:
            # Select model with lowest load ratio
            return min(candidates, key=lambda m: m.get_load_ratio())
        
        elif self.strategy == RoutingStrategy.PRIORITY_BASED:
            # Select highest capability model
            return max(candidates, key=lambda m: (m.max_complexity.get_numeric_value(), m.reliability_score))
        
        elif self.strategy == RoutingStrategy.AVAILABILITY_FIRST:
            # Select model with highest availability
            return max(candidates, key=lambda m: (m.concurrent_limit - m.current_load, m.reliability_score))
        
        else:  # ROUND_ROBIN
            # Simple round-robin based on routing history
            model_counts = {}
            for record in self.routing_history[-100:]:  # Last 100 decisions
                model_id = record.get("model")
                model_counts[model_id] = model_counts.get(model_id, 0) + 1
            
            return min(candidates, key=lambda m: model_counts.get(m.model_id, 0))
    
    def _calculate_confidence(self, model: ModelCapability, task_spec: TaskSpecification) -> float:
        """Calculate confidence score for routing decision."""
        base_confidence = model.reliability_score
        
        # Adjust based on complexity margin
        complexity_margin = model.max_complexity.get_numeric_value() - task_spec.complexity_level.get_numeric_value()
        complexity_bonus = min(0.2, complexity_margin * 0.05)
        
        # Adjust based on load
        load_penalty = model.get_load_ratio() * 0.3
        
        confidence = base_confidence + complexity_bonus - load_penalty
        return max(0.0, min(1.0, confidence))
    
    def _generate_reasoning(self, model: ModelCapability, task_spec: TaskSpecification) -> str:
        """Generate reasoning for routing decision."""
        reasons = []
        
        if task_spec.complexity_level <= model.max_complexity:
            reasons.append(f"Model supports required complexity ({task_spec.complexity_level.value})")
        
        if task_spec.task_type in model.supported_tasks:
            reasons.append(f"Model supports task type ({task_spec.task_type.value})")
        
        if model.reliability_score > 0.9:
            reasons.append("High reliability model")
        
        if model.get_load_ratio() < 0.5:
            reasons.append("Low current load")
        
        if self.strategy == RoutingStrategy.COST_OPTIMIZED and model.cost_per_token < 0.01:
            reasons.append("Cost-effective choice")
        
        return "; ".join(reasons) if reasons else "Default selection"
    
    def _estimate_cost(self, model: ModelCapability, task_spec: TaskSpecification) -> Optional[float]:
        """Estimate cost for task execution."""
        if model.cost_per_token == 0:
            return None
        
        # Rough token estimation based on complexity
        estimated_tokens = {
            ComplexityLevel.SIMPLE: 100,
            ComplexityLevel.BASIC: 500,
            ComplexityLevel.INTERMEDIATE: 1500,
            ComplexityLevel.ADVANCED: 3000,
            ComplexityLevel.COMPLEX: 6000,
            ComplexityLevel.EXPERT: 10000
        }
        
        tokens = estimated_tokens.get(task_spec.complexity_level, 1000)
        return tokens * model.cost_per_token
    
    def _estimate_time(self, model: ModelCapability, task_spec: TaskSpecification) -> Optional[float]:
        """Estimate execution time in milliseconds."""
        # Base time adjusted by complexity
        complexity_multiplier = task_spec.complexity_level.get_numeric_value() / 3.0
        return model.avg_response_time_ms * complexity_multiplier
    
    def _record_routing_decision(
        self,
        model: ModelCapability,
        task_spec: TaskSpecification,
        confidence: float
    ) -> None:
        """Record routing decision for analytics."""
        self.routing_history.append({
            "timestamp": task_spec.name,  # Simplified timestamp
            "model": model.model_id,
            "task_type": task_spec.task_type.value,
            "complexity": task_spec.complexity_level.value,
            "confidence": confidence,
            "strategy": self.strategy.value
        })
        
        # Update model load
        model.current_load = min(model.current_load + 1, model.concurrent_limit)
        
        # Limit history size
        if len(self.routing_history) > 1000:
            self.routing_history = self.routing_history[-500:]
    
    def add_custom_rule(self, rule: Callable[[TaskSpecification], Optional[str]]) -> None:
        """Add a custom routing rule."""
        self.custom_rules.append(rule)
        logger.info("Added custom routing rule")
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        if not self.routing_history:
            return {"total_routes": 0}
        
        model_usage = {}
        for record in self.routing_history:
            model = record.get("model")
            model_usage[model] = model_usage.get(model, 0) + 1
        
        return {
            "total_routes": len(self.routing_history),
            "model_usage": model_usage,
            "strategy": self.strategy.value,
            "available_models": len(self.model_capabilities)
        }
    
    def update_model_load(self, model_id: str, load_change: int) -> None:
        """Update model load (for external monitoring)."""
        if model_id in self.model_capabilities:
            self.model_capabilities[model_id].current_load = max(
                0,
                min(
                    self.model_capabilities[model_id].current_load + load_change,
                    self.model_capabilities[model_id].concurrent_limit
                )
            )


# Global routing policy instance
_default_routing_policy = RoutingPolicy()


def get_routing_policy() -> RoutingPolicy:
    """Get the default routing policy instance."""
    return _default_routing_policy


def create_routing_policy(strategy: RoutingStrategy) -> RoutingPolicy:
    """Create a new routing policy with specified strategy."""
    return RoutingPolicy(strategy)


__all__ = [
    "RoutingStrategy",
    "ModelCapability",
    "RoutingDecision",
    "RoutingPolicy",
    "get_routing_policy",
    "create_routing_policy"
]





