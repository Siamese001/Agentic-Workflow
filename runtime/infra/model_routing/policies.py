"""Model routing policies for Agentic L5."""
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class RoutingStrategy(Enum):
    """Routing strategy enumeration."""
    PRIORITY_BASED = "priority_based"
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    BALANCED = "balanced"
    ARCHETYPE_SPECIFIC = "archetype_specific"

@dataclass
class ModelRoutingConfig:
    """Configuration for model routing."""
    strategy: RoutingStrategy = RoutingStrategy.BALANCED
    priority_weights: Dict[str, float] = field(default_factory=lambda: {
        "c_level": 2.0,
        "executive": 1.5,
        "senior_ta": 1.2,
        "recruiter": 1.0
    })
    cost_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "max_cost_per_request": 0.01,
        "daily_budget_limit": 100.0
    })
    performance_requirements: Dict[str, Any] = field(default_factory=lambda: {
        "max_latency_ms": 5000,
        "min_accuracy": 0.8
    })
    fallback_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RoutingDecision:
    """Result of routing decision."""
    selected_model: str
    confidence: float
    reasoning: str
    cost_estimate: float
    performance_estimate: Dict[str, float]
    fallback_used: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

class ModelRoutingPolicy:
    """Main model routing policy engine."""
    
    def __init__(self, config: Optional[ModelRoutingConfig] = None):
        """Initialize routing policy with configuration."""
        self.config = config or ModelRoutingConfig()
        self.routing_history = []
        self.model_registry = {
            "gpt-5.1": {"cost": 0.03, "performance": {"latency": 2000, "accuracy": 0.95}, "tier": "heavy"},
            "gpt-5-mini": {"cost": 0.015, "performance": {"latency": 1500, "accuracy": 0.90}, "tier": "medium"},
            "gpt-5-nano": {"cost": 0.002, "performance": {"latency": 800, "accuracy": 0.80}, "tier": "light"},
            "claude-opus-4-1-20250805": {"cost": 0.025, "performance": {"latency": 1800, "accuracy": 0.93}, "tier": "heavy"},
            "claude-sonnet-4-5-20250929": {"cost": 0.012, "performance": {"latency": 1200, "accuracy": 0.88}, "tier": "medium"},
            "claude-haiku-4-5-20251001": {"cost": 0.001, "performance": {"latency": 600, "accuracy": 0.75}, "tier": "light"},
            "gemini-3-pro-preview": {"cost": 0.02, "performance": {"latency": 1600, "accuracy": 0.91}, "tier": "heavy"},
            "gemini-2.5-flash": {"cost": 0.01, "performance": {"latency": 1000, "accuracy": 0.85}, "tier": "medium"},
            "gemini-2.5-flash-lite": {"cost": 0.0005, "performance": {"latency": 500, "accuracy": 0.70}, "tier": "light"}
        }
    
    def route_request(self, 
                      request_type: str,
                      archetype: str = None,
                      context: Dict[str, Any] = None) -> RoutingDecision:
        """Route a request to the optimal model based on policy."""
        context = context or {}
        
        # Apply routing strategy
        if self.config.strategy == RoutingStrategy.ARCHETYPE_SPECIFIC and archetype:
            decision = self._route_by_archetype(request_type, archetype, context)
        elif self.config.strategy == RoutingStrategy.COST_OPTIMIZED:
            decision = self._route_by_cost(request_type, context)
        elif self.config.strategy == RoutingStrategy.PERFORMANCE_OPTIMIZED:
            decision = self._route_by_performance(request_type, context)
        elif self.config.strategy == RoutingStrategy.PRIORITY_BASED:
            decision = self._route_by_priority(request_type, archetype, context)
        else:  # BALANCED
            decision = self._route_balanced(request_type, archetype, context)
        
        # Record routing decision
        self.routing_history.append(decision)
        
        return decision
    
    def select_model(self, archetype: str, budget_manager: Any = None, stage: str = None, context: Dict[str, Any] = None) -> str:
        """Select model based on archetype and budget constraints"""
        context = context or {}
        
        # Get priority for archetype (handle both string and enum)
        if hasattr(archetype, 'value'):
            archetype_str = archetype.value
        else:
            archetype_str = str(archetype)
        
        priority = self.config.priority_weights.get(archetype_str, 1.0)
        
        # Safety always gets heavy models regardless of budget
        if stage == 'safety':
            heavy_models = [name for name, info in self.model_registry.items() if info['tier'] == 'heavy']
            return heavy_models[0] if heavy_models else "gpt-5.1"
        
        # Unknown stage defaults to medium models
        if stage is None or stage == 'unknown' or 'unknown' in str(stage).lower():
            medium_models = [name for name, info in self.model_registry.items() if info['tier'] == 'medium']
            return medium_models[0] if medium_models else "gpt-5-mini"
        
        # Check budget constraints only if budget_manager exists and has constraints
        if budget_manager and hasattr(budget_manager, 'current_usage'):
            try:
                usage = budget_manager.current_usage()
                budget_exceeded = usage.get('budget_exceeded', {})
                
                # Check if budget is exceeded for tokens - use light models
                if budget_exceeded.get('tokens', False):
                    light_models = [name for name, info in self.model_registry.items() if info['tier'] == 'light']
                    return light_models[0] if light_models else "gpt-5-nano"
                
                # Check if low budget (less than 30% tokens remaining)
                if usage.get('tokens_remaining', 1000) < 300:
                    light_models = [name for name, info in self.model_registry.items() if info['tier'] == 'light']
                    return light_models[0] if light_models else "gpt-5-nano"
                
                # Check if medium budget (less than 70% tokens remaining)
                if usage.get('tokens_remaining', 1000) < 700:
                    medium_models = [name for name, info in self.model_registry.items() if info['tier'] == 'medium']
                    return medium_models[0] if medium_models else "gpt-5-mini"
                
            except (AttributeError, Exception):
                # If budget checks fail, continue with archetype-based selection
                pass
        
        # Default archetype-based selection when no budget constraints
        if priority >= 2.0:  # C_LEVEL
            heavy_models = [name for name, info in self.model_registry.items() if info['tier'] == 'heavy']
            return heavy_models[0] if heavy_models else "gpt-5.1"
        elif priority >= 1.5:  # EXECUTIVE
            medium_models = [name for name, info in self.model_registry.items() if info['tier'] == 'medium']
            return medium_models[0] if medium_models else "gpt-5-mini"
        elif priority >= 1.2:  # SENIOR_TA
            light_models = [name for name, info in self.model_registry.items() if info['tier'] == 'light']
            return light_models[0] if light_models else "gpt-5-nano"
        else:  # RECRUITER or others
            light_models = [name for name, info in self.model_registry.items() if info['tier'] == 'light']
            return light_models[0] if light_models else "gpt-5-nano"
    
    def _route_by_archetype(self, request_type: str, archetype: str, context: Dict[str, Any]) -> RoutingDecision:
        """Route based on archetype-specific requirements."""
        priority = self.config.priority_weights.get(archetype, 1.0)
        
        # Select model based on archetype priority
        if priority >= 2.0:  # C_LEVEL
            selected_model = "gpt-4"
            reasoning = "High priority archetype - using premium model"
        elif priority >= 1.5:  # EXECUTIVE
            selected_model = "claude-3"
            reasoning = "Executive priority - using high-quality model"
        elif priority >= 1.2:  # SENIOR_TA
            selected_model = "gpt-3.5-turbo"
            reasoning = "Senior technical authority - using standard model"
        else:  # RECRUITER or default
            selected_model = "llama-2"
            reasoning = "Standard priority - using cost-effective model"
        
        model_info = self.model_registry[selected_model]
        
        return RoutingDecision(
            selected_model=selected_model,
            confidence=0.9,
            reasoning=reasoning,
            cost_estimate=model_info["cost"],
            performance_estimate=model_info["performance"],
            fallback_used=False,
            metadata={"archetype": archetype, "priority": priority}
        )
    
    def _route_by_cost(self, request_type: str, context: Dict[str, Any]) -> RoutingDecision:
        """Route based on cost optimization."""
        # Find cheapest model that meets minimum requirements
        min_accuracy = self.config.performance_requirements.get("min_accuracy", 0.8)
        
        suitable_models = [
            (name, info) for name, info in self.model_registry.items()
            if info["performance"]["accuracy"] >= min_accuracy
        ]
        
        if suitable_models:
            selected_model = min(suitable_models, key=lambda x: x[1]["cost"])[0]
            reasoning = "Cost optimization - selected cheapest suitable model"
        else:
            selected_model = "llama-2"  # Fallback
            reasoning = "No models met cost requirements - using fallback"
        
        model_info = self.model_registry[selected_model]
        
        return RoutingDecision(
            selected_model=selected_model,
            confidence=0.8,
            reasoning=reasoning,
            cost_estimate=model_info["cost"],
            performance_estimate=model_info["performance"],
            fallback_used=not suitable_models,
            metadata={"strategy": "cost_optimized"}
        )
    
    def _route_by_performance(self, request_type: str, context: Dict[str, Any]) -> RoutingDecision:
        """Route based on performance optimization."""
        max_latency = self.config.performance_requirements.get("max_latency_ms", 5000)
        
        suitable_models = [
            (name, info) for name, info in self.model_registry.items()
            if info["performance"]["latency"] <= max_latency
        ]
        
        if suitable_models:
            # Select best performing model
            selected_model = max(suitable_models, key=lambda x: x[1]["performance"]["accuracy"])[0]
            reasoning = "Performance optimization - selected best performing model"
        else:
            selected_model = "gpt-3.5-turbo"  # Fallback
            reasoning = "No models met performance requirements - using fallback"
        
        model_info = self.model_registry[selected_model]
        
        return RoutingDecision(
            selected_model=selected_model,
            confidence=0.9,
            reasoning=reasoning,
            cost_estimate=model_info["cost"],
            performance_estimate=model_info["performance"],
            fallback_used=not suitable_models,
            metadata={"strategy": "performance_optimized"}
        )
    
    def _route_by_priority(self, request_type: str, archetype: str, context: Dict[str, Any]) -> RoutingDecision:
        """Route based on priority weighting."""
        priority = context.get("priority", 1.0)
        
        if priority >= 2.0:
            selected_model = "gpt-4"
        elif priority >= 1.5:
            selected_model = "claude-3"
        elif priority >= 1.0:
            selected_model = "gpt-3.5-turbo"
        else:
            selected_model = "llama-2"
        
        model_info = self.model_registry[selected_model]
        reasoning = f"Priority-based routing - priority {priority} mapped to {selected_model}"
        
        return RoutingDecision(
            selected_model=selected_model,
            confidence=0.85,
            reasoning=reasoning,
            cost_estimate=model_info["cost"],
            performance_estimate=model_info["performance"],
            fallback_used=priority < 1.0,
            metadata={"priority": priority, "strategy": "priority_based"}
        )
    
    def _route_balanced(self, request_type: str, archetype: str, context: Dict[str, Any]) -> RoutingDecision:
        """Route using balanced approach considering cost, performance, and priority."""
        # Simple balanced scoring
        best_score = -1
        selected_model = "gpt-3.5-turbo"
        
        for model_name, model_info in self.model_registry.items():
            # Calculate balanced score
            cost_score = 1.0 / (model_info["cost"] + 0.001)  # Lower cost = higher score
            performance_score = model_info["performance"]["accuracy"]
            
            # Apply archetype weighting if available
            if archetype:
                priority = self.config.priority_weights.get(archetype, 1.0)
                priority_weight = priority / 2.0
            else:
                priority_weight = 1.0
            
            balanced_score = (cost_score * 0.3 + performance_score * 0.4 + priority_weight * 0.3)
            
            if balanced_score > best_score:
                best_score = balanced_score
                selected_model = model_name
        
        model_info = self.model_registry[selected_model]
        reasoning = f"Balanced routing - selected {selected_model} with score {best_score:.2f}"
        
        return RoutingDecision(
            selected_model=selected_model,
            confidence=0.85,
            reasoning=reasoning,
            cost_estimate=model_info["cost"],
            performance_estimate=model_info["performance"],
            fallback_used=False,
            metadata={"strategy": "balanced", "score": best_score}
        )
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update routing configuration."""
        if "strategy" in new_config:
            self.config.strategy = RoutingStrategy(new_config["strategy"])
        if "priority_weights" in new_config:
            self.config.priority_weights.update(new_config["priority_weights"])
        if "cost_thresholds" in new_config:
            self.config.cost_thresholds.update(new_config["cost_thresholds"])
        if "performance_requirements" in new_config:
            self.config.performance_requirements.update(new_config["performance_requirements"])
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics and performance metrics."""
        if not self.routing_history:
            return {"total_routes": 0, "message": "No routing history available"}
        
        model_usage = {}
        total_cost = 0.0
        
        for decision in self.routing_history:
            model_name = decision.selected_model
            model_usage[model_name] = model_usage.get(model_name, 0) + 1
            total_cost += decision.cost_estimate
        
        return {
            "total_routes": len(self.routing_history),
            "model_usage": model_usage,
            "total_estimated_cost": total_cost,
            "average_confidence": sum(d.confidence for d in self.routing_history) / len(self.routing_history),
            "fallback_usage_rate": sum(1 for d in self.routing_history if d.fallback_used) / len(self.routing_history),
            "config": {
                "strategy": self.config.strategy.value,
                "priority_weights": self.config.priority_weights
            }
        }
