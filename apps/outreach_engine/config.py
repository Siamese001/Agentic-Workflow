#!/usr/bin/env python3
"""
Outreach Engine Configuration - Lift & Shift + Enhanced from LIC
Parameter presets, context management, and adaptive controls
"""

from typing import Dict, List, Optional, Any, Union
import math

from .models import (
    Route, Archetype, ValidationResult, ValidationSeverity
)


class ContextManager:
    """Context window allocator - Enhanced from LIC"""
    
    def __init__(self, parameter_presets: Dict[str, Any]):
        self.context_config = parameter_presets.get("parameter_presets", {}).get("context_manager", {})
        self.max_tokens = self.context_config.get("max_tokens", 8000)
        self.allocation = self.context_config.get("allocation", {})
        self.overflow_strategy = self.context_config.get("overflow_strategy", {})
    
    def allocate_context(
        self, 
        sender_profile: Dict[str, Any],
        recipient_context: Dict[str, Any],
        rag_results: Optional[Dict[str, Any]] = None,
        reasoning_space: Optional[Dict[str, Any]] = None
    ) -> Dict[str, int]:
        """Allocate context tokens across different components"""
        allocation = {}
        
        # Base allocations from configuration
        allocation["sender_profile"] = self.allocation.get("sender_profile", 500)
        allocation["recipient_context"] = self.allocation.get("recipient_context", 1500)
        allocation["rag_results"] = self.allocation.get("rag_results", 4000)
        allocation["reasoning_space"] = self.allocation.get("reasoning_space", 2000)
        
        # Dynamic adjustments based on content size
        if rag_results:
            rag_size = self._estimate_token_count(str(rag_results))
            if rag_size > allocation["rag_results"]:
                excess = rag_size - allocation["rag_results"]
                allocation = self._handle_overflow(allocation, excess, "rag_results")
        
        # Ensure total doesn't exceed max_tokens
        total_allocated = sum(allocation.values())
        if total_allocated > self.max_tokens:
            allocation = self._scale_down_to_limit(allocation)
        
        return allocation
    
    def _estimate_token_count(self, text: str) -> int:
        """Estimate token count from text (rough approximation)"""
        # Rough estimate: ~4 characters per token
        return len(text) // 4
    
    def _handle_overflow(self, allocation: Dict[str, int], excess: int, source: str) -> Dict[str, int]:
        """Handle context overflow using configured strategy"""
        priority = self.overflow_strategy.get("priority", "sender_profile > rag_results > recipient_context")
        priority_order = [p.strip() for p in priority.split(">")]
        
        # Reduce from lowest priority components first
        for component in reversed(priority_order):
            if component in allocation and excess > 0:
                available = allocation[component]
                reduction = min(excess, available // 2)  # Reduce by up to 50%
                allocation[component] -= reduction
                excess -= reduction
        
        return allocation
    
    def _scale_down_to_limit(self, allocation: Dict[str, int]) -> Dict[str, int]:
        """Scale down allocation to fit within max_tokens"""
        total = sum(allocation.values())
        if total <= self.max_tokens:
            return allocation
        
        scale_factor = self.max_tokens / total
        scaled_allocation = {}
        
        for key, value in allocation.items():
            scaled_allocation[key] = max(100, int(value * scale_factor))  # Minimum 100 tokens per component
        
        return scaled_allocation
    
    def get_context_summary(self, allocation: Dict[str, int]) -> Dict[str, Any]:
        """Get summary of context allocation"""
        total_allocated = sum(allocation.values())
        
        return {
            "total_allocated": total_allocated,
            "max_tokens": self.max_tokens,
            "utilization_percent": (total_allocated / self.max_tokens) * 100,
            "component_breakdown": allocation,
            "remaining_tokens": self.max_tokens - total_allocated
        }


class AdaptiveTemperatureController:
    """Adaptive temperature controller - Lift & Shift from LIC"""
    
    def __init__(self, parameter_presets: Dict[str, Any]):
        self.temp_config = parameter_presets.get("parameter_presets", {}).get("adaptive_temperature_controller", {})
        self.base_temperatures = self.temp_config.get("base_temperatures", {})
        self.escalation_step = self.temp_config.get("escalation_step", 0.15)
        self.max_temperature = self.temp_config.get("max_temperature", 0.95)
        self.max_creative_retries = self.temp_config.get("max_creative_retries", 3)
    
    def get_temperature(
        self, 
        archetype: Archetype, 
        retry_count: int = 0,
        context_difficulty: Optional[float] = None
    ) -> float:
        """Get adaptive temperature for generation"""
        base_temp = self.base_temperatures.get(archetype.value, 0.7)
        
        # Escalate temperature based on retry count
        escalated_temp = base_temp + (retry_count * self.escalation_step)
        
        # Adjust for context difficulty if provided
        if context_difficulty is not None:
            difficulty_adjustment = context_difficulty * 0.1  # Scale difficulty to temperature adjustment
            escalated_temp += difficulty_adjustment
        
        # Cap at maximum temperature
        final_temp = min(escalated_temp, self.max_temperature)
        
        return round(final_temp, 2)
    
    def should_retry_with_higher_temp(self, validation_results: List[ValidationResult]) -> bool:
        """Determine if should retry with higher temperature"""
        # Check if validation failures suggest need for more creativity
        creativity_issues = [
            result for result in validation_results 
            if not result.passed and (
                "generic" in result.message.lower() or 
                "vague" in result.message.lower() or
                "cliché" in result.message.lower()
            )
        ]
        
        return len(creativity_issues) > 0
    
    def get_temperature_guidance(self, archetype: Archetype) -> Dict[str, Any]:
        """Get temperature guidance for archetype"""
        base_temp = self.base_temperatures.get(archetype.value, 0.7)
        
        return {
            "base_temperature": base_temp,
            "max_temperature": self.max_temperature,
            "escalation_step": self.escalation_step,
            "max_retries": self.max_creative_retries,
            "temperature_range": f"{base_temp} - {self.max_temperature}",
            "retry_strategy": "Increase temperature by 0.15 per retry"
        }


class ToolCallBudget:
    """Tool call budget guidance - Enhanced from LIC"""
    
    def __init__(self, parameter_presets: Dict[str, Any]):
        self.budget_config = parameter_presets.get("parameter_presets", {}).get("tool_call_budget", {})
        self.minimum = self.budget_config.get("minimum", 0)
        self.maximum = self.budget_config.get("maximum", 20)
        self.guidance = self.budget_config.get("guidance", {})
        self.scaling = self.budget_config.get("scaling", "")
    
    def get_tool_budget(
        self, 
        route: Route, 
        has_job_context: bool = False,
        query_complexity: Optional[float] = None
    ) -> Dict[str, Any]:
        """Get tool call budget for specific context"""
        route_key = route.value
        
        # Base budget from guidance
        if route_key in self.guidance:
            budget_str = self.guidance[route_key]
            if has_job_context and "job" in route_key:
                budget_str = self.guidance.get(f"{route_key}_job", budget_str)
        else:
            budget_str = "6-10"  # Default
        
        # Parse budget range
        budget_range = self._parse_budget_range(budget_str)
        
        # Adjust for query complexity
        if query_complexity is not None:
            complexity_multiplier = 1.0 + (query_complexity * 0.5)
            budget_range = [
                int(budget_range[0] * complexity_multiplier),
                int(budget_range[1] * complexity_multiplier)
            ]
        
        # Ensure within limits
        budget_range = [
            max(self.minimum, min(self.maximum, budget_range[0])),
            max(self.minimum, min(self.maximum, budget_range[1]))
        ]
        
        return {
            "minimum_calls": budget_range[0],
            "maximum_calls": budget_range[1],
            "recommended_calls": (budget_range[0] + budget_range[1]) // 2,
            "route": route_key,
            "has_job_context": has_job_context,
            "scaling_applied": query_complexity is not None
        }
    
    def _parse_budget_range(self, budget_str: str) -> List[int]:
        """Parse budget range string like "6-10" or "8-12" """
        if "-" in budget_str:
            parts = budget_str.split("-")
            try:
                return [int(parts[0]), int(parts[1])]
            except ValueError:
                return [6, 10]  # Default fallback
        else:
            # Single number, treat as both min and max
            try:
                num = int(budget_str)
                return [num, num]
            except ValueError:
                return [6, 10]  # Default fallback
    
    def validate_tool_usage(self, actual_calls: int, budget: Dict[str, Any]) -> List[ValidationResult]:
        """Validate actual tool usage against budget"""
        validation_results = []
        
        min_calls = budget.get("minimum_calls", 0)
        max_calls = budget.get("maximum_calls", 20)
        
        if actual_calls < min_calls:
            validation_results.append(ValidationResult(
                rule_id="TOOL_CALLS_BELOW_MINIMUM",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message=f"Tool calls {actual_calls} below minimum {min_calls}",
                details={"actual_calls": actual_calls, "minimum_calls": min_calls}
            ))
        
        if actual_calls > max_calls:
            validation_results.append(ValidationResult(
                rule_id="TOOL_CALLS_EXCEEDED_MAXIMUM",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message=f"Tool calls {actual_calls} exceeded maximum {max_calls}",
                details={"actual_calls": actual_calls, "maximum_calls": max_calls}
            ))
        
        return validation_results
    
    def get_budget_summary(self, route: Route) -> Dict[str, Any]:
        """Get budget summary for route"""
        budget = self.get_tool_budget(route)
        
        return {
            "route": route.value,
            "budget_range": f"{budget['minimum_calls']}-{budget['maximum_calls']}",
            "recommended": budget["recommended_calls"],
            "scaling_strategy": self.scaling,
            "global_limits": {
                "minimum": self.minimum,
                "maximum": self.maximum
            }
        }


class OutreachConfig:
    """Main configuration manager - Lift & Shift + Enhanced from LIC"""
    
    def __init__(self, lic_capabilities: Dict[str, Any]):
        self.parameter_presets = lic_capabilities.get("parameter_presets", {})
        self.context_manager = ContextManager(self.parameter_presets)
        self.temperature_controller = AdaptiveTemperatureController(self.parameter_presets)
        self.tool_budget = ToolCallBudget(self.parameter_presets)
    
    def get_generation_config(
        self,
        route: Route,
        archetype: Archetype,
        sender_profile: Dict[str, Any],
        recipient_context: Dict[str, Any],
        rag_results: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """Get complete generation configuration"""
        # Context allocation
        context_allocation = self.context_manager.allocate_context(
            sender_profile, recipient_context, rag_results
        )
        
        # Temperature settings
        temperature = self.temperature_controller.get_temperature(archetype, retry_count)
        
        # Tool budget
        has_job_context = rag_results is not None
        tool_budget = self.tool_budget.get_tool_budget(route, has_job_context)
        
        return {
            "context_allocation": context_allocation,
            "temperature": temperature,
            "tool_budget": tool_budget,
            "route": route.value,
            "archetype": archetype.value,
            "retry_count": retry_count
        }
    
    def validate_configuration(self, config: Dict[str, Any]) -> List[ValidationResult]:
        """Validate configuration parameters"""
        validation_results = []
        
        # Validate temperature
        temperature = config.get("temperature", 0.7)
        if temperature < 0 or temperature > 2:
            validation_results.append(ValidationResult(
                rule_id="TEMPERATURE_OUT_OF_RANGE",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message=f"Temperature {temperature} outside valid range [0, 2]",
                details={"temperature": temperature}
            ))
        
        # Validate context allocation
        context_allocation = config.get("context_allocation", {})
        total_allocated = sum(context_allocation.values())
        max_tokens = self.context_manager.max_tokens
        
        if total_allocated > max_tokens:
            validation_results.append(ValidationResult(
                rule_id="CONTEXT_ALLOCATION_EXCEEDED",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message=f"Context allocation {total_allocated} exceeds maximum {max_tokens}",
                details={"total_allocated": total_allocated, "max_tokens": max_tokens}
            ))
        
        return validation_results
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of all configuration settings"""
        return {
            "context_manager": {
                "max_tokens": self.context_manager.max_tokens,
                "allocation_strategy": self.context_manager.overflow_strategy.get("priority", "default")
            },
            "temperature_controller": {
                "base_temperatures": self.temperature_controller.base_temperatures,
                "escalation_step": self.temperature_controller.escalation_step,
                "max_temperature": self.temperature_controller.max_temperature
            },
            "tool_budget": {
                "global_limits": {
                    "minimum": self.tool_budget.minimum,
                    "maximum": self.tool_budget.maximum
                },
                "scaling_strategy": self.tool_budget.scaling
            }
        }
